# Slice State — docs-retrieval-2-proof

- **Ask:** Score the frozen file-level retrieval method once on the owner's third held-out set (slice B of docs-retrieval-2)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** QA Evidence
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents load from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 6be205c
- **Started:** 2026-09-29T20:58:53Z  ·  **Updated:** 2026-09-29T20:58:53Z

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed (slice A, 2026-09-29); owner directed slice B | runs/docs-retrieval-2-proof/intent.md (== slice A's) | human confirmed |
| Intake | Orchestrator | done | runs/docs-retrieval-2-proof/00-slice-plan.md | owner directed creation 2026-09-29T20:58:53Z |
| QA Evidence | qa-evidence | in-progress | — | gate: >= 13 of 16 answerable, third set, once |
| Security Review | security-privacy | pending (only if the gate passes) | — | — |
| Release Gate | release-manager | pending (only if the gate passes) | — | — |
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
- **Spent:** 0k (0%)  ·  **Remaining:** 430k
- **Next stage:** QA Evidence (qa-evidence, build) est. 130k → **PROCEED** (0k + 130k ≤ 430k)

Slice B's own budget from Scope Review (slice A 460k + slice B 430k = the owner-confirmed 890k), with no separate headroom: an overrun is a stop-and-ask. Budget units are peak context per spawn; processed tokens are typically 10–50× larger. Prefer one fresh spawn per stage.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| — | 0 | 2 | — | — |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| **Total** | | | | | | 0 | 0 | |

Model comes from `usage.mjs` (the harness log) after each stage; effort is the declared frontmatter value.

## Next action

QA scores `evals/retrieval-heldout-3.toml` once, then the two earlier sets once each as diagnostics, then re-runs the full regression. Frozen method commit b3f3fc41f2382283678e638b55ff44b32876034c.
