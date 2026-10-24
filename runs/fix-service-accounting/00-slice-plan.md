# Slice plan — fix-service-accounting

> Orchestrator, 2026-10-23. **Proposed; confirmed with the Charter.** Units: peak context summed per spawn.
> Worktree `.claude/worktrees/fix-service-accounting`, branch `claude/fix-service-accounting`, cut from `main` at 87178bd (pull request 5 merged at 7a32311; pack v28 installed at 87178bd; `main` level with `origin/main`). Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (absolute). Baseline on 87178bd: mypy clean (45 files), ruff clean, `pytest` **636 passed, 1 failed**, 12 deselected.

## Baseline failure found at setup (not one of #6 to #8)
`tests/test_service_pipeline.py::test_core_files_unchanged` fails on `main`: it pins the names in `.claude/hooks/` to `budget-guard.mjs` and `write-scope-guard.mjs`, and pack v28 (87178bd) added `event-log.mjs`. The planned fix is test-only: add `event-log.mjs` to the expected set (stage 3, Backend), so the guard keeps pinning the folder. Nothing under `.claude/` changes. Covered in the Charter as C1.4.

## Live state read at setup (2026-10-23)
Active revision `ca-aveto-ask--0000006` (100% traffic, image `acravetoaskgp.azurecr.io/aveto-ask:879cae23690b`); env `ASK_KILL_SWITCH=off`, `ASK_PRICE_IN_NANO_PER_TOKEN=3000`, `ASK_PRICE_OUT_NANO_PER_TOKEN=15000`, `ASK_MONTHLY_CAP_USD=10`, `ASK_CLIENT_KEY=xff_last`. The Bicep default `killSwitch` is `on`, so the redeploy must pass the switch state explicitly (stage 2 names it).

## Outcome (one line)
The public service reserves and settles judge spend correctly (retries reserved or re-checked, earlier billed attempts kept, the price at $2 and $10 per million tokens), proved by fail-first tests, redeployed to `rg-aveto-ask` and smoke-checked live.

## Success criteria
`intent.md` "Done means", by reference, not restated. Release Gate tier 3. Security Review standard. Review layer tier High.

## Non-goals
Decision D1 (counters that survive a restart); changing the daily or monthly caps; the page's privacy or Article 50 wording; retrieval, ranking, the judge prompt `answerability-judge-v1`, the corpus; any new feature; any change under `aveto_support/`, `prompts/`, `.claude/` or `.agentic/SAFETY_INVARIANTS.md`.

## Constraints from `.agentic/`
INV-1 to INV-5 unchanged, byte for byte (Charter C5.0). Python 3.12, uv, no new runtime dependency. Anthropic and Azure only (no new processor). Agents never handle a credential: the key stays in Key Vault and is checked by name only. The offline commands stay offline; the default test suite makes no network call.

## Stages (tier 3; Stakes tick real user data, money and irreversible; no UI, no safety control)

| # | Stage | Owner | Depth | Environment | Est. |
|---|-------|-------|-------|-------------|------|
| 1 | Scope review: confirm size and the compressed stage list | Engineering Manager | standard | default | 50k |
| 2 | Tech spec: #6 approach chosen with reasons (reserve both attempts and refund, or re-check before retry); #7 rule in one sentence; #8 figures and every file that quotes them; the fail-first tests named; the redeploy's exact parameters (including `killSwitch` and the price, whose Bicep default `killSwitch` is `on`); the five smoke questions picked from earlier spent eval sets | Software Architect | standard | default | 90k |
| 3 | Fixes and fail-first tests (each new test run on 87178bd first and shown failing) | Backend Architect | standard | default | 110k |
| 4 | Review layer: `/code-review` at `high` against `main`, `REVIEW.md` as rules, tier from the diff; findings to the Backend, three rounds at most | Orchestrator | high | default | 50k |
| 5 | QA evidence on the final tree (offline), incl. "nothing else moves" diff | QA Evidence | standard | default | 70k |
| 6 | Security Review limited to the accounting code and the new tests | Security & Privacy | standard | default | 70k |
| 7 | Docs: runbook, README, CURRENT_MVP_STATUS with recorded figures only; estimates labelled | Tech Writer | standard | default | 50k |
| 8 | Release Gate tier 3 (`charter-check` re-run and saved; event log verified and copied) | Release Manager | standard | default | 80k |
| 9 | Deploy to `rg-aveto-ask` (Charter C8.3): `az acr build`, `az deployment group create`; the commands run in the Orchestrator's session (the deploy role has no shell); Cloud Deployment writes the command sheet and rollback first | Cloud Deployment, Orchestrator | standard | default | 60k |
| 10 | Live smoke (five questions, cost per question from `/health`, log search, kill switch on then off, timed) and verdict | Orchestrator, Production Verification | standard | default | 60k |
| 11 | Post-launch learning; `trace.json`, `END_REVIEW.md`, push, pull request (Charter C8.2) | Post-Launch Learning, Orchestrator | standard | default | 40k |

Estimated sum 730k; **plan total 730k**. Ceiling proposed at 950k (1.3×; no adversarial stage and no model proposal, per `RUN_ECONOMICS.md` §2); hard cap 1.2M as the intent recommends. The intent recommended 700k / 900k / 1.2M; the stage sum is 30k above 700k.
Skipped on purpose: Market Research, PRD, Feature spec, UX spec (a bug fix with no visitor-facing change; the intent states the problem, the user and Done means), AI Governance (no model or prompt change; the judge is unchanged), Compliance and Data Governance (no new processor or data; C4.0), FinOps as its own stage (the cost figures are the Architect's and the Security Review's). Gates do not compress; none is dropped. No `fresh-load` stage.

Order and gates: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11. A failed gate sends the slice back per `FAILURE_LOOP.md` (two retries per stage, then escalate).

## Gated actions (scan of `HUMAN_APPROVAL_RULES.md`)
- Rule 3 (deploy): stage 9 (image build, new revision) and stage 10 (kill switch on, then off), Charter C8.3; the push and pull request, C8.2.
- Rule 5 (real model): the live smoke sends five questions through the unchanged runtime judge, Charter C3.1.
- Rule 6 (processor): none new; Anthropic and Azure as approved in `runs/public-ask-the-docs/CHARTER-v2.md` C4.1 and C4.2 (Charter C4.0).
- Rules 1, 2 and 4: none.

## Prerequisites (setup phase; every row has a dry run before the first stage)

| id | What | Stage | Dry run |
|---|---|---|---|
| C6.P | Allow rules in `.claude/settings.local.json` (gitignored), written only after the Charter is approved, deleted after the pull request opens | every stage | each allowed command run once in setup, no prompt |
| C6.1 | Branch cut from `main` at 87178bd, pack v28 | every stage | `git merge-base --is-ancestor 7a32311 HEAD` exit 0; `grep packVersion .claude/agentic.config.json` prints 28 |
| C6.2 | Agent teams on | stages 1 to 11 | `.claude/settings.json` env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| C6.3 | `uv sync --locked`; baseline regression on 87178bd | stages 3 to 8 | mypy, ruff clean; 636 passed, 1 failed (the baseline failure above) (done) |
| C6.4 | Azure sign-in | stages 9, 10 | `az account show` prints "Visual Studio Enterprise Subscription", Enabled |
| C6.5 | Key Vault secret exists | stages 9, 10 | `az keyvault secret list --vault-name kv-aveto-ask-gp --query "[].name" -o tsv` lists `anthropic-api-key`; the value is never read |
| C6.6 | Live service and its current revision | stages 9, 10 | `az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask` shows the active revision (the rollback target) |
| C6.7 | Event log hook writing (the session's project dir is the main checkout) | every stage | `/Users/gopalpatwa/opt/aveto-support/.claude/events/b964fb4e-04f7-4fbf-b787-36bfe8d105df.jsonl` exists and grows (done) |
