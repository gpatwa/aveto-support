# Aveto Support

> **Status: retrieval, plus an attended judge step on branch
> `claude/docs-answerability-2`. Not released, not announced, not deployed.**
> It lists the docs files for a question and generates no answers.
> `retrieve` itself never abstains: a question the docs do not answer still
> returns files. The judge step is a separate, optional step that the operator
> runs by hand in their own Claude Code session; it can replace the files with
> `no confident match`. Release Gate verdict at tier 3 (ruled by the owner):
> **go with conditions** (an internal branch candidate, not announced, **not
> cleared to land**: no push, merge, deploy, PR, tag or announcement without the
> owner's own typed yes). Details and limits are in
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

### The judge step (branch `claude/docs-answerability-2`)

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
  19/24 = 79.2% of answerable questions had the right file in the top 5 (not a
  registered bar of this slice). End to end, 16 of 24 answerable questions end
  with the right file shown after judging.

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

**Release tier and verdict.** The owner ruled the release tier 3 on
2026-10-16. The tier 3 verdict is **go with conditions**: an internally
releasable branch candidate, not announced, and not cleared to land. Six tier 3
items are not met strictly, and the owner holds the conditions T1 to T11. The
main ones:

- The owner's approval of the release action is pending, and the change request
  is PENDING (approver named: Gopal Patwa).
- Anthropic's DPA, account terms, retention and training use are UNKNOWN; the
  owner has not stated them.
- The monitoring thresholds are proposals the owner has not set.
- The rollback has never been rehearsed.
- The retrieval gate result above (19/24 = 79.2% on the fifth set) is not
  accepted yet.
- S5 (quote breakout in the eval-only skill `/aveto-judge-seen`) is open; that
  skill is not to be used until it is fixed.
- S6 (a permissive local permission rule): the file is verified absent in this
  worktree; it was reported removed on the owner's word, and the owner has yet
  to confirm it.
- A final lint, type and test run on the exact commit to be merged has not been
  recorded.

Also new: a dry run on a fixture (11 of 11 criteria pass) and an audit coverage
check (pass with gaps G1 to G9). The model was not run in the dry run, and the
operator path `/aveto-judge` has never been measured. Records: the tier 3
verdict `runs/docs-answerability-2/13-release-checklist-tier3.md`, with
`11-monitoring-plan.md`, `11b-vendor-risk.md`, `11c-change-request.md` and
`12-tier3-dryrun-audit.md` beside it. Nothing here is announced or deployed,
and nothing authorises a push or merge.
