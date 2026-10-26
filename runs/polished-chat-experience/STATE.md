# Slice State — polished-chat-experience

- **Ask:** intents/polished-chat-experience.md — one polished reference product, the ask-the-docs chat, built, released and shown in public
- **Project pack:** ai-agent-product
- **Release tier:** 3
- **Current stage:** 1 Scope review
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents from this repo's `.claude/agents/`
- **Telemetry:** self-reported
- **Charter:** runs/polished-chat-experience/CHARTER.md, sha256 a24c3c56e430aed399ea88d4adaee8838694e5fd1950c776c5c49a1564b10312, approved in APPROVAL_RECORD-1 (2026-10-26T20:08:31Z)
- **Started:** 2026-10-26T20:01Z  ·  **Updated:** 2026-10-26T20:15Z

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed (2026-10-26, in the intent file) | runs/polished-chat-experience/intent.md | human confirms |
| Intake | Orchestrator | done | runs/polished-chat-experience/00-slice-plan.md | n/a |
| Charter | Human | approved | runs/polished-chat-experience/CHARTER.md | approval by hash |
| 1 Scope review | Engineering Manager | done, with a STOP-FLAG (S1: refusal card "nearest passages" contradicts INV-4(b); needs owner decision before stage 2) | runs/polished-chat-experience/01-scope.md | n/a |
| 2 to 14 | see plan | pending | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Charter (covers deploy and rollback rehearsal C8.3, push and PR C8.2, live checks C3.1) | 3, 5 | yes | approved | Gopal Patwa | 2026-10-26T20:08:31Z | runs/polished-chat-experience/APPROVAL_RECORD-1.md |

## Budget

- **Budget:** 1000k tokens  ·  **Depth:** standard
- **Spent:** 0k (0%)  ·  **Remaining:** 1000k
- **Next stage:** 1 Scope review (ai-agent-product) est. 40k → **PROCEED**

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

Read 01-scope.md. Put S1 to the owner (option A: refusal card without nearest passages, recommended; option B: amend INV-4(b) and the Charter, new hash). Confirm the S3 reading and accept or overrule the recorded oversize deviation. Then spawn stage 2 (UI Designer).
