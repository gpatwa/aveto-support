# Escalation 2 — held-out gate failed on the frozen method (docs-retrieval-core)

- **Slice / stage:** docs-retrieval-core, eval gate (Done-means: ≥80% on the held-out set)
- **Category:** gate-violation (the gate cannot be passed honestly by the method as built)
- **Raised:** 2026-09-29T15:52:39Z. Escalated **early** (retry 2 of 2 unspent) for the reasons below.

## What was attempted

Retry 1 was the method revision after eval run 1: lexical v2 pre-registered, then the
owner chose embed-v3 (BAAI/bge-small-en-v1.5 fused with BM25, dense confidence calibrated
on the frozen off-topic list). Frozen at commit `c9b64e7`, verified unchanged. The owner's
held-out set (`de8b0b6`, 17 answerable + 6 unanswerable) was scored **once** by QA, then the
dev set once as a diagnostic. Raw outputs: `eval-run-2-heldout.txt`, `eval-run-3-dev-diagnostic.txt`.

| Set | Answerable (bar) | Unanswerable (bar) | Ungated recall@5 |
|---|---|---|---|
| **Held-out (the gate)** | **5/17 = 29.4%** (≥14) **FAIL** | 5/6 = 83.3% (≥5) PASS | **8/17 = 47%** |
| Dev set (diagnostic; seen) | 10/24 = 41.7% | 4/6 = 66.7% | 17/24 = 71% |
| For comparison: run 1 (lexical v1, dev) | 2/24 | 6/6 | 14/24 = 58% |

## The persistent failure

Same shape as run 1, with a better method. 10 of 12 held-out answerable misses are
below-threshold abstentions (similarity 0.62–0.69 vs τ 0.702); 2 are confident wrong
passages. But **the threshold is again not the binding constraint**: even with no
abstention at all, the correct source is in the top 5 for only **8 of 17** unseen
questions (47%) and 17/24 (71%) on the questions the method was designed after seeing.
The bar needs 14/17. Removing the cutoff could gain at most 3 questions.
The unanswerable pass is thin (5/6, exactly the bar) and one unanswerable question (hu02)
overlaps a calibration question's subject, so it is not fully independent.

## Why escalated early rather than spending retry 2

1. **No unseen evidence remains.** The original 30 and now the held-out 23 have both been
   seen. A further method change would need a third fresh set written by the owner.
2. **The ceiling is in ranking, not tuning.** Ungated 8/17 says a small embedding model
   fused with BM25 does not find the right file for user-phrased questions on this corpus.
   The Architect predicted about a 30% chance of passing and recommended against this path.
3. **Budget.** ≈754k of 1,130k spent. Another method revision + implementation + QA, then
   Security and the Release Gate, projects to ≈1.3M, ≈180k over.
4. FAILURE_LOOP: the final retry escalates one model class and is not to be spent on an
   identical experiment.

## Smallest decisions the owner could make

- **A. Stop core here and record the finding** (recommended). Keep the code on the branch as
  the base. The slice does not pass its Release Gate; nothing ships. A stronger approach
  (a larger embedding model or a reranker, each a new dependency needing approvals, or
  anything generative, which the intent rules out) would be its own slice with a fresh,
  owner-written held-out set.
- **B. Spend retry 2 (last)** on another method change within the existing approvals, with
  the model class escalated. Needs a third fresh set and a budget increase (≈180k over).
  Expected value low given the ungated ceiling.
- **C. Change the bar** (for example top-10, or a lower percentage). That weakens a gate:
  approval rule 4, the owner's decision only, and only as a deliberate intent amendment,
  not as a response to this result. Not recommended.

## Resolution — 2026-09-29T16:06:36Z

The playbook session proposed (as its own proposal, not an approval): stop core here, keep
the code on the branch, leave docs-retrieval-ci unstarted; before closing, QA compares a
handful of embeddings with a reference implementation in a throwaway environment; write a
close-out for the next slice (corpus scope, file-level ranking, and — as an open question
for the owner's next intent under rule 4, not decided here — whether "no confident match"
belongs in the check step).

Owner (Gopal Patwa), prompted with three options, selected verbatim: **"Confirm the
proposal as written"**. Resolution: **A. Stop docs-retrieval-core; nothing ships.**

**The reference comparison is not yet approved.** The Orchestrator told the owner it needs
its own explicit yes before anything is installed (a PyTorch-based reference means a new
install and, for the original weights, a new download beyond Approvals 2–5). A specific
request follows; nothing is installed until it is answered.

Notes for the close-out (evidence, not conclusions): on the held-out run only 2 of 17
answers were confidently wrong (both from broad docs: BACKLOG, ARCHITECTURE, GETTING_STARTED),
and most misses were abstentions, so "most wrong answers came from broad internal files"
is a hypothesis for the next slice, not a finding.
