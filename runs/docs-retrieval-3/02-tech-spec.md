# Tech Spec — docs-retrieval-3 (slice A): a local cross-encoder reranker over `file-rrf-v1`

> Software Architect, depth standard, one fresh spawn, 2026-09-30.
> Sources read: `intent.md`, `00-slice-plan.md`, `01-scope.md`, `STATE.md`, `.agentic/*` (all four), `docs/adr/0003`, `docs/adr/0004`, `runs/docs-retrieval-2-proof/02-close-out.md`, `aveto_support/{embed,search,index,ingest,__main__,evaluate}.py` (targeted), `docs-source.toml`, test names (grep), `tests/fixtures/gen_wordpiece_golden.py`, playbook `docs/HUMAN_APPROVAL_RULES.md` (rules 4 to 6, "How to ask") and `project-packs/ai-agent-product.md` ("Held-out gates").
> **Not read:** any `evals/*.toml`, any eval-run output, any per-question result beyond the close-out's one-line summary. No model page, website or file was opened; nothing was downloaded, installed or run.
>
> Fact labels: **VERIFIED** = read in this repo in this session. **REPORTED** = from published documentation as I know it, not checked in this session (the Orchestrator confirms before A1). **TO BE FILLED** = unknown to me; supplied by the Orchestrator from published metadata before the owner answers A1.

## Summary

Add one second stage to retrieval. `file-rrf-v1` (unchanged) ranks all files; its **top N = 20 files** are re-scored by a local cross-encoder, **`cross-encoder/ms-marco-MiniLM-L6-v2`** (6-layer MiniLM, ~22.7M parameters, Apache-2.0, REPORTED), run from its own fp32 `onnx/model.onnx` with `onnxruntime` + `numpy` and the repo's existing hand-rolled WordPiece. Each candidate file's score is the **maximum cross-encoder logit over the passages `file-rrf-v1` already shows for that file** (at most `per_file_cap` = 2). The final order of the 20 is **by that score alone**, ties broken by the first-stage rank; the top 5 are returned with exactly the passages, headings, line ranges and permalinks `file-rrf-v1` would have shown for them. The new method is `file-rerank-v1`. The model reads the question and passage text and returns one float per pair; it never returns, selects or alters text.

`file-rrf-v1` stays runnable from the same code (`--ranking file-rrf-v1`) for slice B's diagnostics. Corpus, index, first stage and embedding model are unchanged: `embed.py`, `index.py`, `evaluate.py`, `docs-source.toml`, `tests/test_search.py` and `tests/test_index.py` are not edited, and the index sha256 does not change. No new dependency (`pyproject.toml`, `uv.lock` unchanged). **12 files**, under the cap of 13.

Nothing below was chosen by a score on any eval set. Every choice (model, N, the unit scored, the combination, ties) is argued on general grounds in this document, before any run, and recorded as argued. Nothing is downloaded until A1 and A2 (`02-approval-request.md`) are answered yes in the owner's own words.

## Traceability: intent "Done means" to design

| Done means | Satisfied by |
|---|---|
| Starts from `main` (`file-rrf-v1`, 123-file corpus, pack v12); corpus, first stage, embedding model unchanged | Base 36c9cff. First-stage code path is the existing one; with no reranker, `retrieve` is byte-for-byte today's (section "Service surface", S2). `embed.py`, `index.py`, `docs-source.toml` untouched; `tests/test_search.py` untouched and passing is the regression proof; index sha256 unchanged (section "Test plan", T-REG) |
| Local reranker over the first stage's top-N, N argued; reads text, never produces it; exact revision, per-file sha256, ONNX Runtime + numpy, no PyTorch, no `trust_remote_code`; rule 4 and 5 approval first | Sections 1 to 4 below; adapter boundary (`Reranker` protocol, scores only); A1 and A2 in `02-approval-request.md`; pin in `aveto_support/rerank.py` |
| Freeze first; fourth held-out set; label review and scoring by different fresh QA spawns | Out of slice A's code; the freeze set (method files) is listed in section "Freeze set"; the set format in `evals/` is unchanged |
| Gate: a correct file in the top 5 for at least 80% of answerable | Unchanged `evaluate.py` scoring; `eval` exit codes unchanged |
| Three earlier sets reported with `file-rrf-v1` on the same sets | `--ranking {file-rerank-v1,file-rrf-v1}` on `retrieve` and `eval`, same index, same code; `eval` prints the ranking method on its first line |
| Earlier guarantees hold (deterministic ingest, provenance, no generative model, no network outside ingest/CI setup, every model file hash-checked) | Index unchanged; passages shown are the first stage's own `PassageMatch` objects; the cross-encoder is a classifier (one logit), not a generator; reranker files fetched only by `ingest`, re-hashed before every use; INV-5 extended (A2) |

## 1. The model, argued on general grounds

### 1.1 What is needed

A **cross-encoder**: a model that reads the question and one candidate passage together and outputs one relevance score. It differs from the existing bi-encoder (bge-small), which embeds question and passage separately and compares vectors. Reading both together lets every question token attend to every passage token, which is the published reason cross-encoders re-rank better than bi-encoders at the same size (Nogueira and Cho 2019, "Passage Re-ranking with BERT"; the sentence-transformers retrieve-and-rerank documentation). That is the general ground for "a reranker", independent of any result here.

Hard constraints from the intent and scope: local; ONNX Runtime + numpy only; no PyTorch; no `trust_remote_code`; reads text, never produces it (so no generative or LLM reranker); one pinned revision; every file sha256-checked; tokenised with the existing dependencies (scope R2); a file under the existing `MODEL_MAX_BYTES` = 200,000,000 cap (VERIFIED, `ingest.py:45`), which I keep rather than raise.

### 1.2 Proposal: `cross-encoder/ms-marco-MiniLM-L6-v2`

| Property | Value | Label |
|---|---|---|
| Repository | `https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2` (the sentence-transformers team's `cross-encoder` organisation; the repo was formerly named `ms-marco-MiniLM-L-6-v2`) | REPORTED; the Orchestrator confirms the **canonical** id so the request URL needs no rename redirect |
| Revision | full 40-hex commit | **TO BE FILLED** |
| Architecture | `BertForSequenceClassification`, 6 layers, hidden 384, 12 heads, 1 output label (a single logit) | REPORTED; checked at load (output last dimension = 1) |
| Parameters | ~22.7M | REPORTED |
| Training | distilled from larger cross-encoders on MS MARCO passage ranking; base `microsoft/MiniLM-L12-H384-uncased` cut to 6 layers | REPORTED |
| Licence | Apache-2.0 (model card). **Caveat for the owner:** the training data, MS MARCO, is published under terms that restrict it to non-commercial research use. Whether that reaches a model trained on it is a legal question I cannot settle; it is surfaced in A1, not decided here | REPORTED |
| Files used | `onnx/model.onnx` (fp32 export, expected ~91 MB) and `vocab.txt` (expected 231,508 bytes) | **sizes and sha256 TO BE FILLED** |
| ONNX inputs / output | `input_ids`, `attention_mask`, `token_type_ids` (int64) / `logits`, shape `[batch, 1]` | REPORTED; asserted at load |
| Tokenizer | BERT uncased WordPiece, `do_lower_case = true`, 30,522-entry `vocab.txt`, max 512 tokens | REPORTED; see 1.3 |
| Remote code | none (`BertForSequenceClassification` is a stock architecture) | REPORTED |
| Published quality | TREC DL 2019 NDCG@10 74.30; MS MARCO dev MRR@10 39.01 (sentence-transformers "MS MARCO cross-encoders" table) | REPORTED |

**Why this one, on general grounds:**

1. **Size and CPU cost.** It is the smallest model in its family that keeps essentially all of the family's published quality: the 12-layer sibling reports 74.31 / 39.02 against this model's 74.30 / 39.01, at about twice the compute; the 2- and 4-layer siblings and TinyBERT-L2 lose 1 to 7 points. Its width (hidden 384) equals bge-small's, with half its layers, so its per-pair CPU cost is about half of one bge-small embedding (section 1.4). Download ~91 MB, inside the existing 200 MB file cap.
2. **Tokenizer compatibility (scope R2).** It uses BERT's uncased WordPiece. The repo already has a WordPiece implementation that passes a golden-file test against the reference tokenizer (`test_wordpiece_matches_golden`, fixture generated from `tokenizers` 0.22.2, VERIFIED). No new tokenizer code, no new library (section 1.3).
3. **ONNX availability.** The `cross-encoder` organisation publishes ONNX exports in the model repository itself (`onnx/model.onnx`, plus quantised and optimised variants), so nothing is converted locally and no PyTorch is needed. I choose the **plain fp32 `onnx/model.onnx`** and none of the variants: the `qint8_avx512` / `arm64` / `quint8_avx2` files are tied to a CPU instruction set and would make results depend on the machine; the `O1` to `O4` files are graph-optimised for specific hardware (O4 is fp16 for GPU). fp32 is the portable, deterministic choice, matching how bge-small is run. REPORTED; the Orchestrator confirms the file exists at the pinned revision.
4. **No `trust_remote_code`**, a stock architecture, and a permissive model licence.
5. **It reads, it does not write.** A sequence-classification head emits one number. There is no decoder and no vocabulary output; it cannot produce text.
6. **Fit to the problem, stated generally.** It is trained to judge whether a passage answers a question, which is the judgement a lexical-plus-embedding first stage approximates. The close-out's five misses (narrow files losing to broader neighbours) are the motivation for a reranker in the intent; they are not evidence I fitted to, and I have not seen where those files ranked.

### 1.3 Tokenisation with the existing code

- `bge-small-en-v1.5`'s `vocab.txt` (sha256 `07eced37…2038a3`, VERIFIED in `docs-source.toml`) is BERT-base-uncased's vocabulary, and `MiniLM-L12-H384-uncased`, this model's base, uses the same vocabulary. **I therefore expect the reranker's `vocab.txt` to be byte-identical, with the same sha256.** REPORTED, and **a precondition of this proposal**: if the published sha256 of the reranker's `vocab.txt` is not `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`, or its `tokenizer_config.json` does not say `do_lower_case: true`, the proposal is void and comes back to the Architect (a new golden fixture would be needed, which costs two more files and a reference-tokenizer run of its own).
- With the same vocabulary and the same BERT basic-tokenizer settings, `embed.WordPiece` is already proven against the reference by `tests/fixtures/wordpiece_golden.json`. The reranker loads its **own** pinned `vocab.txt` (each model's directory is self-contained and separately hash-checked) into the **same** `embed.WordPiece` class, imported, not changed.
- **Pair layout** (BERT standard, as `BertTokenizer` builds pairs): `[CLS] q [SEP] p [SEP]`; `token_type_ids` 0 for `[CLS]`, `q` and the first `[SEP]`, 1 for `p` and the final `[SEP]`; `attention_mask` all ones; batch size 1, so no padding.
- **Truncation**, a fixed rule of this spec (not the reference's `longest_first`, whose tie behaviour I do not want to depend on): question content ids capped at **64** (end trimmed); the passage gets the rest, `512 − 3 − len(q)` content ids (end trimmed). 64 WordPiece tokens is about 45 to 50 English words, longer than any normal support question, and leaves at least 445 tokens for the passage. For any question under 64 tokens this equals the reference's `only_second` and `longest_first` truncation.
- **Passage text given to the model:** `embed.passage_input(passage)`, the heading trail, a newline, then the verbatim body: the exact string the embedding model already sees. No new formatting choice; the heading trail carries the file's H1 title, which is the standard "title + passage" input for document reranking. The file path is not added (the first stage already uses it lexically; the model was not trained on path strings).
- The question is given as typed. bge's retrieval prefix is not used (it is an instruction for bge only).

### 1.4 CPU latency (estimate, UNVERIFIED)

VERIFIED anchor: `ingest` embeds 890 passages with bge-small (12 layers, hidden 384, single thread) in about 80 s, about 90 ms per passage including overhead (`LOCAL_COMMANDS.md`). This model has 6 layers at the same width, so about 45 to 60 ms per pair, a little more for the added question. At N = 20 files and at most 2 passages per file, at most 40 pairs: **about 2 to 2.5 s per question on one core**, worst case. Model load (hash ~91 MB + session) about 1 s per process. An eval run of ~24 questions takes about a minute. The Implementer reports measured figures in `03-implementation.md` from non-eval questions only; a slow measurement is reported, not used to change N.

### 1.5 Alternatives considered and rejected

| Candidate | Why not |
|---|---|
| `cross-encoder/ms-marco-MiniLM-L12-v2` | Same reported quality (74.31 / 39.02), twice the CPU cost and download |
| `cross-encoder/ms-marco-MiniLM-L4-v2`, `-L2-v2`, `ms-marco-TinyBERT-L2-v2` | Cheaper, but reported 1 to 7 points weaker; the cost of L6 is already small |
| `cross-encoder/ms-marco-electra-base` | Same WordPiece vocabulary, but ~110M parameters (about 10× the compute) and reported weaker than MiniLM-L6 in the same table |
| `BAAI/bge-reranker-base` / `-large` / `-v2-m3` | XLM-RoBERTa SentencePiece tokenizer: a new library or a hand-rolled unigram tokenizer (a correctness risk, scope R2); 278M to 568M parameters, ~1.1 to 2.3 GB fp32, over the file cap |
| `mixedbread-ai/mxbai-rerank-xsmall-v1` / `-base-v1` | DeBERTa-v2/v3 SentencePiece tokenizer: same problem |
| `Alibaba-NLP/gte-reranker-modernbert-base` | ModernBERT BPE tokenizer (new tokenizer code); ~149M parameters |
| `jinaai/jina-reranker-v1-tiny-en` / `-turbo-en` | JinaBERT needs `trust_remote_code` |
| Any LLM reranker, query rewriting | Generative; out of scope (intent) |
| Hosted reranking (Cohere, Voyage, Jina API) | Question and doc text leave the machine (INV-5, rule 6); API key; out of scope |

## 2. The method `file-rerank-v1`, argued before any result

All values below are pre-registered constants in code (`RerankParams`, section "Data model deltas"). None has a tuning knob exposed on the command line, and none may change after a run except by a new intent.

### 2.1 How many candidates: N = 20 files

- The reranker can only promote a file the first stage put in its top N, and can only hurt by promoting a wrong file from inside the top N into the top 5. A larger N raises the ceiling and the exposure together; the cost grows linearly.
- **N must be well above the output's 5**, or the reranker can only shuffle what is already returned and cannot fix a near miss. 20 is 4× `top_k`.
- **N must be well below the corpus size**, or the first stage stops being a filter and the reranker becomes the sole ranker, with its domain shift (web questions to process documentation) unchecked. The corpus is 123 files (VERIFIED, close-out); 20 is about one sixth of it. Published retrieve-then-rerank practice re-ranks a short head of the first-stage list (BEIR's cross-encoder baselines use the top 100 of corpora of thousands to millions of documents; on a 123-file corpus 100 would be 80% of it).
- **Cost:** at most 40 pairs, about 2 to 2.5 s per question on one core (section 1.4), which is an acceptable interactive budget for a command-line tool and keeps a full diagnostic run to minutes.
- **What I did not use:** I do not know, and did not look for, the first-stage ranks of any eval question's expected file. The close-out says only that five expected files were outside the top 5; it gives no ranks.

### 2.2 What is scored: MaxP over the passages the first stage shows

A whole file does not fit in 512 tokens. For each candidate file, the cross-encoder scores the passages that `file-rrf-v1` already selects for display in that file (`_matches_in_file`, top `per_file_cap` = 2 by within-file fusion; VERIFIED, `search.py:388-405`), and the file's score is the **maximum** of those logits.

- **MaxP** (a document scored by its best passage) is the standard way to apply a 512-token cross-encoder to longer documents (Dai and Callan 2019, "Deeper Text Understanding for IR with Contextual Neural Language Modeling") and it is already how the first stage's dense list scores files (ADR 0004). Sum or mean over passages would grow or shrink with the number of passages, which ADR 0004 rejected for the same reason.
- **Scoring exactly the shown passages** adds no parameter (it reuses `per_file_cap`) and keeps the evidence for a file's rank identical to what the user sees next to it: the file is ranked by the best of the passages it shows you.
- **Trade-off, recorded:** if the first stage's within-file choice misses the relevant section of a file, the reranker judges that file on its two weaker sections. The alternative, scoring every passage of every candidate file, would cost about 140 pairs on average (890 passages / 123 files × 20) and unboundedly more for long files, and would change which passages are displayed; rejected on cost and on scope (one change only).

### 2.3 How the score combines with the first stage: the reranker's order replaces it within the top N

- The final order of the N candidates is by the cross-encoder MaxP score, descending. The first stage decides **which** N files are candidates and breaks exact ties (2.4); it does not otherwise vote.
- **Why replacement:** the cross-encoder reads the question and the passage together, so it has strictly more information about each pair than BM25 or the bi-encoder; this is the standard monoBERT design (Nogueira and Cho 2019), where the first stage bounds the candidate set and the cross-encoder orders it. Mixing the first-stage order back in reintroduces exactly the biases a second stage is meant to correct (ADR 0004 records that MaxP favours long, many-section files, and whole-file BM25 favours broad files).
- **Rejected: RRF of the first-stage order and the reranker order** (k = 60, no weight). It needs no tuning, but over 20 items it amounts to averaging two ranks, so a file the reranker puts first but the first stage puts 15th still loses to the first stage's top file whenever the reranker puts that file anywhere in its top 14 (1/61 + 1/74 > 1/75 + 1/61). That halves the reranker's effect by construction.
- **Rejected: a weighted blend of normalised scores** (e.g. `α · logit + (1 − α) · rrf`). Logits and RRF scores have unrelated scales, and α has no principled value; it would be chosen by score, which the intent forbids.
- **Not to be swapped after a result.** If slice B fails, a different combination is a new intent with a new held-out set, not a change to this slice.

### 2.4 Ties and determinism

- **Sort key:** `(-score, first_stage_rank)`. First-stage ranks are distinct integers (the first stage itself ends its sort on the path), so the order is total; exact float ties fall back to the first stage's order.
- **Consequence (and a test):** a reranker that returns the same score for every pair reproduces `file-rrf-v1`'s top 5 exactly. This is how "the reranker only re-orders" is tested without a model.
- **Non-finite scores fail closed.** A NaN or infinite logit raises `ModelError` (exit 2); it is never sorted.
- **Runtime settings,** identical to the embedder's (VERIFIED, `embed.py:235-242`): `intra_op_num_threads = 1`, `inter_op_num_threads = 1`, `ORT_SEQUENTIAL`, `ORT_ENABLE_BASIC`, `CPUExecutionProvider`; batch size 1 (no padding); `OMP/OPENBLAS/MKL_NUM_THREADS = 1` already set by `__main__._limit_threads()`. Pairs are scored in a fixed order (first-stage rank, then passage order).
- **No rounding of logits.** Rounding moves a tie boundary; it does not remove it. Same machine and same inputs give the same output (tested twice in-process and across two sessions). **Across machines**, float32 kernels can differ in the last bits, so a near-tie could flip; slice B therefore scores on the machine where the method is frozen and records the platform and `onnxruntime` version with its evidence. The index is unaffected: reranker scores are computed at query time and never stored.

### 2.5 What `retrieve` prints

Unchanged layout. In `file-rerank-v1` the file line's score is the cross-encoder MaxP logit (in `file-rrf-v1` it stays the file RRF score). The `Ranking:` line names the method and both pins, so every output records which method produced it. The top score (best dense similarity) and the "These are sources, not an answer." line are unchanged. Passage scores, order and text are the first stage's, unchanged.

## Data model deltas

- **Index: none.** No schema change (`aveto-support/index@3` stays), no new field, no re-ingest needed; the index sha256 after `ingest` equals slice 2's for the same config. `index.py` is not edited.
- **Eval file format: none.** `evals/` schema unchanged (scope section 6).
- **Config (`docs-source.toml`): none.** Decision: the reranker pin lives in code, not in config, because (1) it is part of the frozen ranking method, like `k1`, `b` and `rrf_k`, which are code constants in `RetrievalParams`; (2) `retrieve` and `eval` read only the index and `models/`, so a config pin would add a `--config` input to both or put the pin in the index (an `index.py` and schema change the scope forbids); (3) it saves a file. Cost: the embedding model is configurable and the reranker is not, so an adopter who wants a different reranker edits code; any model change needs a rule 5 approval anyway. Recorded in ADR 0005.
- **New frozen dataclass `RerankParams`** in `aveto_support/rerank.py`:

| Field | Value | Note |
|---|---|---|
| `model` | `"cross-encoder/ms-marco-MiniLM-L6-v2"` | canonical id, confirmed in A1 |
| `revision` | 40-hex | from A1 |
| `onnx_file` | `"onnx/model.onnx"` | |
| `onnx_sha256` | 64-hex | from A1 |
| `vocab_file` | `"vocab.txt"` | |
| `vocab_sha256` | `"07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3"` expected | from A1; precondition (1.3) |
| `candidates` | `20` | N (2.1) |
| `max_tokens` | `512` | pair length incl. 3 special tokens |
| `max_question_tokens` | `64` | (1.3) |
| `scoring` | `"ce-maxp-shown-v1"` | label only: MaxP over the shown passages (2.2), replace (2.3) |

`__post_init__` rejects a model id that is not `owner/name`, a revision that is not 40 lowercase hex, and a sha256 that is not 64 lowercase hex (`ValueError`), so a malformed pin cannot be constructed. The passages-per-file count is `RetrievalParams.per_file_cap` (2), read from the index's params, not duplicated.

- **Model cache layout:** `models/cross-encoder--ms-marco-MiniLM-L6-v2/<revision>/{onnx/model.onnx, vocab.txt}`, beside the existing `models/BAAI--bge-small-en-v1.5/<revision>/` (gitignored, VERIFIED `embed.model_dir`).
- **Result types:** unchanged classes. In `file-rerank-v1`, `FileHit.score` holds the MaxP logit; `RetrievalResult.ranking_mode` is `f"file-rerank-v1:hybrid:{emb.model}@{emb.revision}+ce:{rr.model}@{rr.revision}:n{rr.candidates}"`. In `file-rrf-v1` both are exactly today's.

## Service surface

| # | Function / class | File | Signature | Invariants |
|---|---|---|---|---|
| S1 | `Reranker` (Protocol) | `rerank.py` | `score(self, question: str, passage_text: str) -> float` | Returns one finite float. Never returns, stores or alters text |
| S2 | `Searcher.__init__` | `search.py` | `(index, embedder: Embedder \| None = None, reranker: Reranker \| None = None)` | `reranker is None` means `file-rrf-v1`, exactly as today; every existing call site is unchanged |
| S3 | `retrieve` | `search.py` | `(searcher, question) -> RetrievalResult` (unchanged) | Refactored into a private `_first_stage(...)` that returns the full fused file order, the fused scores, `sims` and `lex_scores` (today's lines 410-426, unchanged in behaviour). If `searcher.reranker` is None: top 5 as today. Else: `_rerank(...)` over the first `RerankParams.candidates` files of that order |
| S4 | `_rerank` (private) | `search.py` | `(searcher, question, order, matches_of) -> list[tuple[str, float]]` | Scores each candidate's shown passages (`passage_input(m.passage)`) in fixed order; MaxP; raises `ModelError` on a non-finite score; sorts by `(-score, first_stage_rank)`; returns the top `top_k` |
| S5 | `encode_pair` | `rerank.py` | `(tokenizer: WordPiece, question: str, passage: str, max_tokens=512, max_question_tokens=64) -> tuple[list[int], list[int]]` | Returns `(input_ids, token_type_ids)` per 1.3; pure function |
| S6 | `OnnxReranker` | `rerank.py` | `load(models_dir: Path, params: RerankParams = RerankParams()) -> OnnxReranker`; `score(...)`; `signature() -> GraphSignature` | `load` re-hashes both files with `embed.verify_file` (mismatch deletes and raises `ModelError`) before building the session; never downloads; inputs must equal `embed.INPUT_NAMES`; output last dimension must be 1 |
| S7 | `PlaceholderReranker` | `rerank.py` | `score(...)` raises `RuntimeError("reranker model is not configured in this build.")` | The throwing default for tests that exercise the reranked path without a model |
| S8 | `reranker_dir` | `rerank.py` | `(models_dir, params) -> Path` | `models_dir / model.replace("/", "--") / revision` |
| S9 | `ensure_reranker_files` | `ingest.py` | `(params: RerankParams, models_dir, *, opener=None) -> str` | Same contract as `ensure_model_files`: a cached file is re-hashed and kept only if it matches; otherwise downloaded with `download_model_file`, hashed while streaming, kept only on match. Returns `"downloaded"` or `"cached"` |
| S10 | `download_model_file` | `ingest.py` | first parameter's type widened from `EmbeddingParams` to a small read-only Protocol `_ModelPin` (`model` and `revision` as properties); body unchanged | URL stays `https://huggingface.co/{model}/resolve/{revision}/{name}`; redirects only under `hf.co`; size cap unchanged |
| S11 | `run_ingest` | `ingest.py` | unchanged signature | When it downloads the embedding files (no injected embedder), it also calls `ensure_reranker_files` and then `OnnxReranker.load` (fails early on a bad file). With an injected embedder it fetches no model files, as today. `IngestReport` gains `reranker_status: str = ""` |
| S12 | CLI | `__main__.py` | `retrieve` and `eval` gain `--ranking {file-rerank-v1,file-rrf-v1}`, default `file-rerank-v1`. `main(argv, *, embedder=None, reranker=None, models_dir=...)` | Default mode loads `OnnxReranker` from `models_dir` (or uses the injected one); a missing or bad file exits 2 with "run ingest". **No silent fallback** to `file-rrf-v1`. `file-rrf-v1` never loads or requires reranker files. `eval` prints `Ranking: <ranking_mode>` as its first line. `ingest` prints `reranker files: <status> (sha256 verified before use)` |

No new service file beyond `rerank.py`. Justification: it is the adapter for a second model with its own pin, load and pair encoding; putting it in `embed.py` would edit the frozen embedding module, which the scope forbids, and putting it in `search.py` would mix ONNX loading into the ranking module.

## Adapter boundaries

- **Deterministic side:** first-stage ranking, candidate selection (top 20 by the first stage), passage selection per file (first stage), MaxP, sort and tie-break, output construction. All in `search.py`.
- **Model side:** `Reranker.score(question, passage_text) -> float`. Text goes in; one float comes out. The model never sees the index, paths, or other candidates, and nothing it returns is text.
- **Placeholder:** `PlaceholderReranker` throws by default. The default test suite runs with no model files and no network: tests inject a `FakeReranker` (in `tests/conftest.py`, deterministic, e.g. a token-overlap count, plus a call log) or pass `--ranking file-rrf-v1`. The real `OnnxReranker` is used only under `-m model` and by the CLI in default mode.
- **Load-time trust boundary:** both reranker files are re-hashed against `RerankParams` before every session (`OnnxReranker.load`), as the embedder's are (VERIFIED, `OnnxEmbedder.load`).

## Safety invariant deltas

### INV-4 (retrieval returns only verbatim text; a model may only rank)

**No wording change to the invariant.** Its text already allows "a model may be used only to rank passages and to decide confidence" and forbids producing, selecting fragments of, or altering returned text. The reranker ranks; the returned passages are the first stage's own `PassageMatch` objects; truncation to 512 tokens applies to the model's input only.

**Proposed annotation change only** (the enforcing-test list), because the reranked path needs its own named enforcing tests: add `test_reranked_hits_are_verbatim_passages`, `test_reranked_result_invariant_enforced` and `test_reranker_returns_only_scores`. The existing three enforcing tests are **not retired, rewritten or weakened** (`test_search.py` and `test_index.py` are not edited). Exact text in `02-approval-request.md`, A2.

### INV-5 (egress and hashes)

INV-5 today names exactly two downloads and, in (b), only "the configured embedding model" (VERIFIED). Fetching the reranker's two files without changing it would break it. **Proposed extension:** (b) covers the pinned files of exactly two local models, the embedding model and the reranker, each at its own full 40-hex revision, same host rule, same hash-before-use rule; the enforcing-test list gains the reranker's tests. Every other sentence is unchanged, including "No question, passage or user text ever leaves the machine" and "`retrieve`, `eval` and the default test suite make no network calls". Exact text in `02-approval-request.md`, A2. **No edit to `.agentic/SAFETY_INVARIANTS.md` before A2 is approved; the Implementer applies the approved text verbatim.**

**Rule 6 check (scope section 5):** the files come from `huggingface.co` with redirects under `hf.co`, already INV-5's host; only pinned files are fetched; no question, passage or user text is sent; no credentials. No new subprocessor; `VENDOR_RISK_TEMPLATE.md` does not apply. Confirmed, not assumed: the request URL is built only from the pinned model id, revision and file name (S10).

## Audit / feedback / usage events

The product has no audit log yet (command line only, no state outside `index/` and `models/`). This slice adds no state-changing service function beyond the model cache:

| Function | State change | Record |
|---|---|---|
| `ensure_reranker_files` (via `ingest`) | writes up to two files under `models/` | `ingest` prints `reranker files: downloaded\|cached (sha256 verified before use)`; `IngestReport.reranker_status` |
| `OnnxReranker.load` | deletes a cached file that fails its hash | raises `ModelError` naming the file ("deleted, run ingest"); exit 2 |
| `retrieve` / `eval` | none (read-only) | every output names the method and both model pins (`Ranking:` line / `ranking_mode`), which is the provenance of a result |

No feedback or usage events (no user-facing surface, no spend).

## Integration points

- `embed.py` (imported, not edited): `WordPiece`, `verify_file`, `sha256_file`, `ModelError`, `INPUT_NAMES`, `GraphSignature`, `passage_input`.
- `search.py`: extended (S2 to S4); `_matches_in_file`, `rrf`, BM25 and dense code untouched.
- `ingest.py`: extended (S9 to S11); `download_model_file`, `_HostRestrictedRedirect`, `_hf_host_allowed` reused.
- `evaluate.py`: unchanged; `score()` calls `retrieve(searcher, …)`, which follows the searcher's reranker, so `eval` scores whichever method the CLI built.
- `__main__.py`: extended (S12).

## Files (cap 13, from `01-scope.md` section 4): 12

| # | File | Change | Owner |
|---|---|---|---|
| 1 | `aveto_support/rerank.py` | **new**: `RerankParams`, `Reranker`, `PlaceholderReranker`, `encode_pair`, `OnnxReranker`, `reranker_dir` | Implementer |
| 2 | `aveto_support/search.py` | `Searcher` gains `reranker`; `retrieve` split into first stage + optional rerank | Implementer |
| 3 | `aveto_support/ingest.py` | `ensure_reranker_files`; `_ModelPin`; `run_ingest` fetches and loads the reranker; `IngestReport.reranker_status` | Implementer |
| 4 | `aveto_support/__main__.py` | `--ranking`; `reranker=` injection; load; `Ranking:` line in `eval`; ingest status line | Implementer |
| 5 | `tests/test_rerank.py` | **new** (Test plan) | Implementer |
| 6 | `tests/conftest.py` | `FakeReranker` (deterministic, with a call log), beside `FakeEmbedder` | Implementer |
| 7 | `tests/test_ingest.py` | reranker pin/hash/redirect/offline tests; the existing CLI retrieve test injects `FakeReranker` | Implementer |
| 8 | `tests/test_evaluate.py` | existing CLI `retrieve`/`eval` calls inject `FakeReranker` (default mode now needs one); assertions unchanged | Implementer |
| 9 | `.agentic/SAFETY_INVARIANTS.md` | A2 text verbatim, **only after A2 is approved** | Implementer |
| 10 | `.agentic/LOCAL_COMMANDS.md` | `--ranking`; reranker files in `ingest`; `-m model` additions; latency | Implementer |
| 11 | `.agentic/CURRENT_MVP_STATUS.md` | the two-stage method; runtime deps still `onnxruntime` + `numpy` | Implementer |
| 12 | `docs/adr/0005-cross-encoder-reranker.md` | **new**, status proposed | Architect (this stage) |

**Not edited** (and a `git diff --stat 36c9cff` showing them untouched is part of the evidence): `aveto_support/embed.py`, `index.py`, `evaluate.py`, `docs-source.toml`, `tests/test_search.py`, `tests/test_index.py`, `tests/fixtures/*`, `pyproject.toml`, `uv.lock`, everything under `evals/`. `README.md` and `docs/ARCHITECTURE.md` prose refresh stays deferred (scope section 2; close-out carry-forward (d)). Spare under the cap: 1. The vocab contingency in 1.3 would need 2 more files (a new golden fixture and its generator), so it is a hand-back, not a use of the spare.

## Freeze set (the method files)

Everything that decides ranking at the frozen commit: `aveto_support/rerank.py`, `search.py`, `embed.py`, `index.py`, `ingest.py` (as far as it pins and fetches model files), `__main__.py` (it chooses the default method and builds the searcher), `evaluate.py` (scoring), `docs-source.toml`. QA in slice B diffs `<frozen SHA>..HEAD` over these eight files and expects it empty.

## Test plan

All new default tests are offline (the autouse socket block stays), use synthetic fixtures (`conftest.py` archives, `FakeEmbedder`, `FakeReranker`) and never open `evals/`. `-m model` tests need the cached files that an approved `ingest` fetched.

**`tests/test_rerank.py` (new), default suite:**

| Test | What it proves |
|---|---|
| `test_placeholder_reranker_raises` | the throwing default |
| `test_rerank_params_pin_is_well_formed` | the code pin is `owner/name`, 40-hex, 64-hex; candidates 20 |
| `test_reranker_revision_must_be_40_hex` | `RerankParams(revision="abc123")` raises; same for a 40-char uppercase or a branch name |
| `test_reranker_sha256_must_be_64_hex` | same for both hashes |
| `test_reranker_dir_layout` | `models/cross-encoder--ms-marco-MiniLM-L6-v2/<rev>` |
| `test_pair_encoding_layout` | synthetic vocab: `[CLS] q [SEP] p [SEP]`, `token_type_ids` 0…0 then 1…1, lengths match |
| `test_pair_encoding_truncates_to_512` | long passage: total exactly 512, question intact, passage trimmed at the end |
| `test_pair_encoding_caps_question_at_64` | 100-token question keeps its first 64 content ids |
| `test_constant_reranker_is_identity` | a reranker returning 0.0 for everything gives exactly `file-rrf-v1`'s top 5 (paths, ranks, passages) |
| `test_rerank_only_reorders_top_n` | a fake that scores the first stage's 21st file highest: that file never appears, and the fake was never called with its passages |
| `test_reranker_sees_only_shown_passages` | the call log equals `passage_input` of each of the top 20 files' shown passages, in first-stage order; at most 40 calls |
| `test_rerank_file_score_is_maxp` | a file's `FileHit.score` is the max of its passages' fake scores |
| `test_rerank_ties_break_by_first_stage_rank` | equal scores keep first-stage order |
| `test_rerank_non_finite_score_fails_closed` | NaN and inf raise `ModelError`; CLI exit 2 |
| `test_rerank_is_deterministic` | the same question twice gives identical results |
| `test_reranked_hits_are_verbatim_passages` | **INV-4**: every returned passage is the index's passage object, its text a verbatim slice of the synthetic file at its line range, with path and heading |
| `test_reranked_result_invariant_enforced` | **INV-4**: `FileHit`/`RetrievalResult` validation holds in the reranked path; the reranker cannot inject a path or passage not in the candidates |
| `test_reranker_returns_only_scores` | **INV-4**: a fake that returns a string or a non-float is rejected (`ModelError`); `retrieve` output text contains no string the reranker produced |
| `test_ranking_mode_names_both_models` | `ranking_mode` strings for both methods; `file-rrf-v1` string is exactly today's |
| `test_cli_retrieve_ranking_switch` | `--ranking file-rrf-v1` never calls or loads the reranker and prints today's output; the default calls it and prints `file-rerank-v1` |
| `test_cli_eval_ranking_switch_on_synthetic_set` | on a synthetic eval file in `tmp_path`, both modes run from the same index and print their `Ranking:` line; exit codes per the existing 80% rule |
| `test_cli_default_mode_without_reranker_cache_exits_2` | no files, no injection: exit 2, "run ingest", and no fallback output |

**`tests/test_rerank.py`, `-m model` (need the approved cached files):**

| Test | What it proves |
|---|---|
| `test_reranker_tokenizer_matches_golden` | **the tokenizer golden test.** First asserts the reranker's cached `vocab.txt` sha256 equals the fixture's recorded `vocab_sha256` (`07eced37…`); then `OnnxReranker.load(...).tokenizer.encode(case["text"]) == case["ids"]` for every case in the existing `tests/fixtures/wordpiece_golden.json` (reference: `tokenizers` 0.22.2). If the hashes differed, this test fails loudly rather than passing vacuously |
| `test_reranker_onnx_signature` | inputs equal `INPUT_NAMES`; output rank 2, last dimension 1 |
| `test_reranker_scores_repeatable` | two sessions, three hand-written pairs: identical floats |
| `test_reranker_known_answer` | on hand-written, non-eval pairs (e.g. "How do I install the package?" against an installation paragraph vs a paragraph about release notes), the relevant one scores higher. A sign-of-life check on segment ids and output parsing; written before any run, never changed to fit |

**`tests/test_ingest.py` (extended):**

| Test | What it proves |
|---|---|
| `test_reranker_download_requests_pinned_urls_and_caches` | exactly `https://huggingface.co/<model>/resolve/<40-hex>/{onnx/model.onnx,vocab.txt}`; files land in `reranker_dir` |
| `test_reranker_hash_mismatch_rejected_and_deleted` | **INV-5**: a served file with the wrong hash is not kept; `FetchError`; exit 3 |
| `test_reranker_cached_file_rehashed_before_use` | **INV-5**: a tampered cached file makes `OnnxReranker.load` delete it and raise `ModelError` |
| `test_reranker_redirect_outside_hf_co_refused` | **INV-5**: same host rule as the embedding files |
| `test_ingest_fetches_reranker_with_embedding` | with `ensure_model_files`, `OnnxEmbedder.load`, `ensure_reranker_files` and `OnnxReranker.load` monkeypatched to record calls (fake ONNX bytes cannot be loaded), `run_ingest` without an injected embedder fetches and loads both models, and with an injected embedder fetches neither; `reranker_status` set accordingly |
| `test_retrieve_is_offline_with_cached_reranker` | **INV-5**: default-mode `retrieve` with the socket block and an injected reranker makes no network call |
| existing `test_retrieve_is_offline_with_cached_model` | unchanged assertion; now passes `reranker=FakeReranker()` (default mode needs one). Not weakened |
| `@pytest.mark.network test_live_reranker_download_verifies_hashes` | live fetch of the two pinned files; sizes equal the A1 figures |

**`tests/test_evaluate.py`:** existing CLI calls pass `reranker=FakeReranker()`; no assertion changes. **`tests/test_search.py`, `tests/test_index.py`: not edited.** Their passing unchanged (including `test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file`, `test_hybrid_hits_are_verbatim_passages`, `test_retrieve_is_deterministic`) is the proof that `file-rrf-v1` and the first stage are unchanged (**T-REG**). No INV-enforcing test is retired or rewritten.

**Regression (Implementer, after the last commit):** `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, then `uv run pytest -m model`; `ingest` twice, same index sha256, and equal to slice 2's for the same config; `git diff --stat 36c9cff -- <not-edited files>` empty. **Never `eval` on any `evals/` file; `retrieve` only on the Implementer's own non-eval questions, and the method is not changed by what it shows.**

**Slice B's diagnostics (documented in `LOCAL_COMMANDS.md`, run only by slice B's scoring QA):** `eval --ranking file-rerank-v1 --eval-file <set>` and `eval --ranking file-rrf-v1 --eval-file <set>` on the same index, for the fourth set (gate, default method) and the three earlier sets (diagnostics).

## Rollback plan

Nothing in slice A reaches `main`: no push, PR or merge (scope A3). If the gate fails, the branch is not merged and `main` is untouched; that is the rollback.

If the slice ships and must be undone later:
1. **Immediate, no code change:** run `retrieve` / `eval` with `--ranking file-rrf-v1`; the reranker files are not needed or loaded.
2. **Code:** `git revert` the Implementation commits (the range between 36c9cff and the frozen method SHA, recorded in `STATE.md`). This restores files 1 to 8 and 10 to 11. The index needs no rebuild (it never changed).
3. **INV-5 and INV-4 annotation:** reverting `SAFETY_INVARIANTS.md` to its 36c9cff text narrows egress back to one model; it is still an edit to a safety control, so it is done with the owner's yes, recorded like A2.
4. **Cache:** `rm -rf models/cross-encoder--ms-marco-MiniLM-L6-v2/` (gitignored, local only).
5. **ADR:** write ADR 0006 superseding 0005; never edit 0005.

## Risks / open questions

| # | Risk | Control |
|---|---|---|
| R1 | Tuning by score | Every choice argued above, before any run; no CLI knob; no role runs `eval` in slice A; a later change is a new intent |
| R2 | The reranker's vocab is not BERT-base-uncased's | Precondition (1.3): the Orchestrator checks the published sha256 before A1; a mismatch voids the proposal (hand back). The golden test also checks the hash at test time |
| R3 | Domain shift: trained on web questions (MS MARCO), applied to process documentation; it may prefer generic explanatory passages | Accepted risk, reported, not tuned; the first stage still bounds the candidates to 20; slice B reports `file-rrf-v1` beside it so the reranker's own effect is visible, including any harm |
| R4 | Licence: Apache-2.0 weights trained on MS MARCO, whose terms restrict the data to non-commercial research | Surfaced to the owner in A1 as a separate line to weigh; not decided by an agent. For a public template others deploy, the owner may want a legal view before a release (slice B's Release Gate) |
| R5 | Cross-machine float differences flip near-ties | Same-machine scoring for slice B; platform and `onnxruntime` version recorded; index unaffected |
| R6 | Latency of about 2 to 2.5 s per question is an estimate | Implementer measures and reports; it does not change N |
| R7 | The first stage's shown passages miss a file's relevant section (2.2 trade-off) | Recorded; a different unit is a future slice |
| R8 | Silent fallback to the baseline would make a scored run use the wrong method | No fallback (S12); a missing file is exit 2; every output names the method |
| R9 | Hashes and sizes unknown to the Architect | `02-approval-request.md` marks each **TO BE FILLED BY ORCHESTRATOR FROM PUBLISHED METADATA**; the owner approves only once they are filled (scope section 5, option (i)) |
| R10 | A pass is not a release; nothing abstains | Decision 3 holds; carried by slice B's close-out |

**Open, for the Orchestrator before A1:** the canonical repo id, the 40-hex revision, both files' sha256 and sizes, `tokenizer_config.json` `do_lower_case`, and that `onnx/model.onnx` (fp32) exists at that revision.

## Hand off

- **To:** Orchestrator, for A1 and A2 (`02-approval-request.md`). **Stop here.** No Implementation spawn until both are recorded as approved in the owner's own words.
- **Then to:** backend-architect (one fresh spawn), owning all of files 1 to 11 against this spec. The Architect owns file 12 (ADR 0005, written in this stage).
- The Implementer pins exactly the approved id, revision and hashes into `RerankParams`, applies the approved A2 text verbatim, and hands back rather than widening the file list, the INV-5 wording, or the method.
