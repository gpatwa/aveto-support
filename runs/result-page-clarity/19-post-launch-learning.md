# Post-Launch Review - result-page-clarity

> Owner: Post-Launch Learning Agent (stage 11), 2026-10-27
> Tier: 3
> Released at: live revision `ca-aveto-ask--0000014`, image `aveto-ask:16f9bda31836` (deploy commit `16f9bda`). The pull request is not opened and nothing is merged.
> Source PRD: `runs/result-page-clarity/intent.md` (Charter `CHARTER.md`, C1.4 bars)
> Method: read-only, from the run records. I have no shell, no browser and no live query. The window is about 12 minutes of live evidence (06:45Z to 06:57Z), not a soak. Anything not in a file below is marked unconfirmed.

## Success criteria - did we hit them?

| Criterion (intent "Done means" / "What I want") | Met? | Evidence |
|---|---|---|
| Result heading in the top 25% after Ask, desktop and 375 px, keeping keyboard focus | yes locally; yes live at 1280x800; partial live at 375 px | Local: 16.1 / 16.1 px at 1280x800 and 15.6 / 15.6 px at 375x667, focus on `#result` (`08-browser-checks.md`). Live 1280x800 swap: 16.1 / 16.1 px (`13-live/README.md` row 9). Live 375 px was the page-load path only (17.6 / 15.6 px); the live 375 px swap path is NOT MEASURED (`18-production-verification.md` R2). No raw capture file exists for the live figures; only the README states them. |
| On a result page the result comes first; home page unchanged | yes | `08-browser-checks.md` DOM order; `13-qa-evidence.md` section 3: `GET /`, resting, service off and unknown token byte-equal to main; 8 result states reordered with 0 strings added or removed. Live DOM order recorded in README row 9. |
| No wording changes | yes | `13-qa-evidence.md` section 3 (multiset of whole HTML lines identical for all 8 result states); `code-review.md`. |
| Nothing about answering moves (`aveto_support prompts .claude .agentic` diff empty, 39-case golden byte-equal, headers identical, INV-1 to INV-5) | yes | `13-qa-evidence.md` section 2 (empty diff, golden sha256 equal, 16-state header comparison). Live: `check-new.json` headers equal the literal set. Live answer/refusal comparison with the previous page: NOT MEASURED (R3a). |
| Tests that fail first | yes, with a stated limit | 6 of 7 failed on main, T4 is a pin (`13-qa-evidence.md` section 4; `06-failfirst-6ab5548.txt`); 12 mutations, 2 equivalent survivors. T5-T7 are text checks on the script, not behaviour (QA P3-1). |
| Accessibility: axe zero serious/critical, keyboard-only flow, reading order | partial | axe 0 on 5 views, keyboard flow ok (`08-browser-checks.md`). Not tested: screen reader, receipts drawer, copy-link, dark scheme, no-JS flow. |
| Code review layer; Security smoke; Release Gate tier 3 with rollback rehearsal as a gate | partial | Code review 0 Important, 2 Nits; Security PASS with 3 P3; gate GO TO DEPLOY. Rehearsal: previous image served, `/health` 200, roll forward restored the new image (R4, R5, R7 PASS). R6 (timed to first healthy `/health`) NOT MEASURED, which is an unmet item of the Release Manager's own gate (`18-production-verification.md` section 3). Whether that blocks the pull request is the owner's call. |
| Live checks (C8.1): no question text in logs; kill switch takes | partial / no | Abuse log rows clean (`13-live/log-abuse.txt`). `log-search.txt` is 0 bytes and the query is not saved, so the "no rows" claim is unconfirmed. Kill switch never toggled: NOT MEASURED. |
| README, runbook, `CURRENT_MVP_STATUS.md` state only recorded figures | yes on the face of `15-docs-note.md`; not re-verified by me | `15-docs-note.md`. Security P3-3: the README change was not reviewed by Security; confirm at landing. |
| `STATE.md` set to done when the pull request opens | not yet | `STATE.md` Status is in-progress. |

Overall: the slice met its goal (the result is the first thing seen, measured on the live app at the size where it was measured). It is HEALTHY WITH GAPS, not clean.

## What worked

- Taking before figures first (`00-setup-dryruns.md`) paid off at once: it found the real defect was larger than the intent's 616 px, and the Architect designed against it.
- The static-text tests plus a whole-page comparison against a `git archive main` copy gave strong "only moved, nothing reworded" evidence (`13-qa-evidence.md` sections 2 and 3, mutations M1-M12).
- Keeping the change to one keyword and one script function (`result_first`, `land()`) kept the safety review at smoke depth honest: the diff to `app.py`, headers and `aveto_support/` was empty.
- The roll forward was polled correctly and gave one good timing: 67 s (`12-deploy/forward-polls.txt`).
- Three deployments stayed inside the C8.3 limit, with the env identical across `after-1/2/3.txt`.
- No C8.1 failure condition was observed.

## Surprises

| Surprise | Signal cited | Severity |
|---|---|---|
| `focus()` on a region taller than the viewport scrolls to its far end, so a long answer lands with its heading far above the screen. The real defect was bigger than the intent's 616 px (answer heading at -2,820.9 px at 1280x800 and -4,182.9 px at 375x667; the refusal at 375 px was -2.9 px). | `00-setup-dryruns.md` before table; tech spec "Grounded on the setup finding" | high (it shaped the whole design) |
| The stand-in judge shows long answers (6,463 px region), so local figures are not the live shape: the live answer was 10 passages and 616 px in the intent. Before figures are therefore not comparable to the intent's 616 px. | `08-browser-checks.md` line 13; `00-setup-dryruns.md` | medium |
| The Charter's C3.3 listed sonnet for the Architect and Security though their agent files default to opus. The Architect ran on `opus-5-5`, outside C3. | `STATE.md` Notes ("Charter miss"); checklist M1 | medium (cost and a Charter miss, no safety effect) |
| Release Manager peaked at 139k tokens against a 40k estimate. | `STATE.md` Notes ("139k peak, over its 40k estimate") | medium |
| The `live.py check old` script tested the wrong baseline (the page before the last slice: no skip link, `/scorecard` 404), so the rehearsal poll loop ran blind and the rollback time was never polled. First `/health` 200 on the previous image is about 297 s after the command (an upper bound, not the rollback time). | `12-deploy/check-old.json` (`ok:false`), `rehearsal-polls.txt`, `13-live/README.md` gaps | high (an unmet gate item, and the Charter allowed no repeat of deploy 2) |
| The log-search evidence is an empty file with no query, no tables, no phrases, no control query. An empty file cannot tell "no rows" from "query failed". | `13-live/log-search.txt` (0 bytes); `18-production-verification.md` R3b | medium |
| Peak-context spend ran over plan: 463k spent against the 400k plan (116%), 58% of the 800k hard cap. No notice was due (ceiling 720k). | `STATE.md` Budget and Notes | low |
| `tested-tree-diff.txt` does not hold what the ruling says it holds (it is a run-records diffstat, not an empty product diff); the deploy commands were not saved in `d*-start.txt`; stage 9/10 Approvals rows were not written. | `18-production-verification.md` section 3 items 3, 4, 6 | medium (evidence hygiene) |

## What we'd do differently

- Poll the rollback with a checker whose baseline is the image you are rolling back to (a bare `/health` loop, or a `check` that names the target tag), and start it before the deploy command returns. The one thing timed blind here was the one thing the Release Manager's R6 required.
- Save the exact deploy commands, the query behind each log search and a control query (a phrase known to be present, to prove the search works) at the time they are run, not afterwards.
- Run the live checks that C8.1 names (kill switch) in the pass list only if the allowed deploy budget includes them; here the Charter put the kill switch in the pass list but C8.3 allowed one `killSwitch=on` run "only if C8.1 requires one", and the Orchestrator read it as not triggered. Resolve that in the Charter, not on the day.
- Measure at the size that matters on the live path used by visitors: the swap at 375 px was spent on the 2-question allowance at 1280x800. Plan which of the two live questions goes to which viewport, or allow a third.
- Save a raw capture (JS output or screenshot) for each live measurement; today the live heading figures exist only as README text.
- Check the Charter's model list against the agent files at drafting time (C3.3 vs `.claude/agents/`).

## Carry-forward to next PRD (this product)

1. Measure the live 375 px swap path and one live answered and one refused heading after a roll forward (not an error page). Evidence: `18-production-verification.md` R2, R7.
2. Time a rollback from the command to the first healthy `/health` on the previous image, and the kill switch switch-on and switch-off, in a session that allows the deploys. Evidence: R6, R3c.
3. Re-run the log search with the query saved and a control phrase, after Log Analytics ingestion lag; add the 7-day read-back (runbook s6, Signal 4). Evidence: `13-live/log-search.txt` empty.
4. Compare live passages byte-for-byte with local `retrieve` for the two questions (README gap). Evidence: `13-live/README.md` row 11.
5. Check the first-day and first-week heading position (Signal 1 in `16-release-checklist-tier3.md`), owner-run.
6. Unmeasured: the no-JS path (heading offset after fragment jump; tech spec open item 5), a short error box at 1280x800, reduced-motion emulation, a screen reader, the receipts drawer and copy-link by keyboard, dark scheme. Evidence: `08-browser-checks.md` "Not measured", `13-qa-evidence.md` section 6.
7. Two Nits to revisit if the template changes: `resultFirst` selects blocks by `nextElementSibling` twice from the `h1` (R1-1); load-time `land()` overrides scroll restore on reload (R1-2). Evidence: `code-review.md`.
8. Replace T5-T7 text checks with a behavioural JS check if the suite ever gains a JS runtime (QA P3-1; adding one is a new dependency, so it needs its own decision).
9. Retake the aveto.dev screenshots after the deploy (a separate playbook commit with wording the owner approves). Evidence: intent "Done means".
10. Do not state a rollback time in README, runbook or `CURRENT_MVP_STATUS.md`. The only measured timings are the three deployment durations (66 s, 65 s, 65 s) and the 67 s roll forward.

## Suggestions for the playbook (not edited by me)

| Suggestion | Evidence file |
|---|---|
| Rollback-rehearsal checker: ship a poll helper that takes the target image tag, so `check old` cannot silently test the wrong baseline; fail loud when a poll loop sees zero passes. | `12-deploy/check-old.json`, `13-live/README.md` gaps |
| Evidence rule: a search or query result is only accepted with the query text, the scope and a control query; an empty output file is "unconfirmed", never "no rows". | `13-live/log-search.txt`, `18-production-verification.md` R3b |
| Charter drafting check: compare C3 model lines with the `model:` of each agent file in `.claude/agents/` and flag disagreements before approval. | `STATE.md` Notes (Charter miss) |
| Release Manager estimate: 40k was exceeded 3.5x (139k peak). Revisit the tier 3 stage estimate or set an explicit read budget for the checklist. | `STATE.md` Notes |
| Slice-level plan for tier 3 UI deploys: the 400k plan was passed (463k). Consider a tier 3 deploy-slice default above 400k, or count the deploy stage separately. | `STATE.md` Budget |
| Setup-phase "before" figures should be taken on a real-shaped judge answer or the stand-in's length stated up front, so before and after are comparable to the intent's figure. | `00-setup-dryruns.md`, `08-browser-checks.md` line 13 |
| Gate wording: when a Charter pass list names a live check (kill switch) and the deploy allowance only permits it "if required", the Charter should say which reading applies. | `CHARTER.md` C8.1 and C8.3; `18-production-verification.md` section 3 |
| Stage 9/10 should write one Approvals row per gated action as the Release checklist asked. | `18-production-verification.md` section 3 item 6 |
| Save deploy commands to the record at run time (`12-deploy/commands.txt` appears as untracked in git status; confirm it holds the three commands). | `18-production-verification.md` section 3 item 4 |

## Follow-up slices to file

- [ ] Live verification top-up for result-page-clarity: 375 px swap heading on the live revision, kill switch on/off timing, rollback time to first healthy `/health` with a correct checker, and a saved log query with a control (needs an approved deploy allowance).
- [ ] Accessibility pass on the result-first page: screen reader, no-JS flow, reduced motion, drawer and copy-link by keyboard.
- [ ] Rollback-rehearsal tooling (playbook/support session): target-tag poll helper and the evidence rule for empty search output.

## Pipeline analytics

I could not complete the close-out refresh. I have no shell, so I could not run `node <playbook>/execution/analyze.mjs .`. My Glob of `runs/result-page-clarity/` shows no `trace.json`, only the Trace table in `STATE.md` (stages 1 and 2 only, 148k of 463k), so the machine-readable trace is unconfirmed missing or incomplete. Action for the Orchestrator: complete `trace.json` per `SLICE_STATE.md`, then regenerate `runs/ANALYTICS.md` and `runs/dashboard.html`. Stages to treat as carry-forward on density and cap once the generator runs: Release Manager (139k vs 40k est.) and Software Architect (79k vs 40k est.). I have not confirmed whether the generator flags them.

## Lessons

| Lesson | Evidence | Cost | Enforce where |
|---|---|---|---|
| A timing gate needs a poll that can pass on the target; a poll against the wrong baseline measures nothing. | `12-deploy/check-old.json` ok:false; `rehearsal-polls.txt`; R6 NOT MEASURED | An unmet release-gate item; no repeat allowed (3 deployments used) | Pack defect candidate: rollback checker should take the target tag (playbook live-check script); for support session |
| An empty evidence file is not evidence. Save query, scope and a control. | `13-live/log-search.txt` 0 bytes | A C8.1 condition passes only weakly | Pack defect candidate: evidence rule in the production-verification brief; for support session |
| Cross-check Charter model lines against agent files before approval. | `STATE.md` Notes; Architect ran on opus-5-5 | A Charter miss; Architect 79k vs 40k est. | Pack defect candidate: Charter checker; for support session |
| Measure the true failure before designing the fix: the before figures showed the defect was bigger than the intent said. | `00-setup-dryruns.md` before table | Saved a wrong design (a plain `focus()` plus scroll would not have worked on long answers) | Already in the project pack's setup phase; nowhere new needed |
| A tier 3 slice with a deploy and a rollback gate runs over a 400k plan. | `STATE.md`: 463k vs 400k; Release Manager 139k vs 40k | 63k over plan, within ceiling | Pack suggestion: tier 3 deploy-slice estimates; for support session |
| Run-time capture beats after-the-fact claims: commands, diffs, raw browser output. | `tested-tree-diff.txt` mismatch; unsaved commands; no raw live captures | Four "unconfirmed by file" lines in stage 10 | Release checklist template item "save the output" already asks for it; enforcement nowhere yet |

## Hand off

Next agent: Orchestrator. Surface to the human now: R6 not measured (whether it blocks the pull request is the owner's reading of C7.2 and C8.3), the kill switch not measured, the live 375 px figure is the load path, the empty `log-search.txt`, the Charter model miss, the budget overrun, and the missing `trace.json`. The rest can fold into the next slice's PRD. No product code was edited by this stage.
