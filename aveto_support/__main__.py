"""Command line: ingest | retrieve | eval. Exit codes: 0 ok, 1 eval below 80%, 2 input, 3 fetch."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aveto_support.embed import Embedder
    from aveto_support.index import Index
    from aveto_support.judge import Judge, JudgeParams
    from aveto_support.rerank import Reranker
    from aveto_support.search import (
        Abstention,
        FileHit,
        JudgeVerdict,
        PassageMatch,
        RetrievalResult,
    )

DEFAULT_CONFIG = "docs-source.toml"
DEFAULT_INDEX = "index/docs-index.json"
DEFAULT_EVAL = "evals/retrieval.toml"
DEFAULT_MODELS = "models"
DEFAULT_RANKING = "file-rrf-v1"
RANKINGS = ("file-rrf-v1", "file-rerank-v1")


def _excerpt(match: PassageMatch) -> list[str]:
    p = match.passage
    lines = p.text.split("\n")
    body = lines[1:] if p.heading_path else lines
    out: list[str] = []
    for line in body:
        if line.strip() == "":
            continue
        out.append("      | " + (line if len(line) <= 160 else line[:159] + "…"))
        if len(out) == 3:
            break
    return out


def _format_file(hit: FileHit) -> str:
    parts = [f"{hit.rank}. {hit.path}  (score {hit.score:.4f})", f"   {hit.url}"]
    for letter, match in zip("abcdefghij", hit.passages, strict=False):
        p = match.passage
        heading = " > ".join(p.heading_path) if p.heading_path else "(top of file)"
        parts.append(f"   {letter}. lines {p.line_start}-{p.line_end}  Heading: {heading}")
        parts.append(f"      {match.url}")
        parts.extend(_excerpt(match))
    return "\n".join(parts)


def _judge_detail(verdict: JudgeVerdict, params: JudgeParams) -> str:
    return f"{params.method}: best of {verdict.pairs} shown passages p={verdict.best:.3f}"


def format_result(
    result: RetrievalResult,
    index: Index,
    verdict: JudgeVerdict | None = None,
    params: JudgeParams | None = None,
) -> str:
    parts = [
        f"Sources for: {result.question}",
        f"Docs: {index.repo} @ {index.commit}",
        f"Ranking: {result.ranking_mode}  no text generated",
        (
            f"Top score: {result.top_score:.3f} (best passage similarity; ingest reference "
            f"{result.reference:.3f}, reported only)"
        ),
    ]
    if verdict is not None and params is not None:
        parts.append(
            f"Judge: answers ({_judge_detail(verdict, params)} >= {verdict.threshold:.2f}; "
            f"{params.model}@{params.revision})"
        )
    parts.append("")
    parts.extend(_format_file(f) for f in result.files)
    parts.append("")
    parts.append("These are sources, not an answer.")
    return "\n".join(parts)


def format_abstention(abstention: Abstention, index: Index, params: JudgeParams) -> str:
    """Exactly: header, `no confident match`, the deciding signal. No file or passage."""
    verdict = abstention.verdict
    return "\n".join(
        [
            f"Sources for: {abstention.question}",
            f"Docs: {index.repo} @ {index.commit}",
            f"Ranking: {abstention.ranking_mode}  no text generated",
            "no confident match",
            (
                f"Decided by: answerability judge {params.model}@{params.revision} "
                f"({_judge_detail(verdict, params)} < {verdict.threshold:.2f})"
            ),
        ]
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aveto_support")
    sub = parser.add_subparsers(dest="command", required=True)
    ing = sub.add_parser("ingest", help="fetch the pinned docs and model, and build the index")
    ing.add_argument("--config", default=DEFAULT_CONFIG)
    ing.add_argument("--out", default=DEFAULT_INDEX)
    ing.add_argument(
        "--with-reranker",
        action="store_true",
        help="also fetch and hash-check the optional reranker (file-rerank-v1); off by default",
    )
    ret = sub.add_parser("retrieve", help="find the docs files for a question")
    ret.add_argument("--index", default=DEFAULT_INDEX)
    ret.add_argument("--ranking", choices=RANKINGS, default=DEFAULT_RANKING)
    ret.add_argument("question", nargs="+")
    ev = sub.add_parser("eval", help="score retrieval against an eval set")
    ev.add_argument("--index", default=DEFAULT_INDEX)
    ev.add_argument("--eval-file", default=DEFAULT_EVAL)
    ev.add_argument("--ranking", choices=RANKINGS, default=DEFAULT_RANKING)
    return parser


def _limit_threads() -> None:
    """Single-threaded numeric libraries, set before numpy is first imported."""
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"


def _dispatch(
    args: argparse.Namespace,
    embedder: Embedder | None,
    reranker: Reranker | None,
    judge: Judge | None,
    models_dir: Path,
) -> int:
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.evaluate import check_commit, format_report, load_eval_set, score
    from aveto_support.index import load_index
    from aveto_support.ingest import run_ingest
    from aveto_support.judge import DEFAULT_PARAMS as judge_params
    from aveto_support.judge import OnnxJudge
    from aveto_support.rerank import OnnxReranker
    from aveto_support.search import Abstention, Searcher, ranking_mode, respond

    if args.command == "ingest":
        report = run_ingest(
            Path(args.config),
            Path(args.out),
            models_dir=models_dir,
            embedder=embedder,
            with_reranker=args.with_reranker,
        )
        for warning in report.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        print(f"ingested {report.repo} @ {report.commit}")
        print(
            f"files indexed: {report.files_indexed}   passages: {report.passages}   "
            f"skipped files: {len(report.skipped)}   "
            f"empty sections dropped: {report.empty_sections_dropped}   "
            f"passages truncated for embedding: {report.truncated_for_embedding}"
        )
        offtopic = "none" if report.tau_offtopic is None else f"{report.tau_offtopic:.6f}"
        print(
            f"reference similarity: {report.threshold:.6f} (dense-null-v3: "
            f"tau_salad {report.tau_salad:.6f}, tau_offtopic {offtopic}; seed 20260926; "
            f"diagnostic, retrieval does not abstain)"
        )
        print(f"model files: {report.model_status} (sha256 verified before use)")
        print(f"judge files: {report.judge_status} (sha256 verified before use)")
        if report.reranker_status == "not fetched":
            print(
                "reranker files: not fetched (optional; ingest --with-reranker fetches them "
                "for --ranking file-rerank-v1)"
            )
        else:
            print(f"reranker files: {report.reranker_status} (sha256 verified before use)")
        print(f"wrote {args.out}  sha256 {report.sha256}")
        return 0
    index = load_index(Path(args.index))
    # Adapters this function loads are closed here, judge first; injected ones belong to the caller.
    loaded_embedder: OnnxEmbedder | None = None
    loaded_reranker: OnnxReranker | None = None
    loaded_judge: OnnxJudge | None = None
    try:
        active = embedder
        if active is None:
            active = loaded_embedder = OnnxEmbedder.load(models_dir, index.params.embedding)
        active_reranker: Reranker | None = None
        if args.ranking == "file-rerank-v1":
            active_reranker = reranker
            if active_reranker is None:
                active_reranker = loaded_reranker = OnnxReranker.load(models_dir)
        active_judge = judge
        if active_judge is None:
            active_judge = loaded_judge = OnnxJudge.load(models_dir, judge_params)
        searcher = Searcher(index, active, active_reranker)
        if args.command == "retrieve":
            # Output is built only after the judge has scored every shown passage (INV-4).
            outcome = respond(searcher, active_judge, judge_params, " ".join(args.question))
            if isinstance(outcome, Abstention):
                print(format_abstention(outcome, index, judge_params))
            else:
                print(format_result(outcome.result, index, outcome.verdict, judge_params))
            return 0
        eval_set = load_eval_set(Path(args.eval_file))
        check_commit(index, eval_set)
        report_eval = score(searcher, eval_set, active_judge, judge_params)
        text = format_report(report_eval, args.eval_file, index)
        print(f"Ranking: {ranking_mode(searcher)}")
        # evaluate.py labels its header file-rrf-v1; name the method that actually ran.
        print(text.replace("ranking: file-rrf-v1", f"ranking: {args.ranking}", 1))
        return 0 if report_eval.passed else 1
    finally:
        if loaded_judge is not None:
            loaded_judge.close()
        if loaded_reranker is not None:
            loaded_reranker.close()
        if loaded_embedder is not None:
            loaded_embedder.close()


def main(
    argv: Sequence[str] | None = None,
    *,
    embedder: Embedder | None = None,
    reranker: Reranker | None = None,
    judge: Judge | None = None,
    models_dir: Path = Path(DEFAULT_MODELS),
) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    _limit_threads()
    from aveto_support.embed import ModelError
    from aveto_support.evaluate import EvalFormatError
    from aveto_support.index import IndexFormatError
    from aveto_support.ingest import ConfigError, FetchError

    try:
        return _dispatch(args, embedder, reranker, judge, models_dir)
    except (ConfigError, IndexFormatError, EvalFormatError, ModelError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
