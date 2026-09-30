# Approval Request 2 — a model in the retrieval path (rule 5)

- **Slice:** docs-retrieval (core, with embed-v3 kept in one slice by the owner)
- **Rule:** HUMAN_APPROVAL_RULES §5 — inviting a model into a previously deterministic path
- **Requested:** 2026-09-29T05:25:45Z. Depends on nothing; Requests 3 and 4 depend on this one.

## What

Add a **local, non-generative embedding model** to retrieval: `BAAI/bge-small-en-v1.5`
at revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (MIT, published by BAAI,
ONNX, CPU-only), run with `onnxruntime` and `numpy`. It **ranks** passages
(fused with the existing BM25) and **decides confidence**. It never generates,
selects fragments of, or alters returned text.

This adds the product's first two runtime dependencies (`onnxruntime` MIT,
`numpy` BSD-3-Clause), about 9 packages / roughly 150–250 MB installed
(estimate; the real tree is recorded and a tree over ~12 packages stops Implementation).

## Why

Eval run 1 missed the ≥80% bar (2/24; ungated recall@5 14/24) and lexical
retrieval is probably capped below 80% on user-phrased questions. The Architect's
own recommendation is *against* adding embeddings in this slice (pass chance about
30% vs about 15% for lexical v2); the owner chose to pursue it, and the EM ruled the
work must be split into its own slice (overridden by the owner).

## What is reversible if denied

Everything: embed-v3 is dropped and the slice returns to lexical v2 (already
specified). No code for embed-v3 exists yet. No cost, no data, no credentials.

## The smallest request

This one model at this pinned revision, for ranking and confidence only, with
`onnxruntime` + `numpy`. It does **not** cover generation, any other model, or
any network access (Request 3), or any safety-rule wording (Request 4).

## Facts

See runs/docs-retrieval/02-tech-spec.md, section 'Retrieval — variant embed-v3', "2. Approval-ready facts". Rule 6 (new data processor) is **not**
triggered on the Architect's analysis: no question, passage or user text ever
leaves the machine, and Hugging Face sees only ordinary download metadata (IP,
User-Agent), as GitHub already does. The owner may disagree.
Unverified and stated as such there: the transitive dependency tree and sizes,
per-package licences, the ONNX graph's input names.
