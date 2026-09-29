# Pipeline Analytics — generated

_Generated 2026-09-29T16:21:59Z. **Do not edit by hand** — regenerate with `node <playbook>/execution/analyze.mjs .` from the repo root._

## Fleet

- Runs traced: **1**
- Stages: **15** · Tokens: **853,934** · Tool calls: **336**
- Envelope breaches: **0/1** · Stage outliers: **1**

## Per run

| Run | Tier | Stages | Tokens | Calls | Envelope | Status |
|-----|------|--------|--------|-------|----------|--------|
| docs-retrieval | 2 | 15 | 853,934 | 336 | 1,500,000 | ✅ pass |

## Pipeline completeness

Declared-vs-actual against the 12-stage lifecycle (`AGENTIC_SDLC.md`). An
**always** node missing is a real gap; a **conditional** node missing may be a
legitimate compression (`AGENTIC_SDLC.md` § "When to compress stages") — not
flagged either way, just listed, since only the EM's recorded rationale (not
this table) can say whether a given skip was earned.

| Run | Missing (always) | Skipped (conditional) | Unrecognized stage name |
|-----|-------------------|------------------------|--------------------------|
| docs-retrieval | ⚠ Intake, Release Gate | Market Research, Discovery, UX Research, UI Design, Security Review | — |

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
| **review** | read artefacts → verdict | 8,000 | 13 | 1,283–3,489 | 2,234 |
| **build** | heavy file / test I/O | 5,000 | 1 | 3,828–3,828 | 3,828 |

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

## Untraced stages

None — every stage in every run reported its own telemetry.

## Gate catches

Defects the gates caught before they shipped — the pipeline earning its keep.
**A floor, not a total:** 1 run(s) predate the `gateCatches` field (docs-retrieval) and recorded catches only in prose, so a real block — e.g. Security stopping the http-layer bind — is not counted here.

None structurally recorded yet.

## Outliers

- **Implementation of embed-v3 (resumed)** (docs-retrieval, review): 155,759 tok / 41 calls — 1.0× the 150k per-stage token cap

## Baselines

- Per-stage token cap: **150,000** · Slice envelope: **stages × 100,000**
- Density caps: **design** 15,000 · **review** 8,000 · **build** 5,000 (tok/call)
