# Slice State — docs-abstention

- **Ask:** Make retrieval able to say "the docs don't answer this": baseline a threshold/margin first, model only if it fails, fifth held-out set, two bars (intents/docs-abstention.md)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Closed: NOT RELEASABLE (runs/docs-abstention/07-close-out.md)
- **Status:** done
- **Least-privilege:** enforced — role subagents load from this repo's .claude/agents/ (session rooted in the worktree of this repo)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 3b07317211f22e38c0111cd2fd40e021710c8b5c (main; includes pack v15 commit 894881a)
- **Branch:** claude/docs-abstention-c835b1 (worktree of main at 0dfd433)
- **Started:** 2026-10-09T06:20:00Z  ·  **Updated:** 2026-10-09T06:25:00Z

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed 2026-10-08 (commit 523e7d1) | runs/docs-abstention/intent.md | human confirms plan |
| Intake | Orchestrator | done | runs/docs-abstention/00-slice-plan.md | owner confirmed 2026-10-09T06:32:12Z |
| Scope | Engineering Manager | done | runs/docs-abstention/01-scope.md | accept; clarifications C1-C10 and owner questions Q1-Q5 open |
| Baseline | QA Evidence | done | runs/docs-abstention/02-baseline.md | measurement only; no cell of any rule family meets the Q2 definition (see artefact section 5) |
| Architecture | Software Architect | done (sections 1-11 by the interrupted pass; section 12, 3.4 from support Reply 1, Appendix B and ADR 0007 fact table by the completion pass) | runs/docs-abstention/02-tech-spec.md; docs/adr/0007-answerability-judge.md (proposed) | owner's licence decision (ADR 0007), then rule 5 (8.4) and rule 4 INV-4/INV-5 (8.1, 8.2) approvals |
| Implementation | AI Engineer | done (4.1 condition failed, see artefact) | runs/docs-abstention/03-implementation.md | — |
| Freeze | Orchestrator | pending | — | method commit recorded |
| Label review | QA Evidence (fresh) | pending | — | — |
| Scoring | QA Evidence (fresh, different) | pending | — | both bars |
| Security | Security-Privacy (standard, per option 1 plan) | done: PASS with advisories (0 blockers, 0 required-fix, 4 advisories) | runs/docs-abstention/04-security-review.md | go to Release Gate |
| Release Gate | Release Manager | done: NO-GO, not releasable (bars never evaluated; model path stopped; stale-text pass needed before any merge) | runs/docs-abstention/06-release-checklist.md | tier 2 confirmed |
| Close-out | Post-Launch Learning | done | runs/docs-abstention/07-close-out.md | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Confirm intent and plan | plan confirmation | yes | approved | Gopal Patwa | 2026-10-09T06:32:12Z | runs/docs-abstention/APPROVAL_RECORD-1.md |
| Budget raise 650k to 780k | budget raise (owner only) | yes | approved | Gopal Patwa | 2026-10-09T16:45:05Z | runs/docs-abstention/APPROVAL_RECORD-3.md |
| Licence decision for qnli-electra-base (ADR 0007 option 1) | owner decision (precondition for rule 5) | yes | approved ("accept the model card's Apache-2.0") | Gopal Patwa | 2026-10-09T16:55:27Z | runs/docs-abstention/APPROVAL_RECORD-4.md |
| Rule 5: download/use qnli-electra-base @ c7dea87c | 5 | yes | approved | Gopal Patwa | 2026-10-09T17:05:20Z | runs/docs-abstention/APPROVAL_RECORD-5.md |
| Rule 4: INV-4 items 4-i and 4-ii | 4 | yes | approved | Gopal Patwa | 2026-10-09T17:05:20Z | runs/docs-abstention/APPROVAL_RECORD-5.md |
| Rule 4: INV-5 three-model change + A1 line | 4 | yes | approved | Gopal Patwa | 2026-10-09T17:05:20Z | runs/docs-abstention/APPROVAL_RECORD-5.md |
| Option 1: stop the model path, drop candidate code | owner decision | yes | approved | Gopal Patwa | 2026-10-09T17:49:16Z | runs/docs-abstention/APPROVAL_RECORD-6.md |
| (lapsed) rule 5 model + rule 4 INV-4 4-i/4-ii + INV-5 + A1 line from APPROVAL_RECORD-5 | 4, 5 | n/a | LAPSED, unused (owner chose option 1) | Gopal Patwa | 2026-10-09T17:49:16Z | runs/docs-abstention/APPROVAL_RECORD-6.md |
| Rule 4: INV-4 correction, spec 8.3 text | 4 | yes | approved | Gopal Patwa | 2026-10-09T17:50:52Z | runs/docs-abstention/APPROVAL_RECORD-7.md |
| Stale-text pass incl. .agentic/CURRENT_MVP_STATUS.md | owner approval (status-doc edit) | yes | approved | Gopal Patwa | 2026-10-09T20:41:46Z | runs/docs-abstention/APPROVAL_RECORD-8.md |
| Scope Q1-Q5 decisions (order, 90%/LOSO, abort rule, counts, INV-4 timing) | owner decision | yes | approved ("as recommended") | Gopal Patwa | 2026-10-09T06:45:47Z | runs/docs-abstention/APPROVAL_RECORD-2.md |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 780k tokens  ·  **Depth:** standard (Security adversarial)
- **Spent:** 672k (86.2%)  ·  **Remaining:** 108k
- **Next stage:** none (slice closed; owner decides next)

Note: raised from 650k to 780k by the owner at 2026-10-09T16:45:05Z (APPROVAL_RECORD-3.md); the owner set the total only, not a new A/B split. The earlier split text below describes the original 650k plan. The budget is split at the freeze, as peak context per spawn. Slice A (Scope, Baseline, Architecture, approvals, Implementation, freeze) is 330k, planned at 310k. Slice B (label review, scoring, Security, Release Gate, close-out) is 320k, planned at 310k. Only the owner can raise the budget.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| (none yet) | 0 | 2 | — | — |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|
| Architecture (software-architect) | usage limit (HTTP 429) near the end of the stage | infra | 02-tech-spec.md sections 1-11 plus ADR 0007 draft written; section 12 (model-path cost) and the STATE row missing | yes, by a fresh software-architect completion pass after the owner's budget raise (APPROVAL_RECORD-3); sections 1-11 kept as written |

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| Intake (Orchestrator) | — | — | 2026-10-09T06:20:00Z | 2026-10-09T06:25:00Z | — | — | — | 0 |
| Scope Review (engineering-manager) | sonnet-5-5 | declared: frontmatter default (medium) | — | 2026-10-09 | 2:00 | 232k processed (peak ctx 39k vs 50k est.) | 15 | 0 |
| Baseline (qa-evidence) | sonnet-5-5 | declared: frontmatter default | — | 2026-10-09 | 4:07 | 1.11M processed (peak ctx 82k vs 60k est.) | 22 | 0 |
| Architecture (software-architect), interrupted | opus-5-5 | declared: frontmatter default | — | 2026-10-09 | — | 1.70M processed (peak ctx 124k vs 70k est.) | 21 | 0 (infra interruption, not a retry) |
| Architecture completion (software-architect, fresh pass) | opus-5-5 | declared: frontmatter default | — | 2026-10-09 | 3:29 | 639k processed (peak ctx 63k vs 25k est.) | 26 | 0 (continues the infra interruption) |
| Implementation (ai-engineer) | sonnet-5-5 | declared: frontmatter default | — | 2026-10-09 | 21:44 | 3.15M processed (peak ctx 131k vs 130k est.) | 36 | 0 |
| Security Review (security-privacy, standard) | opus-5-5 | declared: frontmatter default | — | 2026-10-09 | 2:19 | 489k processed (peak ctx 48k vs 50k est.) | 18 | 0 |
| Release Gate (release-manager) | sonnet-5-5 | declared: frontmatter default | — | 2026-10-09 | 2:27 | 483k processed (peak ctx 63k vs 55k est.) | 26 | 0 |
| Stale-text pass (tech-writer) | sonnet-5-5 | declared: frontmatter default | — | 2026-10-09 | 0:56 | 179k processed (peak ctx 32k vs 30k est.) | 29 | 0 |
| ARCHITECTURE.md edit (software-architect) | opus-5-5 | declared: frontmatter default | — | 2026-10-09 | 1:13 | 236k processed (peak ctx 31k vs 25k est.) | 27 | 0 |
| Status-file edit (tech-writer, pack v17) | sonnet-5-5 | declared: frontmatter default | — | 2026-10-09 | 0:16 | 63k processed (peak ctx 18k vs 25k est.) | 9 | 0 |
| Close-out (post-launch-learning) | sonnet-5-5 | declared: frontmatter default | — | 2026-10-09 | 0:39 | 126k processed (peak ctx 41k vs 25k est.) | 11 | 0 |
| **Total** | | | | | | 8.40M processed (peak ctx sum 672k) | 240 | |

## Next action

None for the run. The owner reviews branch claude/docs-abstention-c835b1 (not pushed), reads 07-close-out.md, and decides on push/PR/merge and on the next abstention step. Nothing is approved for push, merge, PR, deploy or announcement.

## Advice received (not approvals)

- 2026-10-09, from the "Aveto AI SDLC" session (advice only): recommends Q1 yes, Q2 90% seen + 80% leave-one-set-out, Q3 as C7, Q4 yes (surplus 24+24 plus 6 reserves, hard negatives tagged), Q5 decide at the rule 4 approval. Claims the default path never abstains (search.py, ADR 0004, LOCAL_COMMANDS.md) and that README line 50 and CURRENT_MVP_STATUS line 12 are stale. The owner has not yet answered Q1-Q5 in this session.
- 2026-10-09, from the "Aveto AI SDLC" session (advice only, sent while Baseline was still running; its claim about the baseline result is unverified until the Baseline agent reports): for Architecture, weigh (a) the already-pinned reranker as answerability judge (no new download, but a relevance score is not an answerability score, and the MS MARCO licence question would become a default-path dependency) against (b) one purpose-built model (rule 5 + INV-5 + ADR first), judged on general grounds with seen-set numbers only confirming; and fix INV-4's stale "or 'no confident match'" wording in the same rule 4 request. Not an instruction from the owner; the Architect may weigh it.
- 2026-10-09, from the "Aveto AI SDLC" session (advice only): after reading 03-confirm-retrieval.txt and -heldout.txt, says the spec 4.1 condition (pooled Bar 1 >= 16/20) cannot be met. Orchestrator check against the raw files: dev set 1/6 and second set 1/6 abstained, 2/12 so far; with 8 unanswerable questions left (heldout-3 and heldout-4, 4 each) the pooled maximum is 10/20 < 16. Confirmed arithmetically. A4 (still running) was told to stop and report on a failed 4.1 criterion; the owner decides what happens next.

## Failed condition (spec 4.1) and crash occurrence

- Seen-set confirmation at the candidate code, rule fixed at judge p >= 0.5, nothing tuned: pooled Bar 1 = 2/20 (required >= 16/20), Bar 2 = 55/56 (required >= 45/56). Per set Bar 1: 1/6, 1/6, 0/4, 0/4. Raw: runs/docs-abstention/03-confirm-<set>.txt and 03-implementation.md. The method is NOT frozen and there is no method commit.
- **Open crash item:** `eval` on retrieval-heldout-3 exited **134** (libc++abi recursive_mutex lock failed) AFTER its full report printed, on the default `file-rrf-v1` path with the judge loaded. Recorded, not retried. This is the exit-134 class slice 4 could not reproduce (0 in 660 runs); this is a new occurrence and is filed against that open item. Whether the judge session (a third ONNX session) is implicated is unknown.
- The candidate code (10 files) is committed on this branch as a candidate, not as the method commit.

## Option 1 plan (owner, APPROVAL_RECORD-6)

Stages run: INV-4 correction via rule 4 (spec 8.3 text), Security Review (standard: a text change to a safety control plus a revert; no new code or download path), Release Gate (verdict: not releasable, with the reason), Close-out. Stages NOT run, with reason: Freeze (no method), Label review and Scoring (no frozen method to score; the fifth set stays unspent and unread), Implementation rework. Candidate code reverted (479f82a reverted); ADR 0007 to be marked rejected; the local models/ cache of the judge files (gitignored) is left in place.

## Process note: Security depth

The intent asked for Security at adversarial depth for any new download path and for INV-4. After the model path was stopped (APPROVAL_RECORD-6) the Orchestrator ran Security at **standard** depth, scoped to the INV-4 text change and the revert, and said so to the owner before the owner approved the 8.3 text. No approval record names the downgrade. It is recorded here and in the close-out as an Orchestrator decision the owner can overturn; the review found the net product diff empty.
- 2026-10-09, from the "Aveto AI SDLC" session (advice only): Request 1 (no role owns .agentic/CURRENT_MVP_STATUS.md) is a confirmed pack defect, fixed upstream in pack v17 (playbook commit bb7dcd0, local, not pushed): Tech Writer and Post-Launch Learning may write that one file. It offers: (A) upgrade this worktree's pack to v17 in a separate commit after the playbook is pushed, then re-spawn the Tech Writer for the file; (B) the Orchestrator makes the single approved edit under record 8. It recommends A. Reply 2 is in SUPPORT_REPLIES.md. Owner has not decided.
