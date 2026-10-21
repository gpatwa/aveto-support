# Slice State — public-ask-the-docs

- **Ask:** `intents/public-ask-the-docs.md` — a public "ask the docs" page, live on Azure: verbatim passages or "no confident match", judged through the Anthropic API under hard cost and abuse limits
- **Project pack:** ai-agent-product
- **Release tier:** 3
- **Current stage:** 15 Docs and safety text
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
| 9 AI adapter | AI Engineer | done — `aveto_service/anthropic_judge.py`; 24 tests on a fake Messages client; request body exact, no tools, effort high explicit, 2 attempts, fixed error categories, hash fail-closed, SDK loggers muted by the adapter; 559 pass, mypy, ruff clean; (U) model id and effort accepted: stage 17 | runs/public-ask-the-docs/09-ai-adapter-note.md | local regression green |
| 10 Public page | Frontend Developer | done — `aveto_service/{pages,render,result_store,main}.py`, static css/js; 25 tests, 584 pass, mypy, ruff clean; no browser preview (no tool): enhance.js only syntax-checked, contrast unmeasured; 3 copy mappings for outcomes the UX table lacks | runs/public-ask-the-docs/10-frontend-note.md | local regression green |
| 11 Infra and image | Cloud Deployment | partial — `infra/main.bicep` + `main.parameters.json` written (C8.3 types only); Dockerfile, .dockerignore, tests/test_infra_static.py blocked by write-scope-guard (text in note); no shell, so no az checks, no regression run | runs/public-ask-the-docs/11-infra-note.md | not met until files written and checks run | 11c done: Dockerfile, .dockerignore, tests/test_infra_static.py written; Azure read-only checks in 11c-infra-checks.md (bicep build FAILS: F1 BCP265 `environment` symbol, F2, F3 for Cloud Deployment); image unbuilt (Docker daemon down); 591 tests green |
| 13 QA evidence (final tree, offline) | QA Evidence | done — GO WITH CONDITIONS: 606 passed x3 (425 on main + 181), mypy, ruff clean; 0 NOT MET offline except intent line 11 (docs, stage 15 pending); 6 required mutations each caught, 1 redundant kill-switch check (`pipeline.py:216`) untested (QA-1); local run on real index + fake judge: 100 passages byte-identical, logs hold abuse lines only; real API, ingress XFF, image build, retention, cold start, browser checks and gate unverified | runs/public-ask-the-docs/13-qa-evidence.md | local regression green |
| 14 Security Review (adversarial) | Security & Privacy | done — PASS WITH REQUIRED FIXES, 0 blockers: S-R1 (unrecorded post-retrieval `paused` refusals give unbounded retrieval per visitor; sync `/health` queues behind it; `pipeline.py:229-252`, `app.py:154-156`), S-R2 (QA-1 test, `pipeline.py:216`); stage 17 conditions S-C1 (CR-4 XFF check, kill switch on), S-C2 (retention 7/7 before on), S-C3 (`az acr build` from the worktree root); C4.1 not breached; CR-3 owner decision (not a blocker), CR-8 advisory, 5xx keeps full charge; 15 advisories, owner decisions D1-D7 | runs/public-ask-the-docs/14-security-review.md | fixes S-R1, S-R2 re-checked before the Release Gate |
| 6 to 19 (except 8, 9, 10, 11, 13, 14) | per plan | pending | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Approve the Charter | Charter | yes | approved | Gopal Patwa | 2026-10-21T06:42:08Z | runs/public-ask-the-docs/APPROVAL_RECORD-1.md |

## Budget

- **Budget:** 2000k tokens  ·  **Depth:** standard
- **Spent:** 1394k (70%)  ·  **Remaining:** 606k
- **Next stage:** 15 Safety text (Architect), docs (Tech Writer), words check (different model) est. 220k → **PROCEED**

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
| 9 AI adapter (ai-adapter) | sonnet-5-5 | medium | — | — | — | 46k | 16 | 0 |
| 10 Frontend page (frontend) | sonnet-5-5 | medium | — | — | — | 76k | 20 | 0 |
| 11 Infra + image (cloud-infra) PARTIAL: guard blocked 3 files; no shell | sonnet-5-5 | medium | — | — | — | 66k | 25 | 0 |
| 11a Spec §12 amendment (arch-amend, smoke) | opus-5-5 | high | — | — | — | 29k | 10 | 0 |
| 11c Dockerfile, infra tests, Azure read-only checks (backend-infra) | sonnet-5-5 | medium | — | — | — | 50k | 16 | 0 |
| 11d Bicep lint fixes (cloud-infra resumed; peak 69k total for stage 11) | sonnet-5-5 | medium | — | — | — | 3k | 7 | 0 |
| 12 Review layer (Orchestrator /code-review high, declared sonnet-5-5; + round 1 fixes backend-fix1) | sonnet-5-5 | high | — | — | — | 55k | 19 | 0 |
| 13 QA evidence (qa-final) | sonnet-5-5 | high | — | — | — | 145k | 57 | 0 |
| 14 Security Review adversarial (security-adv) | opus-5-5 | high | — | — | — | 226k | 63 | 0 |
| 14b Security required fixes S-R1, S-R2, S-A1 (backend-fix1 resumed; peak 70k total) | sonnet-5-5 | medium | — | — | — | 16k | 5 | 0 |
| **Total** | | | | | | 1394k | | |

## Next action

Spawn 15a Architect (INV-4/INV-5 words + ARCHITECTURE.md) and 15b Tech Writer (README, status, runbook) in parallel; then 15c different-model check of the words.

## Setup log

- 2026-10-21T06:35Z C6.5 dry run passed: `az keyvault secret list --vault-name kv-aveto-ask-gp` lists `anthropic-api-key` (name only; value never read). Resource group and vault created by the owner; signed-in Azure account is [owner email removed] (shown in the vault's createdBy).
- 2026-10-21T06:35Z C6.6: owner's statement in this session, "c6.6 is set" (Anthropic console monthly limit $10). Not verifiable by an agent.
- 2026-10-21T06:35Z C6.7: not yet in place (`/Users/gopalpatwa/opt/aveto-gates/public-gate-1.toml` absent); needed at stage 18.
- 2026-10-21 Orchestrator, after stage 5: (1) `kv-aveto-ask-gp` is in RBAC mode (`enableRbacAuthorization` true, read-only check), so the tech spec's possible C8.3 STOP does not arise. (2) Kill switch is an env var applied by `az deployment group create` (covered by C8.3); it creates a new revision with no image rebuild. The intent's "without a redeploy" is met only in that sense — reported at END_REVIEW, not stretched. (3) Hourly and daily counters are in memory and reset when the replica scales to zero; persistence would need a resource C8.3 does not name. The $10 console limit stays the monthly backstop. Security rules at stage 14; owner decides at END_REVIEW. (4) The service shows each passage's full verbatim text (what the judge saw), not the CLI's 3-line excerpt; INV-4 words must say so, within C5.1; Security checks at stage 14.
- 2026-10-21 Orchestrator, after stages 6 and 7: both PASS (06 tier limited, provisional on Art. 50 for owner/legal; 07 PASS WITH REQUIRED FIXES, gates G1-G10). Carried forward as release-gate conditions: page must name Anthropic as recipient, say an AI model decides, tell visitors not to enter personal data (06 R1; 07 top gap) — UX spec 04 patched before stage 10; owner records a line on Art. 50 / privacy / legal or accepts them open (06 R2, END_REVIEW); Security rules at stage 14 on counters reset at scale-to-zero and forwarded-IP (06 R3); stage 17 must search Log Analytics for the tester's own IP in ingress/system tables (07). Only 1 of 4 hostile gate questions tests injection through the question, and the 8/10 bar may miss by chance (06): reported as is, bars not changed. Stage 6's first attempt had already written 06 before the usage-limit cut; the re-run verified it and left it unchanged.
- 2026-10-21 Orchestrator, after stage 8: regression re-run by the Orchestrator: mypy clean, ruff clean, 535 passed (425 + 110 new); `git diff main -- aveto_support prompts .claude .agentic` empty. Stage 8 deviation to carry: `JudgeCall.attempts` — the adapter must set attempts=2 when it retried (08-backend-note). Open gap L1 (the judge_error cause is not logged) is a logging-contract choice for Security at stage 14.
- 2026-10-21 Orchestrator, after stages 9 and 10: regression re-run by the Orchestrator: mypy clean, ruff clean, 584 passed (535 + 24 adapter + 25 pages); method files byte-identical to main (empty diff). No live Anthropic call made; first live call is stage 17. Items routed forward: (a) UX table lacks copy for `unusable_question`, `bad_request`, `body_too_large` — reused Empty / Too long copy (10-frontend-note) → QA/Security to look, no owner action; (b) an unmatched static path returns FastAPI's default JSON 404 without the page headers (app.py is the Backend's) → Security stage 14; (c) enhance.js untested beyond `node --check`, contrast and 320px/forced-colors unmeasured → QA stage 13 (built-in browser available); (d) SDK logger muted by the adapter constructor (09 note).
- 2026-10-21 Orchestrator, after stage 11: SR-1 resolved in-run (Architect amended §12; Backend wrote Dockerfile/.dockerignore/test_infra_static and ran the read-only checks; Cloud Deployment fixed F1-F3). Orchestrator re-ran: `az bicep build` exit 0; `what-if deployApp=false` creates only identity, ACR, ACR role assignment, Log Analytics, environment, Key Vault role assignment (vault: Ignore); mypy clean, ruff clean, 591 passed. No Azure resource was created. The image is unbuilt (no Docker daemon locally); the first build is `az acr build` at stage 17, so "ingest runs inside the build" and the cold-start figure are unconfirmed until then. Stage 17 deploy commands run from the Orchestrator's session under C8.3 (the deploy role has no shell).
- 2026-10-21 Orchestrator, after stage 12: `code-review.md` written (tier High, 8 findings: 4 fixed in round 1, CR-3/CR-8 intentional, CR-4 until stage 17, CR-7 rejected; round 1 diff re-reviewed, 0 new). Review is unscored (Charter C3.R). The Orchestrator's own review spend is the driving session's, not a spawn, so it is not in the Trace; the 55k row is the Backend fix spawn. Regression after fixes: mypy clean, ruff clean, 606 passed. CR-1 supersedes tech spec §3 step 7. Carried forward: CR-3 (scale-to-zero resets limits) is an owner decision for END_REVIEW "Blocked on me".
- 2026-10-21 Orchestrator, after stage 13: QA verdict GO WITH CONDITIONS (606 passed x3, method files byte-identical, mutations a,c-f caught). QA-1: removing the second kill-switch check (`pipeline.py:216`) fails no test — owed a test by the Backend (done with Security's round). QA: a 5xx failure is still charged its full reservation (Security to rule; CR-2 only zeroes status_4xx and connection). Browser checks by the Orchestrator appended to 13-qa-evidence.md: enhance.js, contrast (>= 6.39 light, >= 8.89 dark), 320 px, keyboard focus pass; screen-reader, forced-colors and reduced-motion not checked.
- 2026-10-21 Orchestrator, after stage 14: Security verdict PASS WITH REQUIRED FIXES, no blocker; S-R1 (retrieval cap, /health off the thread pool), S-R2 (kill-switch test) and S-A1 (Settings repr hides the key) fixed by the Backend; Orchestrator re-ran: mypy clean, ruff clean, 610 passed; diff read, no new finding. Rulings: CR-3 not a blocker (owner decision D1); CR-4 rests on stage 17 check S-C1 before the kill switch goes off; CR-8 advisory; 5xx and timeouts keep the full reservation; C4.1 not breached, and the stage 15 INV-5 words must name the SDK headers about the server (SDK version, OS, Python version). Stage 17 checks S-C1 (forged XFF, kill switch on), S-C2 (log retention reads back 7/7 before the switch goes off), S-C3 (`az acr build` from the worktree root only). Owner decisions D1-D7 go to END_REVIEW.
- 2026-10-21 Orchestrator, plan adjustment (no Charter change): `.agentic/SAFETY_INVARIANTS.md` and `docs/ARCHITECTURE.md` are writable only by the Software Architect (write-scope guard), not the Tech Writer as the plan said. Stage 15 therefore: 15a Architect writes the INV-4/INV-5 words (within C5.1/C5.2) and ARCHITECTURE.md; 15b Tech Writer writes README, CURRENT_MVP_STATUS and the runbook; 15c a different-model adversarial check of the words (Charter C5 intro: the Architect is Opus, so the checker is Sonnet: Compliance Reviewer), then stage 16 diffs SAFETY_INVARIANTS.md against 2919c87.
