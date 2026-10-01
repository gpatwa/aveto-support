# Implementation: docs-retrieval-3 (backend-architect, depth standard)

**Last commit:** `8499c2a778b739b08cc41e7fa2ac24e46ce3422c` on `claude/docs-retrieval-3`, three commits over 36c9cff: (1) A2 wording, (2) code and tests, (3) `.agentic` docs.

## First act: open check
`tokenizer_config.json` at revision 233902d2... fetched by HTTPS GET only (not kept): `do_lower_case: true`, `BertTokenizer`, `model_max_length` 512. Holds; proceeded.

## What changed
- `aveto_support/rerank.py` (new): `RerankParams` pinned to the approved id, revision and both sha256s (`onnx` 5d3e70fd...4d4a, `vocab` 07eced37...38a3); `Reranker` protocol; throwing `PlaceholderReranker`; `encode_pair` (question cap 64, 512 total); `OnnxReranker` (re-hashes both files on load, one thread, batch 1, checks inputs and `[batch,1]` output, non-finite score raises `ModelError`).
- `search.py`: `Searcher(reranker=None)`; `retrieve` is the old first stage plus, when a reranker is set, MaxP over the shown passages of the top 20 files, sorted `(-score, first-stage rank)`; `ranking_mode()`. With no reranker the output is the old output (all prior tests pass unedited).
- `ingest.py`: `ensure_reranker_files`, `_ModelPin`, `run_ingest` fetches and loads the reranker only when it also fetches the embedder; `IngestReport.reranker_status`.
- `__main__.py`: `--ranking {file-rerank-v1,file-rrf-v1}` on `retrieve` and `eval`, default `file-rerank-v1`; `main(reranker=)`; no fallback (missing files exit 2, "run ingest"); `eval` prints `Ranking:` first; `ingest` prints the reranker status line.
- `.agentic/SAFETY_INVARIANTS.md`: A2.1 and A2.2 applied verbatim by script from `02-approval-request.md`; no other edit.
- `.agentic/LOCAL_COMMANDS.md`, `CURRENT_MVP_STATUS.md`: flag, reranker files, latency, two-stage description.

## Files (11 committed + ADR 0005 by the Architect, untracked; 12 of 13)
`aveto_support/{rerank,search,ingest,__main__}.py`, `tests/{test_rerank,conftest,test_ingest,test_evaluate}.py`, `.agentic/{SAFETY_INVARIANTS,LOCAL_COMMANDS,CURRENT_MVP_STATUS}.md`. Untouched (diff vs 36c9cff empty): `embed.py`, `index.py`, `evaluate.py`, `docs-source.toml`, `test_search.py`, `test_index.py`, `tests/fixtures/*`, `pyproject.toml`, `uv.lock`, `evals/`.

## Tests and regression (after the last commit)
`uv sync --locked`, `uv run mypy` (15 files clean), `uv run ruff check` (clean), `uv run pytest`: 157 passed, 10 deselected. `uv run pytest -m model`: 7 passed (tokenizer golden for the reranker vocab, signature, repeatability, known answer, plus existing). All test names in A2.1 and A2.2 exist and pass. Live fetch test (`-m network`) written, not run (the real `ingest` is the live evidence). `ingest` twice: index sha256 `f36ef5d4...a756` both times, equal to slice 2's; second run reported reranker files `cached`. `SSL_CERT_FILE=/etc/ssl/cert.pem` was needed per `LOCAL_COMMANDS.md`.

## Measured latency (own non-eval questions, three, whole process)
2.3 s to 3.8 s per `retrieve` with the reranker (model load included); 0.9 s with `--ranking file-rrf-v1`. Inside the 2 to 2.5 s per question estimate once load is excluded. N unchanged.

## Method files (for the freeze)
`aveto_support/rerank.py`, `search.py`, `embed.py`, `index.py`, `ingest.py`, `__main__.py`, `evaluate.py`, `docs-source.toml`.

## Deviations and flags
1. **`evaluate.py` hardcodes `ranking: file-rrf-v1` in its report header** (line 138). The file is frozen and out of the file list, so `__main__` replaces that label in the printed header with the method that actually ran (`str.replace`, first occurrence). A cleaner fix is a later edit of `evaluate.py` (would be file 13). The Orchestrator should decide before the freeze.
2. `test_cli_retrieve_output_shape` (existing) now runs with `--ranking file-rrf-v1` and no reranker to keep its assertion unchanged (it asserts the `file-rrf-v1` `Ranking:` line); other existing CLI calls inject `FakeReranker`.
3. Ran the real `ingest` (approved fetch) in this worktree: it also downloaded the embedding model (pinned in `docs-source.toml`, no other file), because `models/` did not exist. No eval, no `evals/` file read; `retrieve` only on three own questions about the repo.
4. `ADR 0005` and `runs/docs-retrieval-3/` remain untracked, as left by earlier stages; not committed here.
