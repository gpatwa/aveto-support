# ADR 0005: Re-order `file-rrf-v1`'s top 20 files with a local cross-encoder (`file-rerank-v1`)

> Architecture Decision Record. Owned by the Architect. Never edited after it is
> accepted. A changed decision gets a new ADR that supersedes this one.

- **Status:** proposed. Becomes accepted only if the owner approves the specific model (A1, rule 5) and the INV-5 wording (A2, rule 4), and slice B (`docs-retrieval-3-proof`) passes its held-out gate. If A1 is denied, this ADR is superseded before implementation.
- **Date:** 2026-09-30
- **Slice:** `runs/docs-retrieval-3/` (slice A, method to freeze). Full specification: `runs/docs-retrieval-3/02-tech-spec.md`. Approval request: `runs/docs-retrieval-3/02-approval-request.md`.
- **Supersedes:** nothing. Extends [ADR 0004](0004-file-level-ranking-and-fixed-corpus.md): its corpus, its first stage `file-rrf-v1`, its passages per file and its "retrieval never abstains" stand. The embedding model of [ADR 0003](0003-hybrid-embedding-retrieval.md) stands.

## Context

`file-rrf-v1` put a correct file in the top 5 for 11 of 16 fresh held-out questions (bar 13); the close-out's hypothesis is that narrow files lose to broader neighbours, and it names a reranker as the next question. The owner's intent (`docs-retrieval-3`) asks for one change: a local reranker that reads text and never produces it, pinned and hash-checked, on ONNX Runtime + numpy, with the reranker, N and the combination argued before any run.

**Disclosure.** Nothing here was chosen by a score on any eval set. The Architect read the close-out's one-line description of the five misses as motivation; it did not read any eval file, eval output or per-question rank.

## Decision

1. **Model:** `cross-encoder/ms-marco-MiniLM-L6-v2` (6-layer MiniLM, hidden 384, ~22.7M parameters, Apache-2.0 weights, trained on MS MARCO), its fp32 `onnx/model.onnx` and `vocab.txt` at one 40-hex revision, each sha256-pinned (values in the approval record). Run with `onnxruntime` on CPU, single-threaded, batch size 1. No PyTorch, no `trust_remote_code`, no new dependency.
2. **Tokenizer:** the existing `embed.WordPiece`, unchanged, over the reranker's own pinned `vocab.txt`, which is expected to be byte-identical to bge-small's (a precondition checked by hash). BERT pair layout; question capped at 64 tokens, pair at 512.
3. **Method `file-rerank-v1`:** `file-rrf-v1` ranks all files; its top **N = 20** are re-scored; a file's score is the **maximum** logit over the passages `file-rrf-v1` shows for it (at most 2); the 20 are ordered by that score alone, ties by first-stage rank; the top 5 are returned with the first stage's own passages, unchanged.
4. **Pin in code** (`aveto_support/rerank.py`, `RerankParams`), not in `docs-source.toml`; no index or schema change.
5. **Baseline kept:** `retrieve` and `eval` take `--ranking {file-rerank-v1,file-rrf-v1}` (default the reranker). No silent fallback: a missing reranker file is exit 2.
6. **INV-5 extended** to the reranker's files under the same host and hash rules; INV-4 unchanged apart from its list of enforcing tests (exact text in the approval request).

## Alternatives considered

- **The 12-layer sibling:** same reported quality, twice the CPU. **2- and 4-layer siblings, TinyBERT:** reported weaker.
- **bge-reranker, mxbai-rerank, gte-reranker-modernbert:** SentencePiece or BPE tokenizers (new code or a new library) and about 3 to 25 times the parameters. **jina-reranker:** needs `trust_remote_code`. **LLM rerankers and hosted APIs:** out of scope (generative; data leaves the machine).
- **RRF of first-stage and reranker orders:** halves the reranker's effect by construction. **Weighted score blend:** a weight with no principled value, chosen only by score.
- **Scoring every passage of each candidate file:** about 3.5 times the cost on average, unbounded for long files, and it would change which passages are shown.
- **N = 100 or the whole corpus:** the reranker becomes the sole ranker on a 123-file corpus. **N = 5 to 10:** too little room to fix a near miss.
- **Pin in `docs-source.toml`:** consistent with the embedding model, but `retrieve` and `eval` would need the config file or the index would need a schema change.

## Consequences

- Easier: a relevance judgement that reads question and passage together; the passages shown are unchanged, so provenance and INV-4 are untouched; `file-rrf-v1` stays one flag away for comparison and rollback.
- Harder: a third pinned download (~91 MB) on each fresh cache; about 2 seconds of CPU per question (estimate); results depend on float32 inference, so near-ties may differ across machines (the index does not).
- The reranker cannot be swapped by config, unlike the embedding model; a change is a code change and a new rule 5 approval.
- Domain shift (web questions to process documentation) is an accepted, reported risk. The training data's non-commercial terms are surfaced to the owner, not decided here.
- Nothing abstains yet; intent Decision 3 holds.
- Revisit if slice B fails its gate (a new intent and a fresh set, never a tweak to N or the combination), if A1 is denied, or when the check step lands.
