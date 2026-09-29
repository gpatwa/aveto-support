"""Command line: ingest | retrieve | eval. Exit codes: 0 ok, 1 eval miss, 2 input, 3 fetch."""

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
    from aveto_support.search import Hit, RetrievalResult

DEFAULT_CONFIG = "docs-source.toml"
DEFAULT_INDEX = "index/docs-index.json"
DEFAULT_EVAL = "evals/retrieval.toml"
DEFAULT_MODELS = "models"


def _excerpt(hit: Hit) -> list[str]:
    lines = hit.passage.text.split("\n")
    body = lines[1:] if hit.passage.heading_path else lines
    out: list[str] = []
    for line in body:
        if line.strip() == "":
            continue
        out.append("   | " + (line if len(line) <= 160 else line[:159] + "…"))
        if len(out) == 3:
            break
    return out


def _format_hit(hit: Hit) -> str:
    p = hit.passage
    heading = " > ".join(p.heading_path) if p.heading_path else "(top of file)"
    head = [
        f"{hit.rank}. {p.path}  lines {p.line_start}-{p.line_end}",
        f"   Heading: {heading}",
        f"   {hit.url}",
    ]
    return "\n".join(head + _excerpt(hit))


def format_result(result: RetrievalResult, index: Index) -> str:
    docs = f"Docs: {index.repo} @ {index.commit}"
    if not result.confident:
        reason: str = result.reason
        if result.reason == "below-threshold":
            reason += (
                f" (best similarity {result.confidence:.3f}, threshold {result.threshold:.3f})"
            )
        return f"no confident match\n{docs}\nReason: {reason}"
    parts = [
        f"Sources for: {result.question}",
        docs,
        (
            f"Confidence: {result.confidence:.3f} (threshold {result.threshold:.3f})  "
            f"ranking: {result.ranking_mode}  no text generated"
        ),
        f"Lexical corroboration (reported, not gated): {result.corroboration:.2f}",
        "",
    ]
    parts.extend(_format_hit(h) for h in result.hits)
    parts.append("")
    parts.append("These are sources, not an answer.")
    return "\n".join(parts)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aveto_support")
    sub = parser.add_subparsers(dest="command", required=True)
    ing = sub.add_parser("ingest", help="fetch the pinned docs and model, and build the index")
    ing.add_argument("--config", default=DEFAULT_CONFIG)
    ing.add_argument("--out", default=DEFAULT_INDEX)
    ret = sub.add_parser("retrieve", help="find passages for a question")
    ret.add_argument("--index", default=DEFAULT_INDEX)
    ret.add_argument("question", nargs="+")
    ev = sub.add_parser("eval", help="score retrieval against an eval set")
    ev.add_argument("--index", default=DEFAULT_INDEX)
    ev.add_argument("--eval-file", default=DEFAULT_EVAL)
    return parser


def _limit_threads() -> None:
    """Single-threaded numeric libraries, set before numpy is first imported."""
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"


def _dispatch(args: argparse.Namespace, embedder: Embedder | None, models_dir: Path) -> int:
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.evaluate import check_commit, format_report, load_eval_set, score
    from aveto_support.index import load_index
    from aveto_support.ingest import run_ingest
    from aveto_support.search import Searcher, retrieve

    if args.command == "ingest":
        report = run_ingest(
            Path(args.config), Path(args.out), models_dir=models_dir, embedder=embedder
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
            f"confidence threshold: {report.threshold:.6f} (dense-null-v3: "
            f"tau_salad {report.tau_salad:.6f}, tau_offtopic {offtopic}; seed 20260926)"
        )
        print(f"model files: {report.model_status} (sha256 verified before use)")
        print(f"wrote {args.out}  sha256 {report.sha256}")
        return 0
    index = load_index(Path(args.index))
    active = embedder if embedder is not None else OnnxEmbedder.load(models_dir, index.params.embedding)
    searcher = Searcher(index, active)
    if args.command == "retrieve":
        print(format_result(retrieve(searcher, " ".join(args.question)), index))
        return 0
    eval_set = load_eval_set(Path(args.eval_file))
    check_commit(index, eval_set)
    report_eval = score(searcher, eval_set)
    print(format_report(report_eval, args.eval_file, index))
    return 0 if report_eval.passed else 1


def main(
    argv: Sequence[str] | None = None,
    *,
    embedder: Embedder | None = None,
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
        return _dispatch(args, embedder, models_dir)
    except (ConfigError, IndexFormatError, EvalFormatError, ModelError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
