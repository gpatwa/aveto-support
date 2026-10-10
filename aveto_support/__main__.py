"""Command line: ingest | retrieve | eval | judge-input | judge-apply.

Exit codes: 0 ok, 1 eval below 80%, 2 input, 3 fetch, 4 judge error (judge-apply only).
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aveto_support.embed import Embedder
    from aveto_support.index import Index
    from aveto_support.rerank import Reranker
    from aveto_support.search import FileHit, PassageMatch, RetrievalResult, Searcher

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


def format_result(result: RetrievalResult, index: Index) -> str:
    parts = [
        f"Sources for: {result.question}",
        f"Docs: {index.repo} @ {index.commit}",
        f"Ranking: {result.ranking_mode}  no text generated",
        (
            f"Top score: {result.top_score:.3f} (best passage similarity; ingest reference "
            f"{result.reference:.3f}, reported only: retrieval does not decide whether the docs answer)"
        ),
        "",
    ]
    parts.extend(_format_file(f) for f in result.files)
    parts.append("")
    parts.append("These are sources, not an answer.")
    return "\n".join(parts)


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
    ev.add_argument(
        "--verdicts",
        default=None,
        help="also score the answerability bars from a judge verdicts file (reported, not gated)",
    )
    ji = sub.add_parser("judge-input", help="print the answerability judge's payload for a question")
    ji.add_argument("--index", default=DEFAULT_INDEX)
    ji.add_argument("--question-file", default=None)
    ji.add_argument("question", nargs="*")
    ja = sub.add_parser("judge-apply", help="apply one judge verdict to that same payload")
    ja.add_argument("--index", default=DEFAULT_INDEX)
    ja.add_argument("--question-file", default=None)
    ja.add_argument("--input-sha256", required=True)
    ja.add_argument("--verdict-file", required=True)
    ja.add_argument("question", nargs="*")
    return parser


def _limit_threads() -> None:
    """Single-threaded numeric libraries, set before numpy is first imported."""
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"


def _with_searcher[T](
    index_path: str,
    embedder: Embedder | None,
    models_dir: Path,
    fn: Callable[[Searcher, Index], T],
) -> T:
    """Load the index and embedder, run `fn` with the default ranking, close what was loaded."""
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.index import load_index
    from aveto_support.search import Searcher

    index = load_index(Path(index_path))
    loaded: OnnxEmbedder | None = None
    try:
        active = embedder
        if active is None:
            active = loaded = OnnxEmbedder.load(models_dir, index.params.embedding)
        return fn(Searcher(index, active), index)
    finally:
        if loaded is not None:
            loaded.close()


def _raw_question(args: argparse.Namespace) -> str:
    from aveto_support.judge import QuestionFormatError, read_question_file

    if (args.question_file is None) == (not args.question):
        raise QuestionFormatError("give exactly one of --question-file or the question words")
    if args.question_file is not None:
        return read_question_file(Path(args.question_file))
    return " ".join(args.question)


def _judge_input(args: argparse.Namespace, embedder: Embedder | None, models_dir: Path) -> int:
    from aveto_support import judge

    judge.remove_stale_reply()
    raw = _raw_question(args)
    block = _with_searcher(
        args.index,
        embedder,
        models_dir,
        lambda searcher, _: judge.format_judge_input(judge.retrieve_for_judge(searcher, raw)),
    )
    sys.stdout.write(block)
    print(f"input sha256: {judge.input_sha256(block)}", file=sys.stderr)
    return 0


def _apply_verdict(
    args: argparse.Namespace, embedder: Embedder | None, models_dir: Path
) -> tuple[str, int]:
    """Steps 1-5 of judge-apply. Returns (stdout text, exit code 0) or raises."""
    from aveto_support import judge

    safe, category = judge.transport_file(Path(args.verdict_file))
    if safe is None:
        raise judge.JudgeError(category or judge.OUTSIDE)
    reply = judge.read_reply(safe)
    raw = _raw_question(args)

    def build(searcher: Searcher, index: Index) -> tuple[RetrievalResult, Index]:
        return judge.retrieve_for_judge(searcher, raw), index

    result, index = _with_searcher(args.index, embedder, models_dir, build)
    if judge.input_sha256(judge.format_judge_input(result)) != args.input_sha256:
        raise judge.JudgeError(judge.DIFFERENT_INPUT)
    verdict = judge.parse_verdict(reply, judge.BLOCK_ID)
    return judge.render_applied(verdict, result, index), 0


def _judge_apply(args: argparse.Namespace, embedder: Embedder | None, models_dir: Path) -> int:
    """Compute, then delete the transport files, then print (so a deletion failure never
    follows an already-printed judged result). Runs the deletion on every path."""
    from aveto_support import judge

    out, code = "", 0
    err = ""
    pending: Exception | None = None
    try:
        out, code = _apply_verdict(args, embedder, models_dir)
    except judge.JudgeError as exc:
        out, err, code = "judge error\n", f"judge error: {exc.category}\n", 4
    except Exception as exc:  # noqa: BLE001  re-raised below, after the transport files are gone
        pending = exc
    files = [Path(args.verdict_file)]
    if args.question_file is not None:
        files.append(Path(args.question_file))
    if not judge.delete_transport_files(files):
        sys.stdout.write("judge error\n")
        sys.stderr.write(f"judge error: {judge.NOT_DELETED}\n")
        return 4
    if pending is not None:
        raise pending
    sys.stdout.write(out)
    sys.stderr.write(err)
    return code


def _dispatch(
    args: argparse.Namespace,
    embedder: Embedder | None,
    reranker: Reranker | None,
    models_dir: Path,
) -> int:
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.evaluate import check_commit, format_report, load_eval_set, score
    from aveto_support.index import load_index
    from aveto_support.ingest import run_ingest
    from aveto_support.rerank import OnnxReranker
    from aveto_support.search import Searcher, ranking_mode, retrieve

    if args.command == "judge-input":
        return _judge_input(args, embedder, models_dir)
    if args.command == "judge-apply":
        return _judge_apply(args, embedder, models_dir)
    if args.command == "eval" and args.verdicts is not None and args.ranking != DEFAULT_RANKING:
        from aveto_support.judge_eval import VerdictsFormatError

        raise VerdictsFormatError(
            f"--verdicts needs --ranking {DEFAULT_RANKING}: the judge was measured on that ranking only"
        )
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
    # Adapters this function loads are closed here, reranker first; injected ones belong to the caller.
    loaded_embedder: OnnxEmbedder | None = None
    loaded_reranker: OnnxReranker | None = None
    try:
        active = embedder
        if active is None:
            active = loaded_embedder = OnnxEmbedder.load(models_dir, index.params.embedding)
        active_reranker: Reranker | None = None
        if args.ranking == "file-rerank-v1":
            active_reranker = reranker
            if active_reranker is None:
                active_reranker = loaded_reranker = OnnxReranker.load(models_dir)
        searcher = Searcher(index, active, active_reranker)
        if args.command == "retrieve":
            print(format_result(retrieve(searcher, " ".join(args.question)), index))
            return 0
        eval_set = load_eval_set(Path(args.eval_file))
        check_commit(index, eval_set)
        judge_text = None
        if args.verdicts is not None:  # built before any output, so a bad file prints no report
            from aveto_support.judge_eval import judge_section

            judge_text = judge_section(searcher, eval_set, Path(args.verdicts))
        print(f"Ranking: {ranking_mode(searcher)}")
        report_eval = score(searcher, eval_set)
        text = format_report(report_eval, args.eval_file, index)
        # evaluate.py (frozen) labels its header file-rrf-v1; name the method that actually ran.
        print(text.replace("ranking: file-rrf-v1", f"ranking: {args.ranking}", 1))
        if judge_text is not None:
            print(judge_text)
        return 0 if report_eval.passed else 1
    finally:
        if loaded_reranker is not None:
            loaded_reranker.close()
        if loaded_embedder is not None:
            loaded_embedder.close()


def main(
    argv: Sequence[str] | None = None,
    *,
    embedder: Embedder | None = None,
    reranker: Reranker | None = None,
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
    from aveto_support.judge import (
        PayloadMarkerError,
        QuestionFormatError,
        TransportError,
    )
    from aveto_support.judge_eval import VerdictsFormatError

    try:
        return _dispatch(args, embedder, reranker, models_dir)
    except (
        ConfigError,
        IndexFormatError,
        EvalFormatError,
        ModelError,
        QuestionFormatError,
        PayloadMarkerError,
        TransportError,
        VerdictsFormatError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
