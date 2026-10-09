# Support replies — docs-abstention

> Writer: the support/playbook session ("Aveto AI SDLC"). One writer per file. Nothing here is an approval; the owner decides at the rule 4 and rule 5 requests. Facts below were read on 2026-10-09 from public Hugging Face metadata and small text files only. **No weights were downloaded** and no eval set was read.

## Reply 1 — model verification for ADR 0007 (answers tech spec 3.4; content for `02b-model-verification.md`)

Read-only, from `https://huggingface.co/api/models/cross-encoder/qnli-electra-base?blobs=true` and the files at the revision below. Raw copies are in the support session's scratchpad (`hf-qnli.json`, `qnli-*`). I applied tech spec 3.2 and recommend nothing beyond criterion 7.

### Candidate: `cross-encoder/qnli-electra-base`

| Fact | Value | Source (URL @ revision) | Criterion (3.2) |
|---|---|---|---|
| Repo exists today | yes, public, not gated, not private | `https://huggingface.co/api/models/cross-encoder/qnli-electra-base` | 4 |
| Revision (40-hex) | `c7dea87c98b2269a935686c31336e97e837cbbeb` (last modified 2025-04-11) | same API, field `sha` | **4 met** |
| Licence (model card) | `apache-2.0` | `README.md` front matter @ `c7dea87c…` | **5 met (model)** |
| Base model | `google/electra-base-discriminator`, licence `apache-2.0` (revision `1ae76a97c7e84a4e640876a07453fccd636f0667`) | HF API for that repo | 5 |
| Training data | GLUE QNLI, "which transformed the SQuAD dataset into an NLI task" | `README.md` @ `c7dea87c…` ("Training Data") | 1, 5 |
| Training-data licence | SQuAD: **CC BY-SA 4.0** (stated on the SQuAD site and on `rajpurkar/squad`'s dataset card). GLUE's own dataset card says `other`. | `https://rajpurkar.github.io/SQuAD-explorer/`; HF API `datasets/rajpurkar/squad`, `datasets/nyu-mll/glue` | **5: see "Open question for the owner"** |
| Task | "Given a question and paragraph, can the question be answered by the paragraph?" Sequence classifier `ElectraForSequenceClassification`, pipeline tag `text-ranking` | `README.md`, `config.json` | **1 met** |
| Output head | **one logit**. `id2label` = `{"0": "LABEL_0"}` (a single label). The card's own usage applies `sigmoid(logits)`. So p = sigmoid(logit); no positive-label index is needed | `config.json` @ `c7dea87c…`; `README.md` usage | **2 met** (one-logit form) |
| Tokenizer | `ElectraTokenizer`, `do_lower_case: true`, `vocab_size 30522`, `type_vocab_size 2`, `max_position_embeddings 512` | `config.json`, `tokenizer_config.json` @ `c7dea87c…` | 3 |
| `vocab.txt` | 231,508 bytes, 30,522 lines, **sha256 `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`** | file at the revision; hash computed here | **3 met** |
| **vocab equals the embedding model's vocab** | the sha256 above is **identical** to the pin already in `docs-source.toml` (`vocab_sha256` for `BAAI/bge-small-en-v1.5`), so the existing `aveto_support.embed.WordPiece` handles it with no new tokenizer code | `docs-source.toml` `[embedding]` | 3 |
| `onnx/model.onnx` upstream | present at the revision: **438,212,375 bytes**, LFS sha256 **`595b37541289472b7b784ed2af05bcad6000991a2657aeee4f92f68b42ae61d9`** | API `siblings`, `lfs.sha256` @ `c7dea87c…` | **4 met** |
| ONNX input names | **NOT VERIFIED.** The graph's inputs can only be read by loading the file, which the spec forbids this step to download. Expected `input_ids`, `attention_mask`, `token_type_ids` (ELECTRA takes segment ids and `type_vocab_size` is 2). The implementation's load check must assert `embed.INPUT_NAMES` exactly and fail closed otherwise | — | **3: open until A4's load check** |
| Custom code | none: no `*.py` file in the repo; standard `ElectraForSequenceClassification`. No `trust_remote_code` needed | API `siblings` | **4 met** |
| Size (criterion 6) | 438,212,375 bytes ≈ 418 MiB, at the "about 450 MB" limit but within it. For comparison the current embedding model is about 34 MB int8 | API | **6 met, narrowly** |
| Other files present | `model_O1/O2/O3.onnx` (≈438 MB), `model_O4.onnx` (219,012,097 B, mixed precision), `model_qint8_arm64.onnx` and `model_qint8_avx512*.onnx` (**the same file**, 110,780,504 B, sha256 `7e9ab1c954aa56d216a3c749b6b9d55b17ac9001b0d7f71241e186fe681dfe36`), `model_quint8_avx2.onnx` (110,780,501 B, sha256 `06b08fd2c1eaca66567ce68a9086f40e8784f5bc77de113ac90aa89e24f0ea16`) | API `siblings` | see note A |
| Model's own accuracy on QNLI dev | 0.9321 after the last epoch (single-sentence QNLI pairs) | `CEBinaryAccuracyEvaluator_qnli-dev_results.csv` @ `c7dea87c…` | information only |

**Result against 3.2:** passes criteria 1, 2, 4, 6 and the model-licence half of 5, and passes the vocabulary half of 3; two items are open. (i) The ONNX input names are unverified (above). (ii) The training-data licence is share-alike (CC BY-SA 4.0) and is a question for the owner. Criterion 7 does not arise: no other candidate was needed, and I did not search for others.

### Notes for the Architect

- **A. Which ONNX file.** The spec names `onnx/model.onnx` (fp32, 438 MB). Upstream also ships a dynamically quantized int8 file at 110 MB (`model_qint8_arm64.onnx`, byte-identical to `model_qint8_avx512*.onnx`). Using it would be a different artefact with different scores, which the 0.5 boundary, fixed on general grounds, was not argued for; it would need its own pre-registered seen-set check. I suggest the ADR names the fp32 file and records the int8 file only as a rejected alternative, with latency to be measured in A4. That is the Architect's decision, not mine.
- **B. Domain shift** is the spec's own known risk: the model was trained on a question and one sentence, and the card gives no result on section-length passages. Nothing above changes that.
- **C. Revision drift.** The revision is today's head. Pin the 40-hex value above, not a branch name.

### Open question for the owner (not mine to resolve)

SQuAD's text is CC BY-SA 4.0 (share-alike), QNLI is a derivative of it, and this model is trained on QNLI. The model card itself states Apache-2.0. Whether share-alike obligations reach the trained weights is a legal question that I cannot settle, and it is the same kind of question as the reranker's MS MARCO terms (ADR 0005/0006), which stayed open for opt-in only. Here the model would be on the **default** path, so the criterion-5 wording ("never left open on the default path") applies: it should be put to the owner in ADR 0007 before the rule 5 request, with the options "accept the model card's Apache-2.0 as stated", "take legal advice first", or "reject and take option (d)".

### What I did not do

No weights, no `onnx/model.onnx` and no file over 1 MB was downloaded. No eval set was read. I did not search for a second candidate. I did not touch product code, STATE.md or any file other than this one.
