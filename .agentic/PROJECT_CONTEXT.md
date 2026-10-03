# Project Context — Aveto Support

> **Written by the owner, not by a Market Researcher or PM stage.** This is a
> greenfield repo whose first slice takes the short path, which skips the roles
> that normally own this file — so the owner states it directly. Drafted by
> Claude from the 2026-09-26 conversation and confirmed by the owner the same
> day.

## What this is

A **production-ready, deployable support agent**, built so others can take it
and run it for their own product: point it at your documentation and your
GitHub repositories, and it drafts grounded replies to your issues and
Discussions. **It never posts on its own** — a person approves every reply
before it goes out. **Aveto is its first deployment**, answering questions
about Aveto from Aveto's own docs.

## Why it exists

It is **Aveto's reference app** and a template others can deploy: proof that
the pipeline builds real, production-ready software, not a 700-line demo.
It is built in public, with every slice's intent, specs, QA evidence, security findings and approvals committed under `runs/`. The bar
it has to clear is written down in T22 of the playbook's `docs/BACKLOG.md`:
a normal stack, a public deploy, a real model in a shipped feature, and evals
as a merge check.

## Who it serves

- **People evaluating or using Aveto** who ask a question on GitHub and should
  get a correct, sourced answer quickly.
- **The owner**, who currently answers every question by hand and approves
  every draft.
- **Teams adopting the template** for their own product, who need to deploy it
  from the repo alone — its docs are part of the product.

## The stance

**Grounded or silent.** Every claim in a reply must trace to a passage in
the configured documentation, and the reply shows where. When the docs do not answer the
question, the agent says so and escalates rather than producing the least-bad
answer. A draft that cannot be backed by sources is worse than no draft.

## How it works (as designed)

1. **Classify** the question — plain rules first, a model only for what rules
   cannot place.
2. **Retrieve** the relevant passages — a local embedding model ranks files and
   passages (`file-rrf-v1`, the default), plus an optional local cross-encoder
   reranker that is off by default. No generative model is involved.
3. **Draft** a grounded reply — model role 1, as a **bounded tool-using
   loop**: it may search the docs again, read the full issue thread, or look up
   related issues, under a hard cap on turns and spend.
4. **Check** the draft against its sources — model role 2, a separate, cheaper
   model that did not write the draft.
5. **A person approves** before anything is posted.

Deterministic first, per `project-packs/ai-agent-product.md`: each model step
sits behind an adapter and ships only after its plain-code path works.

## Applicable project pack

`project-packs/ai-agent-product.md` — deterministic-first, LLM as adapter,
never invent user-facing claims, audit every automated action, eval suites
required.

## Stage

The first slice (`docs-retrieval`) built the retrieval step (ingest,
provenance, a deterministic index, and a local embedding model fused with
keyword search) but did not pass its held-out gate (answerable 5 of 17, bar
14), so nothing shipped. It is closed; the code stays on the branch.

The second slice (`docs-retrieval-2`, in progress) keeps that machinery and
changes the method: a fixed user-documentation corpus and file-level ranking,
gated on a fresh held-out set. `retrieve` returns its top 5 files and its top
score; deciding "the docs don't answer this" moves to the future check step.

No generative model is used anywhere. One small local embedding model
(BAAI/bge-small-en-v1.5, ONNX, approved by the owner) only helps rank passages.

## Decisions already made (by the owner, 2026-09-26)

- **Runtime model calls** use the owner's own API key at low volume, behind a
  hard monthly spend cap and a rate limit set before the key is first used.
- **Deploy target** is Azure, through the Cloud Deployment role.
- **Credentials** — the API key and the Azure login — are supplied by the owner
  and never handled by an agent.
- **Wiring a real model** is Tier 3 and fires approval rule 5; it happens only
  after the plain-code path ships.
- **Stack:** Python + FastAPI, calling Anthropic's SDK directly — no agent
  framework. Recorded as the first ADR.
- **Production-ready means the checklist in T22** — `azd` deploy with dev and
  prod, Key Vault, a GitHub App, observability, evals as a merge check, a
  threat model for prompt injection from issue text, and docs for someone who
  was not there.

## Out of scope for now

- Posting anything without a person's approval — ever, not just for now.
- Answering from anything other than the configured documentation — no
  general knowledge, no web search, no guessing from the model's training.
- Model-judged evaluation (e.g. RAGAS) — revisited deliberately at the
  drafting slice.
