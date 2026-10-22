# Slice State — public-ask-the-docs

- **Ask:** `intents/public-ask-the-docs.md` — a public "ask the docs" page, live on Azure: verbatim passages or "no confident match", judged through the Anthropic API under hard cost and abuse limits
- **Project pack:** ai-agent-product
- **Release tier:** 3
- **Current stage:** 17 deployed, kill switch ON; waiting on S-C1 step 2 (owner's phone)
- **Status:** in-progress
- **Least-privilege:** enforced — role subagents/teammates in `.claude/agents/` (pack v26), run from this repo's worktree
- **Telemetry:** self-reported — see `TELEMETRY.md`
- **Charter:** runs/public-ask-the-docs/CHARTER-v2.md, sha256 e04b82539e1fe17ed86d945a93b761dafef4f19c1af30dc4353f31743fc8ead4 approved in APPROVAL_RECORD-2 (replaces v1, d0acc534…, APPROVAL_RECORD-1)
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
| 15 Docs and safety text | Software Architect (15a); Tech Writer (15b); Compliance Reviewer (15c) | in progress — 15a done: INV-4 (two callers, service (a)/(b)/(c) mapping, transcript counterpart, 23 test names) and INV-5 (service exception, 19 header names, ops lines, 24 test names) written within C5.1/C5.2; 5 original lines changed, only the C5.1 sentence's words removed; INV-1 to INV-3 untouched; all 44 cited test names verified; `git diff` not run (no shell, U); 4 reading risks R1-R4 for 15c; `docs/ARCHITECTURE.md` gains "Public ask service"; no STOP | runs/public-ask-the-docs/15a-safety-text-note.md, .agentic/SAFETY_INVARIANTS.md, docs/ARCHITECTURE.md | 15c words check; stage 16 diff against 2919c87 |
| 16 Release Gate (tier 3) | Release Manager | done — GO WITH CONDITIONS for stage 17 steps 1 to 4 only (deploy, kill switch ON); kill switch OFF NOT authorised (switch-on gate S1-S9 in the checklist, smoke-depth re-check recommended); code-review tier re-derived High; safety words inside Charter v2 C5.1/C5.2 with reading notes N1-N5; NOT MET: Approvals rows for gated actions (P1), processor record in runbook (G7, P3); saved final-tree checks name b0cf09d, HEAD is 9f40e9a (P2); pre-deploy P1-P4; dry run MET WITH GAPS (no fixture for the first real Anthropic call); rollback rehearsal and Build gate NOT YET (stage 17); live service, gate and owner decisions D1-D7 not covered | runs/public-ask-the-docs/16-release-checklist-tier3.md | P1-P4 recorded before stage 17; S1-S9 before the switch goes off |
| 6 to 19 (except 8, 9, 10, 11, 13, 14, 15, 16) | per plan | pending | — | — |

## Approvals

| Action | Rule | Requested | Decision | Approver | When (UTC) | Record |
|--------|------|-----------|----------|----------|-----------|--------|
| Runtime judge `claude-sonnet-5-5` via the Anthropic API | rule 5 | covered | done in code, first live call at stage 17 | Gopal Patwa via Charter v2 | 2026-10-21 | CHARTER-v2.md#C3.1 (sha256 e04b8253…ead4) |
| Anthropic and Azure as data processors | rule 6 | covered | in effect at deploy | Gopal Patwa via Charter v2 | 2026-10-21 | CHARTER-v2.md#C4.1, #C4.2 |
| INV-4 and INV-5 words | rule 4 | covered | done (15a, 15c check, round 2 and 3) | Gopal Patwa via Charter v2 | 2026-10-21 | CHARTER-v2.md#C5.1, #C5.2; 15c-words-check.md |
| Deploy to rg-aveto-ask; kill switch on/off | rule 3 | covered | stage 17 (kill switch ON first) | Gopal Patwa via Charter v2 | 2026-10-21 | CHARTER-v2.md#C8.3 |
| Kill switch OFF (tech spec §7 step 5): the public service starts answering | rule 3 | covered; switch-on gate S1-S9 met per `17-switch-on-recheck.md` (GO WITH CONDITIONS, conditions C1-C4 saved in `17-deploy/conditions-c1-c4.txt`) | executing 2026-10-22 | Gopal Patwa via Charter v2 | 2026-10-22 | CHARTER-v2.md#C8.3 (sha256 e04b8253…ead4) |
| Push claude/public-ask-the-docs; PR into main | rule 3 | covered | stage 19 | Gopal Patwa via Charter v2 | 2026-10-21 | CHARTER-v2.md#C8.2 |
| Approve Charter v2 (amendment 1: C4.1 SDK headers, C5.2 one sentence) | Charter section 9.1 and 9.5 | yes | approved | Gopal Patwa | 2026-10-21T20:29:11Z | runs/public-ask-the-docs/APPROVAL_RECORD-2.md |
| Approve the Charter | Charter | yes | approved | Gopal Patwa | 2026-10-21T06:42:08Z | runs/public-ask-the-docs/APPROVAL_RECORD-1.md |

## Budget

- **Budget:** 2000k tokens  ·  **Depth:** standard
- **Spent:** 2004k (100%)  ·  **Remaining:** -4k
- **Next stage:** 16 Release Gate tier 3 (after Charter v2 decision) est. 170k → **PROCEED**

Note: ceiling 3000k, hard cap 3600k (Charter C2). Orchestrator intake and setup spend is the driving session's, not a spawn.

## Failure budget

| Stage | Retries used | Cap | Class | Last failure |
|-------|--------------|-----|-------|--------------|
| — | 0 | 2 | — | — |

## Interruptions

| Stage | Cause | Class | Partial artefact reached | Resumed |
|-------|-------|-------|--------------------------|---------|
| 15c words check | usage limit (HTTP 429) | infra | none (no 15c-words-check.md written) | yes |
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
| 14c Security round 2: S-A2 egress pin (ai-sa2) | sonnet-5-5 | medium | — | — | — | 29k | 8 | 0 |
| 14d Security round 2: S-A4, S-A6, S-A8 (backend-sa) | sonnet-5-5 | medium | — | — | — | 36k | 11 | 0 |
| 15a INV-4/INV-5 words + ARCHITECTURE.md (arch-words) | opus-5-5 | high | — | — | — | 203k | 65 | 0 |
| 15b README, status, runbook (writer-docs) | sonnet-5-5 | medium | — | — | — | 110k | 32 | 0 |
| 15c different-model words check (words-check-2; first attempt cut off by usage limit) | sonnet-5-5 | high | — | — | — | 180k | 44 | 0 |
| 15d words round 2 (arch-words-2) | opus-5-5 | high | — | — | — | 52k | 11 | 0 |
| **Total** | | | | | | 2004k | | |

## Next action

Owner opens the service URL on a phone over cellular and presses Ask once (kill switch is ON: nothing reaches Anthropic). Then the Orchestrator reads the new `ip` hash from the workspace; if it differs from `f0dc6b0b54a5e4b4`, S1 is met: re-spawn the Release Manager at smoke depth, record the Approvals row for kill switch OFF, run step 5, then S6 (first call), E3 (rollback rehearsal), stage 18.

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
- 2026-10-21 Orchestrator, security round 2 (advisories fixed, beyond the two required fixes): S-A2 client pinned to `https://api.anthropic.com`, construction fails closed if `ANTHROPIC_CUSTOM_HEADERS` is set; S-A4 service applies the core's 4096-byte reply limit; S-A6 `redirect_slashes` off; S-A8 cross-site POST /ask refused (Sec-Fetch-Site / Origin); FastAPI OpenTelemetry auto-configure pinned off. 636 passed, mypy and ruff clean; method files byte-identical to main. Header names the SDK sends (19, from the adapter note): host, accept, accept-encoding, connection, content-length, content-type, user-agent, anthropic-version, x-api-key, x-stainless-{arch,async,lang,os,package-version,read-timeout,retry-count,runtime,runtime-version,timeout}. NOT fixed, carried to END_REVIEW as advisories: S-A3 (the "paused for today, not a fault" copy is false during an outage; owner-approved UX copy), S-A5 (invisible-character injection carrier not in the 4 hostile gate questions), S-A7 (no uvicorn read timeout; ingress bounds it, unconfirmed), S-A9 (vault-scope role), S-A10 (log daily quota drops late abuse lines), S-A11 (Azure spend has no cap), S-A12 (ops lines to name in the C4.2 words), S-A14, S-A15; owner decisions D1-D7.
- 2026-10-21 Orchestrator, stage 15 stop: the different-model check (`15c-words-check.md`, verdict FAIL as written) found two Charter stops, neither of which the Orchestrator may waive: S10 (INV-5's retained sentence "The operator's session is the one exception, and it is not the program." must change because the service is now a second exception; C5.2 says every other sentence stays) and S11b (the SDK's own headers — user-agent and x-stainless-os/arch/runtime — are beyond C4.1's "exactly"; the words are accurate and must stay). Curable findings S1, F1, F2, F3 applied by the Architect (round 2). Charter v2 drafted at `CHARTER-v2.md` (two lines changed, C4.1 and C5.2; charter-check passes; sha256 e04b82539e1fe17ed86d945a93b761dafef4f19c1af30dc4353f31743fc8ead4); v1 (`CHARTER.md`, d0acc534…) stays the approved Charter until the owner approves v2 by hash. Spend 2004k = 100% of plan total 2000k, under the ceiling 3000k: the run continues above plan total without a notice duty; projected finish about 2.4M. Runbook correction owed (Tech Writer): the vault IS inside rg-aveto-ask (the owner created it there), so deleting the group would delete the key.
- 2026-10-22 Orchestrator, stage 17 (kill switch ON, nothing served): P1-P4 done (73363c5 / 0fa04abda8ad; `17-p2-recheck.txt`; the word-removal list gained `[-the-]` from the N1 reword, inside C5.2). Step 1 created identity, registry, workspace, environment, both role assignments (`17-deploy/step1-*.txt`). Step 2 `az acr build` from the worktree root, tag `aveto-ask:0fa04abda8ad`, 2m15s, digest sha256:82bfb9a3…e8bb; the build's `ingest` wrote index sha256 f36ef5d4…a756, EQUAL to the local index (S4: match), 890 passages, base digests match the Dockerfile pins. Step 3 what-if listed only C8.3 types; create succeeded (revision `ca-aveto-ask--4q3pl0p`, FQDN `ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`). D3 off-state check FAILED: no HTTP response in 150 s; console log `{"ops":"startup_failed","c":"index"}`, replica CrashLoopBackOff. Fail-closed, as designed: nothing was served and no model call was possible. Release-checklist D4 applies (startup_failed: stop, hand back, never work around; a change to the Dockerfile = new commit, P2 again, checklist reopened, no gate set opened until the method is frozen again). Root cause (F-LIVE-1): `ingest` writes `index/` and model files with mkstemp (mode 0600); in the image they are root-owned and the runtime user (uid 10001) cannot read them. Fix routed to the Backend Architect (Dockerfile only, `--chown`); then new commit, P2, rebuild with the new tag, redeploy kill switch ON, D3 again. This is a Dockerfile defect, not a Charter stop (a rebuild and redeploy are C8.3). A smoke-depth Release Manager re-check follows the stage 17 artefact (the checklist already asks for it).
