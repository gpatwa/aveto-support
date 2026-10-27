# End review — result-page-clarity

> Orchestrator, 2026-10-27. Charter `runs/result-page-clarity/CHARTER.md`, sha256 `8eacc407803700bece84af1a3344f02b871b02da10fe10a3ec620099cbd099bc`, approved by Gopal Patwa 2026-10-27T06:13Z (`APPROVAL_RECORD-1.md`). The pull request is the owner's to review (Codex review) and merge; nothing was merged.

## What was asked and what happened
On a result page the result now comes first: title and statement, question box, result, then "What to expect" and the suggestions. The home page is unchanged. After Ask the page focuses the result without letting the browser scroll and jumps to the heading, without animation. The live revision `ca-aveto-ask--0000014` (image `aveto-ask:16f9bda31836`) serves it.

## The measured result (Charter C1.4 item 1: top of the heading, 0 ≤ top ≤ 25% of the viewport)
| Viewport / question | Before (main, local) | After, local | After, live |
|---|---|---|---|
| 1280×800 answered | −2,820.9 px (off screen) | 16.1 px (2.0%) | 16.1 px |
| 1280×800 refused | 292.1 px (36.5%) | 16.1 px | 16.1 px |
| 375×667 answered | −4,182.9 px (off screen) | 15.6 px (2.3%) | 17.6 px (page-load path) |
| 375×667 refused | −2.9 px (cut off) | 15.6 px | 15.6 px (page-load path) |
The intent's 616 px of 800 was for a short real answer on the live revision; the stand-in judge's answer is long, which is why the local before figure is worse. A finding of the run: `focus()` on a region taller than the viewport scrolls to its far end, so a long answer landed with its heading far above the screen. Records: `00-setup-dryruns.md`, `08-browser-checks.md`, `13-live/README.md`.

## Charter bars (C1.4) and gates
| Bar | Result | Record |
|---|---|---|
| 1 heading position | PASS locally and live (2 live questions, C3.1). Live 375 px is the page-load path; the swap path at 375 px is local only | above |
| 2 home unchanged; order on a result page | PASS (home, resting, service-off, unknown-token and scorecard pages byte-equal to main; order tests) | `13-qa-evidence.md` |
| 3 strings | PASS, none added, removed or reworded | `13-qa-evidence.md` |
| 4 nothing about answering moves | PASS: diff of `aveto_support prompts .claude .agentic` safety files empty; 39-case golden file byte-equal; headers equal in 16 page states | `13-qa-evidence.md` |
| 5 focus | PASS (test, local and live) | `08-browser-checks.md` |
| 6 accessibility | PASS locally: axe 4.10.2, zero violations on home, answer, refusal, resting; keyboard flow ok. Not tested: screen reader, dark scheme, no-JavaScript | `08-browser-checks.md` |
| 7 no open P0/P1 | PASS: code review 0 Important, 2 Nits; QA no P0–P2; Security smoke PASS | `code-review.md`, `13-qa-evidence.md`, `14-security-review.md` |
| 8 tests | 738 passed, 0 failed; mypy and ruff clean; 6 of 7 new tests fail on main first (see "Honest notes") | `06-test-count.txt`, `06-failfirst-6ab5548.txt` |
| 9 INV-1..5, limits, cap | unchanged | `14-security-review.md` |
| Release Gate tier 3 | GO TO DEPLOY | `16-release-checklist-tier3.md` |
| Production verification | HEALTHY WITH GAPS | `18-production-verification.md` |

## OPEN items for the owner (a ruling is needed; nothing was softened)
1. **Rollback rehearsal timing not measured (Release Manager R6).** The rehearsal itself passed every C8.1 condition: deployment 2 (previous image `ffc2e2e5f39a`) Succeeded in 65 s, revision `0000013` at 100% Healthy, `/health` 200 and the previous page's script served at 06:53:19–06:53:27; deployment 3 restored the new revision (first healthy poll with the new script 67 s after the command). But my poll loop after deployment 2 used `live.py check old`, which tests for the page before the last slice and could not pass on the previous image, so no time from the rollback command to the first healthy `/health` was recorded. The only bound is the deployment's own 65 s completion, and the first recorded healthy poll is about 297 s after the command (upper bound only). The Charter allowed three deployments and the rehearsal was not repeated. The Release Manager's gate says the rehearsal's timing must be recorded; Production Verification rates this an unmet gate item, not a C8.1 failure (C8.1 names no timing condition). No rollback time is stated anywhere in the docs.
2. **Kill switch not toggled** live (C8.3 allows a toggle only if C8.1 requires one); a named C8.1 live-check condition, therefore NOT MEASURED.
3. **No live byte comparison** of the passages with local `retrieve` (`live.py ask` sends 7 questions; C3.1 allowed 2). The two live questions came back as labelled (answered with 10 passages; refused).

## Charter misses and notes
- **Model (C3.3):** the Software Architect ran on `claude-opus-5-5`, not the `claude-sonnet-5-5` the Charter lists. The Charter text was my error (the role's agent file defaults to opus); I noticed after the spawn and passed a `sonnet` override to every later spawn. The Security & Privacy role ran on `sonnet-5-5`, as C3.3 says. `usage.mjs` is the source.
- **Spend:** peak context summed per spawn is 581k at the last measurement (hard cap 800k, ceiling 720k), against a 400k plan. No budget notice was due: the projection never passed the 720k ceiling, and spent never passed 720k. Per stage against its estimate: Architect 79k vs 40k; Frontend 69k vs 50k; QA 73k vs 40k; Security 54k vs 25k; Tech Writer 47k vs 25k; Release Manager 139k vs 40k; Production Verification 58k vs 45k; Post-Launch 60k vs 30k. The Orchestrator's own stages (review, browser checks, deploy, live) are not in the sum. Cloud Deployment was not spawned (no shell; the Orchestrator ran the deploy sheet, as in the last slice).
- **Tests that pin "unchanged" cannot fail first:** T4, the home byte-equality part of T2 and the string-multiset part of T3 pass on main by design; C1.4 item 8 as literally worded ("each fails on main first") is met for the order and script tests (6 of 7) only. QA's mutation check: 11 of 12 mutations caught; two survivors are behaviourally equivalent.
- **`configureLogRetention=true`** was part of each Bicep deployment (the runbook's final form; the what-if showed no retention change). C8.3 does not name it.
- **Code review** was `unscored` (no rescore since 2026-10-17). Tier Medium. Two Nits accepted: `enhance.js:67` (sibling-position coupling) and `enhance.js:232` (jump on reload at `#result`).
- **C1.7 baseline fixes** done as approved: the one pinned hook hash in `tests/test_service_pipeline.py` (hook untouched) and the import order of `runs/polished-chat-experience/13-live/tls-wrapper.py`.
- `log-search.txt` first run was empty and the query was not saved; re-run with the query and a control query that returns rows (10 rows); the search for the question phrases returned none. Deploy commands: `12-deploy/commands.txt`.

## Questions asked of the human after the Charter
**0 that I know of.** I answered no budget-guard prompt and had none shown to me. The app may have shown the owner a permission prompt that never reaches me; the owner should correct this count if any appeared. The event log shows 4 failed calls and one call per check with no outcome recorded (the verifier's own call) in the Orchestrator's calls, none a prompt I saw.

## Event log
`events-verify-output.txt`: chain intact, 387 lines, head `4b025df05af28d8d` at the time it was saved (before the release stage); the later log is longer. No write outside the Charter's paths was reported. `EVENTS.jsonl` is the copy saved at that time.

## Nothing else moved
No change under `aveto_support/`, `prompts/`, `.claude/`, or `.agentic/` except `CURRENT_MVP_STATUS.md`. No new route, input, header, dependency or processor. aveto.dev screenshots are retaken in a separate playbook commit with wording the owner approves.

## Owner ruling on the open items (typed in the driving session, 2026-10-27)
Gopal Patwa: "Accept the unmeasured rollback timing as a recorded gap; I will run the Codex review and merge." Open item 1 (rollback command-to-healthy time) is accepted as a recorded gap; it is not measured and no rollback time is to be stated anywhere. The ruling does not cover open items 2 and 3 (kill switch, live byte comparison), which stay recorded as not measured. The pull request is the owner's to review and merge.
