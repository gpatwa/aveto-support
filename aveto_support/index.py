"""Passages, the index file format, and heading-based splitting."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "aveto-support/index@1"

CALIBRATION_METHOD = "cross-file-null-v1"
CALIBRATION_SEED = 20260926
CALIBRATION_QUERIES = 2000
CALIBRATION_LENGTHS = (2, 3, 4, 5)
CALIBRATION_QUANTILE = 0.9


class IndexFormatError(Exception):
    """The index file is missing, malformed, or built with other parameters."""


@dataclass(frozen=True)
class RetrievalParams:
    """Pre-registered retrieval constants. Changing one is a spec change."""

    tokenizer: str = "v1"
    stopwords: str = "nltk-english-179"
    stemmer: str = "harman-s"
    k1: float = 1.2
    b: float = 0.75
    heading_weight: int = 2
    path_weight: int = 1
    top_k: int = 5
    per_file_cap: int = 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "tokenizer": self.tokenizer,
            "stopwords": self.stopwords,
            "stemmer": self.stemmer,
            "k1": self.k1,
            "b": self.b,
            "heading_weight": self.heading_weight,
            "path_weight": self.path_weight,
            "top_k": self.top_k,
            "per_file_cap": self.per_file_cap,
        }


@dataclass(frozen=True)
class Passage:
    path: str
    heading: str
    heading_path: tuple[str, ...]
    line_start: int
    line_end: int
    text: str


@dataclass(frozen=True)
class Index:
    repo: str
    commit: str
    files_indexed: int
    skipped: tuple[tuple[str, str], ...]
    passages: tuple[Passage, ...]
    threshold: float
    params: RetrievalParams
    empty_sections_dropped: int = 0


# --- splitting -------------------------------------------------------------

_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_CLOSING_HASHES = re.compile(r"[ \t]+#+[ \t]*$")


def _heading_text(raw: str | None) -> str:
    if raw is None:
        return ""
    text = raw.strip()
    if re.fullmatch(r"#+", text):
        return ""
    return _CLOSING_HASHES.sub("", text).strip()


def _find_headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """Return (line_number, level, text) for each ATX heading outside fences."""
    headings: list[tuple[int, int, str]] = []
    start = 0
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                start = i + 1
                break
    fence: tuple[str, int] | None = None
    for i in range(start, len(lines)):
        line = lines[i]
        if fence is not None:
            char, size = fence
            if re.match(r"^ {0,3}" + re.escape(char) + "{" + str(size) + ",}", line):
                fence = None
            continue
        opened = _FENCE_OPEN.match(line)
        if opened:
            marker = opened.group(1)
            fence = (marker[0], len(marker))
            continue
        heading = _HEADING.match(line)
        if heading:
            headings.append((i + 1, len(heading.group(1)), _heading_text(heading.group(2))))
    return headings


def split_sections(path: str, text: str) -> tuple[list[Passage], int]:
    """Split one file into heading passages; also return the dropped-empty count."""
    lines = text.split("\n")
    headings = _find_headings(lines)
    passages: list[Passage] = []
    dropped = 0

    def trimmed_end(first: int, last: int) -> int:
        end = last
        while end >= first and lines[end - 1].strip() == "":
            end -= 1
        return end

    first_heading_line = headings[0][0] if headings else len(lines) + 1
    if first_heading_line > 1:
        end = trimmed_end(1, first_heading_line - 1)
        if end >= 1:
            passages.append(Passage(path, "", (), 1, end, "\n".join(lines[:end])))

    stack: list[tuple[int, str]] = []
    for idx, (line_no, level, heading) in enumerate(headings):
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, heading))
        next_line = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines) + 1
        end = trimmed_end(line_no, next_line - 1)
        if end <= line_no:
            dropped += 1
            continue
        passages.append(
            Passage(
                path,
                heading,
                tuple(t for _, t in stack),
                line_no,
                end,
                "\n".join(lines[line_no - 1 : end]),
            )
        )
    return passages, dropped


def split_passages(path: str, text: str) -> list[Passage]:
    return split_sections(path, text)[0]


# --- serialisation ---------------------------------------------------------


def serialize_index(index: Index) -> bytes:
    doc: dict[str, Any] = {
        "schema": SCHEMA,
        "source": {"repo": index.repo, "commit": index.commit},
        "params": index.params.to_dict(),
        "calibration": {
            "method": CALIBRATION_METHOD,
            "seed": CALIBRATION_SEED,
            "queries": CALIBRATION_QUERIES,
            "lengths": list(CALIBRATION_LENGTHS),
            "quantile": CALIBRATION_QUANTILE,
            "threshold": index.threshold,
        },
        "counts": {
            "files": index.files_indexed,
            "passages": len(index.passages),
            "skipped": len(index.skipped),
            "empty_sections_dropped": index.empty_sections_dropped,
        },
        "skipped": [{"path": p, "reason": r} for p, r in index.skipped],
        "passages": [
            {
                "path": p.path,
                "heading": p.heading,
                "heading_path": list(p.heading_path),
                "line_start": p.line_start,
                "line_end": p.line_end,
                "text": p.text,
            }
            for p in index.passages
        ],
    }
    return (
        json.dumps(
            doc,
            ensure_ascii=False,
            sort_keys=True,
            indent=1,
            separators=(",", ": "),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def write_index(index: Index, path: Path) -> str:
    """Atomically write the index; return the sha256 hex of the bytes written."""
    data = serialize_index(index)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    return hashlib.sha256(data).hexdigest()


def load_index(path: Path) -> Index:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise IndexFormatError(f"cannot read index {path}: {exc.strerror or exc}; run ingest") from exc
    try:
        doc = json.loads(raw)
    except ValueError as exc:
        raise IndexFormatError(f"index {path} is not valid JSON") from exc
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise IndexFormatError(f"index {path} has an unexpected schema; re-run ingest")
    if doc.get("params") != RetrievalParams().to_dict():
        raise IndexFormatError("index was built with different retrieval parameters; re-run ingest")
    try:
        passages = tuple(
            Passage(
                path=_str(p["path"]),
                heading=_str(p["heading"]),
                heading_path=tuple(_str(h) for h in p["heading_path"]),
                line_start=_int(p["line_start"]),
                line_end=_int(p["line_end"]),
                text=_str(p["text"]),
            )
            for p in doc["passages"]
        )
        skipped = tuple((_str(s["path"]), _str(s["reason"])) for s in doc["skipped"])
        counts = doc["counts"]
        threshold = doc["calibration"]["threshold"]
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise TypeError("threshold")
        return Index(
            repo=_str(doc["source"]["repo"]),
            commit=_str(doc["source"]["commit"]),
            files_indexed=_int(counts["files"]),
            skipped=skipped,
            passages=passages,
            threshold=float(threshold),
            params=RetrievalParams(),
            empty_sections_dropped=_int(counts["empty_sections_dropped"]),
        )
    except (KeyError, TypeError) as exc:
        raise IndexFormatError(f"index {path} is malformed ({exc!r}); re-run ingest") from exc


def _str(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("expected str")
    return value


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("expected int")
    return value
