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
| 6 Code review | Orchestrator | done (round 1 and 2, 0 open; F2 fixed f5c139c) | runs/polished-chat-experience/code-review.md | n/a |
| 7 QA evidence | QA Evidence | done, offline (GO WITH CONDITIONS; no P0/P1; 6 P2; 730 passed, mypy and ruff clean; C1.4.1 golden re-derived byte-identical; 4 intent tests fail first and fail under mutation; a11y, 375 px, keyboard, timings, live checks not verifiable here) | runs/polished-chat-experience/13-qa-evidence.md | n/a |
| 9 Security review | Security & Privacy | done, standard (PASS WITH CONDITIONS; no P0/P1; 2 P2: S1 result-store bound in F1 does not hold for zero-spend JUDGE_ERROR, pre-existing on main; S2 counts unauthenticated and inflatable; 4 advisories; 92 passed in touched tests; conditions: S1/S2 to END_REVIEW, re-run test_service_scorecard and check links after the D8 fill) | runs/polished-chat-experience/14-security-review.md | n/a |
| 8, 10 to 14 | see plan | 8: see 08-browser-checks.md (Orchestrator records); 10 to 14 pending | — | — |

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

Stage 9 done (14-security-review.md, PASS WITH CONDITIONS, no P0/P1, GO). Next: D8 figures fill, then the docs stage; per D8 re-run the full suite, C1.4.1, C1.4.7 and tests/test_service_scorecard.py on the final tree, confirm any scorecard links are https://github.com/ to a repository confirmed public (D9), and carry S1, S2 (and A1 to A4 as notes) into END_REVIEW.md before the Release Gate.
