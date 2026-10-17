# Docs delta - docs-answerability-2 (stage 10, Tech Writer, smoke)

Basis: Release Gate verdict GO WITH CONDITIONS (`09-release-checklist.md`), condition C6. Figures are copied from the checklist's "Evidence figures to carry" table, which copies `05-seen-check.md` and `07-gate-scoring.md`. I opened no set, key, question, reply or diff, and ran no tests. Nothing was committed or approved.

## Applied

| File | Change | Why |
|---|---|---|
| `README.md` | Status banner rewritten: retrieval plus an attended judge step on the branch, not released, not announced, not deployed; `retrieve` itself still never abstains; the judge step can print `no confident match`. Intro line "It answers questions" changed to "is designed to answer" (nothing answers today). Offline paragraph qualified: the program sends nothing; the judge step sends through the operator's session, link to INV-5. New "judge step" section under Status: how it works, plain limits, a figures table, open owner decisions. | C6, intent Done means (only recorded figures, only after the verdict). |
| `.agentic/CURRENT_MVP_STATUS.md` | "What exists": the "abstention is not built / no end-to-end figure" bullet replaced by history plus the judge step, all recorded figures, the verdict. "Not yet done": stale `wordpiece_golden.json` line removed (verified: `tests/fixtures/wordpiece_golden.json` exists, Glob), replaced by the open owner decisions, the one failing model-marked test, and the not-released line. "Out of scope" generative-call line made precise (by the program; the judge is outside it and returns only a verdict). "Questions never leave the machine" qualified. | Scope review section 3 stale lines; C6. |

Figures carried (all in README and status): stage 5 Bar 1 20/20 (16/20), Bar 2 24/28 (23/28); stage 7 Bar 1 24/24 (20/24), Bar 2 16/19 = 84.2% (80%); judge errors 0; never-abstain Bar 1 0/24 (Bar 2 19/19 in README); best-score rule NOT MET both stages (13/20, 17/28; 10/24, 13/19); end to end 16/24; retrieval gate exit 1, 19/24 = 79.2%, not a registered bar; over-abstention 3/19 (4/28 at stage 5); one scored run; tool-use audit clean; D4 source reuse (21 of 24). Bar 2 one question of margin at both stages is stated. No "production-ready", "safe" or "accurate" claim anywhere.

Limits stated: operator-run, own Claude Code session on subscription, attended only, not unattended, not a service; program offline; Anthropic receives the judge's context as INV-5 says (linked, not restated); one model (`claude-sonnet-5-5`), one set, 48 spawns each stage; the judge adds an over-abstention failure mode; open owner decisions (tier, S5, S6, retrieval gate, identity/DPA, final-tree run) listed as open; `/aveto-judge-seen` not to be invoked.

`.agentic/LOCAL_COMMANDS.md` was already updated and not touched. `SAFETY_INVARIANTS.md` not touched.

## NOT applied: blocked by the write-scope guard, handed to the Architect

The guard refused edits to `docs/ARCHITECTURE.md` and `docs/adr/0008-operator-run-answerability-judge.md` ("owned by another role, not tech-writer"). The brief says the same (the Architect owns them). I did not work around it. As they stand, both files still say the judge step is "not yet measured", "no result yet", and carry a "Pending, docs-answerability-2" note, so they now understate what the record shows and contradict README and status. Proposed edits for the Architect (describe, not applied):

1. `docs/ARCHITECTURE.md`, "Safety stance": replace the "Pending" note with: the bullets summarise `.agentic/SAFETY_INVARIANTS.md`, whose INV-4 and INV-5 words were approved (APPROVAL_RECORD-5 and -8) and are authoritative.
2. Remove the four "**Stale on this branch:**" markers and rewrite those sentences as current: INV-4 (a model may rank, and in the operator-run judge step return a verdict; it never produces, selects or alters shown text); "not silent" (judge step can print `no confident match`; figures as above; go with conditions, not announced); INV-5 ("the program sends no question, passage or user text anywhere"; the operator's session sends to Anthropic, attended only).
3. Drop "not yet measured" in the mermaid subgraph title, in step 4, in the Draft bullet and in the "Answerability judge (step 2b)" bullet; change "the INV-5 words that would state it are pending" to "INV-5 states it"; lines about `tools/judge_run.py` "not built yet" need checking against the tree (I did not verify).
4. `docs/ARCHITECTURE.md` Decisions, ADR 0008 line: "no result yet" is stale; say both registered bars were met once and it stays Proposed.
5. `docs/adr/0008`, Status line: "No result of this slice exists as this record is written" is stale in the same way. Leave Proposed (acceptance is the owner's; the Release Gate gives a conditional go and does not accept ADRs), and add a dated note with the figures.
6. Unrelated and untouched: ADR 0003 "implementation pending" status line.

## Intentionally not documented

- Security findings S1-S4, S7, S8 detail (advisory; in `08-security-review.md`), the rollback plan (in the checklist and tech spec), approval record text.
- No release notes or changelog entry: nothing is released or announced. No user help article beyond the README section.

## Handoff

- To the Architect: items 1-6 above, before close-out, or the owner may accept the divergence.
- To the Orchestrator: STATE stage row and Next stage updated (Close-out, 55k). Spent left to you.
- Owner items stay open and are listed in README and status as open, not hidden.
