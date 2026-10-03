# Aveto Support

> **Status: retrieval only; Security Review and Release Gate pending; not announced.** It lists
> the docs files for a question and generates no answers. The default ranking
> (`file-rrf-v1`) scored 14/16 on the latest held-out set (earlier sets 11/16
> and 12/17); an optional reranker is off by default and showed no
> demonstrated gain. Nothing here is released. The record of
> each attempt, including what failed and why, is under
> [`runs/docs-retrieval-2-proof/`](runs/docs-retrieval-2-proof/02-close-out.md)
> and [`runs/docs-retrieval/`](runs/docs-retrieval/08-close-out.md).

A support agent for [Aveto](https://aveto.dev) — built **by Aveto, in public**.

It answers questions about Aveto from Aveto's own documentation and drafts
replies to GitHub issues and Discussions. **It never posts on its own:** every
reply is approved by a person first.

## Why this repo exists

This is Aveto's reference app. Its job is to show the pipeline building real
software — a real stack, a real deploy, a real model in a shipped feature —
where anyone can read how it was built. Every slice's intent, specs, QA
evidence, security findings and approvals are committed under `runs/`.

The plan, and the bar it has to clear, is T22 in the playbook's
[backlog](https://github.com/gpatwa/agentic-sdlc-playbook/blob/main/docs/BACKLOG.md).

## How it works (as designed)

1. **Classify** the question — plain rules first, a model only when they can't.
2. **Retrieve** the relevant docs — keyword search plus a small local embedding model; no generative model.
3. **Draft** a grounded reply — model one.
4. **Check** the draft against its sources — a separate, cheaper model that did
   not write it. Unsupported claims are removed or the question is escalated.
5. **A person approves** before anything is posted.

## Run it

Needs [uv](https://docs.astral.sh/uv/). Python 3.12 is selected or downloaded by uv.

```sh
uv sync --locked                               # install
uv run mypy && uv run ruff check && uv run pytest   # checks (offline)
uv run python -m aveto_support ingest          # fetch the pinned docs and model, build index/docs-index.json
uv run python -m aveto_support retrieve "how do I install it"
uv run python -m aveto_support eval            # score against evals/retrieval.toml
```

`retrieve` prints verbatim passages with their path, heading, line range and a
permalink, or `no confident match`. It never writes an answer. Exit codes are
listed in `.agentic/LOCAL_COMMANDS.md`.

### The local model

Retrieval uses one small embedding model, `BAAI/bge-small-en-v1.5`, run locally
on CPU with `onnxruntime`. It only helps find and rank passages by meaning; it
never generates or changes text.

- **Download, once.** The first `ingest` downloads two files (about 133 MB) from
  huggingface.co into `models/` (gitignored). Each file must match the sha256
  pinned in `docs-source.toml` before it is used; a mismatch deletes the file
  and fails the run. Nothing else is downloaded.
- **Offline afterwards.** `retrieve`, `eval` and the default tests make no network
  calls, and no question or passage text ever leaves your machine. `retrieve`
  and `eval` re-check the cached files' hashes each time and tell you to run
  `ingest` if they are missing.
- **Your own model pin.** The `[embedding]` table in `docs-source.toml` names the
  model, its full 40-character revision, and a sha256 for `onnx/model.onnx` and
  `vocab.txt`. The model must be a BERT-style WordPiece encoder with a 384-dimension CLS
  output, as this one is. Changing the pin is a new download; get it approved.
- **Calibration list.** `offtopic_path` and `offtopic_sha256` name a fixed list of
  fluent questions the docs do not answer, used to calibrate "no confident
  match". Without one, `ingest` warns that abstention is calibrated on word
  salads only and is likely too permissive.

## Point it at your own docs

1. Edit `docs-source.toml`: set `repo` to a public GitHub `owner/name` and `commit`
   to a **full 40-character SHA** (branches, tags and short SHAs are rejected).
   Optionally list path prefixes to skip in `exclude`, and point `offtopic_path`
   at your own list of off-topic questions (or remove it).
2. Run `ingest` again, then `retrieve`.

This repo's approvals to use the network cover only the values committed in
`docs-source.toml`: the docs of `gpatwa/agentic-sdlc-playbook` at its pinned
commit, and the pinned model files. Pointing the file at another repo or model is
a new approval for this repo; on your own fork, it is your decision.
`evals/retrieval.toml` is written for the committed source and will refuse to run
against an index of a different commit.

## Status

Retrieval (`ingest`, `retrieve`, `eval`) is built as a command line tool: hybrid
lexical and local-embedding ranking, with no generative model and nothing that
posts to GitHub. The eval bar is scored once, on a held-out question set, after
the method is frozen; see `.agentic/CURRENT_MVP_STATUS.md`.
