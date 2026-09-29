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

## Owner answers — 2026-09-29T01:31:40Z

Prompted with options, the owner (Gopal Patwa) selected, verbatim:

1. **How fresh questions are used:** "Freeze first; held-out set is the gate (Recommended)".
   Order: revise → implement → **STOP before any eval run** → record that commit
   SHA as the frozen method → owner writes and commits the fresh set (e.g.
   `evals/retrieval-heldout.toml`) after that SHA → run once. **Gate = ≥80% on
   the held-out set**; `evals/retrieval.toml` becomes a dev-set diagnostic. No
   change to the method between the owner's commit and the run. The eval command
   already takes `--eval-file`, so no code change is needed to score it.
   *This amends Done-means item 8 in the intent. The owner owns `intent.md` and
   should amend that line on `main`; the slice copy stays a byte-identical copy
   until then.*
2. **Embeddings:** "Allow a local embedding model". **This is not an approval of
   any specific dependency.** A concrete model, its weights source and its
   download are a new dependency and network call in the build path (rule 5),
   would break INV-5 as written (only network egress = the pinned GitHub fetch;
   changing it is a safety-control change, rule 4), and contradicts the intent's
   "no model is called anywhere" (Done-means, Out of scope). Each needs its own
   explicit approval before implementation.

## Architect's v2 (retry 1), for the record

Lexical only: Porter stemmer, 0.5 × passage BM25 + 0.5 × file BM25, and a
"corroboration" confidence rule; the τ=1.0 was a flaw in the coverage formula.
Pre-registered in 02-tech-spec.md ("Retrieval — variant v2"), 18 files still.
Architect's prediction: ungated recall@5 ≈ 17/24 (range 15–20); ≈15% chance of
passing both bars. It recommends option B (record the ceiling, then an
embeddings decision) rather than a third lexical variant if v2 misses.

## Owner choice — 2026-09-29T01:32:19Z

"Design an embeddings variant first" (verbatim option label). Spec-only: the
Architect writes an embeddings variant with approval-ready facts; nothing is
implemented, added or approved by this. Budget: per-spawn check passes (482k ≤
820k); the later stages project ≈910k vs 820k, so the owner is asked again before
Implementation. This choice is not read as approval of that overspend.

## Owner choice — 2026-09-29T03:46:06Z

Prompted with the Architect's recommendation against it, the owner selected,
verbatim: "Pursue embed-v3 in this slice". **This grants no gated approval.**
Each of these still needs its own explicit yes before anything is installed or
downloaded: rule 5 (a model in the retrieval path), rule 5 (weights download in
ingest and CI), rule 4 (INV-4/INV-5 wording), and the budget increase.

Facts re-checked by the Orchestrator on 2026-09-29T03:46:06Z against Hugging Face metadata
(read-only API and HEAD request; no file downloaded): revision
5c38ec7c405ec4b44b94cc5a9bb96e735b38267a, licence MIT, onnx/model.onnx
133,093,490 bytes sha256 828e1496…cf35, vocab.txt 231,508 bytes, config.json 743
bytes, and a 302 from huggingface.co to us.aws.cdn.hf.co. Not independently
verified: the sha256 of vocab.txt/config.json/tokenizer_config.json (reported by
the playbook session only) and the ONNX graph's input names (needs the 133 MB
download, which needs approval).

## EM re-scope ruling — 2026-09-29T03:53:07Z

The EM (not the owner's choice ratified) rules the embed-v3 work **must split**:
- **docs-retrieval-core** stays lexical v2, Tier 2, ≈812k of 820k, no retry headroom.
- **docs-retrieval-embed** = embed-v3, Tier 3, ≈645k on its own budget (Architect 40k
  + Implementation 195k + QA 160k + Security 130k + Release Gate 120k, +60k re-run reserve).
- Splitting costs ≈390k more than one slice and, if v2 misses, the owner writes a
  second held-out set. Keeping one slice: ≈1,067–1,127k (247–307k over 820k).
- 19 Implementation files accepted (embed.py its own module); the 2 QA/owner files
  (golden tokenizer fixture, frozen off-topic list) count toward the diff but
  Implementation must not author or edit them.
No gated approval is requested yet. Details: 01-scope.md, latest dated amendment.

## Owner choice — 2026-09-29T05:25:45Z

Prompted with the EM's ruling that embed-v3 must split, the owner selected,
verbatim: "Keep one slice with embed-v3". **This knowingly overrides the EM's scope
ruling** (01-scope.md). It grants no gated approval and sets no budget number.
Projection for one slice: ≈1,067–1,127k vs the 820k budget (247–307k over).
Pending, each asked individually: APPROVAL_REQUEST-2 (rule 5, model), -3 (rule 5,
weights download), -4 (rule 4, INV-5/INV-4 wording), and a budget number.
Intent amendments: see INTENT_AMENDMENT_PROPOSAL.md.
