# Slice State — docs-retrieval

- **Ask:** Retrieval only, no model: return the passages in Aveto's pinned docs that answer a question, with exact provenance (see intent.md)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Scope Review done — split into `docs-retrieval-core` and `docs-retrieval-ci`; next is Architecture (docs-retrieval-core)
- **Status:** blocked-on-approval
- **Least-privilege:** enforced — role subagents are discoverable from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 70c095d (absolute; relative path does not resolve from a worktree)
- **Started:** 2026-09-27T02:29:54Z  ·  **Updated:** 2026-09-29T07:17:38Z

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
| Architecture | software-architect | done; retry 1 revision (variant v2) written 2026-09-29, pre-registered before run; embed-v3 spec-only variant added 2026-09-29, finished with verified facts after owner chose to pursue it in this slice; approvals 2–4 granted; ADR 0003 written (accepted, implementation pending); docs/ARCHITECTURE.md updated for embed-v3 | runs/docs-retrieval/02-tech-spec.md ("Retrieval — variant v2"); docs/adr/0001-python-fastapi-uv-no-agent-framework.md; docs/adr/0002-lexical-retrieval-calibrated-abstention.md; docs/ARCHITECTURE.md | tech spec ready; 18 files flagged vs ≤10 rule (justified in spec) |
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
- **Spent:** 571k (51%)  ·  **Remaining:** 559k
- **Next stage:** Implementation of embed-v3 (backend-architect, build) est. 195k → **STOP-AND-ASK** — waiting on the owner to amend intent.md on main (spec order step 1); otherwise 571k + 195k = 766k ≤ 1130k

Budget set to 1,130k by the owner ("Set 1,130k", 2026-09-29T05:28:14Z) for one slice with embed-v3 (EM projection ≈1,067–1,127k, incl. 60k re-run reserve). Earlier: raised from 690k to 820k on the owner's choice of option A in ESCALATION-1.md ("A, and I'll write the fresh questions"), covering one retry (≈818k projected); this is the owner's decision, not a fit-to-spend. The 690k was docs-retrieval-core's proposed budget (Σ560k, 5 stages, +130k headroom), accepted by the owner.
Note: docs-retrieval-ci is proposed at another 690k (Σ560k + 130k). With Scope Review, the split totals 1,220k vs the original single-slice 890k. The owner decides.
Spent is the harness's `subagent_tokens` (peak context, per RUN_ECONOMICS §1; a resumed agent's figure is cumulative, not additive): Scope Review 55,125 + EM (amendment, then file-count ruling) 33,715 + Architecture (incl. INV-4/5 follow-up) 131,797 + Implementation 107,180 = 327,817; after the v2 revision the Architect's cumulative figure is 186,421 (was 131,797), so total 382,441; after the embed-v3 design the Architect's cumulative figure is 225,583, total 421,603; after the embed-v3 fact-fill the Architect's cumulative figure is 275,625, so total ≈471,645; the EM's cumulative figure is then 72,097 (was 33,715), so total 510,027. QA off-topic list 44,781 → 554,808; after ADR 0003 the Architect's cumulative figure is 292,142 (was 275,625), so total 571,325.
The installed guard checks spent ≥ budget only; spent + estimate is checked by hand before each spawn.
Every stage handoff must tell the role: keep Status to one of the four SLICE_STATE values, keep the Budget / Spent / Next stage lines in their exact format, and put reasons and per-slice figures in a note beneath (pack v9 rule; installed pack is v6 + 677c1e1). Reinstall v9+ only after the slice lands.

### Frozen inputs

- **evals/calibration-offtopic.toml** — 59 QA-authored questions, frozen 2026-09-29T05:32:03Z at commit `fa3673ad75278003516a570639a39cdc616444e2`, **sha256 `9045189567b083c83c02336a4f70990c8a8e3ce3e49d5917642fbad6e293627c`**. Not read by the Architect or the engineer; loaded by path only. Overlap with the owner's held-out set is unchecked (not in the repo) and is the owner's to check. QA agent run (44,781 tokens; models seen in transcript: 26 "model":"claude-sonnet-5-5"; frontmatter sonnet/high).

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
| Scope Review (engineering-manager) | sonnet-5 | medium (declared) | 2026-09-27T20:59:31Z | 2026-09-27T21:03:39Z | 4:08 | 55,125 | 18 | 0 |
| EM: scope amendment, file-count ruling, embed-v3 re-scope (resumed twice; cumulative) | sonnet-5-5 | medium (declared) | — | — | — | 72,097 | 31 | 0 |
| Architecture (software-architect) + INV-4/5 follow-up | opus-5-5 | high (declared) | — | — | 13:36 | 131,797 | 44 | 0 |
| Implementation (backend-architect) | sonnet-5-5 | medium (declared) | — | — | 6:16 | 107,180 | 28 | 0 |
| Architecture v2 revision (resumed, retry 1) | opus-5-5 | high (declared) | — | — | 6:24 | +54,624 | +35 | 1 |
| Architecture embed-v3 spec-only design (resumed) | opus-5-5 | high (declared) | — | — | 5:40 | +39,162 | +14 | 1 |
| Architecture embed-v3 fact-fill (resumed) | opus-5-5 | high (declared) | — | — | 4:49 | +50,042 | +39 | 1 |
| Architecture ADR 0003 + ARCHITECTURE.md (resumed) | opus-5-5 | high (declared) | — | — | 1:30 | +16,517 | +11 | 1 |
| QA Evidence: frozen off-topic list (qa-evidence) | sonnet-5-5 | high (declared) | — | — | 2:30 | 44,781 | 15 | 0 |
| **Total** | | | | | | 571,325 | 235 | |

Measured usage (2026-09-29T07:17:38Z, `usage.mjs . --slice docs-retrieval`, harness-logged models; no role marked `*`, so tool restrictions bound): 5/5 stages measured, 156 requests, cache hit 92.3%. **Processed 19.46M tokens (cost-weighted 4.73M)**, of which software-architect 15.60M (84 requests, opus-5-5, peak context 128k), backend-architect 2.14M, engineering-manager 1.26M, qa-evidence 0.45M. The report's peak-context total is 363k; the Tokens column above (571k) is the sum of the harness's per-spawn `subagent_tokens`, kept as the more conservative figure for the budget. **The budget is in peak-context units; what the slice actually consumed from usage limits is the processed figure, roughly 34× larger.** Models above are copied from the report; effort is not in the log, so it is the declared frontmatter value.

Correction (2026-09-29T05:28:36Z): the Architecture rows above were first recorded as sonnet/medium from memory. The role's frontmatter is `model: opus, effort: high` and its harness transcript has 202 turns, all claude-opus-5-5 (reported by the playbook session and re-checked here against .claude/agents/software-architect.md and the subagent transcript). Token figures are unaffected (harness-reported). Exact ids seen in transcripts: Scope Review claude-sonnet-5; later Engineering Manager and Implementation runs claude-sonnet-5-5. Effort is the declared frontmatter value; it is not measurable from the transcript. After the slice, `node <playbook>/execution/usage.mjs --write` should replace these self-reported figures.

## Next action

Still BLOCKED before Implementation: the owner's amended intent.md is only an uncommitted draft in the main checkout (banner: DRAFT, not yet confirmed). Owner answered the open Stakes question (verbatim "Don't tick it; stay on the short path"). Owner to remove the draft banner, resolve the Open questions bullet, and commit intent.md on main (suggested text: INTENT_AMENDMENT_PROPOSAL.md, "To finalise"). Then: merge main, re-copy the intent to runs/docs-retrieval/intent.md, backend-architect implements embed-v3 and STOPS before any eval run; QA generates tests/fixtures/wordpiece_golden.json; record the frozen commit SHA; owner commits the held-out set; run once via --eval-file.
