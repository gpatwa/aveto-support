# ADR 0003: Hybrid retrieval: a local `bge-small-en-v1.5` embedding model (ONNX, CPU) fused with BM25, with dense confidence

> Architecture Decision Record. Owned by the Architect. Never edited after it is
> accepted. A changed decision gets a new ADR that supersedes this one.

- **Status:** accepted, implementation pending
- **Date:** 2026-09-29
- **Slice:** `runs/docs-retrieval/` (docs-retrieval-core). The full specification,
  with every parameter and every fact labelled VERIFIED, REPORTED or
  UNVERIFIED, is `runs/docs-retrieval/02-tech-spec.md`, section
  "Retrieval — variant embed-v3".
- **Supersedes:** the **ranking and confidence** parts of
  [ADR 0002](0002-lexical-retrieval-calibrated-abstention.md). ADR 0002's
  passage splitting by heading, its pre-registration discipline and its
  "no confident match returns no passages" rule still stand.
- **Approvals:** `runs/docs-retrieval/APPROVAL_RECORD-2.md` (rule 5: a model in
  the retrieval path), `APPROVAL_RECORD-3.md` (rule 5: the weights download) and
  `APPROVAL_RECORD-4.md` (rule 4: the exact INV-4 and INV-5 wording). All three
  were given by Gopal Patwa on 2026-09-29, each separately.

## Context

The intent asks for up to 5 sourced passages, or "no confident match", reaching
≥80% on answerable and ≥80% on unanswerable questions. Lexical v1 (ADR 0002)
scored 2/24 answerable with an ungated recall@5 of 14/24 (`eval-run-1.txt`).
Its coverage threshold saturated at 1.0. The eval questions are phrased in user
language, not the docs' language, and that vocabulary mismatch is the known
weakness of lexical retrieval. Variant v2 (Porter stemming, file-level evidence,
corroboration) addressed two general causes, but was still predicted to fall
short.

## Decision

- **Model:** `BAAI/bge-small-en-v1.5` at revision
  `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, MIT licence. It runs **locally on
  CPU** from BAAI's own `onnx/model.onnx` (sha256 `828e1496…40cf35`) with
  `onnxruntime` + `numpy`. There is no PyTorch, no `trust_remote_code` and no
  hosted API.
- **Tokenizer:** plain-Python BERT WordPiece over the pinned `vocab.txt`,
  checked against a golden-id fixture that QA generates once from the
  reference tokenizer, outside the repo.
- **Embedding:** passages are embedded as heading trail plus body; queries get
  bge's retrieval prefix. Vectors use CLS pooling and L2 normalisation, and are
  stored quantised to int8 in the one generated JSON index (`index@3`), with
  batch size 1 and single-threaded, deterministic inference.
- **Ranking `hybrid-v3`:** Reciprocal Rank Fusion (k = 60, top 100 of each
  list) of v2's lexical ranking and dense similarity, followed by the per-file
  cap of 2 and the top 5.
- **Confidence:** the dense similarity of the corpus's best passage must reach
  **τ = max(τ_salad, τ_offtopic)**. τ_salad is the p90 of cross-file word-salad
  nulls. τ_offtopic is the p90 of a frozen list of fluent off-topic questions
  written by QA, which no role that builds retrieval reads. Below τ, **no**
  passages are returned.
- **Integrity and network:** the model files are hash-checked **before use**,
  and a mismatched file is deleted. Downloads come from `huggingface.co`, with
  redirects only to `*.hf.co`. `retrieve` and `eval` are fully offline. No
  question or user text leaves the machine (amended INV-5).
- **Freeze-first:** implement, stop before any eval run, and record the frozen
  SHA. The owner's fresh held-out set is then scored once, and it gates.
  `evals/retrieval.toml` is a dev-set diagnostic.

## Alternatives considered

- **Lexical v2 only.** It has no model, no dependency and no new egress, and it
  keeps Tier 2. It lost because its predicted chance of passing both bars on a
  fresh set was about 15%. It stays specified as the fallback.
- **A hosted embedding API** (Voyage, OpenAI, Cohere and others). It lost
  because question and doc text would leave the machine (rule 6, a new data
  processor), it needs an API key, and it adds metered spend.
- **A bigger local model** (base or large encoders, around 110–335M
  parameters). It lost because it means 3–10× the download and CPU time in
  every CI run for a modest published retrieval gain. The binding weakness is
  abstention, which a bigger ranker does not fix.
- Also rejected, with reasons in the tech spec: `all-MiniLM-L6-v2` (the named
  alternative: smaller, weaker at retrieval), `nomic-embed` (needs
  `trust_remote_code`), PyTorch or sentence-transformers (heavy), and a
  pure-numpy BERT (a correctness risk).

## How the decision was made (recorded honestly)

- **The Architect recommended against pursuing embed-v3 in this slice.** It
  changes the slice's no-model premise mid-flight. Its predicted pass chance was
  about 30%, against about 15% for v2, with abstention still the likely failure.
  The recommendation was to freeze v2 and give embeddings their own slice.
- **The Engineering Manager ruled it should be split** into its own slice.
- **The owner chose to keep it in this slice** and approved each gated item
  separately (APPROVAL_RECORD-2, -3, -4). The budget was set at 1,130k. The
  owner's choice supersedes both recommendations. This ADR records the owner's
  decision and not the Architect's preference.

## Consequences

- **The product has runtime dependencies for the first time:** `onnxruntime`
  and `numpy`, about 9 packages and about 150–250 MB installed (the package
  count is unverified until `uv lock`).
- **A second download:** about 133.3 MB of weights, hash-pinned, cached in the
  gitignored `models/`. CI adds roughly 2–6 minutes per run with a cache.
- **INV-5 is amended** to allow the pinned Hugging Face download (trust rests on
  the sha256, not the host), and **INV-4 gains** "a model may only rank and
  decide confidence; it never produces or alters returned text". Both are
  applied to `.agentic/SAFETY_INVARIANTS.md` under APPROVAL_RECORD-4.
- **Expected Tier 3.** It is the first model in a deterministic path, a changed
  safety control and a new supply-chain input. The Release Manager confirms.
- **The adapter boundary becomes real:** an `Embedder` protocol with a
  `PlaceholderEmbedder` that throws by default, so every unit test runs with no
  model and no network. The new module `aveto_support/embed.py` makes 21 slice
  files in all (EM re-scope).
- **Abstention remains the weak point.** A model ranks well on paraphrase, but
  "the docs do not answer this" is only calibrated, not understood. Sense-aware
  refusal belongs to the later classifier and checker models.
- **Revisit if** the fresh held-out set misses either bar, the determinism
  check fails beyond the spec's fallbacks, or a later slice needs retrieval
  over docs the int8 index cannot hold. Any of these gets a new ADR.
