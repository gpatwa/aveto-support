# ADR 0007: Abstention by a local answerability judge (`abstain-judge-v1`)

> Architecture Decision Record. Owned by the Architect. Never edited after it is accepted. A changed decision gets a new record that supersedes this one.

- **Status:** **proposed.** The fact table is filled from the support session's Reply 1 (`runs/docs-abstention/SUPPORT_REPLIES.md`); those facts are reported by another session and **not independently verified by the Architect**. One fact stays open until the file is loaded in implementation (ONNX input names), and one question is the owner's to decide **before** the rule 5 request (training-data licence, below). The record becomes **accepted** only when the owner has decided that question, approved the model (rule 5) and the INV-4 and INV-5 wording (rule 4), and slice `docs-abstention` passes its Release Gate. Accepting this record is not itself an approval of anything. If the slice stops (option d) or the model is rejected, this record is marked **rejected** with the reason and kept.
- **Date:** 2026-10-09
- **Slice:** `runs/docs-abstention/`. Full specification: `runs/docs-abstention/02-tech-spec.md`.
- **Relates to:** ADR 0004 (retrieval stopped abstaining), ADR 0005/0006 (the reranker and its open MS MARCO licence question; the reranker stays opt-in and is not reused here).

## Context

`retrieve` never abstains (measured, `runs/docs-abstention/02-baseline.md`). On the four seen sets no similarity threshold, margin or combination reaches the owner's bar for shipping without a model (both bars >= 90% pooled and >= 80% leave-one-set-out); the best pooled min(Bar 1, Bar 2) is 0.650. Unanswerable and answerable top scores overlap (unanswerable 0.548-0.808, answerable hits 0.619-0.800).

## Decision

1. Add a local, non-generative answerability judge: a cross-encoder sequence classifier trained on (question, passage) -> "the passage contains the answer". ONNX Runtime + numpy, no PyTorch, no `trust_remote_code`, pinned to one 40-hex revision with a sha256 per file, fetched only by `ingest` (on every ingest, since it serves the default path), re-hashed before every use.
2. The judge scores the question against each shown passage of the five returned files (at most 10). If the best probability is below 0.5 (the model's own decision boundary, not fitted), `retrieve` prints exactly `no confident match`, no passages, and the deciding signal, and exits 0. Otherwise the output is unchanged apart from a verdict line.
3. The judge can only cause an abstention. It never adds, removes, reorders or alters a passage. A missing, hash-failing or erroring judge is an error (exit 2); never an abstention, never a pass-through.
4. The `eval` exit code keeps its meaning (retrieval gate, computed before abstention); the abstention bars are printed.
5. The proposed judge is `cross-encoder/qnli-electra-base` at the revision and with the two files (fp32 `onnx/model.onnx`, `vocab.txt`) in the table below, subject to the owner's licence decision and rule 5 approval.

## Model facts

**Source of every row: reported by the support session ("Aveto AI SDLC", Reply 1 in `runs/docs-abstention/SUPPORT_REPLIES.md`, read 2026-10-09 from public Hugging Face metadata, no weights downloaded), not independently verified by the Architect.** The URLs are the ones that session gives. A wrong hash or revision fails closed at the first `ingest` (sha256 checked before use).

| Fact | Value | Source (as reported, URL @ revision) | Criterion (tech spec 3.2) |
|---|---|---|---|
| Model ID | `cross-encoder/qnli-electra-base` (public, not gated) | `https://huggingface.co/api/models/cross-encoder/qnli-electra-base` | — |
| Revision (40-hex) | `c7dea87c98b2269a935686c31336e97e837cbbeb` (last modified 2025-04-11) | same API, field `sha` | 4: reported met |
| Licence (model card) | `apache-2.0` | `README.md` front matter @ `c7dea87c…` | 5 (model): reported met |
| Base model | `google/electra-base-discriminator` @ `1ae76a97c7e84a4e640876a07453fccd636f0667`, `apache-2.0` | HF API for that repo | 5 |
| Training data | GLUE QNLI ("transformed the SQuAD dataset into an NLI task") | `README.md` @ `c7dea87c…` | 1 |
| Training-data licences | SQuAD: **CC BY-SA 4.0** (share-alike); GLUE dataset card: `other` | `https://rajpurkar.github.io/SQuAD-explorer/`; HF `datasets/rajpurkar/squad`, `datasets/nyu-mll/glue` | 5: **open, owner's question below** |
| Task | "Given a question and paragraph, can the question be answered by the paragraph?"; `ElectraForSequenceClassification` | `README.md`, `config.json` @ `c7dea87c…` | 1: reported met |
| Output head and `id2label` | one logit; `id2label` `{"0": "LABEL_0"}`; card applies `sigmoid`. Pin: `head = "sigmoid1"`, `positive_index = 0` | `config.json`, `README.md` @ `c7dea87c…` | 2: reported met |
| `vocab.txt` | uncased (`do_lower_case: true`), 30,522 entries, 231,508 bytes, sha256 `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`, reported identical to the embedding model's `vocab_sha256` in `docs-source.toml` | file @ `c7dea87c…` | 3 (vocabulary): reported met |
| ONNX inputs (`input_ids`, `attention_mask`, `token_type_ids`), 512 positions | **not verified**: readable only by loading the file. 512 positions and `type_vocab_size` 2 reported from `config.json`. Checked by `OnnxJudge.load` and `test_judge_onnx_signature_matches_pin` in implementation; a mismatch rejects the candidate | — | 3 (graph): **open until loaded** |
| `onnx/model.onnx` (fp32) at the revision | present; 438,212,375 bytes; LFS sha256 `595b37541289472b7b784ed2af05bcad6000991a2657aeee4f92f68b42ae61d9` | API `siblings`, `lfs.sha256` @ `c7dea87c…` | 4: reported met; 6: reported met, narrowly (limit about 450 MB) |
| Custom code / `trust_remote_code` | none (no `*.py` in the repo) | API `siblings` | 4: reported met |

## Open question for the owner (decide before the rule 5 request)

SQuAD's text is licensed CC BY-SA 4.0 (share-alike). QNLI is derived from SQuAD, and this model was trained on QNLI. The model card states Apache-2.0. **Whether the share-alike terms reach the trained weights is a legal question that neither the Architect nor the support session can settle.** It is the same kind of question as the reranker's MS MARCO terms (ADR 0005/0006), which stayed open only because the reranker is opt-in. This model would be on the **default** path, where tech spec criterion 5 does not allow the question to stay open. Options:

1. accept the model card's Apache-2.0 as stated, and proceed to the rule 5 request;
2. take legal advice first (the slice waits);
3. reject the model and take option (d) (stop; correct INV-4's stale clause only).

The owner's answer is recorded in an approval record before the rule 5 request is made. Answering it is not the rule 5 approval.

## Alternatives considered

- **Reuse the pinned reranker (`cross-encoder/ms-marco-MiniLM-L6-v2`) as judge:** a relevance-ranking objective with no native "answers" boundary, so a threshold would be fitted on 20 seen unanswerable questions; it would move the open MS MARCO licence question onto the default path; re-opening the reranker is out of the slice's scope; it would still need rule 5 (new use) and a rule 4 change to INV-5.
- **Extractive QA with a no-answer head:** its native output selects a fragment of the passage, which INV-4 forbids a model to do.
- **NLI entailment:** needs the question rewritten as a hypothesis.
- **The same model's int8 ONNX file** (`model_qint8_arm64.onnx`, reported 110,780,504 bytes, or the other quantized/optimised variants in the repo): a quarter of the size and probably faster, but a different artefact with different scores. The 0.5 boundary was argued for the fp32 model only; the int8 file would need its own rule 5 request and its own pre-registered seen-set check. Rejected; latency of the fp32 file is measured in implementation.
- **Ship the best similarity threshold (t=0.67):** 13/20 and 37/56 on the seen sets; running the gate would spend the fifth set to confirm a predicted failure.
- **Stop:** keeps the fifth set unspent; no abstention; drafting stays blocked.

## Consequences

- **Easier:** abstention exists on the default path; its decision boundary is the model's, not a value fitted to a few questions.
- **Harder:** a third pinned model and a second default-path download (adversarial Security review; INV-5 changes from two models to three); every existing install must re-run `ingest` before `retrieve` works; `file-rerank-v1` mode holds three ONNX sessions (the exit-134 abort of ADR 0006 is unexplained); added latency per question (to be measured).
- **Unknown until measured:** the model was trained on single sentences, our passages are sections up to 512 tokens. Whether the judge meets the bars is measured once on the seen sets at the fixed boundary (pre-registered: pooled Bar 1 >= 16/20 and Bar 2 >= 45/56, or stop and ask) and once on the fifth set. Nothing in this record claims it works.
