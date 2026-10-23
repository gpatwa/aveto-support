# Backend note: stage 3 (Backend Architect), fix-service-accounting

Depth standard. Base 87178bd. Outputs: this note, `03-failfirst-87178bd.txt`, `03-green.txt`.

## Files changed
- Source (5): `aveto_service/{judge_port,anthropic_judge,pipeline,settings}.py`, `infra/main.bicep`.
  - `judge_port.py`: `MAX_ATTEMPTS`, `NEVER_BILLED` (moved here), `JudgeCall.billable_failures`, `JudgeTransportError(..., billable_failures=None)` with the spec's default.
  - `anthropic_judge.py`: imports the two constants; counts billable failed attempts; passes the count on success and on every error.
  - `pipeline.py`: floor and admission reserve `MAX_ATTEMPTS * per_attempt`; `_judged` charges per attempt (`exc.billable_failures * per_attempt`; call: usage cost + `failed * per_attempt`); `_NEVER_BILLED`, `unbilled` and `(attempts-1)*amount` removed.
  - `settings.py`, `main.bicep`: 2000/10000 with the source comment (Anthropic pricing page, owner's console bill, 2026-10-23).
- Tests: `test_service_limits.py` (T6.1, T6.2, T7.1, T7.2 x3, T7.4, T7.5 x9, T8.1; edits at the price lines and the two in-flight tests), `test_anthropic_judge.py` (T7.3 x8, plus success x4 and prompt-hash), `test_infra_static.py` (T8.2), `test_service_pipeline.py` (C1.4: `event-log.mjs` only), `test_service_api.py` (see deviations).
- `limits.py`, `tests/service_fakes.py`, `aveto_support/`, `prompts/`, `.claude/`, `.agentic/`, README, runbook untouched. No new dependency, no logging added.

## Fail-first (base 87178bd, new/changed test files copied in, source untouched; `git diff 87178bd -- aveto_service infra` empty there)
Run: `uv run pytest tests/test_service_limits.py tests/test_anthropic_judge.py tests/test_infra_static.py tests/test_service_pipeline.py`: 30 failed, 137 passed. Full output in `03-failfirst-87178bd.txt`.

| Test | Base | Base figure | Head |
|---|---|---|---|
| T6.1 test_retry_never_settles_above_cap | FAIL | `spent 22466000 <= cap 13124000` (R = 13,124,000; R + 9,342,000) | pass |
| T6.2 test_retry_settles_within_both_reserved_attempts | pass (guard) | n/a | pass |
| T7.1 test_5xx_then_4xx_charges_the_first_attempt | FAIL | `0 == 13124000` | pass |
| T7.2 test_never_billed_attempts_charge_zero (3) | pass (guard) | n/a | pass |
| T7.4 test_never_billed_retry_then_success_charges_usage_only | FAIL | `22466000 == 9342000` | pass |
| T7.5 test_port_defaults_reproduce_the_old_charge (9) | FAIL | AttributeError `billable_failures` | pass |
| T7.3 test_billable_failures_counted_per_attempt (8) | FAIL | AttributeError `billable_failures` | pass |
| (extra) test_billable_failures_on_success (4), test_prompt_hash_mismatch_bills_nothing | FAIL | AttributeError | pass |
| T8.1 test_price_defaults_are_2000_and_10000 | FAIL | `(3000, 15000) == (2000, 10000)` | pass |
| T8.2 test_bicep_price_defaults | FAIL | `('3000','15000') == ('2000','10000')` | pass |
| Edited existing: price lines (2), concurrent-admissions in_flight | FAIL | e.g. `(3150000,0,1000,10) == (2100000,...)`; in_flight 3x amount | pass |
| C1.4 test_core_files_unchanged | pass with the repair (baseline failure fixed) | n/a | pass |
| unedited guards (test_inflight_reservations_do_not_close_the_day) | pass | n/a | pass |

T6.1's figure matches the spec (overshoot 9,342,000 = $0.009342). All required tests failed with the named figure; none passed on base.

## Full regression at head
`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`: mypy and ruff clean; **668 passed, 0 failed, 12 deselected** (636 + 1 C1.4 + 31 new items). Output in `03-green.txt`.

## Section 6 checks (final tree)
1. `git diff --exit-code 87178bd -- aveto_support prompts .claude .agentic ':(exclude).agentic/CURRENT_MVP_STATUS.md'`: no output, exit 0.
2. Each of `aveto_support`, `prompts`, `.claude`, `.agentic/SAFETY_INVARIANTS.md`: no output, exit 0.
3. `git status --porcelain -- aveto_support prompts .claude .agentic`: no output.
4. `git diff --name-only 87178bd -- . ':(exclude)runs'` (tree incl. this commit): 11 paths, `aveto_service/{anthropic_judge,judge_port,pipeline,settings}.py`, `docs/ARCHITECTURE.md` (Architect's, already committed at stage 2), `infra/main.bicep`, `tests/{test_anthropic_judge,test_infra_static,test_service_api,test_service_limits,test_service_pipeline}.py`. **`tests/test_service_api.py` is not in the spec's 13-path list** (deviation 1).
5. `test_core_files_unchanged`: passes; only the C1.4 name added.

## Deviations
1. **`tests/test_service_api.py::test_health_never_calls_model`** quoted the old price: `spend_today_usd == "0.007500"` (2400 x 3000 + 20 x 15000). At 2000/10000 it is `"0.005000"`. The spec's §3.2 list missed it; one-line edit, test-only, a 14th path in the diff.
2. Fail-first run on base: `test_service_limits.py` imports `MAX_ATTEMPTS` from `judge_port`, which does not exist on base, so in the base copy only I changed that import to `aveto_service.anthropic_judge` (same value, 2) so the tests run and show their figures rather than failing at collection. The committed test file is unchanged by this.
3. Extra tests beyond the spec's names: `test_billable_failures_on_success` (4 rows) and `test_prompt_hash_mismatch_bills_nothing`, covering the spec's T7.3 success rows and the prompt-hash row; both fail first.
4. Pipeline detail: non-transport exceptions keep one `per_attempt` (as spec); `_judged` initial `charge = 0` is overwritten on every path that settles.
5. **Not done: the smoke script** `runs/fix-service-accounting/10-smoke/smoke.py` (spec §8.1/§12 assign it to stage 3; the Orchestrator's brief did not list it). Needs a separate instruction.
6. The spec's §5 step 1 `03-implementation.md` is replaced by this note (`08-backend-note.md`) as instructed.
