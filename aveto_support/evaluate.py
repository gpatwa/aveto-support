"""Score retrieval against the owner's eval set (read-only)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aveto_support.index import Index
from aveto_support.search import Searcher, capped, retrieve, tokenize

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
    hit: bool
    detail: str


@dataclass(frozen=True)
class EvalReport:
    outcomes: tuple[QuestionOutcome, ...]
    answerable_hits: int
    answerable_total: int
    unanswerable_hits: int
    unanswerable_total: int
    ungated_recall: int
    answerable_pass: bool
    unanswerable_pass: bool

    @property
    def passed(self) -> bool:
        return self.answerable_pass and self.unanswerable_pass


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
    return EvalSet(commit, tuple(questions))


def check_commit(index: Index, eval_set: EvalSet) -> None:
    if index.commit != eval_set.pinned_commit:
        raise EvalFormatError(
            f"index is for commit {index.commit}, eval set is pinned to "
            f"{eval_set.pinned_commit}; re-run ingest"
        )


def _passes(hits: int, total: int) -> bool:
    return hits * 5 >= total * 4


def score(searcher: Searcher, eval_set: EvalSet) -> EvalReport:
    outcomes: list[QuestionOutcome] = []
    a_hits = a_total = u_hits = u_total = recall = 0
    for q in eval_set.questions:
        result = retrieve(searcher, q.question)
        if q.answerable:
            a_total += 1
            terms = sorted(set(tokenize(q.question)))
            top = capped(searcher.rank(terms), searcher.index.params)
            if any(p.path in q.sources for p, _ in top):
                recall += 1
            matched = [h for h in result.hits if h.passage.path in q.sources]
            if result.confident and matched:
                a_hits += 1
                outcomes.append(
                    QuestionOutcome(q.id, True, True, f"{matched[0].passage.path} (rank {matched[0].rank})")
                )
            elif result.confident:
                got = ", ".join(dict.fromkeys(h.passage.path for h in result.hits))
                outcomes.append(
                    QuestionOutcome(q.id, True, False, f"expected {' | '.join(q.sources)}; got {got}")
                )
            else:
                outcomes.append(
                    QuestionOutcome(
                        q.id,
                        True,
                        False,
                        f"expected {' | '.join(q.sources)}; got no confident match "
                        f"({result.reason}, coverage {result.coverage:.2f})",
                    )
                )
        else:
            u_total += 1
            tag = " [hard negative]" if q.hard_negative else ""
            if not result.confident:
                u_hits += 1
                outcomes.append(
                    QuestionOutcome(
                        q.id,
                        False,
                        True,
                        f"no confident match ({result.reason}, coverage {result.coverage:.2f}){tag}",
                    )
                )
            else:
                outcomes.append(
                    QuestionOutcome(
                        q.id,
                        False,
                        False,
                        f"returned {len(result.hits)} passages; top {result.hits[0].passage.path} "
                        f"(coverage {result.coverage:.2f}){tag}",
                    )
                )
    return EvalReport(
        tuple(outcomes),
        a_hits,
        a_total,
        u_hits,
        u_total,
        recall,
        _passes(a_hits, a_total),
        _passes(u_hits, u_total),
    )


def _pct(hits: int, total: int) -> str:
    return f"{(100.0 * hits / total) if total else 0.0:.1f}%"


def format_report(report: EvalReport, eval_file: str, index: Index) -> str:
    lines = [
        f"eval: {eval_file}  index: {index.repo} @ {index.commit[:8]}…  threshold: {index.threshold:.3f}"
    ]
    for o in report.outcomes:
        lines.append(f"{o.id}  {'HIT' if o.hit else 'MISS':<6}{o.detail}")
    a_verdict = "PASS" if report.answerable_pass else "FAIL"
    u_verdict = "PASS" if report.unanswerable_pass else "FAIL"
    lines.append(
        f"answerable:   {report.answerable_hits}/{report.answerable_total} "
        f"({_pct(report.answerable_hits, report.answerable_total)})  "
        f"required >= {REQUIRED_PERCENT}%  {a_verdict}"
    )
    lines.append(
        f"unanswerable: {report.unanswerable_hits}/{report.unanswerable_total} "
        f"({_pct(report.unanswerable_hits, report.unanswerable_total)})  "
        f"required >= {REQUIRED_PERCENT}%  {u_verdict}"
    )
    lines.append(
        f"diagnostic:   ungated recall@5 {report.ungated_recall}/{report.answerable_total} (not a gate)"
    )
    lines.append(f"eval: {'PASS' if report.passed else 'FAIL'}")
    return "\n".join(lines)
