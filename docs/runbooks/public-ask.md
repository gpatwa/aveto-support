# Runbook: the public Ask the Docs service

> **Status of this runbook.** The service is built. It has not been deployed, and
> nothing below has been run against Azure by this slice's authors except the
> read-only checks recorded in `runs/public-ask-the-docs/11c-infra-checks.md`.
> Commands marked "not run" are written from the design and the tech spec and
> have never been executed. Every figure for cost, response time and cold start
> is **not yet measured (stage 18)**.
>
> **Where this comes from.** Tech spec `runs/public-ask-the-docs/05-tech-spec.md`
> (sections 3, 4, 5, 7) and the Security review
> `runs/public-ask-the-docs/14-security-review.md`. Under Charter C8.3 the
> deploy and rollback commands are run by the Orchestrator's session, not by a
> person typing them from this page, unless the owner says otherwise. The
> attended judge step has its own runbook:
> [`answerability-judge.md`](answerability-judge.md).

## What the service is, in one paragraph

`aveto_service` (FastAPI, one process) wraps `retrieve` and the answerability
judge. `POST /ask` returns verbatim docs passages or `no confident match`;
`GET /health` returns counters; `GET /` is the public page. It runs on Azure
Container Apps in resource group `rg-aveto-ask` (eastus2), scale 0 to 1
replica. The model call goes to the Anthropic Messages API with
`claude-sonnet-5-5`; the key lives in Key Vault `kv-aveto-ask-gp`
(secret `anthropic-api-key`). No visitor question is stored. What the request
carries, including the SDK's own headers, is stated in
[INV-5](../../.agentic/SAFETY_INVARIANTS.md).

## 1. Deploy (commands 1 to 5, exactly as in tech spec section 7)

Run from the **worktree root of the slice branch**, never from the main
checkout (Security S-C3: the main checkout holds a symlink to the worktree that
`az acr build` could upload). Never run a command that prints a secret value
(`az containerapp secret list --show-values`, `az keyvault secret show`,
`az monitor log-analytics workspace get-shared-keys`).

```sh
RG=rg-aveto-ask; F=infra/main.bicep; P=infra/main.parameters.json; TAG=$(git rev-parse --short=12 HEAD)
# 1. identity, registry, workspace, environment, role assignments (no app yet)
az deployment group create -g $RG -f $F -p @$P -p deployApp=false
# 2. build and push the image from the branch (remote build; runs ingest inside)
az acr build -r acravetoaskgp -t aveto-ask:$TAG --platform linux/amd64 -f Dockerfile .
# 3. the app, kill switch ON
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=on
# 4. once ContainerAppConsoleLogs_CL and ContainerAppSystemLogs_CL exist: 7-day retention
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=on configureLogRetention=true
# 5. after the off-state, health, header and XFF checks: turn it on
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=off configureLogRetention=true
```

Notes that apply to these commands:

- Command 5 is the step that makes the service answer visitors. Do not run it
  until section 9 (the pre-switch-on checklist) is complete.
- The image is unbuilt as of this writing. Whether `ingest` runs inside
  `az acr build` and what its last line (`wrote index/docs-index.json  sha256 <hex>`)
  prints are checked at stage 17; keep the build log.
- The Bicep compiled only after fixes F1 to F3 of `11c-infra-checks.md` were
  applied; a clean `what-if` of the final file is a stage 17 item.
- `killSwitch` defaults to `on`: a deploy that forgets the parameter comes up
  off.

## 2. Rollback

Each rollback is one command from the same list. No portal step.

- **Kill switch on** (the first move for any doubt): command 5 with
  `killSwitch=on`.
- **Previous version:** command 5 with `imageTag=<previous tag>`. The tag is the
  commit, tags are never overwritten, so the previous image stays in the
  registry. With `activeRevisionsMode: 'Single'` this starts a revision of the
  previous image.
- Before command 3 nothing is public. A failed command 1 or 2 is re-run; there
  is nothing to undo.

## 3. The kill switch

The kill switch is the Container App environment variable `ASK_KILL_SWITCH`,
set from the Bicep parameter `killSwitch` (`on` or `off`, default `on`).

- **Turn off the service (switch on):** command 5 with `killSwitch=on`.
- **Turn the service back on (switch off):** command 5 with `killSwitch=off`.
- Any value other than exactly `off` (missing, empty, misspelt, or any other
  setting the service cannot parse) means the kill switch is **on**.
- **It makes a new revision.** Changing the variable creates a new Container
  Apps revision and replaces the replica. There is no image build and no code
  change; the image digest is the same. It is not "without a new revision":
  the owner was told this in the tech spec (section 4). How long the
  replacement takes is not yet measured (stage 17).
- **Because the replica is replaced, the in-memory counters restart at zero**
  (see section 5).
- With the switch on: `GET /` loads and says "The service is off";
  `POST /ask` answers `service_off` before reading the body; `GET /health`
  reports `"kill_switch":"on"`. No retrieval and no model call happen.

## 4. Checking `GET /health`

`GET /health` returns 200 JSON with `Cache-Control: no-store`. It never calls a
model and writes no log line. It is public. Fields:

| Field | Meaning |
|---|---|
| `status` | `"ok"` when the process is up and the index, model files and prompt hash loaded. If startup fails the process exits and `/health` does not answer. |
| `kill_switch` | `"on"` or `"off"`, as read at startup. |
| `day` | The current UTC date, `YYYY-MM-DD`. |
| `judged_today` | Questions that reached the model since this replica started on this UTC day. |
| `input_tokens_today`, `output_tokens_today` | Tokens the API reported for those calls. Stage 18 reads cost per question from the change in these across a batch. |
| `spend_today_usd` | The service's own running total for the day, six decimals. It is the service's count, not Anthropic's bill. |
| `daily_cap_usd` | The day's share of the monthly cap: $10 / 31 = `0.322580`. |

All counters are **per replica lifetime**: when the replica stops (scale to
zero after idle, a kill-switch change, a redeploy, a crash) the next replica
starts at zero. A `judged_today` of 0 after a quiet period is normal.

The container's readiness and liveness probes call `/health`. Do not make
`/health` slower or heavier.

## 5. The daily share and the UTC reset

- The service allows a day's share of the monthly cap, `10 / 31` dollars
  (`322,580,645` nano-dollars; the longest month, so 31 days never exceed $10).
- It reserves the worst-case cost of a question before calling the model and
  settles to the reported usage afterwards. A failed 5xx or timed-out call keeps
  the full reservation; a 4xx or connection failure is charged nothing.
- When the room left is too small for the next reservation, the service answers
  "Paused for today" and calls no model.
- **The day resets at 00:00:00 UTC.** A closed day reopens then. The public page
  does not state a reset time, so this is the only place the zone is written.
- **The counters are per replica lifetime, not per day.** After the replica is
  replaced (idle scale-down, kill-switch toggle, redeploy, restart) the spend
  and the 10-an-hour counts start again from zero. The month's money limit holds
  only because of the Anthropic console limit (section 8). This is Security
  finding CR-3 / owner decision D1.
- Also in memory: at most 10 judged questions per visitor key per hour, and at
  most 30 retrievals per visitor key per hour (every request that reaches
  retrieval, admitted or not). The visitor key is an HMAC of the address with a
  per-process random salt; it is never logged in full.

## 6. Retention of the abuse log: the 7-day read-back

The service writes one line per `POST /ask` to stdout, exactly
`{"t":"<UTC time>","ip":"<16 hex>","o":"<outcome code>"}`, plus fixed ops lines
(`startup_ok`, `startup_failed` with a fixed category, `unhandled`). Container
Apps sends them to the Log Analytics workspace `log-aveto-ask`, tables
`ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL`. The question never
appears in a line.

Retention is 7 days only after deploy command 4 (`configureLogRetention=true`).
Until then the workspace default of 30 days applies. **Read it back, read-only,
for each table:**

```sh
az monitor log-analytics workspace table show -g rg-aveto-ask --workspace-name log-aveto-ask -n ContainerAppConsoleLogs_CL --query "{r:retentionInDays,t:totalRetentionInDays}"
az monitor log-analytics workspace table show -g rg-aveto-ask --workspace-name log-aveto-ask -n ContainerAppSystemLogs_CL --query "{r:retentionInDays,t:totalRetentionInDays}"
```

Pass: both print `7` and `7`. Anything else: leave the kill switch on and tell
the owner. (Whether table retention can go below 30 days is unconfirmed; the
first run of command 4 settles it.) The workspace also has a daily ingestion cap
of 0.5 GB; a flood of refused requests can reach it, after which that day's
further abuse lines are dropped (Security S-A10, accepted as a cost guard).

## 7. When the page shows "Paused for today", or "We couldn't decide this time"

**"Paused for today"** (`paused`, HTTP 503) means the day's reservation room is
used up on this replica. It is not a fault. Check `GET /health`:

- `spend_today_usd` close to `daily_cap_usd` and `judged_today` plausible:
  the day's share is spent. It reopens at 00:00 UTC. Nothing to do.
- The page shows the same copy for a short-lived shortfall while slow calls are
  in flight, and during an Anthropic outage (failed 5xx calls keep their
  reservation, so about three failed questions can pause the day). The page
  text "has been used" is not accurate in those two cases (Security S-A3,
  recorded, not fixed).
- A rise in `paused` lines in the abuse log from a handful of `ip` values is the
  intended fail-closed behaviour of a small daily share: about 40 questions from
  a few addresses pause the service for everyone until 00:00 UTC (decision D4).

**"We couldn't decide this time"** (`judge_error`, HTTP 502) covers an
unusable reply and any call failure: timeout, 4xx, 5xx, a stop reason other
than `end_turn`, a tool-use block, or a missing key. The service logs no
category for it. Steps, in order:

1. `GET /health`: is the service up, and is `kill_switch` what you expect?
2. Every question fails the same way right after a deploy: suspect the
   Anthropic request itself (for example, the `effort` field not accepted for
   the model, or the key missing so the placeholder judge is in use). This was
   to be caught at the stage 17 first call, before any gate question.
3. Every question fails after weeks of working: the Anthropic console limit
   ($10 a month) may have been reached. Calls then fail with a 4xx, are charged
   nothing, and visitors see "We couldn't decide this time" until the console's
   period resets. Check the console (owner action).
4. If in doubt, turn the kill switch on (section 3).

**An outage** (the page does not load, or `/health` does not answer):

1. Kill switch on does not help a down platform; check the Container App in the
   portal or `az containerapp show -g rg-aveto-ask -n ca-aveto-ask --query properties.runningStatus` (not run).
2. A replica that exits at startup logs one ops line, `startup_failed`, with
   category `prompt_hash`, `index` or `model`, and `/health` never answers.
   The container restarts. A new deploy of a corrected image (command 5 with the
   fixed `imageTag`) or a rollback (section 2) is the fix.
3. After any outage, write the review with `templates/INCIDENT_REVIEW_TEMPLATE.md`
   in the playbook.

## 8. The Anthropic console limit (an owner action)

The money cap of $10 a month is set by the **owner** in the Anthropic console,
on the account that issued the key. No agent sees the key, creates the account
or sets the limit. The service's own daily counter is a second control, not the
cap: because it resets with the replica, the console limit is what keeps the
month at $10. Whether the console limit is a hard stop, and its period, rests on
the owner's statement and has not been verified by any agent (owner decision D7).
Azure charges are separate and not under that $10 (decision D5); an Azure
budget alert is the owner's choice.

## 9. Pre-switch-on checklist (Security conditions S-C1 to S-C3)

Do these **with the kill switch on**, in order, before command 5 with
`killSwitch=off`. Record each result in the stage 17 artefact.

- **S-C1: the client address behind the ingress.** Within one replica lifetime
  (send a request at least every 4 minutes so the replica does not scale down,
  because the hash salt is per process). Each `POST /ask` then writes a
  `service_off` abuse line keyed by the resolved address, with no retrieval and
  no model call.
  1. From machine A, send `POST /ask` with: no `X-Forwarded-For`;
     `X-Forwarded-For: 203.0.113.1`; `203.0.113.2`; `203.0.113.1, 198.51.100.7`;
     two `X-Forwarded-For` header lines; `garbage`; `203.0.113.9:443`; and with
     `Forwarded: for=203.0.113.3`, `X-Real-IP: 203.0.113.4`,
     `X-Envoy-External-Address: 203.0.113.5`. **All must log the same 16-hex
     `ip`.**
  2. From machine B on a different public network (for example a phone
     hotspot), one `POST /ask`. **Its `ip` must differ from A's.**
  3. Query `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL` for A's
     and B's raw public addresses: **0 hits.**
  - If step 1 fails: redeploy with `clientKey=peer` (add `clientKey=peer` to
    command 5's parameters) before the switch goes off, and repeat step 2.
  - If step 2 fails under either mode: every visitor shares one 10-an-hour
    bucket. Do not switch on silently; report it to the owner (decision D2).
- **S-C2: log retention.** The read-back in section 6 prints `7` and `7` for
  both tables. The switch stays on until it does.
- **S-C3: build from the worktree root only.** Record the build log's ingest
  hash line. Never print a secret value (see the list at the top of section 1).
- Also before switching on, as the spec requires: the off-state of the page and
  `POST /ask` checked, `GET /health` checked, security headers checked, and the
  table list in the workspace read for any table other than the two named
  (the ingress may write per-request records elsewhere; unconfirmed).

## 10. Removing the resources (only on the owner's word)

Nothing here is run by the slice. Run it only when the owner says so, in the
session driving the work. **Not run; written from the resource names in
`infra/main.bicep`.** Delete in this order because of dependencies:

```sh
az containerapp delete -g rg-aveto-ask -n ca-aveto-ask --yes
az containerapp env delete -g rg-aveto-ask -n cae-aveto-ask --yes
az monitor log-analytics workspace delete -g rg-aveto-ask -n log-aveto-ask --yes
az acr delete -g rg-aveto-ask -n acravetoaskgp --yes
az identity delete -g rg-aveto-ask -n id-aveto-ask
```

- The Key Vault `kv-aveto-ask-gp` is the owner's, created by the owner inside
  `rg-aveto-ask`, and referenced by the Bicep as `existing` (never created or
  deleted by it). Do not delete it with the rest. The role
  assignment `Key Vault Secrets User` granted to the identity on that vault is
  removed with `az role assignment delete` for that scope and identity; look it
  up first with `az role assignment list --scope <vault id>`.
- **Do not delete the resource group `rg-aveto-ask`.** It contains the owner's
  Key Vault and the secret `anthropic-api-key`. Delete the named resources one
  by one, as listed above.
- If the owner wants the key gone too, that is a separate owner command, not
  part of this removal. The Anthropic key and its console limit are likewise
  the owner's to revoke or remove.
- After removal, point readers away from the service URL (the link from
  aveto.dev is a separate change in the playbook repo) and update the README
  Status.
