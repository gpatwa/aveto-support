# Slice State — public-ask-the-docs

- **Ask:** `intents/public-ask-the-docs.md` — a public "ask the docs" page, live on Azure: verbatim passages or "no confident match", judged through the Anthropic API under hard cost and abuse limits
- **Project pack:** ai-agent-product
- **Release tier:** 3
- **Current stage:** 9 AI adapter, 10 Frontend (parallel)
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents/teammates in `.claude/agents/` (pack v26), run from this repo's worktree
- **Telemetry:** self-reported — see `TELEMETRY.md`
- **Charter:** runs/public-ask-the-docs/CHARTER.md, sha256 d0acc5346a80e199e3f95ac57e23a2c01fec43e56d93dbda3b4a03e6a99fa74c approved in APPROVAL_RECORD-1
- **Started:** 2026-10-20  ·  **Updated:** 2026-10-20

## Stages

| Stage | Owner | Status | Artefact | Gate |
|-------|-------|--------|----------|------|
| Intent | Human | confirmed by the owner 2026-10-20 (copied unchanged) | runs/public-ask-the-docs/intent.md | human confirms |
| Intake | Orchestrator | done | runs/public-ask-the-docs/00-slice-plan.md | n/a |
| Setup | Orchestrator | done except C6.5 to C6.7 (owner and support session) | 00-slice-plan.md Prerequisites | dry runs |
| Charter | Human | approved by hash 2026-10-21T06:42:08Z | runs/public-ask-the-docs/CHARTER.md | human approves by hash |
| 1 Scope review | Engineering Manager | done — proceed with changes, no stop item | runs/public-ask-the-docs/01-scope.md | n/a |
| 2 PRD | Product Manager | done — 18 requirements, 9 visitor states, no stop item | runs/public-ask-the-docs/02-prd.md | n/a |
| 3 Feature spec | UX Researcher | done — 1 visitor, 9 states, edge cases, WCAG 2.2 AA floor, no stop item | runs/public-ask-the-docs/03-feature-spec.md | n/a |
| 4 UX spec | UI Designer | done — one page, 11 states with final copy, no-JS form post, tokens light/dark, no stop item | runs/public-ask-the-docs/04-ux-spec.md | n/a |
| 5 Tech spec | Software Architect | done — two passes; `aveto_service/` beside the unchanged core; kill switch = Container App env var via Bicep param (default on); limits in fail-closed order; 3 new deps; ADR 0009 proposed; no STOP taken, 1 possible STOP at stage 11 (vault RBAC mode), 2 owner items (counters reset with the replica; "without a redeploy" = no build, new revision) | runs/public-ask-the-docs/05-tech-spec.md, docs/adr/0009-public-ask-service-on-azure-container-apps.md | n/a |
| 8 Backend service | Backend Architect | done — `aveto_service/` (settings, port, limits, abuse log, pipeline, app); fastapi 0.157.0, uvicorn 0.54.0, anthropic 1.7.0; 110 new tests, 535 pass; mypy, ruff clean; deviations in note (attempts field, post-hoc charge for retry) | runs/public-ask-the-docs/08-backend-note.md | local regression green |
| 6 to 19 (except 8) | per plan | pending | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Approve the Charter | Charter | yes | approved | Gopal Patwa | 2026-10-21T06:42:08Z | runs/public-ask-the-docs/APPROVAL_RECORD-1.md |

## Budget

- **Budget:** 2000k tokens  ·  **Depth:** standard
- **Spent:** 684k (34%)  ·  **Remaining:** 1316k
- **Next stage:** 9 AI adapter + 10 Frontend page (build, parallel) est. 190k → **PROCEED**

Note: ceiling 3000k, hard cap 3600k (Charter C2). Orchestrator intake and setup spend is the driving session's, not a spawn.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| — | 0 | 2 | — | — |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|
| 6 AI Governance | usage limit (HTTP 429) | infra | see re-spawn | yes |
| 7 Compliance | usage limit (HTTP 429) | infra | see re-spawn | yes |

## Trace

| Stage | Model | Effort | Start (UTC) | End (UTC) | Wall | Tokens | Tool calls | Retry # |
|-------|-------|--------|-------------|-----------|------|--------|------------|---------|
| 1 Scope review (em-scope) | sonnet-5-5 | medium | — | — | — | 47k | 16 | 0 |
| 2 PRD (pm-prd) | sonnet-5-5 | medium | — | — | — | 36k | 9 | 0 |
| 3 Feature spec (uxr-spec) | sonnet-5-5 | medium | — | — | — | 32k | 7 | 0 |
| 4 UX spec (ui-spec) | sonnet-5-5 | medium | — | — | — | 27k | 9 | 0 |
| 5 Tech spec (arch-spec) | opus-5-5 | high | — | — | — | 215k | 79 | 0 |
| 6 AI Governance (aigov-2; first attempt cut off by usage limit) | sonnet-5-5 | high | — | — | — | 63k | 7 | 0 |
| 7 Compliance + data (compliance-2) | sonnet-5-5 | high | — | — | — | 84k | 21 | 0 |
| 4b UX copy amendment (ui-patch) | sonnet-5-5 | medium | — | — | — | 35k | 6 | 0 |
| 8 Backend service (backend) | sonnet-5-5 | medium | — | — | — | 146k | 36 | 0 |
| **Total** | | | | | | 684k | | |

## Next action

Spawn stages 9 (AI Engineer) and 10 (Frontend Developer) in parallel; then 11 (Cloud Deployment).

## Setup log

- 2026-10-21T06:35Z C6.5 dry run passed: `az keyvault secret list --vault-name kv-aveto-ask-gp` lists `anthropic-api-key` (name only; value never read). Resource group and vault created by the owner; signed-in Azure account is [owner email removed] (shown in the vault's createdBy).
- 2026-10-21T06:35Z C6.6: owner's statement in this session, "c6.6 is set" (Anthropic console monthly limit $10). Not verifiable by an agent.
- 2026-10-21T06:35Z C6.7: not yet in place (`/Users/gopalpatwa/opt/aveto-gates/public-gate-1.toml` absent); needed at stage 18.
- 2026-10-21 Orchestrator, after stage 5: (1) `kv-aveto-ask-gp` is in RBAC mode (`enableRbacAuthorization` true, read-only check), so the tech spec's possible C8.3 STOP does not arise. (2) Kill switch is an env var applied by `az deployment group create` (covered by C8.3); it creates a new revision with no image rebuild. The intent's "without a redeploy" is met only in that sense — reported at END_REVIEW, not stretched. (3) Hourly and daily counters are in memory and reset when the replica scales to zero; persistence would need a resource C8.3 does not name. The $10 console limit stays the monthly backstop. Security rules at stage 14; owner decides at END_REVIEW. (4) The service shows each passage's full verbatim text (what the judge saw), not the CLI's 3-line excerpt; INV-4 words must say so, within C5.1; Security checks at stage 14.
- 2026-10-21 Orchestrator, after stages 6 and 7: both PASS (06 tier limited, provisional on Art. 50 for owner/legal; 07 PASS WITH REQUIRED FIXES, gates G1-G10). Carried forward as release-gate conditions: page must name Anthropic as recipient, say an AI model decides, tell visitors not to enter personal data (06 R1; 07 top gap) — UX spec 04 patched before stage 10; owner records a line on Art. 50 / privacy / legal or accepts them open (06 R2, END_REVIEW); Security rules at stage 14 on counters reset at scale-to-zero and forwarded-IP (06 R3); stage 17 must search Log Analytics for the tester's own IP in ingress/system tables (07). Only 1 of 4 hostile gate questions tests injection through the question, and the 8/10 bar may miss by chance (06): reported as is, bars not changed. Stage 6's first attempt had already written 06 before the usage-limit cut; the re-run verified it and left it unchanged.
- 2026-10-21 Orchestrator, after stage 8: regression re-run by the Orchestrator: mypy clean, ruff clean, 535 passed (425 + 110 new); `git diff main -- aveto_support prompts .claude .agentic` empty. Stage 8 deviation to carry: `JudgeCall.attempts` — the adapter must set attempts=2 when it retried (08-backend-note). Open gap L1 (the judge_error cause is not logged) is a logging-contract choice for Security at stage 14.
