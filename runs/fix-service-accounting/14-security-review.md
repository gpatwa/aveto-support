# Security & Privacy review: fix-service-accounting (stage 6)

- **Agent:** Security & Privacy, depth **standard** (Charter C7.1), `claude-opus-5-5`, 2026-10-23. Offline: no live service, no `az`, no network.
- **Scope (C7.1):** the accounting code, the price defaults and the new tests. No new input surface. `git diff main...HEAD -- aveto_service infra tests` (head `0caa3b1`, product tree = `5f86fd3`).
- **Read:** `intent.md`, `CHARTER.md`, `05-tech-spec.md`, `08-backend-note.md`, `code-review.md`, `13-qa-evidence.md`, `.agentic/SAFETY_INVARIANTS.md` (INV-4, INV-5); `aveto_service/{pipeline,judge_port,anthropic_judge,settings,limits}.py`; `infra/main.bicep`; the SDK's error mapping in `.venv/.../anthropic/_base_client.py` (1.7.0) and `.venv/.../httpx2/_client.py`.
- **Checks I ran** (scratch only, nothing committed but this file): an exhaustive run of every 2-attempt outcome sequence through the **real** adapter (12 outcomes x 12 = 144 sequences: success at the maximum usage the reservation allows, success small, success with no usage, `max_tokens` stop, `tool_use`, 429, 503, 529, 400, connection, timeout, a non-SDK exception) with the cap set to exactly one admission; a `SpendCounter` midnight-straddle demonstration; 71 targeted tests (retry, timeout, billing, price, logging, Bicep, concurrency, midnight, kill switch, hash): all passed. Script: `/private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/b964fb4e-04f7-4fbf-b787-36bfe8d105df/scratchpad/sec/seq_check.py`.

## Verdict: PASS

No blocker, no required fix. Six advisories (A1 to A6); A1 and A2 should be put in front of the owner in `END_REVIEW.md` because they are a choice about how cautiously the service counts money, not a defect in the code. Go to the Release Gate.

## 1. Can settled spend pass the day's cap or the monthly $10 share?

**After the change, the counter's settled spend cannot pass the day's cap through any adapter outcome, retry or concurrent admission within one UTC day.** The only way the counter goes over the cap is the midnight straddle (A3), which is older code (`limits.py` unchanged) and is no worse than before. The monthly $10 is not enforced by the service at all; it rests on the Anthropic console limit (decision D1), and this slice changes nothing there.

Why the daily bound holds:
- Admission reserves `MAX_ATTEMPTS * per_attempt` under the lock (`aveto_service/pipeline.py:254`); `reserve` admits only if `spent + in_flight + amount <= cap` (`aveto_service/limits.py:187`).
- Each attempt is charged at most one `per_attempt`: a billable failure is charged exactly that (`pipeline.py:274`, `:276`, `:284`), and a success's usage is bounded by it, since `max_tokens` is 1024 = `limits.MAX_TOKENS` and input is bounded by bytes + 64 framing tokens (`limits.py:166-170`; the "1 token >= 1 byte" assumption is pre-existing, see A5).
- The adapter sends at most `MAX_ATTEMPTS` (2) requests (`aveto_service/anthropic_judge.py:147`), and the pipeline's reservation and the adapter's loop now read the **same** constant (`aveto_service/judge_port.py:12`), so they cannot drift apart.
- So `charge <= reservation.amount` on every path, and `settle` releases the whole reservation (`limits.py:203`). **Checked:** across the 144 sequences, 0 settled above the cap, `in_flight` was 0 after every one, and no sequence sent more than two requests.
- Concurrency: reserve and settle both run under `self._lock` (`pipeline.py:249`, `:288`); one process, one worker, one replica (`Dockerfile:43`, `infra/main.bicep:223`). `test_concurrent_admissions_never_exceed_cap` now pins `in_flight == 3 * reserved`.
- Kill switch: checked first (`pipeline.py:218`), before any reservation or retrieval; unchanged.
- The floor (`pipeline.py:192`) is two empty-payload attempts, still a lower bound on any real admission, so `peek` never lets through what `reserve` would refuse on the floor's account.

**Before (87178bd):** a retried question reserved one attempt and settled `C + R`, so every 503-then-success could overshoot by up to `C`. The fail-first run reproduced it: `spent 22,466,000 > cap 13,124,000` (`03-failfirst-87178bd.txt`, T6.1). With several such questions in flight at once the overshoots added up. That path is closed.

## 2. 429 then success now charges usage only (spec §2 note, §10 R1)

**Ruling: acceptable, as an owner-visible choice (A1, A2), not a defect.** The counter's own bound (section 1) holds either way, because both attempts are reserved. The question is only whether the counter can read lower than Anthropic's bill.

- **429:** a rate-limited request is rejected before the model runs, so it plausibly bills nothing, and the service has charged 0 for a 429 on the failure path since the previous slice (429+429 and 429+400 were 0 before and are 0 now). Making the success path agree is consistent. **Unconfirmed:** that Anthropic does not bill a 429. Where I looked: this repo (`runs/public-ask-the-docs/08-backend-note.md` CR-2 and `code-review.md` CR-2 state "never billed" with no source; spec §2 and §10 R4 say the same), the SDK source (no billing information), and `runs/public-ask-the-docs/APPROVAL_RECORD-4.md` (pricing only). I had no network access to Anthropic's documentation.
- **The spec's table leaves out a second case the same rule changes: connection error, then success.** It was charged `C + R` and is now charged `C` (`anthropic_judge.py:145` does not count it; `tests/test_anthropic_judge.py` pins `(_conn(), message()) -> billable 0`). Unlike a 429, the `connection` category is not limited to "never sent". **Confirmed from the SDK source:** `_base_client.py:1289-1304` maps *any* non-timeout exception from `send()` to `APIConnectionError`, and `httpx2/_client.py:986-987` reads the response body inside `send()` when not streaming. So a connection that drops while the reply is being read (after Anthropic received, and possibly ran and billed, the request) is classed `connection`, retried, and now charged nothing. See A1.

## 3. CR-3: the day closes at about 33 questions instead of about 41. Any abuse or DoS effect?

**No regression against the live service; slightly better.** The figure to compare with is not 41 (that is the spend-only figure at the new price, which no revision ever ran) but what revision `ca-aveto-ask--0000006` does today: one reservation of about $0.045 at $3/$15 and about $0.0118 counted per question, so the day closes at about 23 questions (spec §1, same basis), or 27 by spend alone (the intent's figure). After: about 33 (an **estimate** from the spec; it assumes about 10 kB per request and was not measured). An attacker therefore needs more questions than before to pause the day, not fewer.
- Worst case, with questions chosen for long payloads and maximum output (charge close to `R` each): about 7 questions closed the day before, about 9 after (estimate, same basis).
- Near the cap, the number of questions in flight at once halves (about 5 instead of about 7). This gives only the transient "paused" (the day stays open, `limits.py:187-188`), lasts at most one call (two 20-second attempts and a 1-second backoff), and is limited by the 10-an-hour and 30-retrievals-an-hour per-visitor limits. The lasting effect is still the daily share being used up, which is decision D4 (fail closed, no spend).
- About $0.06 of the day's $0.3226 is always kept back as two attempts' room, so up to about 19% of the share goes unspent (estimate). That costs availability, not money, and buys the hard bound in section 1.
- The 5xx-outage case is unchanged: a 503+503 question was charged `2R` before and is now.
- D4 context: the runbook's D4 line (`docs/runbooks/public-ask.md:204-208`, already edited by the Tech Writer) now says "recorded as about 40; about 33 by the estimate". That is accurate and labelled as an estimate.

## 4. `billable_failures`, logging, INV-4 and INV-5, attempt count

- **Integer only.** Every value comes from an integer counter in the adapter (`anthropic_judge.py:125`, `:141`, `:146`, `:151`) or from the port's default, which works out to an integer (`judge_port.py:36-38`). The exception's `args` stay `(category,)` (`judge_port.py:33`), and `raise ... from None` is kept (`anthropic_judge.py:142`, `:152`). The test asserts `type(err.billable_failures) is int`, `err.args == (category,)`, and that no secret appears in `repr`/`str`. The count is never logged, returned or exposed in `/health`.
- **No new log line.** The added lines of the source and infra diff contain no `log`, `print`, `emit_`, `stderr` or `warn`. `tests/test_service_logging.py` (including `test_question_never_logged`) passes. The abuse line and the ops lines are unchanged, and no audit or abuse event was removed or renamed.
- **INV-4 and INV-5 are byte-identical:** `.agentic/SAFETY_INVARIANTS.md` blob `3d976e5fc6ce…` on `main` and on `HEAD`, and the working tree matches `main`. `git diff main...HEAD -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md` is empty. No invariant states a charging rule, so none became false (spec §9 agrees). C5.0 holds.
- **At most two attempts:** `MAX_ATTEMPTS = 2` (`judge_port.py:12`); the retry runs only while `attempts < MAX_ATTEMPTS` (`anthropic_judge.py:147`); the timeout still does not retry. `test_retry_once_only_on_retryable` and `test_no_retry_on_timeout` (both cited in INV-5) pass unedited, and the 144-sequence check never saw a third request. The request itself (model, tools, headers, host) is unchanged.
- **Adapter boundary:** `PlaceholderJudgeClient` still raises `JudgeNotConfiguredError` (`judge_port.py:52-55`), which settles at 0 and is not counted. No new client or model, and no new dependency.

## 5. Price override and secrets

- `ASK_PRICE_*` handling is unchanged (`aveto_service/settings.py:46-49`, `:71-77`). A value that is not an integer, or is 0 or below, raises; `from_env` then returns `kill_switch="on"` (fails closed). A very large price only makes the service pause earlier. A very small positive one would under-count, but only the operator can set it (a Bicep parameter, not something a visitor reaches). T8.1 pins the override path.
- The defaults are 2000/10000 in `settings.py:18-19` and `infra/main.bicep:33,36`, with the source and date in a comment. T8.2 checks that the two stay equal and that `infra/main.parameters.json` carries no price. The figure matches `runs/public-ask-the-docs/APPROVAL_RECORD-4.md` line 8 (read 2026-10-23). I could not check the live pricing page offline.
- **Secrets:** the added lines of the whole branch diff hold no key-shaped string (`sk-ant…`, JWT, AWS, private key). The only hits are prose about the Key Vault secret's *name* and commands that must never print values. The new tests use `"test-key"` and `"k"`; the existing canary test is untouched. The key is still a `secretRef` (`main.bicep` unchanged there). No `.env` or credential file was added.

## Findings

| id | severity | file:line | finding | disposition |
|---|---|---|---|---|
| A1 | advisory | `aveto_service/anthropic_judge.py:144-146`; `judge_port.py:13` | Connection error then success is now charged `C` (was `C + R`), and the spec's §2 table does not list this case. `connection` includes failures while the reply is being read, after the request reached Anthropic (SDK `_base_client.py:1298-1304`, `httpx2/_client.py:986-987`), so a billed first attempt can go uncounted: up to `R` (about $0.03, estimate) per occurrence. The same gap has existed on the failure path since the previous slice (conn+conn → 0; 503+conn → `R`). It needs a network fault between Azure and Anthropic and cannot be triggered by a visitor. The counter's cap bound (section 1) still holds; only real spend can sit up to that amount above the counter. | **Owner, at the end review.** Two possible follow-ups for a later slice: (a) classify by the SDK error's `__cause__` (an httpx connect-phase error means "never sent", so 0; a read-phase error means "may be billed", so `R`), which keeps the one rule and makes the category honest; or (b) the spec's §10 R1 alternative (`billable_failures = attempts - 1` on success), which brings back the old charge for both 429 and connection on the success path. The console limit remains the backstop (D1). |
| A2 | advisory | `aveto_service/judge_port.py:13` | That Anthropic does not bill a 429 (or a 4xx) is **unconfirmed** (where I looked: section 2). This slice extends the assumption to the success path. | Record as unconfirmed in `END_REVIEW.md`. Stage 10's `Δspend` against the token cost will show a billed retry only if one happens. |
| A3 | advisory (pre-existing, not worsened) | `aveto_service/limits.py:192-204` with `:156-164` | Midnight straddle: a question admitted on day D and settled after the counter has rolled to D+1 adds its charge to D+1's `spent` with no reservation on D+1. D+1's counter can then read above the cap by the straddlers' charges. Demonstrated: cap 10,000, one straddler and five D+1 questions at `2R` each gave `spent` 12,000. Real spend per admission day stays within the cap, because D reserved room for the straddler. At a month boundary, real billed spend can pass $10 by at most what was in flight at that midnight. The bound per straddler is now `<= 2R`. Before, any retried question could overshoot without a straddle. | Not in this slice's scope (`limits.py` is not one of its files). Candidate fix for later: make `settle` drop the charge from a reservation of another day, or roll the counter only when nothing is in flight. |
| A4 | advisory (pre-existing, D1) | `infra/main.bicep:222`; runbook §5 | Counters reset when the replica is replaced (scale to zero, kill-switch toggle, redeploy). This run's D1 and D2 deploys reset them twice on deploy day, so that day's real spend can reach several times the day's share. The monthly $10 rests on the console limit. | Already the owner's decision D1, documented in the runbook. No action in this slice. |
| A5 | advisory (pre-existing; CR-4) | `aveto_service/limits.py:166-170`, `:204`; `anthropic_judge.py:155-156` | `settle` adds the reported cost without a clamp. The input bound assumes each token covers at least 1 byte, plus 64 framing tokens (unconfirmed for Claude's tokenizer and for anything the effort setting adds on the server). `_count` also accepts a negative integer from the provider. Either would let the counter drift from the bill, though only through data from Anthropic's authenticated endpoint. | As CR-4: later slice, not blocking. |
| A6 | advisory | `aveto_service/pipeline.py:275-276` (CR-2) | A non-transport exception is charged one attempt though two were reserved. Not reachable with the real adapter: everything inside its loop is mapped to `JudgeTransportError`, and only `time.sleep` (a `BaseException` such as `KeyboardInterrupt`) could escape, which would leave the reservation held and fail closed. | Agree with CR-2; no action. |

No blocker. No required fix. Nothing is addressed to the Backend for this slice.

## Release-gate confirmations

- Safety invariants touched (INV-4 outcome mapping, INV-5 egress, attempts and logging): still hold; text byte-identical.
- No audit or abuse event removed or weakened; the meaning of the `/health` spend counter changed as specified (per attempt, at $2/$10).
- No placeholder adapter became a real client; no new model, processor or dependency.
- No secret, credential file or key-shaped literal added.
- Agentic threats (ASI): not applicable; no agent, tool or memory surface changed.

## Hand-off

To the Release Manager (stage 8): **GO** from Security. Carry A1 and A2 into `END_REVIEW.md` as owner decisions, and A3 to A5 as backlog candidates. Stage 10: a `Δspend` above the token cost shows a billed retry, but a connection-then-success retry (A1) will **not** show in `Δspend`, because it is now charged at usage only.
