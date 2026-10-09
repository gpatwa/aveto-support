# Implementation: docs-retrieval-4

Backend Architect, standard depth. Commits on `claude/docs-retrieval-4`, nothing pushed.

## Crash (exit 134) status: NOT REPRODUCED

No "crash fixed" and no "explained" claim is made.

- The spec section 3.2 premise (an ONNX session wrapper still alive at interpreter finalisation) was NOT observed. On the unfixed code, a one-off `weakref` check around `main(["eval", ..., "--ranking", "file-rerank-v1"])` showed both the `OnnxEmbedder` and the `OnnxReranker` already dead when `main` returned, before any `gc.collect()`.
- Reading, not a finding: the spec's own fallback (the dead lock lives in ONNX Runtime's static teardown, which cannot be fixed here without a dependency change) is the likeliest remaining reading.
- `close()` on both adapters, and the `finally` closing in `__main__` and `ingest`, stay as tested ownership hygiene (explicit adapter ownership, closed in reverse order, proven by `test_main_closes_loaded_adapters_in_reverse_order`). They are not offered as the cure. No other fix was tried by trial.
- Only `file-rerank-v1` (two ORT sessions in one process) has ever aborted (once in eight runs, slice 3). The default path now builds one session. The default-mode runs may pass trivially.

### Counts (all on `evals/retrieval.toml` for eval; throwaway question "how do I install the package" for retrieve; exit code 0 / 1 / 134 / other)

Files: `runs/docs-retrieval-4/crash-evidence/`. Per-run exit codes, one line each, restartable scripts alongside.

| Loop | Code | Runs | 0 | 1 | 134 | other |
|------|------|------|---|---|-----|-------|
| eval, file-rerank-v1 (`prefix-unfixed-rerank-eval.txt`) | unfixed (6591bf3) | 20 | 0 | 20 | 0 | 0 |
| retrieve, file-rerank-v1 (`prefix-unfixed-rerank-retrieve200.txt`) | unfixed (6591bf3, scratch worktree, since removed) | 200 | 200 | 0 | 0 | 0 |
| eval, file-rrf-v1, default (`fixed-rrf-eval.txt`) | fixed | 20 | 0 | 20 | 0 | 0 |
| eval, file-rerank-v1 (`fixed-rerank-eval.txt`) | fixed | 20 | 0 | 20 | 0 | 0 |
| retrieve, file-rrf-v1 (`fixed-rrf-retrieve200.txt`) | fixed | 200 | 200 | 0 | 0 | 0 |
| retrieve, file-rerank-v1 (`fixed-rerank-retrieve200.txt`) | fixed | 200 | 200 | 0 | 0 | 0 |

Totals: unfixed 220 runs, fixed 440 runs, zero 134 and no signal exit anywhere. Exit 1 on eval is expected (the dev set misses its bar in both modes) and is not a failure. The unfixed code never aborted in 220 runs (plus 10 more eval runs from a mis-pathed first attempt, also all exit 1, whose file was deleted), so **these loops cannot discriminate the fix**: no before/after difference exists to see. The fixed runs show no regression, nothing stronger. Per mode: default mode (file-rrf-v1, one session) fixed 220 runs, 0 x 134; opt-in mode (file-rerank-v1, two sessions) fixed 220 runs, 0 x 134, unfixed 220 runs, 0 x 134.

Models and index for the loops were copied locally from the slice 3 worktree's `models/` and `index/` (gitignored, hash-checked at load, nothing downloaded). No eval set other than `evals/retrieval.toml` was run; the fourth, second and third sets were not.

## What changed, per file

Code and tests (7 of 7):
- `aveto_support/__main__.py`: `DEFAULT_RANKING = "file-rrf-v1"`, `RANKINGS` reordered, default on `retrieve` and `eval`; `ingest --with-reranker`; reranker report line (`not fetched (...)` or status); `_dispatch` closes the adapters it loaded (reranker, then embedder) in a `finally`; injected ones are untouched.
- `aveto_support/ingest.py`: `run_ingest(..., with_reranker=False)`. Default path fetches and loads only the embedder. Opt-in: `ensure_reranker_files` then a load-check closed at once. `"injected"` reranker status removed. Embedder it loaded is closed in a `finally`. The diff looks large only because the body after the embedder load is indented into that `try`.
- `aveto_support/rerank.py`: `OnnxReranker.close()`, closed-use guard, absent-files `ModelError` with the spec's message (exit 2, no download), hash-mismatch message gains `(reranker: run ingest --with-reranker)`.
- `aveto_support/embed.py`: `OnnxEmbedder.close()` and closed-use guard.
- `tests/test_ingest.py`: replaced `test_ingest_fetches_reranker_with_embedding`; added `test_default_ingest_fetches_no_reranker`, `test_default_ingest_cli_line_says_not_fetched`, `test_default_ingest_makes_no_reranker_request`, `test_ingest_with_reranker_fetches_and_rehashes`, `test_reranker_opt_in_does_not_change_index` (index bytes and sha256 identical), `test_ingest_closes_embedder_it_loaded`. `test_retrieve_is_offline_with_cached_reranker` now passes `--ranking file-rerank-v1` (same meaning).
- `tests/test_rerank.py`: `test_reranker_absent_fails_closed_without_download` (replaces `test_cli_default_mode_without_reranker_cache_exits_2`), `test_onnx_adapters_close_releases_session`; two existing CLI tests now pass `--ranking file-rerank-v1` explicitly.
- `tests/test_evaluate.py` (the one CLI file): `test_retrieve_default_ranking_is_rrf`, `test_eval_default_ranking_is_rrf`, `test_default_run_loads_no_reranker`, `test_rerank_ranking_still_selectable`, `test_main_closes_loaded_adapters_in_reverse_order` (exit 0, 1, 2; default mode; injected never closed).

Wording (6) plus the owner's exception (1): `.agentic/PROJECT_CONTEXT.md`, `.agentic/LOCAL_COMMANDS.md` (default ranking, `ingest --with-reranker` row), `.agentic/CURRENT_MVP_STATUS.md`, `README.md`, `docs/adr/0005-cross-encoder-reranker.md` (status note only), `.agentic/SAFETY_INVARIANTS.md` (INV-5, last), and `docs/ARCHITECTURE.md` (addendum 1: 14 files total with the ADR 0006 and run artefacts excluded).

Not touched: `search.py`, `evaluate.py`, `evals/*.toml`, `docs-source.toml`, `pyproject.toml`, `uv.lock`, the pinned constants, `verify_file`, the download functions, the INV-4 text.

## README correction (Orchestrator, after commit 15d311d)
The README status line first said "internally releasable". That is the Release Gate's verdict, not mine. It now reads "retrieval only; Security Review and Release Gate pending; not announced." A grep of README, `.agentic/`, `docs/ARCHITECTURE.md` and ADRs 0005/0006 for "releasable" and for crash-fixed wording found no other hit.

## INV-5
Applied last, after code, tests and loops. The sentence is the owner's, from `APPROVAL_RECORD-1.md`: "Of the two models, the default path fetches only the embedding model's files: `ingest` fetches the reranker's files only when run with `--with-reranker`." (bold on `ingest` and `--with-reranker` per file style), plus the four test names in the enforced-by list. Nothing else in the file changed. ADR 0006 does not quote the old sentence, so it needed no edit.

## Regression
`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`: mypy no issues (15 files), ruff all checks passed, 168 passed, 10 deselected. The autouse network block is untouched.

## Grep: "plain code" / "file-rerank-v1" outside the six wording files (report only)
- "plain code": `docs/adr/0001-python-fastapi-uv-no-agent-framework.md:95` (a different, still-true use: approval step is plain code).
- "file-rerank-v1": `docs/adr/0006-...` (this slice's ADR), `docs/adr/0005` (decision text, not edited) and the ARCHITECTURE addendum above. No other hit in `.agentic/`, `README.md` or `docs/`.

## Where the spec was wrong or incomplete
- Section 3.2's premise did not hold on the unfixed code (above). The spec's stop rule ("explained, not fixed") applies; I finished the specified, harmless ownership code and the evidence rather than stopping, because the rest of the slice does not depend on it. The owner should read the crash item as open.
- Section 6 assumed `models/` and `index/` were in this checkout; they live in the slice 3 worktree (copied, see above).
- The first loop script wrote its evidence to a relative path after a `cd`; fixed (absolute path required). No evidence was lost.
