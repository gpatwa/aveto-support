# QA Evidence: fix-service-accounting (stage 5)

- **Agent:** QA Evidence, depth standard, 2026-10-23. Offline only: no live service, no network, no `az`.
- **Product head verified:** `5f86fd3`. The branch tip when I ran was `8aee3b4`; `git diff --stat 5f86fd3 HEAD` shows only `runs/` files (08-backend-note.md, 10-smoke/smoke.py, code-review.md), so the product tree is the same.
- **Base:** `87178bd` (= `main`, `git rev-parse main` prints 87178bdf...).
- **No product code or test was modified.** All mutation and fail-first work was done in detached scratch worktrees under `/private/tmp/claude-501/`, removed afterwards (`git worktree list` shows neither). The main worktree's `git status` before and after shows only ` M runs/fix-service-accounting/STATE.md` (not mine to commit).

## Verdict: GO WITH CONDITIONS

The three fixes are in, each is proven by a test that fails on the base commit for the stated reason and by a mutation that makes a test fail again. The full regression is green three times. "Nothing else moves" holds byte for byte. The conditions are not defects in the code; they are lines that cannot be met until later stages:

1. **Docs (stage 7) must still change** `README.md` lines 211 and 233, `docs/runbooks/public-ask.md` lines 118, 245, 257 and `.agentic/CURRENT_MVP_STATUS.md` lines 47 to 50: they still say "$3 and $15", "reads 50% high", "27 questions a day". Per CR-3 they must quote the spec's labelled estimate (about 33 a day), not the intent's "about 41" (see "Open points").
2. **Stage 8 re-runs spec section 6** on the final tree (after Docs adds 3 files: README, runbook, status).
3. **Stage 10 live smoke** and the deploy lines are NOT YET (below).

## Commands run, in order, with results

| # | Command | Result |
|---|---|---|
| 1 | `uv sync --locked` | exit 0 (Resolved 39, Audited 36) |
| 2 | `uv run mypy` | Success: no issues found in 45 source files (3 of 3 runs) |
| 3 | `uv run ruff check` | All checks passed (3 of 3 runs) |
| 4 | `uv run pytest -q` run 1 | **668 passed, 12 deselected**, 53.15 s, exit 0 |
| 5 | `uv run pytest -q` run 2 | **668 passed, 12 deselected**, 18.82 s, exit 0 |
| 6 | `uv run pytest -q` run 3 | **668 passed, 12 deselected**, 18.76 s, exit 0 |

Each step was run on its own, not chained, so one failure could not hide another. Counts match the engineer's `03-green.txt` (668 = 636 baseline + 1 repaired by C1.4 + 31 new items). No test was flaky across the three runs; the 12 deselected are the `network` and `model` marks, unchanged.

## Fail-first, re-run independently on 87178bd

Method: detached worktree at `87178bd`, `uv sync --locked`, then the five changed test files from `5f86fd3` copied in (`test_anthropic_judge.py`, `test_infra_static.py`, `test_service_api.py`, `test_service_limits.py`, `test_service_pipeline.py`). `git diff --stat 87178bd -- aveto_service infra` printed nothing (source is the base's). Command: `uv run pytest tests/test_service_limits.py tests/test_anthropic_judge.py tests/test_infra_static.py tests/test_service_pipeline.py -q`.

**One change to the copied tests, same as the engineer's deviation 2:** `test_service_limits.py` imports `MAX_ATTEMPTS` from `judge_port`, which does not exist on the base. Unpatched, the whole file fails at collection (`ImportError`, seen and recorded), which proves nothing about the figures. In the scratch copy only, I pointed that import at `aveto_service.anthropic_judge.MAX_ATTEMPTS` (same value, 2). The committed test is untouched.

Result: **30 failed, 137 passed.** The set of 30 failing test ids is identical to the engineer's list in `03-failfirst-87178bd.txt` (diffed: identical).

| Test | On 87178bd | Figure I saw | Matches spec |
|---|---|---|---|
| T6.1 `test_retry_never_settles_above_cap` | FAIL | `assert 22466000 <= 13124000` (spent `R + 9,342,000`, cap `R = 13,124,000`) | yes |
| T7.1 `test_5xx_then_4xx_charges_the_first_attempt` | FAIL | `assert 0 == 13124000` | yes |
| T7.4 `test_never_billed_retry_then_success_charges_usage_only` | FAIL | `assert 22466000 == 9342000` | yes |
| T7.5 `test_port_defaults_reproduce_the_old_charge` (9) | FAIL | `AttributeError: ... no attribute 'billable_failures'` | yes |
| T7.3 `test_billable_failures_counted_per_attempt` (8) | FAIL | same `AttributeError` | yes |
| extra `test_billable_failures_on_success` (4), `test_prompt_hash_mismatch_bills_nothing` | FAIL | `AttributeError` | extra to spec, disclosed |
| T8.1 `test_price_defaults_are_2000_and_10000` | FAIL | `assert (3000, 15000) == (2000, 10000)` | yes |
| T8.2 `test_bicep_price_defaults` | FAIL | `('3000','15000') == ('2000','10000')` | yes |
| T6.2 guard, T7.2 guard x3 | PASS | n/a (4 passed in a targeted run) | yes |
| Edited existing: `test_spend_reservation_bounds_and_settles`, `test_not_answerable_is_charged_like_any_judged_call`, `test_concurrent_admissions_never_exceed_cap` | FAIL | e.g. `(3150000,0,1000,10) == (2100000,0,1000,10)` | expected (they encode the new price and reservation) |

**Test acceptance counts:** tests added 31; confirmed failing first on the base 27; guards that pass on the base by design 4 (T6.2, T7.2 x3); 3 existing tests edited and failing on the base; 30 = 27 + 3. Generated tests removed: none (all 31 build, pass in three consecutive runs, and each is tied to a "Done means" line). The 4 guards do not prove the change on their own and are reported as guards.

## Mutation checks (head `5f86fd3` in a scratch worktree; each hunk reverted alone, then restored)

Baseline in the scratch worktree: 167 passed on the four changed files.

| Mutation (reverted hunk) | Tests that fail | Verdict |
|---|---|---|
| #6: admission and the floor reserve one attempt instead of `MAX_ATTEMPTS * per_attempt` | `test_retry_never_settles_above_cap`, `test_concurrent_admissions_never_exceed_cap` (2 failed) | caught |
| #7a: a never-billed last error zeroes the whole charge (`charge = 0 if exc.category in {status_4xx, connection}`) | `test_5xx_then_4xx_charges_the_first_attempt` (1 failed) | caught |
| #7b: a successful call charges every earlier attempt (`failed = attempts - 1`, the old rule) | `test_never_billed_retry_then_success_charges_usage_only` (1 failed) | caught |
| #8a: `settings.py` defaults back to 3000/15000 | `test_spend_reservation_bounds_and_settles`, `test_not_answerable_is_charged_like_any_judged_call`, `test_price_defaults_are_2000_and_10000`, `test_bicep_price_defaults` (4 failed) | caught |
| #8b: `infra/main.bicep` defaults back to 3000/15000 | `test_bicep_price_defaults` (1 failed) | caught |

After the last mutation the scratch tree was restored with `git checkout -- <file>`, `git status --porcelain` was empty, and the four files again gave 167 passed. The scratch worktree was then removed. In the real worktree `git status --porcelain` shows only ` M runs/fix-service-accounting/STATE.md`.

Not mutated: the adapter's per-attempt counting in `anthropic_judge.py`; its 8 + 4 + 1 tests (T7.3 and extras) fail on the base for the right reason, which is the evidence I have for them.

## "Done means", verbatim, with status

**Starts from main after PR 5 is merged, with pack v28 installed.** MET. Branch cut from `87178bd` (= `main`); `.claude/hooks/event-log.mjs` is present and `test_core_files_unchanged` passes. (Per the Charter, C6.1, "pull request 5 merged" is the owner's record; I checked only that `main` is 87178bd and the pack is v28.)

**#6 fixed, with a test that fails first** (the line as written: "with a cap equal to one reservation and a fake client that returns a retryable error and then succeeds, the service never settles spend above the cap because of the retry ... the Architect chooses, and says which and why"). MET. Option chosen: reserve both attempts up front, refund the unused part at settlement (spec section 1, option A). Evidence: T6.1 fails on 87178bd with `22466000 <= 13124000` and passes on head; mutation #6a is caught; T6.2 shows the retry within `cap = 2R` settles at `R + 9,342,000` with `in_flight == 0`. The figure `$0.009342` is the intent's overshoot ($0.039342 - $0.030000). Caveat (CR-1): on head T6.1 passes because admission refuses (PAUSED); the retry-that-runs case is T6.2's job. Both exist.

**#7 fixed, with a test that fails first** ("a 503 followed by a 400 charges the first attempt as a 5xx would be charged; a sequence in which every attempt is never-billed still charges zero. The Architect states the rule in one sentence"). MET. T7.1 fails on base (`0 == 13124000`), passes on head, mutation #7a caught; T7.2 (429+400, conn+conn, 429+429) charge zero on base and head. The rule is stated in spec section 2 (one rule per attempt on its own outcome; I read it, I did not re-derive it). Side effect, already flagged by the Architect for Security: a 429 followed by success now charges the usage only (T7.4).

**#8 fixed** ("the defaults are 2000 and 10000 nano-dollars per token in `settings.py` and `infra/main.bicep`; the `ASK_PRICE_*` override stays; a comment names the source and the date it was read"). MET for the code half. `settings.py:15-19` and `main.bicep` print 2000/10000; T8.1 asserts the override gives (3000, 15000); T8.2 asserts Bicep and code in lockstep and that `infra/main.parameters.json` carries no price. Both carry the comment "Read 2026-10-23 from Anthropic's pricing page and matched by the owner's console bill". **Unconfirmed by me:** the pricing page and the console bill are outside what I can check offline; I verified only that the comment is there.
Second half ("The tests, `docs/runbooks/public-ask.md` and any other place that quotes $0.0118 per question or 27 questions a day are updated ... any figure that is only an estimate says so"): tests MET (the two price lines and `test_health_never_calls_model` updated; the remaining `3000/15000` in tests are explicit-price unit tests and the override case). Docs **NOT YET**: `git grep` on head still finds the old figures at README.md:211,233, docs/runbooks/public-ask.md:118,245,257-258 and .agentic/CURRENT_MVP_STATUS.md:47,50. `$0.0118` itself is nowhere in the repo (as `01-scope.md` said). Stage 7 owns this.

**Nothing else moves** ("`git diff main -- aveto_support prompts .claude .agentic` is empty; the retrieval, the judge prompt, the corpus and every safety invariant are byte-identical"). MET. Evidence (spec section 6, base 87178bd):
- `git diff --exit-code 87178bd -- aveto_support prompts .claude .agentic ':(exclude).agentic/CURRENT_MVP_STATUS.md'`: no output, exit 0.
- Each alone, exit 0: `aveto_support`, `prompts`, `.claude`, `.agentic/SAFETY_INVARIANTS.md`.
- The intent's own command without the exclusion, `git diff --exit-code main -- aveto_support prompts .claude .agentic`: exit 0 (the status file is not yet edited).
- `git status --porcelain -- aveto_support prompts .claude .agentic`: no output.
- Git tree ids equal on base and head for `aveto_support` (fdf11739...), `prompts` (55a8c230...), `.claude` (ff8c0b7d...) and blob `.agentic/SAFETY_INVARIANTS.md` (3d976e5f...).
- Judge prompt `prompts/answerability-judge-v1.txt` sha256 `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427` on head and on base.
- `test_core_files_unchanged` passes; its diff against base is the single line `"event-log.mjs",` (C1.4).
- Change set `git diff --name-only 87178bd -- . ':(exclude)runs'`: 11 paths, all inside the spec's expected list except `tests/test_service_api.py` (the one-line price edit the engineer disclosed). The corpus (`index/`, `docs-source.toml`) is not in the diff. The spec's list also has README, runbook and status; those are Docs' and are not yet edited.

**C1.4** (the baseline repair adds `event-log.mjs` to that test's expected set "and nothing else in that test"). MET: the test diff is exactly that one line; the test passes.

**Live smoke after the deploy** (five questions; cost within 15% of $0.0078; no question text in any log table; kill switch on then off). NOT YET: stage 10. Not run by me (offline). I did not review `10-smoke/smoke.py` (ignored per the brief).

**Code review layer and Security Review; Release Gate tier 3; pull request.** NOT YET for Security (stage 6), Release Gate (stage 8) and the pull request; the code review exists (`code-review.md`: 5 findings, 0 Important, unscored per C3.R).

**README, CURRENT_MVP_STATUS and the runbook state only recorded figures; issues #6, #7, #8 closed by the PR.** NOT YET (stage 7 and stage 11).

## Safety invariants touched

| Invariant | Check | Result |
|---|---|---|
| Money: day cap never overshot by a retry (INV on spend; not renumbered) | T6.1, T6.2, `test_concurrent_admissions_never_exceed_cap` | pass; fail under mutation #6 |
| No question stored or logged | `tests/test_service_logging.py` (incl. `test_question_never_logged`): ran with the two tests below, 20 passed; also inside the three full runs | pass |
| No model call offline / when refused | `test_health_never_calls_model`, `test_each_limit_fails_closed_no_model_call`, `test_unusable_question_no_model_call`; the autouse network block in `tests/conftest.py` stayed on for all runs (no network ran) | pass |
| One retry only, none on timeout (INV-5) | `test_retry_once_only_on_retryable`, `test_no_retry_on_timeout`, `test_bad_stop_reason_on_retry_reports_attempts_2` (unedited, 18 named must-stay-green tests passed in a targeted run) | pass |
| Fail closed on prompt hash mismatch | `test_prompt_hash_mismatch_fails_closed` and the new `test_prompt_hash_mismatch_bills_nothing` | pass |
| Import allow-list of the adapter | `test_anthropic_judge_import_allow_list` | pass |
| INV-1 to INV-5 text, judge prompt, retrieval | byte identity above | pass |

## Open points for later stages (not blockers for this stage)

1. **Intent vs design, pause point.** The intent says the service now pauses at "about 41 questions a day"; reserving two attempts closes the day earlier (CR-3, spec section 3 estimate: about 33). I did not recompute the 33; it is the Architect's labelled estimate (unconfirmed by me, where I looked: spec section 3, code-review CR-3). Docs must quote the labelled estimate, and the owner should know the intent's 41 is not what the chosen option gives.
2. **Security to rule on** the capacity effect (CR-3) and the 429-then-success charge change (T7.4), as the spec and review already ask.
3. **CR-4 (pre-existing):** `settle` adds actual cost unclamped, so a real input over the byte-based estimate could pass the reservation. Not in scope; not tested by this slice.
4. T6.1 on head is satisfied by a refusal (CR-1); do not read it as proof that a retry ran inside the cap. T6.2 is that proof.
5. The pricing-page claim in the code comment could not be checked offline.

## Hand-off to Security & Privacy

GO WITH CONDITIONS as above. Read: `aveto_service/{pipeline,judge_port,anthropic_judge,settings}.py`, `infra/main.bicep`, and the new tests named here. Scratch outputs (not committed): `/private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/b964fb4e-04f7-4fbf-b787-36bfe8d105df/scratchpad/{pytest1,pytest2,pytest3,ff}.txt`.
