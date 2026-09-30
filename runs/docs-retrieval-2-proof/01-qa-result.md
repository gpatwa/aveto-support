# QA Result — docs-retrieval-2-proof (slice B)

**Verdict: GATE FAILED. Third held-out set: 11 of 16 answerable, bar is 13. Recommendation: NO-GO (nothing ships; failure loop).**

## Identity and pre-run checks
- HEAD: `f50049fc6b54fc1fcd12913273e95723eb278821`. Frozen method: `b3f3fc41f2382283678e638b55ff44b32876034c` (`file-rrf-v1` + 123-file corpus).
- `git status --short` before running: empty (no modified tracked file).
- `git diff b3f3fc4 HEAD --stat -- aveto_support tests docs-source.toml pyproject.toml uv.lock evals/retrieval.toml evals/retrieval-heldout.toml evals/calibration-offtopic.toml`: empty.
- `index/docs-index.json` sha256 = `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756` (matches expected; no re-ingest needed, no network used).
- Each eval ran exactly once. (My first shell line for the dev set died on a shell typo before launching `eval`; the dev set's only run is the one recorded, so no eval ran twice.) Raw outputs are in `eval-run-1-heldout3.txt`, `eval-run-2-heldout2-diagnostic.txt`, `eval-run-3-dev-diagnostic.txt`, each with its exit code last.

## Third held-out set (the gate) — `evals/retrieval-heldout-3.toml`
**answerable: 11/16 (68.8%), required >= 13 (80%). FAIL. exit code 1.**

| Q | Result (copied from output) |
|---|---|
| t01 | HIT agents/release-manager.md (rank 1) |
| t02 | HIT templates/MIGRATION_PLAN_TEMPLATE.md (rank 1) |
| t03 | HIT templates/MODEL_CARD_TEMPLATE.md (rank 2) |
| t04 | MISS expected templates/VENDOR_RISK_TEMPLATE.md |
| t05 | HIT templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md (rank 1) |
| t06 | MISS expected agents/ux-researcher.md |
| t07 | HIT templates/CUSTOMER_ISSUE_RESOLUTION_TEMPLATE.md (rank 1) |
| t08 | HIT execution/pack/protocols/RUN_INVENTORY.md (rank 1) |
| t09 | HIT execution/pack/protocols/TELEMETRY.md (rank 1) |
| t10 | HIT docs/DEPLOYMENT.md (rank 1) |
| t11 | HIT project-packs/b2c-saas.md (rank 3) |
| t12 | MISS expected agents/ai-governance.md or templates/AI_RISK_ASSESSMENT_TEMPLATE.md |
| t13 | MISS expected templates/CHANGE_REQUEST_TEMPLATE.md |
| t14 | HIT agents/ml-engineer.md (rank 2) |
| t15 | MISS expected execution/SECURITY.md |
| t16 | HIT docs/OPERATING_MODEL.md (rank 1) |

Unanswerable (4): printed diagnostic only, **not a gate**. Top files and scores: tu01 docs/HUMAN_APPROVAL_RULES.md 0.70; tu02 docs/VALIDATION_MATRIX.md 0.59; tu03 docs/DEPLOYMENT.md 0.81; tu04 docs/DEPLOYMENT.md 0.67. Retrieval always returns its top 5 (approved), so nothing abstains.

Ungated recall diagnostic line the eval prints (every run): `reference similarity: 0.702 (diagnostic)`. The eval prints no other ungated recall line.

## Earlier sets — SEEN SETS; NOT GATES (diagnostics only)
- `evals/retrieval-heldout.toml` (second held-out): answerable 12/17 (70.6%); unanswerable 6 diagnostic; exit 1. Misses: h01, h05, h13, h14, h17.
- `evals/retrieval.toml` (dev): answerable 19/24 (79.2%); unanswerable 6 diagnostic; exit 1. Misses: a01, a02, a10, a11, a16.
- Neither gates. For context only: no set reaches 80%; the third set (11/16) is the lowest.

## Regression (run after the evals, at HEAD, static checks last)
| Command | Result |
|---|---|
| `uv sync --locked --offline` | exit 0 (Audited 16 packages) |
| `uv run --offline pytest` | 122 passed, 5 deselected; exit 0 |
| `uv run --offline pytest -m model` | 3 passed, 124 deselected; exit 0 |
| `uv run --offline mypy` | Success: no issues found in 13 source files; exit 0 |
| `uv run --offline ruff check` | All checks passed; exit 0 |

Post-run `git status --short` shows only the three new eval output files (untracked). No code, config or eval file changed; nothing committed.

## Caveats (part of the record)
- (a) The third set was drafted by Claude in the playbook session and reviewed and committed by the owner. The drafter had read both earlier runs' results and slice 2's tech spec, so it knew the method, though it reports it never ran retrieval on these questions.
- (b) 16 answerable questions is a small sample; one question is 6.25 points. 11 vs the 13 bar is a two-question shortfall.
- (c) The two earlier sets are seen sets; their numbers are not evidence of generalisation and gate nothing.

## Stop
Gate failed. Per the brief, nothing else tried: no rerun, no tuning. Per the slice plan: Security, Release Gate and README/ARCHITECTURE refresh are skipped; a further method change needs a fresh fourth held-out set from the owner and a new rule 4 look; the next question per Decision 3 is a reranker.
