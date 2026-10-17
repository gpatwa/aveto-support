# Architecture docs - docs-answerability-2 (stage 10b, Architect, smoke)

Basis: the blocked edits handed over in `10-docs.md` ("NOT applied", items 1 to 5), the verdict and figures in `09-release-checklist.md` ("Verdict", "Evidence figures to carry"), kept consistent with `README.md`. `.agentic/SAFETY_INVARIANTS.md` was read, not edited. No set, key, question, reply or diff was opened. Nothing committed or approved.

Facts checked before editing:
- `APPROVAL_RECORD-5` is the rule 4 approval of the INV-4 and INV-5 words (2026-10-12); `APPROVAL_RECORD-8` is the rule 4 approval of one INV-5 environment-list edit (2026-10-13).
- `tools/judge_run.py` exists in the tree (Glob: `tools/judge_run.py`, `tools/__init__.py`).
- `APPROVAL_RECORD-9` exists: "release tier ruled 3 ... (owner, typed, 2026-10-16)" (title line only read).

Course correction from the coordinator (mid-stage, applied): do not edit `STATE.md`. The owner has ruled tier 3 (APPROVAL_RECORD-9), so every mention of the verdict says: GO WITH CONDITIONS was given at tier 2 and is being re-run for tier 3. Tier 3 is the owner's ruling. ADR 0008 stays Proposed.

## Changes: `docs/ARCHITECTURE.md`

| Where | Before | After |
|---|---|---|
| Header "Current as of" | pass 2 (2026-10-12); "not yet measured", INV words "await the owner's approval" | stage 10b (2026-10-16); both registered bars met once; verdict GO WITH CONDITIONS given at tier 2, being re-run for tier 3 (owner's ruling, APPROVAL_RECORD-9); nothing released or announced; INV-4/INV-5 words approved, in `.agentic/SAFETY_INVARIANTS.md` |
| ASCII pipeline diagram | "this branch, not yet measured" | "this branch" |
| Components, Judge (offline half) | "This branch, not yet measured." | "This branch." |
| Mermaid subgraph title | "attended, not yet measured" | "attended" |
| Data flow step 4 heading | "this branch; not yet measured; ADR 0008, proposed" | "this branch; ADR 0008, proposed" |
| Data flow step 4, data-leaves bullet | "INV-5 words that would state it are pending" | "INV-5 in `.agentic/SAFETY_INVARIANTS.md` states it" |
| Data flow step 4, eval bullet | `tools/judge_run.py` "planned ... not built yet ... will" | exists (verified), outside the package, present tense |
| Adapter boundaries, Draft bullet | "is not yet measured and is not wired" | "is not wired" |
| Adapter boundaries, judge bullet | "this branch, not yet measured" | "this branch" |
| Safety stance note | "Pending" note (replacement words awaiting approval) | pointer: bullets are a summary; INV-4 and INV-5 in `.agentic/SAFETY_INVARIANTS.md` are authoritative, approved under APPROVAL_RECORD-5 (and -8 for one INV-5 edit); the file wins on any difference. The approved words are not restated. |
| Safety stance, INV-4 bullet | old "only rank and decide confidence" + Stale marker | current summary: rank, confidence, and in the operator-run judge step only a verdict choosing between `retrieve`'s whole output and `no confident match`; no model produces, selects among or alters shown text |
| Safety stance, "Not silent" bullet | "abstention is not built" Stale marker; "no measured result yet" | current: `retrieve` alone never abstains; judge step can print `no confident match`; stage 5 and stage 7 figures; judge errors 0; one question of margin on Bar 2 at both stages; end to end 16/24 (diagnostic); verdict at tier 2 being re-run for tier 3; not released, not announced |
| Safety stance, INV-5 bullet | "No question ... ever leaves the machine" + Stale marker | "The program sends no question, passage or user text anywhere" (with the offline commands and test), then the operator's session as the one exception (Anthropic, APPROVAL_RECORD-3, attended only); INV-5 lists what is attached |
| Decisions, ADR 0008 line | "no result yet" | both registered bars met once (stage 5 and stage 7); acceptance is the owner's; still Proposed |

All four "Stale on this branch" markers removed. Grep confirms no "not yet measured", "Stale on this branch", "not built yet" or "no result" remains. The only "pending" left is the ADR 0003 status sentence, which is unrelated and not touched (10-docs item 6).

## Changes: `docs/adr/0008-operator-run-answerability-judge.md`

- I added one sub-bullet under **Status**: "Note, 2026-10-16 (Architect, stage 10b): results recorded; status stays proposed". It records:
  - stage 5: Bar 1 20/20, Bar 2 24/28
  - stage 7: Bar 1 24/24, Bar 2 16/19 = 84.2%
  - judge errors 0, and one question of margin on Bar 2 at both stages
  - the INV words approved (records 5 and 8)
  - the verdict GO WITH CONDITIONS, given at tier 2 and being re-run for tier 3 (owner's ruling, APPROVAL_RECORD-9), so the Release Gate acceptance condition is not settled
  - acceptance is the owner's, and neither the note nor the Release Gate accepts the record
- I did not change the original status text, including "No result of this slice exists as this record is written". That sentence is still true of the time of writing, and the dated note brings the record up to date. Status stays **proposed**. The record is not accepted, so adding a note is allowed.

## Not done

- `STATE.md` was not edited, per the coordinator. The Orchestrator owns the stage row, Next stage and Spent.
- `.agentic/SAFETY_INVARIANTS.md`, code, tests, agents, skills, prompts and evals were not touched. No set, key, question, reply, `06-label-review.md` or `diffs.md` was opened.
- Nothing was committed or approved. No "production-ready", "safe" or "accurate" claim was made.
- Divergence confirmed, for the Tech Writer or Orchestrator: `README.md` was written before APPROVAL_RECORD-9 and is now out of date. Line 9 gives the verdict "go with conditions" without the tier-3 re-run. Lines 160-161 list the release tier as an open owner decision ("this slice is run at tier 2"), but the owner has now ruled it. `.agentic/CURRENT_MVP_STATUS.md` probably has the same problem (not checked). I edited neither (not my files).

Follow-up, 2026-10-16 (tier 3 verdict): in `docs/ARCHITECTURE.md` (header and the "Not silent" bullet) and in the ADR 0008 2026-10-16 note, I replaced "verdict GO WITH CONDITIONS was given at tier 2 and is being re-run for tier 3" with: the owner ruled tier 3 on 2026-10-16 (APPROVAL_RECORD-9), and the tier 3 verdict is GO WITH CONDITIONS (internally releasable candidate, not announced, not cleared to land; conditions T1 to T11; `13-release-checklist-tier3.md`). The record assigns T1 to T11 to "the owner, or a named role" (for example, T11 is the Orchestrator's), so the text says that rather than "the owner holds" all of them. Nothing else changed: ADR 0008 stays Proposed, and the bullet list above shows the pre-follow-up state.
