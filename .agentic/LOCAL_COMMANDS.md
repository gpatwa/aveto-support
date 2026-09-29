# Local Commands

All commands run from the repo root. Python 3.12 via uv; `uv.lock` is committed.
Only commands that have been run are listed.

| Purpose | Command | Network |
|---------|---------|---------|
| Install (clean checkout) | `uv sync --locked` | PyPI (toolchain) |
| Type-check | `uv run mypy` | none |
| Lint | `uv run ruff check` | none |
| Test (default, offline) | `uv run pytest` | blocked by an autouse fixture |
| Test (live fetch) | `uv run pytest -m network` | the pinned fetch only |
| Ingest | `uv run python -m aveto_support ingest [--config docs-source.toml] [--out index/docs-index.json]` | the pinned fetch only |
| Retrieve | `uv run python -m aveto_support retrieve [--index index/docs-index.json] <question words...>` | none |
| Eval score | `uv run python -m aveto_support eval [--index index/docs-index.json] [--eval-file evals/retrieval.toml]` | none |

Full local regression: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`.

Exit codes: 0 success (for `retrieve`, "no confident match" is a success); 1 eval
below either threshold; 2 input or usage error (config, index, eval file, commit
mismatch); 3 fetch error (`ingest` only).

Note (macOS, python.org Python): if `ingest` fails with `CERTIFICATE_VERIFY_FAILED`,
point Python at the system CA bundle, for example `SSL_CERT_FILE=/etc/ssl/cert.pem`.
Verification stays on.
