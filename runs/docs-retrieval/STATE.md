# Slice State — docs-retrieval

- **Ask:** Retrieval only, no model: return the passages in Aveto's pinned docs that answer a question, with exact provenance (see intent.md)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Scope Review done — split into `docs-retrieval-core` and `docs-retrieval-ci`; next is Architecture (docs-retrieval-core)
- **Status:** blocked-on-approval
- **Least-privilege:** enforced — role subagents are discoverable from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 70c095d (absolute; relative path does not resolve from a worktree)
- **Started:** 2026-09-27T02:29:54Z  ·  **Updated:** 2026-09-27T21:04:32Z

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed (dcca4c1, a3803ca) | runs/docs-retrieval/intent.md (== main:intent.md) | human confirmed |
| Eval set | Human (owner) | done (a4e5275, before any retrieval code) | evals/retrieval.toml | owner-authored; read-only to implementer |
| Intake | Orchestrator | done | runs/docs-retrieval/00-slice-plan.md | owner confirmed plan 2026-09-27T20:59:31Z |
| Scope Review | engineering-manager | done — split into docs-retrieval-core + docs-retrieval-ci | runs/docs-retrieval/01-scope.md | RUN_ECONOMICS §2 (>6 stages / ~600k signal) |

### docs-retrieval-core

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Architecture | software-architect | pending — awaits owner acceptance of the split | — | — |
| Implementation | backend-architect | pending — blocked on Approval-1 | — | — |
| QA Evidence | qa-evidence | pending | — | — |
| Security Review | security-privacy | pending | — | — |
| Release Gate | release-manager | pending | — | — |

### docs-retrieval-ci (sequenced after docs-retrieval-core's Release Gate)

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Implementation | backend-architect | pending — blocked on docs-retrieval-core + Approval-1 | — | — |
| QA Evidence | qa-evidence | pending | — | — |
| Security Review | security-privacy | pending | — | — |
| Release Gate | release-manager | pending | — | — |
| Post-Launch | post-launch-learning | pending (smoke) | — | — |

## Approvals

Plan confirmation (not a rule approval): Gopal Patwa, 2026-09-27T20:59:31Z, verbatim: "plan is approved".
Approval 1 is PENDING and gates **Implementation**, per the confirmed plan; Scope Review and Architecture do not depend on it.

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Read-only fetch of pinned playbook docs in ingest + CI | 5 | yes | PENDING | — | — | runs/docs-retrieval/APPROVAL_REQUEST-1.md |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 690k tokens  ·  **Depth:** standard
- **Spent:** 55k (8%)  ·  **Remaining:** 635k
- **Next stage:** Architecture (docs-retrieval-core, review) est. 100k → **STOP-AND-ASK** — the owner has not yet accepted the split (plan: a split returns to the owner before anything else runs)

The 690k above is docs-retrieval-core's proposed budget (Σ560k, 5 stages, +130k headroom), pending owner acceptance of the split in `01-scope.md`.
Note: docs-retrieval-ci is proposed at another 690k (Σ560k + 130k). With Scope Review, the split totals 1,220k vs the original single-slice 890k. The owner decides.
Spent is the harness's `subagent_tokens` for Scope Review (55,125; peak context, per RUN_ECONOMICS §1), not the 100k estimate.
The installed guard checks spent ≥ budget only; spent + estimate is checked by hand before each spawn.

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
| Scope Review | sonnet | medium | 2026-09-27T20:59:31Z | 2026-09-27T21:03:39Z | 4:08 | 55,125 | 18 | 0 |
| **Total** | | | | | | 55,125 | 18 | |

## Next action

Owner decides: (1) accept or amend the split in 01-scope.md (incl. where the ≥80% bar is enforced), (2) answer APPROVAL_REQUEST-1. Then spawn software-architect for docs-retrieval-core Architecture.
