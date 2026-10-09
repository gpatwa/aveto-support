"""Score retrieval against the owner's eval set (read-only)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aveto_support.index import Index
from aveto_support.judge import Judge, JudgeParams
from aveto_support.search import Searcher, judge_result, retrieve

REQUIRED_PERCENT = 80


class EvalFormatError(Exception):
    """The eval file is malformed, or does not match the index."""


@dataclass(frozen=True)
class EvalQuestion:
    id: str
    question: str
    answerable: bool
    sources: tuple[str, ...] = ()
    hard_negative: bool = False


@dataclass(frozen=True)
class EvalSet:
    pinned_commit: str
    questions: tuple[EvalQuestion, ...]


@dataclass(frozen=True)
class QuestionOutcome:
    id: str
    answerable: bool
    hit: bool  # accepted file in the top 5 before abstention (retrieval's own ranking)
    detail: str
    abstained: bool = False
    judge_best: float = 0.0
    top1_hit: bool = False


@dataclass(frozen=True)
class EvalReport:
    outcomes: tuple[QuestionOutcome, ...]
    answerable_hits: int
    answerable_total: int
    unanswerable_total: int
    bar1_abstained: int = 0  # unanswerable questions the judge abstained on
    bar2_kept: int = 0  # top-5 hits the judge did not abstain on
    bar2_denominator: int = 0  # answerable questions with an accepted file in the 5 files before abstention
    end_to_end_top5: int = 0
    end_to_end_top1: int = 0

    @property
    def passed(self) -> bool:
        return self.answerable_total > 0 and self.answerable_hits * 5 >= self.answerable_total * 4

    @property
    def bar1_passed(self) -> bool:
        return self.bar1_abstained * 5 >= self.unanswerable_total * 4

    @property
    def bar2_passed(self) -> bool:
        return self.bar2_kept * 5 >= self.bar2_denominator * 4


def load_eval_set(path: Path) -> EvalSet:
    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except OSError as exc:
        raise EvalFormatError(f"cannot read eval file {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise EvalFormatError(f"eval file {path} is not valid TOML: {exc}") from exc
    commit = raw.get("pinned_commit")
    entries = raw.get("question")
    if not isinstance(commit, str) or not isinstance(entries, list):
        raise EvalFormatError("eval file needs pinned_commit (string) and [[question]] tables")
    questions: list[EvalQuestion] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise EvalFormatError("each [[question]] must be a table")
        qid, text = entry.get("id"), entry.get("question")
        if not isinstance(qid, str) or not isinstance(text, str) or not text.strip():
            raise EvalFormatError("each question needs a string id and question")
        flag = entry.get("answerable", True)
        if not isinstance(flag, bool):
            raise EvalFormatError(f"{qid}: answerable must be true or false")
        if flag:
            sources = entry.get("sources")
            if (
                not isinstance(sources, list)
                or not sources
                or not all(isinstance(s, str) for s in sources)
            ):
                raise EvalFormatError(f"{qid}: an answerable question needs a non-empty sources list")
            questions.append(EvalQuestion(qid, text, True, tuple(sources)))
        else:
            questions.append(
                EvalQuestion(qid, text, False, hard_negative=entry.get("hard_negative") is True)
            )
    if not any(q.answerable for q in questions):
        raise EvalFormatError("eval file needs at least one answerable question")
    return EvalSet(commit, tuple(questions))


def check_commit(index: Index, eval_set: EvalSet) -> None:
    if index.commit != eval_set.pinned_commit:
        raise EvalFormatError(
            f"index is for commit {index.commit}, eval set is pinned to "
            f"{eval_set.pinned_commit}; re-run ingest"
        )


def score(searcher: Searcher, eval_set: EvalSet, judge: Judge, params: JudgeParams) -> EvalReport:
    outcomes: list[QuestionOutcome] = []
    a_hits = a_total = u_total = 0
    bar1 = kept = e5 = e1 = 0
    for q in eval_set.questions:
        result = retrieve(searcher, q.question)
        verdict = judge_result(judge, params, result)  # the same decision `respond` makes
        abstained = not verdict.answers
        top = f"top score {result.top_score:.2f}"
        if q.answerable:
            a_total += 1
            matched = [f for f in result.files if f.path in q.sources]
            top1 = result.files[0].path in q.sources
            if matched:
                a_hits += 1
                if not abstained:
                    kept += 1
                    e5 += 1
                    e1 += 1 if top1 else 0
                detail = f"{matched[0].path} (rank {matched[0].rank})  {top}"
            else:
                got = ", ".join(f.path for f in result.files)
                detail = f"expected {' | '.join(q.sources)}; got {got}  {top}"
            outcomes.append(
                QuestionOutcome(q.id, True, bool(matched), detail, abstained, verdict.best, top1)
            )
        else:
            u_total += 1
            if abstained:
                bar1 += 1
                e5 += 1
                e1 += 1
            tag = " [hard negative]" if q.hard_negative else ""
            outcomes.append(
                QuestionOutcome(
                    q.id, False, False, f"top file {result.files[0].path}  {top}{tag}", abstained,
                    verdict.best,
                )
            )
    return EvalReport(tuple(outcomes), a_hits, a_total, u_total, bar1, kept, a_hits, e5, e1)


def _ceil80(n: int) -> int:
    return (4 * n + 4) // 5


def _pct(hits: int, total: int) -> str:
    return f"{(100.0 * hits / total) if total else 0.0:.1f}%"


def format_report(report: EvalReport, eval_file: str, index: Index) -> str:
    lines = [
        (
            f"eval: {eval_file}  index: {index.repo} @ {index.commit[:8]}…  ranking: file-rrf-v1  "
            f"reference similarity: {index.threshold:.3f} (diagnostic)"
        )
    ]
    for o in report.outcomes:
        if o.answerable:
            label = "HIT" if o.hit else "MISS"
            judged = f"  judge p={o.judge_best:.2f} {'ABSTAINED' if o.abstained else 'answered'}"
        else:
            label = "ABST" if o.abstained else "DIAG"
            judged = f"  judge p={o.judge_best:.2f}"
        lines.append(f"{o.id}  {label:<6}{o.detail}{judged}")
    verdict = "PASS" if report.passed else "FAIL"
    total = report.answerable_total + report.unanswerable_total
    lines.append(
        f"answerable:   {report.answerable_hits}/{report.answerable_total} "
        f"({_pct(report.answerable_hits, report.answerable_total)})  "
        f"required >= {REQUIRED_PERCENT}%  {verdict}"
    )
    u, h = report.unanswerable_total, report.bar2_denominator
    lines.append(
        f"abstention bar 1: {report.bar1_abstained}/{u} unanswerable abstained  "
        f"required >= {_ceil80(u)}  {'PASS' if report.bar1_passed else 'FAIL'}"
    )
    lines.append(
        f"abstention bar 2: {report.bar2_kept}/{h} top-5 hits not abstained  "
        f"required >= {_ceil80(h)}  {'PASS' if report.bar2_passed else 'FAIL'}"
    )
    lines.append(
        f"end-to-end (top 5): {report.end_to_end_top5}/{total}  "
        f"end-to-end (top 1): {report.end_to_end_top1}/{total}"
    )
    lines.append(
        f"unanswerable: {u} (abstention bars reported above; eval exit code reflects the "
        "retrieval gate only)"
    )
    lines.append(f"eval: {verdict}")
    return "\n".join(lines)
