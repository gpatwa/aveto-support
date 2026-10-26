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
| 2 UX spec | UI Designer | done (ready for architecture; 10 open items for stage 3, section 11) | runs/polished-chat-experience/03-ux-spec.md | n/a |
| 3 Tech spec | Software Architect | done (no STOP-FLAG; two readings for the Orchestrator to rule, 05-tech-spec.md section 15; offline retrieval of the suggestions not run by me, handed to stage 4 step 2) | runs/polished-chat-experience/05-tech-spec.md; docs/ARCHITECTURE.md; docs/adr/0010, 0011, 0012 | n/a |
| 4 Backend | Backend Architect | done at the checkpoint (commit 1 tests first cd4d4b1; commit 2 checkpoint: mypy and ruff clean, 714 passed, 6 failed = the stage 5 contract in tests/test_page_cards.py, as 14.1 step 4 requires); suggestions pass offline retrieval, no reserve needed | runs/polished-chat-experience/04-implementation.md; 04-failfirst-32e54a6.txt; 04-checkpoint.txt; 04-retrieval-check.json | n/a |
| 5 Frontend | Frontend Developer | done (730 passed, 0 failed; mypy, ruff clean; the 6 frozen page-card tests pass; no browser preview possible for the role, left to stage 8; one test assertion widened, see 05-frontend.md) | runs/polished-chat-experience/05-frontend.md; 05-failfirst-base.txt | n/a |
| 6 to 14 | see plan | pending | — | — |

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

Stage 5 done and committed. Rule on the two test-related readings in 05-frontend.md (the `#` prefix added to test_no_external_origin_in_page_or_static for the UX skip link; refusal suggestions/drawer placed in #result-extra). Then stage 6 (review layer) onward; stage 8 is the first real browser look at the page.
