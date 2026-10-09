# QA result: Release Gate step 2, docs-retrieval-4

QA Evidence, depth standard. Follows `06-release-gate-plan.md` sections 2 and 3 (committed in 23d233c before this run). No source, test, eval, README or `.agentic` file was edited. No recommendation beyond the outcome words; the verdict is the later Release Manager's.

## 1. Inputs (no run)

| Item | Value |
|------|-------|
| git HEAD | `090f30ca5917208a1f41b2ee7e193b0e234d2585` (branch claude/docs-retrieval-4, working tree clean at start) |
| sha256 `evals/retrieval-heldout-4.toml` | `180cfc0b5505935b02e92a3f96dba2f0bf5799af71ed36ea9d855cdfdcc48aee` (matches the recorded `180cfc0b…8aee`) |
| sha256 `index/docs-index.json` | `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756` |

## 2. The regression check (fourth set, default ranking, run once)

Command: `uv run python -m aveto_support eval --eval-file evals/retrieval-heldout-4.toml > runs/docs-retrieval-4/06-eval-run-heldout4.txt 2>&1; echo "exit $?" >> ...` (no `--ranking`, no `--index`). Run once, not retried.

| Bar item (plan section 2) | Observed | Result |
|---|---|---|
| 1. 14 of 16 answerable (87.5%) | `answerable: 14/16 (87.5%) required >= 80% PASS` | met |
| 2. Misses are f04 and f12 | MISS lines: f04 and f12 only | met |
| 3. Exit code 0 | `exit 0` (also printed `eval: PASS`) | met |
| 4. `Ranking:` names file-rrf-v1, no reranker loaded | Line 1: `Ranking: file-rrf-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`; line 2 names `ranking: file-rrf-v1`; the 26-line report has no reranker line | met |
| 5. Hashes recorded and eval hash matches | section 1 | met |

Unanswerable diagnostic as printed: `unanswerable: 4 (diagnostic only, not gated)` (fu01 to fu04, DIAG lines).

Derivation check (read-only against `runs/docs-retrieval-3-proof/`): `eval-run-2-retrieval-heldout-4-file-rrf-v1.txt` shows the same `14/16 (87.5%)` with MISS f04 and f12, so the plan's derivation of the misses is correct, not a discrepancy of the record. The reranker run `eval-run-1-heldout4.txt` shows 13/16 with misses f01, f12, f13, as the close-out says. Top-score values and the top-5 lists printed for f04 and f12 were not compared line by line.

**Outcome word: at bar.** The ids and counts are identical to the recorded run. This is a regression check, not a release claim (plan section 2, last paragraph).

## 3. Full local regression (run once, each step separate, no `&&` chain hiding a failure)

| Step | Exit | Tail line |
|---|---|---|
| `uv sync --locked` | 0 | `Audited 16 packages` |
| `uv run mypy` | 0 | `Success: no issues found in 15 source files` |
| `uv run ruff check` | 0 | `All checks passed!` |
| `uv run pytest -q` | 0 | `168 passed, 10 deselected in 8.87s` (matches Security's 168 / 10) |

Raw: `06-regress-sync.txt`, `06-regress-mypy.txt`, `06-regress-ruff.txt`, `06-regress-pytest.txt`.

INV-4 and INV-5 enforced-by names (from `.agentic/SAFETY_INVARIANTS.md`), run by name with `-k` (all 22 names): `27 passed, 151 deselected`, exit 0 (`06-regress-inv45.txt`). All 22 names were collected and passed; 27 is more than 22 because `-k` is a substring match and some names parametrize or prefix other tests (for example `test_reranker_revision_must_be_40_hex` matched 5 items plus `..._for_download`). No skips or failures. I did not run INV-1 to INV-3 names (the plan scopes this to INV-4 and INV-5; Security covered them).

## 4. Diagnostics (after step 2 was on disk; one run each, default ranking, nothing chosen from them)

| Set | Recorded (close-out) | This run | Exit | Misses |
|---|---|---|---|---|
| `evals/retrieval.toml` (dev) | 19/24 (79.2%) | 19/24 (79.2%) | 1 (by design, below 80%) | a01 a02 a10 a11 a16 |
| `evals/retrieval-heldout.toml` (second) | 12/17 (70.6%) | 12/17 (70.6%) | 1 | h01 h05 h13 h14 h17 |
| `evals/retrieval-heldout-3.toml` (third) | 11/16 (68.8%) | 11/16 (68.8%) | 1 | t04 t06 t12 t13 t15 |

All three print `Ranking: file-rrf-v1:...`. No differences from the recorded scores. Recorded and reported only. Raw: `06-diag-dev.txt`, `06-diag-heldout2.txt`, `06-diag-heldout3.txt`. Recorded scores were cross-checked against `eval-run-4`, `eval-run-6` and `eval-run-8` in the slice-3 proof folder.

## 5. Anomalies

1. **No exit 134 and no signal exit** in any of the four eval runs, and none in the regression steps. Counts for this QA run: 0 aborts in 4 eval runs on the default path. (The 3 malformed invocations in item 2 are not counted; they never ran an eval.) This does not change the "crash NOT REPRODUCED" wording: it is 4 more clean runs, not an explanation.
2. **QA shell error on the diagnostics, first attempt.** My first diagnostics loop used zsh word-splitting wrongly, so each of the three commands received a malformed path (`evals/retrieval-heldout-3 heldout3.toml`) and exited 2 with `error: cannot read eval file ... No such file or directory`. No eval file was read and nothing was scored. I deleted those three stub outputs and ran each diagnostic exactly once with a corrected loop. This is a harness slip, not a retry of a scored run; the step 2 run was not involved. Disclosed because the plan says one run each.
3. My first by-name INV-4 / INV-5 attempt also failed on a shell quoting error (`-k` expression error, exit 4, "no tests ran") and a second one printed no PASSED lines because `-q -v` cancel. Neither was a test failure; the final recorded file is the third invocation. Test-only, offline, no scoring.
4. `git status` after the run shows only new files under `runs/docs-retrieval-4/`; no tracked source changed.

## 6. Deferred / not run

Per plan section 3.5, not run: `--ranking file-rerank-v1`, ingest, network, 20-run crash loops, `pytest -m network`, `pytest -m model`. No UI, so no preview verification.
