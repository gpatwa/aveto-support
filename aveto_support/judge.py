"""Offline pieces of the answerability judge step: payload, verdict parser, transport files.

This module never calls a model, opens a socket or starts a process. The judge itself runs in
the operator's own Claude Code session (see the slice's spec); the program only builds the
payload the judge reads and applies the one-token verdict the session hands back.
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from aveto_support.index import Index
from aveto_support.search import QuestionError, RetrievalResult, Searcher, retrieve

BLOCK_ID = "Q1"
PROMPT_ID = "answerability-judge-v1"
PROMPT_SHA256 = "24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427"
TRANSPORT_DIR = Path(".aveto-judge")
REPLY_NAME = "reply.txt"
MAX_QUESTION_BYTES = 4096
MAX_REPLY_BYTES = 4096

# Fixed judge-error categories (spec 4.2). Nothing else is ever printed about a bad reply.
OUTSIDE = "verdict file outside .aveto-judge/"
UNREADABLE = "verdict file unreadable"
TOO_LONG = "reply too long"
NOT_UTF8 = "reply not UTF-8"
EMPTY = "empty reply"
MULTI_LINE = "more than one line"
CONTROL = "control or format character"
MALFORMED = "malformed verdict line"
WRONG_ID = "wrong block id"
MULTI_TOKEN = "more than one verdict token"
DIFFERENT_INPUT = "verdict is for a different input"
NOT_DELETED = "transport file not deleted"

_MARKERS = ("=== ", "--- passage ", "--- end passage ")
_VERDICT_LINE = re.compile(
    r"(?P<id>[^ ]+) (?P<token>ANSWERABLE|NOT_ANSWERABLE)(?: (?P<reason>\S.*))?"
)


class QuestionFormatError(Exception):
    """The question cannot be turned into a judge payload."""


class PayloadMarkerError(Exception):
    """A passage line would forge a payload boundary."""


class TransportError(Exception):
    """A stale transport file could not be removed."""


class JudgeError(Exception):
    """A verdict was not usable. `category` is one of the fixed strings above."""

    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


@dataclass(frozen=True)
class Verdict:
    token: Literal["ANSWERABLE", "NOT_ANSWERABLE"]


# --- question and payload ---------------------------------------------------


def _has_hidden_chars(text: str) -> bool:
    return any(unicodedata.category(ch) in ("Cc", "Cf") for ch in text)


def normalise_question(raw: str) -> str:
    text = " ".join(raw.split())
    if not text:
        raise QuestionFormatError("the question is empty")
    if _has_hidden_chars(text):
        raise QuestionFormatError("the question contains a control or format character")
    return text


def read_question_file(path: Path) -> str:
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_QUESTION_BYTES + 1)
    except OSError as exc:
        raise QuestionFormatError(f"cannot read question file: {exc.strerror or exc}") from exc
    if len(data) > MAX_QUESTION_BYTES:
        raise QuestionFormatError(f"question file is over {MAX_QUESTION_BYTES} bytes")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise QuestionFormatError("question file is not UTF-8") from exc


def retrieve_for_judge(searcher: Searcher, raw_question: str) -> RetrievalResult:
    """Normalise the question, then retrieve with the default ranking (the judged question)."""
    try:
        return retrieve(searcher, normalise_question(raw_question))
    except QuestionError as exc:
        raise QuestionFormatError(str(exc)) from exc


def format_judge_input(result: RetrievalResult) -> str:
    lines = [f"=== {BLOCK_ID} ===", f"Question: {result.question}", ""]
    for hit in result.files:
        lines.append(f"File {hit.rank}: {hit.path}")
        for letter, match in zip("abcdefghij", hit.passages, strict=False):
            p = match.passage
            label = f"{hit.rank}{letter}"
            for offset, text_line in enumerate(p.text.splitlines()):
                if text_line.startswith(_MARKERS):
                    raise PayloadMarkerError(
                        f"{p.path} lines {p.line_start}-{p.line_end}: a passage line "
                        f"({offset + 1}) starts like a payload marker"
                    )
            heading = " > ".join(p.heading_path) if p.heading_path else "(top of file)"
            lines.append(
                f"--- passage {label} | heading: {heading} | "
                f"lines {p.line_start}-{p.line_end} ---"
            )
            lines.append(p.text)
            lines.append(f"--- end passage {label} ---")
            lines.append("")
    lines.append(f"=== end {BLOCK_ID} ===")
    return "\n".join(lines) + "\n"


def input_sha256(block: str) -> str:
    return hashlib.sha256(block.encode("utf-8")).hexdigest()


# --- verdict ----------------------------------------------------------------


def parse_verdict(reply: str, block_id: str) -> Verdict:
    """Accept exactly one line `<id> <token> [reason]`; keep the token, drop the reason."""
    s = reply.strip()
    if not s:
        raise JudgeError(EMPTY)
    if "\n" in s or "\r" in s:
        raise JudgeError(MULTI_LINE)
    if _has_hidden_chars(s):
        raise JudgeError(CONTROL)
    m = _VERDICT_LINE.fullmatch(s)
    if m is None:
        raise JudgeError(MALFORMED)
    if m.group("id") != block_id:
        raise JudgeError(WRONG_ID)
    if s.count("ANSWERABLE") != 1:
        raise JudgeError(MULTI_TOKEN)
    token = m.group("token")
    if token == "ANSWERABLE":
        return Verdict("ANSWERABLE")
    return Verdict("NOT_ANSWERABLE")


def signal_line(verdict: Verdict) -> str:
    return (
        f"Deciding signal: answerability judge verdict {verdict.token} "
        f"(prompt {PROMPT_ID}, sha256 {PROMPT_SHA256})"
    )


def render_applied(verdict: Verdict, result: RetrievalResult, index: Index) -> str:
    """The text `judge-apply` prints on success, ending in a newline."""
    if verdict.token == "NOT_ANSWERABLE":
        return "no confident match\n" + signal_line(verdict) + "\n"
    from aveto_support.__main__ import format_result

    return format_result(result, index) + "\n" + signal_line(verdict) + "\n"


# --- transport files ---------------------------------------------------------


def transport_file(path: Path) -> tuple[Path | None, str | None]:
    """(safe path, None) when `path` is a regular, non-symlink file directly inside the
    transport directory; otherwise (None, the judge-error category)."""
    base = TRANSPORT_DIR.resolve()
    if not base.is_dir() or path.name in ("", ".", ".."):
        return None, OUTSIDE
    if Path(os.path.realpath(path.parent)) != base:
        return None, OUTSIDE
    candidate = base / path.name
    if candidate.is_symlink():
        return None, OUTSIDE
    if not candidate.is_file():
        return None, UNREADABLE
    return candidate, None


def read_reply(safe: Path) -> str:
    try:
        fd = os.open(safe, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as handle:
            data = handle.read(MAX_REPLY_BYTES + 1)
    except OSError as exc:
        raise JudgeError(UNREADABLE) from exc
    if len(data) > MAX_REPLY_BYTES:
        raise JudgeError(TOO_LONG)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise JudgeError(NOT_UTF8) from exc


def delete_transport_files(paths: Iterable[Path]) -> bool:
    """Delete each path that is a safe transport file; True when nothing failed.
    Anything outside the transport directory, or a symlink, is never touched."""
    ok = True
    for path in paths:
        safe, _ = transport_file(path)
        if safe is None:
            continue
        try:
            safe.unlink()
        except FileNotFoundError:
            continue
        except OSError:
            ok = False
    return ok


def remove_stale_reply() -> None:
    if not delete_transport_files([TRANSPORT_DIR / REPLY_NAME]):
        raise TransportError("cannot remove the stale reply file in .aveto-judge/")
