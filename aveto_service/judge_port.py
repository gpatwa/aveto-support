"""The boundary to the generative model: the pipeline is the only caller.

The real adapter (`anthropic_judge.AnthropicJudgeClient`, stage 9) implements `JudgeClient`.
The adapter receives the system prompt and the payload and nothing about the visitor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class JudgeCall:
    reply: str  # concatenated text blocks only; never logged, never returned past the parser
    input_tokens: int | None  # from response usage; None when no response arrived
    output_tokens: int | None
    attempts: int = 1  # API attempts made (1 or 2); every attempt is charged to the spend counter


class JudgeTransportError(Exception):
    """The call produced no usable response. `category` is a fixed string; no message text."""

    def __init__(self, category: str, attempts: int = 1) -> None:
        super().__init__(category)
        self.category = category
        self.attempts = attempts


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
