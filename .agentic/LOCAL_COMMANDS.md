# Local Commands

All commands run from the repo root. Python 3.12 via uv; `uv.lock` is committed.
Only commands that have been run are listed.

| Purpose | Command | Network |
|---------|---------|---------|
| Install (clean checkout) | `uv sync --locked` | PyPI (toolchain) |
| Type-check | `uv run mypy` | none |
| Lint | `uv run ruff check` | none |
| Test (default, offline) | `uv run pytest` | blocked by an autouse fixture |
| Test (live fetch) | `uv run pytest -m network` | the pinned GitHub fetch and the pinned Hugging Face files only |
| Test (cached model) | `uv run pytest -m model` | none; needs the model cache that `ingest` fills |
| Ingest | `uv run python -m aveto_support ingest [--config docs-source.toml] [--out index/docs-index.json]` | the pinned GitHub archive, plus the pinned files of the embedding model and of the reranker (two each) on first run (cached in `models/`, sha256-checked before use) |
| Retrieve (lists the top 5 files, each with its best passages and the top score; never abstains; exit 0) | `uv run python -m aveto_support retrieve [--index index/docs-index.json] [--ranking file-rerank-v1|file-rrf-v1] <question words...>` | none |
| Eval score (gate: a correct file in the top 5 for at least 80% of answerable questions; unanswerable is a printed diagnostic; exit 0 pass, 1 below 80%). Exercised in this slice only against synthetic files inside the tests; not run against `evals/` by the implementer | `uv run python -m aveto_support eval [--index index/docs-index.json] [--eval-file evals/retrieval.toml] [--ranking file-rerank-v1|file-rrf-v1]` | none |

`ingest` takes about 80 seconds on a laptop (embedding 890 passages on CPU). `retrieve` and
`eval` load the cached models from `models/` and never use the network. The default
ranking is `file-rerank-v1` (a local cross-encoder over the first stage's top 20 files);
`--ranking file-rrf-v1` runs the first stage alone and needs no reranker files. Measured on
non-eval questions: about 2.3 to 3.8 s per `retrieve` process with the reranker (model load
included) against about 0.9 s for `file-rrf-v1`.

Full local regression: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`.

`uv run pytest -m model` includes `test_wordpiece_matches_golden`, which fails until QA adds
`tests/fixtures/wordpiece_golden.json`.

Exit codes: 0 success (`retrieve` always lists its top 5 files); 1 `eval` answerable
below 80%; 2 input or usage error (config incl. a bad `include` or an entry matching no
file, index incl. one built by other params, eval file incl. no answerable question,
commit mismatch, question with no words, missing model cache); 3 fetch error (`ingest` only, including a downloaded model file that fails its pinned sha256).

Note (macOS, python.org Python): if `ingest` fails with `CERTIFICATE_VERIFY_FAILED`,
point Python at the system CA bundle, for example `SSL_CERT_FILE=/etc/ssl/cert.pem`.
Verification stays on.
