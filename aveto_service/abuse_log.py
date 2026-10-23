"""The service's only log events: abuse lines and fixed-code ops lines on stdout.

An abuse line holds a hashed IP prefix, a time and an outcome code. Nothing else is ever
logged: not the question, the passages, the payload, the reply, headers, URLs or exceptions.
"""

from __future__ import annotations

import logging
import re
import sys
import threading
from datetime import UTC, datetime
from enum import StrEnum
from types import TracebackType

ABUSE_LOGGER = "aveto_service.abuse"
OPS_LOGGER = "aveto_service.ops"
_ALLOWED = frozenset({ABUSE_LOGGER, OPS_LOGGER})
_SILENCED = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "anthropic",
    "httpx",
    "httpx2",
    "httpcore",
    "httpcore2",
    "fastapi",
    "starlette",
)
_IP16 = re.compile(r"[0-9a-f]{16}")
_OPS_CATEGORIES = frozenset({"prompt_hash", "index", "model"})
_OPS_CODES = frozenset({"startup_ok", "startup_failed", "unhandled"})


class Outcome(StrEnum):
    ANSWER = "answer"
    NO_CONFIDENT_MATCH = "no_confident_match"
    JUDGE_ERROR = "judge_error"
    EMPTY_QUESTION = "empty_question"
    TOO_LONG = "too_long"
    UNUSABLE_QUESTION = "unusable_question"
    BODY_TOO_LARGE = "body_too_large"
    BAD_REQUEST = "bad_request"
    RATE_LIMITED = "rate_limited"
    PAUSED = "paused"
    SERVICE_OFF = "service_off"


def _stamp(now: datetime) -> str:
    return now.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def abuse_line(ip16: str, outcome: Outcome, now: datetime) -> str:
    """The one abuse line. Takes no other argument, so nothing else can be put in it."""
    if not _IP16.fullmatch(ip16):
        raise ValueError("ip16 must be 16 lowercase hex characters")
    return f'{{"t":"{_stamp(now)}","ip":"{ip16}","o":"{Outcome(outcome).value}"}}'


def ops_line(code: str, now: datetime, category: str | None = None) -> str:
    if code not in _OPS_CODES:
        raise ValueError("unknown ops code")
    if code == "startup_failed":
        if category not in _OPS_CATEGORIES:
            raise ValueError("unknown startup category")
        return f'{{"t":"{_stamp(now)}","ops":"startup_failed","c":"{category}"}}'
    if category is not None:
        raise ValueError("this ops code takes no category")
    return f'{{"t":"{_stamp(now)}","ops":"{code}"}}'


def emit_abuse(ip16: str, outcome: Outcome, now: datetime) -> None:
    logging.getLogger(ABUSE_LOGGER).info(abuse_line(ip16, outcome, now))


def emit_ops(code: str, now: datetime | None = None, category: str | None = None) -> None:
    logging.getLogger(OPS_LOGGER).info(ops_line(code, now or datetime.now(UTC), category))


class _AllowListFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name in _ALLOWED


class _StdoutHandler(logging.Handler):
    """Writes to whatever `sys.stdout` is at emit time."""

    def emit(self, record: logging.LogRecord) -> None:
        sys.stdout.write(self.format(record) + "\n")
        sys.stdout.flush()


_installed: _StdoutHandler | None = None


def _excepthook(
    exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None
) -> None:
    emit_ops("unhandled")


def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
    emit_ops("unhandled")


def configure_logging() -> None:
    """Only the abuse and ops loggers reach stdout; every library logger is silenced."""
    global _installed
    root = logging.getLogger()
    if _installed is not None:
        root.removeHandler(_installed)
    handler = _StdoutHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(_AllowListFilter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    _installed = handler
    for name in _SILENCED:
        lib = logging.getLogger(name)
        for existing in list(lib.handlers):
            lib.removeHandler(existing)
        lib.setLevel(logging.CRITICAL)
        lib.propagate = False
        lib.disabled = True
    sys.excepthook = _excepthook
    threading.excepthook = _thread_excepthook
