# Slice State — docs-retrieval

- **Ask:** Retrieval only, no model: return the passages in Aveto's pinned docs that answer a question, with exact provenance (see intent.md)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Scope Review done — split into `docs-retrieval-core` and `docs-retrieval-ci`; next is Architecture (docs-retrieval-core)
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents are discoverable from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 70c095d (absolute; relative path does not resolve from a worktree)
- **Started:** 2026-09-27T02:29:54Z  ·  **Updated:** 2026-09-29T05:28:14Z

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
| Architecture | software-architect | done; retry 1 revision (variant v2) written 2026-09-29, pre-registered before run; embed-v3 spec-only variant added 2026-09-29, finished with verified facts after owner chose to pursue it in this slice (NO gated approval; not implemented) | runs/docs-retrieval/02-tech-spec.md ("Retrieval — variant v2"); docs/adr/0001-python-fastapi-uv-no-agent-framework.md; docs/adr/0002-lexical-retrieval-calibrated-abstention.md; docs/ARCHITECTURE.md | tech spec ready; 18 files flagged vs ≤10 rule (justified in spec) |
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
| Local embedding model in retrieval (embed-v3) + onnxruntime/numpy | 5 | yes | APPROVED | Gopal Patwa | 2026-09-29T05:28:14Z | runs/docs-retrieval/APPROVAL_RECORD-2.md |
| Weights download (huggingface.co + *.hf.co, sha256-pinned) in ingest and CI | 5 | yes | APPROVED | Gopal Patwa | 2026-09-29T05:28:14Z | runs/docs-retrieval/APPROVAL_RECORD-3.md |
| Amend INV-5 and INV-4 wording | 4 | yes | APPROVED | Gopal Patwa | 2026-09-29T05:28:14Z | runs/docs-retrieval/APPROVAL_RECORD-4.md |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 1130k tokens  ·  **Depth:** standard
- **Spent:** 510k (45%)  ·  **Remaining:** 620k
- **Next stage:** QA, write the frozen off-topic calibration list (evals/calibration-offtopic.toml; build) est. 40k → **PROCEED** (510k + 40k = 550k ≤ 1130k); then Implementation est. 195k

Budget set to 1,130k by the owner ("Set 1,130k", 2026-09-29T05:28:14Z) for one slice with embed-v3 (EM projection ≈1,067–1,127k, incl. 60k re-run reserve). Earlier: raised from 690k to 820k on the owner's choice of option A in ESCALATION-1.md ("A, and I'll write the fresh questions"), covering one retry (≈818k projected); this is the owner's decision, not a fit-to-spend. The 690k was docs-retrieval-core's proposed budget (Σ560k, 5 stages, +130k headroom), accepted by the owner.
Note: docs-retrieval-ci is proposed at another 690k (Σ560k + 130k). With Scope Review, the split totals 1,220k vs the original single-slice 890k. The owner decides.
Spent is the harness's `subagent_tokens` (peak context, per RUN_ECONOMICS §1; a resumed agent's figure is cumulative, not additive): Scope Review 55,125 + EM (amendment, then file-count ruling) 33,715 + Architecture (incl. INV-4/5 follow-up) 131,797 + Implementation 107,180 = 327,817; after the v2 revision the Architect's cumulative figure is 186,421 (was 131,797), so total 382,441; after the embed-v3 design the Architect's cumulative figure is 225,583, total 421,603; after the embed-v3 fact-fill the Architect's cumulative figure is 275,625, so total ≈471,645; the EM's cumulative figure is then 72,097 (was 33,715), so total 510,027.
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
| Architecture (resumed once for INV-4/5) | opus | high | — | — | 13:36 | 131,797 | 44 | 0 |
| Implementation | sonnet | medium | — | — | 6:16 | 107,180 | 28 | 0 |
| Architecture v2 revision (retry 1; same resumed agent, cumulative) | opus | high | — | — | 6:24 | +54,624 | +35 | 1 |
| Architecture embed-v3 spec-only design (same resumed agent, cumulative) | opus | high | — | — | 5:40 | +39,162 | +14 | 1 |
| **Total** | | | | | | 421,603 | 172 | |

Correction (2026-09-29T05:28:36Z): the Architecture rows above were first recorded as sonnet/medium from memory. The role's frontmatter is `model: opus, effort: high` and its harness transcript has 202 turns, all claude-opus-5-5 (reported by the playbook session and re-checked here against .claude/agents/software-architect.md and the subagent transcript). Token figures are unaffected (harness-reported). Exact ids seen in transcripts: Scope Review claude-sonnet-5; later Engineering Manager and Implementation runs claude-sonnet-5-5. Effort is the declared frontmatter value; it is not measurable from the transcript. After the slice, `node <playbook>/execution/usage.mjs --write` should replace these self-reported figures.

## Next action

Approvals 2, 3, 4 approved and the budget set to 1,130k. 1) QA writes evals/calibration-offtopic.toml (50+ fluent off-topic questions; frozen with its sha256 in STATE.md before Implementation). 2) backend-architect implements embed-v3 per 02-tech-spec.md, then STOP before any eval run. 3) QA generates tests/fixtures/wordpiece_golden.json. 4) Record the frozen commit SHA; owner commits the held-out set after it; run once via --eval-file. Owner still to amend intent.md on main (INTENT_AMENDMENT_PROPOSAL.md) before QA/Release Gate.
