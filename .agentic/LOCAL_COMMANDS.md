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
| Ingest | `uv run python -m aveto_support ingest [--config docs-source.toml] [--out index/docs-index.json]` | the pinned GitHub archive, plus the pinned files of the embedding model (two) on first run; the reranker's are fetched only with `--with-reranker` (cached in `models/`, sha256-checked before use) |
| Ingest, with the optional reranker | `uv run python -m aveto_support ingest --with-reranker [--config ...] [--out ...]` | as Ingest, plus the reranker's two pinned files (cached in `models/`, sha256-checked before use) |
| Retrieve (lists the top 5 files, each with its best passages and the top score; never abstains; exit 0) | `uv run python -m aveto_support retrieve [--index index/docs-index.json] [--ranking file-rrf-v1|file-rerank-v1] <question words...>` (default `file-rrf-v1`; `file-rerank-v1` needs `ingest --with-reranker` first, else exit 2) | none |
| Eval score (gate: a correct file in the top 5 for at least 80% of answerable questions; unanswerable is a printed diagnostic; exit 0 pass, 1 below 80%). Exercised in this slice only against synthetic files inside the tests; not run against `evals/` by the implementer | `uv run python -m aveto_support eval [--index index/docs-index.json] [--eval-file evals/retrieval.toml] [--ranking file-rrf-v1|file-rerank-v1]` (default `file-rrf-v1`; the dev set scores 19/24 = 79.2% on it, so `eval` may exit 1 by design) | none |
| Judge input (prints the answerability judge's payload for one question; stderr has `input sha256: <hex>`; writes nothing; deletes a stale `.aveto-judge/reply.txt`) | `uv run python -m aveto_support judge-input --question-file <file>` (or the question words) | none; no model is called |
| Judge apply (applies one verdict file from `.aveto-judge/` to the same payload; deletes the transport files; `NOT_ANSWERABLE` prints `no confident match` then the one deciding-signal line; exit 4 and `judge error` on any bad reply) | `uv run python -m aveto_support judge-apply --question-file <file> --input-sha256 <hex> --verdict-file .aveto-judge/reply.txt` | none |
| Eval with verdicts (prints both answerability bars, judge errors and diagnostics after the usual report; exit code is still the retrieval gate). Exercised only against synthetic files in the tests | `uv run python -m aveto_support eval --eval-file <file> --verdicts <verdicts.toml>` (default ranking only) | none |
| Derive the seen-check sample (eval-only; stops with exit 2 and writes nothing unless U = 20 and H = 56 split 6/6/4/4 and 19/12/11/14; refuses to overwrite an existing key) | `uv run python -m tools.judge_run derive-sample [--out runs/docs-answerability-2/judge-check]` | none |
| Best score rule self-check (reproduces 13/20 and 37/56 on the four seen sets; exit 1 if not) | `uv run python -m tools.judge_run diagnostics --self-check` | none |
| Read judge transcripts (read-only; prints model, offered tools, `tool_use`, base-dir line length, payload and peak per spawn; no reply text, no token) | `uv run python -m tools.judge_run check-transcripts <subagents-dir>` | none |
| Audit and verdicts for a batch (voids on any tool use, other model, other offered tools, bad layout, unknown payload, duplicate or missing id; else writes `verdicts.toml`, `audit.md`, `diffs.md`, `audit.json`). Exercised only against synthetic transcripts in the tests | `uv run python -m tools.judge_run record --subagents-dir <dir> --eval-file <file> --stage-dir <dir> --expect-tools none\|<comma list>` | none |
| Extra diagnostics (best score rule, over-abstention, ANSWERABLE without a hit, judge errors split, usage). Exercised only against synthetic data in the tests | `uv run python -m tools.judge_run diagnostics --eval-file <file> --verdicts <verdicts.toml> [--audit <audit.json>]` | none |
| Add the gate set to the check directory (stage 7 only; `r101` upwards; reads no label). Exercised only against synthetic data in the tests | `uv run python -m tools.judge_run add-set --eval-file <file>` | none |

`ingest` takes about 80 seconds on a laptop (embedding 890 passages on CPU). `retrieve` and
`eval` load the cached models from `models/` and never use the network. The default
ranking is `file-rrf-v1` (the first stage alone; no reranker files needed);
`--ranking file-rerank-v1` adds a local cross-encoder over its top 20 files and needs `ingest --with-reranker` first. Measured on
non-eval questions: about 2.3 to 3.8 s per `retrieve` process with the reranker (model load
included) against about 0.9 s for `file-rrf-v1`.

Full local regression: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`.

`uv run pytest -m model` includes `test_sample_derivation_reproducible` (re-derives the seen-check sample from the real index, about 50 s) and `test_wordpiece_matches_golden`, which fails until QA adds
`tests/fixtures/wordpiece_golden.json`.

Exit codes: 0 success (`retrieve` always lists its top 5 files); 1 `eval` answerable
below 80%; 4 `judge-apply` could not use the verdict (prints `judge error`); 2 input or usage error (config incl. a bad `include` or an entry matching no
file, index incl. one built by other params, eval file incl. no answerable question,
commit mismatch, question with no words, missing model cache); 3 fetch error (`ingest` only, including a downloaded model file that fails its pinned sha256).

Note (macOS, python.org Python): if `ingest` fails with `CERTIFICATE_VERIFY_FAILED`,
point Python at the system CA bundle, for example `SSL_CERT_FILE=/etc/ssl/cert.pem`.
Verification stays on.
