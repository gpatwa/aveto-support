# Slice plan — docs-abstention

> Orchestrator, Intake. Source of truth for what was asked: `runs/docs-abstention/intent.md`
> (a byte-identical copy of `intents/docs-abstention.md`, committed 523e7d1, confirmed 2026-10-08).
> Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` @ 3b07317211f22e38c0111cd2fd40e021710c8b5c (pack v15).
> **Status: awaiting the owner's confirmation. Nothing is spawned until then.**

## Outcome (one line)

`retrieve` and `eval` can say `no confident match` when the docs do not answer the question. The method is chosen
from a baseline measured on the four seen sets, frozen, then scored once on a fifth held-out set against two bars set in advance.

## Stages

Units are **peak context per spawn** (RUN_ECONOMICS.md §1). Review stages are estimated at 50–60k, or 100–130k at
adversarial depth, each with a tight read list. The budget is checked (`spent + estimate ≤ budget`) before every spawn.
Every spawn is a fresh agent and none is resumed. Spent and Model come from `usage.mjs` after each stage.

### Slice A: up to and including the freeze (330k)

| # | Stage | Role (agent) | Depth | Est. | Output |
|---|-------|--------------|-------|------|--------|
| A1 | Scope Review | engineering-manager | standard | 50k | `01-scope.md` |
| A2 | Baseline measurement on the unchanged code: top-1 score, top-1 minus top-2 margin, and rank of the correct file, for all 93 seen questions (73 answerable, 20 unanswerable). It re-measures the intent's overlap paragraph and argues no cause. | qa-evidence (has a shell; the Architect does not) | standard | 60k | `02-baseline.md` + raw `02-baseline-*.txt` |
| A3 | Architecture: reads A2, then sweeps the threshold and margin rules against both bars on the seen sets. If neither rule passes with room to spare, it argues **one** model on general grounds, with an ADR covering licence and training data. Writes the exact INV-4 sentence (and the INV-5 change if a model is added). | software-architect | standard | 70k | `02-tech-spec.md` (+ ADR if a model) |
| — | **Owner approvals:** rule 4 (the INV-4 sentence), plus rule 5 and the INV-5 rule 4 change if a model is added. You type each one in this session, and each goes into an `APPROVAL_RECORD-N.md` in your words. | Orchestrator | — | 0 | approval records |
| A4 | Implementation: method, `no confident match` output with the deciding signal, tests, INV-4 (and INV-5) text, regression green | backend-architect (ai-engineer if a model is added) | standard | 130k | `03-implementation.md` |
| — | **Freeze:** method commit recorded in STATE.md before any gate-set file enters the repo | Orchestrator | — | 0 | STATE.md |
| | **Slice A total** | | | **310k** | reserve 20k |

### Slice B: after the freeze (320k)

| # | Stage | Role (agent) | Depth | Est. | Output |
|---|-------|--------------|-------|------|--------|
| — | The fifth set is delivered by the "Aveto AI SDLC" session. I have not read it and the builder never wrote it. | (other session) | — | 0 | file outside the repo |
| B1 | Label review: every label, with **every unanswerable label tested by trying to find a defensible answer in the docs**. The reviewer drops or reclassifies questions. It gets the questions and the docs, not the method or any result. After that the Orchestrator commits the set. | qa-evidence (fresh) | standard | 80k | `05-label-review.md` |
| B2 | Scoring: run once at the frozen commit against both bars, plus all the diagnostics the intent lists, plus full regression | qa-evidence (a different fresh spawn) | standard | 50k | `06-qa-result.md` + raw outputs |
| B3 | Security Review: **adversarial** on INV-4 (and on any new download path) | security-privacy | adversarial | 100k (130k if a model was added) | `04-security-review.md` |
| B4 | Release Gate, tier 2: one verdict spawn. The bars were committed in the intent (523e7d1) before any run, so a separate bar-commit step is not needed. | release-manager | standard | 55k | `06-release-checklist.md` |
| B5 | Close-out, then I regenerate `runs/ANALYTICS.md` and `runs/dashboard.html` | post-launch-learning | standard | 25k | `07-close-out.md` |
| | **Slice B total** | | | **310k** | reserve 10k |

**Total: 620k of 650k.** On the **model path** the budget is likely to run out: A4 tends toward its 178k worst
case, and B3 is 130k, which puts slice B at 340k against 320k. In that case I stop and ask you with the numbers.
I won't compress Security or the Release Gate to fit, and I won't raise the budget myself.

Gates (RELEASE_GATES.md, tier 2) fail closed between stages. The retry cap is 2 per stage, per FAILURE_LOOP.md. A failed
bar is a result, and nothing gets tuned afterwards to pass it.

## Success criteria (from the intent's "Done means")

1. Baseline first, on seen sets only. A model is added only if neither threshold nor margin meets both bars there with room to spare.
2. Freeze, then commit the fifth set (≥24 unanswerable, at least half of them hard negatives, and ≥24 answerable), labels reviewed first, then run once.
3. **Bar 1:** abstains on at least 80% of the unanswerable questions. **Bar 2:** does not abstain on at least 80% of the answerable
   questions whose correct file was in the top 5. Both must pass, and neither moves after a result.
4. Diagnostics in the same run: the end-to-end figure, the baseline method (and any earlier one) on the same set, abstention on the four seen sets,
   and the top-score distributions for abstained and answered questions.
5. An abstention prints exactly `no confident match` with no passages, exits 0, and names the deciding signal. Retrieved text stays verbatim.
6. INV-4 gains one approved sentence. INV-5 names the pin only if a model is added.
7. Security (adversarial) and the Release Gate run once. The only possible verdicts are "internally releasable, not announced"
   (both bars pass) and "not releasable" (with the reason).
8. The README status line and CURRENT_MVP_STATUS state the whole-pipeline figure and nothing stronger.
9. Every earlier guarantee still holds: deterministic ingest, provenance, no generative model, no new network, every model file hash-checked, retrieve offline.

## Non-goals

The INV-3 draft checker, any generative model or drafting, changes to the corpus, ranking or embeddings, reopening the reranker,
`docs-retrieval-ci`, and posting anywhere.

## Constraints

From `.agentic/` and the intent: Python 3.12 with uv, runtime dependencies onnxruntime and numpy only, at most one new model (ONNX,
pinned revision, sha256 per file, no PyTorch, no `trust_remote_code`). Nothing is chosen by its score on the gate set. There is
no metered API, no `claude -p`, no Azure, no API key, no deploy, no push, merge or PR, and no credentials. Approvals count only
when you type them in this session.

## Notes for the owner

- The intent's first "Done means" line says "pack v14". The repo is now on v15 (0dfd433). The intent is copied unchanged,
  and the line's substance (slice 4 merged, `file-rrf-v1` the default) holds.
- The Architect has no shell under least privilege, so the baseline is measured by a separate spawn (A2) that argues no cause.
