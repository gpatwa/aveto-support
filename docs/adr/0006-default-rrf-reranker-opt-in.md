# ADR 0006: `file-rrf-v1` is the default ranking; the reranker is opt-in, and ONNX sessions are closed by their owner

> Architecture Decision Record. Owned by the Architect. Never edited after it is accepted. A changed decision gets a new record that supersedes this one.

- **Status:** proposed. It becomes accepted when the owner approves the INV-5 wording (rule 4, `runs/docs-retrieval-4/APPROVAL_RECORD-1.md`) and slice `docs-retrieval-4` passes its Release Gate.
- **Date:** 2026-10-03
- **Slice:** `runs/docs-retrieval-4/`. Full specification: `runs/docs-retrieval-4/02-tech-spec.md`.
- **Relates to:** ADR 0005 (the reranker is kept as specified, off by default).

## Context

Across four held-out sets, the reranker (`file-rerank-v1`, ADR 0005) did no better than `file-rrf-v1` and cost 2.3-3.8 s a question against 0.9 s. It met slice 3's gate by exactly the minimum, where `file-rrf-v1` scored 14/16 on the same set. `ingest` fetched and loaded the reranker unconditionally. A process holding two ONNX Runtime sessions aborted intermittently at teardown (exit 134, `recursive_mutex lock failed: Invalid argument`).

## Decision

1. `retrieve` and `eval` default to `--ranking file-rrf-v1`. `file-rerank-v1` stays selectable and is unchanged.
2. `ingest` fetches and loads the reranker's pinned files only with `--with-reranker`. By default, the only model it fetches is the embedding model. The index is byte-identical either way.
3. `--ranking file-rerank-v1` with the reranker's files absent fails closed (exit 2, with a message naming `ingest --with-reranker`) and never downloads.
4. Whoever loads an `OnnxEmbedder` / `OnnxReranker` closes it (`close()` drops the session) in a `finally`, in reverse order of creation, before control returns to the interpreter. Session lifetime no longer depends on Python finalisation order relative to ONNX Runtime's process-wide teardown.

## Alternatives considered

- **Keep the reranker as default:** it earned nothing across four sets, at 3-4x the latency.
- **Remove the reranker:** discards a working, hash-pinned, INV-4-tested option. Keeping it off costs only the opt-in path.
- **A config key instead of a flag:** it would put an egress choice in `docs-source.toml`, and a flag is visible per run.
- **`os._exit` to skip teardown:** it would skip teardown rather than manage it, and drops `atexit` and stderr flushing.
- **Changing ONNX Runtime options or version:** threads are already 1/1/sequential, and a version change is a new dependency decision.

## Consequences

- **Easier:** the default path has one model, one session and one download. The MS MARCO licence question does not apply to the default path; it stays open for anyone who opts in (`--with-reranker`). Our two adapters are now explicitly closed, in reverse order of creation, before interpreter shutdown (proven by `test_main_closes_loaded_adapters_in_reverse_order`). This is a property of the code, not a claim about exit codes.
- **Harder:** anyone using `file-rerank-v1` must run `ingest --with-reranker` first.
- **Unchanged:** the close discipline is not shown to fix the abort.
- **Status of the exit-134 abort: NOT REPRODUCED.** Unfixed code: `eval` with `file-rerank-v1`, 20 runs, 0 exit-134; `retrieve` with `file-rerank-v1`, 200 runs, 0 exit-134. Fixed code: `eval` 20 runs per mode, `retrieve` 200 runs per mode, 0 exit-134 and no signal exit anywhere. The loops cannot tell the fixed code from the unfixed code. The spec's hypothesised mechanism (sessions alive at interpreter finalisation) was not observed. The likeliest remaining reading is a lock inside ONNX Runtime's own teardown, which is a reading and not a finding. Slice 4 reports the abort as not reproduced, neither fixed nor explained.
