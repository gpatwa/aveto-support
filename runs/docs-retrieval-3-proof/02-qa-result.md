# QA Result: docs-retrieval-3-proof (scorer, fresh spawn #2, depth standard)

## Verdict: PASS against the bar (13/16 answerable = 81.2%, required >= 80%)

Gate run once, default method `file-rerank-v1`, on `evals/retrieval-heldout-4.toml`. Retries: 0. The gate set was not re-run, relabelled or tuned. Raw output: `eval-run-1-heldout4.txt`.

Caveat the verdict does not hide: the pass is by exactly the minimum (13 of 16; 12 would have been 75%). Without the reranker, `file-rrf-v1` scored 14/16 on the same set. See the diagnostics.

A process-level note: the gate run printed its full report (`eval: PASS`) and then the process aborted at teardown (`libc++abi: terminating due to uncaught exception of type std::__1::system_error: recursive_mutex lock failed`, exit 134), an ONNX Runtime shutdown crash after the result was written. It did not recur in the seven diagnostic runs (exit codes 0 or 1, as the score dictates), and I did not re-run the gate. The score is unaffected; the exit code of that one run is not trustworthy as a pass/fail signal. Flag for Security / Release.

## Step 1: preconditions (all verified before the gate)

- HEAD `b148562`; working tree clean before my runs.
- `git diff 8499c2a778b739b08cc41e7fa2ac24e46ce3422c HEAD` over `aveto_support tests docs-source.toml pyproject.toml uv.lock .agentic evals/retrieval.toml evals/retrieval-heldout.toml evals/retrieval-heldout-3.toml evals/calibration-offtopic.toml`: **empty** (`--stat` empty, 0 bytes).
- `evals/retrieval-heldout-4.toml` sha256 `180cfc0b5505935b02e92a3f96dba2f0bf5799af71ed36ea9d855cdfdcc48aee`: **matches**.
- `index/docs-index.json` sha256 `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756`: equals the `f36ef5d4…a756` recorded in `runs/docs-retrieval-3/03-implementation.md` and `04-freeze.md`. No rebuild needed.
- `models/` holds `BAAI--bge-small-en-v1.5` and `cross-encoder--ms-marco-MiniLM-L6-v2`; the tool re-hashes both reranker files on load (`OnnxReranker`, per 03) and the eval ran without a `ModelError`.
- Gate output line 1: `Ranking: file-rerank-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c…+ce:cross-encoder/ms-marco-MiniLM-L6-v2@233902d2…:n20`. Method confirmed.

## Step 2: the gate, fourth set, `file-rerank-v1`

Answerable 13/16 (81.2%). Misses: f01, f12, f13. Hits: f02 (rank 1), f03 (2), f04 (5), f05 (2), f06 (2), f07 (1), f08 (1), f09 (2), f10 (1), f11 (1), f14 (1), f15 (1), f16 (1).

| Miss | Expected (committed labels) | Got in top 5 |
|------|-----------------------------|--------------|
| f01 | PRD_TEMPLATE, product-manager, product-brief, INTENT_TEMPLATE | software-architect, FEATURE_SPEC_TEMPLATE, tech-writer, README, ai-risk-review |
| f12 | post-launch-learning, POST_LAUNCH_REVIEW_TEMPLATE, data-analyst | APPROVAL_PROTOCOL, AGENTIC_SDLC, GETTING_STARTED, qa-evidence, release-manager |
| f13 | orchestrator (agent), prompts/orchestrator, agentic-slice command | RUN_ECONOMICS, analytics-engineer, AGENT_ROLES, AGENT_HANDOFF_TEMPLATE, qa-evidence |

(I did not look at question text beyond what the eval prints; no judgement about the labels was made, and none could change the result.)

## Step 3: diagnostics (none gating)

Reranker effect, per set. "Rerank in" = hit under `file-rerank-v1`, miss under `file-rrf-v1`; "rerank out" = the reverse.

| Set | file-rerank-v1 | file-rrf-v1 | Rerank in | Rerank out | Raw outputs |
|-----|----------------|-------------|-----------|------------|-------------|
| fourth (gate set) | 13/16 81.2% PASS | 14/16 87.5% | f04 | f01, f13 | run-1, run-2 |
| retrieval.toml (dev) | 14/24 58.3% | 19/24 79.2% | a11 | a05, a06, a20, a21, a22, a24 | run-3, run-4 |
| retrieval-heldout.toml | 12/17 70.6% | 12/17 70.6% | h13 | h06 | run-5, run-6 |
| retrieval-heldout-3.toml | 13/16 81.2% | 11/16 68.8% | t12, t13 | none | run-7, run-8 |
| Four sets together (73 answerable) | 52 (71.2%) | 56 (76.7%) | 5 in | 11 out | |

Misses by set (rerank / rrf):
- fourth: f01, f12, f13 / f04, f12.
- retrieval.toml: a01, a02, a05, a06, a10, a16, a20, a21, a22, a24 / a01, a02, a10, a11, a16.
- heldout: h01, h05, h06, h14, h17 / h01, h05, h13, h14, h17.
- heldout-3: t04, t06, t15 / t04, t06, t12, t13, t15.

Rank movement among questions that hit under both: fourth: f03, f05, f06, f09 each fell from rank 1 to rank 2; retrieval.toml: a08 1 to 2, a09 1 to 3, a13 5 to 1, a23 1 to 5; heldout: h02 5 to 1, h03 1 to 3, h09 4 to 2, h10 2 to 3, h12 2 to 5, h15 2 to 4; heldout-3: t02 1 to 2, t03 2 to 4, t07 1 to 2, t10 1 to 2, t11 3 to 1, t14 2 to 1.

Unanswerable questions, top score and top file (diagnostic; the printed "top score" is identical under both rankings on every question, so it is the first-stage similarity, not the reranker's score; nothing abstains):
- fourth: fu01 0.61 VALIDATION_MATRIX, fu02 0.74 DEPLOYMENT, fu03 0.65 README, fu04 0.66 prompts/doc-update.
- retrieval.toml: u01 0.55 COST_BUDGET_TEMPLATE, u02 0.72 README, u03 0.70 APPROVAL_PROTOCOL, u04 0.66 browser-automation-product, u05 0.63 agentic-slice, u06 0.70 APPROVAL_PROTOCOL.
- heldout: hu01 0.70, hu02 0.60, hu03 0.65, hu04 0.63, hu05 0.68, hu06 0.65.
- heldout-3: tu01 0.70, tu02 0.59, tu03 0.81, tu04 0.67.
- Unanswerable top scores (0.55 to 0.81) overlap the answerable range, so no score cutoff separates them; abstention stays with the check-step slice.

Honest reading, for the owner and Orchestrator (not a re-scoring): on the gate set the reranker passed, but did not beat its own first stage (14/16 without it). Across all four sets it is net negative (-4 hits), strongly so on the development set (-5), neutral on `retrieval-heldout`, and positive only on `retrieval-heldout-3` (+2). The gate, as written in the intent, is met; whether the reranker earns its latency (2.3 to 3.8 s vs 0.9 s) and the MS MARCO licence question is for the owner and Release Manager.

## Step 4: full regression (after the gate, static checks last)

| Command | Result |
|---------|--------|
| `uv sync --locked` | Resolved 18 packages, audited 16, ok |
| `uv run pytest` | 157 passed, 10 deselected |
| `uv run pytest -m model` | 7 passed, 160 deselected |
| `uv run mypy` | Success: no issues found in 15 source files |
| `uv run ruff check` | All checks passed |

Each was run as its own command (no `&&` chain). Exit codes were not captured by my shell wrapper (PIPESTATUS printed empty); the pass lines above are the tools' own summaries. Network-marked tests were not run (outside this slice's regression).

## Safety invariants

Nothing in this stage touched code, the index, models or `.agentic/`; `git diff 8499c2a HEAD` over the method files is empty (above). No network was used by any command in this stage (eval and tests run offline; the autouse fixture blocks the network in pytest). No generative model is involved; retrieval output is a ranked file list, never presented as an answer. Method files and eval files are unchanged by me (`git status` shows only my new `eval-run-*.txt` files and this artefact).

## Deferred or not verifiable

- Label quality of the committed set: not assessed here (reviewed by spawn #1, committed by the owner, fixed).
- The teardown abort (exit 134) in the gate run: not investigated, per instructions not to investigate or tune.
- Latency was not re-measured.

## Recommendation to Security: GO on the gate (PASS), with two flags: the ONNX teardown abort, and the reranker's net-negative diagnostics against `file-rrf-v1`. Budget: Security, Release and Post-Launch would overrun slice B's 240k per the STATE note; the Orchestrator stops and asks the owner.

## Artefacts

`eval-run-1-heldout4.txt` (the gate), `eval-run-2-retrieval-heldout-4-file-rrf-v1.txt`, `eval-run-3-retrieval-file-rerank-v1.txt`, `eval-run-4-retrieval-file-rrf-v1.txt`, `eval-run-5-retrieval-heldout-file-rerank-v1.txt`, `eval-run-6-retrieval-heldout-file-rrf-v1.txt`, `eval-run-7-retrieval-heldout-3-file-rerank-v1.txt`, `eval-run-8-retrieval-heldout-3-file-rrf-v1.txt`, all under `runs/docs-retrieval-3-proof/`.
