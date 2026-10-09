# Tech Spec — docs-abstention (Architecture, A3)

> Owner: Software Architect Agent. Depth: standard.
> Status: **ready for owner decision, not yet for implementation.** Implementation (A4) may start only after (1) the owner's stop-and-ask on the model-path cost (section 12), (2) the model verification spawn (section 3.4) has recorded its facts in ADR 0007, and (3) the owner's rule 5 approval (named model + exact revision) and two rule 4 approvals (INV-4, INV-5) are recorded.
> Sources: `runs/docs-abstention/intent.md` (source of truth), `01-scope.md` (C1-C10 binding), `APPROVAL_RECORD-2.md` (Q1-Q5), `02-baseline.md` + `02-baseline-questions.csv` (measured facts), `.agentic/SAFETY_INVARIANTS.md`, `.agentic/LOCAL_COMMANDS.md`, `aveto_support/{search,rerank,evaluate,__main__}.py` (interfaces read, nothing changed), ADR 0006. No fifth (gate) set was read or looked for. No other run was read.
> Pack v15 terms: "baseline a defect first", "method commit", "freeze", "seen set", "gate set", "fail closed".

## Summary

Retrieval today never abstains (measured; section 1). This slice adds one abstention rule to `retrieve` and `eval`: a local, non-generative **answerability judge** (a cross-encoder classifier, ONNX Runtime + numpy, pinned by revision and sha256) reads the question with each passage that retrieval would show (the five returned files, at most two passages each, so at most 10 pairs) and returns one score per pair. If no shown passage scores at or above the model's own decision boundary (probability 0.5, fixed now, not fitted), the command prints exactly `no confident match`, no passages, names the deciding signal, and exits 0. Otherwise the output is today's output, unchanged, plus one line stating the judge's verdict. The judge cannot add, drop, reorder or alter a passage; it can only turn a result into an abstention. A missing, unreadable, hash-failing or erroring judge is an error (exit 2), never an abstention and never a pass-through. First-stage ranking, the corpus and the embedding model are unchanged. The `eval` exit-code rule is unchanged; the two bars, the end-to-end figure and the comparators are printed. I recommend this model path over reusing the reranker, over shipping the best simple rule, and, only if no candidate passes verification, over stopping (section 3). The model is not named with certainty: I name a leading candidate from memory and give binding selection criteria; every fact about it (existence, revision, licence, training data, ONNX files, hashes) is unverified and must be recorded in ADR 0007 by a verification spawn before the owner is asked. **The model path overruns the 650k budget (estimate 700k-780k, section 12); the Orchestrator must stop and ask before A4.**

## 1. What was observed (baseline on the unchanged code)

All figures are from `02-baseline.md` (A2, 93 seen questions, worktree at product code identical to `main` 0dfd433). I add one count from `02-baseline-questions.csv`, marked.

**Today's behaviour (measured).**
- The default path `file-rrf-v1` never abstains. `search.py` `retrieve()` says "Never abstains"; `RetrievalResult.__post_init__` rejects an empty file list; nothing compares `top_score` with `reference`. The string `no confident match` appears nowhere under `aveto_support/`. On the 93 seen questions: 0 abstentions, so Bar 1 = 0/20 and Bar 2 = 56/56.
- The ingest reference (0.701717) is printed and decides nothing. Applied as a counterfactual threshold it gives Bar 1 15/20, Bar 2 23/56 (41.1%).
- Stale text (facts): `README.md` line 50 and `.agentic/CURRENT_MVP_STATUS.md` line 12 say retrieval returns `no confident match`; it does not. Per C6 they are corrected only after the Release Gate verdict, by the Orchestrator or Backend, and are not touched in A4. **INV-4 itself** says retrieval returns passages "or 'no confident match' with no passages", which has not been true of the code since ADR 0004; that sentence is stale today and is corrected in the rule 4 request (section 8).
- There is nothing to compose with (C3): no abstention rule exists today, so the new rule is the only one, and "can only add abstentions" holds trivially against today's zero.

**Can a simple rule do it? (measured, against the owner's Q2 definition).** Q2: a simple rule ships without a model only if both bars are >= 90% pooled on the seen sets AND >= 80% leave-one-set-out.
- Threshold on the primary signal: best pooled min(Bar 1, Bar 2) = 0.650 at t=0.67 (Bar 1 13/20, Bar 2 37/56). 0 of 51 cells reach both >= 80% pooled, let alone 90%. LOSO: 0 of 4 folds with both held-out bars >= 80%.
- Margin (file-level): best 0.554 at m=0.015 (14/20, 31/56). 0 of 21 cells both >= 80%. LOSO 1 of 4 folds.
- Combined (threshold OR margin, 1071 cells): best 0.650, the same cell as threshold alone. 0 cells both >= 80%. LOSO 0 of 4, pooled over folds 10/20 and 32/56.
- Secondary signals (passage-level margin, printed global score): best 0.518 and 0.600; none reach both >= 80%.
- The trade-off is steep in every family: Bar 1 reaches 16/20 or more only where Bar 2 is at or below 42.9% (combined t=0.66, m=0.015: 16/20, 24/56); Bar 2 reaches 90% only where Bar 1 is at or below 30%.

**Conclusion (from the numbers, not from the intent's paragraph):** no threshold, margin or combined rule meets Q2's "room to spare". None meets the bars themselves even on the data it would be fitted to. Under the intent ("If not, the Architect argues one model, on general grounds, before any run") a model is argued below. The 20 seen unanswerable questions are too few to fit anything on (one question moves a per-set Bar 1 by 17-25 points), so no parameter of the recommended method is fitted to them (section 4).

**What is measured about the overlap, and what is conjecture.**
- Measured: pooled top-1 ranges overlap almost completely. Answerable hits 0.619-0.800 (median 0.691, n=56); unanswerable 0.548-0.808 (median 0.654, n=20). The highest-scoring question of all 93 is unanswerable (`tu03`, 0.808). The intent's set-4 figures reproduce exactly (`fu02` 0.740 above every set-4 hit, max 0.713).
- Measured (my count from `02-baseline-questions.csv`): 6 of the 20 unanswerable questions have `docs/DEPLOYMENT.md` as their top file (`u02`, `u05`, `hu01`, `tu03`, `tu04`, `fu02`), and these include the four highest-scoring unanswerable questions (`tu03` 0.808, `fu02` 0.740, `u02` 0.724, `hu01` 0.705).
- **Conjecture, not measured:** dense similarity measures how close the question's topic is to a passage, not whether the passage states the answer, so a question about a topic the docs cover but a fact they omit (for example `fu02`, "Is Aveto listed on the GitHub Marketplace?", top file `docs/DEPLOYMENT.md`) scores like an answerable one. I have not tested this; nothing in this slice depends on it being true. The recommended method is justified by what the task requires (a reading of question and passage together), and its worth is measured on the seen sets at a pre-fixed setting (section 4) and then once on the gate set.

## 2. Options weighed (general grounds; seen-set numbers only where stated)

| Option | What it is | For | Against | Approvals it needs |
|---|---|---|---|---|
| **(a) Reuse the reranker as judge** | `cross-encoder/ms-marco-MiniLM-L6-v2` @ `233902d2...`, already pinned in `rerank.py`, scores (question, shown passage); abstain below some logit | No new download; adapter, pins, hash checks and tests already exist | (1) It was trained to **rank** passages for a query (MS MARCO passage ranking); its logit orders passages within one question, and nothing in that objective gives a boundary that means "this passage answers" across questions. A threshold on it would have to be fitted, on 20 unanswerable questions. (2) It would move the open MS MARCO licence question (ADR 0005/0006) onto the **default path**, which ADR 0006 removed it from. (3) The intent's "Out of scope" lists "Re-opening the reranker". (4) Slice 4 measured it doing no better than `file-rrf-v1` on ranking (ADR 0006); that is not a measurement of answerability and I do not argue from it. | **Yes, rule 5 and rule 4 even though no new file is fetched.** Its slice-3 approval covered an opt-in ranking method. Making it a default-path dependency that decides a safety-controlled output is a new use of a real model (rule 5), and it falsifies INV-5's "the default path fetches only the embedding model's files" (rule 4), and supersedes ADR 0006 decision 2 (new ADR). So (a) is not cheaper on approvals; it only skips a download. |
| **(b) One purpose-built answerability cross-encoder** (recommended) | A non-generative sequence classifier trained on (question, passage) -> "this passage contains the answer"; local, ONNX Runtime + numpy, pinned 40-hex revision, sha256 per file, no PyTorch, no `trust_remote_code` | Its training objective is the decision we need, so it comes with a native decision boundary (probability 0.5) that need not be fitted on the 20 seen unanswerable questions. Reuses the existing WordPiece tokenizer, `encode_pair`, `verify_file` and the ONNX session pattern if it meets the criteria in 3.2 | A new download path (adversarial Security), a new licence and training-data question, a third ONNX session in `file-rerank-v1` mode (the unexplained exit-134 history, ADR 0006), latency, and domain shift (see 3.3). The candidate is unverified. | Rule 5 for the named model at its exact revision (after ADR 0007 records licence and training data); rule 4 for INV-5 ("exactly two" -> three); rule 4 for INV-4 |
| **(c) No model: ship the best simple rule honestly** | Threshold t=0.67 on the primary signal, labelled low-confidence | No new model, INV-5 untouched, smallest A4 | Seen-set pooled 13/20 and 37/56; LOSO 0 of 4 folds pass. The gate run is predicted to fail both bars, and running it **consumes the fifth set** (it becomes a seen set) to confirm what the seen sets already show. Drafting stays blocked. | Rule 4 for INV-4 (the stale clause must still be corrected) |
| **(d) Stop** | Record the baseline as the slice's finding; correct INV-4's stale clause; close out | Cheapest (about 221k total, section 12). The fifth set is not consumed and stays available for a later method | No abstention; drafting stays blocked; the whole-pipeline figure cannot be stated | Rule 4 for INV-4's correction only (wording in section 8.3) |

**Recommendation: (b).** It is the only option whose decision boundary does not have to be fitted to 20 seen questions, and the only one whose training task is the decision the bars measure. (a) is rejected on general grounds (a relevance objective, a licence question moved onto the default path, and explicitly out of scope), not on a measurement. (c) is rejected because it spends the gate set to confirm a predicted failure. **If no candidate passes the criteria in 3.2, the recommendation becomes (d), not (c).**

## 3. The judge

### 3.1 Task family, argued

Candidate task families for a non-generative classifier that reads the question and a passage together:
- **Relevance ranking (MS MARCO-style).** Option (a). Rejected above.
- **Extractive QA with a no-answer head (SQuAD 2.0-style).** Its native output is a span of the passage. Even if only the no-answer score were kept, the model's job is to select a fragment of the returned text, which is what INV-4 forbids a model to do, and the boundary would be tested by "we discard the span" rather than by the model's shape. **Excluded.**
- **NLI (MNLI/SNLI-style) entailment.** Needs a hypothesis statement; our input is a question. Turning a question into a hypothesis means rewriting text. **Excluded.**
- **Question-answer containment (QNLI-style sequence classification).** Input is (question, passage); output is "the passage contains the answer / does not". As I recall from the GLUE paper, QNLI's negatives are sentences from the same source paragraph as the answer, which share the question's topic and vocabulary; that is the hard-negative shape `fu02` has. This recollection is unverified and must be confirmed in ADR 0007. **Chosen family.**

### 3.2 Selection criteria (binding; a candidate failing any one is rejected)

1. **Task:** a cross-encoder sequence classifier trained on (question, passage) -> answer-containment (QNLI-type or equivalent). Not relevance-only, not span extraction, not generative or seq2seq, not NLI needing a rewritten hypothesis.
2. **Output head:** either one logit (probability = sigmoid) or two logits with the positive ("contains the answer" / "entailment") label named in the model's `config.json` `id2label`. Nothing else.
3. **Tokenizer and graph:** BERT-family encoder whose `vocab.txt` is a WordPiece vocabulary the existing `aveto_support.embed.WordPiece` handles (uncased, as both current models use); ONNX inputs exactly `input_ids`, `attention_mask`, `token_type_ids` (`embed.INPUT_NAMES`); 512 positions. No new tokenizer code and no new Python dependency.
4. **Files upstream:** `onnx/model.onnx` and `vocab.txt` present in the Hugging Face repo **at one full 40-hex revision**, with their LFS sha256 recorded. We never convert, quantise or host a model file ourselves (that would need PyTorch and would make our own artefact the thing trusted). No custom code files; no `trust_remote_code`.
5. **Licence and training data:** an explicit licence on the model card that permits this product's use, and the training data named with their licences. If any training-data terms restrict use (the MS MARCO case) or cannot be determined, the candidate is rejected or the question is put to the owner in ADR 0007 before any request; it is never left open on the default path.
6. **Size:** `onnx/model.onnx` at most about 450 MB (base-size encoder at fp32), so a CPU judge over at most 10 pairs per question stays in the seconds range. Latency is reported in A4, not gated.
7. **Selection among candidates that pass:** by these criteria and the ADR facts only (prefer the clearest licence, then the smallest model), never by a score on any eval set.

### 3.3 Leading candidate (unverified)

`cross-encoder/qnli-electra-base` (the sentence-transformers QNLI cross-encoder), named **from memory**. I could not verify, and the verification spawn must establish and record in ADR 0007:
- that the repository exists under that ID today, and its current full 40-hex revision;
- whether `onnx/model.onnx` exists upstream at that revision (criterion 4; if it does not, the candidate is rejected);
- the sha256 and size of `onnx/model.onnx` and `vocab.txt` (from Hugging Face's LFS metadata; ingest re-hashes the downloaded bytes in any case);
- the licence on the model card;
- the training data (I believe QNLI, which is derived from SQuAD v1.1; SQuAD is, as I recall, CC BY-SA 4.0; both unverified) and their terms;
- the output head shape and `id2label` (criterion 2);
- that its `vocab.txt` is an uncased BERT WordPiece vocabulary (I believe ELECTRA uses BERT's; unverified) and the ONNX input names (criterion 3).

Known general risk for this family, not a measurement: QNLI pairs are a question and **one sentence**; our passages are whole sections truncated at 512 tokens. Section-length input is a domain shift whose effect is unknown until measured (section 4).

I do **not** name a second candidate: I cannot recall one that I believe meets criteria 1-4 together. If the leading candidate fails, the verification spawn lists any other models it finds that meet all of 3.2, with the same facts; the choice among them follows criterion 7; if none, the slice takes option (d).

### 3.4 Model verification spawn (before any approval request)

- **Role:** research (Market/Technical Research brief) or the Orchestrator itself; read-only web access. **Est. 30-40k.**
- **May read:** Hugging Face model pages, the public API metadata for the repo's file tree at a revision (names, sizes, LFS sha256), and small text files (`README.md` model card, `config.json`, `tokenizer_config.json`). **Must not download** `onnx/model.onnx` or any weights, install anything, or read any eval set.
- **Writes:** `runs/docs-abstention/02b-model-verification.md` with, for each candidate, every fact listed in 3.3 against criteria 1-6, each with the URL and revision it was read from, and a pass/fail per criterion. It recommends nothing beyond applying criterion 7.
- **Approval note:** this reads public metadata only and calls no model; I do not consider it a rule 5 action, but because it is the slice's first network use by an agent, the Orchestrator should include it in the stop-and-ask at this stage's exit (section 12) rather than infer permission.
- **Then:** ADR 0007 (draft in `docs/adr/0007-answerability-judge.md`, section 9) has its fact slots filled from `02b-model-verification.md` (by a short Architect pass or the Orchestrator, est. 10k), **then** the rule 5 request is made for that model at that revision, with INV-5's exact text (section 8.2) filled in with the same values.

## 4. Decision rule, fixed now (method `abstain-judge-v1`)

Committed in this spec, before any judge has been run on anything and before the gate set exists in the repo. Nothing below is fitted to the seen sets.

1. **First stage unchanged.** `retrieve()` ranks exactly as today (`file-rrf-v1` by default, or `file-rerank-v1`) and produces the five files with their shown passages (`per_file_cap` = 2, so at most 10 passages).
2. **Which passages the judge sees:** exactly the shown passages of the five returned files, in rank order, each as `passage_input(passage)` (the same text the reranker reads). Not other passages of those files, not passages of other files. The judge sees what the user would see.
3. **Input encoding:** `rerank.encode_pair` (`[CLS] question [SEP] passage [SEP]`, question capped at 64 tokens, passage truncated to fill 512).
4. **Per-pair score:** p = sigmoid(logit) for a one-logit head; p = softmax(logits)[positive label] for a two-logit head (the positive label index is pinned in `JudgeParams` from ADR 0007, never inferred at run time).
5. **Aggregate:** `best = max(p)` over the judged pairs (at most 10).
6. **Threshold: 0.5, the model's own decision boundary.** Answer if `best >= 0.5`; abstain if `best < 0.5`. Chosen on general grounds (it is where the classifier's training puts "contains the answer"), not from data. No seen-set tuning, no fallback threshold.
7. **Composition:** this is the only abstention rule (section 1). It never changes which files are returned, their order, or their passages; if it does not abstain, the output's files and passages are byte-identical to today's.

Known costs of this rule, stated before measurement: taking the max over up to 10 pairs gives an unanswerable question more chances to be judged answerable (pushes Bar 1 down); a correct file whose answering passage is not among its two shown passages, or lies past the 512-token cut, can be judged unanswerable (pushes Bar 2 down). Both are measured by the bars, not argued away.

### 4.1 Seen-set confirmation (measures, picks nothing)

After A4 implements `abstain-judge-v1` with the approved model, and **before the method commit is recorded**, A4 runs `eval` once on each of the four seen sets at the candidate commit and saves the raw output to `runs/docs-abstention/04-seen-confirmation-<set>.txt`. It records, per set and pooled: Bar 1 (count/20), Bar 2 (count/56 at the pre-abstention denominator), the end-to-end figures, and `best` per question. It needs a shell (A4 has one). It changes nothing in the method.

**Pre-registered condition:** proceed to the freeze only if, pooled over the four seen sets, **Bar 1 >= 16/20 and Bar 2 >= 45/56** (ceil(0.8 x 56) = 45). Otherwise the Orchestrator stops and asks the owner, with the numbers; options then are (d) stop or a new method in a new slice. The threshold is **not** re-chosen from these numbers. Leave-one-set-out is not applied: no parameter was fitted, so there is nothing for it to guard against.

Honest reading in advance: a narrow seen-set pass (16-17 of 20) predicts close to a coin flip on 24 gate questions; the Release Gate must not read a narrow pass as more than it is (C4 note).

### 4.2 Comparators on the gate set (fixed now, reported by the scorer as diagnostics)

The scorer (B2) also reports, on the fifth set and in the same run, using `runs/docs-abstention/02-baseline-sweep.py collect` (or an equivalent read-only computation of the primary signal) at the frozen commit:
- never-abstain (today's behaviour);
- threshold **t = 0.67** on the primary signal (the best pooled seen cell, ties to lowest t);
- margin **m = 0.015** on the file-level margin (the best pooled seen margin cell).
These values are taken from `02-baseline.md` section 5 and are fixed by this spec; they are not re-chosen on the gate set. If the script needs a flag to accept a fifth eval file, that change is to the run script, not to product code, and does not touch the method.

## 5. Composition and output (C3, C8)

### 5.1 `retrieve` output

On **abstention**, stdout is exactly these lines, exit **0**:

```
Sources for: <question>
Docs: <repo> @ <commit>
Ranking: <ranking_mode>  no text generated
no confident match
Decided by: answerability judge <model>@<revision> (abstain-judge-v1: best of <n> shown passages p=<best:.3f> < 0.50)
```

The fourth line is exactly `no confident match` (no prefix, no punctuation). No file, URL, heading, line range or passage text is printed. The first-stage files are not printed in any form.

On **answer**, stdout is today's output with two changes only:
- the `Top score:` line's parenthesis no longer says "retrieval does not decide whether the docs answer"; it reads `Top score: <s:.3f> (best passage similarity; ingest reference <r:.3f>, reported only)`;
- one new line after it: `Judge: answers (abstain-judge-v1: best of <n> shown passages p=<best:.3f> >= 0.50; <model>@<revision>)`.
Files, passages, excerpts, URLs and the closing `These are sources, not an answer.` are unchanged. Retrieved text stays verbatim.

### 5.2 `eval` output and exit code

Per question (the existing line plus a judge field):
- answerable: `HIT` / `MISS` exactly as today (pre-abstention, retrieval's own ranking), then `  judge p=<best:.2f> answered|ABSTAINED`;
- unanswerable: `ABST` if abstained, else `DIAG` as today; then `  judge p=<best:.2f>`.

New summary lines, after the existing `answerable:` line:
```
abstention bar 1: <a>/<u> unanswerable abstained  required >= <ceil(0.8u)>  PASS|FAIL
abstention bar 2: <b>/<h> top-5 hits not abstained  required >= <ceil(0.8h)>  PASS|FAIL
end-to-end (top 5): <e5>/<N>  end-to-end (top 1): <e1>/<N>
```
where `h` is the number of answerable questions with an accepted file in the five files returned **before** abstention (C4), `e5` counts answerable questions with an accepted file in the top 5 and not abstained plus unanswerable questions abstained (C10), and `e1` the same with rank 1. The existing `unanswerable: <u> (diagnostic only, not gated)` line becomes `unanswerable: <u> (abstention bars reported above; eval exit code reflects the retrieval gate only)`.

**Exit code: unchanged.** `eval` exits 0 when answerable hits in the top 5, computed **before abstention**, are >= 80%, else 1. Reason it need not change: the bars are scored by the slice's scorer from the printed counts, and tying the exit code to them would change the meaning of an existing gate (scope, section 5 last bullet). Computing the retrieval gate before abstention keeps the existing gate's meaning exactly.

### 5.3 Fail-closed behaviour (exact)

| Condition | `retrieve` | `eval` |
|---|---|---|
| Judge files not cached | `error: answerability judge files are not cached in <dir>; run ingest` on stderr, **exit 2**, nothing on stdout. Never downloads. | same, exit 2, before any question is scored |
| A judge file fails its sha256 | `error: ... (judge: run ingest)`, exit 2, nothing on stdout. (Ingest, not retrieve, deletes a mismatching download.) | same |
| ONNX inputs or output shape unexpected | `ModelError`, exit 2 | same |
| A pair's score is non-numeric or non-finite, or the session errors mid-question | `ModelError`, exit 2, nothing on stdout for that question | the run aborts with exit 2; no partial report is printed |
| Judge returns normally | rule in section 4 | rule in section 4 |

Never: abstaining because the judge broke (that would hide a broken install and inflate Bar 1), or printing passages the judge did not score. `retrieve` builds its stdout only after the judge has scored every shown passage, so an error can never leave passages on stdout.

## 6. Data model, service surface, adapter boundary

### 6.1 Data model deltas

No index, schema, migration or config-file change. `index/docs-index.json` (schema `aveto-support/index@3`) and `docs-source.toml` are untouched; the judge pin lives in code, as the reranker's does.

| Type | Change | Rationale |
|---|---|---|
| `judge.JudgeParams` (frozen dataclass) | new | The pin and the pre-registered constants: `model`, `revision` (40-hex, validated), `onnx_file`, `onnx_sha256`, `vocab_file`, `vocab_sha256` (64-hex, validated), `head: Literal["sigmoid1", "softmax2"]`, `positive_index: int` (0 for `sigmoid1`), `max_tokens = 512`, `max_question_tokens = 64`, `threshold = 0.5`, `method = "abstain-judge-v1"`. Values for model/revision/hashes/head come only from ADR 0007. |
| `search.JudgeVerdict` (frozen dataclass) | new | `answers: bool`, `best: float`, `pairs: int`, `threshold: float`, `signal: str` (e.g. `judge:<model>@<revision>:abstain-judge-v1`). Invariant: `0 <= best <= 1`, `pairs >= 1`, `answers == (best >= threshold)`. |
| `search.Abstention` (frozen dataclass) | new | `question: str`, `ranking_mode: str`, `verdict: JudgeVerdict`. **Has no files or passages field** (INV-4 by construction). Invariant: `verdict.answers is False`. |
| `search.Answer` (frozen dataclass) | new | `result: RetrievalResult`, `verdict: JudgeVerdict`. Invariant: `verdict.answers is True`. |
| `RetrievalResult` | unchanged | Still requires >= 1 file; it remains the first stage's output. `test_result_invariant_enforced` is unchanged. |
| `evaluate.QuestionOutcome` | modified | adds `abstained: bool`, `judge_best: float`, `top1_hit: bool`. `hit` keeps its meaning (accepted file in the top 5 before abstention). |
| `evaluate.EvalReport` | modified | adds `bar1_abstained`, `bar2_kept`, `bar2_denominator`, `end_to_end_top5`, `end_to_end_top1`, and properties `bar1_passed` / `bar2_passed` (counts against `ceil(0.8 n)` with integer arithmetic: `count * 5 >= n * 4`, which equals `count >= ceil(0.8 n)`). `passed` is unchanged. |

### 6.2 Service surface

| Function | Signature | Invariant |
|---|---|---|
| `search.py:retrieve` | unchanged `(Searcher, str) -> RetrievalResult` | First stage only; still never abstains. Docstring changes to say so ("first stage; abstention is `respond`"). |
| `search.py:judge_result` | `(judge: Judge, params: JudgeParams, result: RetrievalResult) -> JudgeVerdict` | Scores exactly the shown passages of `result.files`, in rank order, each once; validates every score (numeric, finite, in [0,1] after the head transform) or raises `ModelError`; never reads or returns text other than to pass it to the judge. Pure apart from the judge call. |
| `search.py:respond` | `(searcher: Searcher, judge: Judge, params: JudgeParams, question: str) -> Answer \| Abstention` | `retrieve` then `judge_result`; returns `Abstention` iff `not verdict.answers`. Raises (never returns) on any judge error. |
| `judge.py:OnnxJudge.load` | `(models_dir: Path, params: JudgeParams = DEFAULT_PARAMS) -> OnnxJudge` | Files absent -> `ModelError` naming `ingest`; re-hashes both files before building the session; never downloads. Checks ONNX input names == `INPUT_NAMES` and output shape matches `params.head` (`[batch, 1]` or `[batch, 2]`). |
| `judge.py:OnnxJudge.logits` | `(question: str, passage_text: str) -> tuple[float, ...]` | Returns 1 or 2 finite floats per `params.head`; no text out. Single-threaded, sequential, batch 1, CPU, like `OnnxReranker`. |
| `judge.py:OnnxJudge.close` | `() -> None` | Idempotent; drops the session (ADR 0006 decision 4). |
| `judge.py:probability` | `(logits: tuple[float, ...], params: JudgeParams) -> float` | sigmoid or softmax[positive_index]; raises `ModelError` on wrong arity or non-finite. |
| `ingest.py:ensure_judge_files` | `(params: JudgeParams, models_dir: Path, opener=...) -> str` | Mirrors `ensure_reranker_files`: HTTPS GET from `huggingface.co` at the 40-hex revision, redirects only under `hf.co`, sha256 checked before use, delete-and-fail (exit 3) on mismatch, cached files re-hashed. Called on **every** `ingest` (default path). |
| `ingest.py:run_ingest` | unchanged signature | Calls `ensure_judge_files` unconditionally; adds `judge_status` to its report; prints `judge files: <status> (sha256 verified before use)`. Index bytes unchanged. |
| `__main__.py:main` | adds keyword `judge: Judge \| None = None` | `retrieve`/`eval` load `OnnxJudge` when none is injected, on both rankings; adapters are created embedder, reranker (if any), judge, and closed in reverse (judge, reranker, embedder) in `finally`. |
| `evaluate.py:score` | `(searcher: Searcher, eval_set: EvalSet, judge: Judge, params: JudgeParams) -> EvalReport` | Per question: one `retrieve`, then `judge_result` on that same result (so `hit` and the Bar 2 denominator come from the pre-abstention files, C4). The decision equals `respond`'s for the same inputs. |

**New file justification.** `aveto_support/judge.py` is a new adapter boundary for a third model with its own pin, output head and fail-closed messages. Folding it into `rerank.py` would mix two models' pins and approvals in one file and blur which approval covers what. It reuses `embed.WordPiece`, `embed.verify_file`, `embed.INPUT_NAMES`, `rerank.encode_pair`; it adds no dependency.

### 6.3 Adapter boundary

| Boundary | Default adapter | Placeholder behaviour |
|---|---|---|
| Answerability judge (`judge.Judge` protocol: `logits(question, passage_text) -> tuple[float, ...]`) | `OnnxJudge` (local ONNX Runtime, files from `models/<owner>--<name>/<revision>/`) | `PlaceholderJudge.logits` raises `RuntimeError("answerability judge model is not configured in this build.")`, so tests without model files cannot silently answer or abstain |

Deterministic side: ranking, the choice of which passages are judged, the head transform, the max, the threshold comparison, the output format. Model side: one forward pass per (question, passage) pair returning logits. The model never sees anything but the question and a shown passage; nothing it returns is printed except the derived `p`.

### 6.4 Audit / feedback / usage events

The product has no event log; `retrieve` and `eval` change no state. The only state-changing function touched is `ingest` (writes the model cache).

| Event | Emitted from | Fields |
|---|---|---|
| judge files status (usage/audit, stdout line) | `__main__.py` after `run_ingest` | `judge files: <fetched|cached> (sha256 verified before use)`, model, revision |
| abstention decision (usage, stdout line) | `__main__.py:format_*` | `no confident match` + `Decided by:` line: model, revision, method, n pairs, best p, threshold |
| answer decision (usage, stdout line) | `__main__.py:format_result` | `Judge: answers (...)` line, same fields |
| per-question judge verdict (usage, eval line) | `evaluate.py:format_report` | id, `p`, answered/ABSTAINED, bar summaries |

No new feedback channel. No question or passage text is written anywhere but stdout.

### 6.5 Integration points

- `aveto_support.search.retrieve`, `Searcher`, `ranking_mode` — first stage, unchanged.
- `aveto_support.embed` — `WordPiece`, `verify_file`, `INPUT_NAMES`, `passage_input`, `ModelError`.
- `aveto_support.rerank.encode_pair` — the pair encoding (reused, not modified).
- `aveto_support.ingest` model-fetch helpers used by `ensure_reranker_files` (host allow-list, 40-hex check, hash-then-use) — reused for the judge, not reimplemented.

## 7. Implementation scope (A4) and test plan

### 7.1 Files A4 touches: 10 (at the limit; an 11th means split and return to the EM)

| # | File | Change |
|---|---|---|
| 1 | `aveto_support/judge.py` | **new**: `JudgeParams`, `DEFAULT_PARAMS`, `Judge`, `PlaceholderJudge`, `judge_dir`, `OnnxJudge`, `probability` |
| 2 | `aveto_support/search.py` | `JudgeVerdict`, `Answer`, `Abstention`, `judge_result`, `respond`; `retrieve` docstring only |
| 3 | `aveto_support/__main__.py` | load/close the judge; `format_result` (Top score wording, `Judge:` line); new `format_abstention`; `main(..., judge=None)` |
| 4 | `aveto_support/evaluate.py` | `score(..., judge, params)`, `QuestionOutcome`/`EvalReport` fields, `format_report` lines (5.2) |
| 5 | `aveto_support/ingest.py` | `ensure_judge_files`, call it on every ingest, `judge_status` |
| 6 | `tests/test_judge.py` | **new**: adapter tests |
| 7 | `tests/test_search.py` | decision and INV-4 tests |
| 8 | `tests/test_evaluate.py` | bar, exit-code and CLI tests; modify `test_main_closes_loaded_adapters_in_reverse_order` |
| 9 | `tests/test_ingest.py` | judge fetch/hash/offline tests |
| 10 | `tests/conftest.py` | a `FakeJudge` (fixed scores) and an autouse fixture that injects a fake "always answers" `OnnxJudge.load` for existing CLI tests that call `main()` without a judge, so their assertions stay unchanged; opted out by a `real_judge_load` marker in the judge-loading tests |

Not in A4 (and why): `.agentic/SAFETY_INVARIANTS.md` (the Orchestrator applies the owner-approved text verbatim, in the method commit); `.agentic/LOCAL_COMMANDS.md` (the Orchestrator updates the `retrieve`/`eval`/`ingest` rows to describe abstention and the judge download, no figures, at the method commit); `docs/ARCHITECTURE.md` (Architect-owned; delta text in Appendix B, applied at the method commit); `docs/adr/0007-*.md` (Architect, this stage); `README.md` line 50 and `.agentic/CURRENT_MVP_STATUS.md` line 12 (**after the Release Gate verdict only**, C6; A4 writes no whole-pipeline figure). `tests/test_rerank.py` must not need edits; if the conftest fixture cannot cover it, A4 stops (that would be an 11th file).

### 7.2 Tests to add (names are binding: INV-4/INV-5 cite them)

`tests/test_judge.py`
- `test_judge_revision_must_be_40_hex`
- `test_judge_sha256_must_be_64_hex`
- `test_placeholder_judge_raises`
- `test_judge_absent_fails_closed_without_download`
- `test_judge_cached_file_rehashed_before_use`
- `test_judge_rejects_unexpected_inputs_or_output_shape`
- `test_judge_returns_only_scores` (the adapter returns a tuple of floats and nothing else)
- `test_probability_head_transform` (sigmoid1 and softmax2, arity and non-finite rejected)
- `test_judge_onnx_signature_matches_pin` (`@pytest.mark.model`, real cached files)

`tests/test_search.py`
- `test_abstains_when_no_shown_passage_reaches_threshold`
- `test_answers_when_one_shown_passage_reaches_threshold` (boundary: `best == 0.5` answers)
- `test_abstention_carries_no_passages` (type has no files field; formatted output has no path/URL/excerpt)
- `test_abstention_output_is_exactly_no_confident_match` (fourth stdout line `== "no confident match"`, exit 0)
- `test_abstention_names_deciding_signal`
- `test_judge_reads_only_question_and_shown_passages` (a recording fake sees exactly the shown passages of the five files, in rank order, once each)
- `test_judge_never_changes_shown_files_or_order` (answered output byte-equal to the first-stage formatting apart from the two specified lines)
- `test_judged_hits_are_verbatim_passages`
- `test_judge_error_shows_no_passages_and_exits_2` (raising fake, non-finite fake: stderr error, empty stdout, exit 2)
- `test_judge_applies_on_reranked_path` (fakes for both)

`tests/test_evaluate.py`
- `test_always_abstain_judge_fails_bar_two` — **the test that proves an always-abstain system fails Bar 2**: a synthetic eval set with answerable questions whose accepted file is in the top 5 and some unanswerable ones; a `FakeJudge` returning p = 0.0 for every pair; asserts `bar1_abstained == u`, `bar2_kept == 0`, `bar2_denominator == h > 0`, `bar2_passed is False`, and the printed `abstention bar 2:` line ends `FAIL`.
- `test_never_abstain_judge_fails_bar_one` (p = 1.0 everywhere -> `bar1_passed is False` when u > 0)
- `test_bar_two_denominator_is_pre_abstention_hits` (a hit that is abstained stays in the denominator)
- `test_bar_thresholds_are_ceil_eighty_percent` (u = 20 -> 16; u = 24 -> 20; h = 56 -> 45; h = 21 -> 17)
- `test_end_to_end_counts_top5_and_top1`
- `test_eval_exit_code_unchanged_by_abstention` (all-abstain judge with >= 80% pre-abstention hits still exits 0; below 80% still exits 1)
- `test_eval_judge_error_aborts_with_exit_2_and_no_report`
- modified: `test_main_closes_loaded_adapters_in_reverse_order` (three adapters: judge, then reranker, then embedder)

`tests/test_ingest.py`
- `test_default_ingest_fetches_and_rehashes_judge`
- `test_judge_hash_mismatch_rejected_and_deleted`
- `test_judge_redirect_outside_hf_co_refused`
- `test_retrieve_is_offline_with_cached_judge`
- `test_index_bytes_unchanged_by_judge_fetch`
- unchanged and still required to pass: `test_default_ingest_fetches_no_reranker`, `test_default_ingest_makes_no_reranker_request`, `test_retrieve_is_offline_with_cached_model`, and every test INV-4/INV-5 already names.

Existing INV-4 tests (`test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file`, `test_hybrid_hits_are_verbatim_passages`, the three reranked ones): **unchanged**, must pass.

### 7.3 Runs

- Targeted first: `uv run pytest tests/test_judge.py tests/test_search.py tests/test_evaluate.py tests/test_ingest.py`.
- Full regression before the method commit: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, and `uv run pytest -m model` (needs the judge files that `ingest` fetches after the rule 5 approval).
- Seen-set confirmation (4.1): `uv run python -m aveto_support eval --eval-file evals/<set>.toml` for the four seen sets, raw output saved. Latency: time two non-eval `retrieve` probes and report seconds, not gated.
- Any exit 134 in these runs is recorded (C7 spirit) and reported; no retry wrapper.

## 8. Rule 4 requests: exact text for the owner (nothing here is approved)

Shown verbatim so the owner approves words, not a description. The Orchestrator applies approved text in the method commit; until then `.agentic/SAFETY_INVARIANTS.md` is not edited.

### 8.1 INV-4 (model path) — two items, approve each separately

**Item 4-i, correcting the stale clause.** Today INV-4's first sentence says retrieval returns passages "or 'no confident match' with no passages"; the code has not done that since ADR 0004. Replace that clause so it is true once this slice's code lands (apply only in the same commit as the code):

- from: `each with path, heading and line range, or "no confident match" with no passages.`
- to: `each with path, heading and line range, or exactly "no confident match" with no passages and the name of the signal that decided.`

**Item 4-ii, the new sentence (Q5: it states four things not true today: what the judge may read, that it returns only scores, that it can only cause an abstention, and the fail-closed rule).** Append after the bold sentence:

> A model may judge whether the passages retrieval would show answer the question: it reads only the question and those passages, returns only a score for each pair, can only turn a result into "no confident match", and if its files are missing or fail their sha256, or it errors, the command exits with an error and shows no passages.

Full INV-4 after both items (for review; the bold sentence and the existing test list are unchanged):

> - **INV-4** — Retrieval returns only verbatim passages from the configured source at its pinned commit, each with path, heading and line range, or exactly "no confident match" with no passages and the name of the signal that decided. It never returns generated or reworded text. **A model may be used only to rank passages and to decide confidence. It never produces, selects fragments of, or alters the text returned.** A model may judge whether the passages retrieval would show answer the question: it reads only the question and those passages, returns only a score for each pair, can only turn a result into "no confident match", and if its files are missing or fail their sha256, or it errors, the command exits with an error and shows no passages.
>   *(Enforced by `test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file`, `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method, `test_reranked_hits_are_verbatim_passages`, `test_reranked_result_invariant_enforced` and `test_reranker_returns_only_scores`; for abstention, `test_abstention_carries_no_passages`, `test_abstention_output_is_exactly_no_confident_match`, `test_judge_reads_only_question_and_shown_passages`, `test_judge_never_changes_shown_files_or_order`, `test_judged_hits_are_verbatim_passages`, `test_judge_returns_only_scores`, `test_judge_error_shows_no_passages_and_exits_2` and `test_judge_absent_fails_closed_without_download`.)*

### 8.2 INV-5 (model path only) — a separate rule 4 item, plus one optional line

The slots `<JUDGE_MODEL_ID>` and `<JUDGE_REVISION>` are filled **only** from ADR 0007 after the verification spawn; the owner is shown the text with real values, never with slots.

Replace INV-5 (b) and the sentence after it with:

> (b) the pinned files of exactly three local models — the configured embedding model (`docs-source.toml`), the answerability judge `<JUDGE_MODEL_ID>` pinned in `aveto_support/judge.py`, and the reranker model pinned in `aveto_support/rerank.py` — each requested from `huggingface.co` at its own full 40-hex revision, with redirects only to hosts under `hf.co` (for example `us.aws.cdn.hf.co`).
> Of the three models, the default path fetches the embedding model's and the judge's files: **`ingest`** fetches the reranker's files only when run with **`--with-reranker`**.

The rest of INV-5 is unchanged. Append to its test list: `test_judge_revision_must_be_40_hex`, `test_judge_hash_mismatch_rejected_and_deleted`, `test_judge_cached_file_rehashed_before_use`, `test_judge_redirect_outside_hf_co_refused`, `test_default_ingest_fetches_and_rehashes_judge`, `test_retrieve_is_offline_with_cached_judge`, `test_judge_absent_fails_closed_without_download`.

(The revision is recorded in `judge.py` and ADR 0007, not in INV-5's prose, matching how the two existing models are named. If the owner wants the revision in the invariant, add ` at revision <JUDGE_REVISION>` after the model ID.)

**Optional line (slice 4 advisory A1, due at this INV-5 touch; add only if the owner approves this exact text):**

> On the default path, `retrieve` and `eval` load only the cached embedding model and judge, and make no network call (`test_retrieve_is_offline_with_cached_judge`).

### 8.3 If the slice stops (option d) — INV-4 correction only

Replace the first sentence of INV-4 with:

> Retrieval returns only verbatim passages from the configured source at its pinned commit, each with path, heading and line range; it does not abstain (a question the docs do not answer still returns its top files, and `eval` reports unanswerable questions as a diagnostic).

No new sentence; INV-5 untouched; slice 4's A1 stays carried forward.

### 8.4 Rule 5 request (model path), shape only

"Approve downloading and using `<JUDGE_MODEL_ID>` at revision `<JUDGE_REVISION>`, files `onnx/model.onnx` (sha256 `<…>`) and `vocab.txt` (sha256 `<…>`), licence `<…>`, training data `<…>` as recorded in `docs/adr/0007-answerability-judge.md`, as the default-path answerability judge." Made only after ADR 0007's fact table is complete. Not made by me.

## 9. ADR

Written as a draft at `docs/adr/0007-answerability-judge.md` (the write was allowed). Status **draft — facts not yet verified**: its model-fact table has open slots that only the verification spawn (3.4) can fill. It must be complete, and its status moved to **proposed**, before the rule 5 request. It records the decision, the alternatives (including reusing the reranker), and the consequences, and claims nothing about whether the judge works. If the slice stops, it is marked **rejected** with the reason.

`docs/ARCHITECTURE.md` is not edited now: it describes the system as it stands, and the judge does not exist yet. The delta is Appendix B, applied at the method commit.

## 10. Freeze and the post-freeze rule

- **Method commit:** the one commit that contains A4's code and tests, the owner-approved INV-4/INV-5 text, and the `LOCAL_COMMANDS.md`/`ARCHITECTURE.md` updates, made **after** the seen-set confirmation (4.1) passes and the full regression is green. The Orchestrator records its full 40-hex SHA in `STATE.md` as `Method commit: <sha>`, together with the sha256 of `index/docs-index.json` and of the two judge files in `models/` used for the confirmation.
- **Abstention-decision code** (a change to any of these after the method commit voids the fifth set; it becomes a seen set and the slice needs a new one):
  - everything under `aveto_support/` (the decision path imports `judge.py`, `search.py`, `embed.py`, `index.py`, `rerank.py`, `evaluate.py`, `__main__.py`; `ingest.py` holds the judge fetch and is included so the pinned files cannot change);
  - `pyproject.toml` and `uv.lock` (an ONNX Runtime or numpy change can change scores);
  - `docs-source.toml` (corpus and embedding pin);
  - the index and model files: the scorer re-checks the recorded sha256 of `index/docs-index.json` and the judge files before scoring.
- **Check:** `git diff --name-only <method-sha> HEAD -- aveto_support pyproject.toml uv.lock docs-source.toml` prints nothing at scoring, and B2 scores at exactly `<method-sha>`.
- **Do not void:** `tests/`, `docs/`, `README.md`, `.agentic/`, `runs/`, and the commit that adds the fifth set under `evals/`.
- **Recommendation (for the Orchestrator; within Q1):** run Security (B3) on the method commit **before the fifth set is committed into the repo**. A decision-code fix B3 requires then gives a new method commit (a re-freeze) without voiding anything, since nobody on the method side has seen the set. Once the set is in the repo, any decision-code change voids it.

## 11. Rollback plan

Executable from this spec alone:

1. `git revert <method-sha>` (the method commit is one focused commit). This removes `aveto_support/judge.py` and the judge tests, restores `retrieve`/`eval` output and `ingest` to the pre-slice behaviour (never abstains; default ingest fetches only the embedding model), and restores the pre-slice INV-4/INV-5, `LOCAL_COMMANDS.md` and `ARCHITECTURE.md` text.
2. The revert restores INV-4's stale clause. Reverting a safety-control text is itself a rule 4 change: ask the owner to approve the section 8.3 wording (the "does not abstain" correction), and apply it in a follow-up commit.
3. If the README / `CURRENT_MVP_STATUS.md` status lines were updated after the verdict, revert those lines in the same follow-up commit.
4. Optional local cleanup: delete `models/<judge owner>--<judge name>/` (gitignored cache). Nothing else on disk depends on it.
5. No re-ingest: the index is byte-identical with or without the judge.
6. Write a new ADR that supersedes ADR 0007 (if it was accepted) recording why; do not edit 0007.
7. Verify: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`; `retrieve` lists five files for any question again.

<!-- next -->
