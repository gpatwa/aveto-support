"""Eval-only driver tooling for the answerability judge (slice docs-answerability-2).

Not product behaviour. It derives the seen-set sample from retrieval, reads the forked judge
transcripts the harness writes, audits them, turns each reply into a token through the
product's own `judge-apply` (in-process), writes the verdicts file the product's
`eval --verdicts` scores, and prints the extra diagnostics the intent asks for.

It makes no network call, starts no process and calls no model. Standard library plus
`aveto_support` only (a test pins the import list).

    uv run python -m tools.judge_run <command> ...
        derive-sample | add-set | check-transcripts | record | diagnostics
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aveto_support import judge
from aveto_support.embed import Embedder
from aveto_support.evaluate import EvalSet, load_eval_set
from aveto_support.index import load_index
from aveto_support.judge_eval import (
    FORMAT,
    bar_met,
    build_results,
    load_verdicts,
    right_file_rank,
)
from aveto_support.search import Searcher, retrieve

JUDGE_AGENT = "aveto-answerability-judge"
JUDGE_MODEL = "claude-sonnet-5-5"
SKILL_NAME = "aveto-judge-seen"
EXPECT_LINE_LEN = 137  # R1: 31 + len(<worktree>/.claude/skills/aveto-judge-seen)
BASE_PREFIX = "Base directory for this skill: "
KEY_ORDER = (
    "evals/retrieval.toml",
    "evals/retrieval-heldout.toml",
    "evals/retrieval-heldout-3.toml",
    "evals/retrieval-heldout-4.toml",
)
EXPECTED_U = (6, 6, 4, 4)
EXPECTED_H = (19, 12, 11, 14)
SMOKE_ID = "r049"
GATE_FIRST = 101
BEST_SCORE_THRESHOLD = 0.67
BEST_SCORE_REPRODUCE = ((13, 20), (37, 56))
CHECK_DIR = "runs/docs-answerability-2/judge-check"
GENERATING_COMMAND = f"uv run python -m tools.judge_run derive-sample --out {CHECK_DIR}"
TRANSPORT = Path(".aveto-judge")
CATEGORIES = frozenset(
    {
        judge.OUTSIDE, judge.UNREADABLE, judge.TOO_LONG, judge.NOT_UTF8, judge.EMPTY,
        judge.CONTROL, judge.MALFORMED, judge.WRONG_ID, judge.MULTI_TOKEN,
        judge.DIFFERENT_INPUT, judge.NOT_DELETED,
    }
)
_SIGNAL = re.compile(
    r"Deciding signal: answerability judge verdict (ANSWERABLE|NOT_ANSWERABLE) "
    rf"\(prompt {re.escape(judge.PROMPT_ID)}, sha256 {judge.PROMPT_SHA256}\)"
)
_RUN_ID = re.compile(r"r[0-9]{3}")


class SampleError(Exception):
    """The sample cannot be derived or written as registered. Nothing is written."""


class TranscriptFormatError(Exception):
    """A transcript has a shape this reader does not know. Nothing is scored."""


class ApplyError(Exception):
    """`judge-apply` did something the registered contract does not allow."""


# --- TOML output ----------------------------------------------------------------


def toml_str(value: str) -> str:
    """One escaping function for every string written to a TOML file."""
    return json.dumps(value, ensure_ascii=False).replace("\x7f", "\\u007f")


def toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return repr(value)
    if isinstance(value, str):
        return toml_str(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(v) for v in value) + "]"
    raise SampleError(f"cannot write a {type(value).__name__} to TOML")


# --- sample derivation (R4) ---------------------------------------------------------


@dataclass(frozen=True)
class Row:
    run_id: str
    set_path: str
    eval_id: str
    question: str
    role: str  # sample | smoke | gate
    entry: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


def _raw_entries(path: Path) -> list[dict[str, Any]]:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    entries = raw.get("question")
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise SampleError(f"{path}: no [[question]] tables")
    return entries


def _check_question_text(text: str, where: str) -> None:
    if not text.strip() or any(c in text for c in "\n\r") or text != text.strip():
        raise SampleError(f"{where}: the question must be one non-empty line without edge spaces")


def derive_sample(
    searcher: Searcher,
    root: Path,
    *,
    sets: Sequence[str] = KEY_ORDER,
    expected_u: Sequence[int] = EXPECTED_U,
    expected_h: Sequence[int] = EXPECTED_H,
) -> list[Row]:
    """R4 exactly. Raises SampleError unless U and H (total and per set) are as registered."""
    unanswerable: list[tuple[int, int, Row]] = []
    hits: list[tuple[int, int, Row]] = []
    commits: set[str] = set()
    for si, rel in enumerate(sets):
        eval_set = load_eval_set(root / rel)
        commits.add(eval_set.pinned_commit)
        entries = _raw_entries(root / rel)
        if len(entries) != len(eval_set.questions):
            raise SampleError(f"{rel}: question count mismatch")
        for qi, (q, entry) in enumerate(zip(eval_set.questions, entries, strict=True)):
            if not q.answerable:
                unanswerable.append((si, qi, Row("", rel, q.id, q.question, "sample", entry)))
                continue
            rank = right_file_rank(judge.retrieve_for_judge(searcher, q.question), q.sources)
            if rank is not None:
                hits.append((si, qi, Row("", rel, q.id, q.question, "sample", entry)))
    if len(commits) != 1:
        raise SampleError(f"the seen sets are not pinned to one commit: {sorted(commits)}")
    u_counts = tuple(sum(1 for si, _, _ in unanswerable if si == i) for i in range(len(sets)))
    h_counts = tuple(sum(1 for si, _, _ in hits if si == i) for i in range(len(sets)))
    if (
        u_counts != tuple(expected_u)
        or h_counts != tuple(expected_h)
        or len(unanswerable) != sum(expected_u)
        or len(hits) != sum(expected_h)
    ):
        raise SampleError(
            f"split is not as registered: U {len(unanswerable)} {u_counts} (expected "
            f"{sum(expected_u)} {tuple(expected_u)}), H {len(hits)} {h_counts} (expected "
            f"{sum(expected_h)} {tuple(expected_h)}); nothing written"
        )
    selected = hits[0::2]  # positions 1, 3, 5, ... (1-based)
    smoke = hits[1]
    ordered = sorted(unanswerable + selected, key=lambda t: (t[0], t[1]))
    rows = [
        Row(f"r{n:03d}", r.set_path, r.eval_id, r.question, "sample", r.entry)
        for n, (_, _, r) in enumerate(ordered, start=1)
    ]
    s = smoke[2]
    rows.append(Row(SMOKE_ID, s.set_path, s.eval_id, s.question, "smoke", s.entry))
    for r in rows:
        _check_question_text(r.question, f"{r.set_path} {r.eval_id}")
    return rows


def _key_text(rows: Sequence[Row], header: Sequence[str]) -> str:
    lines = [f"# {h}" if h else "#" for h in header]
    for r in rows:
        lines.append(f"[{r.run_id}]")
        lines.append(f"set = {toml_str(r.set_path)}")
        lines.append(f"id = {toml_str(r.eval_id)}")
    return "\n".join(lines) + "\n"


def _per_set(rows: Sequence[Row], role: str) -> list[int]:
    chosen = [r for r in rows if r.role == role]
    return [sum(1 for r in chosen if r.set_path == s) for s in KEY_ORDER]


def write_check_dir(rows: Sequence[Row], out: Path, index_sha256: str, pinned_commit: str) -> None:
    """Write key/key.toml, batch-1.txt and sample-eval.toml. Refuses to overwrite a key."""
    key_path = out / "key" / "key.toml"
    if key_path.exists():
        raise SampleError(f"{key_path} already exists; the sample is never redrawn")
    sample = [r for r in rows if r.role == "sample"]
    header = [
        "docs-answerability-2 judge-check key. Membership only (the helper reads table names).",
        f"Generated by: {GENERATING_COMMAND}",
        f"index sha256 {index_sha256}; ranking file-rrf-v1",
        f"sample {len(sample)} (per set {_per_set(rows, 'sample')}); r049 = smoke (H position 2), never scored",
        "parity: H positions 1, 3, 5, ... 55 (1-based); U = every unanswerable question",
    ]
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(_key_text(rows, header), encoding="utf-8")
    (out / "batch-1.txt").write_text(
        "".join(f"{r.run_id} {r.question}\n" for r in rows), encoding="utf-8"
    )
    parts = [f"# Derived by {GENERATING_COMMAND}. Questions copied verbatim from the seen sets.\n"]
    parts.append(f"pinned_commit = {toml_str(pinned_commit)}\n")
    for r in sample:
        parts.append("\n[[question]]\n")
        for k, v in r.entry.items():
            parts.append(f"{k} = {toml_value(v)}\n")
    (out / "sample-eval.toml").write_text("".join(parts), encoding="utf-8")


def add_set(eval_file: Path, out: Path, first: int = GATE_FIRST, *, set_label: str | None = None) -> list[Row]:
    """Stage 7: append key tables and write batch-2.txt for every question in the file."""
    batch = out / "batch-2.txt"
    key_path = out / "key" / "key.toml"
    if batch.exists():
        raise SampleError(f"{batch} already exists")
    if not key_path.exists():
        raise SampleError(f"{key_path} does not exist; derive the sample first")
    entries = _raw_entries(eval_file)  # only id and question are read below
    if first + len(entries) - 1 > 999:
        raise SampleError("the run ids would pass r999")
    label = set_label if set_label is not None else str(eval_file)
    rows: list[Row] = []
    for n, entry in enumerate(entries, start=first):
        qid, text = entry.get("id"), entry.get("question")
        if not isinstance(qid, str) or not isinstance(text, str):
            raise SampleError("each question needs a string id and question")
        _check_question_text(text, f"{eval_file} {qid}")
        rows.append(Row(f"r{n:03d}", label, qid, text, "gate"))
    with key_path.open("a", encoding="utf-8") as handle:
        handle.write(_key_text(rows, [f"Gate set {label}: added by judge_run add-set (no label read)."]))
    batch.write_text("".join(f"{r.run_id} {r.question}\n" for r in rows), encoding="utf-8")
    return rows


# --- transcripts (R1, R6, R7) -----------------------------------------------------------


@dataclass(frozen=True)
class Spawn:
    agent_id: str
    agent_type: str
    models: tuple[str, ...]
    offered_tools: tuple[str, ...]
    tool_uses: int
    base_line_len: int
    layout_ok: bool
    payload: str | None
    reply: str | None
    requests: int
    peak: int
    in_equiv: float


_USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
_BLOCKS_OK = frozenset({"text", "thinking", "redacted_thinking"})
_PROMPT_LINE = re.compile(
    re.escape(BASE_PREFIX) + r"/[^\n]*/\.claude/skills/" + re.escape(SKILL_NAME)
)


def _fail(path: Path, why: str) -> TranscriptFormatError:
    return TranscriptFormatError(f"{path.name}: {why}")


def read_spawn(jsonl: Path) -> Spawn:
    """Read one forked spawn: `<agent>.jsonl`, `.meta.json` and `.prefix.json`. Fails closed."""
    stem = jsonl.name[: -len(".jsonl")]
    try:
        meta = json.loads((jsonl.parent / f"{stem}.meta.json").read_text(encoding="utf-8"))
        prefix = json.loads((jsonl.parent / f"{stem}.prefix.json").read_text(encoding="utf-8"))
        lines = jsonl.read_text(encoding="utf-8").splitlines()
    except (OSError, ValueError) as exc:
        raise _fail(jsonl, f"cannot read the transcript files: {exc}") from exc
    if not isinstance(meta, dict) or not isinstance(meta.get("agentType"), str):
        raise _fail(jsonl, "meta.json has no agentType")
    state = prefix.get("state") if isinstance(prefix, dict) else None
    tools = state.get("toolNames") if isinstance(state, dict) else None
    if not isinstance(tools, list) or not all(isinstance(t, str) for t in tools):
        raise _fail(jsonl, "prefix.json has no toolNames list")
    prompt: str | None = None
    tool_uses = 0
    models: list[str] = []
    usage: dict[str, dict[str, int]] = {}
    messages: list[tuple[str, list[str]]] = []  # (message id, text blocks) in file order
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except ValueError as exc:
            raise _fail(jsonl, f"line {number} is not JSON") from exc
        if not isinstance(rec, dict):
            raise _fail(jsonl, f"line {number} is not an object")
        kind = rec.get("type")
        if kind == "attachment":
            continue
        message = rec.get("message")
        if kind not in ("user", "assistant") or not isinstance(message, dict):
            raise _fail(jsonl, f"line {number}: unknown record type {kind!r}")
        content = message.get("content")
        if kind == "user":
            if prompt is None:
                if not isinstance(content, str):
                    raise _fail(jsonl, f"line {number}: the first user record is not a string prompt")
                prompt = content
            elif not isinstance(content, (str, list)):
                raise _fail(jsonl, f"line {number}: unknown user content")
            continue
        if prompt is None:
            raise _fail(jsonl, f"line {number}: an assistant record before the prompt")
        mid, model, use = message.get("id"), message.get("model"), message.get("usage")
        if not isinstance(mid, str) or not isinstance(model, str) or not isinstance(use, dict):
            raise _fail(jsonl, f"line {number}: assistant record without id, model and usage")
        if not isinstance(content, list):
            raise _fail(jsonl, f"line {number}: assistant content is not a list")
        models.append(model)
        counts = {k: use.get(k, 0) for k in _USAGE_KEYS}
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in counts.values()):
            raise _fail(jsonl, f"line {number}: usage counts are not integers")
        previous = usage.setdefault(mid, dict.fromkeys(_USAGE_KEYS, 0))
        usage[mid] = {k: max(previous[k], counts[k]) for k in _USAGE_KEYS}
        texts: list[str] = []
        for block in content:
            btype = block.get("type") if isinstance(block, dict) else None
            if not isinstance(btype, str):
                raise _fail(jsonl, f"line {number}: a content block without a type")
            if btype.endswith("tool_use"):
                tool_uses += 1
            elif btype == "text":
                text = block.get("text")
                if not isinstance(text, str):
                    raise _fail(jsonl, f"line {number}: a text block without text")
                texts.append(text)
            elif btype not in _BLOCKS_OK:
                raise _fail(jsonl, f"line {number}: unknown content block {btype!r}")
        messages.append((mid, texts))
    if prompt is None:
        raise _fail(jsonl, "no user prompt")
    first_line = prompt.split("\n", 1)[0]
    layout_ok = bool(_PROMPT_LINE.fullmatch(first_line)) and prompt[len(first_line) :].startswith("\n\n")
    payload = prompt[len(first_line) + 2 :] if layout_ok else None
    reply: str | None = None
    if messages:
        last = messages[-1][0]
        joined = "".join(t for mid, texts in messages if mid == last for t in texts)
        reply = joined if any(texts for mid, texts in messages if mid == last) else None
    peak = max((sum(u.values()) for u in usage.values()), default=0)
    in_equiv = sum(
        u["input_tokens"] + 1.25 * u["cache_creation_input_tokens"]
        + 0.1 * u["cache_read_input_tokens"] + u["output_tokens"]
        for u in usage.values()
    )
    return Spawn(
        agent_id=stem.removeprefix("agent-"),
        agent_type=meta["agentType"],
        models=tuple(sorted(set(models))),
        offered_tools=tuple(tools),
        tool_uses=tool_uses,
        base_line_len=len(first_line),
        layout_ok=layout_ok,
        payload=payload,
        reply=reply,
        requests=len(usage),
        peak=peak,
        in_equiv=in_equiv,
    )


def check_transcripts(subagents_dir: Path) -> str:
    """Read-only: per transcript, the audited fields. No reply text and no token."""
    lines: list[str] = []
    for path in sorted(subagents_dir.glob("agent-*.jsonl")):
        s = read_spawn(path)
        parse = "no reply"
        if s.reply is not None:
            try:
                judge.parse_verdict(s.reply, judge.BLOCK_ID)
                parse = "parses"
            except judge.JudgeError as exc:
                parse = f"does not parse ({exc.category})"
        sha = hashlib.sha256(s.payload.encode("utf-8")).hexdigest()[:16] if s.payload is not None else "none"
        lines.append(
            f"agent {s.agent_id}: type {s.agent_type}; models {','.join(s.models) or 'none'}; "
            f"offered tools {len(s.offered_tools)}; tool_use {s.tool_uses}; "
            f"base line {s.base_line_len} (layout {'ok' if s.layout_ok else 'BAD'}); payload sha16 {sha}; "
            f"reply {'present, ' + str(len(s.reply)) + ' chars' if s.reply is not None else 'absent'}; "
            f"parse {parse}; requests {s.requests}; peak {s.peak}; in-equivalent {s.in_equiv:,.0f}"
        )
    return "\n".join(lines) + ("\n" if lines else "")


# --- applying a reply through the product's judge-apply (R5) ---------------------------


@dataclass(frozen=True)
class Applied:
    token: str  # ANSWERABLE | NOT_ANSWERABLE | JUDGE_ERROR
    category: str | None


def apply_reply(
    question: str,
    payload_sha: str,
    reply: str | None,
    *,
    embedder: Embedder,
    index: Path,
) -> Applied:
    """Run the product's `judge-apply` in-process. Only the token and category come back."""
    from aveto_support.__main__ import main

    TRANSPORT.mkdir(exist_ok=True)
    question_file, reply_file = TRANSPORT / "question.txt", TRANSPORT / "reply.txt"
    question_file.write_text(question, encoding="utf-8")
    reply_file.write_bytes((reply or "").encode("utf-8", errors="surrogatepass"))
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(
            [
                "judge-apply", "--index", str(index), "--question-file", str(question_file),
                "--input-sha256", payload_sha, "--verdict-file", str(reply_file),
            ],
            embedder=embedder,
        )
    stdout, stderr = out.getvalue(), err.getvalue()
    if code == 0:
        last = stdout.rstrip("\n").rsplit("\n", 1)[-1]
        m = _SIGNAL.fullmatch(last)
        if m is None or not stdout.endswith("\n"):
            raise ApplyError("judge-apply exit 0 without the deciding-signal line")
        token = m.group(1)
        if token == "NOT_ANSWERABLE" and stdout != f"no confident match\n{last}\n":
            raise ApplyError("judge-apply NOT_ANSWERABLE output is not the two registered lines")
        return Applied(token, None)
    if code == 4:
        m2 = re.fullmatch(r"judge error: (.+)\n", stderr)
        if stdout != "judge error\n" or m2 is None or m2.group(1) not in CATEGORIES:
            raise ApplyError("judge-apply exit 4 with an unexpected output shape")
        return Applied("JUDGE_ERROR", m2.group(1))
    raise ApplyError(f"judge-apply exited {code}")


# --- record: audit, void rules, verdicts (R6) ------------------------------------------------


@dataclass(frozen=True)
class SpawnRecord:
    run_id: str
    eval_id: str
    agent_id: str
    model: str
    offered: int
    tool_use: int
    line_len: int
    payload_sha: str
    reply_sha: str
    token: str
    category: str
    peak: int
    in_equiv: float
    in_batch: bool


@dataclass(frozen=True)
class RecordResult:
    void: bool
    reasons: tuple[str, ...]
    rows: tuple[SpawnRecord, ...]
    others: tuple[str, ...]
    verdicts_path: Path | None

    @property
    def batch_rows(self) -> tuple[SpawnRecord, ...]:
        return tuple(r for r in self.rows if r.in_batch)


def load_key(check_dir: Path) -> dict[str, tuple[str, str]]:
    with (check_dir / "key" / "key.toml").open("rb") as handle:
        raw = tomllib.load(handle)
    out: dict[str, tuple[str, str]] = {}
    for run_id, table in raw.items():
        if not _RUN_ID.fullmatch(run_id) or not isinstance(table, dict) or set(table) != {"set", "id"}:
            raise SampleError(f"key table {run_id}: needs exactly set and id")
        out[run_id] = (str(table["set"]), str(table["id"]))
    return out


def _question_for(root: Path, set_path: str, eval_id: str, cache: dict[str, list[dict[str, Any]]]) -> str:
    entries = cache.setdefault(set_path, _raw_entries(root / set_path))
    for entry in entries:
        if entry.get("id") == eval_id:
            return str(entry["question"])
    raise SampleError(f"{set_path}: no question {eval_id}")


def _sha16(text: str | None) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="surrogatepass")).hexdigest()[:16] if text is not None else "none"


def _audit_md(result: RecordResult, expect_tools: tuple[str, ...]) -> str:
    lines = [
        "# Tool-use audit",
        "",
        (f"Batch decision: {'VOID' if result.void else 'valid'}; expected offered tools {len(expect_tools)}; "
        f"expected model {JUDGE_MODEL}; expected base-dir line {EXPECT_LINE_LEN}."),
    ]
    for reason in result.reasons:
        lines.append(f"- void reason: {reason}")
    lines += ["", "| run | eval id | agent | model | offered | tool_use | line | payload16 | reply16 | result | peak | in-equiv |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in result.rows:
        shown = r.token + (f" ({r.category})" if r.category else "")
        batch = "" if r.in_batch else " (not in batch)"
        lines.append(
            f"| {r.run_id}{batch} | {r.eval_id} | {r.agent_id} | {r.model} | {r.offered} | {r.tool_use} | "
            f"{r.line_len} | {r.payload_sha[:16]} | {r.reply_sha} | {shown} | {r.peak} | {r.in_equiv:,.0f} |"
        )
    batch_rows = result.batch_rows
    lines += [
        "",
        (f"Batch spawns: {len(batch_rows)}; peak sum {sum(r.peak for r in batch_rows):,}; "
        f"in-equivalent sum {sum(r.in_equiv for r in batch_rows):,.0f}."),
        f"Other agents (not judge spawns, not counted): {', '.join(result.others) or 'none'}.",
    ]
    return "\n".join(lines) + "\n"


def record(
    subagents_dir: Path,
    check_dir: Path,
    eval_file: Path,
    stage_dir: Path,
    expect_tools: tuple[str, ...],
    *,
    embedder: Embedder,
    index: Path,
    root: Path = Path("."),
    expect_line_len: int = EXPECT_LINE_LEN,
) -> RecordResult:
    """Audit every judge transcript, void the batch on any R6 point 2 condition, else write
    verdicts.toml, audit.md and diffs.md (and audit.json for `diagnostics`)."""
    stage_dir.mkdir(parents=True, exist_ok=True)
    searcher = Searcher(load_index(index), embedder)
    key = load_key(check_dir)
    cache: dict[str, list[dict[str, Any]]] = {}
    eval_set = load_eval_set(eval_file)
    eval_ids = {q.id for q in eval_set.questions}
    questions: dict[str, str] = {}
    by_sha: dict[str, str] = {}
    reasons: list[str] = []
    for run_id, (set_path, eval_id) in key.items():
        questions[run_id] = _question_for(root, set_path, eval_id, cache)
        sha = judge.input_sha256(judge.format_judge_input(judge.retrieve_for_judge(searcher, questions[run_id])))
        if sha in by_sha:
            reasons.append(f"key rows {by_sha[sha]} and {run_id} have the same payload")
        by_sha[sha] = run_id
    batch_ids = sorted(rid for rid, (_, eid) in key.items() if eid in eval_ids and rid != SMOKE_ID)
    others: list[str] = []
    seen: dict[str, str] = {}  # run id -> agent id
    rows: list[SpawnRecord] = []
    spawns: list[tuple[Spawn, str]] = []
    for path in sorted(subagents_dir.glob("agent-*.jsonl")):
        meta_path = path.with_name(path.name[: -len(".jsonl")] + ".meta.json")
        try:
            agent_type = json.loads(meta_path.read_text(encoding="utf-8")).get("agentType")
        except (OSError, ValueError, AttributeError) as exc:
            raise TranscriptFormatError(f"{meta_path.name}: unreadable meta.json") from exc
        if agent_type != JUDGE_AGENT:
            others.append(f"{path.stem.removeprefix('agent-')} ({agent_type})")
            continue
        spawn = read_spawn(path)
        sha = hashlib.sha256(spawn.payload.encode("utf-8")).hexdigest() if spawn.payload is not None else ""
        run_id = by_sha.get(sha, "")
        tag = spawn.agent_id
        if spawn.tool_uses:
            reasons.append(f"{tag}: {spawn.tool_uses} tool_use block(s)")
        if spawn.models != (JUDGE_MODEL,):
            reasons.append(f"{tag}: model {','.join(spawn.models) or 'none'}, not {JUDGE_MODEL}")
        if spawn.offered_tools != expect_tools:
            reasons.append(f"{tag}: {len(spawn.offered_tools)} offered tools, expected {len(expect_tools)}")
        if not spawn.layout_ok or spawn.base_line_len != expect_line_len:
            reasons.append(f"{tag}: base-dir line {spawn.base_line_len}, layout {'ok' if spawn.layout_ok else 'bad'}")
        if not run_id:
            reasons.append(f"{tag}: the payload matches no key question")
        elif run_id in seen:
            reasons.append(f"{run_id}: two transcripts ({seen[run_id]}, {tag})")
        else:
            seen[run_id] = tag
        spawns.append((spawn, run_id))
    for rid in batch_ids:
        if rid not in seen:
            reasons.append(f"{rid}: no transcript")
    applied: dict[str, Applied] = {}
    if not reasons:
        for spawn, run_id in spawns:
            assert spawn.payload is not None
            applied[run_id] = apply_reply(
                questions[run_id], hashlib.sha256(spawn.payload.encode("utf-8")).hexdigest(),
                spawn.reply, embedder=embedder, index=index,
            )
    for spawn, run_id in sorted(spawns, key=lambda t: t[1]):
        got = applied.get(run_id)
        rows.append(
            SpawnRecord(
                run_id=run_id or "?", eval_id=key[run_id][1] if run_id else "?", agent_id=spawn.agent_id,
                model=",".join(spawn.models), offered=len(spawn.offered_tools), tool_use=spawn.tool_uses,
                line_len=spawn.base_line_len,
                payload_sha=hashlib.sha256(spawn.payload.encode("utf-8")).hexdigest() if spawn.payload is not None else "",
                reply_sha=_sha16(spawn.reply), token=got.token if got else "(not applied)",
                category=got.category or "" if got else "", peak=spawn.peak, in_equiv=spawn.in_equiv,
                in_batch=run_id in batch_ids,
            )
        )
    result = RecordResult(bool(reasons), tuple(reasons), tuple(rows), tuple(others), None)
    (stage_dir / "audit.md").write_text(_audit_md(result, expect_tools), encoding="utf-8")
    if reasons:
        return result
    verdicts_path = stage_dir / "verdicts.toml"
    by_eval = {key[r.run_id][1]: r for r in result.batch_rows}
    results = build_results(searcher, eval_set)
    parts = [f'format = "{FORMAT}"\nprompt_sha256 = "{judge.PROMPT_SHA256}"\n']
    for q in eval_set.questions:
        r = by_eval[q.id]
        parts.append(
            f'\n[[verdict]]\nid = {toml_str(q.id)}\nverdict = {toml_str(r.token)}\n'
            f'input_sha256 = {toml_str(r.payload_sha)}\n'
        )
    verdicts_path.write_text("".join(parts), encoding="utf-8")
    diffs = ["# Differing replies and judge errors (run record only)\n"]
    reply_of = {run_id: spawn.reply for spawn, run_id in spawns}
    for q in eval_set.questions:
        r = by_eval[q.id]
        run_id = r.run_id
        if not q.answerable:
            want: str | None = "NOT_ANSWERABLE"
        else:
            want = "ANSWERABLE" if right_file_rank(results[q.id], q.sources) is not None else None
        if r.token == "JUDGE_ERROR" or (want is not None and r.token != want):
            diffs.append(
                f"\n## {run_id} ({q.id})\n\nexpected: {want or 'none (right file not in top 5)'}; "
                f"verdict: {r.token}{' (' + r.category + ')' if r.category else ''}\n\n"
                f"reply:\n\n```\n{reply_of[run_id] if reply_of[run_id] is not None else '(no reply)'}\n```\n"
            )
    (stage_dir / "diffs.md").write_text("".join(diffs), encoding="utf-8")
    (stage_dir / "audit.json").write_text(
        json.dumps(
            [
                {"run_id": r.run_id, "eval_id": r.eval_id, "token": r.token, "category": r.category,
                 "peak": r.peak, "in_equiv": r.in_equiv, "in_batch": r.in_batch}
                for r in result.rows
            ],
            indent=1,
        ),
        encoding="utf-8",
    )
    return RecordResult(False, (), result.rows, result.others, verdicts_path)


# --- diagnostics (R7) ------------------------------------------------------------------------


@dataclass(frozen=True)
class BestScore:
    abstained: int
    unanswerable: int
    shown: int
    hits: int


def best_score_rule(searcher: Searcher, eval_set: EvalSet) -> BestScore:
    """Abstain when top1 < 0.67; top1 = highest, over the five returned files, of each file's
    best dense similarity over all of that file's passages (docs-abstention primary signal)."""
    by_file: dict[str, list[int]] = {}
    for i, p in enumerate(searcher.index.passages):
        by_file.setdefault(p.path, []).append(i)
    abstained = unanswerable = shown = hits = 0
    for q in eval_set.questions:
        result = retrieve(searcher, q.question)
        sims = searcher.passage_sims(searcher.embedder.embed_query(q.question))
        top1 = max(max(sims[i] for i in by_file[f.path]) for f in result.files)
        abstain = top1 < BEST_SCORE_THRESHOLD
        if not q.answerable:
            unanswerable += 1
            abstained += abstain
        elif right_file_rank(result, q.sources) is not None:
            hits += 1
            shown += not abstain
    return BestScore(abstained, unanswerable, shown, hits)


def self_check(searcher: Searcher, root: Path) -> tuple[bool, str]:
    total = [0, 0, 0, 0]
    for rel in KEY_ORDER:
        b = best_score_rule(searcher, load_eval_set(root / rel))
        total = [total[0] + b.abstained, total[1] + b.unanswerable, total[2] + b.shown, total[3] + b.hits]
    ok = (total[0], total[1]) == BEST_SCORE_REPRODUCE[0] and (total[2], total[3]) == BEST_SCORE_REPRODUCE[1]
    want = f"{BEST_SCORE_REPRODUCE[0][0]}/{BEST_SCORE_REPRODUCE[0][1]} and {BEST_SCORE_REPRODUCE[1][0]}/{BEST_SCORE_REPRODUCE[1][1]}"
    text = (
        f"best score rule (top1 < {BEST_SCORE_THRESHOLD}) on the four seen sets: bar 1 {total[0]}/{total[1]}, "
        f"bar 2 {total[2]}/{total[3]}; recorded {want}: {'reproduced' if ok else 'NOT reproduced'}"
    )
    return ok, text


def diagnostics(
    searcher: Searcher, eval_file: Path, verdicts: Path, audit: Sequence[dict[str, Any]] | None
) -> str:
    eval_set = load_eval_set(eval_file)
    results = build_results(searcher, eval_set)
    tokens = load_verdicts(verdicts, eval_set, results)
    over = hit_total = no_hit_yes = no_hit_total = 0
    err = {"bar 1": 0, "bar 2": 0, "neither": 0}
    for q in eval_set.questions:
        token = tokens[q.id]
        hit = q.answerable and right_file_rank(results[q.id], q.sources) is not None
        if token == "JUDGE_ERROR":
            err["bar 1" if not q.answerable else ("bar 2" if hit else "neither")] += 1
        if hit:
            hit_total += 1
            over += token == "NOT_ANSWERABLE"
        elif q.answerable:
            no_hit_total += 1
            no_hit_yes += token == "ANSWERABLE"
    b = best_score_rule(searcher, eval_set)
    met1 = "MET" if bar_met(b.abstained, b.unanswerable) else "NOT MET"
    met2 = "MET" if bar_met(b.shown, b.hits) else "NOT MET"
    lines = [
        (f"best score rule (top1 < {BEST_SCORE_THRESHOLD}): bar 1 {b.abstained}/{b.unanswerable} {met1}; "
        f"bar 2 {b.shown}/{b.hits} {met2}"),
        (f"over-abstention: {over}/{hit_total} answerable questions with a hit were called NOT_ANSWERABLE "
        "(judge errors excluded)"),
        f"ANSWERABLE without a hit: {no_hit_yes}/{no_hit_total}",
        f"judge errors: {sum(err.values())}; bar 1 {err['bar 1']} / bar 2 {err['bar 2']} / neither {err['neither']}",
    ]
    if audit is not None:
        rows = [r for r in audit if r["in_batch"]]
        cats: dict[str, int] = {}
        for r in rows:
            if r["category"]:
                cats[r["category"]] = cats.get(r["category"], 0) + 1
        lines.append("judge error categories: " + (", ".join(f"{k} x{v}" for k, v in sorted(cats.items())) or "none"))
        lines.append(
            f"usage: {len(rows)} spawns; peak sum {sum(int(r['peak']) for r in rows):,}; "
            f"in-equivalent sum {sum(float(r['in_equiv']) for r in rows):,.0f}"
        )
    return "\n".join(lines) + "\n"


# --- command line -------------------------------------------------------------------------


def _open(index_path: str, models: str) -> tuple[Searcher, Any]:
    from aveto_support.embed import OnnxEmbedder

    index = load_index(Path(index_path))
    embedder = OnnxEmbedder.load(Path(models), index.params.embedding)
    return Searcher(index, embedder), embedder


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="judge_run")
    p.add_argument("--index", default="index/docs-index.json")
    p.add_argument("--models", default="models")
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("derive-sample")
    d.add_argument("--out", default=CHECK_DIR)
    a = sub.add_parser("add-set")
    a.add_argument("--eval-file", required=True)
    a.add_argument("--out", default=CHECK_DIR)
    c = sub.add_parser("check-transcripts")
    c.add_argument("subagents_dir")
    r = sub.add_parser("record")
    r.add_argument("--subagents-dir", required=True)
    r.add_argument("--check-dir", default=CHECK_DIR)
    r.add_argument("--eval-file", required=True)
    r.add_argument("--stage-dir", required=True)
    r.add_argument("--expect-tools", required=True, help="comma-separated names, or 'none' for 0")
    g = sub.add_parser("diagnostics")
    g.add_argument("--self-check", action="store_true")
    g.add_argument("--eval-file")
    g.add_argument("--verdicts")
    g.add_argument("--audit")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return _run(args)
    except (SampleError, TranscriptFormatError, ApplyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _run(args: argparse.Namespace) -> int:
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    if args.command == "check-transcripts":
        sys.stdout.write(check_transcripts(Path(args.subagents_dir)))
        return 0
    searcher, embedder = _open(args.index, args.models)
    try:
        if args.command == "derive-sample":
            rows = derive_sample(searcher, Path("."))
            digest = hashlib.sha256(Path(args.index).read_bytes()).hexdigest()
            commit = load_eval_set(Path(KEY_ORDER[0])).pinned_commit
            write_check_dir(rows, Path(args.out), digest, commit)
            print(f"wrote {len(rows)} rows (48 sample + smoke {SMOKE_ID}) to {args.out}; index sha256 {digest}")
            return 0
        if args.command == "add-set":
            rows = add_set(Path(args.eval_file), Path(args.out))
            print(f"added {len(rows)} rows {rows[0].run_id}..{rows[-1].run_id}")
            return 0
        if args.command == "record":
            names = () if args.expect_tools == "none" else tuple(args.expect_tools.split(","))
            result = record(
                Path(args.subagents_dir), Path(args.check_dir), Path(args.eval_file), Path(args.stage_dir),
                names, embedder=embedder, index=Path(args.index),
            )
            print(f"batch {'VOID' if result.void else 'valid'}; {len(result.batch_rows)} batch spawns")
            for reason in result.reasons:
                print(f"void: {reason}")
            return 1 if result.void else 0
        if args.self_check:
            ok, text = self_check(searcher, Path("."))
            print(text)
            return 0 if ok else 1
        audit = json.loads(Path(args.audit).read_text(encoding="utf-8")) if args.audit else None
        sys.stdout.write(diagnostics(searcher, Path(args.eval_file), Path(args.verdicts), audit))
        return 0
    finally:
        embedder.close()


if __name__ == "__main__":
    sys.exit(main())
