# Release Checklist — fix-service-accounting

> Owner: Release Manager Agent (stage 8, `claude-sonnet-5-5`, depth standard, 2026-10-23). Separate invocation from every author in this run.
> Tier: **3** (Charter C7.2). Risk tier of the code review, re-derived: **High** (see below).
> Source artefacts: `intent.md`, `CHARTER.md`, `APPROVAL_RECORD-1.md`, `00-slice-plan.md`, `01-scope.md`, `05-tech-spec.md`, `08-backend-note.md`, `03-failfirst-87178bd.txt`, `03-green.txt`, `code-review.md`, `13-qa-evidence.md`, `14-security-review.md`, `15-docs-note.md`, `charter-check-output.txt`, `events-verify-output.txt`, `EVENTS.jsonl`, `STATE.md`.
> I have no shell. Every result below is read from a saved output or from the Read/Grep of a file; where I read a file myself I say so. Nothing here is a re-run.

## Verdict for stage 9 (deploy): GO WITH CONDITIONS

No gate that can be met before the deploy has failed. The conditions in section "Pre-deploy conditions" (P1 to P5) are all things the Orchestrator does in its own session before the first gated command; none needs the owner. If P1 to P5 hold, stage 9 proceeds with no further decision. If any fails, C8.1 applies: no deploy, `ca-aveto-ask--0000006` keeps serving, close-out, stop.

Not failures, but to be carried into `END_REVIEW.md` (section "For END_REVIEW"): the rollback is not rehearsed, A1 and A2 are owner decisions, the budget is over plan.

## Tier classification rationale

Tier 3 per `docs/RELEASE_GATES.md`: the run builds an image and deploys a new revision of a public service that spends real money on a third-party API (Anthropic), and it changes how that spend is counted and capped. Charter C7.2 fixes tier 3 and it may not be lowered. The code-review tier, re-derived from the diff list (`08-backend-note.md` section 6 item 4, `13-qa-evidence.md`, `15-docs-note.md`): product paths `aveto_service/{pipeline,judge_port,anthropic_judge,settings}.py` and `infra/main.bicep` set the day's cap and reservation, the runtime model adapter's billing count and the price that drives the cap. `CODE_REVIEW.md` section 2 lists "a model or processor line" and settings under High, and the intent names High. **My tier: High; it equals the recorded one (code-review.md), so no change.** Human review at the end is therefore the owner reading the change itself, and "a rollback is rehearsed before it is offered" (see gap R-1).

Diff scope: 14 paths outside `runs/` by the QA and Docs records (4 `aveto_service`, `infra/main.bicep`, 5 tests, `docs/ARCHITECTURE.md`, README, runbook, `CURRENT_MVP_STATUS.md`), plus `runs/.../10-smoke/smoke.py`. The spec's expected list was 13; the 14th is `tests/test_service_api.py` (one price line, disclosed by the Backend, deviation 1, accepted by QA). I could not run `git diff --name-only`; this list is from the artefacts (unconfirmed by me against git).

## Charter and approvals (Process v2)

| Check | Evidence | Result |
|---|---|---|
| Approval record holds the human's verbatim approval of CHARTER.md by sha256 | `APPROVAL_RECORD-1.md`: approver Gopal Patwa, directly in the driving session; full sha256 `afc984d16f94...9aefe4` on the record; the quoted words abbreviate it as `afc984d1…aefe4` and name plan 730k, ceiling 950k, hard cap 1,200k | PASS. Note: the owner's own words abbreviate the hash; the full hash is on the record line. `verify-approvals.mjs` (GitHub check) is not something I can run; not evidenced here |
| `charter-check-output.txt` shows same sha256 and "charter complete" | prints `charter complete: runs/fix-service-accounting/CHARTER.md` and `sha256 afc984d16f941f514dcf9da5b4f7efbe530e554ea828fecaa0f3a039269aefe4`; identical to the record and to STATE.md | PASS |
| Every gated action cites a Charter line that names it exactly | STATE.md Approvals table has one row (the Charter, rules 3 and 5, deploy C8.3, push and PR C8.2, smoke C3.1). Mapped below | PASS |
| No C6.P allow rule in a tracked settings file | I read `.claude/settings.json` in the worktree: the `permissions` block holds only `deny` rules; no `allow`. QA verified the `.claude` tree id equals 87178bd's. The saved `git diff <base> -- .claude/settings.json` output is **not in the run folder** | PASS on my own read; saved output still wanted (P2) |
| Event log: chain intact, no write outside the allowed paths | `events-verify-output.txt`: `chain intact; 533 lines`; no write-outside-paths line. One alert: `seq 533: main attempted Bash cd #91ac... with no outcome recorded (denied, blocked or interrupted)` | PASS. The alert is reported, not blocking. The saved output ends at stage 7; events from stages 8 on are covered by a re-run at the end (P5) |
| `code-review.md`: every finding fixed or carried with a reason | 5 findings, 0 Important. CR-1, CR-2, CR-5 intentional with reasons; CR-3 routed to Docs (done, I grepped the three docs: the old `$3 and $15`, `50% high`, `$0.0079`, `$0.2354`, `3000/15000` are gone; the only `27 a day` hit is the runbook line saying the earlier 27 was wrong); CR-4 pre-existing, reported, out of scope. No unaddressed correctness finding | PASS. Review is `unscored` (C3.R), as the Charter says |
| Risk tier re-derived | High (above) | equals recorded |

Gated actions against Charter lines:

| Action | Rule | Charter line | Stage | Status |
|---|---|---|---|---|
| `az acr build -r acravetoaskgp` (one new image, worktree root) | 3 | C8.3 | 9 | NOT YET |
| `az deployment group create -g rg-aveto-ask` with `killSwitch=on` (new image, new revision) | 3 | C8.3 | 9 | NOT YET |
| `az deployment group create ...` with `killSwitch=off` (new revision, the smoke state) | 3 | C8.3 ("set the kill switch on, then off, through the same deployment command") | 9/10 | NOT YET |
| `az containerapp revision activate ... ca-aveto-ask--0000006` | 3 | C8.3 / C8.1 (only on a smoke failure) | 10 | NOT YET, conditional |
| Five live judge calls through the deployed service | 5 | C3.1, C8.5 | 10 | NOT YET |
| `git push -u origin claude/fix-service-accounting`, `gh pr create` (never merge) | 3 | C8.2 | 11 | NOT YET |
| New processor | 6 | C4.0 (none new) | n/a | none |
| Safety control change | 4 | C5.0 (none) | n/a | none: INV text byte-identical (QA, Security) |

## Deploy command sheet (spec 05 section 7) checked against C8.3 and C6.P

| C8.3 limit | Sheet | Result |
|---|---|---|
| `rg-aveto-ask` only | Every `az` command carries `-g rg-aveto-ask` or the ACR `acravetoaskgp` named in C6.P; the one resource group is literal | PASS (the log query uses a workspace id, read-only) |
| New image from the worktree root with `az acr build -r acravetoaskgp` | 7.1: `az acr build -r acravetoaskgp -t aveto-ask:<TAG12> --platform linux/amd64 -f Dockerfile /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/fix-service-accounting`; context is the worktree, not the main checkout | PASS. `-f` relative-to-source is the Architect's own "from memory, unconfirmed"; a path error pushes nothing and a re-run is still "one new image" |
| `az deployment group create` of the repository's `infra/main.bicep`, `deployApp=true`, new image tag, `killSwitch` explicit, new price defaults | 7.2/7.3: `-p deployApp=true imageTag=<TAG12> killSwitch=on|off configureLogRetention=true`; price not passed so the Bicep defaults apply. I read `main.bicep`: `priceInNanoPerToken int = 2000`, `priceOutNanoPerToken int = 10000`, `killSwitch string = 'on'` (default stays on), `monthlyCapUsd = 10`, `clientKey = 'xff_last'` (equal to the live values, plan "Live state") | PASS |
| New revision of `ca-aveto-ask` only, no other resource added or removed | `what-if` precedes each `create`; pass rule fixed in advance: no `Create`, no `Delete`, no type outside C8.3; environment/registry/role `Modify` noise is listed, not a stop; any change to retention is a failed check. The Bicep resources behind `if (configureLogRetention)` are the two log tables (already present from the previous run) | PASS (fail closed) |
| Kill switch on then off through the same command | D1 `killSwitch=on`, D2 `killSwitch=off`, each watched by `smoke.py watch` | PASS |
| Rollback: activate the previous revision, or kill switch on | 7.4: R1 `az containerapp revision activate -g rg-aveto-ask -n ca-aveto-ask --revision ca-aveto-ask--0000006` then revision list; R2 D1's `create` with `killSwitch=on`. Redeploying the old image through Bicep is excluded as outside C8.3's words | PASS. Target `ca-aveto-ask--0000006` matches C6.6 and C8.1 |
| Deleting a resource is not allowed | none in the sheet; `-` no `delete` verb | PASS |
| Literal commands matching C6.P prefixes | Pre-flight `git status *`, `git log *`, `az account show *`, `az containerapp revision list -g rg-aveto-ask *`, `az containerapp show -g rg-aveto-ask *`, `az bicep build *`; `az acr build -r acravetoaskgp *`; `az deployment group what-if|create -g rg-aveto-ask *`; `az containerapp revision activate -g rg-aveto-ask *`; `az monitor log-analytics query *`; smoke via `uv run *`. All match. One gap, stated by the Architect: `az monitor log-analytics workspace show` (to read the workspace id) is not in C6.P, so it prompts; a prompt, not a Charter stop | PASS with the recorded prompt |
| Placeholders | `<TAG12>` (the 12-hex commit), `<WORKSPACE_ID>`, `<D1_START_UTC>`: each replaced by a literal before running; never `$(...)` | PASS if P1 is done |

## Gates (RELEASE_GATES.md, tier 3)

### Implementation

- [x] Typecheck passed: `uv run mypy` clean, 45 files (`03-green.txt`; QA 3 of 3 runs).
- [x] Targeted tests passed: fail-first proven on 87178bd, 30 failed / 137 passed with the spec's figures (`03-failfirst-87178bd.txt`, `08-backend-note.md`; QA re-ran independently, identical 30 ids); green on head.
- [x] Full test suite passed: 668 passed, 0 failed, 12 deselected (`03-green.txt`; QA 3 more runs, same). `uv run ruff check` clean.
- [ ] Build passed: Python has no build step. The two buildable artefacts are the Bicep (`az bicep build`, in the pre-flight, NOT YET) and the image (`az acr build`, stage 9, NOT YET). Condition P3 and stage 9, not a failure.
- [x] One commit per task: the recent log is one commit per stage (`0caa3b1`, `2a7c3f2`, `cce4ec2`, `b7ebce6`, `506bcd7`; product tree at `5f86fd3`). I did not read the full `git log`; unconfirmed beyond those subjects.
- [ ] No new lint warnings (`git diff --check`): ruff is clean, but no saved `git diff --check 87178bd` output exists. Condition P2.

### QA

- [x] UI verified in preview: n/a, no UI or visible copy changed (intent: "Adds a screen or UI" unticked).
- [x] Local regression command passed (`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`): 668 passed (above).
- [x] Safety invariants verified: `13-qa-evidence.md` table; `.agentic/SAFETY_INVARIANTS.md` blob `3d976e5f...` identical on base and head; `aveto_support`, `prompts`, `.claude` tree ids equal; judge prompt sha256 `24b244d2...9427` unchanged; `test_core_files_unchanged` passes with only the C1.4 name added. "Nothing else moves" is met at `5f86fd3`; it must be re-run on the final tree (P2).
- [x] Mutations for #6, #7a, #7b, #8a, #8b each caught (QA). Adapter counting is not mutated (QA says so); covered by 13 adapter tests that fail on base.

### Security (standard, C7.1)

- [x] No secrets / credentials in diff: Security grepped the added lines of the branch diff; none. The key stays a `secretRef`.
- [x] No PII / sensitive data logged: no new log line; `billable_failures` is an integer, never logged or returned; `test_service_logging.py` passes.
- [x] Audit events cover state changes: no event added, removed or renamed (Security section 4; spec section 4). Verified by the Security cross-check, which serves as the manual verification for the tier 3 line below.
- [x] Adapter boundary placeholder still throws: `PlaceholderJudgeClient` raises `JudgeNotConfiguredError`; settles 0 and is not counted (Security section 4).
- Verdict PASS, 0 required fixes, advisories A1 to A6. Security's question "can settled spend pass the cap through any outcome" answered no (144 sequences through the real adapter).

### Tier 3 only

- [x] Human approval per `HUMAN_APPROVAL_RULES.md` ("Approval by Charter"): `APPROVAL_RECORD-1.md`, Gopal Patwa, 2026-10-23T07:18Z (STATE.md), direct in the driving session, names the file and (abbreviated) hash, plus budget. The Charter surfaces each gated action as its own line (C3.1, C8.2, C8.3). One approval for the Charter, by design.
- [x] Approval recorded: who Gopal Patwa; when 2026-10-23T07:18Z; exact request the Charter at the stated hash; exact response quoted on the record. One note on the record stands: after approving, the owner switched the session model to `claude-sonnet-5-5` while C3.2 names `claude-opus-5-5` for the Orchestrator. It is the owner's own act and is recorded; but `code-review.md` says the review was run by `claude-opus-5-5` and the Orchestrator's own model cannot be checked by me from the artefacts (telemetry is self-reported). Reconcile the wording in `END_REVIEW.md`.
- [x] Dry-run on a fixture before live: all new tests drive the real `AnthropicJudgeClient` over an injected fake `messages` client, offline, with the autouse network block on; `smoke.py --dry-run` was run (backend note addendum), no live call. The `what-if` before each `create` is the deploy-side dry run (NOT YET, P-D).
- [x] Audit event coverage manually verified: see Security above.
- [x] Post-launch monitoring plan exists: below.

### Enterprise and governance gates

All n/a with a reason: Data governance, compliance, vendor risk (no new data, processor or subprocessor; C4.0), AI governance (judge, prompt and model unchanged; no eval rescored), schema/data migration (no storage; counters are in memory), threat model (no new input surface; Security standard confirms), FinOps as its own gate (cost figures are the Architect's and Security's; kill switch is exercised by D1/D2), change request/CAB (not enterprise context; the Charter is the recorded approval), SRE runbook (the runbook was updated by Docs; rollback drill see R-1).

### Skipped gates

| Gate | Reason for skip | Approved by |
|------|-----------------|-------------|
| Market research, PRD, feature spec, UX spec stages | Bug fix with no visitor-facing change; the intent states problem, user and Done means (plan, "Skipped on purpose") | Orchestrator in the plan, confirmed by the Charter (C1.2 hash) |
| AI Governance, Compliance, Data Governance, FinOps as separate stages | No model, prompt, processor or data change (C4.0, C5.0) | Orchestrator in the plan, confirmed by the Charter |
| Security at adversarial depth | The Charter fixes standard (C7.1); not lowered by anyone | Charter |

No release gate was skipped without a reason.

## Pre-deploy conditions (stage 9 may start only when all hold)

| id | Condition | Who | Fail means |
|---|---|---|---|
| P1 | Tree clean (`git status --porcelain` empty); `<TAG12>` is the 12-hex short hash of the HEAD that carries this checklist's gated product tree; all three placeholders replaced by literals. Any later commit that touches a path outside `runs/` voids this checklist and sends the slice back through P2 | Orchestrator | no deploy |
| P2 | On the final tree, spec section 6 checks 1 to 5 re-run and saved under the run folder (`git diff --exit-code 87178bd -- aveto_support prompts .claude .agentic ':(exclude).agentic/CURRENT_MVP_STATUS.md'`, each protected path alone, `git status --porcelain -- aveto_support prompts .claude .agentic`, `git diff --name-only 87178bd -- . ':(exclude)runs'` is within the 14 known paths plus no other, `test_core_files_unchanged`); plus `git diff --check 87178bd` and `git diff 87178bd -- .claude/settings.json` (empty of allow rules) saved. The docs files are now in the diff, so this is the check QA could not make | Orchestrator | no deploy |
| P3 | Pre-flight (spec 7.0) passes: subscription Enabled; active revision exactly `ca-aveto-ask--0000006 100 Healthy` (else the rollback target is not the Charter's: stop); before-state env saved (`3000`/`15000`, switch `off`, key as `secretRef` only); `az bicep build` compiles | Orchestrator | no deploy (C8.1); an expired sign-in is Charter stop 3 |
| P4 | `smoke.py` was committed (`8aee3b4`) after `code-review.md`'s head (`5f86fd3`) and QA did not review it, so it is **unreviewed code that will make five live, billed calls**. I read it end to end: matches spec 8.1; host is the single `SERVICE_URL`; no `az` call; no retry on a POST (the watcher's bounded empty-question POST only); question and reply text are never written (only ids, status, outcome, seconds, field names); 15% band and the #8 check as the spec; an empty question is refused at validation before any rate count (`pipeline.py:220`, so the watcher cannot eat the visitor's ten-an-hour). This is a Release Manager read, not a `/code-review`. Condition: the Orchestrator either runs a quick review of the file or records that it accepts this read; and runs `smoke.py ... --dry-run` again on the final tree | Orchestrator | the smoke does not run; the deploy may still proceed but then a smoke-less deploy is outside the plan, so do not deploy first |
| P5 | Notice of budget status sent (C2.2): spent 775k against plan 730k (106%); projection about 1,015k with stages 8 to 11, above the 950k ceiling and below the 1,200k hard cap. C2.2: above the ceiling the run continues and sends a notice. Hard cap is a stop (C2.3); 425k headroom. Re-run `events-verify.mjs` and save at the end | Orchestrator | stop only at the hard cap |
| P-D | `what-if` for D1 passes its fixed rule (no `Create`/`Delete`; `Modify` on `ca-aveto-ask` only for image tag `879cae23690b` to `<TAG12>`, `ASK_KILL_SWITCH` off to on, prices 3000/15000 to 2000/10000), saved, before the first `create`. A failed what-if is a failed check: no deploy | Orchestrator | no deploy |

Also before stage 9 starts: the build's ingest line `wrote index/docs-index.json sha256 <hex>` must equal `f36ef5d4...a756` (spec 7.1). A mismatch is reported and makes the smoke's byte-equality "not established"; it is not a stop.

## Post-deploy checks (stages 9 and 10; fixed in advance by spec 05 sections 7 and 8)

After D1 (`killSwitch=on`, watcher started first):
1. One new revision (predicted `ca-aveto-ask--0000007`, a prediction) at 100% and Healthy; image `acravetoaskgp.azurecr.io/aveto-ask:<TAG12>`; env `ASK_PRICE_IN_NANO_PER_TOKEN 2000`, `ASK_PRICE_OUT_NANO_PER_TOKEN 10000`, `ASK_KILL_SWITCH on`, `ASK_CLIENT_KEY xff_last`, `ASK_MONTHLY_CAP_USD 10`, key a `secretRef` with no value.
2. `/health` shows `"kill_switch":"on"` and an empty-question `POST /ask` returns 503 `service_off`; seconds to state recorded. A revision that does not go Healthy: previous revision keeps serving or R1; stop and report.

After D2 (`killSwitch=off`): same two reads, new revision (predicted `...0008`) at 100% Healthy, env as above with `off`; the what-if showed only `ASK_KILL_SWITCH` on to off; three consecutive `off` reads.

Smoke (one replica lifetime, straight after D2):
3. g01, g03, g04 answered `answer`; gu15, gu18 `no_confident_match`; each HTTP 200. Any other outcome or a 5xx/network error is a behaviour failure: R1, else R2, report, stop (C8.1).
4. Every `answer` byte-equal to the local `retrieve` when the index hash matches the build's ingest hash.
5. `Δjudged = 5` in a valid window (same `day`, `judged_today` not down). A restart in the window means "not measured" and the questions are not re-sent.
6. Cost per judged question `(Δin x 2000 + Δout x 10000) / Δjudged` inside $0.00663 to $0.00897 (15% of $0.0078). Outside is reported as measured, not a rollback (C8.1). `Δspend` within 2,000 nano-dollars of the token cost proves the live counter charges at $2/$10; a larger gap near one per-attempt reservation shows a billed retry.
7. No question text in any log table: wait at least 5 minutes after the last request, confirm the smoke's own abuse rows arrived, then the three queries (abuse lines only in the first, no rows in the second and third; a third-query row fails only if it holds question words). The first-use prompt of `az monitor log-analytics workspace show` is recorded.
8. gu15 or gu18 answered with passages: R2 directly (kill switch on), stop.
9. Kill-switch timing recorded (seconds, previous run 65 s on and 66 s plus about 6 s off, not like-for-like for D1).
10. Every saved output under `runs/fix-service-accounting/09-deploy/` and `10-smoke/` searched for `sk-ant` and key-shaped strings, subscription id masked, before commit. No command that prints a secret value is run.

Rollback decision uses spec 8.5 as written; I add nothing to it.

## Rollback plan

Lifted from spec section 7.4 and confirmed against the diff (code: five source files and the Bicep, no data model, no storage, no migration, so nothing to undo in data):

1. Before D1 (build, what-if, or any gate fails): nothing to undo; `ca-aveto-ask--0000006` (image `aveto-ask:879cae23690b`, 3000/15000, switch off) keeps serving; close-out, stop.
2. After D1 or D2 on a behaviour failure: `az containerapp revision activate -g rg-aveto-ask -n ca-aveto-ask --revision ca-aveto-ask--0000006`, then the revision list; pass is `...0006` active, traffic 100, Healthy, `/health` `"kill_switch":"off"` (the exact pre-slice service).
3. If step 2 errors or `...0006` does not hold 100% within 5 minutes: D1's `create` with `killSwitch=on` (the service then refuses everything and calls no model); report and stop.
4. Code: nothing merges in the run (C8.2); undoing it means not merging the PR, or reverting the merge commit after the owner merges. Redeploying the old image through Bicep and deleting anything are outside the Charter and need the owner.

**R-1 (gap, not a failure): the rollback is not rehearsed.** `CODE_REVIEW.md` section 2 says High-tier rollback "is rehearsed before it is offered". `revision activate` under single-revision mode has never been run on this app (spec 7.4, R3 in section 10); only the kill-switch direction was rehearsed in the previous run (`runs/public-ask-the-docs/17-deploy/e3-rollback.txt`), and D1 re-exercises it live. A rehearsal of R1 on a passing run is not named in C8.3 (it names `activate` only "on a smoke failure"), so doing it would be an action outside the Charter (stop 1). So the run cannot rehearse it without the owner. END_REVIEW must say this plainly.

## Post-launch monitoring (Tier 3)

- Signals to watch (owner, and the Post-Launch Learning agent in its stage): `/health` `spend_today_usd` against `judged_today` x token cost (the counter should track the Anthropic console at $2/$10); the Anthropic console spend against the counter, particularly after any day with 5xx or connection errors (A1: a connection error then success is now counted as usage only); `paused` outcomes per day against the roughly 33-a-day estimate (labelled estimate, payload about 10 kB assumed, not measured); abuse-log lines only in the `{"t","ip","o"}` shape; `judge_error` rate.
- Threshold for concern: counter below the console by more than one per-attempt reservation (about $0.03, estimate) on a day; any non-abuse row in the log tables; a day that pauses before about 20 questions; a cost per question outside $0.00663 to $0.00897 over more than the smoke's five.
- The Anthropic console limit remains the backstop for the monthly $10 (decision D1: counters restart with each revision; the two deploys reset them twice today, so today's real spend can exceed the day's share, Security A4).
- Owner: Post-Launch Learning Agent for the record; the owner for any action.

## For END_REVIEW (so the owner sees it, not for a stop)

1. Security A1 and A2 are owner decisions: connection-error-then-success and 429-then-success are now charged usage only; that Anthropic does not bill a 429 is unconfirmed (where looked: repo records, the SDK source; no network). A3 to A5 are backlog candidates (midnight straddle; counters reset; unclamped settle).
2. The day pauses at about 33 questions (estimate), not the intent's "about 41": the design reserves two attempts. Docs say so.
3. R-1: rollback by `revision activate` is unrehearsed; the kill-switch rollback is.
4. Budget: spend above plan (775k of 730k at this point, projected about 1,015k), above the 950k ceiling by projection; notice sent (P5); under the 1,200k hard cap.
5. Model lines: the owner switched the session model to `claude-sonnet-5-5` after approving a Charter whose C3.2 names `claude-opus-5-5` for the Orchestrator; `code-review.md` attributes the review to `claude-opus-5-5`. Reconcile in the record.
6. `smoke.py` was reviewed only by the Release Manager's read (P4). The price source in the code comment (Anthropic's pricing page and the owner's console bill, read 2026-10-23) was not checked by QA, Security or me.
7. After the deploy, the docs still say "not deployed yet" in several places (`15-docs-note.md`); stage 11 must update those lines to the deployed state and the smoke's recorded figures before the PR, and the PR body must carry `Closes #6`, `Closes #7`, `Closes #8`.
8. Event-log alert: `seq 533: main attempted Bash cd ... no outcome recorded`; not a write, not blocking.
9. Gated-command permission prompts (C6.P) recorded: `az acr build`, `az deployment group create`, `revision activate`, `git push`, `gh pr create`, and `az monitor log-analytics workspace show`.

## Decision

- [x] **Go with conditions, for stage 9 (the deploy only)**: conditions P1 to P5 and P-D above; the slice does not land yet.
- [ ] No-go.

What this does not decide: stage 10's verdict (the live smoke, by spec 8.5) and the pull request at stage 11, which the owner merges or not (C8.2: never merged by the run). Landing is the end action and stays with the owner (C8.2, C8.4: review). Tier 1 auto-merge does not apply: the run is tier 3 and there is no standing Charter.

## Hand off

If P1 to P5 and P-D hold: stage 9 (Cloud Deployment writes the command record; the Orchestrator runs the commands under C8.3), then stage 10 (Production Verification), then the Post-Launch Learning Agent at stage 11. If any pre-deploy condition fails: back to the Orchestrator with that condition named; for P2 findings the owning stage is the Backend (code) or the Tech Writer (docs).
