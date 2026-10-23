"""The boundary to the generative model: the pipeline is the only caller.

The real adapter (`anthropic_judge.AnthropicJudgeClient`, stage 9) implements `JudgeClient`.
The adapter receives the system prompt and the payload and nothing about the visitor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

MAX_ATTEMPTS = 2  # the most API attempts the adapter makes for one question
NEVER_BILLED = frozenset({"status_4xx", "connection"})  # categories the provider does not bill


@dataclass(frozen=True)
class JudgeCall:
    reply: str  # concatenated text blocks only; never logged, never returned past the parser
    input_tokens: int | None  # from response usage; None when no response arrived
    output_tokens: int | None
    attempts: int = 1  # API attempts made (1 or 2)
    # Failed attempts before the successful one that may have been billed. None: the adapter
    # did not say, so the pipeline charges every earlier attempt.
    billable_failures: int | None = None


class JudgeTransportError(Exception):
    """The call produced no usable response. `category` is a fixed string; no message text."""

    def __init__(
        self, category: str, attempts: int = 1, billable_failures: int | None = None
    ) -> None:
        super().__init__(category)
        self.category = category
        self.attempts = attempts
        if billable_failures is None:  # attempts made that may have been billed
            billable_failures = 0 if category in NEVER_BILLED or attempts == 0 else attempts
        self.billable_failures: int = billable_failures


class JudgeNotConfiguredError(RuntimeError):
    """No judge adapter is configured: nothing was called, nothing was billed."""


class JudgeClient(Protocol):
    def judge(self, system_prompt: str, payload: str) -> JudgeCall: ...


class PlaceholderJudgeClient:
    """Default when no API key is set. Never returns a fake verdict."""

    def judge(self, system_prompt: str, payload: str) -> JudgeCall:
        raise JudgeNotConfiguredError(
            "answerability judge LLM adapter is not configured in this build."
        )
