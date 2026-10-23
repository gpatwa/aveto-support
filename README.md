# Aveto Support

> **Status: retrieval, plus an attended judge step, merged to `main` by pull
> request #4 (2026-10-17). Not announced; the attended path is not deployed
> (the public service below is separate).** It lists the docs files for a question and generates no answers.
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

> **Public service (slice `public-ask-the-docs`): deployed on Azure Container
> Apps and answering; gate scored once.** A small web service, `aveto_service`,
> is built on this branch and deployed. It is separate from the attended
> `/aveto-judge` path described above, which remains attended and internal. On a
> pre-registered 20-question gate it scored Bar 1 10/10 and Bar 2 8/10, exactly at
> the bar: the margin is zero, the set is small, and 2 of the 10 answerable
> questions got no answer. That is a measurement, not a capability claim. Figures
> and caveats: [Public service](#public-service-ask-the-docs) below. This branch
> is not merged.

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

## Public service (Ask the Docs)

**Status: deployed on Azure Container Apps (East US 2) and answering; scored once
on a pre-registered gate.** The code, the container recipe (`Dockerfile`) and the
Azure infrastructure file (`infra/main.bicep`) are in this repo. The address is
recorded in the [runbook](docs/runbooks/public-ask.md); it is not linked from
aveto.dev, and that link is a separate later change on the owner's word. The
release decision is the Release Manager's and is not made here.

**What it is.** A visitor asks a question about Aveto and gets either the
**verbatim documentation passages** that answer it, each with its file, heading,
line range and a link to the pinned commit, or **`no confident match`** (the page
says "The docs don't answer this") with a link to open a GitHub issue. The model
decides only whether the shown passages answer the question. **It generates no
text:** every word shown is copied from the docs. A reply the service cannot use
shows `judge error` and no passage.

**How it differs from the attended path.** Both exist. `/aveto-judge` (above)
still runs only in your own Claude Code session, by hand, and is still attended
and internal. The service is a separate package (`aveto_service`, not
`python -m aveto_support`) that runs the same retrieval, the same judge prompt
(`answerability-judge-v1`, checked by hash at startup) and the same verdict-only
parser, but calls the Anthropic Messages API from a server with
`claude-sonnet-5-5` and no tools. One difference in what is shown: on a match the
service returns each passage's full text (what the judge read) and no scores,
where `judge-apply` prints `retrieve`'s three-line excerpts and scores.
`retrieve`, `eval`, `judge-input` and `judge-apply` are unchanged and still make
no network call.

**Routes.** `GET /` (the page), `POST /ask` (JSON `{"question": "..."}` or the
page's form), `GET /health` (counters and the kill-switch state).

**Limits** (enforced by the service; each refusal happens before any model call):

- 10 questions per visitor per hour. The visitor is identified by a hash of the
  address, kept in memory only. Questions that reach the model count, including
  ones that end in `judge error`.
- 500 characters per question.
- A daily share of $10 a month ($10 / 31 a day, reset at 00:00 UTC). When it is
  used up the page says "Paused for today" and no model is called.
- A kill switch (`ASK_KILL_SWITCH`): anything other than exactly `off` means on.
  Changing it creates a new revision of the app.
- The owner's $10-a-month limit in the Anthropic console is the backstop. The
  service's counters are held in memory and **restart when the replica restarts**
  (scale to zero, a kill-switch change, a redeploy), so the daily share holds per
  replica lifetime, not per day. The console limit is what holds the month. Its
  existence rests on the owner's statement; no agent has verified it.

**What is sent to whom.** Anthropic receives the question and the passages shown,
with a fixed prompt, the owner's API key and the SDK's own headers (they describe
the service's runtime: SDK version, operating system, CPU architecture, Python
version, timeouts); no visitor address, identifier or request header. The exact
list and wording are in [INV-5](.agentic/SAFETY_INVARIANTS.md), which names two
exceptions to "the program sends nothing anywhere": the operator's own Claude Code
session on the attended path, and this service. Microsoft Azure hosts the service (Container Apps, in the
owner's subscription) and keeps the platform logs. **No question is stored or
logged.** The service logs one line per request holding a time, the first 16
characters of a hashed address and an outcome code, and a few fixed operational
codes, kept 7 days (the retention setting was applied and read back as 7 and 7
for both tables). Anthropic's own retention is under its terms and
has not been verified by any agent.

**Run it locally.** The service needs the `ingest` output (`index/` and
`models/`) and reads the key from `ANTHROPIC_API_KEY`.

```sh
uv sync --locked
uv run python -m aveto_support ingest                        # builds index/ and models/ (the server needs them; the tests below use a fake embedder)
uv run pytest tests/test_service_pipeline.py tests/test_service_limits.py \
  tests/test_service_logging.py tests/test_service_api.py tests/test_anthropic_judge.py \
  tests/test_service_pages.py                                # the service tests, all with a fake judge, offline
```

Those tests are the way to exercise the service with a fake judge: they use
`FakeJudgeClient` from `tests/service_fakes.py`. **There is no committed command
that starts a server with a fake judge.** The server entry point is
`aveto_service.main:app` (the `Dockerfile` starts it with `uvicorn`); with no
`ANTHROPIC_API_KEY` set it uses a placeholder judge and every question that
reaches it ends in `judge error`, and the kill switch defaults to on until
`ASK_KILL_SWITCH=off`. Deployment and operations: the runbook
[`docs/runbooks/public-ask.md`](docs/runbooks/public-ask.md).

**Recorded figures (stage 18, scored once through the deployed service).** Gate
`evals/public-gate-1.toml` (sha256 `7eb4f588…064f`), 20 questions: 10 the docs
answer, 6 they do not, 4 hostile. Revision `ca-aveto-ask--0000006`, kill switch
off, real limits.

| Measure | Result |
|---|---|
| Bar 1: all 10 unanswerable and hostile questions get `no confident match`, no passage, no judge error | 10 of 10, met |
| Bar 2: at least 8 of 10 answerable questions show a passage from a listed source | 8 of 10, met exactly at the bar |
| Judge errors in 20 calls | 0 |
| Cost per judged question | about $0.0078 per question at Anthropic's published prices for `claude-sonnet-5-5` ($2 and $10 per million tokens; $0.1569 for the 20 gate questions, $0.1569 / 20, recomputed from the recorded 71,151 input and 1,460 output tokens, checked 2026-10-23). The first live question cost $0.0099. The service's own counter defaults to the same $2 and $10 (2000 and 10000 nano-dollars per token) from the code of pull request "fix-service-accounting"; that change is **not deployed yet**, and the live revision measured here (`ca-aveto-ask--0000006`) still counts at its earlier defaults. To be confirmed by the live smoke after the redeploy. |
| Response time, from one client (a Mac, to East US 2), n = 20 | median 1.66 s, slowest 5.09 s |
| Cold start, from zero replicas after more than an hour idle | 30.8 s to the first `/health` answer |
| Monthly Azure cost | **not measured** (Azure's cost data lags about a day) |

Read these plainly:

- **The margin on Bar 2 is zero.** One more miss would have failed it. With 10
  questions the result cannot separate "meets 80%" from "somewhat below it".
- **Over-abstention is 2 of 10 answerable questions** (p06 and p09): the judge
  said not answerable, so the service showed `no confident match` for questions
  the docs answer. It fails toward silence, as designed.
- The set is small and its answerable sources overlap earlier sets' files, so
  Bar 2 may read slightly optimistic. "Right passages" means the service showed a
  passage from a listed source; other files shown with it were not judged.
- Not covered: real visitors, adversarial load, invisible-character injection
  (S-A5), IPv6 clients (the service has no AAAA record), a screen reader, a
  different judge model or prompt.
- The service's counters restart with the replica, so the Anthropic console limit
  is the only durable cap. The $0.0078 is recomputed from recorded tokens at
  Anthropic's published prices, not read from Anthropic's bill. About 1,270
  questions a month fit inside the $10 limit at that price (estimate).
- **How the service counts spend (fix-service-accounting; not deployed yet).**
  The two price settings (`ASK_PRICE_IN_NANO_PER_TOKEN` and
  `ASK_PRICE_OUT_NANO_PER_TOKEN`) default to 2000 and 10000 nano-dollars per
  token, that is $2 and $10 per million tokens, read 2026-10-23 from Anthropic's
  pricing page and matched by the owner's console bill; the settings still
  override the defaults. Retries are reserved: a question is admitted only if
  room for two attempts is free, and the unused part is returned when it
  settles. Each attempt is charged on its own outcome (usage at the price if it
  returned a usable response, nothing if it failed as a 4xx or a connection
  error, one full reservation for any other failure), so a later attempt never
  changes what an earlier one is charged. This closes issues #6, #7 and #8 when
  the pull request is merged. **Daily pause, an estimate:** about 33 questions a
  day by the service's counter with two attempts reserved (assumes about
  $0.030 reserved per attempt for a request of about 10,000 bytes; the request
  size is not measured). By spend alone about 41 fit in the day's $10 / 31
  share, but the design pauses earlier, so the 41 first expected is not what it
  gives. To be confirmed by the live smoke after the redeploy.
- An Azure budget alert (`bud-aveto-ask`, $20 a month, resource group
  `rg-aveto-ask`) emails the Owner role at 50%, 80% and 100% of actual cost and
  100% of forecast. It only notifies; it does not stop or cap spending.

## Status

Retrieval (`ingest`, `retrieve`, `eval`) is built as a command line tool: hybrid
lexical and local-embedding ranking, with no generative model and nothing that
posts to GitHub. The eval bar is scored once, on a held-out question set, after
the method is frozen; see `.agentic/CURRENT_MVP_STATUS.md`.

### The judge step (merged in pull request #4; attended, internal use)

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
**Merged by pull request #4 on 2026-10-17 (a merge commit, which keeps the rehearsed rollback valid).** For the attended judge step, nothing is announced or deployed and nothing runs on a server (the public service above is a separate path).
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

## License

Licensed under the [Apache License, Version 2.0](LICENSE). See [NOTICE](NOTICE) for the copyright holder, the trademark note and, where relevant, third-party components.
