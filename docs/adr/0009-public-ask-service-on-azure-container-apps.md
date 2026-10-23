# ADR 0009: A public ask-the-docs service on Azure Container Apps, judging through the Anthropic API

> Architecture Decision Record. Owned by the Architect. Never edited after it is
> accepted. A changed decision gets a new ADR that supersedes this one.

- **Status:** proposed
- **Date:** 2026-10-21. The owner decided hosting, metered API and limits on 2026-10-20
  (`runs/public-ask-the-docs/intent.md`, Charter approved in `APPROVAL_RECORD-1.md`); the
  shape below is the Architect's.
- **Slice:** `runs/public-ask-the-docs/`. Tech spec: `runs/public-ask-the-docs/05-tech-spec.md`.

## Context

The retrieve-then-judge product (ADR 0008) passed its gates but runs only in the operator's
Claude Code session. The owner wants it public: a visitor's question gets either `retrieve`'s
verbatim passages (judge says ANSWERABLE) or `no confident match`, with no generated text
(INV-4), under a $10-a-month cap, hosted on Azure, scaling to zero. ADR 0001 fixed FastAPI
and the Anthropic SDK called directly; it did not decide hosting, the package boundary, or
how the judge runs unattended.

## Decision

1. **A separate package `aveto_service/`** (FastAPI) beside `aveto_support/`, which it imports
   and never changes. `python -m aveto_support` stays the offline program INV-5 describes; the
   service is the one component allowed API egress (Charter C5.2).
2. **The judge runs through the Anthropic Messages API** behind a `JudgeClient` Protocol with a
   placeholder that raises by default: `claude-sonnet-5-5`, effort `high` sent explicitly, no
   tools, the hash-pinned prompt `answerability-judge-v1` as the system prompt, `judge-input`'s
   payload as the only user message, the existing `parse_verdict`.
3. **Limits in the service, fail closed, before any model call:** kill switch, 500 characters,
   10 an hour per hashed IP, a daily spend share of $10/31 with per-question reservations. State
   is in memory, one replica.
4. **Azure Container Apps**, Consumption, `minReplicas 0`, `maxReplicas 1`, external HTTPS
   ingress; image built by `az acr build` with `ingest` run inside the build (the pinned docs
   and model, sha256-checked); key from Key Vault through a user-assigned identity; Log
   Analytics with 7-day table retention; Bicep in `infra/`.
5. **Kill switch = a Container App environment variable** set from a Bicep parameter (default
   on), applied by `az deployment group create`: no build, same image, a new revision.

## Alternatives considered

- **Service inside `aveto_support/`.** Lost: INV-5's "the program never sends a question"
  would need rewording beyond C5.2, and the import allow-list tests would have to change.
- **Copying the local `models/` and `index/` into the image.** Lost: both are gitignored, so
  the image would depend on unrecorded files on one laptop. Cost of the choice made: the
  build-time index may differ from the laptop's if int8 rounding differs on another CPU; the
  build log's index sha256 is compared and reported.
- **Durable counters (storage account or Log Analytics queries) or `minReplicas 1`.** Not in
  the Charter's resource list (C8.3), which also says scale to zero. Cost: counters reset when
  the replica stops; the owner's $10 console limit remains the monthly hard cap.
- **Kill switch in Key Vault or a Container Apps secret with a revision restart.** Lost: needs
  a vault write or `az rest` calls C8.3 does not name, and runtime Key Vault reads would add
  egress outside C5.2.
- **App Service or Azure Functions.** Not chosen: the owner named Container Apps (scale to
  zero, container image with the ONNX model inside).

## Consequences

- **Easier:** one judge caller (`POST /ask`); the offline program and its tests unchanged;
  rollback is one `az deployment group create` (previous image tag, or kill switch on).
- **Harder:** a public surface to defend (Security, adversarial); per-lifetime counters; cold
  starts of tens of seconds (unmeasured); the API price for `claude-sonnet-5-5` is unconfirmed
  in the repo and set as a parameter.
- **Revisit if:** traffic needs durable limits (add storage, a new ADR and Charter), the gate
  bars are missed, or a drafting step needs the same service surface.
