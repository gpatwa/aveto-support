# Slice State — public-ask-the-docs

- **Ask:** `intents/public-ask-the-docs.md` — a public "ask the docs" page, live on Azure: verbatim passages or "no confident match", judged through the Anthropic API under hard cost and abuse limits
- **Project pack:** ai-agent-product
- **Release tier:** 3
- **Current stage:** 1 Scope review
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents/teammates in `.claude/agents/` (pack v26), run from this repo's worktree
- **Telemetry:** self-reported — see `TELEMETRY.md`
- **Charter:** runs/public-ask-the-docs/CHARTER.md, sha256 d0acc5346a80e199e3f95ac57e23a2c01fec43e56d93dbda3b4a03e6a99fa74c approved in APPROVAL_RECORD-1
- **Started:** 2026-10-20  ·  **Updated:** 2026-10-20

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed by the owner 2026-10-20 (copied unchanged) | runs/public-ask-the-docs/intent.md | human confirms |
| Intake | Orchestrator | done | runs/public-ask-the-docs/00-slice-plan.md | n/a |
| Setup | Orchestrator | done except C6.5 to C6.7 (owner and support session) | 00-slice-plan.md Prerequisites | dry runs |
| Charter | Human | approved by hash 2026-10-21T06:42:08Z | runs/public-ask-the-docs/CHARTER.md | human approves by hash |
| 1 to 19 | per plan | pending | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Approve the Charter | Charter | yes | approved | Gopal Patwa | 2026-10-21T06:42:08Z | runs/public-ask-the-docs/APPROVAL_RECORD-1.md |

## Budget

- **Budget:** 2000k tokens  ·  **Depth:** standard
- **Spent:** 0k (0%)  ·  **Remaining:** 2000k
- **Next stage:** Scope review (review) est. 100k → **PROCEED**

Note: ceiling 3000k, hard cap 3600k (Charter C2). Orchestrator intake and setup spend is the driving session's, not a spawn.

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

## Next action

Spawn stage 1 (Engineering Manager, scope review). C6.7 gate-set hash check before stage 18.

## Setup log

- 2026-10-21T06:35Z C6.5 dry run passed: `az keyvault secret list --vault-name kv-aveto-ask-gp` lists `anthropic-api-key` (name only; value never read). Resource group and vault created by the owner; signed-in Azure account is [owner email removed] (shown in the vault's createdBy).
- 2026-10-21T06:35Z C6.6: owner's statement in this session, "c6.6 is set" (Anthropic console monthly limit $10). Not verifiable by an agent.
- 2026-10-21T06:35Z C6.7: not yet in place (`/Users/gopalpatwa/opt/aveto-gates/public-gate-1.toml` absent); needed at stage 18.
