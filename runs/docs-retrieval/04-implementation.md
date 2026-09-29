# Implementation note: embed-v3 (with the lexical v2 changes it builds on)

Slice docs-retrieval-core. Author: backend-architect. Date: 2026-09-29. Depth: standard.
Everything is uncommitted; the Orchestrator commits.

## What was built

Per `02-tech-spec.md`, "Retrieval — variant v2" and "Retrieval — variant embed-v3".

- Porter 1980 stemmer (plain Python, in `search.py`), ranking-v2 (passage BM25 plus file-level
  BM25, lambda 0.5), corroboration (reported, not gated).
- Local embedding: `aveto_support/embed.py` (new): `Embedder` protocol, `OnnxEmbedder`,
  `PlaceholderEmbedder` (raises "embedding model is not configured in this build."),
  plain-Python BERT WordPiece, int8 quantisation.
- Hybrid ranking `hybrid-v3` (RRF k=60, depth 100, then per-file cap 2 and top 5); confidence
  `dense-null-v3` (tau = max(tau_salad, tau_offtopic)); index@3 with base64 int8 vectors.
- `ingest` downloads exactly `onnx/model.onnx` and `vocab.txt` from huggingface.co
  (redirects only to `huggingface.co` / `*.hf.co`), hashing while streaming; a mismatch
  deletes the temp file and raises `FetchError` (exit 3). Cached files are re-hashed before
  every use; a mismatch at load deletes the file and exits 2. `retrieve` and `eval` never download.

## Files (count check against the spec's list of 19)

Changed or created, 18: `pyproject.toml`, `uv.lock`, `docs-source.toml`, `.gitignore`,
`aveto_support/__main__.py`, `ingest.py`, `index.py`, `search.py`, `evaluate.py`,
`embed.py` (new), `tests/conftest.py`, `test_ingest.py`, `test_index.py`, `test_search.py`,
`test_evaluate.py`, `README.md`, `.agentic/LOCAL_COMMANDS.md`, `.agentic/CURRENT_MVP_STATUS.md`.
`aveto_support/__init__.py` (the 19th) is unchanged, as the spec says. Not touched:
`evals/*`, `.claude/`, `.agentic/SAFETY_INVARIANTS.md`, `tests/fixtures/`. Also written:
this note and the Implementation row and Next action in `STATE.md`. No 20th file.

## Dependencies (measured)

`uv tree`: 18 packages resolved in total (including dev). Runtime set is 5 packages:
`numpy` 2.5.3 and `onnxruntime` 1.30.0 (top-level, nothing else), plus `flatbuffers` 25.12.19,
`packaging` 26.3 and `protobuf` 7.36.2. New top-level dependencies beyond the two approved: none.
Installed size: `.venv` is 199 MB in total including dev tools (mypy, pytest, ruff);
onnxruntime about 77 MB and numpy about 22 MB. Model cache `models/` is 129 MB (133.3 MB
downloaded, hence 129 MiB).

## Verified hashes and graph signature

- `onnx/model.onnx`: sha256 `828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35`,
  133,093,490 bytes. **Matched the pin.**
- `vocab.txt`: sha256 `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`,
  231,508 bytes. **Matched the pin.** The REPORTED vocab hash is now verified.
  (`test_live_model_download_verifies_hashes` and the ingest download both checked it.)
- ONNX graph signature observed: inputs `input_ids`, `attention_mask`, `token_type_ids`;
  one output `last_hidden_state`, shape `[batch_size, sequence_length, 384]`, float. Matches
  the spec. `test_onnx_graph_signature` passes.

## Gate evidence

- `uv sync --locked`: ok. `uv run mypy`: no issues (12 files). `uv run ruff check`: all checks passed.
- `uv run pytest`: 118 passed, 5 deselected (model and network marked).
- `uv run pytest -m model`: 2 passed, 1 failed. The failure is `test_wordpiece_matches_golden`,
  expected: `tests/fixtures/wordpiece_golden.json` is QA's file and does not exist yet; the
  test fails loudly with that message and never skips. `test_onnx_graph_signature` and
  `test_onnx_embedding_is_repeatable` pass.
- `uv run pytest -m network`: 2 passed (`test_live_model_download_verifies_hashes`,
  `test_live_ingest_byte_identical`), 2 min 32 s.

## Determinism evidence

Three real ingests of the pinned commit (two after the model was cached) produced
the same file, sha256
`1f6b2194db040446aa09ba6021d30a80df4361bcbc1e9c2958292c97d0cbe5c9` (`cmp` identical),
size 1,218,356 bytes. `test_live_ingest_byte_identical` also compares two runs.
The synthetic tests cover member reordering. `test_onnx_embedding_is_repeatable` gives bitwise-equal
int8 vectors across two sessions. Same machine and same Python only; cross-machine identity is not claimed.

## Ingest numbers and timings (macOS laptop, single-threaded)

126 files, 910 passages, 0 skipped, 32 empty sections dropped, 27 passages truncated for embedding.
tau_salad 0.701779, tau_offtopic 0.696323, threshold 0.701779.
First ingest with the model download: 81 s wall clock. Cached ingest: about 79 s, so the download
itself is a few seconds; embedding 910 passages plus 2000 salad queries and the off-topic
list dominates. (Needs `SSL_CERT_FILE=/etc/ssl/cert.pem` with python.org Python on macOS.)

## Hand checks (my own questions, not from any eval set)

- "how can I install the pack into an existing repository": confident, 3 or more passages
  with path, heading, line range and permalink.
- "what is the capital of France": `no confident match` (below-threshold, best similarity
  0.486 against 0.702). An empty question: `no-searchable-words`.
No recall figure was computed.

## Not done, on purpose

- **`eval` was not run, on any set.** No recall figure was computed.
- **`evals/calibration-offtopic.toml` was not opened, read, printed or grepped.** The code loads
  it by path after checking its sha256 against `docs-source.toml`; unit tests use synthetic
  lists defined inside the tests. The ingest report prints only aggregate values. No held-out
  question file was read, and `evals/retrieval.toml` was not used in any test beyond the one
  structural sanity test and the live path-agreement check (paths only).
- `tests/fixtures/wordpiece_golden.json` was not created.

## Deviations from the spec, and why

1. **Model identity fields are data in the index, not compared to code constants.**
   `load_index` compares every fixed constant (dim, prefix, quantisation, fusion, rrf_k,
   depth, confidence, and the lexical params) with the code and rejects a mismatch, but treats
   `model`, `revision`, both sha256 values and `offtopic_sha256` as validated data (40 or 64
   lowercase hex). Reason: the spec makes the model pin configurable in `docs-source.toml`, and
   `retrieve` builds its embedder from the index's own recorded pin, so it cannot ask a config file.
2. **`Embedder` gained `token_count(text)`.** It is needed for "no-searchable-words" (no
   WordPiece tokens beyond the prefix) and for counting truncated passages, without changing the
   spec's `embed_passage`/`embed_query`.
3. **`Passage.embedding` (bytes, default empty), `Index.tau_salad`, `tau_offtopic` and
   `truncated_for_embedding`** were added as fields; `counts.truncated_for_embedding` is in the index.
4. **`RetrievalResult`** keeps `coverage` renamed to `confidence` (the dense similarity), adds
   `corroboration` and `ranking_mode`, per the spec's proposal.
5. **`main(argv, *, embedder=None, models_dir=Path("models"))`** takes two keyword-only test hooks.
   `__main__` imports project modules inside functions so thread-limit env vars are set before
   numpy is first imported (keeping ruff's default E402 rule clean without an ignore).
6. `docs-source.toml` `[embedding]` key names (`onnx_sha256`, `vocab_sha256`, `offtopic_path`,
   `offtopic_sha256`) are mine; the spec named the contents but not the keys. `offtopic_path` is
   resolved relative to the config file's folder.
7. Download cap: 200,000,000 bytes per model file (a constant). Not in the spec.
8. `pyproject.toml` also has `pythonpath = ["."]` (from the first pass) and a mypy override
   ignoring missing stubs for `onnxruntime`.
9. The off-topic loader also rejects an off-topic file with no `[[question]]` entries, and warns
   when it has fewer than 50. It does not check the file's `pinned_commit`, because the spec does not require it.

No pre-registered value (parameters, weights, quantiles, seed, tau rule) was changed.
