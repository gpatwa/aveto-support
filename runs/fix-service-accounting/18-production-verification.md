# Production Verification: fix-service-accounting

> Role: Production Verification, standard depth, 2026-10-24. No shell: every result is read from a saved file in `09-deploy/` or `10-smoke/`; nothing was re-run or queried live by me. Basis: checklist `16-release-checklist-tier3.md` post-deploy checks 1 to 10, spec `05-tech-spec.md` 7.2 to 8.5.

## Verdict: HEALTHY WITH WATCH ITEMS

C8.1 rollback is **not required**. No spec 8.5 behaviour-failure trigger fired. Revision `ca-aveto-ask--0000008` is at 100%, Healthy, kill switch off, image `aveto-ask:d067b9a95ac6`, and it answered the five smoke questions as specified at the corrected price. The watch items below are gaps in what was measured, none of them a failed signal.

## Window

Smoke ran 06:49:04Z to 06:49:17Z, about 40 s after D2 reached `off` (06:48:41Z), inside one replica lifetime (`window_valid: true`, same `day`, counters rose from 0). The log search ran 06:55:30Z, 6 min 13 s after the last request (spec asks at least 5 min). That is a short window, but it is what the spec fixed in advance. I judge it enough for this change: the change is in-memory accounting, so the signal is the counter delta and the log shape, and both were read. It says nothing about behaviour over a day (see W3).

## Post-deploy checks (checklist 1 to 10)

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | After D1: one new revision at 100% Healthy, image and env as predicted | MET | `7.2-verify.txt`: `...0007 100 Healthy`, image `d067b9a95ac6` (preflight HEAD, `7.0-preflight.txt`), 2000/10000, switch `on`, `xff_last`, cap 10, key `secretRef` with null value. `...0006` still listed active at weight 0 |
| 2 | After D1: `/health` `kill_switch on`, empty `POST /ask` gives 503 `service_off`; seconds recorded | MET for state, NOT MEASURED for seconds | `watch-on-recheck.stdout`: 503 `service_off` confirmed, reached in 0.6 s (but only a recheck, long after the toggle). First watcher `watch-on.stdout` failed all 213 polls (local TLS error, no wanted state seen); `watch-on-attempt1-tls-failed.json` kept. Upper bound only: `7.2-create-start.txt` 06:35:57Z to `7.2-create.txt` end 06:37:06Z, about 69 s (about 73 s from the watcher start 06:35:53Z) |
| 3 | After D2: new revision `...0008` at 100% Healthy, env as D1 with `off`, three consecutive `off` reads | MET | `7.3-verify.txt` (`...0008 100 Healthy`, switch `off`, other env unchanged); `watch-off.json` `ok: true`, 27 polls, reached |
| 4 | g01, g03, g04 `answer`; gu15, gu18 `no_confident_match`; all HTTP 200 | MET | `smoke-result.json` questions[0..4]: all 200, outcomes as expected |
| 5 | Every `answer` byte-equal to local `retrieve` | MET | `smoke-result.json`: `byte_equal: true` for g01, g03, g04; `index_sha256 f36ef5d4...a756` equals the build ingest line (`7.1-build.log` line 131) |
| 6 | `Δjudged = 5` in a valid window | MET | `figures.delta_judged 5`, `window_valid true`; health before all zero, same `day` 2026-10-24 |
| 7 | Cost per judged question inside $0.00663 to $0.00897 | MET | `cost_per_judged_question_usd 0.008544` (20,304 in, 211 out; 42,718,000 nano / 5). Within 15% of $0.0078 but 9.5% above it, near the band's top edge (see W2) |
| 8 | Live #8 check: `Δspend` within 2,000 nano of token cost at $2/$10 | MET | `spend_minus_token_cost_nano: 0`, `issue_8_check: pass`. Zero gap also shows no billed retry occurred in the window |
| 9 | No question text in any log table | MET | `log-search.txt`: Q1 returns only the six abuse-shape lines (`t`, `ip`, `o`), including all five smoke outcomes, so the zero in Q2 and Q3 is meaningful; Q2 (phrases) and Q3 (words) return no rows |
| 10 | gu15 / gu18 not answered with passages | MET | both `no_confident_match` |
| 11 | Kill-switch timing recorded; each state within 600 s | D2 MET with measurement, D1 NOT MEASURED | D2: 71.4 s watcher-start to `off` (`watch-off.json`; create took 41.1 s). D1: only the 69 to 73 s upper bound above, which is not a watcher measure. Both states were reached and `service_off` confirmed, so the pass condition (state reached, `service_off` answered) holds; the number does not |
| 12 | Saved outputs searched for secrets before commit | MET for key-shaped strings, UNCONFIRMED for subscription id masking | I grepped `09-deploy` and `10-smoke` (.txt, .json, .stdout, .md) for `sk-ant` and strings of 40 or more alphanumerics: only the public index sha256. Not searched: `.log` files, and I did not search for a subscription GUID. Preflight prints the subscription name, not its id |

Spec 8.5 behaviour-failure list, restated: all five 200 and in the expected set (yes); byte-equal (yes); question words in logs (no); kill switch took (yes); `Δjudged = 5` (yes). Canary rule (gu15/gu18 with passages): not triggered. Items "reported as measured" (cost band, retry in `Δspend`, index hash mismatch): none outside tolerance.

## Watch items (carry to SRE and `END_REVIEW.md`)

- **W1: D1 toggle time not measured.** First `watch on` failed on a local TLS verification error (python.org Python; fixed with `SSL_CERT_FILE=/etc/ssl/cert.pem`, `LOCAL_COMMANDS.md`). Report D1 as "about 69 to 73 s upper bound from deploy timestamps, not watcher-measured", not as a measured toggle. The recheck proves the end state only. The run's own tooling gap (the watcher needs that env var on this machine) is for the support session; I changed nothing.
- **W2: cost 9.5% above the $0.0078 reference.** Inside the stated band, and the counter matches the token cost exactly, so the counter is right. The difference is the sample (five questions, 4,061 input tokens each on average). Five questions are a small sample; keep this against the day-limit estimate (about 33 a day) which the docs label an estimate. At $0.008544 per question a day pauses near 37 judged questions on the per-question cost alone, so the 33 figure (two-attempt reservation) remains the binding one.
- **W3: rollback R1 is untested and now degraded.** `ca-aveto-ask--0000006` is no longer listed active after D2 (`7.3-verify.txt` shows only 0007 and 0008). `az containerapp revision activate` on an inactive revision under single-revision mode has never been run on this app, so R1 is both unrehearsed (checklist R-1) and unproven for an inactive target. R2 (kill switch on via D1's command) remains the proven fallback and does not depend on revision 0006. No rollback was needed, so nothing was exercised; this item matters for the next incident.
- **W4: short observation window and in-memory counters.** Verified over about 6 minutes at 5 requests. Counters reset on each revision (decision D1, out of scope): the two deploys reset them twice, and the smoke's 0.042718 USD is the only spend the counter has seen today. Continued assurance of the day cap under real traffic belongs to SRE. Anthropic console remains the backstop.
- **W5: first smoke `ask` failed on an import before any network call** (needed `PYTHONPATH=.`), then ran once. Checked against `smoke-result.json`: one start at 06:49:04Z, `delta_judged` 5, so the questions were sent once, not twice. The tool-invocation gap is for the support session.
- **W6: unconfirmed by me** (looked: `09-deploy`, `10-smoke` saved files only): the what-if ruling is the Orchestrator's own read (`7.2-whatif-ruling.md`); I did not re-read `7.2-whatif.json` or `7.3-whatif.json`. I did not read `watch-on-attempt1-tls-failed.json` beyond its stdout counterpart.

## Handoff

Verified healthy with the watch items above, so the slice goes to SRE for ongoing ownership and on to stage 11 (docs lines still saying "not deployed yet" must be updated to the recorded figures above before the pull request). No rollback executed, so no On-Call handoff and no new Intake slice from this stage. The two tooling gaps (W1, W5) go to `SUPPORT_REQUESTS.md` at the Orchestrator's discretion.
