# Slice State — docs-retrieval-2-proof

- **Ask:** Score the frozen file-level retrieval method once on the owner's third held-out set (slice B of docs-retrieval-2)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** QA Evidence — held-out gate failed; escalated (ESCALATION-1.md)
- **Status:** blocked-on-failure
- **Least-privilege:** enforced — role subagents load from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 6be205c
- **Started:** 2026-09-29T20:58:53Z  ·  **Updated:** 2026-09-29T21:01:51Z

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed (slice A, 2026-09-29); owner directed slice B | runs/docs-retrieval-2-proof/intent.md (== slice A's) | human confirmed |
| Intake | Orchestrator | done | runs/docs-retrieval-2-proof/00-slice-plan.md | owner directed creation 2026-09-29T20:58:53Z |
| QA Evidence | qa-evidence | done: GATE FAILED (11/16, bar 13) | runs/docs-retrieval-2-proof/01-qa-result.md | gate: >= 13 of 16 answerable, third set, once: FAIL |
| Security Review | security-privacy | not run — gate failed | — | — |
| Release Gate | release-manager | not run — gate failed | — | — |
| Post-Launch | post-launch-learning | pending (smoke) | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Drop the unanswerable half of the gate (slice A, covers the pair) | 4 | yes | APPROVED | Gopal Patwa | 2026-09-29T16:54:46Z | runs/docs-retrieval-2/APPROVAL_RECORD-1.md |
| Retrieval always returns its top 5 files (slice A, covers the pair) | 4 | yes | APPROVED | Gopal Patwa | 2026-09-29T16:54:46Z | runs/docs-retrieval-2/APPROVAL_RECORD-2.md |
| INV-4 "Enforced by" note: remove the retired test's name (applied) | 4 | yes | APPROVED | Gopal Patwa | see record | runs/docs-retrieval-2/APPROVAL_RECORD-3.md |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 430k tokens  ·  **Depth:** standard
- **Spent:** 27k (6%)  ·  **Remaining:** 403k
- **Next stage:** Security Review (security-privacy, review) est. 100k → **STOP-AND-ASK** — held-out gate failed (11 of 16, need 13); a failed gate sends the slice back, never forward; see ESCALATION-1.md

Slice B's own budget from Scope Review (slice A 460k + slice B 430k = the owner-confirmed 890k), with no separate headroom: an overrun is a stop-and-ask. Budget units are peak context per spawn; processed tokens are typically 10–50× larger. Prefer one fresh spawn per stage.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| QA Evidence (held-out gate) | 0 of 2 used; escalated | 2 | gate-violation | third held-out: answerable 11/16 (need 13). See ESCALATION-1.md |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| QA Evidence (qa-evidence; fresh single spawn) | sonnet-5-5 | high (declared) | — | — | 1:30 | 26,879 | 11 | 0 |
| **Total** | | | | | | 26,879 | 11 | |

Model comes from `usage.mjs` (the harness log) after each stage; effort is the declared frontmatter value.

## Next action

Owner decides (ESCALATION-1.md): A) stop and record the finding, the next question being a reranker as its own slice with a fourth fresh held-out set (recommended); B) spend a retry (needs a larger budget and a fourth set); C) change the bar (rule 4, owner only, not recommended). Nothing runs until answered.
