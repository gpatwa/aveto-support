# Aveto Support

> **Status: retrieval, plus an attended judge step, landing by pull request
> (branch `claude/land-answerability`); the owner merges. Not announced, not
> deployed.** It lists the docs files for a question and generates no answers.
> `retrieve` itself never abstains: a question the docs do not answer still
> returns files. The judge step is a separate, optional step that the operator
> runs by hand in their own Claude Code session; it can replace the files with
> `no confident match`. Release tier 3 (the owner's ruling, `APPROVAL_RECORD-9`
> of slice `docs-answerability-2`). **Known limit:** on the fifth question set,
> retrieval put the right file in the top five for 19 of 24 answerable
> questions (79.2%, under its 80% bar), and 16 of 24 ended with the right file
> shown after judging. The judge bars describe the eval path; the operator path
> is unmeasured. Details and limits are in
> [Status](#status) below. The default ranking (`file-rrf-v1`) scored 14/16 on
> an earlier held-out set; an optional reranker is off by default and showed no
> demonstrated gain. The record of each attempt, including what failed and
> why, is under
> [`runs/docs-answerability-2/`](runs/docs-answerability-2/09-release-checklist.md),
> [`runs/docs-retrieval-2-proof/`](runs/docs-retrieval-2-proof/02-close-out.md)
> and [`runs/docs-retrieval/`](runs/docs-retrieval/08-close-out.md).

A support agent for [Aveto](https://aveto.dev) — built **by Aveto, in public**.

It is designed to answer questions about Aveto from Aveto's own documentation
and to draft replies to GitHub issues and Discussions. Today only the retrieval
step and the attended judge step exist (see Status); nothing is drafted or
answered. **It never posts on its own:** every reply is approved by a person
first.

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

`retrieve` prints verbatim passages from the top five files, each with path,
heading, line range and permalink, plus the top score. It never abstains (a
question the docs do not answer still returns files) and never writes an
answer. Exit codes are
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
  calls, and the program never sends a question or passage text anywhere. The
  one exception is outside the program: the optional judge step, when you run
  it in your own Claude Code session (see Status and
  [INV-5](.agentic/SAFETY_INVARIANTS.md)). `retrieve`
  and `eval` re-check the cached files' hashes each time and tell you to run
  `ingest` if they are missing.
- **Your own model pin.** The `[embedding]` table in `docs-source.toml` names the
  model, its full 40-character revision, and a sha256 for `onnx/model.onnx` and
  `vocab.txt`. The model must be a BERT-style WordPiece encoder with a 384-dimension CLS
  output, as this one is. Changing the pin is a new download; get it approved.
- **Calibration list.** `offtopic_path` and `offtopic_sha256` name a fixed list of
  fluent questions the docs do not answer, used to compute a reference
  similarity that `ingest` prints for information. It decides nothing:
  retrieval does not abstain.

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

### The judge step (landing by pull request from `claude/land-answerability`)

A separate step decides whether the files `retrieve` would show answer the
question. `judge-input` (offline) prints the question and those passages;
you pass them to a `claude-sonnet-5-5` subagent with `/aveto-judge <question>`
in your own Claude Code session; `judge-apply` (offline) reads its reply and
prints either `retrieve`'s output or `no confident match`. A reply it cannot
use is `judge error` (exit 4), never passages. Commands and exit codes:
`.agentic/LOCAL_COMMANDS.md`. The reasoning: [ADR 0008](docs/adr/0008-operator-run-answerability-judge.md),
which stays Proposed.

**Limits, stated plainly**

- **Operator-run, attended only.** It runs in your own Claude Code session on
  your subscription. It is not unattended, not scheduled, not a service, and
  uses no API key and no `claude -p`.
- **The program stays offline.** It makes no network call and calls no model.
  What the judge step sends (the question, the shown passages, the reply and
  the session context the harness attaches) goes to Anthropic through your
  session, as [INV-5](.agentic/SAFETY_INVARIANTS.md) states.
- **One model, one set, a small sample.** `claude-sonnet-5-5`; one held-out
  set scored once (24 answerable and 24 unanswerable questions); 48 judge
  spawns at each of the two stages.
- **The judge adds a failure mode: over-abstaining.** It said
  `NOT_ANSWERABLE` on 3 of 19 answerable questions whose right file `retrieve`
  had in the top five (4 of 28 in the seen-set sample).
- **It does not repair retrieval.** On the fifth set the retrieval gate exits 1:
  retrieval put the right file in the top five for 19 of 24 answerable
  questions (79.2%, under its 80% bar; not a registered bar of the judge
  slice). End to end, 16 of 24 answerable questions end with the right file
  shown after judging. The owner accepted this as a known limit.
- **The bars describe the eval path; the operator path is unmeasured.** The
  figures below come from the eval path (a fixed payload per run id).
  `/aveto-judge`, where your session retypes the payload, has never been
  measured. Nothing here claims the product answers questions.
- **Operating rule: public-docs questions only until a DPA is in place.** The
  judge step runs on a personal subscription with no DPA. Retention and training
  use follow that plan's public terms, which no agent verified. The repo cannot
  enforce this rule; it is the operator's.

**Recorded figures** (each scored once; judge errors counted as failures)

| Measure | Stage 5, seen-set sample | Stage 7, fifth set (held out) |
|---|---|---|
| Bar 1: abstain on unanswerable | 20/20 (needed 16/20) | 24/24 (needed 20/24) |
| Bar 2: not abstain on answerable, right file in top 5 | 24/28 (needed 23/28) | 16/19 = 84.2% (needed 80%) |
| Judge errors | 0 | 0 |
| Never abstain (what `retrieve` alone does) | not printed | Bar 1 0/24, Bar 2 19/19 |
| Best-score rule (`top1 < 0.67`), same set | Bar 1 13/20, Bar 2 17/28: not met | Bar 1 10/24, Bar 2 13/19: not met |

Both judge bars were met. **Bar 2 passed by one question at both stages**
(22 of 28 and 15 of 19 would have failed). The best-score rule, the cheap
alternative, failed both bars at both stages. Tool-use audit clean: 0 tools
offered, 0 tool calls, 48 spawns each stage. Fifth-set source files overlap
earlier sets' (21 of 24 answerable questions cite at least one such file; no
question repeats), which may flatter Bar 2.

**Release tier and landing.** The release tier is 3 (the owner's ruling,
`APPROVAL_RECORD-9` of slice `docs-answerability-2`, 2026-10-16). Slice
`docs-answerability-2` closed as an internal release candidate; its conditions
T1 to T11 are carried out by slice `land-answerability`, whose Charter the owner
approved on 2026-10-17 (`runs/land-answerability/APPROVAL_RECORD-1.md`).
**Landing by pull request; the owner merges.** Nothing is announced or deployed.
What that slice's Charter recorded or changed:

- **S5 is fixed.** `/aveto-judge-seen` (eval only) no longer takes caller text
  in its shell line. To use it, write the run id to `.aveto-judge/seen-id`, then
  run `/aveto-judge-seen` with no argument. `/aveto-judge` is unchanged.
- **The S6 rule was deleted** (the owner said so on 2026-10-16).
- **Monitoring is adopted as written:** the thresholds, cadence and stop rules
  of `runs/docs-answerability-2/11-monitoring-plan.md`, with the standing
  mitigation "stop typing `/aveto-judge`, use `retrieve` alone". The runbook is
  [`docs/runbooks/answerability-judge.md`](docs/runbooks/answerability-judge.md).
- **Rollback was rehearsed** on a throwaway branch: `git revert -m 1` restored a
  tree identical to `main` and the regression passed on it
  (`runs/land-answerability/02-rollback-rehearsal.md`).
- **Vendor terms:** personal subscription, no DPA in place. The operating rule
  above is adopted; other vendor fields remain UNKNOWN
  (`runs/docs-answerability-2/11b-vendor-risk.md`).
- **Retrieval limit accepted and stated** (the known limit above).

The dry run on a fixture (11 of 11 criteria; no model ran in it) and the audit
coverage check (pass with gaps G1 to G9) are in
`runs/docs-answerability-2/`. The tier 3 gate record is
`runs/docs-answerability-2/13-release-checklist-tier3.md`; this slice's records
are under `runs/land-answerability/`.
