# Pipeline Analytics — generated

_Generated 2026-10-27T07:56:29Z. **Do not edit by hand** — regenerate with `node <playbook>/execution/analyze.mjs .` from the repo root._

## Fleet

- Runs traced: **13**
- Stages: **144** · Tokens: **36,458,192** · Tool calls: **3,256**
- **Untraced stages: 19** across 8 run(s) — executed by the Orchestrator rather than spawned, so they carry no tokens or tool calls
- Envelope breaches: **5/13** · Stage outliers: **44**

## Per run

| Run | Tier | Stages | Tokens | Calls | Envelope | Status |
|-----|------|--------|--------|-------|----------|--------|
| docs-retrieval | 2 | 15 | 853,934 | 336 | 1,500,000 | ✅ pass |
| docs-retrieval-2 | 2 | 5 | 311,729 | 118 | 500,000 | ✅ pass |
| docs-retrieval-2-proof | 2 | 3 | 74,665 | 30 | 300,000 | ✅ pass |
| docs-retrieval-3 | 2 | 5 | 5,792,000 | 109 | 300,000 | ❌ over 5492k |
| docs-retrieval-3-proof | 2 | 4 | 2,345,000 | 51 | 200,000 | ❌ over 2145k |
| docs-retrieval-4 | 2 | 11 | 9,684,000 | 232 | 1,000,000 | ❌ over 8684k |
| docs-abstention | 2 | 12 | 8,407,000 | 240 | 1,100,000 | ❌ over 7307k |
| docs-answerability-2 | 3 | 22 | 2,772,517 | 766 | 2,200,000 | ❌ over 573k |
| land-answerability | 3 | 11 | 651,000 | 0 | 900,000 | ✅ pass |
| public-ask-the-docs | 3 | 30 | 2,496,347 | 482 | 3,000,000 | ✅ pass |
| fix-service-accounting | 3 | 13 | 919,000 | 285 | 1,000,000 | ✅ pass |
| polished-chat-experience | 3 | 21 | 1,572,000 | 398 | 1,600,000 | ✅ pass |
| result-page-clarity | 3 | 11 | 579,000 | 209 | 800,000 | ✅ pass |

## Pipeline completeness

Declared-vs-actual against the 12-stage lifecycle (`AGENTIC_SDLC.md`). An
**always** node missing is a real gap; a **conditional** node missing may be a
legitimate compression (`AGENTIC_SDLC.md` § "When to compress stages") — not
flagged either way, just listed, since only the EM's recorded rationale (not
this table) can say whether a given skip was earned.

| Run | Missing (always) | Skipped (conditional) | Unrecognized stage name |
|-----|-------------------|------------------------|--------------------------|
| docs-retrieval | ⚠ Intake, Release Gate | Market Research, Discovery, UX Research, UI Design, Security Review | — |
| docs-retrieval-2 | ⚠ Intake, Release Gate | Market Research, Discovery, UX Research, UI Design, QA Evidence, Security Review, Post-Launch | Doc fix C1 (PROJECT_CONTEXT Stage paragraph) |
| docs-retrieval-2-proof | ⚠ Intake, Scope Review, Implementation, Release Gate | Market Research, Discovery, UX Research, UI Design, Architecture, Security Review | — |
| docs-retrieval-3 | ⚠ Release Gate | Market Research, Discovery, UX Research, UI Design, QA Evidence, Security Review, Post-Launch | Freeze |
| docs-retrieval-3-proof | ⚠ Scope Review, Implementation, Release Gate | Market Research, Discovery, UX Research, UI Design, Architecture, QA Evidence, Security Review, Post-Launch | Label review, Scoring, Close-out |
| docs-retrieval-4 | — | Market Research, Discovery, UX Research, UI Design, QA Evidence, Post-Launch | Close-out |
| docs-abstention | — | Market Research, Discovery, UX Research, UI Design, QA Evidence, Post-Launch | Baseline, Stale-text pass (README), Status-file edit, Close-out |
| docs-answerability-2 | ⚠ Intake | Market Research, Discovery, UX Research, UI Design | Stage 1 measurement (2 judge spawns, owner-started session), Smoke r049 + stage 5 judge spawns (49), Stage 6 label review, Stage 7 judge spawns (48, driver session), Docs finish (Architect, resumed), Docs finish, tier wording (Architect, resumed again) |
| land-answerability | ⚠ Intake, Scope Review, Implementation | Market Research, Discovery, UX Research, UI Design, Post-Launch | S5 fix, Rollback rehearsal, Vendor risk, Records and docs, Setup phase, Code review layer (/code-review high) |
| public-ask-the-docs | ⚠ Intake | Market Research, UI Design | Stage 5 tech spec (software-architect), Stage 8 backend service (backend-architect), Stage 9 Anthropic judge adapter (ai-engineer), Stage 10 public page (frontend-developer), Stage 11 infra and image (cloud-deployment), Amend tech spec work split (software-architect), Stage 11c Dockerfile and Azure checks (backend-architect), Review round 1 fixes (Backend) (backend-architect), S-A4, S-A6, S-A8 service hardening (Backend) (backend-architect), Stage 15b README, status, runbook (tech-writer), Apply curable safety-text rewordings (software-architect), Runbook processor record and monitoring section (tech-writer), INV-5 reading notes N1 and N4 (software-architect), Stage 18 production verification (from saved evidence) (production-verification), Docs: record the measured figures (README, status, runbook) (tech-writer) |
| fix-service-accounting | ⚠ Implementation | Market Research, Discovery, UX Research, UI Design, Architecture | Stage 2 tech spec (software-architect), Stage 3 fixes, fail-first tests, smoke script (backend-architect, two passes), Stage 4 review layer (/code-review high), Stage 7 docs (tech-writer), Stage 9 deploy D1/D2, Stage 10 live smoke (orchestrator) and verdict (production-verification), Stage 11 docs addendum (tech-writer) |
| polished-chat-experience | ⚠ Implementation | Market Research, Discovery, UI Design, Architecture | 3 Tech spec, 4 Backend, 5 Frontend, 6 Review fix F2 (Backend), 7b Fix Q1 Q2 (Frontend), 9b Scorecard fill (Backend), 10 Docs, 10b Docs correction, 10b Scorecard correction (Backend), 13 Production verification, 6 Code review (/code-review high, unscored), 8 Browser checks, 12 Deploy (Charter C8.3; Cloud Deployment not spawned, D14), 13 Live checks, rollback rehearsal, roll forward, cold start |
| result-page-clarity | ⚠ Intake, Scope Review, Implementation | Market Research, Discovery, UX Research, Architecture | 1 Tech spec, 7 Docs, 10 Production verification, 3 Code review, 4 Browser checks, 9 Deploy, 10 rollback rehearsal and live checks |

## DORA

Per `PIPELINE_SLOS.md` § DORA mapping. **Only metrics the traces ground are reported** — anything without data says so.

| Metric | Value | Basis |
|--------|-------|-------|
| Lead time (median) | — | intake → landed, 0/0 slices dated |
| Deployment frequency | — | 0 landed over the traced span |
| Change failure rate | — | 0 post-landing fixes + 0 reverts ÷ 0 landed |
| Rework rate | — | 7 stage retries + 0 post-landing fixes ÷ 0 landed |
| Failed-deployment recovery time | **not captured** | needs `detectedAt`/`resolvedAt` on a `gateCatches` entry; no run has recorded them |

## Density by archetype

Tokens per tool call, measured against each archetype's own cap.

| Archetype | What it does | Cap | Observed (n) | Range | Avg |
|-----------|--------------|-----|--------------|-------|-----|
| **review** | read artefacts → verdict | 8,000 | 73 | 654–7,000 | 3,080 |
| **build** | heavy file / test I/O | 5,000 | 2 | 3,420–3,828 | 3,624 |

## Per stage

| Run | Stage | Type | Model | Effort | Tokens | Calls | Tok/call | % of cap | Flags |
|-----|-------|------|-------|--------|--------|-------|----------|----------|-------|
| docs-retrieval | Scope Review | review | sonnet-5 | medium | 55,125 | 18 | 3,063 | 38% | — |
| docs-retrieval | Scope amendment + file-count ruling | review | sonnet-5-5 | medium | 33,715 | 20 | 1,686 | 21% | — |
| docs-retrieval | Architecture | review | opus-5-5 | high | 131,797 | 44 | 2,995 | 37% | — |
| docs-retrieval | Implementation | build | sonnet-5-5 | medium (declared) | 107,180 | 28 | 3,828 | 77% | — |
| docs-retrieval | Architecture v2 revision (retry 1) | review | opus-5-5 | high | 54,624 | 35 | 1,561 | 20% | — |
| docs-retrieval | Architecture embed-v3 spec-only design | review | opus-5-5 | high | 39,162 | 14 | 2,797 | 35% | — |
| docs-retrieval | QA off-topic calibration list | review | sonnet-5-5 | high (declared) | 44,781 | 15 | 2,985 | 37% | — |
| docs-retrieval | Architecture: ADR 0003 + ARCHITECTURE.md (resumed) | review | opus-5-5 | high | 16,517 | 11 | 1,502 | 19% | — |
| docs-retrieval | Implementation of embed-v3 (resumed) | review | sonnet-5-5 | medium (declared) | 155,759 | 41 | 3,799 | 47% | ⚠ over cap |
| docs-retrieval | QA golden fixture (resumed) | review | sonnet-5-5 | high (declared) | 15,923 | 10 | 1,592 | 20% | — |
| docs-retrieval | QA held-out scoring (resumed) | review | sonnet-5-5 | high (declared) | 11,427 | 7 | 1,632 | 20% | — |
| docs-retrieval | QA reference-embedding comparison (resumed) | review | sonnet-5-5 | high (declared) | 30,234 | 16 | 1,890 | 24% | — |
| docs-retrieval | Architecture embed-v3 fact-fill (resumed) | review | opus-5-5 | high (declared) | 50,042 | 39 | 1,283 | 16% | — |
| docs-retrieval | EM embed-v3 re-scope (resumed) | review | sonnet-5-5 | medium (declared) | 38,382 | 11 | 3,489 | 44% | — |
| docs-retrieval | Close-out (post-launch-learning) | review | sonnet-5-5 | medium (declared) | 69,266 | 27 | 2,565 | 32% | — |
| docs-retrieval-2 | Scope Review | review | sonnet-5-5 | medium (declared) | 51,899 | 21 | 2,471 | 31% | — |
| docs-retrieval-2 | Architecture (fresh single spawn) | review | opus-5-5 | high (declared) | 122,905 | 49 | 2,508 | 31% | — |
| docs-retrieval-2 | Implementation | build | sonnet-5-5 | medium (declared) | 116,263 | 34 | 3,420 | 68% | — |
| docs-retrieval-2 | Doc fix C1 (PROJECT_CONTEXT Stage paragraph) | review | sonnet-5-5 | medium (declared) | 15,429 | 6 | 2,572 | 32% | — |
| docs-retrieval-2 | Architecture: INV-4 note edit (resumed) | review | opus-5-5 | high (declared) | 5,233 | 8 | 654 | 8% | — |
| docs-retrieval-2-proof | QA Evidence (fresh single spawn) | review | sonnet-5-5 | high (declared) | 26,879 | 11 | 2,444 | 31% | — |
| docs-retrieval-2-proof | Post-Launch close-out attempt (resumed once to return its draft) | review | sonnet-5-5 | medium (declared) | 39,756 | 14 | 2,840 | 36% | — |
| docs-retrieval-2-proof | Post-Launch close-out written (resumed after hook fix) | review | sonnet-5-5 | medium (declared) | 8,030 | 5 | 1,606 | 20% | — |
| docs-retrieval-3 | Scope Review | review | sonnet-5-5 | declared: frontmatter default | 402,000 | 22 | 18,273 | 228% | ⚠ over cap, ⚠ density |
| docs-retrieval-3 | Architecture | review | opus-5-5 | declared: frontmatter default | 2,690,000 | 50 | 53,800 | 673% | ⚠ over cap, ⚠ density |
| docs-retrieval-3 | Implementation | build | sonnet-5-5 | declared: frontmatter default | 2,700,000 | 37 | 72,973 | 1459% | ⚠ over cap, ⚠ density |
| docs-retrieval-3-proof | Label review | review | sonnet-5-5 | declared: frontmatter default | 2,070,000 | 35 | 59,143 | 739% | ⚠ over cap, ⚠ density |
| docs-retrieval-3-proof | Scoring | review | sonnet-5-5 | declared: frontmatter default | 275,000 | 16 | 17,188 | 215% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Scope Review | review | sonnet-5-5 | declared: frontmatter default | 194,000 | 18 | 10,778 | 135% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Architecture | review | opus-5-5 | declared: frontmatter default | 825,000 | 30 | 27,500 | 344% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Implementation | build | sonnet-5-5 | declared: frontmatter default | 4,320,000 | 64 | 67,500 | 1350% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Security Review | review | opus-5-5 | declared: frontmatter default | 2,860,000 | 43 | 66,512 | 831% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | R1 fix (Security retry 1) | review | sonnet-5-5 | declared: frontmatter default | 53,000 | 5 | 10,600 | 133% | ⚠ density |
| docs-retrieval-4 | Security re-check (retry 1) | review | opus-5-5 | declared: frontmatter default | 238,000 | 12 | 19,833 | 248% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Release Gate step 1 (plan and bar) | review | sonnet-5-5 | declared: frontmatter default | 223,000 | 14 | 15,929 | 199% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Release Gate step 2 (QA run) | review | sonnet-5-5 | declared: frontmatter default | 604,000 | 23 | 26,261 | 328% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Release Gate step 3 (verdict) | review | sonnet-5-5 | declared: frontmatter default | 305,000 | 17 | 17,941 | 224% | ⚠ over cap, ⚠ density |
| docs-retrieval-4 | Close-out | review | sonnet-5-5 | declared: frontmatter default | 62,000 | 6 | 10,333 | 129% | ⚠ density |
| docs-abstention | Scope Review | review | sonnet-5-5 | declared: frontmatter default | 232,000 | 15 | 15,467 | 193% | ⚠ over cap, ⚠ density |
| docs-abstention | Baseline | review | sonnet-5-5 | declared: frontmatter default | 1,110,000 | 22 | 50,455 | 631% | ⚠ over cap, ⚠ density |
| docs-abstention | Architecture (interrupted by usage limit) | review | opus-5-5 | declared: frontmatter default | 1,700,000 | 21 | 80,952 | 1012% | ⚠ over cap, ⚠ density |
| docs-abstention | Architecture completion | review | opus-5-5 | declared: frontmatter default | 639,000 | 26 | 24,577 | 307% | ⚠ over cap, ⚠ density |
| docs-abstention | Implementation (candidate, reverted) | review | sonnet-5-5 | declared: frontmatter default | 3,150,000 | 36 | 87,500 | 1094% | ⚠ over cap, ⚠ density |
| docs-abstention | Security Review | review | opus-5-5 | declared: frontmatter default | 489,000 | 18 | 27,167 | 340% | ⚠ over cap, ⚠ density |
| docs-abstention | Release Gate | review | sonnet-5-5 | declared: frontmatter default | 483,000 | 26 | 18,577 | 232% | ⚠ over cap, ⚠ density |
| docs-abstention | Stale-text pass (README) | review | sonnet-5-5 | declared: frontmatter default | 179,000 | 29 | 6,172 | 77% | ⚠ over cap |
| docs-abstention | ARCHITECTURE.md edit | review | opus-5-5 | declared: frontmatter default | 236,000 | 27 | 8,741 | 109% | ⚠ over cap, ⚠ density |
| docs-abstention | Status-file edit | review | sonnet-5-5 | declared: frontmatter default | 63,000 | 9 | 7,000 | 88% | — |
| docs-abstention | Close-out | review | sonnet-5-5 | declared: frontmatter default | 126,000 | 11 | 11,455 | 143% | ⚠ density |
| docs-answerability-2 | Stage 1 measurement (2 judge spawns, owner-started session) | review | sonnet-5-5 | n/a | 28,517 | 0 | — | — | — |
| docs-answerability-2 | Scope Review | review | sonnet-5-5 | medium (declared) | 107,000 | 61 | 1,754 | 22% | — |
| docs-answerability-2 | Architecture pass 1 | review | opus-5-5 | high (declared) | 178,000 | 78 | 2,282 | 29% | ⚠ over cap |
| docs-answerability-2 | Architecture pass 2 | review | opus-5-5 | high (declared) | 165,000 | 69 | 2,391 | 30% | ⚠ over cap |
| docs-answerability-2 | Implementation (stage 4) | review | sonnet-5-5 | medium (declared) | 154,000 | 47 | 3,277 | 41% | ⚠ over cap |
| docs-answerability-2 | Smoke r049 + stage 5 judge spawns (49) | review | sonnet-5-5 | n/a | 386,000 | 0 | — | — | ⚠ over cap |
| docs-answerability-2 | Stage 5 scoring QA | review | sonnet-5-5 | medium (declared) | 42,000 | 10 | 4,200 | 53% | — |
| docs-answerability-2 | Stage 6 label review | review | sonnet-5-5 | high (declared) | 226,000 | 109 | 2,073 | 26% | ⚠ over cap |
| docs-answerability-2 | Stage 7 judge spawns (48, driver session) | review | sonnet-5-5 | n/a | 411,000 | 0 | — | — | ⚠ over cap |
| docs-answerability-2 | Stage 7 scoring QA | review | sonnet-5-5 | medium (declared) | 47,000 | 13 | 3,615 | 45% | — |
| docs-answerability-2 | Security Review (adversarial) | review | opus-5-5 | high (declared) | 157,000 | 54 | 2,907 | 36% | ⚠ over cap |
| docs-answerability-2 | Release Gate QA run | review | sonnet-5-5 | medium (declared) | 83,000 | 35 | 2,371 | 30% | — |
| docs-answerability-2 | Release Gate verdict (tier 2) | review | sonnet-5-5 | medium (declared) | 104,000 | 45 | 2,311 | 29% | — |
| docs-answerability-2 | Docs (Tech Writer) | review | sonnet-5-5 | medium (declared) | 65,000 | 42 | 1,548 | 19% | — |
| docs-answerability-2 | Docs finish (Architect, resumed) | review | opus-5-5 | high (declared) | 52,000 | 19 | 2,737 | 34% | — |
| docs-answerability-2 | Tier 3: monitoring plan (SRE) | review | sonnet-5-5 | medium (declared) | 58,000 | 9 | 6,444 | 81% | — |
| docs-answerability-2 | Tier 3: vendor risk and change request (Compliance Reviewer) | review | sonnet-5-5 | high (declared) | 83,000 | 31 | 2,677 | 33% | — |
| docs-answerability-2 | Tier 3: fixture dry run and audit coverage (QA) | review | sonnet-5-5 | medium (declared) | 121,000 | 44 | 2,750 | 34% | — |
| docs-answerability-2 | Release Gate verdict at tier 3 | review | sonnet-5-5 | medium (declared) | 152,000 | 56 | 2,714 | 34% | ⚠ over cap |
| docs-answerability-2 | Docs update, tier 3 state (Tech Writer) | review | sonnet-5-5 | medium (declared) | 40,000 | 8 | 5,000 | 63% | — |
| docs-answerability-2 | Docs finish, tier wording (Architect, resumed again) | review | opus-5-5 | high (declared) | 8,000 | 9 | 889 | 11% | — |
| docs-answerability-2 | Close-out (Post-Launch Learning) | review | sonnet-5-5 | medium (declared) | 105,000 | 27 | 3,889 | 49% | — |
| land-answerability | S5 fix | review | sonnet-5-5 | declared | 32,000 | 0 | — | — | — |
| land-answerability | Rollback rehearsal | review | sonnet-5-5 | declared | 32,000 | 0 | — | — | — |
| land-answerability | Vendor risk | review | sonnet-5-5 | declared | 44,000 | 0 | — | — | — |
| land-answerability | AI Governance | design | sonnet-5-5 | declared | 90,000 | 0 | — | — | — |
| land-answerability | Records and docs | review | sonnet-5-5 | declared | 97,000 | 0 | — | — | — |
| land-answerability | ARCHITECTURE.md edits | review | opus-5-5 | declared | 35,000 | 0 | — | — | — |
| land-answerability | Security re-check | review | opus-5-5 | declared | 94,000 | 0 | — | — | — |
| land-answerability | Final-tree QA | review | sonnet-5-5 | declared | 40,000 | 0 | — | — | — |
| land-answerability | Release Gate tier 3 | review | declared | declared | 187,000 | 0 | — | — | ⚠ over cap |
| public-ask-the-docs | Stage 1 scope review (engineering-manager) | review | sonnet-5-5 | declared | 46,779 | 16 | 2,924 | 37% | — |
| public-ask-the-docs | Stage 2 PRD (product-manager) | review | sonnet-5-5 | declared | 35,923 | 9 | 3,991 | 50% | — |
| public-ask-the-docs | Stage 3 feature spec (ux-researcher) | review | sonnet-5-5 | declared | 31,984 | 7 | 4,569 | 57% | — |
| public-ask-the-docs | Stage 4 UX spec (ui-designer) | review | sonnet-5-5 | declared | 26,080 | 9 | 2,898 | 36% | — |
| public-ask-the-docs | Stage 5 tech spec (software-architect) | review | opus-5-5 | declared | 214,927 | 79 | 2,721 | 34% | ⚠ over cap |
| public-ask-the-docs | Stage 6 AI governance (re-spawn) (ai-governance) | review | sonnet-5-5 | declared | 63,072 | 7 | 9,010 | 113% | ⚠ density |
| public-ask-the-docs | Stage 7 compliance (re-spawn) (compliance-reviewer) | review | sonnet-5-5 | declared | 83,754 | 21 | 3,988 | 50% | — |
| public-ask-the-docs | Patch UX copy for disclosures (ui-designer) | review | sonnet-5-5 | declared | 34,508 | 6 | 5,751 | 72% | — |
| public-ask-the-docs | Stage 8 backend service (backend-architect) | review | sonnet-5-5 | declared | 146,111 | 36 | 4,059 | 51% | — |
| public-ask-the-docs | Stage 9 Anthropic judge adapter (ai-engineer) | review | sonnet-5-5 | declared | 46,201 | 16 | 2,888 | 36% | — |
| public-ask-the-docs | Stage 10 public page (frontend-developer) | review | sonnet-5-5 | declared | 75,644 | 20 | 3,782 | 47% | — |
| public-ask-the-docs | Stage 11 infra and image (cloud-deployment) | review | sonnet-5-5 | declared | 69,025 | 25 | 2,761 | 35% | — |
| public-ask-the-docs | Amend tech spec work split (software-architect) | review | opus-5-5 | declared | 28,716 | 10 | 2,872 | 36% | — |
| public-ask-the-docs | Stage 11c Dockerfile and Azure checks (backend-architect) | review | sonnet-5-5 | declared | 53,412 | 16 | 3,338 | 42% | — |
| public-ask-the-docs | Review round 1 fixes (Backend) (backend-architect) | review | sonnet-5-5 | declared | 70,008 | 19 | 3,685 | 46% | — |
| public-ask-the-docs | Stage 13 QA evidence (qa-evidence) | review | sonnet-5-5 | declared | 144,154 | 57 | 2,529 | 32% | — |
| public-ask-the-docs | Stage 14 adversarial security review (security-privacy) | review | opus-5-5 | declared | 225,649 | 63 | 3,582 | 45% | ⚠ over cap |
| public-ask-the-docs | S-A2 SDK egress pinning (AI Engineer) (ai-engineer) | review | sonnet-5-5 | declared | 28,514 | null | — | — | — |
| public-ask-the-docs | S-A4, S-A6, S-A8 service hardening (Backend) (backend-architect) | review | sonnet-5-5 | declared | 36,185 | 11 | 3,290 | 41% | — |
| public-ask-the-docs | Stage 15a safety words and architecture doc (software-architect) | review | opus-5-5 | declared | 202,516 | null | — | — | ⚠ over cap |
| public-ask-the-docs | Stage 15b README, status, runbook (tech-writer) | review | sonnet-5-5 | declared | 118,548 | null | — | — | — |
| public-ask-the-docs | Stage 15c words check (re-spawn) (compliance-reviewer) | review | sonnet-5-5 | declared | 180,118 | 44 | 4,094 | 51% | ⚠ over cap |
| public-ask-the-docs | Apply curable safety-text rewordings (software-architect) | review | opus-5-5 | declared | 52,279 | 11 | 4,753 | 59% | — |
| public-ask-the-docs | Stage 16 Release Gate tier 3 (release-manager) | review | sonnet-5-5 | declared | 197,438 | null | — | — | ⚠ over cap |
| public-ask-the-docs | Runbook processor record and monitoring section (tech-writer) | review | sonnet-5-5 | declared | 49,605 | null | — | — | — |
| public-ask-the-docs | INV-5 reading notes N1 and N4 (software-architect) | review | opus-5-5 | declared | 38,254 | null | — | — | — |
| public-ask-the-docs | Release Manager smoke re-check, switch-on gate (release-manager) | review | sonnet-5-5 | declared | 54,024 | null | — | — | — |
| public-ask-the-docs | Stage 18 production verification (from saved evidence) (production-verification) | review | sonnet-5-5 | declared | 48,664 | null | — | — | — |
| public-ask-the-docs | Docs: record the measured figures (README, status, runbook) (tech-writer) | review | sonnet-5-5 | declared | 55,131 | null | — | — | — |
| public-ask-the-docs | Stage 19 post-launch learning (post-launch-learning) | review | sonnet-5-5 | declared | 39,124 | null | — | — | — |
| fix-service-accounting | Stage 1 scope review (engineering-manager) | review | sonnet-5-5 | medium | 64,000 | 25 | 2,560 | 32% | — |
| fix-service-accounting | Stage 2 tech spec (software-architect) | review | opus-5-5 | high | 236,000 | 72 | 3,278 | 41% | ⚠ over cap |
| fix-service-accounting | Stage 3 fixes, fail-first tests, smoke script (backend-architect, two passes) | review | sonnet-5-5 | medium | 103,000 | 26 | 3,962 | 50% | — |
| fix-service-accounting | Stage 5 QA evidence (qa-evidence) | review | sonnet-5-5 | high | 65,000 | 21 | 3,095 | 39% | — |
| fix-service-accounting | Stage 6 Security Review standard (security-privacy) | review | opus-5-5 | high | 125,000 | 33 | 3,788 | 47% | — |
| fix-service-accounting | Stage 7 docs (tech-writer) | review | sonnet-5-5 | medium | 81,000 | 26 | 3,115 | 39% | — |
| fix-service-accounting | Stage 8 Release Gate tier 3 (release-manager) | review | sonnet-5-5 | high | 117,000 | 33 | 3,545 | 44% | — |
| fix-service-accounting | Stage 10 live smoke (orchestrator) and verdict (production-verification) | review | sonnet-5-5 | medium | 46,000 | 21 | 2,190 | 27% | — |
| fix-service-accounting | Stage 11 docs addendum (tech-writer) | review | sonnet-5-5 | medium | 30,000 | 19 | 1,579 | 20% | — |
| fix-service-accounting | Stage 11 post-launch learning (post-launch-learning) | review | sonnet-5-5 | medium | 52,000 | 9 | 5,778 | 72% | — |
| polished-chat-experience | 1 Scope review | review | sonnet-5-5 | medium | 84,000 | 34 | 2,471 | 31% | — |
| polished-chat-experience | 2 UX spec | review | sonnet-5-5 | medium | 106,000 | 24 | 4,417 | 55% | — |
| polished-chat-experience | 3 Tech spec | review | opus-5-5 | high | 352,000 | 102 | 3,451 | 43% | ⚠ over cap |
| polished-chat-experience | 4 Backend | review | sonnet-5-5 | medium | 220,000 | 80 | 2,750 | 34% | ⚠ over cap |
| polished-chat-experience | 5 Frontend | review | sonnet-5-5 | medium | 150,000 | 36 | 4,167 | 52% | — |
| polished-chat-experience | 6 Review fix F2 (Backend) | review | sonnet-5-5 | medium | 14,000 | 0 | — | — | — |
| polished-chat-experience | 7 QA evidence | review | sonnet-5-5 | high | 128,000 | 47 | 2,723 | 34% | — |
| polished-chat-experience | 7b Fix Q1 Q2 (Frontend) | review | sonnet-5-5 | medium | 23,000 | 0 | — | — | — |
| polished-chat-experience | 9 Security Review | review | opus-5-5 | high | 120,000 | 34 | 3,529 | 44% | — |
| polished-chat-experience | 9b Scorecard fill (Backend) | review | sonnet-5-5 | medium | 14,000 | 0 | — | — | — |
| polished-chat-experience | 10 Docs | review | sonnet-5-5 | medium | 106,000 | 41 | 2,585 | 32% | — |
| polished-chat-experience | 10b Docs correction | review | sonnet-5-5 | medium | 16,000 | 0 | — | — | — |
| polished-chat-experience | 10b Scorecard correction (Backend) | review | sonnet-5-5 | medium | 12,000 | 0 | — | — | — |
| polished-chat-experience | 11 Release Gate | review | sonnet-5-5 | high | 126,000 | 0 | — | — | — |
| polished-chat-experience | 13 Production verification | review | sonnet-5-5 | medium | 40,000 | 0 | — | — | — |
| polished-chat-experience | 14 Post-launch learning | review | sonnet-5-5 | medium | 61,000 | 0 | — | — | — |
| result-page-clarity | 1 Tech spec | review | opus-5-5 | high | 79,000 | 32 | 2,469 | 31% | — |
| result-page-clarity | 2 Build | review | sonnet-5-5 | medium | 69,000 | 20 | 3,450 | 43% | — |
| result-page-clarity | 5 QA evidence | review | sonnet-5-5 | high | 73,000 | 23 | 3,174 | 40% | — |
| result-page-clarity | 6 Security review (smoke) | review | sonnet-5-5 | medium | 54,000 | 10 | 5,400 | 68% | — |
| result-page-clarity | 7 Docs | review | sonnet-5-5 | medium | 47,000 | 13 | 3,615 | 45% | — |
| result-page-clarity | 8 Release gate | review | sonnet-5-5 | high | 139,000 | 66 | 2,106 | 26% | — |
| result-page-clarity | 10 Production verification | review | sonnet-5-5 | medium | 58,000 | 29 | 2,000 | 25% | — |
| result-page-clarity | 11 Post-launch learning | review | sonnet-5-5 | medium | 60,000 | 16 | 3,750 | 47% | — |

## Untraced stages

Executed by the Orchestrator rather than spawned as a subagent, so they
carry no tokens or tool calls. **Every fleet and per-run figure above
excludes them** — treat slice costs as a floor, not a total.

| Run | Stage | Recorded via |
|-----|-------|-------------|
| docs-retrieval-3 | Intake | `executor` (trace@2) |
| docs-retrieval-3 | Freeze | `executor` (trace@2) |
| docs-retrieval-3-proof | Intake | `executor` (trace@2) |
| docs-retrieval-3-proof | Close-out | `executor` (trace@2) |
| docs-retrieval-4 | Intake | `executor` (trace@2) |
| docs-abstention | Intake | `executor` (trace@2) |
| land-answerability | Setup phase | `executor` (trace@2) |
| land-answerability | Code review layer (/code-review high) | `executor` (trace@2) |
| fix-service-accounting | Intake, setup, Charter | `executor` (trace@2) |
| fix-service-accounting | Stage 4 review layer (/code-review high) | `executor` (trace@2) |
| fix-service-accounting | Stage 9 deploy D1/D2 | `executor` (trace@2) |
| polished-chat-experience | 0 Intake, Charter, setup | `executor` (trace@2) |
| polished-chat-experience | 6 Code review (/code-review high, unscored) | `executor` (trace@2) |
| polished-chat-experience | 8 Browser checks | `executor` (trace@2) |
| polished-chat-experience | 12 Deploy (Charter C8.3; Cloud Deployment not spawned, D14) | `executor` (trace@2) |
| polished-chat-experience | 13 Live checks, rollback rehearsal, roll forward, cold start | `executor` (trace@2) |
| result-page-clarity | 3 Code review | `executor` (trace@2) |
| result-page-clarity | 4 Browser checks | `executor` (trace@2) |
| result-page-clarity | 9 Deploy, 10 rollback rehearsal and live checks | `executor` (trace@2) |

## Gate catches

Defects the gates caught before they shipped — the pipeline earning its keep.
**A floor, not a total:** 5 run(s) predate the `gateCatches` field (docs-retrieval, docs-retrieval-2, docs-retrieval-2-proof, docs-retrieval-3, docs-retrieval-3-proof) and recorded catches only in prose, so a real block — e.g. Security stopping the http-layer bind — is not counted here.

**Structured catches: 38**

| Run | Gate | Verdict | Severity | Finding | Recovery |
|-----|------|---------|----------|--------|----------|
| docs-retrieval-4 | Security | fail | required-fix | ADR 0006 states crash outcomes the evidence does not support (crash not reproduced) | — |
| docs-abstention | Pre-registered seen-set condition (spec 4.1) | fail | blocker | judge pooled Bar 1 2/20 vs >=16/20; method stopped before the one-shot fifth set was spent | — |
| docs-abstention | Baseline | fail | advisory | baseline on the unchanged code showed retrieve never abstains while INV-4, README and status said it did | — |
| docs-abstention | Release Gate | fail | blocker | NO-GO: bars never evaluated; model path stopped | — |
| docs-answerability-2 | Label review | fail | required-fix | One unanswerable label (gu09) ambiguous; replaced by a reserve (owner D5b). Ten answerable questions had defensible sources missing; additions applied. | — |
| docs-answerability-2 | Security | fail | required-fix | S5: quote breakout in the eval-only skill /aveto-judge-seen (single-quoted $ARGUMENTS); open, the skill is not to be used until fixed. | — |
| docs-answerability-2 | Security | fail | required-fix | S6: a wide local permission rule for seen_payload.py; the file was removed on the owner's word (verified absent). | — |
| docs-answerability-2 | Release Gate (QA run) | fail | required-fix | ruff exit 1: 23 errors in the committed security probe scripts; fixed with a first-line noqa (D6), acknowledged by the owner. | — |
| docs-answerability-2 | Release Gate (tier 3) | fail | required-fix | Six tier 3 items not met: release-action approval, change request approval, vendor risk and DPA (unknown), plus governance gates unruled; owner holds conditions T1 to T11. | — |
| land-answerability | Orchestrator code review | fail | required-fix | Run permission rules (git branch *, git commit *, ...) committed into shared .claude/settings.json | — |
| land-answerability | Security | fail | required-fix | R1: hostile-id test accepted r001\n and touched the real tree; passed only because index/models were absent | — |
| land-answerability | AI Governance | fail | required-fix | S5 fix removed test_refuses_wrong_argument_count cited by INV-5; restored | — |
| public-ask-the-docs | Orchestrator code review | fail | required-fix | CR-1: in-flight spend reservations could close the whole day for everyone (one visitor, 10 concurrent requests) | — |
| public-ask-the-docs | Orchestrator code review | fail | required-fix | CR-2: unbilled judge failures charged a full reservation, so an outage or a rejected request drains the daily share | — |
| public-ask-the-docs | Orchestrator code review | fail | advisory | CR-5, CR-6: stale day at UTC midnight; error responses skipped the page and its security headers | — |
| public-ask-the-docs | QA | fail | required-fix | QA-1: the redundant kill-switch check in the pipeline had no test (mutation survived) | — |
| public-ask-the-docs | Security | fail | required-fix | S-R1: refused-after-retrieval requests unbounded per visitor, and /health queued behind them (825 retrievals in 12 s, health 6 ms to 1.15 s) | — |
| public-ask-the-docs | Security | fail | advisory | S-A2, S-A4, S-A6, S-A8: SDK env redirect, reply-length parity, trailing-slash redirect reflecting Host, cross-site form POST (all fixed) | — |
| public-ask-the-docs | Compliance | fail | required-fix | The page copy lacked the AI-disclosure, Anthropic-as-recipient and no-personal-data lines (fixed before build) | — |
| public-ask-the-docs | Different-model words check | fail | blocker | Two Charter stops in the INV-4/INV-5 words (S10, S11b) and four wording errors; Charter v2 approved by the owner | — |
| public-ask-the-docs | Release Manager | fail | required-fix | No Approvals rows for gated actions (P1) and no processor record in the runbook (P3), fixed before deploy | — |
| public-ask-the-docs | Live first deploy | fail | blocker | F-LIVE-1: index and models written 0600 were unreadable by the runtime uid, container crash-looped (startup_failed index); Dockerfile fixed, rebuilt, redeployed | — |
| public-ask-the-docs | Live first call | fail | blocker | First judge call returned judge error: the stored key was bad (cause not logged by design); owner re-stored it, kill switch back on at once, second call answered | — |
| fix-service-accounting | Setup baseline | fail | required-fix | test_core_files_unchanged red on main after pack v28 added event-log.mjs; repaired test-only under Charter C1.4 | — |
| fix-service-accounting | Scope review | fail | advisory | #7 needs the adapter to carry earlier billable attempts out; anthropic_judge.py and judge_port.py join the diff | — |
| fix-service-accounting | Orchestrator code review | pass | advisory | 5 findings, 0 Important: CR-3 (day pauses at about 33, not 41) routed to Docs and Security | — |
| fix-service-accounting | Security | pass | advisory | A1: connection error then success now charges usage only (a dropped read may hide a billed attempt); A2: 429 not billed is unconfirmed; owner decisions | — |
| fix-service-accounting | Release Manager | pass | required-fix | GO WITH CONDITIONS: P2 re-run of nothing-else-moves on the final tree, P4 smoke.py unreviewed until read, P5 budget notice | — |
| fix-service-accounting | Live smoke tooling | fail | advisory | watch on failed TLS verification on every poll (local python.org CA bundle), D1 toggle time not measured; smoke ask needed PYTHONPATH | — |
| polished-chat-experience | Scope review | fail | required-fix | Refusal card 'nearest passages' contradicts INV-4(b); run took the in-Charter path (no passages), D1 | — |
| polished-chat-experience | Code review | fail | required-fix | F2: warm() cached a failed warm-up for the life of the process; fixed f5c139c | — |
| polished-chat-experience | QA | fail | required-fix | Q1: client-side empty/over-limit guard dropped while copy still said 'Nothing was sent'; fixed 6c32de1 | — |
| polished-chat-experience | QA | fail | required-fix | Q2/Q3: waiting copy and a scorecard basis claimed things with no record; reworded | — |
| polished-chat-experience | Security | pass | advisory | S1 result-store bound corrects code-review F1 (judge-error results stored at zero spend); S2 counts can be inflated; no P0/P1 | — |
| polished-chat-experience | Release Gate | pass | advisory | GO WITH CONDITIONS: live.py had never been run; dry-run against the local server before the build | — |
| polished-chat-experience | Production verification | pass | advisory | Record gaps: first check-new overwritten, empty search output, idle time claim; corrected in 13-live/README.md | — |
| result-page-clarity | Baseline | fail | required-fix | main 6ab5548 had one failing test (stale budget-guard hash pin after the pack v30 install) and one ruff error; fixed under Charter C1.7 | — |
| result-page-clarity | Release gate (rollback rehearsal timing) | open | required-fix | time from the rollback command to a first healthy /health was not polled (wrong baseline in the check script); owner to rule, see END_REVIEW.md | — |


## Outliers

- **Implementation of embed-v3 (resumed)** (docs-retrieval, review): 155,759 tok / 41 calls — 1.0× the 150k per-stage token cap
- **Scope Review** (docs-retrieval-3, review): 402,000 tok / 22 calls — 2.7× the 150k per-stage token cap; 2.3× the 8.0k review-density cap
- **Architecture** (docs-retrieval-3, review): 2,690,000 tok / 50 calls — 17.9× the 150k per-stage token cap; 6.7× the 8.0k review-density cap
- **Implementation** (docs-retrieval-3, build): 2,700,000 tok / 37 calls — 18.0× the 150k per-stage token cap; 14.6× the 5.0k build-density cap
- **Label review** (docs-retrieval-3-proof, review): 2,070,000 tok / 35 calls — 13.8× the 150k per-stage token cap; 7.4× the 8.0k review-density cap
- **Scoring** (docs-retrieval-3-proof, review): 275,000 tok / 16 calls — 1.8× the 150k per-stage token cap; 2.1× the 8.0k review-density cap
- **Scope Review** (docs-retrieval-4, review): 194,000 tok / 18 calls — 1.3× the 150k per-stage token cap; 1.3× the 8.0k review-density cap
- **Architecture** (docs-retrieval-4, review): 825,000 tok / 30 calls — 5.5× the 150k per-stage token cap; 3.4× the 8.0k review-density cap
- **Implementation** (docs-retrieval-4, build): 4,320,000 tok / 64 calls — 28.8× the 150k per-stage token cap; 13.5× the 5.0k build-density cap
- **Security Review** (docs-retrieval-4, review): 2,860,000 tok / 43 calls — 19.1× the 150k per-stage token cap; 8.3× the 8.0k review-density cap
- **R1 fix (Security retry 1)** (docs-retrieval-4, review): 53,000 tok / 5 calls — 1.3× the 8.0k review-density cap
- **Security re-check (retry 1)** (docs-retrieval-4, review): 238,000 tok / 12 calls — 1.6× the 150k per-stage token cap; 2.5× the 8.0k review-density cap
- **Release Gate step 1 (plan and bar)** (docs-retrieval-4, review): 223,000 tok / 14 calls — 1.5× the 150k per-stage token cap; 2.0× the 8.0k review-density cap
- **Release Gate step 2 (QA run)** (docs-retrieval-4, review): 604,000 tok / 23 calls — 4.0× the 150k per-stage token cap; 3.3× the 8.0k review-density cap
- **Release Gate step 3 (verdict)** (docs-retrieval-4, review): 305,000 tok / 17 calls — 2.0× the 150k per-stage token cap; 2.2× the 8.0k review-density cap
- **Close-out** (docs-retrieval-4, review): 62,000 tok / 6 calls — 1.3× the 8.0k review-density cap
- **Scope Review** (docs-abstention, review): 232,000 tok / 15 calls — 1.5× the 150k per-stage token cap; 1.9× the 8.0k review-density cap
- **Baseline** (docs-abstention, review): 1,110,000 tok / 22 calls — 7.4× the 150k per-stage token cap; 6.3× the 8.0k review-density cap
- **Architecture (interrupted by usage limit)** (docs-abstention, review): 1,700,000 tok / 21 calls — 11.3× the 150k per-stage token cap; 10.1× the 8.0k review-density cap
- **Architecture completion** (docs-abstention, review): 639,000 tok / 26 calls — 4.3× the 150k per-stage token cap; 3.1× the 8.0k review-density cap
- **Implementation (candidate, reverted)** (docs-abstention, review): 3,150,000 tok / 36 calls — 21.0× the 150k per-stage token cap; 10.9× the 8.0k review-density cap
- **Security Review** (docs-abstention, review): 489,000 tok / 18 calls — 3.3× the 150k per-stage token cap; 3.4× the 8.0k review-density cap
- **Release Gate** (docs-abstention, review): 483,000 tok / 26 calls — 3.2× the 150k per-stage token cap; 2.3× the 8.0k review-density cap
- **Stale-text pass (README)** (docs-abstention, review): 179,000 tok / 29 calls — 1.2× the 150k per-stage token cap
- **ARCHITECTURE.md edit** (docs-abstention, review): 236,000 tok / 27 calls — 1.6× the 150k per-stage token cap; 1.1× the 8.0k review-density cap
- **Close-out** (docs-abstention, review): 126,000 tok / 11 calls — 1.4× the 8.0k review-density cap
- **Architecture pass 1** (docs-answerability-2, review): 178,000 tok / 78 calls — 1.2× the 150k per-stage token cap
- **Architecture pass 2** (docs-answerability-2, review): 165,000 tok / 69 calls — 1.1× the 150k per-stage token cap
- **Implementation (stage 4)** (docs-answerability-2, review): 154,000 tok / 47 calls — 1.0× the 150k per-stage token cap
- **Smoke r049 + stage 5 judge spawns (49)** (docs-answerability-2, review): 386,000 tok / 0 calls — 2.6× the 150k per-stage token cap
- **Stage 6 label review** (docs-answerability-2, review): 226,000 tok / 109 calls — 1.5× the 150k per-stage token cap
- **Stage 7 judge spawns (48, driver session)** (docs-answerability-2, review): 411,000 tok / 0 calls — 2.7× the 150k per-stage token cap
- **Security Review (adversarial)** (docs-answerability-2, review): 157,000 tok / 54 calls — 1.0× the 150k per-stage token cap
- **Release Gate verdict at tier 3** (docs-answerability-2, review): 152,000 tok / 56 calls — 1.0× the 150k per-stage token cap
- **Release Gate tier 3** (land-answerability, review): 187,000 tok / 0 calls — 1.2× the 150k per-stage token cap
- **Stage 5 tech spec (software-architect)** (public-ask-the-docs, review): 214,927 tok / 79 calls — 1.4× the 150k per-stage token cap
- **Stage 6 AI governance (re-spawn) (ai-governance)** (public-ask-the-docs, review): 63,072 tok / 7 calls — 1.1× the 8.0k review-density cap
- **Stage 14 adversarial security review (security-privacy)** (public-ask-the-docs, review): 225,649 tok / 63 calls — 1.5× the 150k per-stage token cap
- **Stage 15a safety words and architecture doc (software-architect)** (public-ask-the-docs, review): 202,516 tok / null calls — 1.4× the 150k per-stage token cap
- **Stage 15c words check (re-spawn) (compliance-reviewer)** (public-ask-the-docs, review): 180,118 tok / 44 calls — 1.2× the 150k per-stage token cap
- **Stage 16 Release Gate tier 3 (release-manager)** (public-ask-the-docs, review): 197,438 tok / null calls — 1.3× the 150k per-stage token cap
- **Stage 2 tech spec (software-architect)** (fix-service-accounting, review): 236,000 tok / 72 calls — 1.6× the 150k per-stage token cap
- **3 Tech spec** (polished-chat-experience, review): 352,000 tok / 102 calls — 2.3× the 150k per-stage token cap
- **4 Backend** (polished-chat-experience, review): 220,000 tok / 80 calls — 1.5× the 150k per-stage token cap

## Baselines

- Per-stage token cap: **150,000** · Slice envelope: **stages × 100,000**
- Density caps: **design** 15,000 · **review** 8,000 · **build** 5,000 (tok/call)
