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
- The default ranking is `file-rrf-v1` (the first stage alone: hybrid dense and lexical
  rank fusion over all files). `--ranking file-rerank-v1` is opt-in: a local cross-encoder
  (`cross-encoder/ms-marco-MiniLM-L6-v2`, ONNX, CPU) re-scores the top 20 files' shown
  passages (MaxP) and orders them; it needs `ingest --with-reranker` first. Recorded
  scores: `file-rrf-v1` 14/16 on the fourth held-out set (11/16 and 12/17 on earlier
  ones; 19/24 = 79.2% on the dev set, below the 80% bar); `file-rerank-v1` 13/16 on the
  fourth. The reranker showed no demonstrated gain (slice 3 close-out).
- The models (`BAAI/bge-small-en-v1.5` and the reranker, ONNX, CPU) only rank. They never
  write or alter text. Questions never leave the machine; `retrieve` and
  `eval` are offline.
- Runtime dependencies: `onnxruntime` and `numpy` only.

## Not yet done

- `tests/fixtures/wordpiece_golden.json` (QA) is missing, so
  `test_wordpiece_matches_golden` fails until it lands.
- Retrieval has not passed its held-out gate as a released feature; nothing is released
  or announced, and no answers are generated.

## Out of scope (not built)

- Any generative model call: classify, draft, check.
- An HTTP surface (FastAPI is decided but not installed), a database.
- CI: arrives with `docs-retrieval-ci`.
- Anything that posts to GitHub.
