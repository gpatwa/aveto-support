# Approval record 8 — stale-text pass, including .agentic/CURRENT_MVP_STATUS.md

- **Approver:** Gopal Patwa, typed directly in the driving session
- **When (UTC):** 2026-10-09T20:41:46Z
- **In the owner's words:** "approve the stale-text pass including CURRENT_MVP_STATUS"
- **Scope approved:** the edits listed in `runs/docs-abstention/06-release-checklist.md`, section "Stale text", items 1-4: README.md lines 49-51 and its status line, .agentic/CURRENT_MVP_STATUS.md lines 11-16, docs/ARCHITECTURE.md lines 27, 85-87, 109-112, 132-134, 141-144, and a final grep of docs/ and README.md. Wording says retrieval never abstains; abstention is unbuilt; no whole-pipeline or end-to-end figure; no production or drafting-readiness claim.
- **Out of scope / not approved:** any edit to INV-4 or INV-5 (SAFETY_INVARIANTS.md), to code or tests, push, merge, PR or deploy. `.agentic/LOCAL_COMMANDS.md` is already correct and untouched.

## Addendum 2 (2026-10-09T21:43:05Z): option A chosen for CURRENT_MVP_STATUS.md

- The owner first typed "B, make the edit yourself"; the tool call applying it was interrupted by the owner before any edit was made, and nothing was written. The owner then typed "A": re-spawn the Tech Writer under pack v17 (commit ebd6c6e, made by the support session on this branch; the owner's go on installing it is as relayed by that session and not separately recorded here).
- No Orchestrator edit was made, and no addendum for option B was written.
- Scope unchanged: the `retrieve` bullet at lines 11-16 and the "Abstention is not built" bullet, per `06b-stale-text-pass.md`; no other `.agentic/` file.
