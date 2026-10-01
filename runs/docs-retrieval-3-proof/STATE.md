# Slice State — docs-retrieval-3-proof

- **Ask:** Score slice 3's frozen reranker method once on a fourth held-out set (slice B of docs-retrieval-3)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Scoring done — GATE PASSED 13/16; awaiting the owner's budget decision for Security, Release Gate, Post-Launch
- **Status:** blocked-on-approval
- **Least-privilege:** enforced — role subagents load from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 383058a
- **Started:** 2026-10-01T06:55:00Z  ·  **Updated:** 2026-10-01T06:55:00Z

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed | runs/docs-retrieval-3-proof/intent.md | human confirmed |
| Intake | Orchestrator | done | runs/docs-retrieval-3-proof/00-slice-plan.md | owner directed slice B at the freeze |
| Label review | qa-evidence (fresh #1) | done | runs/docs-retrieval-3-proof/01-label-review.md (reviewed set: retrieval-heldout-4.reviewed.toml) | labels reviewed before the owner commits the set |
| Owner commits reviewed set | Human | done: main 431486e, evals/retrieval-heldout-4.toml (sha256 180cfc0b…8aee), merged here at 0be91a4 | evals/retrieval-heldout-4.toml | git order: freeze 8499c2a before the set |
| Scoring | qa-evidence (different fresh spawn) | done: PASS 13/16 (81.2%), run once | runs/docs-retrieval-3-proof/02-qa-result.md | >= 13 of 16 answerable, once |
| Security Review | security-privacy | pending (only if the gate passes) | — | — |
| Release Gate | release-manager | pending (only if the gate passes) | — | — |
| Post-Launch | post-launch-learning | pending | — | — |

## Approvals

Slice A's approvals (A1 rule 5, A2 rule 4) cover this pair: `runs/docs-retrieval-3/APPROVAL_RECORD-1.md`, `-2.md`. Nothing wider.

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| (none new) | | | | | | |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 240k tokens  ·  **Depth:** standard
- **Spent:** 143k (60%)  ·  **Remaining:** 97k
- **Next stage:** Security Review (security-privacy) est. 60k → **STOP-AND-ASK**

Note (Orchestrator): scoring peaked at 38k (est. 90k). Remaining stages (Security 60k, Release Gate 60k, Post-Launch 60k = 180k at the plan's estimates, or ~120k if the Release/Post-Launch estimates are lean) exceed the 97k remaining: stop and ask the owner with the numbers, as he directed.

Note: label review peaked at 106k vs a 60k estimate. Scoring (90k) fits (196k of 240k); if the gate passes, Security, Release and Post-Launch (est. 120k) would overrun by about 76k: stop and ask the owner with the numbers then.

Note: owner set A 360k / B 240k (total 600k). Plan estimates total 270k; if B runs short, stop and ask the owner with the numbers. Units are peak context per spawn.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| (none) | 0 | 2 | — | — |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|
| (none) | | | | |

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| Label review (qa-evidence #1) | sonnet-5-5 | declared: frontmatter default | 2026-10-01T06:56:00Z | 2026-10-01T07:01:00Z | 4:16 | 2.07M processed (peak ctx 105k) | 35 | 0 |
| Scoring (qa-evidence #2) | sonnet-5-5 | declared: frontmatter default | 2026-10-01T07:20:00Z | 2026-10-01T07:25:00Z | 5:12 | 275k processed (peak ctx 38k) | 16 | 0 |
| **Total** | | | | | | 0 | 0 | |

## Next action

Owner decides how to spend the remaining 97k on Security Review, Release Gate (which blocks on the MS MARCO licence question) and Post-Launch. Then spawn each as a fresh spawn.
