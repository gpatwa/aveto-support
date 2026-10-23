"""The Anthropic Messages API adapter for the answerability judge (the only model boundary).

Request: model, max_tokens, system, one user message, output_config.effort. Nothing else:
no tools, no metadata, no visitor value. Errors leave as `JudgeTransportError` with a fixed
category; the exception text, request and response are dropped. Nothing here logs or prints.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from collections.abc import Callable
from typing import Any

import anthropic

from aveto_service.judge_port import JudgeCall, JudgeTransportError
from aveto_support import judge as core_judge

MODEL = "claude-sonnet-5-5"
EFFORT = "high"
MAX_TOKENS = 1024
TIMEOUT_SECONDS = 20.0
BACKOFF_SECONDS = 1.0
MAX_ATTEMPTS = 2
BASE_URL = "https://api.anthropic.com"
ADAPTER_ID = "anthropic-messages-judge-v1"
# The SDK's DEBUG logging prints the request options, which hold the payload: mute it here too.
_SDK_LOGGERS = ("anthropic", "httpx", "httpx2", "httpcore", "httpcore2")


def build_request(system_prompt: str, payload: str) -> dict[str, Any]:
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": payload}],
        "output_config": {"effort": EFFORT},
    }


def prompt_matches_pin(system_prompt: str) -> bool:
    digest = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()
    return digest == core_judge.PROMPT_SHA256


def extract_reply(message: Any) -> str:
    """Text blocks joined; thinking blocks dropped unread; anything but end_turn is an error."""
    if getattr(message, "stop_reason", None) != "end_turn":
        raise JudgeTransportError("stop_reason")
    parts: list[str] = []
    for block in getattr(message, "content", None) or []:
        kind = getattr(block, "type", None)
        if kind in ("tool_use", "server_tool_use"):
            raise JudgeTransportError("tool_use")
        if kind == "text":
            text = getattr(block, "text", "")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts)


def _category(exc: BaseException) -> str:
    if isinstance(exc, anthropic.APITimeoutError):
        return "timeout"
    if isinstance(exc, anthropic.APIConnectionError):
        return "connection"
    if isinstance(exc, anthropic.APIStatusError):
        return "status_5xx" if exc.status_code >= 500 else "status_4xx"
    return "other"


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, anthropic.APITimeoutError):
        return False
    return isinstance(
        exc,
        (
            anthropic.RateLimitError,
            anthropic.InternalServerError,
            anthropic.APIConnectionError,
        ),
    )


class AnthropicJudgeClient:
    name = ADAPTER_ID

    def __init__(
        self,
        api_key: str,
        *,
        client: Any | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key:
            raise ValueError("Anthropic judge adapter needs an API key.")
        for name in _SDK_LOGGERS:
            sdk_logger = logging.getLogger(name)
            sdk_logger.setLevel(logging.CRITICAL + 1)
            sdk_logger.propagate = False
        if client is None:
            # The SDK merges ANTHROPIC_CUSTOM_HEADERS into every request and an explicit
            # default_headers cannot remove them: fail closed. ANTHROPIC_BASE_URL is
            # overridden by the explicit base_url below.
            if os.environ.get("ANTHROPIC_CUSTOM_HEADERS") is not None:
                raise ValueError("Anthropic judge adapter refuses extra SDK header settings.")
            client = anthropic.Anthropic(
                api_key=api_key, base_url=BASE_URL, max_retries=0, timeout=TIMEOUT_SECONDS
            )
        self._client = client
        self._sleep = sleep

    def judge(self, system_prompt: str, payload: str) -> JudgeCall:
        if not prompt_matches_pin(system_prompt):
            raise JudgeTransportError("prompt_hash", attempts=0)
        request = build_request(system_prompt, payload)
        attempts = 0
        while True:
            attempts += 1
            try:
                message = self._client.messages.create(**request)
                reply = extract_reply(message)
                usage = getattr(message, "usage", None)
                return JudgeCall(
                    reply=reply,
                    input_tokens=_count(getattr(usage, "input_tokens", None)),
                    output_tokens=_count(getattr(usage, "output_tokens", None)),
                    attempts=attempts,
                )
            except JudgeTransportError as exc:
                raise JudgeTransportError(exc.category, attempts=attempts) from None
            except Exception as exc:  # noqa: BLE001 - all failures map to a fixed category
                if attempts < MAX_ATTEMPTS and _retryable(exc):
                    self._sleep(BACKOFF_SECONDS)
                    continue
                raise JudgeTransportError(_category(exc), attempts=attempts) from None


def _count(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
