# Approval Request 3 — model weights download in ingest and CI (rule 5)

- **Slice:** docs-retrieval
- **Rule:** HUMAN_APPROVAL_RULES §5 — "Adding a network call to the build / test / commit path"
- **Requested:** 2026-09-29T05:25:45Z. Only meaningful if Request 2 is approved.

## What

`ingest` downloads two files, once per machine, and the CI workflow will do the same
(cached): `onnx/model.onnx` (133,093,490 bytes, sha256
`828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35`) and `vocab.txt`
(231,508 bytes, sha256 `07eced37…38a3`; **REPORTED, not yet verified** — the first
download checks it and a mismatch stops the work), about **133.3 MB** total, from
`https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/5c38ec7c…`. That URL answers
**302 to `us.aws.cdn.hf.co`** (verified), a host that can vary, so the rule allows
`huggingface.co` plus hosts under `hf.co`, HTTPS only, GET only, no credentials.
Every file is checked against its committed sha256 **before it is used**; on a
mismatch it is deleted and ingest fails. After that, `retrieve`, `eval` and the
default tests are offline.

No pickle and no `trust_remote_code`: the graph is protobuf and the vocab is plain
text. The PyTorch `.bin` files are never downloaded.

## Why

The model is unusable without its weights and vocabulary, and pinning a sha256 per
file is the integrity control (trust rests on the hash, not on the host).

## What is reversible if denied

Embed-v3 cannot run without the weights, so a denial drops embed-v3 and returns to
lexical v2. Nothing is downloaded, so nothing needs undoing. If approved and later
withdrawn: delete `models/` (gitignored) and revert the code.

## The smallest request

These two files at this revision, downloaded by `ingest` (and CI) only, from those
hosts only. Not a general licence to download anything else, and not the
amended safety wording (Request 4).

## Cost

About +2–6 minutes per CI run, no token or API cost. CI cost is measured by
`docs-retrieval-ci`.
