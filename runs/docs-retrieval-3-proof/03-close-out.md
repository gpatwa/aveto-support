# Close-out: docs-retrieval-3 (slice A) and docs-retrieval-3-proof (slice B)

> Written by the Orchestrator on the owner's direction (verbatim: "Stop slice B here as 'gate met, no demonstrated gain'"; no Post-Launch spawn was run). **Outcome: gate met, no demonstrated gain. Nothing ships from this slice.** Security Review, the Release Gate and Post-Launch did not run, by the owner's decision; the MS MARCO licence question was deliberately not settled.

## 1. Gate result

`file-rerank-v1` (frozen at `8499c2a778b739b08cc41e7fa2ac24e46ce3422c`) scored **13 of 16 answerable (81.2%) on the fourth held-out set, bar 13.** Run once, 0 retries, scored by a fresh QA spawn that did not review the labels (`02-qa-result.md`, raw `eval-run-1-heldout4.txt`). Misses: f01, f12, f13. Set: `evals/retrieval-heldout-4.toml`, main `431486e`, committed after the freeze, sha256 `180cfc0b…8aee`; label-reviewed before commit (`01-label-review.md`); the owner's committed labels differ from the reviewer's (he dropped `docs/AGENTIC_SDLC.md` from every question and trimmed other additions) before any result.

**Minimum-margin caveat.** The pass is by exactly the minimum: 12 would be 75% and one question is 6.25 points. On the same set `file-rrf-v1` scored **14 of 16**, so the gate does not show the reranker helped.

## 2. Comparison (answerable hits; diagnostics only except the fourth set)

| Set | `file-rerank-v1` | `file-rrf-v1` | Moved in / out by the reranker |
|---|---|---|---|
| Fourth (the gate set) | **13/16 (81.2%)** | 14/16 (87.5%) | in: f04; out: f01, f13 |
| Dev (`retrieval.toml`, seen) | 14/24 (58.3%) | 19/24 (79.2%) | in: a11; out: a05, a06, a20, a21, a22, a24 |
| Second held-out (seen) | 12/17 (70.6%) | 12/17 (70.6%) | in: h13; out: h06 |
| Third held-out (seen) | 13/16 (81.2%) | 11/16 (68.8%) | in: t12, t13; out: none |
| **All four (73 answerable)** | **52 (71.2%)** | **56 (76.7%)** | 5 in, 11 out |

The reranker helped where slice 2's five narrow-file misses were (third set, +2) and hurt on the dev set (-5): **net negative, -4 hits across the four sets.** Three of the four sets are seen, so only the fourth is evidence, and it points the wrong way. Unanswerable questions' top scores (0.55 to 0.81) overlap the answerable range on every set; nothing abstains (carried by the check-step slice, Decision 3).

## 3. Latency (Implementer, `03-implementation.md`)

About 2.3 to 3.8 s per `retrieve` process with the reranker (model load included), against 0.9 s with `--ranking file-rrf-v1`: roughly 3 to 4 times slower, for no demonstrated gain.

## 4. Open defect: teardown abort (exit 134)

The gate run printed its full report and `eval: PASS`, then the process aborted at teardown: `libc++abi: terminating due to uncaught exception of type std::__1::system_error: recursive_mutex lock failed: Invalid argument`, exit 134 (`eval-run-1-heldout4.txt`). It did not recur in the seven diagnostic runs, so it is intermittent, and it is not yet explained (it appears at ONNX Runtime shutdown with two sessions loaded; that is a hypothesis). **It must be fixed before any CI**, because a pass that exits 134 reads as a failure. It is not a scoring issue: the printed result is complete and the QA verified it.

## 5. What shipped / what did not

Nothing ships. The branch `claude/docs-retrieval-3` holds `file-rerank-v1` (default ranking), the pinned reranker in `aveto_support/rerank.py`, the approved INV-5 and INV-4 wording (`APPROVAL_RECORD-1.md`, `-2.md`) and ADR 0005. Not run: Security Review, Release Gate, Post-Launch, README/ARCHITECTURE prose refresh. The MS MARCO licence question (owner's condition on A1) stays open and unsettled; it blocks any release of the reranker.

## 6. Carry-forward (the owner's direction; not yet an intent)

**Slice 4:** a smaller change that
1. makes `file-rrf-v1` the default ranking, with the reranker optional and **off by default**;
2. fixes the teardown crash (exit 134);
3. runs **Security Review and the Release Gate once** on that smaller change.

Other open items, unchanged: the check-step slice (abstention; Decision 3: nothing that writes text ships before it); `docs-retrieval-ci` (blocked on the exit-134 fix and a passing release); stale "plain code" wording in `.agentic/PROJECT_CONTEXT.md` and `README.md`. Slice 4 will also need to decide what to do with the approved-but-unshipped reranker pin (INV-5 wording currently names two models).

## 7. Process and cost

- Freeze-first held: method commit `8499c2a` before the set (`431486e`); label review by one fresh spawn, scoring by a different one; one fresh spawn per stage, none resumed.
- Budget (owner-split 600k: A 360k, B 240k; units peak context per spawn): slice A spent 314k (EM 60k, Architect 143k vs 110k est., Implementer 111k); slice B spent 143k (label review 105k vs 60k est., scoring 38k vs 90k est.). Processed tokens by `usage.mjs`: slice A 5.79M, slice B 2.34M.
- The owner's mid-slice budget move (30k from B to A) and the stop at the pass are in the STATE files.
- The label review's cost overran its estimate (105k vs 60k); the scorer's came in under (38k vs 90k). Estimates for QA stages on a 16-question set should be revisited.
