# QA: product embeddings versus a reference implementation (docs-retrieval, embed-v3)

Depth standard, under APPROVAL_RECORD-6. HEAD ddf95f0. No eval was run, no recall figure computed, no product code touched.

## Verdict: MATCHES. The embedding code does not understate the method.
The product's float embeddings equal the reference's to about 1e-7. The only difference is the int8 quantisation the design chose. No divergence in tokenisation, prefix, pooling, normalisation or truncation was found.

## Environment and downloads (all outside the repo)
- Throwaway venv (Python 3.12.3, uv 0.9.7), scratchpad `.../scratchpad/ref/venv`, 870 MB on disk. Installed exactly as pinned: sentence-transformers 6.1.0, torch 2.14.0, transformers 5.17.0, tokenizers 0.23.2, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, safetensors 0.8.0, huggingface-hub 1.33.0. 41 packages (the Orchestrator's plan said 40; the extra is setuptools). No version drifted.
- Downloaded over HTTPS with curl from `huggingface.co/.../resolve/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/` (redirects went to huggingface.co and `*.hf.co` only): `model.safetensors` 133,466,304 B; `config.json` 743; `tokenizer_config.json` 366; `special_tokens_map.json` 125; `modules.json` 349; `sentence_bert_config.json` 52; `1_Pooling/config.json` 190. Every size equals the approved list. Total about 133.5 MB (the wheels, about 197 MB, are additional). No other file or host, no credentials, no pickle, no `trust_remote_code`.
- Hash checks: `model.safetensors` sha256 = `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`, equal to the pin, checked before loading. `vocab.txt` is the local cached copy, sha256 `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`, equal to the pin.
- Reference loaded with `HF_HUB_OFFLINE=1` from the local directory: `SentenceTransformer(local_dir)` = BertModel, CLS pooling, Normalize, max_seq_length 512. (`2_Normalize` has no files and needed none.)
- Nothing was added to the project: `git status` clean, `git diff pyproject.toml uv.lock` empty. No `uv sync` or `uv add`. Scripts `product.py` and `reference.py` and the vectors are in the scratchpad, not committed.

## What was compared
- Product side: `OnnxEmbedder.load` (read-only), the exact `passage_input` string for passages, `QUERY_PREFIX` plus question for queries. Float vectors came from the product's own tokenizer and ONNX session, L2-normalised. The product's int8 bytes came from `embed_passage` and `embed_query`, dequantised by `/127`. My float replica re-quantised to the product's exact bytes for all 20 strings, so the float path is faithful.
- Reference side: sentence-transformers on the same exact strings, batch size 1, normalisation on.
- 12 passages from the product's index: 3 truncated at 512 tokens (README.md:1, docs/PLATFORM_EVAL.md:48, prompts/ml-training.md:9; 546, 529 and 732 content-plus-special tokens before truncation) and 9 untruncated (34 to 303 tokens; one is non-English-heavy markdown). 8 synthetic queries I wrote, none from any evals/ file. The index's stored int8 bytes equal fresh product output for all 12.

## Numbers
| Group | float vs reference: cos min / mean, max abs diff | int8 (dequantised) vs reference: cos min / mean, max abs diff |
|-------|------|------|
| Passages (12) | 0.99999989 / 1.0000000, 2.5e-7 | 0.998923 / 0.999000, 0.003937 |
| of which truncated (3) | 1 - cos <= 1.1e-7, 2.5e-7 | 0.998923 / 0.999007, 0.003934 |
| Queries (8) | 0.99999999 / 1.0000000, 1.8e-7 | 0.998924 / 0.999020, 0.003936 |

- The int8 gap is exactly the quantisation step: max abs diff 0.003937 is half a step (0.5/127), and product int8 versus product float shows the same 0.003936.
- All 910 stored index vectors versus reference floats: cos min 0.998860, mean 0.999013. Re-quantising the reference floats with the product's formula reproduces the stored bytes in 99.9991% of elements (rows identical in 99.7%). The remainder are rounding ties, one step apart.
- Reference token counts equal the product's content count plus 2 for all 12 passages (truncated ones 512) and the 8 queries.

## Top-5 (product int8 query against product stored int8 passages, versus reference float over all 910)
- Top-1 agrees for 8 of 8. Top-5 as a set differs for **3 of 8** queries (order differs for 6 of 8). In each case exactly one passage swaps at the 5th or 6th place, and the reference scores of the swapped pair are within 0.0004 to 0.0111 of each other (for example 0.7417 versus 0.7404).
- Cause is quantisation, not a bug: ranking with the reference floats quantised by the product's formula gives the product's top-5 exactly, 8 of 8. Float against float, the vectors are equal to 1e-7, so ranking is identical to that precision.
- Max score difference over all query-passage pairs, product int8 versus reference float: 0.0137.

## Not checked
The embedding code was compared, not the retrieval fusion, calibration or threshold. Whether int8 near-ties matter for the held-out result is not something this comparison measures; it says only that the vectors are right. Strings were limited to 12 passages, 8 queries and the whole-index stored vectors.
