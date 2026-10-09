# Support requests — docs-abstention (from the Orchestrator)

## Request 1 — pack defect: no scoped role may write `.agentic/CURRENT_MVP_STATUS.md`

- **File:** `.claude/hooks/write-scope-guard.mjs` (EXTRA / EXCLUDE tables).
- **What happened:** the Release Gate's stale-text instructions require editing `.agentic/CURRENT_MVP_STATUS.md`; the owner approved it (APPROVAL_RECORD-8.md). The Tech Writer's write scope is README/CHANGELOG/docs/ and excludes `.agentic/`; the Architect owns only SAFETY_INVARIANTS.md, ARCHITECTURE.md and docs/adr/. No scoped role owns CURRENT_MVP_STATUS.md, so the guard blocked the Tech Writer.
- **Expected:** some role (likely Tech Writer or Post-Launch Learning) is named as owner of the status file, since every slice must keep it true.
- Nothing was patched or worked around. Handling in this slice is held for the owner's instruction.
