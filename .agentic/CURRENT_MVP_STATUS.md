# Current MVP Status

## What exists (slice docs-retrieval-core, command line only)

- `ingest`: downloads the markdown of the configured repo at its pinned commit
  (one read-only HTTPS archive fetch), splits it into passages at headings, and
  writes a deterministic index file (`index/`, gitignored).
- `retrieve`: returns up to 5 verbatim passages with path, heading trail, line
  range and a permalink at the pinned commit, or `no confident match`.
- `eval`: scores retrieval against `evals/retrieval.toml` and exits non-zero
  below 80% on either group.
- Plain code only: no model call, no runtime dependency, standard library only.

## Eval status

Run 1 missed the bar (see `runs/docs-retrieval/eval-run-1.txt`): answerable 2/24,
unanswerable 6/6. The slice does not meet Done-means 8 yet; this goes back to the
Architect per the overfitting protocol.

## Out of scope (not built)

- Any model call: classify, draft, check.
- An HTTP surface (FastAPI is decided but not installed), a database.
- CI: arrives with `docs-retrieval-ci`.
- Anything that posts to GitHub.
