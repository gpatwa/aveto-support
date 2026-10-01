# Current MVP Status

## What exists (slice docs-retrieval-core, command line only)

- `ingest`: downloads the markdown of the configured repo at its pinned commit
  (one read-only HTTPS archive fetch), splits it into passages at headings,
  embeds each passage with a local model, and writes a deterministic index file
  (`index/`, gitignored). On first run it also downloads two pinned model files
  from huggingface.co into `models/` (gitignored), each checked against its
  committed sha256 before use.
- `retrieve`: returns up to 5 verbatim passages with path, heading trail, line
  range and a permalink at the pinned commit, or `no confident match` with no
  passages. Ranking is hybrid: BM25 (Porter stemming, passage plus file
  evidence) fused with dense similarity by reciprocal rank fusion. Confidence is
  the dense similarity of the best passage against a threshold calibrated at
  ingest from word salads and a frozen off-topic question list.
- `eval`: scores retrieval against an eval file and exits non-zero below 80% on
  either group.
- Retrieval is two-stage (`file-rerank-v1`, default): `file-rrf-v1` ranks all files, then a
  local cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`, ONNX, CPU) re-scores the
  top 20 files' shown passages (MaxP) and orders them; `--ranking file-rrf-v1` runs the
  first stage alone. Not yet evaluated on a held-out set.
- The models (`BAAI/bge-small-en-v1.5` and the reranker, ONNX, CPU) only rank. They never
  write or alter text. Questions never leave the machine; `retrieve` and
  `eval` are offline.
- Runtime dependencies: `onnxruntime` and `numpy` only.

## Not yet done

- `tests/fixtures/wordpiece_golden.json` (QA) is missing, so
  `test_wordpiece_matches_golden` fails until it lands.
- No `eval` has been run on this variant. The freeze-first ordering applies:
  the fresh held-out set is scored once, after the freeze.

## Out of scope (not built)

- Any generative model call: classify, draft, check.
- An HTTP surface (FastAPI is decided but not installed), a database.
- CI: arrives with `docs-retrieval-ci`.
- Anything that posts to GitHub.
