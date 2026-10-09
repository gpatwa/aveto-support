# ADR 0007: Abstention by a local answerability judge (`abstain-judge-v1`)

> Architecture Decision Record. Owned by the Architect. Never edited after it is accepted. A changed decision gets a new record that supersedes this one.

- **Status:** **draft — facts not yet verified.** The fact table below has open slots. It must be completed from `runs/docs-abstention/02b-model-verification.md` before the owner is asked for the rule 5 approval of the model. It becomes **proposed** when the table is complete, and **accepted** when the owner approves the model (rule 5) and the INV-4 and INV-5 wording (rule 4), and slice `docs-abstention` passes its Release Gate. If the slice stops (option d) or the model is rejected, this record is marked **rejected** with the reason and kept.
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

## Model facts (to be completed before the rule 5 request; every slot is unverified until filled with a source URL)

| Fact | Value | Source (URL @ revision) | Criterion (tech spec 3.2) met? |
|---|---|---|---|
| Model ID | leading candidate `cross-encoder/qnli-electra-base` (named from memory; unverified) | — | — |
| Revision (40-hex) | — | — | 4 |
| Licence (model card) | — | — | 5 |
| Training data and their licences | believed QNLI (from SQuAD v1.1, believed CC BY-SA 4.0); unverified | — | 5 |
| Output head and `id2label` | — | — | 2 |
| `vocab.txt` WordPiece, uncased; sha256; size | — | — | 3, 4 |
| ONNX inputs (`input_ids`, `attention_mask`, `token_type_ids`), 512 positions | — | — | 3 |
| `onnx/model.onnx` present upstream at the revision; sha256; size | — | — | 4, 6 |
| Custom code / `trust_remote_code` needed | — | — | 4 |

## Alternatives considered

- **Reuse the pinned reranker (`cross-encoder/ms-marco-MiniLM-L6-v2`) as judge:** a relevance-ranking objective with no native "answers" boundary, so a threshold would be fitted on 20 seen unanswerable questions; it would move the open MS MARCO licence question onto the default path; re-opening the reranker is out of the slice's scope; it would still need rule 5 (new use) and a rule 4 change to INV-5.
- **Extractive QA with a no-answer head:** its native output selects a fragment of the passage, which INV-4 forbids a model to do.
- **NLI entailment:** needs the question rewritten as a hypothesis.
- **Ship the best similarity threshold (t=0.67):** 13/20 and 37/56 on the seen sets; running the gate would spend the fifth set to confirm a predicted failure.
- **Stop:** keeps the fifth set unspent; no abstention; drafting stays blocked.

## Consequences

- **Easier:** abstention exists on the default path; its decision boundary is the model's, not a value fitted to a few questions.
- **Harder:** a third pinned model and a second default-path download (adversarial Security review; INV-5 changes from two models to three); every existing install must re-run `ingest` before `retrieve` works; `file-rerank-v1` mode holds three ONNX sessions (the exit-134 abort of ADR 0006 is unexplained); added latency per question (to be measured).
- **Unknown until measured:** the model was trained on single sentences, our passages are sections up to 512 tokens. Whether the judge meets the bars is measured once on the seen sets at the fixed boundary (pre-registered: pooled Bar 1 >= 16/20 and Bar 2 >= 45/56, or stop and ask) and once on the fifth set. Nothing in this record claims it works.
