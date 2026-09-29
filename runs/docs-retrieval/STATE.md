# Slice State — docs-retrieval

- **Ask:** Retrieval only, no model: return the passages in Aveto's pinned docs that answer a question, with exact provenance (see intent.md)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Scope Review done — split into `docs-retrieval-core` and `docs-retrieval-ci`; next is Architecture (docs-retrieval-core)
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents are discoverable from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 70c095d (absolute; relative path does not resolve from a worktree)
- **Started:** 2026-09-27T02:29:54Z  ·  **Updated:** 2026-09-29T01:32:19Z

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
| Architecture | software-architect | done; retry 1 revision (variant v2) written 2026-09-29, pre-registered before run | runs/docs-retrieval/02-tech-spec.md ("Retrieval — variant v2"); docs/adr/0001-python-fastapi-uv-no-agent-framework.md; docs/adr/0002-lexical-retrieval-calibrated-abstention.md; docs/ARCHITECTURE.md | tech spec ready; 18 files flagged vs ≤10 rule (justified in spec) |
| Implementation | backend-architect | blocked-on-failure — built and green; eval run 1 missed the bar (answerable 2/24, unanswerable 6/6) | runs/docs-retrieval/eval-run-1.txt | eval gate FAILED; retry 1 of 2 goes to Architect |
| QA Evidence | qa-evidence | pending | — | — |
| Security Review | security-privacy | pending | — | — |
| Release Gate | release-manager | pending | — | — |

### docs-retrieval-ci (sequenced after docs-retrieval-core's Release Gate)

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Implementation | backend-architect | pending — blocked on docs-retrieval-core's Release Gate | — | — |
| QA Evidence | qa-evidence | pending | — | — |
| Security Review | security-privacy | pending | — | — |
| Release Gate | release-manager | pending | — | — |
| Post-Launch | post-launch-learning | pending (smoke) | — | — |

## Approvals

Plan confirmation (not a rule approval): Gopal Patwa, 2026-09-27T20:59:31Z, verbatim: "plan is approved".
Approval 1 APPROVED by Gopal Patwa, 2026-09-29T00:02:48Z (APPROVAL_RECORD-1.md), verbatim "Approve". Split accepted with the ≥80% bar moved into core (verbatim "Accept split + ≥80% in core (Recommended)").

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Read-only fetch of pinned playbook docs in ingest + CI | 5 | yes | APPROVED | Gopal Patwa | 2026-09-29T00:02:48Z | runs/docs-retrieval/APPROVAL_RECORD-1.md |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 820k tokens  ·  **Depth:** standard
- **Spent:** 382k (47%)  ·  **Remaining:** 438k
- **Next stage:** Architecture, embeddings variant (spec-only, retry-1 continuation, review) est. 100k → **PROCEED** (382k + 100k = 482k ≤ 820k). Later stages project to ≈910k, over 820k: ask the owner before Implementation.

Budget raised from 690k to 820k on the owner's choice of option A in ESCALATION-1.md ("A, and I'll write the fresh questions"), covering one retry (≈818k projected); this is the owner's decision, not a fit-to-spend. The 690k was docs-retrieval-core's proposed budget (Σ560k, 5 stages, +130k headroom), accepted by the owner.
Note: docs-retrieval-ci is proposed at another 690k (Σ560k + 130k). With Scope Review, the split totals 1,220k vs the original single-slice 890k. The owner decides.
Spent is the harness's `subagent_tokens` (peak context, per RUN_ECONOMICS §1; a resumed agent's figure is cumulative, not additive): Scope Review 55,125 + EM (amendment, then file-count ruling) 33,715 + Architecture (incl. INV-4/5 follow-up) 131,797 + Implementation 107,180 = 327,817; after the v2 revision the Architect's cumulative figure is 186,421 (was 131,797), so total 382,441.
The installed guard checks spent ≥ budget only; spent + estimate is checked by hand before each spawn.
Every stage handoff must tell the role: keep Status to one of the four SLICE_STATE values, keep the Budget / Spent / Next stage lines in their exact format, and put reasons and per-slice figures in a note beneath (pack v9 rule; installed pack is v6 + 677c1e1). Reinstall v9+ only after the slice lands.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| Implementation (eval gate) | 1 of 2 (Architect ranking revision, started 2026-09-29T00:41:49Z) | 2 | gate-violation | eval run 1: answerable 2/24 (need 20); ungated recall@5 14/24. See ESCALATION-1.md |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| Scope Review | sonnet | medium | 2026-09-27T20:59:31Z | 2026-09-27T21:03:39Z | 4:08 | 55,125 | 18 | 0 |
| Scope amendment + file-count ruling (EM, resumed once) | sonnet | medium | — | — | — | 33,715 | 20 | 0 |
| Architecture (resumed once for INV-4/5) | sonnet | medium | — | — | 13:36 | 131,797 | 44 | 0 |
| Implementation | sonnet | medium | — | — | 6:16 | 107,180 | 28 | 0 |
| Architecture v2 revision (retry 1; same resumed agent, cumulative) | sonnet | medium | — | — | 6:24 | +54,624 | +35 | 1 |
| **Total** | | | | | | 382,441 | 158 | |

## Next action

Architect writes a SPEC-ONLY embeddings variant (embed-v3) with concrete approval-ready facts. No code, no dependency added, nothing approved. Then the Orchestrator writes the specific approval requests (rule 5; INV-5 = rule 4; intent 'no model' amendment) and asks the owner, plus the budget decision.
