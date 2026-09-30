# Post-Launch Review (close-out) — docs-retrieval

> Owner: Post-Launch Learning Agent · Depth: standard
> Tier: 2 proposed (Release Manager never confirmed; the Architect suggested embed-v3 would probably be Tier 3)
> Released at: **nothing released.** The held-out gate failed and the owner resolved ESCALATION-2 as "stop docs-retrieval-core; nothing ships; code stays on the branch" (ESCALATION-2.md, Resolution, 2026-09-29T16:06:36Z).
> Source intent: `runs/docs-retrieval/intent.md` (owner-confirmed 2026-09-26, amended 2026-09-29)

This is a close-out of a slice that did not ship. It records what the artefacts show. It decides nothing for the owner and does not restate any gate as passed.

## 1. Did it meet its success criteria?

**No.** The headline gate (at least 80% on the held-out set) failed, so the slice does not pass. Security Review and the Release Gate did not run, because a failed gate sends a slice back, never forward (STATE.md, Stages). `docs-retrieval-ci` was never started.

Criteria are the intent's "Done means", in order, abbreviated.

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | Clean checkout installs, type-checks, passes tests with the recorded commands | Partly evidenced | 04-implementation.md, Gate evidence: `uv sync --locked`, mypy, ruff clean, 118 default tests passed, `-m network` 2 passed. That is the implementer's run at the time. Nobody re-verified it from a clean checkout after the held-out run, and the Release Gate did not run. |
| 2 | Ingest reads the pinned commit, splits by heading, reports counts | Yes | 04-implementation.md: 126 files, 910 passages, 0 skipped, 32 empty sections dropped. |
| 3 | Ingest twice gives byte-identical output | Yes (same machine and Python only) | 04-implementation.md, Determinism: three real ingests, same sha256 `1f6b2194…0c9b`; QA re-checked the index hash before the held-out run (06-qa-heldout-result.md). Cross-machine identity was not claimed. |
| 4 | Retrieve returns up to 5 passages with path, heading, line range | Yes (built and hand-checked) | 04-implementation.md, Hand checks. Not scored as a criterion by any gate. |
| 5 | Unanswerable question returns "no confident match" | Built; scored under the gate row below | See row 8. |
| 6 | Committed eval set of at least 20 answerable and 5 unanswerable, written by the owner, committed before tuning | Yes | `evals/retrieval.toml`, owner commit `a4e5275` before any retrieval code (STATE.md, Eval set). 24 answerable, 6 unanswerable. |
| 7 | Method frozen and its SHA recorded, then a fresh owner-written held-out set (at least 15 and 5) committed, run once | Yes as process | Frozen `c9b64e7`, verified unchanged through `593bb35` (STATE.md, METHOD FROZEN). Held-out set `de8b0b6`: 17 answerable, 6 unanswerable. Scored once (06-qa-heldout-result.md: `git diff c9b64e7 HEAD` over the method files is empty). See section 4 for provenance caveats. |
| 8 | Held-out: at least 80% answerable in top 5, at least 80% of unanswerable get "no confident match"; dev score printed alongside; held-out score checked in CI | **No** | Answerable **5/17 (29.4%), need 14: FAIL.** Unanswerable 5/6 (83.3%): passes, exactly at the bar. Dev set printed alongside: 10/24 and 4/6 (eval-run-2-heldout.txt, eval-run-3-dev-diagnostic.txt). The CI half was not built (row 9). |
| 9 | First CI workflow (GitHub Actions) runs install, type-check, tests and eval; a sub-threshold score fails the build | **No** | `docs-retrieval-ci` never started (STATE.md: blocked on core's Release Gate). No workflow exists. |
| 10 | No generative model, no model API called; at most one local embedding model, pinned, sha256-checked, with rule 4/5 approval | Yes | One local model (BAAI/bge-small-en-v1.5 via ONNX Runtime and numpy), revision `5c38ec7c…`, hashes verified (04-implementation.md, Verified hashes). Approvals 2, 3, 4 recorded (STATE.md, Approvals). No generative model was used. |
| 11 | Network only in ingest and CI setup; retrieve and eval make no network calls | Yes as built, not independently reviewed | Design and tests (SAFETY_INVARIANTS.md INV-5 lists the enforcing tests). QA ran eval with `uv run --offline` (06). Security Review did not run. |
| 12 | Architect records ADR 0001 and starts ARCHITECTURE.md; README explains ingest and retrieve | Yes | `docs/adr/0001`, `0002`, `0003`, `docs/ARCHITECTURE.md`, and `README.md` updated per 04-implementation.md. |

Must-not-break (from the intent): nothing retrieved is presented as an answer, provenance is always shown, and the question and docs never leave the machine. The artefacts show no violation. Security Review, which would have checked these, did not run.

## 2. Method history and results

| Step | Method | Result | Artefact |
|------|--------|--------|----------|
| v1 | Lexical (BM25-style, calibrated coverage threshold) | Run 1 on the dev set: answerable **2/24**, unanswerable 6/6, **ungated recall@5 14/24**. Threshold came out at 1.000, so 22 of 24 answerable were withheld. | eval-run-1.txt, ESCALATION-1.md |
| v2 | Lexical revision (Porter stemmer, file-level BM25, corroboration rule), pre-registered | **Never run.** The Architect predicted ungated 15–20/24 and about 15% chance of passing; the owner chose to design an embeddings variant instead. Its stemmer, ranking and corroboration code is part of the frozen build. | 02-tech-spec.md, "Retrieval — variant v2" |
| embed-v3 | Hybrid: BAAI/bge-small-en-v1.5 (int8, ONNX) fused with BM25 by reciprocal rank fusion, per-file cap 2, dense confidence calibrated on 2,000 synthetic queries and the frozen 59-question off-topic list (tau 0.702) | Frozen at **`c9b64e7`**. | 02-tech-spec.md, "Retrieval — variant embed-v3"; ADR 0003; 04-implementation.md |
| Held-out (the gate, run once) | embed-v3 | Answerable **5/17**, unanswerable **5/6**, ungated recall@5 **8/17** | eval-run-2-heldout.txt; 06 |
| Dev set (diagnostic, already seen) | embed-v3 | Answerable **10/24**, unanswerable **4/6** (misses u02, u06), ungated recall@5 **17/24** | eval-run-3-dev-diagnostic.txt |

**What the ungated number means.** Ungated recall@5 removes the confidence threshold and asks only whether a correct file is in the top 5. It is 8/17 on the held-out set (47%). The bar needs 14/17. Of the 12 held-out answerable misses, 10 were below-threshold abstentions (similarity 0.62 to 0.69 against 0.702) and 2 were confident wrong passages (h01, h02). Removing the threshold entirely could gain at most 3 questions (8 minus 5). So on this corpus and these questions the ceiling is in ranking, not in the confidence threshold. Run 1 showed the same shape with a different method (14/24 ungated against a bar of 20). Loosening the threshold cannot pass the gate.

## 3. What we ruled out

QA compared the product's embeddings with sentence-transformers and PyTorch in a throwaway environment outside the project (07-qa-reference-embeddings.md, under APPROVAL_RECORD-6):

- Float vectors match the reference to about 1e-7 (cosine minimum 0.99999989, max abs difference 2.5e-7 for passages, 1.8e-7 for queries), including the three passages truncated at 512 tokens.
- The only difference is int8 quantisation: max abs difference 0.003937, exactly half a quantisation step. Top-1 agreed for 8 of 8 queries. The top-5 set differed for 3 of 8, each by one swapped passage at the 5th or 6th place with scores within 0.0004 to 0.0111. Ranking the reference floats quantised with the product's formula reproduces the product's top-5 exactly, 8 of 8.
- No divergence in tokenisation, prefix, pooling, normalisation or truncation was found.

**Conclusion: there is no embedding bug. The failure is in the method.** Limits stated by QA: only the embedding code was compared (12 passages, 8 queries, all stored vectors), not the fusion, calibration or threshold. Whether int8 near-ties matter for the held-out result was not measured.

## 4. Evidence caveats

- **Provenance of the held-out set.** It was drafted by Claude in the playbook session and reviewed and committed by the owner. The drafter had read eval run 1 and the embed-v3 spec, and reports it did not run retrieval on the questions (06, caveat a). This is not a set written by the owner alone.
- **Overlap.** hu02 (Jira tickets) shares a subject with calibration question o01, so its abstention is not fully independent of calibration (06, caveat b). hu01 (Raspberry Pi) shares a subject with dev-set u02 (Windows) (06, caveat c). The owner was told that overlap with the calibration list was unchecked and is the owner's to check (STATE.md, Frozen inputs). No artefact shows that check was done.
- **The unanswerable pass is exactly the bar.** 5/6 needed 5. One more miss would have failed it. It is thin evidence that abstention works.
- **Small sample.** 17 answerable questions. One question is 5.9 points. The 5/17 versus 14/17 gap is large, but the split of causes within the misses rests on very few items.
- **Only 2 of 17 answers were confidently wrong** (h01, h02, from broad docs: BACKLOG, ARCHITECTURE, GETTING_STARTED). Most misses were abstentions. Any story about which files cause the failures is a hypothesis (ESCALATION-2.md, notes for the close-out).
- **Both eval sets have now been seen** (30 original, 23 held-out), so neither is unseen evidence for a further method change.
- The dev-set numbers (10/24, 17/24) are for a method designed after the dev set was seen, so they are diagnostic only.

## 5. Carry-forward for the next slice (options and hypotheses, not decisions)

These are not ranked and nothing here is recommended. The owner and the next intent decide.

**(a) Corpus scope.** Hypothesis: excluding internal or broad documents from the index (for example `docs/BACKLOG.md`, `docs/ARCHITECTURE.md`, `docs/GETTING_STARTED.md`) might reduce confidently wrong results. Evidence is thin: those files produced both confident wrong answers (h01, h02) but only 2 of 17 held-out answers were confidently wrong, and 10 of 12 misses were abstentions that corpus scope would not obviously fix. To test: rerun with the exclusion on a fresh question set.

**(b) File-level ranking.** The eval scores files, not passages (the intent says "a correct source appears in the top 5"; labels are file paths). Hypothesis: a method that ranks files (aggregating passage scores per file, or scoring file titles and headings) might do better on this scoring than passage-first retrieval. This is untested. Test on new questions, not on the seen sets.

**(c) OPEN QUESTION FOR THE OWNER: does "no confident match" belong in the check step rather than in retrieval?** The current intent makes retrieval decide abstention, using a calibrated similarity threshold. Both runs show the threshold cost most answerable questions (10 of 12 held-out misses) while ranking is also below the bar. Moving the abstention judgement to the later check step would change the intent's "Done means" (retrieval returning "no confident match", and the unanswerable half of the gate). That is a change to the intent and to a gate, which is the owner's decision under approval rule 4 in the next slice's intent. **Recorded as open. This close-out does not answer it.**

**(d) Stronger retrieval approaches, as candidates only.**
- A larger embedding model: a new model choice, new download and pin, and a new rule 4/5 approval (the intent's "no choosing the model by its score on either eval set" also applies).
- A reranker: an additional model, so a new dependency and its own approvals.
- Anything generative (for example query rewriting or an LLM reranker): out of scope of the current intent, which excludes any generative model call.
- Each would also need a new INV-4/INV-5 review if it changes what is loaded or downloaded.

**(e) A fresh held-out set written by the owner for any further method change**, since both existing sets have been seen (ESCALATION-2.md, reason 1). Also note that the freeze-first sequencing (freeze, then write the gate, run once) is what made this result trustworthy; a further attempt would have to repeat it.

## 6. What surprised us, and what we'd do differently

**Surprises (each from an artefact):**

| Surprise | Signal | Severity |
|----------|--------|----------|
| Embeddings did not fix ranking. The spec predicted embed-v3 ungated recall about 20/24 (17–23) and "ranking probably clears; abstention is still the likely failure". Measured ungated: 8/17 held-out, 17/24 dev. Ranking, not abstention, was the binding limit. | 02-tech-spec.md section 6 vs eval-run-2-heldout.txt / eval-run-3-dev-diagnostic.txt | High |
| The Architect recommended against embed-v3 in this slice with about a 30% pass chance; the EM ruled the work must split into two slices; the owner overrode both ("Pursue embed-v3 in this slice", "Keep one slice with embed-v3"). The slice failed its gate. Recorded neutrally: the owner's choice was informed and was the owner's to make. The consequence was budget: 690k, then 820k, then 1,130k. Spent at close 785k of 1,130k. | ESCALATION-1.md; STATE.md, Budget | Medium |
| STATE.md format defects silently switched the budget guard off. Fixed upstream in pack v9; this slice's installed pack is v6 plus a patch. | STATE.md, Budget: "The installed guard checks spent ≥ budget only" | Medium |
| The playbook path `../agentic-sdlc-playbook` does not resolve from a git worktree, so every stage needed the absolute path. | STATE.md Playbook line; 00-slice-plan.md | Low |
| The owner's intent had to be amended mid-slice (held-out set as gate, one local embedding model) and a stakes question (does changing INV-5 tick "changes a safety control"?) had to be answered mid-slice ("Don't tick it; stay on the short path"). | intent.md banner and Open questions; INTENT_AMENDMENT_PROPOSAL.md | Medium |
| Token accounting is misleading. The Architect was resumed many times: processed tokens (15.60M, 84 requests) are far larger than its 128k peak context. The budget is in peak-context units, not consumption: STATE.md itself records the processed figure as roughly 34 times larger at the 07:17 snapshot. The usage report may not count all resumed passes, so real consumption may be higher than shown. | usage-report.txt; STATE.md, Trace notes | Medium |
| The Orchestrator's first handoff omitted a file from the Architect's write scope (EM ruled 18 files against the 10-file rule, then 19 plus 2 QA/owner files). | STATE.md, Architecture gate cell; ESCALATION-1.md, EM re-scope ruling | Low |
| Models were first mis-recorded from memory (three Architecture rows as sonnet/medium; the real role is opus/high). Corrected after checking the harness transcript. | STATE.md, Correction 2026-09-29T05:28:36Z; trace.json corrections | Low |

**What worked:**
- Freeze-first ordering kept the gate honest: method frozen at `c9b64e7`, verified unchanged by `git diff`, the held-out set committed after, scored once, nothing tuned. The failure is a real failure, not a tuned pass.
- Early escalation on run 1 and run 2 (with a retry unspent each time) stopped further spend on identical experiments.
- The reference comparison ruled out a cheap explanation (embedding bug) before the owner decided.

**What we'd do differently (process, actionable):**
- Before committing a slice to a model-based method, run a small ungated recall check on a seen set with the cheapest candidate (for example the run 1 ungated figure of 14/24 was already an early warning that ranking, not the threshold, was the ceiling). A ranking ceiling was visible before embed-v3 was designed.
- Treat an Architect recommendation against a path, together with an EM must-split ruling, as a prompt to state the expected budget and pass chance to the owner in one line each, and record the owner's reasoning. This was done here; keep doing it.
- Put the absolute playbook path in every worktree run from the start, and reinstall the pack (v9+) before starting so the budget guard and STATE format are correct.
- Record the trace row at the moment a resumed agent finishes, and reconcile `trace.json` with STATE.md (see section 8).

## 7. Follow-up slices to file (no commitment; the Orchestrator and owner decide)

- [ ] **Retrieval improvement.** A new slice with a fresh, owner-written held-out set testing corpus scope (5a) and file-level ranking (5b), using the existing code on the branch as the base.
- [ ] **Decision slice: where does "no confident match" live?** An owner decision on the next intent (section 5c), possibly moving abstention into the check step; needs the owner's rule 4 approval if a gate changes.
- [ ] **`docs-retrieval-ci`** (GitHub Actions: install, type-check, tests, held-out eval). Blocked on a passing gate; it cannot start honestly today.
- [ ] **Stale "no model" text.** `.agentic/PROJECT_CONTEXT.md` line 66 still says "First slice: retrieval only, no model", which is no longer true (one local embedding model exists on the branch). README line 85 already says "no generative model". Fix when the intent is next revised.
- [ ] **Candidate stronger-retrieval spike** (larger embedding model or reranker), each with its own approvals, only if the owner chooses it after the above.

## 8. Cost and pipeline health

**Figures used are from `trace.json`, STATE.md Trace and `usage-report.txt` only.**

- **Budget:** 1,130k; spent 785k (STATE.md Budget), 69%. STATE.md's Trace total is 784,668 tokens over 309 tool calls, in peak-context units, with each resumed agent counted cumulatively (not additively).
- **Processed consumption (usage-report.txt):** 233 requests, 30.50M tokens processed, 6.42M cost-weighted, cache hit 93.5%. By role: software-architect 15.60M (84 requests, opus-5-5), backend-architect 10.55M, qa-evidence 3.09M, engineering-manager 0.76M plus 0.50M. The report's peak-context sum is 363k against the Trace's 785k, and its per-role peaks (Architect 128k, backend 107k, QA 45k) equal the first-pass figures in the Trace, not the resumed cumulative peaks (292,142; 262,939; 102,365). So the report probably does not capture all resumed passes; the real consumption may be higher than shown, and the two units (peak context and processed) should not be compared directly. The Architect's processed figure (15.60M) is unchanged from the earlier 07:17 snapshot in STATE.md, which suggests later resumed Architect passes may be missing from it.
- **Per-stage cap (150k, PIPELINE_SLOS.md):** no single first pass exceeds it (largest 131,797, Architecture). Two cumulative or resumed rows do: the Implementation embed-v3 pass is +155,759 in one row (cumulative peak 262,939), and the Architect's cumulative peak reached 292,142 over its resumed passes. Treat both as carry-forward flags: they are resumed sessions, so the cap flags accumulated passes, not one large stage.
- **Density (Tokens ÷ Tool calls; review 8k, build 5k):** computed from the Trace, none over its cap. Highest review-type: Scope Review 55,125/18 = 3.1k; Architecture 131,797/44 = 3.0k. Highest build-type: Implementation embed-v3 155,759/41 = 3.8k; QA off-topic list 44,781/15 = 3.0k. No stage is at or over 2x the baseline.
- **Stage wall-clock (p95 20 min):** Implementation embed-v3 resumed pass 18:14 (under p95, over the 5 min p50); Architecture 13:36. No stage over 20 min in the recorded rows. Several rows have no start/end recorded.
- **Slice envelope (stages × 100k):** cannot be judged cleanly. Counting the 5 distinct roles gives 500k and the slice is over; counting all 13 spawned passes gives 1.3M and it is within. The slice was also 785k against an original single-slice plan of 890k that became 690k for core alone, so the cost of this slice's pivot is the budget history in section 6.
- **Retries:** 1 of 2 used (STATE.md, Failure budget); retry 2 unspent, escalated early. Two escalations (ESCALATION-1, ESCALATION-2).
- **Artefact inconsistencies found:**
  1. `trace.json` stage tokens sum to 696,244, but STATE.md's Trace total is 784,668. `trace.json` is missing the Architect embed-v3 fact-fill row (+50,042) and the EM's second increment (STATE.md shows the EM cumulative at 72,097, while `trace.json` records 33,715, a difference of 38,382). 50,042 plus 38,382 equals the 88,424 gap. `trace.json` is therefore incomplete and must be corrected by the Orchestrator before analytics are trusted (per SLICE_STATE.md).
  2. STATE.md's "Current stage" line still reads "Scope Review done … next is Architecture", and the `docs-retrieval-ci` Implementation row says "in-progress — blocked". The CI slice never started.
  3. `trace.json` has `usageMeasured` at the 07:17 snapshot (19.46M processed, 156 requests), while `usage-report.txt` now shows 30.50M and 233 requests.
  4. The Budget block's spent-breakdown paragraph in STATE.md ends at 571k while its Spent line says 785k. The Trace table carries the later rows.

**Analytics regeneration:** `runs/ANALYTICS.md` and `runs/dashboard.html` are regenerated by the Orchestrator with `node <playbook>/execution/analyze.mjs .`. I have no shell, and I did not regenerate them. Fix `trace.json` (inconsistency 1) first, or the generated views will understate this slice's spend.

## Hand off

Next agent: Orchestrator. Decisions that belong to the owner: whether "no confident match" belongs in the check step (5c); whether and how to start a retrieval-improvement slice and with which method (5a, 5b, 5d); the fresh held-out set for any further method change (5e). Nothing in this close-out is approval, and no gate is restated as passed.
