# Approval record 6 — stop the model path (option 1); drop the candidate code

- **Decision:** option 1 — stop this slice's model path after the failed spec 4.1 seen-set condition (pooled Bar 1 2/20 vs required >= 16/20). Drop the candidate judge code from the branch.
- **Approver:** Gopal Patwa, typed directly in the driving session
- **When (UTC):** 2026-10-09T17:49:16Z
- **In the owner's words:** "option 1, drop the candidate code"
- **Effect:** the candidate code commit 479f82a is reverted by a new commit (history kept, nothing rewritten, nothing pushed). The model approvals in APPROVAL_RECORD-5.md (rule 5 for qnli-electra-base, rule 4 INV-4 items 4-i/4-ii, rule 4 INV-5 and the A1 line) are LAPSED: unused, not applied, and not to be applied. The method is not frozen; there is no method commit; the fifth set is not run.
- **Not approved by this record:** the INV-4 correction of spec 8.3 (a different text, still PENDING), any push, merge or PR.
