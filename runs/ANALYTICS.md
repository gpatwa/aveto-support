# Pipeline Analytics — generated

_Generated 2026-09-30T01:37:41Z. **Do not edit by hand** — regenerate with `node <playbook>/execution/analyze.mjs .` from the repo root._

## Fleet

- Runs traced: **3**
- Stages: **23** · Tokens: **1,240,328** · Tool calls: **484**
- Envelope breaches: **0/3** · Stage outliers: **1**

## Per run

| Run | Tier | Stages | Tokens | Calls | Envelope | Status |
|-----|------|--------|--------|-------|----------|--------|
| docs-retrieval | 2 | 15 | 853,934 | 336 | 1,500,000 | ✅ pass |
| docs-retrieval-2 | 2 | 5 | 311,729 | 118 | 500,000 | ✅ pass |
| docs-retrieval-2-proof | 2 | 3 | 74,665 | 30 | 300,000 | ✅ pass |

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

## DORA

Per `PIPELINE_SLOS.md` § DORA mapping. **Only metrics the traces ground are reported** — anything without data says so.

| Metric | Value | Basis |
|--------|-------|-------|
| Lead time (median) | — | intake → landed, 0/0 slices dated |
| Deployment frequency | — | 0 landed over the traced span |
| Change failure rate | — | 0 post-landing fixes + 0 reverts ÷ 0 landed |
| Rework rate | — | 0 stage retries + 0 post-landing fixes ÷ 0 landed |
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

## Untraced stages

None — every stage in every run reported its own telemetry.

## Gate catches

Defects the gates caught before they shipped — the pipeline earning its keep.
**A floor, not a total:** 3 run(s) predate the `gateCatches` field (docs-retrieval, docs-retrieval-2, docs-retrieval-2-proof) and recorded catches only in prose, so a real block — e.g. Security stopping the http-layer bind — is not counted here.

None structurally recorded yet.

## Outliers

- **Implementation of embed-v3 (resumed)** (docs-retrieval, review): 155,759 tok / 41 calls — 1.0× the 150k per-stage token cap

## Baselines

- Per-stage token cap: **150,000** · Slice envelope: **stages × 100,000**
- Density caps: **design** 15,000 · **review** 8,000 · **build** 5,000 (tok/call)
