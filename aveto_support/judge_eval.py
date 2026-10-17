"""Score the two answerability bars from a verdicts file (read-only; no model, no network).

The verdicts file is written by a run, never by the product. It carries a token per eval
question and the sha256 of the payload that question produced, and nothing else: a judge's
reason text is rejected, so the product never reads or carries it."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aveto_support.evaluate import EvalSet
from aveto_support.judge import (
    PROMPT_ID,
    PROMPT_SHA256,
    format_judge_input,
    input_sha256,
    retrieve_for_judge,
)
from aveto_support.search import RetrievalResult, Searcher

FORMAT = "aveto-judge-verdicts-v1"
VERDICTS = ("ANSWERABLE", "NOT_ANSWERABLE", "JUDGE_ERROR")
_ENTRY_KEYS = {"id", "verdict", "input_sha256"}
_TOP_KEYS = {"format", "prompt_sha256", "verdict"}


class VerdictsFormatError(Exception):
    """The verdicts file is malformed, or was not made on this product's payloads."""


@dataclass(frozen=True)
class QuestionVerdict:
    id: str
    verdict: str
    expected: str
    agreement: str  # AGREE | DIFF | n/a


@dataclass(frozen=True)
class JudgeReport:
    rows: tuple[QuestionVerdict, ...]
    abstained: int  # bar 1 numerator
    unanswerable_total: int
    shown: int  # bar 2 numerator
    hit_total: int
    answerable_total: int
    judge_errors: int
    hard_abstained: int
    hard_total: int


def bar_met(count: int, total: int) -> bool:
    return total > 0 and count * 5 >= total * 4


def _pct(count: int, total: int) -> str:
    return f"{(100.0 * count / total) if total else 0.0:.1f}%"


def right_file_rank(result: RetrievalResult, sources: tuple[str, ...]) -> int | None:
    """Rank of the first returned file in `sources` (the rule `evaluate.score` uses), else None."""
    matched = [f for f in result.files if f.path in sources]
    return matched[0].rank if matched else None


def build_results(searcher: Searcher, eval_set: EvalSet) -> dict[str, RetrievalResult]:
    return {q.id: retrieve_for_judge(searcher, q.question) for q in eval_set.questions}


def load_verdicts(
    path: Path, eval_set: EvalSet, results: dict[str, RetrievalResult]
) -> dict[str, str]:
    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except OSError as exc:
        raise VerdictsFormatError(f"cannot read verdicts file {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise VerdictsFormatError(f"verdicts file {path} is not valid TOML: {exc}") from exc
    if set(raw) - _TOP_KEYS:
        raise VerdictsFormatError("verdicts file has a key other than format, prompt_sha256, verdict")
    if raw.get("format") != FORMAT:
        raise VerdictsFormatError(f"verdicts file format must be {FORMAT}")
    if raw.get("prompt_sha256") != PROMPT_SHA256:
        raise VerdictsFormatError("verdicts file prompt_sha256 is not this product's judge prompt")
    entries = raw.get("verdict")
    if not isinstance(entries, list):
        raise VerdictsFormatError("verdicts file needs [[verdict]] tables")
    known = {q.id for q in eval_set.questions}
    out: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != _ENTRY_KEYS:
            raise VerdictsFormatError("each [[verdict]] needs exactly id, verdict, input_sha256")
        qid, token, digest = entry["id"], entry["verdict"], entry["input_sha256"]
        if not isinstance(qid, str) or not isinstance(token, str) or not isinstance(digest, str):
            raise VerdictsFormatError("each [[verdict]] value must be a string")
        if qid not in known:
            raise VerdictsFormatError(f"{qid}: not a question in the eval set")
        if qid in out:
            raise VerdictsFormatError(f"{qid}: appears more than once")
        if token not in VERDICTS:
            raise VerdictsFormatError(f"{qid}: verdict must be one of {', '.join(VERDICTS)}")
        if digest != input_sha256(format_judge_input(results[qid])):
            raise VerdictsFormatError(
                f"{qid}: input_sha256 is not the hash of this product's payload for the question"
            )
        out[qid] = token
    missing = [q.id for q in eval_set.questions if q.id not in out]
    if missing:
        raise VerdictsFormatError(f"{missing[0]}: no verdict for this eval question")
    return out


def score_verdicts(
    eval_set: EvalSet, results: dict[str, RetrievalResult], verdicts: dict[str, str]
) -> JudgeReport:
    rows: list[QuestionVerdict] = []
    abstained = u_total = shown = hit_total = a_total = errors = hard = hard_total = 0
    for q in eval_set.questions:
        token = verdicts[q.id]
        errors += token == "JUDGE_ERROR"
        if not q.answerable:
            u_total += 1
            ok = token == "NOT_ANSWERABLE"
            abstained += ok
            if q.hard_negative:
                hard_total += 1
                hard += ok
            rows.append(QuestionVerdict(q.id, token, "abstain", "AGREE" if ok else "DIFF"))
            continue
        a_total += 1
        rank = right_file_rank(results[q.id], q.sources)
        if rank is None:
            rows.append(QuestionVerdict(q.id, token, "show (right file not in top 5)", "n/a"))
            continue
        hit_total += 1
        ok = token == "ANSWERABLE"
        shown += ok
        rows.append(
            QuestionVerdict(
                q.id, token, f"show (right file rank {rank})", "AGREE" if ok else "DIFF"
            )
        )
    return JudgeReport(tuple(rows), abstained, u_total, shown, hit_total, a_total, errors, hard, hard_total)


def format_judge_section(report: JudgeReport, verdicts_path: str) -> str:
    r = report
    label1 = "bar 1 (unanswerable abstained):"
    label2 = "bar 2 (answerable, right file in top 5, not abstained):"
    width = len(label2) + 1
    met1 = "MET" if bar_met(r.abstained, r.unanswerable_total) else "NOT MET"
    met2 = "MET" if bar_met(r.shown, r.hit_total) else "NOT MET"
    lines = [f"judge: verdicts {verdicts_path}  prompt {PROMPT_ID} sha256 {PROMPT_SHA256[:12]}…"]
    lines.extend(f"{row.id}  {row.verdict}  {row.expected}  {row.agreement}" for row in r.rows)
    lines.append(
        f"{label1:<{width}}{r.abstained}/{r.unanswerable_total} "
        f"({_pct(r.abstained, r.unanswerable_total)})  required >= 80%  {met1}"
    )
    lines.append(
        f"{label2:<{width}}{r.shown}/{r.hit_total} "
        f"({_pct(r.shown, r.hit_total)})  required >= 80%  {met2}"
    )
    lines.append(f"judge errors: {r.judge_errors} (counted as failures on both bars)")
    lines.append(f"hard negatives abstained: {r.hard_abstained}/{r.hard_total} (diagnostic)")
    lines.append(f"never abstain (today): bar 1 0/{r.unanswerable_total}, bar 2 {r.hit_total}/{r.hit_total}")
    lines.append(
        "end to end: answerable questions whose right file is shown after judging: "
        f"{r.shown}/{r.answerable_total} (diagnostic)"
    )
    lines.append(
        f"bars: unanswerable_abstained={r.abstained}/{r.unanswerable_total} "
        f"answerable_hit_not_abstained={r.shown}/{r.hit_total} judge_errors={r.judge_errors}"
    )
    lines.append("judge: bars reported, not gated here; eval exit code is the retrieval gate")
    return "\n".join(lines)


def judge_section(searcher: Searcher, eval_set: EvalSet, verdicts_path: Path) -> str:
    """Everything `eval --verdicts` appends; raises before any output on a bad file."""
    results = build_results(searcher, eval_set)
    verdicts = load_verdicts(verdicts_path, eval_set, results)
    return format_judge_section(score_verdicts(eval_set, results, verdicts), str(verdicts_path))
