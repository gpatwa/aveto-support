# Slice State — docs-answerability

- **Ask:** intents/docs-answerability.md — a judge step in the operator's own Claude Code session decides whether the shown passages answer the question.
- **Project pack:** ai-agent-product
- **Release tier:** 2
- **Current stage:** Close-out done
- **Status:** closed-not-releasable (seen-set check FAILED Bar 2, 44/56 vs 45/56; owner accepted as registered; see Update 4 and 07-close-out.md)
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
| Seen-set check | QA Evidence | done, FAILED Bar 2 44/56 (Bar 1 20/20 met) | runs/docs-answerability/04-seen-set-check.md | pooled >= 16/20 and 45/56: not met |
| Freeze | Orchestrator | not started (owner decision) | — | — |
| Label review | QA Evidence | not started (owner decision) | — | — |
| Scoring | QA Evidence | not started (owner decision) | — | — |
| Security (adversarial) | Security & Privacy | not started (owner decision) | — | — |
| Release Gate | QA / Release Manager | not started (owner decision) | — | — |
| Docs | Tech Writer | not started (owner decision) | — | — |
| Close-out | Post-Launch Learning | done | runs/docs-answerability/07-close-out.md; runs/docs-answerability/trace.json | — |

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
- **Spent:** about 2.5M peak-sum (717k from usage.mjs + about 1.76M by transcript for forked judge spawns not listed by usage.mjs; plan 950k, ceiling 2.6M)  ·  **Remaining:** none (about 100k under the 2.6M ceiling)
- **Next stage:** none (slice closed not releasable)

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

**Next action: none; owner decides anything further.** Closed not releasable; the branch must not be merged as a release. (The text below is history and is stale.)

APPROVAL_RECORD-8 (owner, typed): `mcp__*` appended to the judge's `disallowedTools` (applied, plus the same token in `tests/test_judge_artefacts.py`; 267 passed, ruff and mypy clean); ceiling now **2.6M peak-sum** (replaces 1.4M); probe respawn (judge spawn 2 of 2) and then the 93-spawn seen-set check approved.

**Blocked on a reload, not on the owner:** the session still holds the old agent definition (its Agent-tool listing for `aveto-answerability-judge` lacks `mcp__*`). A spawn now would likely offer 141 tools and burn spawn 2 of 2. After the session reloads agents: (1) confirm the listing shows `mcp__*`; (2) QA pass A recreates `probe-canary/` (new token) and checks `probe-prompt.txt` sha256 0615e164...; (3) one judge spawn, then check `prefix.json` `toolNames` is 7 harness tools; (4) QA pass B audits and writes `03b-refusal-probe-2.md`; (5) seen-set check per spec 5 / addendum 7.4. Projection 2.44M peak-sum vs ceiling 2.6M: margin about 160k (6%); stop and ask above 2.6M.

## Update (seen-set check, driven by Orchestrator top-level session)

- Probe 2 (judge spawn 2 of 2): PASS on 3.3 criteria 1-5 as written, outcome A everywhere; prefix.json shows 7 harness tools, no mcp__ (03b-refusal-probe-2.md). No live hook refusal this time (only probe 1's, on the older definition); the 7 harness tools are offered and not exercised.
- Spent per usage.mjs before the check: 849k of 2.6M. Preparer done (seen-check/batch-1..6.txt, key/key.toml; 93 = 20 unanswerable + 73 answerable, matches).
- Batch 1: r001 JUDGE_ERROR (the judge wrote `NOT_ANSWERABLE:` with a colon; grammar 4.1 step 4 rejects it; counts as failure on both bars, as registered). r002 ANSWERABLE (exit 0). r003 INVALID: the driver's spawn prompt was truncated (driver copy error), so batch 1 is void and must be rerun with a fresh driver (spec 5.3: rerun once, then stop).
- **Stopped at r003, nothing further spawned.** Why: the contract needs a model to retype each ~4-5k-token payload verbatim into the Agent call, and that failed on the third question. Continuing would void batches and spend the rerun allowance. Owner decision needed on how to drive the remaining 91 spawns (see the reply).

## Update 2 (SI-2: Reply 5 D1-D8 adopted; forked driver built and tested once)
- Built `.claude/skills/aveto-judge-seen/` (03d-seen-driver.md; 287 passed; largest payload r072 20,674 chars < ~30k inline ceiling). First live use (r001, batch 1 rerun, attempt 1 moved to *-attempt1-VOID): the judge received the payload plus a 150-char harness prefix `Base directory for this skill: <path>\n\n` (payload itself byte-identical, ends the prompt). Spec 5.4 freezes the payload layout and says a change after the first verdict is a new pre-registration for the owner; spec 5.2 says "verbatim, no labels". **Stopped (D8 / 5.4); nothing else spawned.** r001 reran: judge again wrote `NOT_ANSWERABLE:` (colon) = JUDGE_ERROR if scored; r001 result not yet applied/recorded.

## Update 3 (re-registered run, APPROVAL_RECORD-9; grammar accepts optional colon, 03e-grammar-change.md, 304 passed)
- Check run once from r001 via skill aveto-judge-seen (prefix 150 chars registered). Ledger: seen-check/ledger-run1.md. Earlier attempts moved to seen-check/discarded/.
- r001-r012 done: 6 ANSWERABLE, 4 NOT_ANSWERABLE (r001 r005 r006 r011), 2 JUDGE_ERROR (r010, r012: multi-line replies). The colon fix worked (r002 r003 r004 r008 colon forms parsed). **Stopped under D6** (anomaly: judge errors); the driver should have stopped at r010. r013-r093 not run. Judge transcripts not yet audited. Spend about 1.0M (usage.mjs to rerun) of 2.6M.

## Update 4 (seen-set check result; APPROVAL_RECORD-10 grammar: last non-empty line)
- Ran once, r001-r093, all audited (04-seen-set-check.md): **pooled Bar 1 20/20 MET; pooled Bar 2 44/56, NOT MET (needs 45)**. Denominators exactly 20 and 56, so valid. Per set Bar 2: retrieval 13/19, heldout 11/12, heldout-3 9/11, heldout-4 11/14. One JUDGE_ERROR under the final grammar: r093 (a trailing "Note:" paragraph). 11 other Bar 2 misses are NOT_ANSWERABLE verdicts on answerable questions. Audit: 93 transcripts, zero tool_use, all claude-haiku-5-5, 150-char prefix, payload hashes match. Colon rule rescued 20 rows, last-line rule 5 (r010, r012 observed; r046, r051, r077 inferred).
- Per spec 5.4: **stopped before the fifth set; owner decides.** No retuning, no second prompt, no larger model, nothing proposed. Slice stays blocked; Freeze, Label review, Scoring, Security, Release Gate, Docs, Close-out not started.
- Spend by transcript peak-sum: about 2.5M of the 2.6M ceiling (usage.mjs does not list the forked judge spawns). Any further stage needs the owner to set the ceiling.
- Disclosures: both re-registrations came after seeing failures on these same sets; driver was not a fresh context; driver deviations listed at the end of seen-check/ledger-run1.md; the scorer noted the ledger's discarded-attempt counts (4 and 2) do not match the directory (3 and 1) and its batch-complete labels do not match the batch files.
