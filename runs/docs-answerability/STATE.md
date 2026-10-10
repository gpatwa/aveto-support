# Slice State — docs-answerability

- **Ask:** intents/docs-answerability.md — a judge step in the operator's own Claude Code session decides whether the shown passages answer the question.
- **Project pack:** ai-agent-product
- **Release tier:** 2
- **Current stage:** Architecture (INV-4/INV-5 words, packet 2.4)
- **Status:** blocked-on-approval
- **Least-privilege:** enforced (to verify at first spawn: agents discovered from this worktree's `.claude/agents/`) — see "Least-privilege tier"
- **Telemetry:** self-reported until `usage.mjs` is run; model names will come from the harness log
- **Started:** 2026-10-10T04:32Z  ·  **Updated:** 2026-10-10 (refusal probe PASS; judge spawn 1 of 2, QA pass B)

- **Branch:** claude/aveto-docs-answerability-85eb6d (worktree off main at 56b4723)
- **Pack:** v17 → v18 by cherry-pick of main 77e6462 (commit a3bcfa6) at the clean boundary after 3a (5d1ca47), on the support session's advice (SUPPORT_REPLIES.md Reply 3); installer not run in the worktree.
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 00d491ac2de0418bd29bd17f9890d814b2260dcd (main), clean. Pack v17.
- **Method commit (freeze):** not yet recorded
- **Judge prompt sha256 (spec 3.2; line 104 of the pilot doc @ 00d491a, quotes stripped, one trailing newline):** 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427 (computed by the Orchestrator)
- **Fifth set:** not read, not requested, not looked for (held by the support session outside this repo)

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed 2026-10-09 (copied unchanged) | runs/docs-answerability/intent.md | human confirms plan |
| Intake | Orchestrator | done, plan confirmed | runs/docs-answerability/00-slice-plan.md | confirmed (APPROVAL_RECORD-1) |
| Scope | Engineering Manager | done | runs/docs-answerability/01-scope.md | accepted; Q1 closed by APPROVAL_RECORD-3 (keep skipped) |
| Architecture (2 passes + 3b addendum) | Software Architect | done (pass 1, pass 2, 3b addendum) | runs/docs-answerability/02-tech-spec.md; runs/docs-answerability/02b-approval-packet.md; docs/adr/0008-operator-run-answerability-judge.md (Proposed); runs/docs-answerability/02c-3b-addendum.md | rule 4/5 approved; split trigger fired (11 files → 3a/3b, spec 7.2); addendum settles 8.1/8.2/8.5/8.6/8.14 and has 3 items needing owner approval before 3b (addendum section 8) |
| Implementation | AI Engineer | 3a done (files 1-8); 3b done (files 9-11, skill not command) | runs/docs-answerability/03a-implementation.md; runs/docs-answerability/03b-implementation.md | regression green (267 passed); live refusal probe still pending (QA) |
| Seen-set check | QA Evidence | pending (refusal probe PASS, 03b-refusal-probe.md; INV-4/INV-5 words next) | runs/docs-answerability/03b-refusal-probe.md | pooled >= 16/20 and 45/56 |
| Freeze | Orchestrator | pending | — | method commit recorded |
| Label review | QA Evidence | pending | — | — |
| Scoring | QA Evidence | pending | — | both bars |
| Security (adversarial) | Security & Privacy | pending | — | — |
| Release Gate | QA / Release Manager | pending | — | — |
| Docs | Tech Writer | pending | — | — |
| Close-out | Post-Launch Learning | pending | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Plan, intent, ceiling 1.4M, decisions 3 and 4 | plan confirmation | yes | approved | Gopal Patwa | 2026-10-10T04:42:04Z | runs/docs-answerability/APPROVAL_RECORD-1.md |
| Data processor: Anthropic via the operator's own Claude Code session | 6 | yes | approved | Gopal Patwa | 2026-10-10T04:42:04Z | runs/docs-answerability/APPROVAL_RECORD-2.md |
| INV-4 / INV-5 exact words | 4 | yes (02b section 2) | approved | Gopal Patwa | 2026-10-10T05:13:28Z | runs/docs-answerability/APPROVAL_RECORD-4.md |
| 3b design: frontmatter, live probe (<=2 judge spawns), A-counts with mcp__ attempt, no probe agent, skill instead of command | 5 (follow-up) | yes (02c section 8) | approved | Gopal Patwa | 2026-10-10T05:42:01Z | runs/docs-answerability/APPROVAL_RECORD-7.md |
| Judge in a previously deterministic path | 5 | yes (02b section 3) | approved with 2 conditions: model pinned to full ID claude-haiku-5-5 (not alias); stop-and-ask unless a test shows a tool call refused | Gopal Patwa | 2026-10-10T05:13:28Z | runs/docs-answerability/APPROVAL_RECORD-5.md |

## Budget

- **Budget:** 950k tokens  ·  **Depth:** adversarial
- **Ceiling (owner-typed, APPROVAL_RECORD-1):** 1.4M
- **Spent:** 717k (75.5% of plan; 51.2% of ceiling), from usage.mjs  ·  **Remaining:** 233k
- **Next stage:** Seen-set check: 93 judge spawns, **STOP-AND-ASK** (budget basis; see Open stop)

Note: pass 1 ran 134k peak vs 80k est; the projection to the end is about 1.0M against the 950k plan, under the 1.4M ceiling. 950k is the confirmed plan total; 1.4M the owner's ceiling. The intent's own figure is about 700k (A 300k, B 400k); measured ratios give A 425k + B 510k. Units are peak context per spawn. Depth is adversarial only for Security; other stages standard (see plan).

## Open stop

INV-4/INV-5 words applied verbatim (a8c9604; test renamed on default, STANDING_INSTRUCTIONS #3). Spent now ~717k + Architect ~42k = ~759k (usage.mjs to be rerun).

Seen-set check cannot start under the budget rule. Plan estimate was 100k for this stage. The ledger sums peak context per spawn, and the probe judge peaked at 76k (the deferred-tool list the harness gives it, 141 tools) with 113k in-equiv. 93 one-question spawns (spec 5.2, thresholds fixed) are about 93 x 76k = ~7M peak-sum (~10M in-equiv), against 950k plan / 1.4M ceiling. Owner decision needed; nothing spawned.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| — | 0 | 2 | — | — |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|
| — | — | — | — | — |

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| Scope | sonnet-5-5 (harness log) | medium (declared) | 04:43 | 04:46 | 2:04 | 63k peak (457k processed) | 35 | 0 |
| Architecture pass 1 | opus-5-5 (harness log) | high (declared) | 04:49 | 05:02 | 12:55 | 134k peak (1.89M processed) | 38 | 0 |
| Architecture pass 2 | opus-5-5 (harness log) | high (declared) | 05:10 | 05:16 | 5:51 | 99k peak (1.04M processed) | 26 | 0 |
| Implementation 3a | sonnet-5-5 (harness log) | medium (declared) | 05:15 | 05:24 | 7:56 | 139k peak (3.19M processed) | 36 | 0 |
| Architecture addendum (3b) | opus-5-5 (harness log) | high (declared) | 05:33 | 05:40 | 6:13 | 77k peak (805k processed) | 26 | 0 |
| Implementation 3b | sonnet-5-5 (harness log) | medium (declared) | 06:05 | 06:08 | 1:39 | 47k peak (408k processed) | 13 | 0 |
| Refusal probe setup (QA pass A) | sonnet-5-5 (harness log) | high (declared) | 06:11 | 06:13 | 1:01 | 37k peak (307k processed) | 12 | 0 |
| Judge probe (spawn 1 of 2) | haiku-5-5 (harness log) | n/a | — | — | 0:11 | 76k peak | 5 (all refused) | 0 |
| Refusal probe audit (QA pass B) | sonnet-5-5 (harness log) | high (declared) | — | — | 1:40 | 46k peak | 11 | 0 |
| **Total** | | | | | | 717k | 202 | |

## Next action

Owner chose `lean` (typed, 2026-10-10): measurement only, no ceiling change, nothing approved. A new session with this worktree as project root and MCP servers off runs exactly 2 one-question judge spawns on seen-set questions (measurement-only, not seen-set verdicts; all 93 still run fresh later), runs usage.mjs, and reports per-spawn peak and in-equiv, the tool count the judge was offered, and a 93-spawn projection with a derived ceiling. Judge spawns for the refusal probe: 1 of 2 used, separate. This session spawns nothing further until the numbers come back and the owner decides the budget basis.
