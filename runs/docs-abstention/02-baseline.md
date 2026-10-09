# Baseline (A2): docs-abstention

Stage: Baseline (QA Evidence), depth standard. Measurement only. No cause is argued and no method or value is selected here; that is the Architect's job from the tables below. Product code under `aveto_support/` and `tests/` was not touched. Run date 2026-10-08/09, worktree `claude/docs-abstention-c835b1` at HEAD 3e9e9cc (product code identical to main 0dfd433).

## 1. Setup and C1 checks

- `models/` and `index/` were absent in the worktree. Copied (local `cp -R`, no network, `ingest` not run) from the main checkout `/Users/gopalpatwa/opt/aveto-support/{models,index}` (both gitignored; `git status` stays clean).
- `uv sync --locked --offline`: exit 0.
- Embedding model files match the pins in `docs-source.toml`: `onnx/model.onnx` sha256 `828e1496...cf35`, `vocab.txt` sha256 `07eced37...38a3` (both recomputed here, equal to the pinned values).
- Index `index/docs-index.json` (sha256 `f36ef5d4f9...a756`, built by `ingest` in the main checkout on 2 Oct, not rebuilt by me): `source.commit` = `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`, equal to the `commit` pin in `docs-source.toml`; 123 files, 890 passages; schema `aveto-support/index@3`. All four eval files carry the same `pinned_commit` (`check_commit` passed in every run).
- `docs-source.toml` is byte-identical to the main checkout's copy (`diff` clean) and `git diff main -- docs-source.toml` is empty (C1: corpus pin unchanged).
- The default ranking is `file-rrf-v1` (`__main__.py`: `DEFAULT_RANKING = "file-rrf-v1"`; the `Ranking:` line of every `eval` output reads `file-rrf-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c...`).
- Not re-verified: that a fresh `ingest` reproduces this index byte-for-byte (needs the network).

## 2. Row 0 (C3): what the default path does today

Fact from code and runs: **the default path `file-rrf-v1` never abstains.**

- `aveto_support/search.py` `retrieve()` docstring: "Never abstains." It always builds `ranked` as the top `top_k` (5) files and returns `RetrievalResult(..., top_score=max(sims), reference=index.threshold, ...)`. `RetrievalResult` requires at least one file. No code path in `search.py`, `evaluate.py` or `__main__.py` compares `top_score` with `reference`, and the string `no confident match` appears nowhere in `aveto_support/` (grep). The ingest-time threshold (`index.threshold` = 0.701717 here: tau_salad 0.701717, tau_offtopic 0.696323) is printed as "ingest reference ..., reported only" and never decides anything.
- Real runs, offline, default ranking (raw: `02-baseline-eval-*.txt`, `02-baseline-exit-codes.txt`, `02-baseline-retrieve-probe.txt`):

| eval file | answerable correct file in top 5 | unanswerable lines | exit |
|---|---|---|---|
| evals/retrieval.toml | 19/24 (79.2%) | 6 `DIAG`, each with a top file | 1 (below 80%, by design, as LOCAL_COMMANDS says) |
| evals/retrieval-heldout.toml | 12/17 (70.6%) | 6 `DIAG` | 1 |
| evals/retrieval-heldout-3.toml | 11/16 (68.8%) | 4 `DIAG` | 1 |
| evals/retrieval-heldout-4.toml | 14/16 (87.5%) | 4 `DIAG` | 0 |
| total | 56/73 | 20 | |

- On the 93 seen questions: abstentions = **0**. The phrase `no confident match` appears in none of the four outputs (grep count 0); every one of the 20 unanswerable questions returned a top file with a score. So today **Bar 1 = 0/20 (0%)** and, since nothing is ever abstained, **Bar 2 = 56/56 (100%)** (denominator per C4: answerable with the accepted file in the five returned files). The "always abstain" and "never abstain" extremes are the t=0.40 row of the sweep below (same numbers).
- Two real `retrieve` probes (raw in `02-baseline-retrieve-probe.txt`): a deployment question ("How do I deploy the agent to production on Kubernetes with autoscaling?", top score 0.715, above the 0.702 reference) and a word-salad ("purple elephant bicycle quantum banana", top score 0.528, well below the 0.702 reference) both exit 0 and list five files. The word-salad is below the reference and is still answered with five files.
- The calibrated threshold, applied as a counterfactual (not today's behaviour): abstain when top-1 < 0.701717 gives Bar 1 15/20 (75.0%), Bar 2 23/56 (41.1%) on the primary signal; 15/20 and 26/56 (46.4%) on the printed global signal.
- Stale statements found (facts only): `.agentic/CURRENT_MVP_STATUS.md` line 12 and `README.md` line 50 say retrieval returns "`no confident match`" when unsure; the code never does. `.agentic/SAFETY_INVARIANTS.md` INV-4 still reads "...or 'no confident match' with no passages" as a requirement on retrieval's output. `LOCAL_COMMANDS.md` and `evaluate.py` state correctly that retrieve never abstains and unanswerable is a diagnostic. ADR 0002's abstention part is marked superseded by ADR 0004.
- Premise check (C3): the default path does not already meet the bars; the plan's premise (there is nothing to compose with: the new rule would be the only abstention rule) holds.

## 3. Signal definitions (what is printed vs computed)

- **Printed / existing confidence** (`Top score` in `retrieve`, `top score` in `eval`): `max(sims)` over **all 890 passages** of the index (dense cosine similarity, int8 dot product / 127^2). It is global; it is not restricted to the five returned files.
- **Primary signal (scope C2, used for every sweep unless stated)**: for each of the five returned files, the best dense passage similarity among **all passages of that file**; top-1 = the highest of the five, top-2 = the second highest of the five (a different file), margin = top-1 minus top-2.
- The primary top-1 equals the printed global score on 69 of 93 questions and is lower on 24 (the global best passage sits in a file outside the five returned; list in Integrity below). The best passage **shown** in the output (per-file cap) differs from the primary top-1 on 7 questions. Both differences are recorded; the printed-global threshold sweep is run as a labelled secondary.
- "Top-2" is ambiguous in C2. Primary = the second-best **file**. A secondary passage-level margin (top-1 minus the second-highest passage similarity among all passages of the five files, same-file allowed) is also swept for the margin family only, declared up front in the script header.
- Rank of the correct file: lowest rank among returned files that appear in the question's `sources`; "none" if no accepted file is returned.
- Grid, fixed in the script header before any result was read: t = 0.40..0.90 step 0.01 (51 values), abstain when top-1 < t; m = 0.000..0.100 step 0.005 (21), abstain when margin < m; combined = either, over all 51 x 21 = 1071 cells. LOSO procedure as in the brief (max of min(Bar1, Bar2) on the other three sets; ties to lowest t then lowest m). "Both bars >= 90%" is tested as count*100 >= den*90 with integers; same for 80%.
- Script: `runs/docs-abstention/02-baseline-sweep.py` (`collect` then `sweep`; paths relative to `--repo-root`/`--out-dir`; it calls only the product's read-only `load_index`, `OnnxEmbedder`, `Searcher`, `retrieve`, `load_eval_set`, `check_commit`). `collect` ran once, exit 0, 3.9 s, 93 rows.

## 4. Re-measure of the intent's overlap paragraph (step 4)

The paragraph reproduces on set 4 and the facts are as follows (distribution tables in section 6):

- Set 4 answerable hits (14): top-1 0.633 to 0.713. The intent says 0.63 to 0.71: **reproduces**.
- Set 4 unanswerable: fu01 0.609, fu02 0.740, fu03 0.649, fu04 0.656 (2 dp: 0.61, 0.74, 0.65, 0.66, the same values `eval` prints). The intent says 0.61, 0.74, 0.65, 0.66: **reproduces**.
- fu02 (0.740) is above every answerable hit on set 4 (max 0.713): **reproduces**. (fu02's text is "Is Aveto listed on the GitHub Marketplace?"; its top file is `docs/DEPLOYMENT.md`.)
- Across all four sets pooled, the range is wider than the set-4 figures: answerable-with-hit top-1 0.619 to 0.800 (median 0.691, n=56); answerable-with-miss 0.599 to 0.750 (median 0.674, n=17); unanswerable 0.548 to 0.808 (median 0.654, n=20). The three groups' ranges overlap; the intent's "0.63-0.71" is a set-4 figure and does not describe the other sets (dev set hits reach 0.781, heldout-3 hits reach 0.800).

## 5. Results against the owner-approved "room to spare" definition (Q2)

Definition (APPROVAL_RECORD-2, Q2): both bars >= 90% on the pooled seen sets AND >= 80% leave-one-set-out. Facts only; no value is recommended here.

| rule family | best pooled cell (max of min(Bar1, Bar2), ties to lowest t, m) | cells with both bars >= 90% pooled | cells with both bars >= 80% pooled | LOSO: folds with both held-out bars >= 80% | LOSO pooled over folds (Bar1 / Bar2) | meets "room to spare" |
|---|---|---|---|---|---|---|
| threshold (primary signal) | t=0.67: Bar 1 13/20 (65.0%), Bar 2 37/56 (66.1%) | 0 of 51 | 0 | 0 of 4 | 13/20 (65.0%) / 37/56 (66.1%) | **no** |
| margin (primary, file-level) | m=0.015: Bar 1 14/20 (70.0%), Bar 2 31/56 (55.4%) | 0 of 21 | 0 | 1 of 4 (held-out set `heldout` only) | 14/20 (70.0%) / 31/56 (55.4%) | **no** |
| combined (t OR m) | t=0.67, m=0.000: Bar 1 13/20, Bar 2 37/56 (same as threshold alone) | 0 of 1071 | 0 | 0 of 4 | 10/20 (50.0%) / 32/56 (57.1%) | **no** |
| secondary: margin, passage-level | m=0.010: Bar 1 11/20, Bar 2 29/56 (min 0.518) | 0 of 21 | 0 | not run (pooled sweep only) | - | no (pooled fails) |
| secondary: threshold on printed global score | t=0.67: Bar 1 12/20, Bar 2 39/56 (min 0.600) | 0 of 51 | 0 | not run (pooled sweep only) | - | no (pooled fails) |

What the data show, as numbers:

- No cell of any family reaches either "both >= 90%" or even "both >= 80%" on the pooled seen sets. The best pooled min(Bar1, Bar2) is 0.650 (threshold and combined, at t=0.67).
- Bar 1 reaches 16/20 (80%) only where Bar 2 is much lower: threshold t=0.71 gives 17/20 with Bar 2 21/56 (37.5%); t=0.73 gives 18/20 (90%) with 14/56 (25.0%). Bar 2 reaches 90% or more only where Bar 1 is low: t=0.63 gives Bar 2 54/56 (96.4%) with Bar 1 6/20 (30.0%); t=0.64 gives 50/56 (89.3%) with 6/20.
- Margin alone: Bar 1 gets to 19/20 only at m=0.055 with Bar 2 6/56 (10.7%), and to 20/20 at m=0.090 with Bar 2 3/56.
- Pooled Pareto frontier of the combined rule is in section 6; no point on it has both bars above 70%.
- Per-set bars on 4 to 6 unanswerable questions are coarse (one question moves Bar 1 by 17 to 25 points); LOSO fold results should be read with that in mind.

## 6. Tables

Generated by the script from `02-baseline-questions.csv`: distributions, integrity, threshold and margin sweeps (all cells, pooled and per set), the combined Pareto frontier, the secondary sweeps, the ingest-reference counterfactual and LOSO. The full per-cell data are in `02-baseline-sweep-threshold.csv`, `02-baseline-sweep-margin.csv`, `02-baseline-sweep-margin-secondary.csv`, `02-baseline-sweep-combined.csv` (1071 cells) and `02-baseline-sweep-threshold-global.csv`.

### 6. Integrity

- rows: 93; answerable 73, unanswerable 20
- (set, id) pairs unique: True; ids repeated across sets: []
- answerable with accepted file in top 5 (Bar 2 denominator): 56; answerable misses: 17
- top1 (best passage of the five returned files) differs from the printed global `Top score` on 24 questions: [('retrieval', 'a03'), ('retrieval', 'a07'), ('retrieval', 'a11'), ('retrieval', 'a13'), ('retrieval', 'a22'), ('retrieval', 'a24'), ('retrieval', 'u03'), ('retrieval', 'u04'), ('retrieval', 'u05'), ('heldout', 'h05'), ('heldout', 'h12'), ('heldout', 'h17'), ('heldout', 'hu02'), ('heldout', 'hu03'), ('heldout', 'hu05'), ('heldout-3', 't01'), ('heldout-3', 't06'), ('heldout-3', 't12'), ('heldout-3', 'tu02'), ('heldout-4', 'f01'), ('heldout-4', 'f11'), ('heldout-4', 'f12'), ('heldout-4', 'f15'), ('heldout-4', 'f16')]
- top1 differs from the best SHOWN passage on 7 questions: [('retrieval', 'a03'), ('retrieval', 'a16'), ('retrieval', 'u04'), ('heldout', 'h11'), ('heldout-3', 't12'), ('heldout-3', 'tu02'), ('heldout-4', 'f14')]

### 6. Top-1 score distribution (primary signal), by group

| set | answerable-hit | answerable-miss | unanswerable |
|---|---|---|---|
| retrieval | n=19 min=0.632 med=0.700 max=0.781 | n=5 min=0.660 med=0.739 max=0.750 | n=6 min=0.548 med=0.672 max=0.724 |
| heldout | n=12 min=0.624 med=0.696 max=0.749 | n=5 min=0.599 med=0.673 max=0.705 | n=6 min=0.572 med=0.647 max=0.705 |
| heldout-3 | n=11 min=0.619 med=0.732 max=0.800 | n=5 min=0.618 med=0.672 max=0.700 | n=4 min=0.574 med=0.683 max=0.808 |
| heldout-4 | n=14 min=0.633 med=0.681 max=0.713 | n=2 min=0.639 med=0.657 max=0.675 | n=4 min=0.609 med=0.652 max=0.740 |
| POOLED | n=56 min=0.619 med=0.691 max=0.800 | n=17 min=0.599 med=0.674 max=0.750 | n=20 min=0.548 med=0.654 max=0.808 |

### 6. Margin (top1 - top2 file) distribution, by group

| set | answerable-hit | answerable-miss | unanswerable |
|---|---|---|---|
| retrieval | n=19 min=0.001 med=0.020 max=0.078 | n=5 min=0.010 med=0.027 max=0.050 | n=6 min=0.005 med=0.008 max=0.031 |
| heldout | n=12 min=0.006 med=0.025 max=0.093 | n=5 min=0.004 med=0.010 max=0.017 | n=6 min=0.006 med=0.010 max=0.014 |
| heldout-3 | n=11 min=0.005 med=0.022 max=0.124 | n=5 min=0.001 med=0.022 max=0.049 | n=4 min=0.002 med=0.008 max=0.086 |
| heldout-4 | n=14 min=0.000 med=0.008 max=0.040 | n=2 min=0.004 med=0.030 max=0.055 | n=4 min=0.004 med=0.031 max=0.054 |
| POOLED | n=56 min=0.000 med=0.019 max=0.124 | n=17 min=0.001 med=0.017 max=0.055 | n=20 min=0.002 med=0.010 max=0.086 |

### 6. Intent paragraph, set 4 (heldout-4)

- answerable hits top-1: min 0.633, max 0.713 (n=14); sorted: [0.633, 0.636, 0.644, 0.659, 0.662, 0.664, 0.681, 0.682, 0.685, 0.688, 0.689, 0.69, 0.692, 0.713]
- fu01: top1 0.609 (printed global 0.609), above every answerable hit on this set: False
- fu02: top1 0.740 (printed global 0.740), above every answerable hit on this set: True
- fu03: top1 0.649 (printed global 0.649), above every answerable hit on this set: False
- fu04: top1 0.656 (printed global 0.656), above every answerable hit on this set: False

### 6. Sweep: threshold rule, pooled and per set (counts)

Bar1 = unanswerable abstained/den; Bar2 = hits not abstained/den.

| cell | pooled B1 | pooled B2 | retrieval B1 | retrieval B2 | heldout B1 | heldout B2 | heldout-3 B1 | heldout-3 B2 | heldout-4 B1 | heldout-4 B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| t=0.40 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.41 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.42 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.43 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.44 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.45 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.46 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.47 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.48 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.49 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.50 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.51 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.52 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.53 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.54 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.55 | 1/20 (5.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.56 | 1/20 (5.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.57 | 1/20 (5.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| t=0.58 | 3/20 (15.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 1/6 | 12/12 | 1/4 | 11/11 | 0/4 | 14/14 |
| t=0.59 | 3/20 (15.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 1/6 | 12/12 | 1/4 | 11/11 | 0/4 | 14/14 |
| t=0.60 | 3/20 (15.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 1/6 | 12/12 | 1/4 | 11/11 | 0/4 | 14/14 |
| t=0.61 | 4/20 (20.0%) | 56/56 (100.0%) | 1/6 | 19/19 | 1/6 | 12/12 | 1/4 | 11/11 | 1/4 | 14/14 |
| t=0.62 | 4/20 (20.0%) | 55/56 (98.2%) | 1/6 | 19/19 | 1/6 | 12/12 | 1/4 | 10/11 | 1/4 | 14/14 |
| t=0.63 | 6/20 (30.0%) | 54/56 (96.4%) | 2/6 | 19/19 | 2/6 | 11/12 | 1/4 | 10/11 | 1/4 | 14/14 |
| t=0.64 | 6/20 (30.0%) | 50/56 (89.3%) | 2/6 | 17/19 | 2/6 | 11/12 | 1/4 | 10/11 | 1/4 | 12/14 |
| t=0.65 | 9/20 (45.0%) | 48/56 (85.7%) | 2/6 | 17/19 | 4/6 | 11/12 | 1/4 | 9/11 | 2/4 | 11/14 |
| t=0.66 | 11/20 (55.0%) | 42/56 (75.0%) | 3/6 | 17/19 | 4/6 | 7/12 | 1/4 | 8/11 | 3/4 | 10/14 |
| t=0.67 | 13/20 (65.0%) | 37/56 (66.1%) | 3/6 | 15/19 | 5/6 | 7/12 | 2/4 | 7/11 | 3/4 | 8/14 |
| t=0.68 | 13/20 (65.0%) | 36/56 (64.3%) | 3/6 | 14/19 | 5/6 | 7/12 | 2/4 | 7/11 | 3/4 | 8/14 |
| t=0.69 | 13/20 (65.0%) | 28/56 (50.0%) | 3/6 | 13/19 | 5/6 | 6/12 | 2/4 | 7/11 | 3/4 | 2/14 |
| t=0.70 | 15/20 (75.0%) | 23/56 (41.1%) | 4/6 | 9/19 | 5/6 | 6/12 | 3/4 | 7/11 | 3/4 | 1/14 |
| t=0.71 | 17/20 (85.0%) | 21/56 (37.5%) | 5/6 | 9/19 | 6/6 | 4/12 | 3/4 | 7/11 | 3/4 | 1/14 |
| t=0.72 | 17/20 (85.0%) | 15/56 (26.8%) | 5/6 | 6/19 | 6/6 | 3/12 | 3/4 | 6/11 | 3/4 | 0/14 |
| t=0.73 | 18/20 (90.0%) | 14/56 (25.0%) | 6/6 | 6/19 | 6/6 | 2/12 | 3/4 | 6/11 | 3/4 | 0/14 |
| t=0.74 | 18/20 (90.0%) | 6/56 (10.7%) | 6/6 | 3/19 | 6/6 | 1/12 | 3/4 | 2/11 | 3/4 | 0/14 |
| t=0.75 | 19/20 (95.0%) | 3/56 (5.4%) | 6/6 | 2/19 | 6/6 | 0/12 | 3/4 | 1/11 | 4/4 | 0/14 |
| t=0.76 | 19/20 (95.0%) | 2/56 (3.6%) | 6/6 | 1/19 | 6/6 | 0/12 | 3/4 | 1/11 | 4/4 | 0/14 |
| t=0.77 | 19/20 (95.0%) | 2/56 (3.6%) | 6/6 | 1/19 | 6/6 | 0/12 | 3/4 | 1/11 | 4/4 | 0/14 |
| t=0.78 | 19/20 (95.0%) | 2/56 (3.6%) | 6/6 | 1/19 | 6/6 | 0/12 | 3/4 | 1/11 | 4/4 | 0/14 |
| t=0.79 | 19/20 (95.0%) | 1/56 (1.8%) | 6/6 | 0/19 | 6/6 | 0/12 | 3/4 | 1/11 | 4/4 | 0/14 |
| t=0.80 | 19/20 (95.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 3/4 | 0/11 | 4/4 | 0/14 |
| t=0.81 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.82 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.83 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.84 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.85 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.86 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.87 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.88 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.89 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |
| t=0.90 | 20/20 (100.0%) | 0/56 (0.0%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 0/11 | 4/4 | 0/14 |

### 6. Sweep: margin rule, pooled and per set (counts)

Bar1 = unanswerable abstained/den; Bar2 = hits not abstained/den.

| cell | pooled B1 | pooled B2 | retrieval B1 | retrieval B2 | heldout B1 | heldout B2 | heldout-3 B1 | heldout-3 B2 | heldout-4 B1 | heldout-4 B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| m=0.000 | 0/20 (0.0%) | 56/56 (100.0%) | 0/6 | 19/19 | 0/6 | 12/12 | 0/4 | 11/11 | 0/4 | 14/14 |
| m=0.005 | 4/20 (20.0%) | 49/56 (87.5%) | 1/6 | 16/19 | 0/6 | 12/12 | 2/4 | 11/11 | 1/4 | 10/14 |
| m=0.010 | 10/20 (50.0%) | 40/56 (71.4%) | 3/6 | 12/19 | 4/6 | 11/12 | 2/4 | 10/11 | 1/4 | 7/14 |
| m=0.015 | 14/20 (70.0%) | 31/56 (55.4%) | 4/6 | 11/19 | 6/6 | 10/12 | 3/4 | 7/11 | 1/4 | 3/14 |
| m=0.020 | 14/20 (70.0%) | 28/56 (50.0%) | 4/6 | 10/19 | 6/6 | 9/12 | 3/4 | 7/11 | 1/4 | 2/14 |
| m=0.025 | 16/20 (80.0%) | 18/56 (32.1%) | 5/6 | 6/19 | 6/6 | 6/12 | 3/4 | 4/11 | 2/4 | 2/14 |
| m=0.030 | 16/20 (80.0%) | 14/56 (25.0%) | 5/6 | 5/19 | 6/6 | 5/12 | 3/4 | 3/11 | 2/4 | 1/14 |
| m=0.035 | 17/20 (85.0%) | 10/56 (17.9%) | 6/6 | 3/19 | 6/6 | 3/12 | 3/4 | 3/11 | 2/4 | 1/14 |
| m=0.040 | 17/20 (85.0%) | 9/56 (16.1%) | 6/6 | 3/19 | 6/6 | 3/12 | 3/4 | 3/11 | 2/4 | 0/14 |
| m=0.045 | 18/20 (90.0%) | 8/56 (14.3%) | 6/6 | 3/19 | 6/6 | 2/12 | 3/4 | 3/11 | 3/4 | 0/14 |
| m=0.050 | 18/20 (90.0%) | 8/56 (14.3%) | 6/6 | 3/19 | 6/6 | 2/12 | 3/4 | 3/11 | 3/4 | 0/14 |
| m=0.055 | 19/20 (95.0%) | 6/56 (10.7%) | 6/6 | 2/19 | 6/6 | 2/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.060 | 19/20 (95.0%) | 5/56 (8.9%) | 6/6 | 2/19 | 6/6 | 1/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.065 | 19/20 (95.0%) | 4/56 (7.1%) | 6/6 | 1/19 | 6/6 | 1/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.070 | 19/20 (95.0%) | 4/56 (7.1%) | 6/6 | 1/19 | 6/6 | 1/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.075 | 19/20 (95.0%) | 4/56 (7.1%) | 6/6 | 1/19 | 6/6 | 1/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.080 | 19/20 (95.0%) | 3/56 (5.4%) | 6/6 | 0/19 | 6/6 | 1/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.085 | 19/20 (95.0%) | 3/56 (5.4%) | 6/6 | 0/19 | 6/6 | 1/12 | 3/4 | 2/11 | 4/4 | 0/14 |
| m=0.090 | 20/20 (100.0%) | 3/56 (5.4%) | 6/6 | 0/19 | 6/6 | 1/12 | 4/4 | 2/11 | 4/4 | 0/14 |
| m=0.095 | 20/20 (100.0%) | 2/56 (3.6%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 2/11 | 4/4 | 0/14 |
| m=0.100 | 20/20 (100.0%) | 1/56 (1.8%) | 6/6 | 0/19 | 6/6 | 0/12 | 4/4 | 1/11 | 4/4 | 0/14 |

### 6. Sweep: combined rule (t OR m), pooled Pareto frontier

Cells not dominated on (Bar1 count, Bar2 count); first cell in (t, m) order per distinct pair. Full 1071-cell table in 02-baseline-sweep-combined.csv.

| cell | pooled B1 | pooled B2 | min frac |
|---|---|---|---|
| t=0.61,m=0.000 | 4/20 (20.0%) | 56/56 (100.0%) | 0.200 |
| t=0.63,m=0.000 | 6/20 (30.0%) | 54/56 (96.4%) | 0.300 |
| t=0.65,m=0.000 | 9/20 (45.0%) | 48/56 (85.7%) | 0.450 |
| t=0.66,m=0.000 | 11/20 (55.0%) | 42/56 (75.0%) | 0.550 |
| t=0.63,m=0.010 | 12/20 (60.0%) | 39/56 (69.6%) | 0.600 |
| t=0.67,m=0.000 | 13/20 (65.0%) | 37/56 (66.1%) | 0.650 |
| t=0.40,m=0.015 | 14/20 (70.0%) | 31/56 (55.4%) | 0.554 |
| t=0.65,m=0.015 | 15/20 (75.0%) | 28/56 (50.0%) | 0.500 |
| t=0.66,m=0.015 | 16/20 (80.0%) | 24/56 (42.9%) | 0.429 |
| t=0.71,m=0.000 | 17/20 (85.0%) | 21/56 (37.5%) | 0.375 |
| t=0.73,m=0.000 | 18/20 (90.0%) | 14/56 (25.0%) | 0.250 |
| t=0.40,m=0.055 | 19/20 (95.0%) | 6/56 (10.7%) | 0.107 |
| t=0.40,m=0.090 | 20/20 (100.0%) | 3/56 (5.4%) | 0.054 |

### 6. Pooled sweep summary by family

- **threshold** (51 cells): best pooled min(Bar1,Bar2) = 0.650 at t=0.67 (Bar1 13/20, Bar2 37/56; first cell reaching that max in lowest-t, lowest-m order). Cells with both bars >= 90% pooled: 0. Cells with both bars >= 80% pooled: 0
- **margin** (21 cells): best pooled min(Bar1,Bar2) = 0.554 at m=0.015 (Bar1 14/20, Bar2 31/56; first cell reaching that max in lowest-t, lowest-m order). Cells with both bars >= 90% pooled: 0. Cells with both bars >= 80% pooled: 0
- **margin-secondary(pmargin)** (21 cells): best pooled min(Bar1,Bar2) = 0.518 at m=0.010 (Bar1 11/20, Bar2 29/56; first cell reaching that max in lowest-t, lowest-m order). Cells with both bars >= 90% pooled: 0. Cells with both bars >= 80% pooled: 0
- **combined** (1071 cells): best pooled min(Bar1,Bar2) = 0.650 at t=0.67,m=0.000 (Bar1 13/20, Bar2 37/56; first cell reaching that max in lowest-t, lowest-m order). Cells with both bars >= 90% pooled: 0. Cells with both bars >= 80% pooled: 0

### 6. Secondary: threshold on the PRINTED global `Top score` (max over all 890 passages)

Declared up front as secondary: the existing confidence is this quantity (search.py `max(sims)`), which differs from the primary signal on some questions.

- best pooled min(Bar1,Bar2) = 0.600 at t=0.67 (Bar1 12/20, Bar2 39/56); cells with both >= 90%: 0; both >= 80%: 0

### 6. Counterfactual: the ingest reference similarity 0.701717 applied as a threshold (NOT what the default path does today)

- signal `top1`: Bar1 15/20 (75.0%), Bar2 23/56 (41.1%)
- signal `top1_printed_global`: Bar1 15/20 (75.0%), Bar2 26/56 (46.4%)

### 6. Leave-one-set-out (committed procedure)

Train = the other three sets; best cell maximises min(Bar1 frac, Bar2 frac) on train, ties to lowest t then lowest m; scored on the held-out set.

| family | held-out | chosen cell | train B1 | train B2 | held-out B1 | held-out B2 | >=80% both |
|---|---|---|---|---|---|---|---|
| threshold | retrieval | t=0.67 | 10/14 (71.4%) | 22/37 (59.5%) | 3/6 | 15/19 | no |
| threshold | heldout | t=0.67 | 8/14 (57.1%) | 30/44 (68.2%) | 5/6 | 7/12 | no |
| threshold | heldout-3 | t=0.67 | 11/16 (68.8%) | 30/45 (66.7%) | 2/4 | 7/11 | no |
| threshold | heldout-4 | t=0.67 | 10/16 (62.5%) | 29/42 (69.0%) | 3/4 | 8/14 | no |
| margin | retrieval | m=0.015 | 10/14 (71.4%) | 20/37 (54.1%) | 4/6 | 11/19 | no |
| margin | heldout | m=0.015 | 8/14 (57.1%) | 21/44 (47.7%) | 6/6 | 10/12 | yes |
| margin | heldout-3 | m=0.015 | 11/16 (68.8%) | 24/45 (53.3%) | 3/4 | 7/11 | no |
| margin | heldout-4 | m=0.015 | 13/16 (81.2%) | 28/42 (66.7%) | 1/4 | 3/14 | no |
| combined | retrieval | t=0.65,m=0.010 | 10/14 (71.4%) | 25/37 (67.6%) | 3/6 | 11/19 | no |
| combined | heldout | t=0.66,m=0.005 | 8/14 (57.1%) | 30/44 (68.2%) | 4/6 | 7/12 | no |
| combined | heldout-3 | t=0.67,m=0.000 | 11/16 (68.8%) | 30/45 (66.7%) | 2/4 | 7/11 | no |
| combined | heldout-4 | t=0.63,m=0.010 | 11/16 (68.8%) | 32/42 (76.2%) | 1/4 | 7/14 | no |

LOSO pooled over the four folds (sum of held-out counts):

- threshold: Bar1 13/20 (65.0%), Bar2 37/56 (66.1%); folds with both held-out bars >= 80%: 0/4; pooled-fold both >= 80%: False
- margin: Bar1 14/20 (70.0%), Bar2 31/56 (55.4%); folds with both held-out bars >= 80%: 1/4; pooled-fold both >= 80%: False
- combined: Bar1 10/20 (50.0%), Bar2 32/56 (57.1%); folds with both held-out bars >= 80%: 0/4; pooled-fold both >= 80%: False

## 7. Per-question table (C2): all 93 seen questions

"top-1/top-2/margin" are the primary signal (section 3); rank is among the five returned files; "in top 5" is the Bar 2 denominator membership.

| id | set | label | in top 5 | rank of correct file | top-1 | top-2 | margin | printed global Top score |
|---|---|---|---|---|---|---|---|---|
| a01 | retrieval | answerable | no | none | 0.7502 | 0.7003 | 0.0499 | 0.7502 |
| a02 | retrieval | answerable | no | none | 0.7474 | 0.7208 | 0.0267 | 0.7474 |
| a03 | retrieval | answerable | yes | 1 | 0.6857 | 0.6816 | 0.0041 | 0.7156 |
| a04 | retrieval | answerable | yes | 1 | 0.7154 | 0.6546 | 0.0608 | 0.7154 |
| a05 | retrieval | answerable | yes | 1 | 0.6944 | 0.6618 | 0.0326 | 0.6944 |
| a06 | retrieval | answerable | yes | 3 | 0.7318 | 0.7252 | 0.0067 | 0.7318 |
| a07 | retrieval | answerable | yes | 2 | 0.6320 | 0.6238 | 0.0081 | 0.6457 |
| a08 | retrieval | answerable | yes | 1 | 0.7403 | 0.7141 | 0.0262 | 0.7403 |
| a09 | retrieval | answerable | yes | 1 | 0.7129 | 0.7081 | 0.0048 | 0.7129 |
| a10 | retrieval | answerable | no | none | 0.6599 | 0.6367 | 0.0231 | 0.6599 |
| a11 | retrieval | answerable | no | none | 0.7385 | 0.7281 | 0.0105 | 0.7570 |
| a12 | retrieval | answerable | yes | 1 | 0.6346 | 0.6034 | 0.0312 | 0.6346 |
| a13 | retrieval | answerable | yes | 5 | 0.6744 | 0.6731 | 0.0014 | 0.6961 |
| a14 | retrieval | answerable | yes | 1 | 0.6997 | 0.6933 | 0.0064 | 0.6997 |
| a15 | retrieval | answerable | yes | 1 | 0.7172 | 0.6941 | 0.0231 | 0.7172 |
| a16 | retrieval | answerable | no | none | 0.6735 | 0.6368 | 0.0367 | 0.6735 |
| a17 | retrieval | answerable | yes | 1 | 0.7564 | 0.7056 | 0.0508 | 0.7564 |
| a18 | retrieval | answerable | yes | 1 | 0.7813 | 0.7030 | 0.0783 | 0.7813 |
| a19 | retrieval | answerable | yes | 1 | 0.6643 | 0.6550 | 0.0094 | 0.6643 |
| a20 | retrieval | answerable | yes | 2 | 0.7301 | 0.7066 | 0.0235 | 0.7301 |
| a21 | retrieval | answerable | yes | 3 | 0.6964 | 0.6805 | 0.0159 | 0.6964 |
| a22 | retrieval | answerable | yes | 2 | 0.6952 | 0.6852 | 0.0100 | 0.7178 |
| a23 | retrieval | answerable | yes | 1 | 0.7396 | 0.7177 | 0.0219 | 0.7396 |
| a24 | retrieval | answerable | yes | 3 | 0.6657 | 0.6455 | 0.0202 | 0.6752 |
| u01 | retrieval | unanswerable | - | - | 0.5482 | 0.5436 | 0.0046 | 0.5482 |
| u02 | retrieval | unanswerable | - | - | 0.7244 | 0.7035 | 0.0209 | 0.7244 |
| u03 | retrieval | unanswerable | - | - | 0.6909 | 0.6604 | 0.0306 | 0.6993 |
| u04 | retrieval | unanswerable | - | - | 0.6522 | 0.6458 | 0.0064 | 0.6564 |
| u05 | retrieval | unanswerable | - | - | 0.6233 | 0.6168 | 0.0064 | 0.6345 |
| u06 | retrieval | unanswerable | - | - | 0.7044 | 0.6941 | 0.0103 | 0.7044 |
| h01 | heldout | answerable | no | none | 0.7049 | 0.6950 | 0.0100 | 0.7049 |
| h02 | heldout | answerable | yes | 5 | 0.7048 | 0.6894 | 0.0154 | 0.7048 |
| h03 | heldout | answerable | yes | 1 | 0.6552 | 0.6438 | 0.0113 | 0.6552 |
| h04 | heldout | answerable | yes | 1 | 0.7092 | 0.6506 | 0.0585 | 0.7092 |
| h05 | heldout | answerable | no | none | 0.6648 | 0.6559 | 0.0089 | 0.6797 |
| h06 | heldout | answerable | yes | 2 | 0.6547 | 0.6309 | 0.0238 | 0.6547 |
| h07 | heldout | answerable | yes | 1 | 0.7485 | 0.7247 | 0.0238 | 0.7485 |
| h08 | heldout | answerable | yes | 1 | 0.6512 | 0.6183 | 0.0329 | 0.6512 |
| h09 | heldout | answerable | yes | 4 | 0.6866 | 0.6805 | 0.0061 | 0.6866 |
| h10 | heldout | answerable | yes | 2 | 0.7328 | 0.6999 | 0.0330 | 0.7328 |
| h11 | heldout | answerable | yes | 3 | 0.6557 | 0.6289 | 0.0268 | 0.6557 |
| h12 | heldout | answerable | yes | 2 | 0.6239 | 0.6002 | 0.0237 | 0.6444 |
| h13 | heldout | answerable | no | none | 0.6818 | 0.6643 | 0.0175 | 0.6818 |
| h14 | heldout | answerable | no | none | 0.6729 | 0.6591 | 0.0138 | 0.6729 |
| h15 | heldout | answerable | yes | 2 | 0.7105 | 0.6674 | 0.0431 | 0.7105 |
| h16 | heldout | answerable | yes | 1 | 0.7241 | 0.6313 | 0.0928 | 0.7241 |
| h17 | heldout | answerable | no | none | 0.5989 | 0.5944 | 0.0045 | 0.6249 |
| hu01 | heldout | unanswerable | - | - | 0.7048 | 0.6986 | 0.0063 | 0.7048 |
| hu02 | heldout | unanswerable | - | - | 0.5719 | 0.5576 | 0.0143 | 0.5983 |
| hu03 | heldout | unanswerable | - | - | 0.6488 | 0.6406 | 0.0082 | 0.6506 |
| hu04 | heldout | unanswerable | - | - | 0.6264 | 0.6124 | 0.0140 | 0.6264 |
| hu05 | heldout | unanswerable | - | - | 0.6637 | 0.6541 | 0.0096 | 0.6807 |
| hu06 | heldout | unanswerable | - | - | 0.6450 | 0.6354 | 0.0096 | 0.6450 |
| t01 | heldout-3 | answerable | yes | 1 | 0.6189 | 0.6139 | 0.0050 | 0.6220 |
| t02 | heldout-3 | answerable | yes | 1 | 0.6538 | 0.6250 | 0.0288 | 0.6538 |
| t03 | heldout-3 | answerable | yes | 2 | 0.7322 | 0.7196 | 0.0126 | 0.7322 |
| t04 | heldout-3 | answerable | no | none | 0.6525 | 0.6307 | 0.0218 | 0.6525 |
| t05 | heldout-3 | answerable | yes | 1 | 0.6633 | 0.6408 | 0.0224 | 0.6633 |
| t06 | heldout-3 | answerable | no | none | 0.6177 | 0.6061 | 0.0116 | 0.6862 |
| t07 | heldout-3 | answerable | yes | 1 | 0.7422 | 0.7205 | 0.0217 | 0.7422 |
| t08 | heldout-3 | answerable | yes | 1 | 0.7378 | 0.6391 | 0.0987 | 0.7378 |
| t09 | heldout-3 | answerable | yes | 1 | 0.7352 | 0.7109 | 0.0243 | 0.7352 |
| t10 | heldout-3 | answerable | yes | 1 | 0.7366 | 0.6849 | 0.0517 | 0.7366 |
| t11 | heldout-3 | answerable | yes | 3 | 0.6440 | 0.6326 | 0.0114 | 0.6440 |
| t12 | heldout-3 | answerable | no | none | 0.7005 | 0.6750 | 0.0255 | 0.7354 |
| t13 | heldout-3 | answerable | no | none | 0.6906 | 0.6897 | 0.0009 | 0.6906 |
| t14 | heldout-3 | answerable | yes | 2 | 0.7163 | 0.7062 | 0.0101 | 0.7163 |
| t15 | heldout-3 | answerable | no | none | 0.6717 | 0.6224 | 0.0493 | 0.6717 |
| t16 | heldout-3 | answerable | yes | 1 | 0.7999 | 0.6763 | 0.1236 | 0.7999 |
| tu01 | heldout-3 | unanswerable | - | - | 0.6963 | 0.6844 | 0.0118 | 0.6963 |
| tu02 | heldout-3 | unanswerable | - | - | 0.5742 | 0.5721 | 0.0022 | 0.5942 |
| tu03 | heldout-3 | unanswerable | - | - | 0.8076 | 0.7215 | 0.0861 | 0.8076 |
| tu04 | heldout-3 | unanswerable | - | - | 0.6688 | 0.6648 | 0.0040 | 0.6688 |
| f01 | heldout-4 | answerable | yes | 5 | 0.6823 | 0.6692 | 0.0131 | 0.7080 |
| f02 | heldout-4 | answerable | yes | 1 | 0.6850 | 0.6850 | 0.0001 | 0.6850 |
| f03 | heldout-4 | answerable | yes | 1 | 0.6620 | 0.6509 | 0.0110 | 0.6620 |
| f04 | heldout-4 | answerable | no | none | 0.6747 | 0.6196 | 0.0552 | 0.6747 |
| f05 | heldout-4 | answerable | yes | 1 | 0.6875 | 0.6590 | 0.0285 | 0.6875 |
| f06 | heldout-4 | answerable | yes | 1 | 0.7134 | 0.7089 | 0.0045 | 0.7134 |
| f07 | heldout-4 | answerable | yes | 1 | 0.6888 | 0.6833 | 0.0055 | 0.6888 |
| f08 | heldout-4 | answerable | yes | 1 | 0.6806 | 0.6747 | 0.0059 | 0.6806 |
| f09 | heldout-4 | answerable | yes | 1 | 0.6924 | 0.6789 | 0.0135 | 0.6924 |
| f10 | heldout-4 | answerable | yes | 1 | 0.6899 | 0.6503 | 0.0396 | 0.6899 |
| f11 | heldout-4 | answerable | yes | 1 | 0.6443 | 0.6398 | 0.0045 | 0.6594 |
| f12 | heldout-4 | answerable | no | none | 0.6385 | 0.6345 | 0.0040 | 0.6541 |
| f13 | heldout-4 | answerable | yes | 1 | 0.6331 | 0.6162 | 0.0169 | 0.6331 |
| f14 | heldout-4 | answerable | yes | 1 | 0.6359 | 0.6306 | 0.0053 | 0.6359 |
| f15 | heldout-4 | answerable | yes | 1 | 0.6588 | 0.6561 | 0.0027 | 0.6626 |
| f16 | heldout-4 | answerable | yes | 1 | 0.6643 | 0.6521 | 0.0122 | 0.6914 |
| fu01 | heldout-4 | unanswerable | - | - | 0.6087 | 0.6043 | 0.0044 | 0.6087 |
| fu02 | heldout-4 | unanswerable | - | - | 0.7402 | 0.6865 | 0.0538 | 0.7402 |
| fu03 | heldout-4 | unanswerable | - | - | 0.6489 | 0.6263 | 0.0226 | 0.6489 |
| fu04 | heldout-4 | unanswerable | - | - | 0.6557 | 0.6154 | 0.0403 | 0.6557 |

## 8. Anomalies and notes

- Exit codes: `eval` exited 1, 1, 1, 0 for retrieval, heldout, heldout-3, heldout-4 (1 = answerable below 80%, expected per LOCAL_COMMANDS); the two `retrieve` probes exited 0; `collect` and `sweep` exited 0. **No exit 134 or other abort occurred** in any run (4 eval runs, 2 retrieve probes, the collect script). Nothing was retried.
- Duplicates: none. 93 (set, id) pairs are unique, no id appears in two sets, and no question text (case-folded) appears in two sets.
- Counts match the brief: 73 answerable (24 + 17 + 16 + 16) and 20 unanswerable (6 + 6 + 4 + 4). Bar 2 denominator = 56 (19 + 12 + 11 + 14), identical to the hit counts `eval` printed. Labels are the sets' own `answerable` flags.
- The `eval` output header reads `ranking: file-rrf-v1` and prints top scores to 2 dp; the CSV carries full precision.
- Thresholds are applied to full-precision scores; grid points at 2 dp are not ties with any question's score except by chance, and no tie-handling affected a reported result that I could see (strict `<`).
- Not done, by instruction: no fifth/gate set was read or looked for; no model downloaded; nothing under `aveto_support/` or `tests/` modified; no commit.
- Crystallize: nothing was added to `tests/` (out of my write scope for this stage). The script and the CSV are the re-runnable record; the Architect/Implementation stage decides whether a regression test belongs in `tests/`.

## 9. Files

All under `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-abstention-c835b1/runs/docs-abstention/`:
`02-baseline.md` (this), `02-baseline-sweep.py`, `02-baseline-questions.csv`, `02-baseline-perquestion.md`, `02-baseline-tables.md`, `02-baseline-sweep-*.csv`, `02-baseline-eval-{retrieval,heldout,heldout-3,heldout-4}.txt`, `02-baseline-exit-codes.txt`, `02-baseline-retrieve-probe.txt`, `02-baseline-collect.txt`, `02-baseline-sweep-run.txt`.
