# Production Verification - result-page-clarity (stage 10)

Role: Production Verification. Method: read-only, from the records. No shell, no browser, no live query by me. Every line below rests on the file named; anything I could not confirm says so and says where I looked.
Files read: `CHARTER.md`, `16-release-checklist-tier3.md`, `13-live/` (README, check-new.json, check-new-after-forward.json, log-abuse.txt, log-search.txt), `12-deploy/` (d1/d2/d3 start, end, result; after-1/2/3; whatif-1-ruling.md; rehearsal-polls.txt; forward-polls.txt; check-old.json; tested-tree-diff.txt), `STATE.md`.

## Verdict: HEALTHY WITH GAPS

No C8.1 failure condition is observed to have failed. The new revision (`ca-aveto-ask--0000014`, image `16f9bda31836`) is serving, `/health` and the nine live checks pass, the heading is far inside the top 25% where it was measured, the previous image served during the rehearsal, and the roll forward restored the new image. Four gaps are real, and one of them (R6) is an unmet item of the Release Manager's own gate, which I do not soften (section 3). One C8.1 condition (the kill switch taking) was never measured.

## 1. R1 to R7 (Release Manager, `16-release-checklist-tier3.md` section 6)

| # | Result | Evidence and limit |
|---|---|---|
| R1 new image active; `/health` 200, kill switch off | PASS | `after-1.txt`: revision `0000012` at 100, image `acravetoaskgp.azurecr.io/aveto-ask:16f9bda31836`, `ASK_KILL_SWITCH=off`. `check-new.json`: `health_200_kill_switch_off` true, `warm_ready_true` true, ok. Note: `after-1.txt` shows `0000012` running status as `None` at the moment it was read (the old `0000011` shows Healthy at 0); `check-new` at 06:46:47Z shows it serving. |
| R2 live heading in top 25%, 1280x800 and 375x667, answered and refused | PASS at 1280x800 (swap path, 16.1 / 16.1 px, bar 200). PASS at 375x667 on the page-load path only (17.6 / 15.6 px, bar 166.75). **375 px swap path on the live revision: NOT MEASURED.** | `13-live/README.md` table rows 9 and 10. Only the README records these figures; there is no raw capture file (no screenshot, no JS output saved) in `13-live/`. They are the Orchestrator's reading of the browser, not a file I can re-check. The 375 px swap figure (15.6 px) is the local one from `08-browser-checks.md` and must not be presented as live. Questions: 2 sent (`log-abuse.txt` shows exactly one `answer` and one `no_confident_match`, both from ip hash `0842751aaf72ca81` at 06:47:08Z and 06:47:20Z), which matches C3.1. |
| R3a answer / refusal not different from the previous page's | PASS on outcome class; comparison with the previous page NOT MEASURED | README: question 1 answered (10 passages), question 4 refused, "as labelled". `log-abuse.txt` agrees (`answer`, `no_confident_match`). The same two questions were never sent to the previous image and there was no byte comparison with local `retrieve` (README gap). `aveto_support/` and `prompts/` are unchanged (checklist section 4 item 4), so a difference is not expected, but it is expected, not measured. |
| R3b no question text in a log table | PASS on the abuse log; the search PASS is weak | `log-abuse.txt`: four rows, each exactly `{"t","ip":"<16 hex>","o":"answer"/"no_confident_match"/"bad_request"}`, no text. `log-search.txt` is **empty (0 bytes)**. The README says the search of all tables since 06:36Z for three question phrases "returned no rows". An empty file cannot tell "no rows" from "query failed or returned nothing". The query, the tables searched and the phrases are not saved. Log Analytics ingestion lag is also not addressed. UNCONFIRMED beyond the README's word; I looked in `13-live/` and `12-deploy/` for a query record and found none. |
| R3c kill switch takes | **NOT MEASURED** | README last line: not toggled. C8.1 names "a kill switch that does not take" as a live-check failure; C8.3 allowed the single `killSwitch=on` run only if C8.1 required one, which the Orchestrator read as not triggered. Only the off state is evidenced (`after-1/2/3.txt`). The earlier release's figure (about 65 s, cited by the runbook) is not this release's evidence. |
| R4 previous image serves after deploy 2 | PASS on image and script; the old DOM order was not observed | `after-2.txt`: revision `0000013` at 100 Healthy, image `...aveto-ask:ffc2e2e5f39a`. `rehearsal-polls.txt`: 06:53:19, :23, :27Z `health=200`, `home_status=200`, `js_has_preventScroll=0` (the previous script). The previous page's order ("What to expect" above the question box) was not fetched from a result page on `0000013`; identity rests on image tag plus the absent `preventScroll`. `check-old.json` (06:53:01Z) is `ok:false` (`root_has_no_skip_link` false, `scorecard_404` false): that is the wrong checker (it tests for the page before the last slice, whose page has the skip link and `/scorecard`), as the README says, and it is not a failure of the rehearsal. |
| R5 `/health` answers on the previous image | PASS | `rehearsal-polls.txt` three polls 200; `check-old.json` `health_200_kill_switch_off` true at 06:53:01Z. |
| R6 timed: command to healthy `/health` on the previous image | **NOT MEASURED** | Command at 06:48:03Z (`d2-start.txt`); deployment `Succeeded` 06:49:08Z (`d2-end.txt`, 65 s, which is the deployment's completion, not a `/health` poll); first `/health` 200 on the previous image in any file is `check-old.json` at 06:53:00-01Z, about 297 s after the command, with the polls at 06:53:19 about 316 s. Those are upper bounds from a loop that ran blind, not the time to first healthy. No figure may be stated as the rollback time. The deployment time (65 s) may be quoted only as "the deployment completed in 65 s". |
| R7 roll forward restores the new revision | PASS on image, health and checks; heading evidence is weak | `after-3.txt`: `0000014` at 100 Healthy, image `16f9bda31836`, env unchanged. `forward-polls.txt`: `new_js=1` first at t+67s (06:54:54Z), 80 polls, `health=200` throughout. `check-new-after-forward.json` ok, all nine true (06:55:31Z). Heading 16.1 / 15.6 px on an empty-question error page (native form post), not an answer or a refusal. |

Detail on R7: `health=200` at t+0 in `forward-polls.txt` is the previous revision still answering; only `new_js` marks the switch. The 67 s is therefore a good figure for the roll forward and is the one measured timing in the release.

## 2. C8.1 failure conditions

| Condition | Result | Evidence |
|---|---|---|
| Result heading outside the top 25% at either size | PASS (not observed) | R2. 16.1 / 16.1 px at 1280x800 swap; 17.6 / 15.6 px at 375x667 load path; error page 16.1 / 15.6 px after the roll forward. The one unmeasured cell is the 375 px swap path, live. |
| Answer or refusal different from the previous page's | PASS on outcome class; the comparison NOT MEASURED | R3a. |
| Question text in a log table | PASS, weakly | `log-abuse.txt` (clean rows); `log-search.txt` empty (R3b). |
| Kill switch that does not take | **NOT MEASURED** | R3c. |
| Rehearsal: the previous page does not serve | PASS | R4. |
| Rehearsal: `/health` does not answer | PASS | R5. |
| Rehearsal: roll forward does not restore the new revision | PASS | R7. |

No C8.1 condition is a FAIL. Two are NOT MEASURED (kill switch; comparison with the previous page) and two are weakly evidenced (log search; the old DOM order). I make no claim that a not-measured condition passed.

## 3. The Orchestrator's README gaps against C8.1, and contradictions

| Gap | A failure of the rehearsal under C8.1? | My ruling |
|---|---|---|
| Rollback time to a first healthy `/health` poll not measured | **No**, C8.1 lists three rehearsal failures (previous page does not serve; `/health` does not answer; roll forward does not restore) and timing is none of them. | But it is **not just a reported gap**. C8.3 says "the rollback timing for the release gate is measured from the command to a healthy `/health` on the previous image", and the Release Manager's R6 says the release "is not passed until every item below is recorded". R6 is therefore an unmet item of the release gate as the Release Manager wrote it, with no C8.1 failure attached. The Orchestrator's reason (the poll used the wrong checker) is a process error, and the Charter allowed no repeat of deploy 2. Whether an unmet R6 blocks the pull request is the owner's reading of C7.2 and C8.3, to be put in `END_REVIEW.md`. I would not call the release "passed" without that line. |
| Live 375 px figures are the page-load path, not the JS swap | No. The bar (heading within the top 25%) is met by what was measured; C8.1 fires on a measured miss, and there is none. | Reported gap. The live 375 px swap path is NOT MEASURED; `END_REVIEW.md` and the docs must say "load path" for the live 375 px figures. |
| Post-roll-forward heading used an error page | No. The roll-forward failure condition is "does not restore the new revision", which is shown by image, `new_js=1` and `check new`. | Reported gap. It shows the new script and CSS are live; it does not show an answer or refusal heading after the roll forward. Stored result tokens may be gone after a revision change (the result store is in memory; UNCONFIRMED, not checked), so a `GET /result/<token>` re-check may not have been possible without a third question, which C3.1 forbids. |
| Kill switch not toggled | It is a C8.1 live-check condition left unmeasured. | Reported gap, and the largest unmeasured safety control here. The code path is unchanged (checklist section 4 item 9), but the Charter put the check in the pass list. |
| No byte comparison with local `retrieve`; no cold-start or warm timing | No (not a Charter bar for this slice). | Reported. |

Contradictions and imprecisions found in the README and records:

1. README says the first recorded `/health` 200 on the previous image is 06:53:19. `check-old.json` records `health_200_kill_switch_off: true` at 06:53:00-01Z. Small, in the README's favour, and it changes nothing about R6 (still not a poll from the command).
2. README row 7 says "Succeeded in 66 s" for deployment 1 and `d1-start/end` agree (06:45:02 to 06:46:08Z). Rows for deployments 2 and 3 (65 s each) agree with the stamps. No arithmetic contradiction.
3. `12-deploy/tested-tree-diff.txt` does not show what `whatif-1-ruling.md` says it shows. The ruling says `git diff --stat d223e11 HEAD -- aveto_service tests infra Dockerfile pyproject.toml uv.lock` printed nothing. The saved file is a diffstat of run records only ("8 files changed", `STATE.md`, `charter-check-output.txt`), not an empty product diff. The "tested tree = candidate" claim therefore rests on the ruling's sentence and not on a saved output. UNCONFIRMED by file; I have no shell to re-run it. The release checklist asked for exactly this output to be saved.
4. The deploy commands for deployments 1, 2, 3 are not saved. `d*-start.txt` hold a timestamp, `d*-result.txt` the word "Succeeded". Only the what-if (deployment 1's parameters) is recorded verbatim. The resource group, `killSwitch=off` passed explicitly, and the unchanged price and cap for deployments 2 and 3 are shown only by the resulting environment in `after-2/3.txt`. UNCONFIRMED for the literal commands; I looked in `12-deploy/`, `13-live/` and `STATE.md`.
5. The what-if command includes `configureLogRetention=true`. C8.3 lists `deployApp`, `killSwitch` and `imageTag`/price/cap; the ruling reports no resource-level Create or Delete and "no env change", so I do not read it as a new resource, but the parameter is not named in the Charter line. Reported, not a failure.
6. `STATE.md` Approvals has the Charter row only; the checklist asked for one row per gated action (build, three deploys, live questions) citing `CHARTER.md#C8.3`. The Stages table has no row for 9 or 10 until this update. Process gap.
7. `log-search.txt` empty (R3b). Noted above.

## 4. Safety-invariant and C8.3 checks you asked for

| Check | Result | Evidence |
|---|---|---|
| Deployments used <= 3 | PASS: 3 (new, rehearsal, roll forward); no `killSwitch=on` run | `d1`, `d2`, `d3` start/end/result; revisions `0000012`, `0000013`, `0000014` in `after-1/2/3.txt`. Sequence is strictly in order with no overlap: 06:45:02-06:46:08, 06:48:03-06:49:08, 06:53:47-06:54:52Z. |
| All inside C8.3: resource group `rg-aveto-ask` | PASS for deployment 1 (what-if ran with `-g rg-aveto-ask`); UNCONFIRMED for 2 and 3 as literal commands | Gap 4 above. The revision names (`ca-aveto-ask--0000012` to `--0000014`, one app) are consistent with the one resource group, and the what-if shows no Create or Delete. |
| `killSwitch=off` explicit | PASS for deployment 1 (what-if line); deployments 2 and 3 UNCONFIRMED as commands, confirmed as outcome | `ASK_KILL_SWITCH off` in all of `after-1/2/3.txt`. |
| Price and cap unchanged | PASS | `ASK_PRICE_IN_NANO_PER_TOKEN 2000`, `ASK_PRICE_OUT_NANO_PER_TOKEN 10000`, `ASK_MONTHLY_CAP_USD 10` in all three. The pre-deploy values of `0000011` are not in these files; the "unchanged" rests on the what-if ruling ("no env change") and the README. |
| Env identical across revisions | PASS | `after-1.txt`, `after-2.txt`, `after-3.txt` are line-for-line identical in the env block: `ANTHROPIC_API_KEY` as secretref `anthropic-api-key` (no value shown), `ASK_KILL_SWITCH=off`, `ASK_CLIENT_KEY=xff_last`, the two prices, the cap. |
| No question text in logs | PASS (abuse log), weak (search) | R3b. |
| Image tags | PASS | New `16f9bda31836` in `after-1.txt` and `after-3.txt`; `git log` HEAD of the deploy commit is `16f9bda`; previous `ffc2e2e5f39a` in `after-2.txt`, equal to Charter C6.5. The build log `acr-build.log` was not re-read by me for the tag. |
| Active revision now | `ca-aveto-ask--0000014` at 100, Healthy, image `16f9bda31836` | `after-3.txt`. |
| INV-1 to INV-5 | No live evidence beyond the unchanged code and the passing checks | The two live questions came out answered and refused as labelled and a refusal printed "The docs don't answer this". `check-new` headers equal the literal set (including the root and `/scorecard`). Refusal behaviour under adversarial live input was not tested (and not asked for). |

## 5. What this stage cannot say

- Anything not in `13-live/README.md` or the files above. In particular I cannot confirm the raw browser measurements: only the README states them.
- The live cold-start behaviour, the kill switch toggle, and the old-versus-new answer comparison.
- Whether the 7-day log read-back (runbook s6) will show question text; that is for the SRE / owner after the window.

## 6. Verification window

The window is one session of about 12 minutes of live evidence (06:45Z to 06:57Z) across three revisions, which suits a stateless presentation change with no data, schema or model path touched. It is not a long soak and I do not claim one. The checklist's later re-checks (first live day, first week; Signal 1 and Signal 4) stay with the owner.

## 7. Handoff

Verified, with the gaps above: hand off to the SRE / owner for ongoing ownership, and to the Orchestrator for `END_REVIEW.md`, which must list (a) R6 not measured, (b) the kill switch not measured, (c) the live 375 px figures are the load path, (d) the roll-forward heading is an error page, (e) the empty `log-search.txt` and the missing query, (f) the unsaved product diff and deploy commands, (g) no stage 9/10 Approvals rows. Do not state a rollback time anywhere (README, runbook, `CURRENT_MVP_STATUS.md`): the only measured timings are the three deployment durations and the 67 s roll forward.
