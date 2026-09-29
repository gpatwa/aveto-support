# Approval Request 2 — retrieval stops abstaining: it always returns its top 5 files (rule 4)

- **Slice:** docs-retrieval-2
- **Rule:** HUMAN_APPROVAL_RULES §4 — changes to safety controls
- **Requested:** 2026-09-29T16:52:18Z. **Only needed if this reading of the intent is right.** The intent does not say it in these words; the Orchestrator infers it (see the plan, "Interpretations").

## What

Today `retrieve` prints "no confident match" and returns **no** passages when the best dense similarity is below a calibrated cutoff (INV-4's second clause; enforced by `test_not_confident_returns_no_hits`; the cutoff is calibrated at `ingest` from word salads and the frozen off-topic list pinned in `docs-source.toml`). Decision 1 says abstention moves to the check step and retrieval is scored on "a correct file in the top 5", which a withheld result can never satisfy. So retrieval would **always return its top 5 files** (with the passages that matched, their headings and line ranges, and its **top score printed**) and **stop deciding abstention**. The calibration and the off-topic list become unused by retrieval (the Architect decides whether to keep them as a diagnostic). INV-4's first clause still holds: everything returned is a verbatim passage with provenance, nothing is presented as an answer.

## Why

A gate on "correct file in the top 5" is only meaningful if the result is not withheld. Two methods could not make the cutoff work.

## What is reversible if denied

Retrieval keeps abstaining as in slice 1, and then the gate must either count a withheld result as a miss (making the 80% bar harder) or be rescored ungated, which is a different gate. The Orchestrator would ask the owner which before any implementation.

## The smallest request

Retrieval stops emitting "no confident match" and always returns its top 5 files with the top score. It is not approval for anything generative, a new model, or any wider network access, and it does not decide the check step's design.
