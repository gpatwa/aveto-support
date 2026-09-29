# ADR 0001: Python 3.12 with uv, FastAPI for HTTP, Anthropic's SDK called directly, no agent framework

> Architecture Decision Record. Owned by the Architect. Never edited after it is
> accepted. A changed decision gets a new ADR that supersedes this one.

- **Status:** accepted
- **Date:** 2026-09-28. The owner made the decision on 2026-09-26, and it is
  recorded here by the Architect.
- **Slice:** `runs/docs-retrieval/` (docs-retrieval-core). The tech spec is
  `runs/docs-retrieval/02-tech-spec.md`.

## Context

Aveto Support is a support agent that others will deploy for their own docs. Its
pipeline is classify, retrieve, draft, check, then a person approves. The last two
model steps sit behind adapters, and each ships only after its plain-code path
works (`.agentic/PROJECT_CONTEXT.md`, `project-packs/ai-agent-product.md`). The
owner fixed the stack before the first slice (PROJECT_CONTEXT, "Decisions already
made"). The first slice's intent needs the stack exercised for language,
structure and tests only, with no model call:

- Done-means 1: "A clean checkout installs, type-checks and passes its tests with
  the commands recorded in `.agentic/LOCAL_COMMANDS.md`."
- Constraints: "Python + FastAPI, calling Anthropic's SDK directly, with no agent
  framework… pytest for tests. As few dependencies as possible. **uv** manages the
  Python environment, with its lockfile committed… Python 3.12."

This record makes the decision findable in the product repo, and it states
exactly what each part means in practice, so later slices apply it the same way.

## Decision

1. **Language: Python 3.12.** `requires-python = ">=3.12,<3.13"`.
2. **Environment and dependencies: uv, with `uv.lock` committed.** CI and a clean
   checkout install with `uv sync --locked`, which fails if the lockfile is stale.
   Dev tools (pytest, mypy, ruff) go in a `dev` dependency group. Every new
   dependency, runtime or dev, is justified in the slice's tech spec, covering
   what it adds and what it costs.
3. **Tests: pytest. Type-check: mypy `--strict`. Lint: ruff.**
4. **HTTP: FastAPI, added by the first slice that needs an HTTP surface** (the
   GitHub App webhook, or an API for the approval UI), not before. Slice 1 is a
   CLI (`python -m aveto_support ingest | retrieve | eval`) with **zero runtime
   dependencies**. When FastAPI arrives, routes stay thin and call the same
   service functions the CLI calls (`search.retrieve()`), so the HTTP layer has
   no retrieval or safety logic of its own.
5. **Models: Anthropic's Python SDK, called directly from adapter classes.** Each
   model step (classify fallback, draft, check) sits behind a small Python
   `Protocol`. It has a deterministic implementation where one exists, and a
   placeholder that raises `"<capability> LLM adapter is not configured in this
   build."` by default. Wiring the real SDK is Tier 3 and needs approval under
   rule 5. The drafter's "bounded tool-using loop" is written in plain Python
   against the SDK's tool-use API, with an explicit turn cap and spend cap in our
   code.
6. **No agent framework.** No LangChain, LangGraph, LlamaIndex, CrewAI, AutoGen,
   Pydantic AI, DSPy, or any equivalent, for orchestration, retrieval or prompting.

## Alternatives considered

- **TypeScript/Node.** This is the playbook's native language, and its worked
  examples are TypeScript. It lost because the owner chose Python. The eval
  ecosystem the drafting slice will revisit (RAGAS and similar) is Python.
  Anthropic's Python SDK is first-class. The intent notes that RAGAS being Python
  removes a language objection. Cost: the pack's TypeScript examples need
  translating (the adapter pattern maps directly onto `typing.Protocol`).
- **An agent framework (LangChain / LlamaIndex / LangGraph / Pydantic AI).** It
  lost because the product's core promises have to be **explicit, inspectable
  code**: grounded or silent, a hard cap on turns and spend, a separate checker
  model, and a person approving before anything is posted. Frameworks put
  prompts, retry loops and retrieval behind abstractions that are harder to
  audit. They also bring large, fast-moving dependency trees, and they would
  make "as few dependencies as possible" impossible from day one. Retrieval in
  slice 1 is about 150 lines of plain BM25. Cost: we write our own tool loop and
  adapter plumbing, perhaps a few hundred lines, and we own its bugs.
- **Flask or Django instead of FastAPI.** Django brings an ORM, an admin and
  templating that a webhook-and-API service does not need. Flask lacks typed
  request and response models. FastAPI's Pydantic models and OpenAPI output suit
  a typed, mypy-strict codebase. FastAPI is also familiar, which is a reason and
  is stated as one.
- **pip + pip-tools, or Poetry, instead of uv.** uv gives a cross-platform
  lockfile, manages the Python interpreter, and is fast in CI, all in one tool.
  pip-tools needs a separate interpreter manager. Poetry is slower, and its lock
  format is less common in CI. Cost: uv is younger, and its lock format is
  uv-specific.
- **pyright instead of mypy.** pyright needs Node on the machine. mypy is
  pure Python and installs through uv. Cost: mypy is slower, and a few inference
  cases differ.
- **Adding FastAPI in slice 1 anyway ("scaffold the stack now").** That would add
  a dependency tree and a listening network surface for Security to review, with
  no Done-means item that uses it. It lost to "as few dependencies as possible".

## Consequences

- **Easier:** a clean checkout installs the same versions everywhere. Slice 1 has
  no runtime dependency to audit. Safety-critical logic (abstention, caps,
  approval) is plain code that tests can reach directly. Swapping model vendors
  later means changing the adapter, not the pipeline.
- **Harder:** we own the orchestration code a framework would have supplied, the
  tool loop, retries and tracing included. Framework-native integrations (vector
  stores, eval tooling) are not "free". Each one is a dependency decision with
  its cost written down.
- **Packaging is deferred.** Slice 1 runs with `[tool.uv] package = false` and a
  flat `aveto_support/` package, so it needs no build backend. The deploy slice
  (Azure) may need a built package or container image. Adding a build backend
  then is a small, recorded change, not a reversal of this ADR.
- **Revisit if:** a framework offers something we would otherwise build and that
  cannot be audited in our own code; the Python/Anthropic SDK combination blocks
  a required capability; or a later slice needs an HTTP stack FastAPI does not fit
  (for example a pure queue worker). Any of these gets a new ADR that supersedes
  this one.
