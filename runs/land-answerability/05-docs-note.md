# 05 Docs note (Tech Writer, standard) — land-answerability, 2026-10-17

Sources: Charter C4.1 and C8.5 (approved in APPROVAL_RECORD-1), `01-s5-fix.md`, `02-rollback-rehearsal.md`, `03-vendor-risk-note.md`, slice 7 `11-monitoring-plan.md`, `11c-change-request.md`, `13-release-checklist-tier3.md` (sections 7 to 9, T items). All figures copied from those. No code, test, skill, agent, invariant or method file touched. Nothing committed.

## Files changed

| File | Change |
|---|---|
| `runs/docs-answerability-2/11-monitoring-plan.md` | T5: one note added under the header: owner adopted thresholds (section 1), cadence (sections 2, 4) and stop rules (section 2) as written, Charter C8.5 / APPROVAL_RECORD-1, Gopal Patwa (operator), with the standing mitigation "stop typing `/aveto-judge`, use `retrieve` alone". Plan body unchanged. |
| `docs/runbooks/answerability-judge.md` | T5: new. Plan sections 2 and 5 (section numbers verified in the plan: 2 = periodic re-check protocol, 5 = runbook and rollback) copied, with a header on source and adoption. Deliberate departures: the plan's open-item paragraph at the start of section 5 (about writing this copy) was dropped as now done; an "Update" block after the "Rollback is tested" paragraph records the T4 rehearsal (original sentence kept, marked superseded); the header notes S5 fixed and S6 deleted since the plan and that the signal/section references stay in the plan. |
| `runs/docs-answerability-2/11c-change-request.md` | T2: human-owner row of the Approvals table now APPROVED as given by the Charter (landing by pull request into `main`; merge is the owner's own act), Gopal Patwa, 2026-10-17, time of day not recorded, tested rollback yes (`02-rollback-rehearsal.md`). Release Manager and Compliance approver rows untouched (still PENDING). |
| `runs/docs-answerability-2/STATE.md` | T9c: `Updated:` set to 2026-10-17; Next action says slice 7 closed as an internal candidate and its T items are carried out by `land-answerability`. **No duplicate record 7 row exists in the Approvals table** (record 7 appears once in it, line 46; line 25 is the stage table), so nothing was removed; the Next action says so. |
| `README.md` | T7, T9b: status block and judge-step section rewritten: known limit (19 of 24, 79.2%, under 80%; 16 of 24 after judging), eval-path-only bars, operating rule, tier 3, S5 fixed with the new operator usage, S6 deleted, monitoring adopted and runbook link, rollback rehearsed. Old "not cleared to land", T1-T11 deferred list and S5/S6 open items removed. No release-verdict claim; "landing by pull request; the owner merges". |
| `.agentic/CURRENT_MVP_STATUS.md` | Same content as README (T7, T9b); the "Not yet done" list now carries the merge being the owner's, DPA not in place with other vendor fields UNKNOWN, operator path unmeasured, D6. Final-tree regression (T6) is not stated either way; it is the Release Manager's/Orchestrator's record. |
| `runs/land-answerability/05-docs-note.md` | This file. |
| `runs/land-answerability/STATE.md` | Stage row added. |

## Blocked: `docs/ARCHITECTURE.md` (Architect-owned; write-scope guard refused the edit)

Hand to the Architect (T9b). Proposed changes:
1. Header "Current as of": land-answerability, 2026-10-17, branch `claude/land-answerability`, "landing by pull request; the owner merges" (replace "docs-answerability-2, stage 10b ... not merged").
2. Replace "tier 3 verdict is **GO WITH CONDITIONS** (internally releasable candidate, not announced, not cleared to land; conditions T1 to T11 ...)" (header and Safety stance) with: release tier 3 (owner's ruling, APPROVAL_RECORD-9 of slice 7); slice 7 closed as an internal candidate and its T items are carried by `land-answerability`; landing by pull request, the owner merges; not announced. No Release Manager verdict claimed.
3. State S5 fixed: `/aveto-judge-seen` takes no caller text in its shell line; the operator writes the run id to `.aveto-judge/seen-id` and runs it with no argument (update "Data flow" item 4, last bullet, which still says `/aveto-judge-seen <run id>`, and the component row, which says the helper "injects the payload for a run id").
4. State the S6 rule was deleted (owner, 2026-10-16) wherever it is listed as undecided (none found in ARCHITECTURE.md beyond the verdict wording).
5. Operating rule (Charter C4.1): public-docs questions only until a DPA is in place; personal subscription, no DPA.
6. ADR 0008 stays Proposed (its entry already says so).

Applied by the Architect, 2026-10-17: items 1 to 5 edited into `docs/ARCHITECTURE.md` (header, Judge agent component row, Data flow item 4 last bullet, Safety stance); item 6 needed no change. No figures added; no code, invariant or ADR touched; not committed.

## Flags
- The retrieval figure 19/24 appears elsewhere in the docs for the dev set (also 79.2%); not changed.
- The runbook says "the plan" for signals/sections it does not copy; a reader of the repo alone sees run-record paths. Acceptable per the Charter's instruction to copy only sections 2 and 5.
- Security advisory A5: runbook rollback item 6 reworded (S6 deleted 2026-10-16; `.claude/settings.local.json` now holds only the run's local rules, Charter C6.P, gitignored, deleted when the run ends). Done.
- Security advisory A5, ADR 0008: the write-scope guard refused the edit (Architect-owned). Exact one-line edit for the Architect, to insert after line 27 (item 4, which shows `/aveto-judge-seen <run id>`), changing nothing else (ADR stays Proposed): `   *Note (slice land-answerability, 2026-10-17): after the S5 fix, `/aveto-judge-seen` takes no argument; it reads the run id from `.aveto-judge/seen-id`.*`
- No figures invented. Time of day is recorded nowhere (as stated in APPROVAL_RECORD-1).
