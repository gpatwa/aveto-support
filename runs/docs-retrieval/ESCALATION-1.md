# Escalation 1 — eval run 1 missed the ≥80% bar (docs-retrieval-core)

- **Slice / stage:** docs-retrieval-core, Implementation → eval gate
- **Category:** gate-violation (the gate cannot be passed honestly by the method as specified)
- **Raised:** 2026-09-29T00:27:40Z. Escalated **early** (retry 1 of 2 unspent) for the reasons below.

## What was attempted

Implementation built the spec exactly (18 files, EM-accepted; 80 tests, strict mypy
and ruff pass; ingest twice → byte-identical, sha256 41d7ee3b…, 126 files / 910
passages). Eval ran **once**, per the spec's overfitting protocol. Nothing was tuned.
Raw output: `runs/docs-retrieval/eval-run-1.txt`.

| Group | Result | Required | |
|---|---|---|---|
| Answerable | **2 / 24** | ≥ 20 | FAIL |
| Unanswerable | 6 / 6 | ≥ 5 | PASS (but only because nearly everything is withheld) |
| Diagnostic: ungated recall@5 | **14 / 24** | — | not a gate |

## The persistent failure

The calibrated confidence threshold came out at 1.000 (p90 of the null-query
coverage), so 22 of 24 answerable questions were withheld. That is a consequence of
the pre-registered method, not a bug. But **the threshold is not the binding
constraint**: even with a perfect cutoff, ranking alone puts a correct source in
the top 5 for only 14 of 24 (58%). The bar needs 20. Plain lexical (BM25) ranking
would need to gain at least 6 questions of recall before any cutoff could pass.

## Why this is escalated now, with a retry left

1. **New information.** The ungated diagnostic shows threshold work cannot fix this;
   only ranking changes can, and every ranking change made after seeing
   `eval-run-1.txt` is informed by the test set (spec, "Overfitting protocol" §7:
   after any revision the 30 questions are no longer unseen).
2. **Budget.** Spent 328k of 690k. One retry (Architect revision ≈100k+, rework
   ≈60k) plus QA 130k, Security 100k, Release Gate 100k projects to ≈ 818k, over the
   690k budget. RUN_ECONOMICS §2: degrade, drop, or ask the human — never raise the
   budget to fit the spend.
3. FAILURE_LOOP: "a loop with no new information after one retry is already a
   signal" — here the first attempt already tells us the retry has a hard ceiling.

## Smallest decisions the owner could make (see the driving session)

- **A. Spend retry 1 as the spec plans:** the Architect revises the *method* on
  general grounds as a versioned variant (ranking, not threshold), run once more.
  Needs a budget decision (≈818k projected vs 690k), and the result is no longer
  held-out evidence; the spec recommends the owner then write a small fresh set.
- **B. Stop core here and record the finding:** plain lexical retrieval reaches
  14/24 recall on these questions. Embeddings would add a dependency or a model
  call (approval rules 5 and 6), which is the owner's decision and a different slice.
- **C. Lower the ≥80% bar.** Not recommended: weakening a gate is approval rule 4,
  and it would need the owner's explicit approval.

## Resolution — 2026-09-29T00:41:49Z

Owner (Gopal Patwa) chose **A**. Verbatim: "A, and I'll write the fresh questions".

- Retry 1 of 2 is spent on a **ranking** revision by the Architect (a versioned
  variant in the tech spec, recorded before it is run). Model class unchanged;
  the final retry (if any) escalates one class per FAILURE_LOOP.
- Option A as presented included accepting ≈818k projected against 690k. The
  Orchestrator read the choice of A as accepting that, and set the Budget line to
  820k. **Assumption: if this is wrong, the owner should say so.**
- The owner writes a small **fresh held-out question set**. Handling: it is kept
  out of this repo/worktree until QA (stage 9); no role except QA reads it; the
  Architect and engineer must not. The owner supplies a sha256 of the file now
  so the record shows it existed before the revision was tuned.
- `eval-run-1.txt` stays as committed. The original 30 questions are no longer
  unseen evidence (spec, Overfitting protocol §7).
