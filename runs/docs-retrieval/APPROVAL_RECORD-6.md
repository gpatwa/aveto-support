# Approval Record 6 — full reference-embedding comparison (one-off, outside the project)

- **Request:** raised by the Orchestrator in the driving session; part of the ESCALATION-2 resolution (A). Rule 5 territory: installs and a download beyond Approvals 2–5.
- **Decision:** APPROVED
- **Approver:** Gopal Patwa (owner; answered in the driving session)
- **When (UTC):** 2026-09-29T16:14:41Z
- **Owner's response, verbatim** (prompted with three options): "Full reference: sentence-transformers + PyTorch"

## Facts checked by the Orchestrator before proceeding (read-only lookups, nothing downloaded)

The owner was told the Orchestrator would verify sizes first and ask again if they looked large. They did not:
- Resolved plan (uv dry-run in a throwaway venv, macOS arm64, Python 3.12): 40 packages, incl. sentence-transformers==6.1.0, torch==2.14.0, transformers==5.17.0, tokenizers==0.23.2, scipy==1.18.1, scikit-learn==1.9.1, numpy==2.5.3, safetensors==0.8.0, huggingface-hub==1.33.0.
- **Total wheel size 197 MB** (PyPI metadata; torch 127.3 MB the largest).
- Model files at revision 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a (HF metadata API): model.safetensors 133,466,304 bytes, sha256 3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad; and small files config.json 743, tokenizer_config.json 366, special_tokens_map.json 125, modules.json 349, sentence_bert_config.json 52, 1_Pooling/config.json 190 bytes. vocab.txt is already local and hash-checked. Roughly **330 MB** to download in total; disk is ample.

## Scope approved — nothing wider

QA may, in a **throwaway environment outside the repo** (never added to pyproject.toml or uv.lock): install the pinned packages above from PyPI; download **model.safetensors** and the six small files listed, from huggingface.co at the pinned revision (redirects only to hosts under hf.co), verifying model.safetensors' sha256 before use; load the model **offline** (HF_HUB_OFFLINE=1) from a local directory; compare a handful of embeddings with the product's, and write the result. **No pytorch_model.bin, no pickle, no trust_remote_code, no other file or host, no credentials, no eval run, no product code change.** If anything else is needed, QA stops and the owner is asked again.

## Interpretation to confirm

The owner named the packages and `model.safetensors`. The Orchestrator read "full reference" as also covering the six tiny config files sentence-transformers reads from the same repo at the same revision (1.8 KB together). If the owner does not want them, say so; QA has not started.
