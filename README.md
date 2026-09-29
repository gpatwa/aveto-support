# Aveto Support

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
2. **Retrieve** the relevant docs — plain code.
3. **Draft** a grounded reply — model one.
4. **Check** the draft against its sources — a separate, cheaper model that did
   not write it. Unsupported claims are removed or the question is escalated.
5. **A person approves** before anything is posted.

## Run it

Needs [uv](https://docs.astral.sh/uv/). Python 3.12 is selected or downloaded by uv.

```sh
uv sync --locked                               # install
uv run mypy && uv run ruff check && uv run pytest   # checks (offline)
uv run python -m aveto_support ingest          # fetch the pinned docs, build index/docs-index.json
uv run python -m aveto_support retrieve "how do I install it"
uv run python -m aveto_support eval            # score against evals/retrieval.toml
```

`retrieve` prints verbatim passages with their path, heading, line range and a
permalink, or `no confident match`. It never writes an answer: nothing here calls
a model. Exit codes are listed in `.agentic/LOCAL_COMMANDS.md`.

## Point it at your own docs

1. Edit `docs-source.toml`: set `repo` to a public GitHub `owner/name` and `commit`
   to a **full 40-character SHA** (branches, tags and short SHAs are rejected).
   Optionally list path prefixes to skip in `exclude`.
2. Run `ingest` again, then `retrieve`.

This repo's approval to fetch from the network covers only the value committed in
`docs-source.toml` (`gpatwa/agentic-sdlc-playbook` at its pinned commit). Pointing
the file at another repo is a new approval for this repo; on your own fork, it is
your decision. `evals/retrieval.toml` is written for the committed source and will
refuse to run against an index of a different commit.

## Status

Retrieval (`ingest`, `retrieve`, `eval`) is built as a command line tool in plain
code. The eval bar (80% answerable, 80% unanswerable) is not yet met; see
`.agentic/CURRENT_MVP_STATUS.md`. No model is wired in and nothing posts to GitHub.
