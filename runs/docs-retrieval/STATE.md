# Slice State — docs-retrieval

- **Ask:** Retrieval only, no model: return the passages in Aveto's pinned docs that answer a question, with exact provenance (see intent.md)
- **Project pack:** ai-agent-product
- **Release tier:** 2 (proposed; Release Manager confirms)
- **Current stage:** Closed — held-out gate failed; nothing ships (see 08-close-out.md)
- **Status:** done
- **Least-privilege:** enforced — role subagents are discoverable from this repo's .claude/agents/ (worktree of aveto-support)
- **Telemetry:** self-reported
- **Playbook:** /Users/gopalpatwa/opt/agentic-sdlc-playbook @ 70c095d (absolute; relative path does not resolve from a worktree)
- **Started:** 2026-09-27T02:29:54Z  ·  **Updated:** 2026-09-29T16:21:53Z

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
| Implementation | backend-architect | done — embed-v3 (with v2 lexical) built, uncommitted; golden-fixture test expected-failing until QA lands it; no eval run | runs/docs-retrieval/04-implementation.md | typecheck, lint, 118 default tests, -m model and -m network green except the golden test; ingest x3 byte-identical |
| QA Evidence | qa-evidence | held-out scored once 2026-09-29: answerable 5/17 FAIL, unanswerable 5/6 PASS; dev diagnostic 10/24 and 4/6 | runs/docs-retrieval/06-qa-heldout-result.md; eval-run-2-heldout.txt; eval-run-3-dev-diagnostic.txt ; reference-embedding check: product matches reference, no embedding bug (07-qa-reference-embeddings.md) | eval gate FAILED (held-out answerable) |
| Security Review | security-privacy | not run — held-out gate failed; a failed gate sends the slice back, never forward | — | — |
| Release Gate | release-manager | not run — held-out gate failed | — | — |

### docs-retrieval-ci (sequenced after docs-retrieval-core's Release Gate)

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Implementation | backend-architect | not started — core's gate failed; blocked on a passing core Release Gate | — | — |
| QA Evidence | qa-evidence | not started | — | — |
| Security Review | security-privacy | not started | — | — |
| Release Gate | release-manager | not started | — | — |
| Post-Launch | post-launch-learning | done for the whole run (08-close-out.md) | — | — |

## Approvals

Plan confirmation (not a rule approval): Gopal Patwa, 2026-09-27T20:59:31Z, verbatim: "plan is approved".
Approval 1 APPROVED by Gopal Patwa, 2026-09-29T00:02:48Z (APPROVAL_RECORD-1.md), verbatim "Approve". Split accepted with the ≥80% bar moved into core (verbatim "Accept split + ≥80% in core (Recommended)").

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Read-only fetch of pinned playbook docs in ingest + CI | 5 | yes | APPROVED | Gopal Patwa | 2026-09-29T00:02:48Z | runs/docs-retrieval/APPROVAL_RECORD-1.md |
| Local embedding model in retrieval (embed-v3) + onnxruntime/numpy | 5 | yes | APPROVED | Gopal Patwa | 2026-09-29T05:28:14Z | runs/docs-retrieval/APPROVAL_RECORD-2.md |
| Weights download (huggingface.co + *.hf.co, sha256-pinned) in ingest and CI | 5 | yes | APPROVED | Gopal Patwa | 2026-09-29T05:28:14Z | runs/docs-retrieval/APPROVAL_RECORD-3.md |
| Amend INV-5 and INV-4 wording | 4 | yes | APPROVED | Gopal Patwa | 2026-09-29T05:28:14Z | runs/docs-retrieval/APPROVAL_RECORD-4.md |
| One-off throwaway `tokenizers` install (PyPI, pinned, outside the project) to generate the golden fixture | 5 (scope beyond Approvals 2–4) | yes | APPROVED | Gopal Patwa | 2026-09-29T15:26:12Z | runs/docs-retrieval/APPROVAL_RECORD-5.md |
| One-off reference comparison: sentence-transformers + PyTorch (PyPI, pinned, throwaway env) + model.safetensors and 6 small config files from HF (≈330 MB) | 5 (scope beyond Approvals 2–5) | yes | APPROVED | Gopal Patwa | 2026-09-29T16:14:41Z | runs/docs-retrieval/APPROVAL_RECORD-6.md |

## Budget

Per `RUN_ECONOMICS.md`. Checked **before every spawn** — never reconciled after.

- **Budget:** 1130k tokens  ·  **Depth:** standard
- **Spent:** 854k (76%)  ·  **Remaining:** 276k
- **Next stage:** none — slice closed (gate failed; nothing ships). Any follow-up is a new slice decided by the owner (08-close-out.md).

Budget set to 1,130k by the owner ("Set 1,130k", 2026-09-29T05:28:14Z) for one slice with embed-v3 (EM projection ≈1,067–1,127k, incl. 60k re-run reserve). Earlier: raised from 690k to 820k on the owner's choice of option A in ESCALATION-1.md ("A, and I'll write the fresh questions"), covering one retry (≈818k projected); this is the owner's decision, not a fit-to-spend. The 690k was docs-retrieval-core's proposed budget (Σ560k, 5 stages, +130k headroom), accepted by the owner.
Note: docs-retrieval-ci is proposed at another 690k (Σ560k + 130k). With Scope Review, the split totals 1,220k vs the original single-slice 890k. The owner decides.
Spent is the harness's `subagent_tokens` (peak context, per RUN_ECONOMICS §1; a resumed agent's figure is cumulative, not additive): Scope Review 55,125 + EM (amendment, then file-count ruling) 33,715 + Architecture (incl. INV-4/5 follow-up) 131,797 + Implementation 107,180 = 327,817; after the v2 revision the Architect's cumulative figure is 186,421 (was 131,797), so total 382,441; after the embed-v3 design the Architect's cumulative figure is 225,583, total 421,603; after the embed-v3 fact-fill the Architect's cumulative figure is 275,625, so total ≈471,645; the EM's cumulative figure is then 72,097 (was 33,715), so total 510,027. QA off-topic list 44,781 → 554,808; after ADR 0003 the Architect's cumulative figure is 292,142 (was 275,625), so total 571,325.
The installed guard checks spent ≥ budget only; spent + estimate is checked by hand before each spawn.
Every stage handoff must tell the role: keep Status to one of the four SLICE_STATE values, keep the Budget / Spent / Next stage lines in their exact format, and put reasons and per-slice figures in a note beneath (pack v9 rule; installed pack is v6 + 677c1e1). Reinstall v9+ only after the slice lands.

### Frozen inputs

- **evals/calibration-offtopic.toml** — 59 QA-authored questions, frozen 2026-09-29T05:32:03Z at commit `fa3673ad75278003516a570639a39cdc616444e2`, **sha256 `9045189567b083c83c02336a4f70990c8a8e3ce3e49d5917642fbad6e293627c`**. Not read by the Architect or the engineer; loaded by path only. Overlap with the owner's held-out set is unchecked (not in the repo) and is the owner's to check. QA agent run (44,781 tokens; models seen in transcript: 26 "model":"claude-sonnet-5-5"; frontmatter sonnet/high).

- **Method commit (implementation, embed-v3):** `c9b64e7bf55da02a925e5a0be8ca37a4a9dc189a`, committed 2026-09-29T07:45:37Z. This is the method to freeze. The golden fixture and its generator are test-only additions after it; if the fixture forces any change to `aveto_support/`, the method changes and the freeze is re-recorded before the owner writes the held-out set. Off-topic list still sha256 `9045189567b083c83c02336a4f70990c8a8e3ce3e49d5917642fbad6e293627c`. Index sha256 (three byte-identical ingests) `1f6b2194db040446aa09ba6021d30a80df4361bcbc1e9c2958292c97d0cbe5c9`. No eval has been run on any set.

### METHOD FROZEN — 2026-09-29T15:28:06Z

- **Frozen method commit:** `c9b64e7bf55da02a925e5a0be8ca37a4a9dc189a` (embed-v3 implementation). Verified **unchanged** through the fixture commit `593bb35110da0b0b5ae3e10817a277f6ca01a81e`: `git diff c9b64e7 -- aveto_support pyproject.toml uv.lock docs-source.toml tests/*.py evals` is empty.
- Golden tokenizer fixture landed in `593bb35110da0b0b5ae3e10817a277f6ca01a81e` (test-only; `tokenizers==0.22.2` one-off, not a dependency; 13 cases; mutation-checked by the Orchestrator: one perturbed id fails the test, restored fixture passes).
- Off-topic list sha256 `9045189567b083c83c02336a4f70990c8a8e3ce3e49d5917642fbad6e293627c` (frozen `fa3673a`); index sha256 `1f6b2194db040446aa09ba6021d30a80df4361bcbc1e9c2958292c97d0cbe5c9`.
- **No eval has been run on any set since eval run 1** (the lexical v1 run, 2/24). From this point the owner may commit the held-out set. **No change to `aveto_support/`, `pyproject.toml`, `uv.lock`, `docs-source.toml` or the off-topic list between the held-out commit and the scoring run.**

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| Implementation (eval gate) | 1 of 2 used (retry 1 = v2/embed-v3 revision, failed the held-out gate); retry 2 unspent, escalated early | 2 | gate-violation | held-out gate: answerable 5/17 (need 14), unanswerable 5/6; ungated recall@5 8/17. See ESCALATION-2.md |

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
| Implementation of embed-v3 (resumed; cumulative peak 262,939, was 107,180) | sonnet-5-5 | medium (declared) | — | — | 18:14 | +155,759 | +41 | 1 |
| QA golden fixture (resumed; cumulative peak 60,704, was 44,781) | sonnet-5-5 | high (declared) | — | — | 1:08 | +15,923 | +10 | 0 |
| QA held-out scoring (resumed; cumulative peak 72,131, was 60,704) | sonnet-5-5 | high (declared) | — | — | 0:51 | +11,427 | +7 | 0 |
| QA reference-embedding comparison (resumed; cumulative peak 102,365, was 72,131) | sonnet-5-5 | high (declared) | — | — | 3:41 | +30,234 | +16 | 0 |
| Architecture embed-v3 fact-fill (resumed; was missing from this table) | opus-5-5 | high (declared) | — | — | 4:49 | +50,042 | +39 | 1 |
| EM embed-v3 re-scope (resumed; was missing from this table) | sonnet-5-5 | medium (declared) | — | — | 1:51 | +38,382 | +11 | 1 |
| Close-out (post-launch-learning) | sonnet-5-5 | medium (declared) | — | — | 1:47 | 69,266 | 27 | 0 |
| **Total** | | | | | | 853,934 | 386 | |

Measured usage (2026-09-29T07:17:38Z, `usage.mjs . --slice docs-retrieval`, harness-logged models; no role marked `*`, so tool restrictions bound): 5/5 stages measured, 156 requests, cache hit 92.3%. **Processed 19.46M tokens (cost-weighted 4.73M)**, of which software-architect 15.60M (84 requests, opus-5-5, peak context 128k), backend-architect 2.14M, engineering-manager 1.26M, qa-evidence 0.45M. The report's peak-context total is 363k; the Tokens column above (571k) is the sum of the harness's per-spawn `subagent_tokens`, kept as the more conservative figure for the budget. **The budget is in peak-context units; what the slice actually consumed from usage limits is the processed figure, roughly 34× larger.** Models above are copied from the report; effort is not in the log, so it is the declared frontmatter value.

Correction (2026-09-29T05:28:36Z): the Architecture rows above were first recorded as sonnet/medium from memory. The role's frontmatter is `model: opus, effort: high` and its harness transcript has 202 turns, all claude-opus-5-5 (reported by the playbook session and re-checked here against .claude/agents/software-architect.md and the subagent transcript). Token figures are unaffected (harness-reported). Exact ids seen in transcripts: Scope Review claude-sonnet-5; later Engineering Manager and Implementation runs claude-sonnet-5-5. Effort is the declared frontmatter value; it is not measurable from the transcript. After the slice, `node <playbook>/execution/usage.mjs --write` should replace these self-reported figures.

## Next action

Slice closed. Held-out gate failed (answerable 5/17, need 14); nothing ships; code stays on this branch. The owner decides any follow-up: 08-close-out.md section 5 (incl. the open question whether "no confident match" belongs in the check step, approval rule 4). Reinstall pack v9+ only now that the slice has landed/closed.
