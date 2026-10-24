# Tech Spec — fix-service-accounting (issues #6, #7, #8)

> Owner: Software Architect Agent (stage 2, depth standard, 2026-10-23)
> Status: ready for implementation
> Source: `intent.md` (short path: no feature or UX spec), `00-slice-plan.md`, `CHARTER.md` (sha256 afc984d1…), `01-scope.md`.
> Read for this spec: `aveto_service/{pipeline,anthropic_judge,judge_port,settings,limits}.py`, `infra/main.bicep`, `infra/main.parameters.json` (via `test_infra_static.py`), `tests/{service_fakes,test_service_limits,test_service_pipeline,test_anthropic_judge,test_infra_static}.py`, `runs/public-ask-the-docs/05-tech-spec.md` §3, §7, §8, `runs/public-ask-the-docs/17-deploy/{README.md,e3-rollback.txt,g5-canary.txt}`, `18-gate/g5-recheck.txt`, `docs/runbooks/public-ask.md`, `README.md` 200-240, `.agentic/CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md` 250-285, `evals/retrieval-heldout-5.toml`, `runs/docs-answerability-2/07-gate-scoring.md` and `judge-check/stage7/verdicts.toml`.
> File name: the Orchestrator asked for `05-tech-spec.md`; `01-scope.md` names it `02-tech-spec.md`. This file is the stage 2 artefact under the Orchestrator's name.

## Summary

Three defects in how `aveto_service` reserves and settles judge spend, fixed in one change and redeployed. **#6:** admission reserves one attempt but the adapter may send two; the fix reserves `MAX_ATTEMPTS` (2) full per-attempt reservations at admission and lets settlement return what was not used. **#7:** the final error's category zeroes the whole charge; the fix has the adapter count, per attempt, the failed attempts that may have been billed, carried out as an integer on the port's types, and the pipeline charges from that count. **#8:** price defaults go from 3000/15000 to 2000/10000 nano-dollars per token in `settings.py` and `infra/main.bicep`. Five source files change, as `01-scope.md` requires. No change to `aveto_support/`, `prompts/`, `.claude/`, the safety invariants, the retrieval, the judge prompt or the corpus. **No safety-text change is needed** (§9): INV-5's "at most two attempts per question" stays true, and no invariant states a charging rule.

## Done means → design (short-path trace)

| intent "Done means" line | Satisfied by |
|---|---|
| Starts from `main` after PR 5, pack v28 | Already true at setup (plan, C6.1); nothing to design |
| #6 fixed, test fails first | §1 (option A), §5 tests T6.1 (fail-first), T6.2 |
| #7 fixed, test fails first, rule in one sentence | §2 (rule, port fields), §5 tests T7.1, T7.3, T7.4 (fail-first), T7.2 |
| #8 fixed, comment with source and date, override stays, every quote updated | §3, §5 tests T8.1, T8.2 (fail-first), §3.3 quote list |
| Nothing else moves | §6 (exact commands) |
| Live smoke | §8 |
| Review layer, Security standard, Gate tier 3 | Unchanged stages; §10 lists what Security reads |
| README, status, runbook state recorded figures; issues closed by the PR | §3.3 (figures for Docs); PR text at stage 11 |

## Baseline: what is observed and what is only read

I have no shell (Read, Write, Edit, Grep, Glob), so **none of the three defects has been reproduced by me.** Each is deterministic and read from the code at 87178bd: `pipeline.py:246-258` reserves one `reservation_amount`; `anthropic_judge.py:136` retries once on 429, 5xx and connection errors; `pipeline.py:286` adds `(attempts - 1) * amount` at settlement; `pipeline.py:275-288` sets `charge = 0` whenever the *last* category is `status_4xx` or `connection`; `settings.py:15-16` and `main.bicep:31,34` hold 3000/15000. The observation is the stage 3 fail-first run: each test marked fail-first in §5 is run against the 87178bd source and must fail **with the figure named in §5**. If one passes on 87178bd, or fails with a different figure, stage 3 stops and reports it; it does not claim a fix for that issue.

## 1. #6: reserve every possible attempt at admission (option A)

**Choice: (a) reserve both possible attempts up front; settlement returns the unused part.** Not (b).

Why (a):
- **It is all in `pipeline.py`.** `SpendCounter.settle` already does the refund: it removes `reservation.amount` from `in_flight` and adds the actual charge to `spent` (`limits.py:192-208`). Reserving `MAX_ATTEMPTS × per_attempt` and settling the true charge needs no change to `limits.py` (not one of the five files) and no new method.
- **The port stays as it is.** (b) needs the adapter to hold a budget handle (a callback or a two-step `judge`), which puts spend accounting on the far side of the model boundary, changes the `JudgeClient` Protocol, and touches every fake (`FakeJudgeClient`, `SlowJudge`, `BlockingJudge`, `PlaceholderJudgeClient`) plus a second `Reservation` per request to settle. That is the port and fake-client churn `01-scope.md` warned would put stage 3 at risk.
- **The bound is then structural, not a race.** Each attempt costs at most one per-attempt reservation (a failed billable attempt is charged exactly that; a response's usage is bounded by it, `limits.py:166-170`), and the adapter makes at most `MAX_ATTEMPTS`. So the settled charge is at most the reservation, and `reserve` already guarantees `spent + in_flight + reservation ≤ cap`. Settled spend can no longer pass the cap because of a retry.

What it costs (stated, accepted):
- Admission needs room for two attempts. The day pauses earlier: by spend about 41 questions fit, but the pause comes when settled spend leaves less than two per-attempt reservations, **about 33 questions a day (estimate**, assuming a request of about 10,000 bytes of system prompt plus payload, so a per-attempt reservation of about $0.030 at $2/$10; the payload size is not measured here). On the same basis the service paused at about 23 a day before this slice (one reservation of about $0.045 at $3/$15, $0.0118 counted per question).
- At most about half as many requests can be in flight at once near the cap. With `maxReplicas: 1`, one uvicorn worker and retrieval serialised by a lock, this is not a throughput limit in practice (unconfirmed under load; no load test exists).
- MAX_ATTEMPTS stays 2 (`01-scope.md` constraint; INV-5's words depend on it).

### 1.1 Exact effects

| Item | Change |
|---|---|
| `MAX_ATTEMPTS` | Moves to `judge_port.py` as the port's contract (`MAX_ATTEMPTS = 2`). `anthropic_judge.py` imports it from there, so `anthropic_judge.MAX_ATTEMPTS` still resolves (the import allow-list test already permits `aveto_service.judge_port`). The pipeline imports it from the port, never from the adapter. |
| `SpendCounter.reservation_amount` (`limits.py`) | **Unchanged.** It stays the per-attempt bound. `limits.py` does not change. |
| Admission (`pipeline.py` step 7) | `per_attempt = reservation_amount(system_bytes, payload_bytes)`; `reserve(day, MAX_ATTEMPTS * per_attempt)`. `_judged` receives `per_attempt` (the unit it charges in) and the `Reservation` (whose `.amount` is the doubled figure). |
| Floor (`pipeline.py:192`) | `self._floor = MAX_ATTEMPTS * reservation_amount(system_bytes, 0)`. The floor must stay a lower bound on what admission will ask for, and the smallest admission is now two empty-payload attempts. `peek` is unchanged. |
| Day close | Unchanged rule in `reserve`: the day closes when settled spend plus the (now doubled) reservation is over the cap. |
| Settlement | `settle(reservation, charge, in_tokens, out_tokens)`; `charge` per §2; `in_flight` drops by the doubled amount, so the unused attempt is returned at settlement. The refund never makes `spent` lower than the true charge: nothing is ever subtracted from `spent`. |
| Non-transport exception from the adapter (`except Exception`) | Keeps today's charge of **one** per-attempt reservation (`test_non_transport_failure_keeps_full_reservation` unchanged). The real adapter maps every exception inside its loop to `JudgeTransportError`, so an unexpected exception can only come from before the first send (prompt check, request build); one attempt is already a conservative charge. |
| `JudgeNotConfiguredError` | Unchanged: settle 0, `counted=False`. |
| `test_inflight_reservations_do_not_close_the_day` | Its intent stays ("room for three in flight, and the floor check still passes for a fourth") but its arithmetic must use the request's reservation: `reserved = MAX_ATTEMPTS * amount`, `cap = spent + 3 * reserved + service._floor`. Without that edit the cap admits one or two in flight, not three; the test's assertions (a `PAUSED` result, day not closed, an `ANSWER` after) are kept as they are. |
| `test_concurrent_admissions_never_exceed_cap` | Same edit: `cap = spent + 3 * reserved + reserved // 2`, and `assert service._spend.in_flight == 3 * reserved`. This assertion is what pins the doubled reservation (it would read `3 * amount` on 87178bd). |
| Other existing tests | `test_each_limit_fails_closed_no_model_call` steps 5 and 7, `test_spend_pause_closes_day`, `test_spend_resets_at_utc_midnight` set `cap` from `service._floor` (± 1000) and keep their meaning with the doubled floor: unchanged. `test_failed_call_charge_by_category`, `test_spend_reservation_bounds_and_settles` compare with the per-attempt figure from `reservation_amount`, which is still what each billable attempt is charged: unchanged except §3.2's price lines. |
| Port (`judge_port.py`) | Signature of `JudgeClient.judge` unchanged. Additions are §2's. |
| Stage 3 size | Option A keeps stage 3 inside its 110k estimate (estimate, not measured): five small source edits, about six new tests, about eight changed test lines, and the smoke script of §8. Option B is not chosen, so its size is not estimated beyond the churn listed above (a Protocol change, four fakes, a second reservation per request). |

## 2. #7: charge each attempt on its own outcome

**The rule, in one sentence:** every attempt the adapter makes is charged on its own outcome — its reported usage at the configured price if it returned a usable response, nothing if it failed as `status_4xx` or `connection` or was never sent, and one full per-attempt reservation for any other failure — so a later attempt's category never changes what an earlier attempt is charged.

Worked through (per-attempt reservation `R`, usage cost `C`):

| Attempts | Charge today (87178bd) | Charge after |
|---|---|---|
| 503, then 400 | 0 (the bug) | `R` |
| 503, then 503 | `2R` | `2R` |
| 503, then success | `C + R` | `C + R` |
| 503, then `stop_reason` | `2R` | `2R` |
| 429, then 400 | 0 | 0 |
| connection, then connection | 0 | 0 |
| **429, then success** | `C + R` | **`C`** (see note) |
| timeout (no retry) | `R` | `R` |
| 400 (no retry) | 0 | 0 |
| prompt-hash mismatch (nothing sent) | 0 | 0 |
| success | `C` | `C` |

**Note on 429 then success.** The same rule applied to the success path stops charging a rate-limited first attempt that the code already classes as never billed (`status_4xx`). It is the one behaviour change outside the exact case #7 names. It is kept, rather than special-cased, because a rule that read differently on success and on failure would be two rules; it lowers a charge only for a category the service already charges nothing for on its own. Security (stage 6) is asked to confirm or reject it (§10). The `status_4xx`/`connection` classification itself is inherited from the previous slice and is not revisited (whether a connection error after the request reached Anthropic can be billed is not established; looked: `runs/public-ask-the-docs/05-tech-spec.md` §3, the runbook §5; neither cites a source).

### 2.1 How "an earlier attempt may have been billed" leaves the adapter

A **count**, carried on the port's existing types. Never exception text, never a message: the exception's `args` stay `(category,)`.

| Type (`judge_port.py`) | Change | Meaning |
|---|---|---|
| `NEVER_BILLED: frozenset[str]` | **new constant**, `{"status_4xx", "connection"}`, moved from `pipeline._NEVER_BILLED` (which is removed) | The categories the provider does not bill. One definition, used by the adapter and by the default below |
| `MAX_ATTEMPTS: int = 2` | **moved here** from `anthropic_judge.py` | §1.1 |
| `JudgeCall.billable_failures: int \| None = None` | **new field** (last, with a default, so every existing `JudgeCall(...)` still builds) | Failed attempts *before* the successful one that may have been billed. `None` means the adapter did not say: the pipeline then charges `attempts - 1` of them, which is today's rule (fail safe: it never charges less than 87178bd did) |
| `JudgeTransportError(category, attempts=1, billable_failures=None)` | **new keyword argument**, stored as an `int` attribute `billable_failures` | Attempts made that may have been billed, the final one included. When not given it resolves in `__init__` to `0` if `category in NEVER_BILLED` or `attempts == 0`, else `attempts`, which reproduces exactly what the pipeline charges today for every exception the existing tests and fakes construct. `super().__init__(category)` is unchanged |

**Adapter (`anthropic_judge.py`, `judge`):** a local integer counter of billable failed attempts, starting at 0.
- Before a retry (the `continue` branch): add 1 unless `_category(exc)` is in `NEVER_BILLED`.
- On the final failure from the SDK: raise `JudgeTransportError(category, attempts=attempts, billable_failures=counter + (0 if category in NEVER_BILLED else 1))`.
- On `extract_reply`'s `JudgeTransportError` (`stop_reason`, `tool_use`: a response arrived): re-raise with `billable_failures=counter + 1`.
- On success: `JudgeCall(..., attempts=attempts, billable_failures=counter)`.
- Prompt-hash mismatch: unchanged (`attempts=0`, which resolves to 0).
Nothing else in the adapter changes: no logging, no new import beyond the two names from `judge_port`, `raise ... from None` kept.

**Pipeline (`pipeline.py`, `_judged(found, payload, reservation, per_attempt)`):**
- `JudgeNotConfiguredError` → unchanged.
- `JudgeTransportError as exc` → `charge = exc.billable_failures * per_attempt`; tokens 0.
- Any other exception → `charge = per_attempt` (unchanged).
- A `JudgeCall` → `failed = call.billable_failures if not None else max(0, call.attempts - 1)`; `charge = cost(usage) + failed * per_attempt` when both token counts are present, else `per_attempt + failed * per_attempt`; tokens as reported.
- The `unbilled` flag, `_NEVER_BILLED` and `charge += (attempts - 1) * amount` go. `settle` is called once, under the lock, as now.
- Invariant (asserted by T6.2 and T7.1, not by a runtime check): with at most `MAX_ATTEMPTS` attempts, `charge ≤ reservation.amount`. No clamp is added: if an adapter ever broke the contract, the counter should record the true charge, not hide it.

### 2.2 Files

Exactly the five named in `01-scope.md`: `aveto_service/judge_port.py` (§2.1 types, `MAX_ATTEMPTS`, `NEVER_BILLED`), `aveto_service/anthropic_judge.py` (§2.1 counter; `MAX_ATTEMPTS` imported), `aveto_service/pipeline.py` (§1.1 and §2.1), `aveto_service/settings.py` and `infra/main.bicep` (§3). `limits.py`, `abuse_log.py`, `app.py`, `tests/service_fakes.py` do not change.

## 3. #8: price defaults 2000 and 10000

### 3.1 Source changes

| File | Line today | After |
|---|---|---|
| `aveto_service/settings.py` | 15 `DEFAULT_PRICE_IN_NANO = 3000` | `2000`, with a comment above the two constants: `claude-sonnet-5-5`: $2 per million input tokens, $10 per million output tokens; read 2026-10-23 from Anthropic's pricing page and matched by the owner's console bill (intent #8). |
| `aveto_service/settings.py` | 16 `DEFAULT_PRICE_OUT_NANO = 15000` | `10000` |
| `infra/main.bicep` | 31 `param priceInNanoPerToken int = 3000` | `2000`; the `@description` stays and a `//` comment line above the pair names the same source and date |
| `infra/main.bicep` | 34 `param priceOutNanoPerToken int = 15000` | `10000` |

- The `ASK_PRICE_IN_NANO_PER_TOKEN` / `ASK_PRICE_OUT_NANO_PER_TOKEN` override in `Settings.from_env` stays as it is, including its fail-closed parse.
- The Bicep keeps passing the price to the container as env values (`main.bicep:186-187`), so the deployed revision's env becomes `2000`/`10000` from the template defaults; `infra/main.parameters.json` carries only `location` and is not changed (no price there, so the template default is what applies).
- 1 nano-dollar per token = $1 per million tokens, so 2000/10000 are exactly $2/$10.

### 3.2 Test lines that quote the old figures

| File:line (87178bd) | What it does | Change |
|---|---|---|
| `tests/test_service_limits.py:449` | `actual = 1000 * 3000 + 10 * 15000` under `make_settings()` defaults | **must change**: `1000 * 2000 + 10 * 10000` (it reads the defaults, not explicit prices; `01-scope.md` listed it as "may stay", which is not so) |
| `tests/test_service_limits.py:489` | `100 * 3000 + 10 * 15000` under defaults | **must change**: `100 * 2000 + 10 * 10000` |
| `tests/test_service_limits.py:463-465` | `SpendCounter(10**9, 3000, 15000)`: the reservation formula with explicit prices | **stays** (explicit prices, tests the formula, not the default) |
| `tests/test_service_limits.py:474` | `Settings().daily_cap_nano` | stays (cap only) |
| `tests/test_service_limits.py:155`, `:542` | cap only | stay |

### 3.3 Docs lines that quote the old figures (for stage 7; recorded figures and their arithmetic)

The baseline cost per question is **$0.0078**: recorded 71,151 input and 1,460 output tokens for 20 gate questions → 71,151 × $2e-6 + 1,460 × $10e-6 = $0.142302 + $0.014600 = **$0.156902 / 20 = $0.0078451**, which is $0.0078 to four places. The docs' "about $0.0079" is a rounding up of the same figure; the intent and Charter C8.1 say $0.0078. **The smoke's 15% band uses $0.0078** (band $0.00663 to $0.00897), as the intent and Charter say; I see no reason to depart from it. I recommend stage 7 write "$0.0078 ($0.1569 for 20)" where the docs now say "$0.0079"; that is the Tech Writer's wording call, and the Charter's figure is not changed by it.

The intent's "$0.0118 per question" appears nowhere in the repo (`01-scope.md`); it is the old counter's figure, $0.00785 × 1.5 = $0.01177. Nothing to edit for it.

| Place | Now says | Fact to state after this slice |
|---|---|---|
| `README.md:211` | $0.0079; "counter uses built-in defaults of $3 and $15, so it reads 50% high ($0.2354 …); safe side" | $0.0078 ($0.1569 / 20, recomputed from recorded tokens at $2/$10). The counter's defaults are $2 and $10 from this slice's deploy; the "50% high" sentence goes (it was true of revision `ca-aveto-ask--0000006` only). $0.0099 for the first live question is already at $2/$10 (4,641 × 2e-6 + 60 × 1e-5) and stays |
| `README.md:230-236` | $0.0079; "daily pause, counting at $3 and $15, comes at about 27 questions a day (about 41 at the real price)"; price settings "have not been changed …; owner's call" | $0.0078; about 41 questions a day fit the $10/31 share by spend ($0.3226 / $0.00785); the pause comes earlier because a question is admitted only when two full attempts' reservations fit: about 33 a day (**estimate**, assumes a per-attempt reservation of about $0.030); the price defaults are 2000 and 10000 since this slice's deploy. 1,270 a month at $0.0078 stays (10 / 0.00785 = 1,274) |
| `docs/runbooks/public-ask.md:10-11` | $0.0079; "(the service's counter reads 50% high)" | $0.0078; drop the parenthesis |
| runbook `:118` | $0.0079; "the service's own counter, at its $3 and $15 defaults, reads 50% high" | $0.0078; the counter uses $2 and $10 |
| runbook `:133-135` (§5) | "A failed 5xx or timed-out call keeps the full reservation; a 4xx or connection failure is charged nothing." | The §2 rule, and that admission reserves two attempts and returns the unused part at settlement |
| runbook `:181-183` (§7) | "about three failed questions can pause the day" | about five questions whose two attempts both fail with a 5xx can pause the day (**estimate**, same $0.030 assumption) |
| runbook `:188` | "about 40 questions from a few addresses pause the service" (decision D4) | consistent with "about 33 to 41"; a decision record, the Tech Writer decides whether to touch it |
| runbook `:242-246` | $0.0079; "27 questions a day by its own counter (about 41 at the real price)" | as README 230-236 |
| runbook `:257-261` | "built-in defaults assume $3 and $15 … overstates real cost by 50% … It has not been done; it is the owner's call." | defaults are 2000/10000 since this slice (source and date as §3.1); `ASK_PRICE_*` still override |
| `.agentic/CURRENT_MVP_STATUS.md:43-51` | as README 211 and 230-236 | as README |
| `.agentic/CURRENT_MVP_STATUS.md:147-151` | open item: set the price env values to 2000 and 10000 | done by this slice; the line goes |
| `docs/ARCHITECTURE.md` steps 5, 7, 8 | one reservation; last-category charging | **updated by me in this stage** (my file; §11) |

Every figure above that depends on the payload size (33 a day, five failed questions) is an estimate and must be labelled so. The recorded figures are $0.1569 for 20, 71,151 and 1,460 tokens, $0.0099 for the first live question, and whatever stage 10 measures.

## 4. Data model, service surface, adapters, events, integration

**Data model deltas.** No storage exists and none is added. In-memory types only:

| Type | Change | Rationale |
|---|---|---|
| `judge_port.JudgeCall` | modified: `billable_failures: int \| None = None` | §2.1 |
| `judge_port.JudgeTransportError` | modified: `billable_failures: int` attribute, keyword argument defaulting as §2.1 | §2.1 |
| `judge_port.NEVER_BILLED`, `judge_port.MAX_ATTEMPTS` | new module constants (moved, not invented) | one definition each, shared by adapter and pipeline |
| `limits.Reservation`, `limits.SpendCounter` | unchanged | the doubled amount is just a larger `amount` |

**Service surface.**

| Function | Signature | Invariant |
|---|---|---|
| `pipeline.AskService.__init__` | unchanged | `self._floor == MAX_ATTEMPTS * reservation_amount(system_bytes, 0)` |
| `pipeline.AskService._ask` | unchanged | an admitted request holds `MAX_ATTEMPTS * per_attempt` in `in_flight` until settled |
| `pipeline.AskService._judged` | `(found, payload, reservation, per_attempt) -> AskResult` (parameter renamed from `amount`; same position) | settles exactly once; `charge` per §2; `charge ≤ reservation.amount` for any adapter within `MAX_ATTEMPTS` |
| `anthropic_judge.AnthropicJudgeClient.judge` | unchanged | `billable_failures` on every `JudgeCall` and `JudgeTransportError` it produces, `0 ≤ billable_failures ≤ attempts ≤ MAX_ATTEMPTS` |
| `settings.Settings` | unchanged fields | defaults 2000/10000 |

**Adapter boundaries.** Unchanged. The judge port is the only model boundary; `PlaceholderJudgeClient` still raises `JudgeNotConfiguredError` when no key is set, so every test runs without a key; the real adapter is tested only through an injected fake `messages` client. The new count is computed inside the adapter (the only place that sees each attempt) and crosses the boundary as an integer.

**Audit / feedback / usage events.** No new event and no changed event. The service's only events are the abuse line (`{"t","ip","o"}`, one per `POST /ask`, unchanged) and the ops lines; usage is the `/health` counters. What changes is the *meaning* of two counters: `spend_today_usd` is charged per §2 at $2/$10; `in_flight` (not exposed) holds two attempts per admitted request. The `billable_failures` count is **not** logged or exposed: adding it to a log line would change the C4.2 description of the log (and the INV-5 logging rules); nothing in this slice needs it outside the process.

**Integration points.** `aveto_support.judge` (`retrieve_for_judge`, `format_judge_input`, `parse_verdict`; unchanged, called as now); `limits.SpendCounter` (`reservation_amount`, `peek`, `reserve`, `settle`, `cost`; called as now, with a larger reservation); the Anthropic Messages API through the unchanged request.

**ADR.** None. No stack, storage, dependency or boundary decision is made: the accounting rule and the reservation size are recorded in `docs/ARCHITECTURE.md` (steps 7 and 8) and in this spec. No new dependency.

## 5. Test plan: fail-first tests and the changes to existing ones

All offline, in the default suite, no key, no network (the autouse block stays). The integration tests drive the **real** `AnthropicJudgeClient` over an injected fake `messages` client, so the retry really happens inside the adapter, as in production. `tests/test_service_limits.py` gains three small helpers local to the file: a fake `messages` object that returns or raises scripted items (the same shape as `test_anthropic_judge.FakeMessages`), an SDK-error builder (as `test_anthropic_judge._status`, with `httpx2`), and a probe that learns this question's per-attempt reservation by asking once through a `FakeJudgeClient` and reading `len(fake.calls[0][1].encode())`, as the existing spend tests do. `sleep` is injected as a no-op. **Prices are passed explicitly** (`make_settings(price_in_nano_per_token=2000, price_out_nano_per_token=10000)`) in every new pipeline test, so the figures are the same on 87178bd and after the fix.

**The reviewer's figures, mapped.** The usage of the successful attempt is fixed at 4,421 input and 50 output tokens: at $2/$10 that is `C = 4,421 × 2000 + 50 × 10000 = 9,342,000` nano-dollars = **$0.009342**, exactly the reviewer's overshoot ($0.039342 − $0.030000). The cap is set to one per-attempt reservation `R` of this test's payload (the role the reviewer's $0.030000 plays; the fake corpus gives a smaller `R`, and the test computes it rather than hard-coding $0.030000). On 87178bd the settled spend is then `R + C`, i.e. the reviewer's figure when `R` is $0.030000.

| Id | File :: test name | Script (fake API responses in order) | Exact assertions | On 87178bd |
|---|---|---|---|---|
| **T6.1 fail-first (#6)** | `test_service_limits.py::test_retry_never_settles_above_cap` | 503 (`InternalServerError`), then a message with usage 4,421 / 50 | `cap = R`. `assert service._spend.spent <= service._spend.cap, (service._spend.spent, service._spend.cap)`; then `assert service._spend.in_flight == 0`; then `assert result.outcome is Outcome.PAUSED and messages.requests == []` | **fails** on the first assertion with `spent == R + 9_342_000`, `cap == R` (overshoot $0.009342) |
| T6.2 guard (#6) | `test_service_limits.py::test_retry_settles_within_both_reserved_attempts` | same | `cap = 2 * R`. `result.outcome is Outcome.ANSWER`; `len(messages.requests) == 2`; `spent == R + 9_342_000`; `spent <= cap`; `in_flight == 0` | passes (a guard, not evidence) |
| **T7.1 fail-first (#7)** | `test_service_limits.py::test_5xx_then_4xx_charges_the_first_attempt` | 503, then 400 (`BadRequestError`) | default cap. `result.outcome is Outcome.JUDGE_ERROR`; `len(messages.requests) == 2`; `assert service._spend.spent == R`; `in_flight == 0` | **fails**: `spent == 0` |
| T7.2 guard (#7) | `test_service_limits.py::test_never_billed_attempts_charge_zero` (parametrised) | (429 `RateLimitError`, 400); (connection, connection); (429, 429) | `JUDGE_ERROR`; `spent == 0`; `in_flight == 0`; two requests each | passes |
| **T7.4 fail-first (#7 rule on success)** | `test_service_limits.py::test_never_billed_retry_then_success_charges_usage_only` | 429, then usage 4,421 / 50 | `ANSWER`; `assert service._spend.spent == 9_342_000` | **fails**: `spent == 9_342_000 + R` |
| **T7.5 fail-first (port default)** | `test_service_limits.py::test_port_defaults_reproduce_the_old_charge` | none (constructs the types) | for each `(category, attempts)` in `test_failed_call_charge_by_category`'s table: `JudgeTransportError(category, attempts=a).billable_failures == (0 if category in {"status_4xx", "connection"} or a == 0 else a)`; `JudgeCall("x", 1, 1, attempts=2).billable_failures is None`; `JudgeTransportError("status_4xx", attempts=2, billable_failures=1).billable_failures == 1` | **fails**: `AttributeError` / `TypeError` |
| **T7.3 fail-first (adapter)** | `test_anthropic_judge.py::test_billable_failures_counted_per_attempt` (parametrised) | rows: (503, 400) → error `status_4xx`, attempts 2, **1**; (429, 400) → `status_4xx`, 2, 0; (conn, conn) → `connection`, 2, 0; (503, 503) → `status_5xx`, 2, 2; (503, message `stop="max_tokens"`) → `stop_reason`, 2, 2; (timeout) → `timeout`, 1, 1; (400) → `status_4xx`, 1, 0; (message) → call, attempts 1, 0; (429, message) → call, 2, 0; (503, message) → call, 2, 1 | errors: `(err.category, err.attempts, err.billable_failures) == row`, `type(err.billable_failures) is int`, `err.args == (category,)`, `SECRET not in repr(err) + str(err)`; calls: `(call.attempts, call.billable_failures) == row`; prompt-hash mismatch: `info.value.billable_failures == 0` | **fails**: `AttributeError` |
| **T8.1 fail-first (#8)** | `test_service_limits.py::test_price_defaults_are_2000_and_10000` | — | `(Settings().price_in_nano_per_token, Settings().price_out_nano_per_token) == (2000, 10000)`; the same from `Settings.from_env({"ASK_KILL_SWITCH": "off"})`; and `Settings.from_env({"ASK_KILL_SWITCH": "off", "ASK_PRICE_IN_NANO_PER_TOKEN": "3000", "ASK_PRICE_OUT_NANO_PER_TOKEN": "15000"})` gives `(3000, 15000)` with `kill_switch == "off"` (the override stays) | **fails**: `(3000, 15000)` |
| **T8.2 fail-first (#8)** | `test_infra_static.py::test_bicep_price_defaults` | — | `re.search(r"param priceInNanoPerToken int = (\d+)\b", BICEP)` captures `2000` and the out param `10000`; both equal `settings.DEFAULT_PRICE_IN_NANO` / `DEFAULT_PRICE_OUT_NANO` (Bicep and code in lockstep); `"priceInNanoPerToken" not in PARAMS and "priceOutNanoPerToken" not in PARAMS` | **fails**: captures 3000 / 15000 |
| C1.4 repair | `test_service_pipeline.py::test_core_files_unchanged` | — | add `"event-log.mjs"` to the hook-name set; **nothing else in the test changes** (the `CORE_SHA256` table is the guard for §6) | the repair turns the baseline failure green; it is not fail-first evidence |

**Existing tests that change** (they encode the new behaviour, so they also fail on the 87178bd source; they are not fail-first evidence):
- `test_service_limits.py:449` and `:489`: prices, §3.2.
- `test_inflight_reservations_do_not_close_the_day` and `test_concurrent_admissions_never_exceed_cap`: `reserved = MAX_ATTEMPTS * amount` (import `MAX_ATTEMPTS` from `aveto_service.judge_port`), §1.1. The second asserts `in_flight == 3 * reserved`.

**Must stay green, unedited, by name:** `test_retry_once_only_on_retryable`, `test_no_retry_on_timeout` (cited in INV-5), `test_failed_call_charge_by_category`, `test_non_transport_failure_keeps_full_reservation`, `test_seven_4xx_failures_do_not_pause_the_day`, `test_bad_stop_reason_on_retry_reports_attempts_2`, `test_prompt_hash_mismatch_fails_closed`, `test_anthropic_judge_import_allow_list`, `test_core_files_unchanged`'s `CORE_SHA256` part, every `test_service_pages.py`, `test_service_logging.py`, `test_service_api.py` test.

**Fail-first procedure (stage 3).**
1. Write the new tests and the changed lines only. Show `git diff --stat 87178bd -- aveto_service infra` prints nothing (the source is 87178bd's).
2. Run `uv run pytest tests/test_service_limits.py tests/test_anthropic_judge.py tests/test_infra_static.py tests/test_service_pipeline.py -q` and save the output to `runs/fix-service-accounting/03-failfirst-87178bd.txt`. Required: T6.1, T7.1, T7.3, T7.4, T7.5, T8.1, T8.2 fail, each with the figure in the table (T6.1's message must show `R + 9342000` against `R`). T6.2 and T7.2 pass. If any required test passes, or fails for another reason, stop and report (Baseline section).
3. Implement §1 to §3. Run `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`: 0 failed; passed = 636 + 1 (C1.4) + the new test items; the 12 deselected unchanged. Save as `runs/fix-service-accounting/03-green.txt`.

Eval cases: none (no retrieval, prompt or judge change; no eval is rescored). UI checks: none (no visible change).

## 6. "Nothing else moves": the exact checks (stage 5 QA, again at stage 8)

The base is the commit, not the branch name, so the check does not drift if `main` moves: **87178bd** (= `main` at setup). Run from the worktree root on the final tree, after `git status --porcelain` shows only what is intended.

1. The intent's check, with the one exclusion `01-scope.md` recorded (the status file is a Docs target and Charter C1.3 forbids only `SAFETY_INVARIANTS.md`):
   ```
   git diff --exit-code 87178bd -- aveto_support prompts .claude .agentic ':(exclude).agentic/CURRENT_MVP_STATUS.md'
   ```
   Pass: no output, exit 0. (While `main` still equals 87178bd, `git diff --exit-code main -- …` with the same paths is the same command; stage 8 states which it ran.)
2. Each protected path on its own, so a reader sees each proven empty:
   ```
   git diff --exit-code 87178bd -- aveto_support
   git diff --exit-code 87178bd -- prompts
   git diff --exit-code 87178bd -- .claude
   git diff --exit-code 87178bd -- .agentic/SAFETY_INVARIANTS.md
   ```
   Pass: each prints nothing, exit 0.
3. Untracked files do not show in `git diff`, so also:
   ```
   git status --porcelain -- aveto_support prompts .claude .agentic
   ```
   Pass: no output, or only ` M .agentic/CURRENT_MVP_STATUS.md` (before it is committed). `.claude/settings.local.json` is gitignored and does not show.
4. The whole change set is the expected one:
   ```
   git diff --name-only 87178bd -- . ':(exclude)runs'
   ```
   Pass: a subset of exactly these 13 paths: `aveto_service/pipeline.py`, `aveto_service/anthropic_judge.py`, `aveto_service/judge_port.py`, `aveto_service/settings.py`, `infra/main.bicep`, `tests/test_service_limits.py`, `tests/test_service_pipeline.py`, `tests/test_anthropic_judge.py`, `tests/test_infra_static.py`, `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md`. Any other path is a finding. (`docs/ARCHITECTURE.md` is the Architect's file, edited at this stage, §11; it is the one file beyond `01-scope.md`'s count, and it is documentation.)
5. `test_core_files_unchanged` passes unmodified apart from C1.4: its `CORE_SHA256` table pins `aveto_support/*.py`, `prompts/answerability-judge-v1.txt`, `docs-source.toml`, the judge agent and skills and the two older hooks, byte for byte.
6. `tests/service_fakes.py` is not in the list in 4: the fakes need no change (§2.1 defaults).

## 7. Deploy command sheet (stage 9, Orchestrator's session, Charter C8.3)

Every command is literal so it matches a C6.P allow rule; there is **one placeholder, `<TAG12>`**, which the Orchestrator replaces with the literal 12-hex short commit of the gated HEAD before running anything (never `$(…)`, never a variable). Paths are absolute, so the commands do not depend on the shell's working directory; the build context is the **worktree root**, never the main checkout (Security S-C3 of the previous slice: the main checkout holds a symlink to the worktree). Save every output under `runs/fix-service-accounting/09-deploy/`, search it for `sk-ant` and key-shaped strings before committing, and mask the subscription id. Never run a command that prints a secret value (`az containerapp secret list --show-values`, `az keyvault secret show`, `az monitor log-analytics workspace get-shared-keys`).

Prices come from the **Bicep defaults** (2000/10000 after §3): no price parameter is passed. `monthlyCapUsd` (10) and `clientKey` (`xff_last`) defaults equal the live values (plan, "Live state read at setup"), so they are not passed either. `killSwitch` **is always passed** (its default is `on`, `test_bicep_kill_switch_default_on`). `configureLogRetention=true` is passed as in the previous run's command 5, so the two tables' 7-day retention is re-declared, not dropped from the template.

### 7.0 Pre-flight (read-only)

```
git status --porcelain
git log -1 --format=%h --abbrev=12
az account show --query "{name:name,state:state}" -o tsv
az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].{name:name,traffic:properties.trafficWeight,health:properties.healthState}" -o tsv
az containerapp show -g rg-aveto-ask -n ca-aveto-ask --query "properties.template.containers[0].{image:image,env:env[].{n:name,v:value,s:secretRef}}" -o json
az bicep build --file /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.bicep --stdout
```
Pass: no uncommitted change (the image must equal the commit); the second line gives `<TAG12>`; `Visual Studio Enterprise Subscription  Enabled` (expired sign-in is Charter stop 3); exactly `ca-aveto-ask--0000006  100  Healthy` (if the active revision is anything else, stop: the rollback target is not the one C6.6 and C8.1 name); the env shows `ASK_PRICE_IN_NANO_PER_TOKEN 3000`, `ASK_PRICE_OUT_NANO_PER_TOKEN 15000`, `ASK_KILL_SWITCH off`, `ANTHROPIC_API_KEY` as `secretRef anthropic-api-key` with no value (saved as the before-state); the Bicep compiles.

### 7.1 Build one image (C8.3)

```
az acr build -r acravetoaskgp -t aveto-ask:<TAG12> --platform linux/amd64 -f Dockerfile /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting
```
Pass: build and push succeed; the log's ingest line `wrote index/docs-index.json  sha256 <hex>` equals the previous build's `f36ef5d4…a756` (nothing in `aveto_support/`, `docs-source.toml` or the Dockerfile changed) and the local index used by the smoke (§8.2). A different hash is reported, not hidden, and makes the smoke's byte comparison a comparison against a different index (then the smoke reports byte equality as not established). `-f` is read relative to the source directory (from memory of the CLI, unconfirmed); a build that fails on the path pushes nothing and may be re-run with the corrected form; it is still "one new image".

### 7.2 D1: new image, kill switch ON (visitors see "The service is off" while the new code comes up)

```
az deployment group what-if -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.parameters.json -p deployApp=true imageTag=<TAG12> killSwitch=on configureLogRetention=true
```
Pass rule, fixed now: **no `Create`, no `Delete`**, no resource type outside C8.3. `Modify` on `ca-aveto-ask` showing the image tag `879cae23690b` → `<TAG12>`, `ASK_KILL_SWITCH` `off` → `on`, `ASK_PRICE_IN_NANO_PER_TOKEN` `3000` → `2000`, `ASK_PRICE_OUT_NANO_PER_TOKEN` `15000` → `10000`, and nothing else on the app. `Modify` lines on the environment, registry and role assignments were seen in the previous run and recorded as what-if noise (`runs/public-ask-the-docs/17-switch-on-recheck.md`); they are listed in the record, not a stop. A change to the tables' or workspace's retention, or any `Create`/`Delete`, is a failed check: no deploy (C8.1).

Start the watcher in the background first (§8.1, `watch on`), then:
```
az deployment group create -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.parameters.json -p deployApp=true imageTag=<TAG12> killSwitch=on configureLogRetention=true
```
Verify:
```
az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].{name:name,traffic:properties.trafficWeight,health:properties.healthState}" -o tsv
az containerapp show -g rg-aveto-ask -n ca-aveto-ask --query "properties.template.containers[0].{image:image,env:env[].{n:name,v:value,s:secretRef}}" -o json
```
Pass: one new revision (expected `ca-aveto-ask--0000007`; the number is a prediction from the previous sequence) at 100% and Healthy; image `acravetoaskgp.azurecr.io/aveto-ask:<TAG12>`; env `ASK_PRICE_IN_NANO_PER_TOKEN 2000`, `ASK_PRICE_OUT_NANO_PER_TOKEN 10000`, `ASK_KILL_SWITCH on`, `ASK_CLIENT_KEY xff_last`, `ASK_MONTHLY_CAP_USD 10`, key as `secretRef` only. The watcher shows `/health` `"kill_switch":"on"` and `POST /ask` → 503 `service_off`. A revision that does not become Healthy (for example a crash loop like F-LIVE-1) means the previous revision keeps serving or rollback R1 is run; stop and report.

### 7.3 D2: kill switch OFF (the service answers with the fix)

Same `what-if` and `create` as 7.2 with **`killSwitch=off`**, the watcher started first in `watch off` mode:
```
az deployment group what-if -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.parameters.json -p deployApp=true imageTag=<TAG12> killSwitch=off configureLogRetention=true
az deployment group create -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting/infra/main.parameters.json -p deployApp=true imageTag=<TAG12> killSwitch=off configureLogRetention=true
```
What-if pass: the only app change is `ASK_KILL_SWITCH` `on` → `off`; otherwise as 7.2. Verify with the same two read commands: a new revision (expected `ca-aveto-ask--0000008`) at 100% and Healthy, env as 7.2 with `ASK_KILL_SWITCH off`. D1 and D2 are the timed kill-switch check (§8.4). Then stage 10 runs §8.2 to §8.3 at once (inside one replica lifetime).

### 7.4 Rollback (C8.1, C8.3)

- **Before D1** (build failure, what-if failure, a failed gate): nothing to undo; `ca-aveto-ask--0000006` keeps serving; write the close-out and stop.
- **R1, on a behaviour failure after D1 or D2** (§8.5):
  ```
  az containerapp revision activate -g rg-aveto-ask -n ca-aveto-ask --revision ca-aveto-ask--0000006
  az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].{name:name,traffic:properties.trafficWeight,health:properties.healthState}" -o tsv
  ```
  Pass: `ca-aveto-ask--0000006` active with traffic 100 and Healthy, and `/health` answers `"kill_switch":"off"` (the old revision's env: old image, 3000/15000, switch off: exactly the pre-slice service). **Unconfirmed:** whether `revision activate` moves traffic back to an older revision under `activeRevisionsMode: 'Single'`; it has never been run on this app (the previous spec avoided it, P10, and the previous-image rollback was never rehearsed). It is the Charter's named rollback, so it is tried first.
- **R2, if R1 errors or 0000006 does not hold 100% within 5 minutes:** the kill switch on, with D1's `create` command exactly as in 7.2 (`killSwitch=on`). The service then refuses everything and calls no model. Report and stop.
- Redeploying the **old image** through the Bicep (`imageTag=879cae23690b`) is **not** in C8.3's words for this run ("the new image tag"); it is not used without the owner. Deleting anything is not allowed.
- **The code**: nothing is merged by the run (C8.2); undoing the code is not merging the pull request, or reverting its merge commit after the owner merges it. No data migration exists to undo: all counters are in memory and restart with each revision anyway (decision D1).

## 8. Live smoke (stage 10; a check, not a gate)

Service: `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io` (unchanged by a redeploy; same app name).

### 8.0 The five questions (fixed now, sent once each, through the real limits, no bypass: C8.5)

From **`evals/retrieval-heldout-5.toml`** (pinned commit `3a83b669…`), the fifth held-out set. **How it is known spent:** it was scored once at stage 7 of slice `docs-answerability-2` (`runs/docs-answerability-2/07-gate-scoring.md`, verdicts in `judge-check/stage7/verdicts.toml`); a held-out set is spent once scored. It is not the public gate set. (Note for the Orchestrator: `evals/public-gate-1.toml` *is* committed in this repo, contrary to "outside the repo" in the stage brief; it is not used either way.) None of these five has been sent through the API judge before; the expectations below are the attended judge's stage 7 verdicts.

| Order | Id | Kind | Stage 7 verdict | Right file in top 5 at stage 7 | Expected live outcome |
|---|---|---|---|---|---|
| 1 | `g01` | the docs answer it | ANSWERABLE | yes (not among the misses g05, g06, g18, g19, g22) | `answer` |
| 2 | `g03` | the docs answer it | ANSWERABLE | yes | `answer` |
| 3 | `g04` | the docs answer it | ANSWERABLE | yes | `answer` |
| 4 | `gu15` | the docs do not (not a hard negative) | NOT_ANSWERABLE | n/a | `no_confident_match` |
| 5 | `gu18` | the docs do not (not a hard negative) | NOT_ANSWERABLE | n/a | `no_confident_match` |

The questions are read from the eval file by id at run time; the record holds ids, never question or passage text.

### 8.1 The script (written at stage 3 by the Backend Architect, reviewed at stage 4, run at stage 9/10 by the Orchestrator)

`runs/fix-service-accounting/10-smoke/smoke.py`, run as `uv run python runs/fix-service-accounting/10-smoke/smoke.py <mode> …` from the worktree root (not `curl`, C6.P). Standard library HTTP only (`urllib.request`, `json`, `tomllib`, `decimal`, `time`, `datetime`) plus the local `aveto_support` for the comparison; no new dependency; it calls no `az` command and no host other than the service URL. It never retries a POST. It prints and writes ids, codes, counts and times only.

- **`watch on`** / **`watch off`** (timeout 600 s, poll every 2 s): records its start time (UTC, to the second), polls `GET /health`, and records the first time `kill_switch` equals the wanted value. For `on` it then sends one `POST /ask` with `{"question": ""}` and requires `503 {"outcome":"service_off"}` (an empty question can never reach retrieval or the model, even if a poll races the traffic shift and an old revision answers: that would give 400 `empty_question`, which is recorded and the POST repeated after 5 s, at most 10 times). For `off` it requires three consecutive `"off"` reads (the previous run saw about 6 s of the old revision after the deploy finished). Writes `runs/fix-service-accounting/10-smoke/watch-on.json` / `watch-off.json`. Exit 1 on timeout.
- **`ask --index <path> --models <path>`**: (1) loads `g01, g03, g04, gu15, gu18` from the eval file; (2) builds the local `Searcher` from the given index and models with the same loader the service uses at startup, records the index file's sha256, and computes `retrieve(searcher, judge.normalise_question(q))` for all five **before sending anything** (a local failure sends nothing); (3) `GET /health` (must be `status ok`, `kill_switch off`); (4) the five `POST /ask` in order, JSON body, recording HTTP status, `outcome`, wall time; for each `answer`, compares every file (`rank`, `path`, `url`) and passage (`heading`, `line_start`, `line_end`, `url`, `text` as UTF-8 bytes) with the local result and records `byte_equal` and, on a difference, the first differing field name; (5) `GET /health`; (6) computes §8.2; (7) writes `runs/fix-service-accounting/10-smoke/smoke-result.json` (start and end UTC, index sha256, per id: status, outcome, expected outcome, seconds, `byte_equal`; health before and after; deltas; figures).
- Index: the worktree's `index/docs-index.json` and `models/` if present, else the main checkout's (`/Users/gopalpatwa/opt/aveto-support/index/docs-index.json`, `/Users/gopalpatwa/opt/aveto-support/models`), read only. Its sha256 must equal the build log's ingest hash (§7.1); if not, byte equality is "not established" and reported.

### 8.2 Cost per judged question from `/health`

All five run within one replica lifetime, straight after D2 (well inside the scale-to-zero cooldown, about 300 s, unconfirmed): the window is valid only if `day` is the same before and after and `judged_today` did not go down (a restart resets every counter; then the cost is "not measured", reported, and **not re-run**: the questions are sent once).

- `Δjudged = after.judged_today − before.judged_today` (expected 5); `Δin`, `Δout` likewise; `Δspend` from the two `spend_today_usd` strings converted to nano-dollars exactly (`Decimal × 10⁹`).
- **Cost per judged question** = `(Δin × 2000 + Δout × 10000) / Δjudged` nano-dollars, i.e. at Anthropic's $2/$10. **Band: within 15% of $0.0078 = $0.00663 to $0.00897.** Outside the band is reported as measured; it is not a rollback (C8.1).
- **Live check of #8:** with no retry, `Δspend` must equal `Δin × 2000 + Δout × 10000` to within 2,000 nano-dollars (each `spend_today_usd` reading is truncated to 1,000 nano-dollars). Equal → the deployed counter charges at $2/$10. `Δspend` above the token cost by about one per-attempt reservation → a billable retry happened (the service logs no category; reported). Any other difference is a finding for the end review.

### 8.3 No question text in any log table

Wait at least 5 minutes after the last smoke request; first confirm the smoke's own abuse rows have arrived (otherwise a zero proves nothing); re-query up to three times over 30 minutes if they have not. `<WORKSPACE_ID>` is the workspace's customer id and `<D1_START_UTC>` the watcher's start time for D1, both filled in as literals.

```
az monitor log-analytics query -w <WORKSPACE_ID> --analytics-query 'ContainerAppConsoleLogs_CL | where TimeGenerated > datetime(<D1_START_UTC>) | where Log_s has "ip" | project TimeGenerated, Log_s' -o tsv
az monitor log-analytics query -w <WORKSPACE_ID> --analytics-query 'search "count as approving" or "long-lived feature branch" or "website goes wrong" or "Who founded Aveto" or "right-to-left languages" | where TimeGenerated > datetime(<D1_START_UTC>) | summarize hits=count() by $table' -o tsv
az monitor log-analytics query -w <WORKSPACE_ID> --analytics-query 'search "approving" or "long-lived" or "website" or "founded" or "right-to-left" | where TimeGenerated > datetime(<D1_START_UTC>) | summarize hits=count() by $table' -o tsv
```
(Single quotes around each query, so the shell expands nothing; `$table` is KQL's, not a shell variable.)
Pass: the first lists exactly the expected abuse lines (`{"t":…,"ip":"<16 hex>","o":…}` for the five outcomes, plus the watcher's `service_off` or `empty_question` lines), nothing else shaped like request data; the second and third return no rows. A row from the third query is inspected: it fails the check only if it holds question words. (The column name `Log_s` and the KQL `search` phrase syntax are from memory, unconfirmed; the previous run's queries were not saved as commands. The query text is the Production Verification role's to correct before the run; the pass rule does not change.)

**Gap in C6.P (for the Orchestrator):** the workspace customer id is not recorded anywhere in the repo (looked: `runs/public-ask-the-docs/17-deploy/*`, `18-gate/*`, the runbook). Reading it needs `az monitor log-analytics workspace show -g rg-aveto-ask -n log-aveto-ask --query customerId -o tsv`, which is read-only and prints no secret but is **not** in C6.P's allow list, so its first use will prompt. That is a permission prompt, not a Charter stop (it is not an action of section 9.1's kinds); record it in `END_REVIEW.md` as the gated commands' prompts are. Do not work around it (for example through a script that shells out to `az`).

### 8.4 Kill switch, timed

D1 (`on`) and D2 (`off`) of §7 are the kill-switch check. Reported: seconds from the watcher's start (immediately before `create`) to the wanted state, and the `create` command's own duration. Compared with the previous run's 65 s (on) and 66 s plus about 6 s (off), with the caveat that D1 also pulls a new image, so its figure is not a like-for-like toggle time. Pass: each state reached within 600 s, and with the switch on `POST /ask` answers `service_off`.

### 8.5 Verdict rules (fixed before the run)

- **Behaviour failure → R1 (activate `ca-aveto-ask--0000006`), else R2 (kill switch on); report; stop (C8.1):** any of the five not answered with HTTP 200 and `answer` or `no_confident_match` (for example `judge_error`, `paused`, `rate_limited`, a 5xx or a network error); any `answer` not byte-equal to the local `retrieve` (when the index hashes match); question words in any log row; a kill switch that does not take; `Δjudged ≠ 5` in a valid window.
- **`gu15` or `gu18` answered with passages** (a not-answerable question shown): the runbook's canary rule applies, **R2 directly** (kill switch on) and stop. The judge is unchanged by this slice, so the old revision would behave the same.
- **Reported as measured, not a rollback:** `g01`, `g03` or `g04` answered `no_confident_match` (over-abstention, a known judge behaviour, 2 of 10 at the public gate); the cost outside the band; a `Δspend` that shows a retry; an index-hash mismatch (byte equality then not established).
- Spend: five questions at about $0.0078 is about $0.04 of the day's $0.3226 share; the double reservation is about $0.06 per question in flight (estimate). Nothing here bypasses a limit.

## 9. Safety text (Charter C5.0): no change needed

Checked `.agentic/SAFETY_INVARIANTS.md` for every word about charging, billing, reservations, prices, attempts and spend (grep `charg|billed|reserv|price|attempt|spend|cap`): the only hits are a test name (`test_oversize_reply_is_judge_error_and_charged`, line 144, still true and still passing) and INV-5's "at most two attempts per question" (line 220), which stays true because `MAX_ATTEMPTS` stays 2 and the request is unchanged. No invariant states a charging rule, a price or a reservation size. The new `billable_failures` count is not logged and adds no field to the abuse line, so the logging rules are untouched. **No safety-text change is needed; the run does not stop on C5.0.** If stage 3 finds otherwise, it stops and says so.

## 10. Risks, open items, and what Security (stage 6) reads

| # | Item | Handling |
|---|---|---|
| R1 | 429-then-success charges the usage only (§2 note): a lower charge than 87178bd for one case | Kept for one rule; Security confirms or rejects. If rejected, the alternative is to count every failed retry as billable on the success path only (`billable_failures = attempts - 1` for `JudgeCall`), which is a one-line change in the adapter and T7.4's figure |
| R2 | Admission now needs two attempts' room: fewer questions a day (about 33 by estimate, against about 41 by spend) and about half the in-flight capacity near the cap | Accepted (§1). Stated in the docs as an estimate |
| R3 | `revision activate` under single-revision mode is unproven on this app | R2 (kill switch on) is the fallback, in the Charter's words |
| R4 | `connection` treated as never billed is inherited, not sourced | Not revisited (out of scope); listed for the end review |
| R5 | Workspace customer id not in C6.P (§8.3) | One read-only prompt, recorded |
| R6 | The five smoke questions were judged by the attended path, not the API path | Expectations are labelled as stage 7 verdicts; only shown-unanswerable is a stop |
| R7 | Counters reset with each revision (D1); D1 and D2 create two revisions | The smoke runs after D2 inside one lifetime (§8.2) |

**Security (standard, C7.1) reads:** `pipeline.py` `_ask` step 7 and `_judged`; `judge_port.py`; `anthropic_judge.py` `judge`; `settings.py` 15-16; `main.bicep` 30-34; the new and changed tests in §5. Questions for it: does any path settle above `reservation.amount` for an adapter within `MAX_ATTEMPTS`; can `billable_failures` carry anything but an integer; does the 429 rule (R1) under-count; is the floor still a lower bound.

## 11. Living architecture record

`docs/ARCHITECTURE.md` steps 5, 7 and 8 (the spend peek, admission, judge settlement) are updated by me in this stage to describe the system after this slice: admission reserves two full attempts, the floor is two empty-payload attempts, and each attempt is charged on its own outcome. No other part of the file states a price or a charging rule. No ADR (§4).

## 12. Work split and hand-off

| Stage, role | Owns (edits) | Reads only |
|---|---|---|
| 3 Backend Architect | `aveto_service/{pipeline,anthropic_judge,judge_port,settings}.py`, `infra/main.bicep` (no sixth source file without telling the Orchestrator), `tests/{test_service_limits,test_service_pipeline,test_anthropic_judge,test_infra_static}.py`, `runs/fix-service-accounting/10-smoke/smoke.py`, `runs/fix-service-accounting/03-implementation.md` with `03-failfirst-87178bd.txt` and `03-green.txt` | this spec, `limits.py`, `tests/service_fakes.py`, the eval file |
| 7 Tech Writer | `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md` (§3.3 facts; the runbook's command block should use §7's literal form or say why not) | this spec, stage 10's record (the smoke figures arrive after stage 7: either Docs runs a short addendum after stage 10, or the docs carry only the recorded figures above and the smoke result is added at stage 11; the Orchestrator chooses) |
| 9 Cloud Deployment, Orchestrator | the command record under `runs/fix-service-accounting/09-deploy/` from §7 | `infra/*`, this spec |
| 10 Orchestrator, Production Verification | runs §8; writes `runs/fix-service-accounting/10-smoke/` records | this spec |

**Hand-off:** Backend Architect (stage 3). Artefacts: code and tests per §1 to §5, the smoke script per §8.1, the fail-first record, one focused commit (or tests-first then fix, so the fail-first state is visible in history).

