# Runbook: the public Ask the Docs service

> **Status of this runbook.** The service is deployed and answering at
> `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`
> (Azure Container Apps, East US 2). It is not linked from aveto.dev; that is a
> separate later change on the owner's word. Deploy commands 1 to 5 and the
> kill-switch change were run by the Orchestrator's session
> (`runs/public-ask-the-docs/17-deploy/`). Commands marked "not run" were written
> from the design and have never been executed. Measured: kill-switch change 65 s
> (on) and 66 s plus about 6 s (off), cold start 30.8 s, cost per question about
> $0.0078 at Anthropic's published prices, response median 1.66 s and slowest
> 5.09 s from one client (`18-gate/RESULT.md`). **Not measured:** the monthly
> Azure cost.
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
- `ingest` runs inside `az acr build`; the index sha256 it prints
  (`f36ef5d4…a756`) matched the local index at stage 17. Keep the build log.
- The Bicep compiled after fixes F1 to F3 of `11c-infra-checks.md`; `what-if`
  was run before each create at stage 17.
- `killSwitch` defaults to `on`: a deploy that forgets the parameter comes up
  off.
- **Pass `killSwitch` explicitly on every deploy**, as the commands above do
  (`killSwitch=on` or `killSwitch=off`); never rely on the default. The shell
  variables (`$RG`, `$F`, `$P`, `$TAG`) are for a person typing the commands;
  the Orchestrator's session runs the same commands with literal values (absolute
  paths, the 12-character commit as the tag) and without a price parameter:
  the price comes from the Bicep defaults (2000 and 10000), and
  `monthlyCapUsd` and `clientKey` are left at their defaults, which equal the
  live values.

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
  the owner was told this in the tech spec (section 4). Measured
  (`17-deploy/e3-rollback.txt`): **65 s** from command to a healthy switch-on
  revision; **66 s** to switch off, plus about 6 s for traffic to move to the new
  revision. Cold start from zero replicas after more than an hour idle: **30.8 s**
  to the first `/health` answer (the second call took 0.25 s).
- **Because the replica is replaced, the in-memory counters restart at zero**
  (see section 5). A revision change or scale to zero resets the spend, token
  and rate counters; the Anthropic console limit is the only durable cap.
- The rollback to the previous image was not rehearsed: the only other tag
  (`0fa04abda8ad`) is the build that crash-loops (F-LIVE-1, section 7).
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
| `input_tokens_today`, `output_tokens_today` | Tokens the API reported for those calls. Stage 18 read cost per question from the change in these across a batch: about $0.0078 per question at Anthropic's published prices. The service's own counter uses $2 and $10 by default from the fix-service-accounting change (deployed 2026-10-24, revision `ca-aveto-ask--0000008`; see section 8). The live smoke that day read $0.008544 per question (n = 5) and spend equal to the token cost at $2 and $10. |
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
  settles afterwards. **Retries are reserved:** the adapter makes at most two
  attempts per question, so admission reserves two full per-attempt
  reservations and settlement returns the unused part. **Each attempt is
  charged on its own outcome:** its reported usage at the configured price if it
  returned a usable response, nothing if it failed as a 4xx or a connection
  error (or was never sent), and one full per-attempt reservation for any other
  failure (5xx, timeout, bad stop reason); a later attempt's category never
  changes what an earlier attempt is charged. (This replaces the earlier rule,
  where the last error's category could erase an earlier attempt's cost. Not
  deployed yet; the live revision still follows the earlier rule until the
  redeploy.)
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
  in flight, and during an Anthropic outage (a question whose two attempts both
  fail with a 5xx is charged two reservations, so about five such questions can
  pause the day; estimate, assuming about $0.030 per attempt). The page
  text "has been used" is not accurate in those two cases (Security S-A3,
  recorded, not fixed).
- A rise in `paused` lines in the abuse log from a handful of `ip` values is the
  intended fail-closed behaviour of a small daily share: a few dozen questions
  from a few addresses pause the service for everyone until 00:00 UTC (decision
  D4, recorded as about 40; about 33 by the estimate in section 8 once the
  two-attempt reservation is deployed).

**"We couldn't decide this time"** (`judge_error`, HTTP 502) covers an
unusable reply and any call failure: timeout, 4xx, 5xx, a stop reason other
than `end_turn`, a tool-use block, or a missing key. The service logs no
category for it. Steps, in order:

1. `GET /health`: is the service up, and is `kill_switch` what you expect?
2. Every question fails the same way right after a deploy: suspect the
   Anthropic request or the key. **First-live-call lesson:** the first call
   after the first switch-on returned `judge error` in 0.43 s with nothing
   billed. The key had been stored in Key Vault with stray whitespace (the
   probable cause, not proven; the service logs no cause by design). The
   owner's direct API test with the same request shape returned 200, so the
   model id and `effort` field are accepted. The fix was to store the key again
   **with whitespace stripped**, then redeploy; the next call answered. Check the
   secret was stored that way before suspecting anything else.
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
   **F-LIVE-1 (seen at stage 17):** the first image crash-looped with
   `startup_failed` category `index`. `ingest` wrote the index and model files
   with mode 0600, and the runtime user (uid 10001) could not read them. The
   Dockerfile now sets `--chown=root:10001` and a `chmod` so uid 10001 can read
   the index and models (image `879cae23690b`). If `startup_failed` returns
   with category `index` or `model` on a new image, check that those files are
   readable by uid 10001 first.
3. After any outage, write the review with `templates/INCIDENT_REVIEW_TEMPLATE.md`
   in the playbook.

## 8. The Anthropic console limit (an owner action)

The money cap of $10 a month is set by the **owner** in the Anthropic console,
on the account that issued the key. No agent sees the key, creates the account
or sets the limit. The service's own daily counter is a second control, not the
cap: because it resets with the replica, the console limit is what keeps the
month at $10. Whether the console limit is a hard stop, and its period, rests on
the owner's statement and has not been verified by any agent (owner decision D7).
Azure charges are separate and not under that $10 (decision D5); see "Budget
alert" below.

### Cost and capacity

- Real cost (recorded): about $0.0078 per question ($0.1569 for the 20 gate
  questions, $0.1569 / 20; 71,151 input and 1,460 output tokens). The first live
  question cost $0.0099.
- About 1,270 questions a month fit inside the $10 console limit at that price
  (estimate).
- **Estimate, not measured:** the service's daily pause comes at about 33
  questions a day by its own counter with two attempts reserved (assumes about
  $0.030 reserved per attempt for a request of about 10,000 bytes; the request
  size is not measured). By spend alone about 41 questions fit in the day's
  share, but admission needs room for two attempts, so the pause comes earlier;
  41 is not what this design gives. The earlier 27 a day counted at the wrong
  price and is withdrawn. The 33 stays an estimate; the live smoke (2026-10-24,
  five questions) did not run to the pause.
- Live smoke, 2026-10-24, revision `ca-aveto-ask--0000008` (five questions from
  `evals/retrieval-heldout-5.toml`): g01, g03, g04 answered, byte-identical to
  `retrieve`; gu15, gu18 no confident match. Cost per judged question $0.008544
  (n = 5, from `/health` counters: 20,304 input and 211 output tokens), within
  15% of $0.0078. The counter's spend equals the token cost at $2/$10 exactly.
  No question text in any log table. Kill switch off took 71.4 s; the on toggle
  was not measured (watcher TLS error; about 73 s upper bound from deploy
  timestamps). Previous-revision rollback not rehearsed; the kill switch is the
  proven fallback.

### Pricing (confirmed 2026-10-23)

Confirmed from Anthropic's live pricing page and models overview:
`claude-sonnet-5-5` is $2 per million input tokens and $10 per million output
tokens (5-minute cache writes $2.50, 1-hour $4, cache reads $0.10, Batch API $1
and $5). There is no long-context surcharge. The id `claude-sonnet-5-5` is a
pinned snapshot (the dateless id is its own snapshot), with retirement not
sooner than 2027-09-28. The `effort` parameter defaults to `high` on this model.

The service's built-in defaults are `ASK_PRICE_IN_NANO_PER_TOKEN=2000` and
`ASK_PRICE_OUT_NANO_PER_TOKEN=10000` (nano-dollars per token; 1 nano-dollar per
token is $1 per million tokens, so $2 and $10), in `aveto_service/settings.py`
and `infra/main.bicep`, with the source and date (2026-10-23) in a comment next
to each. Setting `ASK_PRICE_*` still overrides them. The Bicep passes the price
to the container, so the deployed revision takes the values from the template
default. **Deployed 2026-10-24** as revision `ca-aveto-ask--0000008` (image
`aveto-ask:d067b9a95ac6`); defaults 2000/10000 are live, and the live smoke
confirmed the counter's spend equals the token cost at $2 and $10.

### Budget alert

Created 2026-10-23 on the owner's instruction:

- Budget `bud-aveto-ask`, scope resource group `rg-aveto-ask`, $20 per month
  (a figure chosen by the Orchestrator; adjustable), monthly from 2026-10-01 to
  2028-10-31.
- Notifications to the Owner role (one holder) at 50%, 80% and 100% of actual
  cost and at 100% of forecast cost.
- It only notifies. It does not stop or cap spending. Decision D5 is therefore
  partly answered: alert yes, cap no.
- It is not in `infra/main.bicep` (the Charter's resource list names no budget).
  It was created by hand with `az rest` PUT on `Microsoft.Consumption/budgets`
  (API 2023-05-01).
- Remove it with:
  `az rest --method delete --uri https://management.azure.com/subscriptions/<id>/resourceGroups/rg-aveto-ask/providers/Microsoft.Consumption/budgets/bud-aveto-ask?api-version=2023-05-01`
- A separate subscription budget, `compass-pilot-budget` ($100), belongs to the
  owner's other work and is untouched.

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

## 11. Processors and data

This is the processor record for the service, carried from
`runs/public-ask-the-docs/07-compliance-data.md` section 9 (the full review and
the line-by-line check are there). The approval it rests on is Charter v2 lines
C4.1 (Anthropic) and C4.2 (Azure) in `runs/public-ask-the-docs/CHARTER-v2.md`.
Anything marked **UNKNOWN** has not been established by anyone recorded; nothing
below fills it in.

| Field | Anthropic | Microsoft Azure |
|---|---|---|
| Purpose | Decide whether retrieved docs passages answer a visitor's question | Host the service; platform logs for 7 days |
| What it receives | Per question, in one request to `api.anthropic.com/v1/messages`: the question (at most 500 characters), the fixed judge prompt, the retrieved passages (path, heading, line range, text), the protocol fields (model, effort, `max_tokens`) and the SDK's own headers about the container. Never a visitor IP, visitor id, hashed key or visitor header. It also sees the Azure outbound address and the owner's API key identity; neither is visitor data. Exact list: [INV-5](../../.agentic/SAFETY_INVARIANTS.md) and C4.1 | The container image (code, pinned index and models, public docs text); the Key Vault secret; each visitor request in transit through ingress, which contains the visitor's raw IP and the question in the POST body; Log Analytics abuse lines (hashed IP, time, outcome) and ops lines |
| Channel | HTTPS, metered API, key from Key Vault `kv-aveto-ask-gp` | Container Apps, `rg-aveto-ask`, eastus2 |
| Terms | Commercial Terms, which incorporate the Data Processing Addendum by reference, per the owner's statement (2026-10-20). **DPA: in place by reference per the owner's statement; text unread; not verified. Not recorded as met.** | The owner's Azure subscription terms, unread by any agent. Whether that offer permits production hosting of a public service: **UNKNOWN** |
| Retention | **UNKNOWN** (no period stated by any artefact; training or improvement use of API inputs also **UNKNOWN**) | Abuse log lines: 7 days, for the two tables `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL`, once deploy command 4 is applied and read back (section 6). Other tables and platform records (ingress, metrics, activity log): **UNKNOWN** until the table list is read (section 9) |
| Residency and transfer | **UNKNOWN** (processing location not stated anywhere; no transfer basis recorded) | United States (eastus2); transfer basis for visitors outside it not recorded |
| Subprocessors | **UNKNOWN** | **UNKNOWN** |
| Approver | Gopal Patwa, Charter C4.1 | Gopal Patwa, Charter C4.2 |

Also **UNKNOWN**, from the same review: breach-notification and liability
terms, certifications and status page for either vendor; whether Anthropic's
terms and usage policy permit a public, unauthenticated use and require any
disclosure; whether a hashed IP is still personal data. These and the EU AI Act
Art. 50 reading (OI-1) are for the owner and legal, not decided here. No
named compliance approver exists yet; the owner is asked at the end review.

**What the visitor is told.** The page (`aveto_service/render.py`) says that an
AI model decides; that the question is sent to Anthropic, named, and handled
there under Anthropic's terms; not to enter personal or confidential
information; that the address is read to apply the limit and a scrambled form
is kept 7 days with the time and outcome; and that the service is hosted in the
United States (Azure East US 2). It is checked in the served HTML before the
switch goes off (stage 17, release condition S8). It does not say that nothing
is kept anywhere, because retention at Anthropic is UNKNOWN.

## 12. Monitoring

Nobody is on call and nothing pushes an alert. The owner acts. The signals,
thresholds and actions below are stated in
`runs/public-ask-the-docs/06-ai-risk-assessment.md` section 7, which is the
source; if the two differ, that section wins. No threshold here is new.

**What to look at.** The abuse log in Log Analytics (7 days; outcome codes `o`
as in section 6) and the `GET /health` counters (section 4; per replica
lifetime). No question text is kept, so correctness cannot be observed directly:
every rate is a screening rule on a small sample. The `judge_error` cause is
deliberately not logged (section 7).

**Cadence.** Daily for the first 3 days live; then at least every 5 days;
weekly after a quiet month.

| Signal | Threshold | Action |
|---|---|---|
| `judge_error` share of admitted calls (abuse log) | Over 5% in 50 calls, or 3 in a row | Check Anthropic status, console limit and key (section 7); kill switch on if unexplained |
| Input and output tokens per judged question (`/health` deltas) | Over 2x the stage 18 figure (about 3,557 input and 73 output tokens per question) | Prompt or model change suspected; kill switch on; re-run the canary |
| `answer` share of admitted calls | Moves more than 20 points from the stage 18 baseline (not yet recorded) over 100 or more calls | Run the canary; review |
| `paused` days | More than 2 in a week | Demand or abuse; the owner decides on the cap, not an agent |
| `rate_limited` on one `ip` hash | Any day above 30 | Abuse; kill switch on if cost is rising |
| Anthropic console spend, Azure bill, and the estimate | Any month over $10, or Azure over $10 | Stop and report |
| Canary: 6 questions from the spent gate set (3 answerable, 3 not), asked through the page by the owner or operator | Monthly, after any trigger above, and on any model notice; any not-answerable question shown means switch off | Kill switch on; a new pre-registered check before re-enable |
| Control integrity (zero tolerance) | A request with `tools`; a model other than `claude-sonnet-5-5`; a prompt-hash mismatch (the service refuses to start, `startup_failed` category `prompt_hash`); any shown text that differs from `retrieve` | Kill switch on |

**Who acts.** The repository owner. The Post-Launch Learning Agent reads the
stage 18 record and each review.

**Known gaps** (06 section 7): **M1** push alerting is outside Charter C8.3, so
detection depends on someone looking; the owner is to accept that in words at the
end review. **M2** a fixed `judge_error` category on an ops line is not added
(it would change the logging contract; for the Architect and Security).
**M3** stage 18 should compare live passages with local `retrieve`, byte for
byte, on a sample; not yet done. The two baselines marked "not yet recorded"
do not exist before stage 18, so those two rows cannot be applied until then.
