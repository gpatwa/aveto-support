# Pipeline Analytics — generated

_Generated 2026-10-09T05:08:54Z. **Do not edit by hand** — regenerate with `node <playbook>/execution/analyze.mjs .` from the repo root._

## Fleet

- Runs traced: **6**
- Stages: **38** · Tokens: **19,061,328** · Tool calls: **876**
- **Untraced stages: 5** across 3 run(s) — executed by the Orchestrator rather than spawned, so they carry no tokens or tool calls
- Envelope breaches: **3/6** · Stage outliers: **16**

## Per run

| Run | Tier | Stages | Tokens | Calls | Envelope | Status |
|-----|------|--------|--------|-------|----------|--------|
| docs-retrieval | 2 | 15 | 853,934 | 336 | 1,500,000 | ✅ pass |
| docs-retrieval-2 | 2 | 5 | 311,729 | 118 | 500,000 | ✅ pass |
| docs-retrieval-2-proof | 2 | 3 | 74,665 | 30 | 300,000 | ✅ pass |
| docs-retrieval-3 | 2 | 5 | 5,792,000 | 109 | 300,000 | ❌ over 5492k |
| docs-retrieval-3-proof | 2 | 4 | 2,345,000 | 51 | 200,000 | ❌ over 2145k |
| docs-retrieval-4 | 2 | 11 | 9,684,000 | 232 | 1,000,000 | ❌ over 8684k |

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

## DORA

Per `PIPELINE_SLOS.md` § DORA mapping. **Only metrics the traces ground are reported** — anything without data says so.

| Metric | Value | Basis |
|--------|-------|-------|
| Lead time (median) | — | intake → landed, 0/0 slices dated |
| Deployment frequency | — | 0 landed over the traced span |
| Change failure rate | — | 0 post-landing fixes + 0 reverts ÷ 0 landed |
| Rework rate | — | 2 stage retries + 0 post-landing fixes ÷ 0 landed |
| Failed-deployment recovery time | **not captured** | needs `detectedAt`/`resolvedAt` on a `gateCatches` entry; no run has recorded them |

## Density by archetype

Tokens per tool call, measured against each archetype's own cap.

| Archetype | What it does | Cap | Observed (n) | Range | Avg |
|-----------|--------------|-----|--------------|-------|-----|
| **review** | read artefacts → verdict | 8,000 | 20 | 654–3,489 | 2,207 |
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

## Gate catches

Defects the gates caught before they shipped — the pipeline earning its keep.
**A floor, not a total:** 5 run(s) predate the `gateCatches` field (docs-retrieval, docs-retrieval-2, docs-retrieval-2-proof, docs-retrieval-3, docs-retrieval-3-proof) and recorded catches only in prose, so a real block — e.g. Security stopping the http-layer bind — is not counted here.

**Structured catches: 1**

| Run | Gate | Verdict | Severity | Finding | Recovery |
|-----|------|---------|----------|--------|----------|
| docs-retrieval-4 | Security | fail | required-fix | ADR 0006 states crash outcomes the evidence does not support (crash not reproduced) | — |


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

## Baselines

- Per-stage token cap: **150,000** · Slice envelope: **stages × 100,000**
- Density caps: **design** 15,000 · **review** 8,000 · **build** 5,000 (tok/call)
