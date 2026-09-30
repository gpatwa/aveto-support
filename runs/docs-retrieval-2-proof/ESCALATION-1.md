# Escalation 1 — the third held-out gate failed (docs-retrieval-2-proof)

- **Slice / stage:** docs-retrieval-2-proof (slice B), QA Evidence, the single scoring run of the frozen method
- **Category:** gate-violation (the gate cannot be passed honestly by the method as built)
- **Raised:** 2026-09-29T21:01:51Z. **No retry has been spent**; escalated because the intent already names the next step for a fail (Decision 3) and any further attempt needs the owner.

## What was attempted

The frozen method `file-rrf-v1` (commit `b3f3fc41…`, the fixed 123-file corpus, file-level ranking, always the top 5 files) was scored **once** on the owner's third held-out set (`74c5a2d`, committed after the freeze), then each earlier set once as a diagnostic. Nothing was tuned and no method file changed (verified). Raw outputs: `eval-run-1-heldout3.txt`, `eval-run-2-heldout2-diagnostic.txt`, `eval-run-3-dev-diagnostic.txt`; write-up `01-qa-result.md`.

| Set | Result | Bar | |
|---|---|---|---|
| **Third held-out (the gate)** | **11 of 16 answerable = 68.8%** | ≥ 13 (80%) | **FAIL** by two questions |
| Third held-out, unanswerable | 4 printed | none | diagnostic only |
| Second held-out (seen; diagnostic) | 12 of 17 = 70.6% | none | not a gate |
| Dev set (seen; diagnostic) | 19 of 24 = 79.2% | none | not a gate |

Misses on the gate set: t04 (vendor risk template), t06 (UX researcher role), t12 (AI governance role and AI risk template), t13 (change request template), t15 (`execution/SECURITY.md`). In each, the expected file was narrow and specialised and the top 5 held broader or neighbouring role and template files. That is a pattern in five items, a hypothesis and not a finding.

## Against slice 1, on the same sets

Slice 1's method, ignoring its abstention (its "ungated recall@5"), put a correct file in the top 5 for 8 of 17 on the second held-out set and 17 of 24 on the dev set (slice 1's `eval-run-2-heldout.txt` / `eval-run-3-dev-diagnostic.txt`). The new method scores 12 of 17 and 19 of 24 on those same sets: +4 and +2 questions. Both sets are seen, so this is an indication, not proof; the fresh set is the fair test, and it is 11 of 16.

## Caveats that belong to the record

The third set was drafted by Claude in the playbook session, reviewed and committed by the owner; the drafter had read both earlier runs and slice 2's tech spec (it knew the method) but reports it never ran retrieval on the questions. 16 questions is a small sample: one question is 6.25 points, and 11 vs the 13 bar is a two-question shortfall. The earlier sets are seen sets.

## Smallest decisions the owner could make

- **A. Stop here and record the finding (recommended).** Nothing ships; Security Review and the Release Gate do not run; the close-out records the result and carries forward the hypothesis. The intent's Decision 3 already names the next question: a **reranker** (a cross-encoder that re-orders the top candidates), which is a new model, dependency and download (approval rules 5 and possibly 4), its own slice, and a **fourth fresh held-out set**, since this one is now seen.
- **B. Spend a retry on another method change within the existing approvals** (no new model). It would need a fourth fresh set, a new design choice made after seeing these misses (so not held out from the designer), and about 360k for Architecture, Implementation and QA before Security, the Release Gate and the close-out (another about 300k). Slice B's budget is 430k with 27k spent, so this needs the owner to set a larger budget. Expected value is low: the intent already judged that further gains need a stronger component.
- **C. Change the bar** (for example to accept about 69%). That weakens a gate after seeing the result: approval rule 4, the owner's decision only, and exactly the reactive change the intent avoided. Not recommended.

## Resolution — 2026-09-30T01:32:07Z

Prompted with options A, B and C (see above), the owner (Gopal Patwa) answered, verbatim: **"A."** Read as option A as presented: **stop here and record the finding.**

- Nothing ships. Security Review and the Release Gate do not run (a failed gate sends the slice back, never forward).
- The Post-Launch close-out runs (smoke; it was in the plan either way) and records the result, the caveats, and the carry-forward.
- No retry is spent (0 of 2 used). The next question, per the intent's Decision 3, is a reranker: its own slice, with its own rule 5 (and possibly rule 4) approvals and a fourth fresh held-out set. **None of that is started or approved by this answer.**
- `docs-retrieval-ci` stays unstarted (blocked on a passing gate).
