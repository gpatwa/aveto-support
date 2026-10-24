# Charter: fix-service-accounting

> The only human approval in a Process v2 run. The Orchestrator drafts this file
> at plan confirmation; the human reads it whole and approves it once, in their
> own words, naming this file and its sha256 (`node <playbook>/execution/charter-check.mjs
> runs/fix-service-accounting/CHARTER.md` prints both). After that the run proceeds to a
> finished result and **asks nothing**. It stops only when an action is outside
> this Charter (section 9). Every gated action cites the line id that allows it.

## 1. Scope
- **C1.1 Intent:** `runs/fix-service-accounting/intent.md`, sha256 `d5946e7f955a3d487fbef67b0994ce214bd22d94cb4da1351217982667939cc7` (a byte copy of `intents/fix-service-accounting.md`, confirmed by the owner 2026-10-23)
- **C1.2 Plan:** `runs/fix-service-accounting/00-slice-plan.md`, sha256 `ccc851c6c166ff74590aaa8567bd97212cafd63c72ebb27a110dae0e4f575e3d`
- **C1.3 Non-goals:** Decision D1 (counters that survive a restart); changing the daily or monthly caps; the page's privacy or Article 50 wording; retrieval, ranking, the judge prompt `answerability-judge-v1`, the corpus; any new feature; any change under `aveto_support/`, `prompts/`, `.claude/` or `.agentic/SAFETY_INVARIANTS.md`.
- **C1.4 Baseline repair:** `tests/test_service_pipeline.py::test_core_files_unchanged` fails on `main` at 87178bd because pack v28 added `.claude/hooks/event-log.mjs`; the run may add `event-log.mjs` to that test's expected set of hook names, and nothing else in that test.

## 2. Budget (unit: peak context summed per spawn)
- **C2.1 Plan total:** 730k
- **C2.2 Ceiling:** 950k. Above it the run continues and sends a notice.
- **C2.3 Hard cap:** 1,200k. Above it the run stops. The run never raises it.

## 3. Models (rule 5)
- **C3.1** Runtime answerability judge (unchanged): `claude-sonnet-5-5`, effort high, the app at runtime via the Anthropic Messages API; called live only by the stage 10 smoke (five questions) and by visitors.
- **C3.2** Orchestrator and the review layer (`/code-review`): `claude-opus-5-5`, effort high, the operator's session.
- **C3.3** Software Architect and Security & Privacy: `claude-opus-5-5`, effort high, the operator's session.
- **C3.4** QA Evidence and Release Manager: `claude-sonnet-5-5`, effort high, the operator's session.
- **C3.5** Engineering Manager, Backend Architect, Tech Writer, Cloud Deployment, Production Verification and Post-Launch Learning: `claude-sonnet-5-5`, effort medium, the operator's session. A failure escalation may raise a role's effort per `MODEL_ROUTING.md`; it never changes its model.
- **C3.R Review rescore:** no rescore since 2026-10-17; the review in this run is `unscored`, and `code-review.md` says so.

## 4. Data processors (rule 6)
- **C4.0** None beyond those already approved: Anthropic (Commercial Terms, DPA by reference) and Microsoft Azure, as in `runs/public-ask-the-docs/CHARTER-v2.md` C4.1 and C4.2 (APPROVAL_RECORD-2 of that slice). In this run Anthropic receives, from the run itself, only the five smoke questions and the passages `retrieve` shows for them, through the deployed service; no personal data.

## 5. Safety controls (rule 4)
- **C5.0** None. INV-1 to INV-5 stay byte-identical; if a change to safety text turns out to be needed, the run stops (section 9, item 1).

## 6. Prerequisites (set once in the setup phase, each with its dry run)
| id | What | Why | Dry run that proves it |
|---|---|---|---|
| C6.P | Allow rules written to the main checkout's `/Users/gopalpatwa/opt/aveto-support/.claude/settings.local.json` (gitignored; the session's project dir), after this Charter is approved, deleted after the pull request opens; exactly: `Bash(uv run *)`, `Bash(uv sync --locked)`, `Bash(git status *)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git show *)`, `Bash(git add *)`, `Bash(git commit *)`, `Bash(git worktree add --detach *)`, `Bash(git worktree remove *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/charter-check.mjs *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/events-verify.mjs *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/usage.mjs *)`, `Bash(az account show *)`, `Bash(az keyvault secret list --vault-name kv-aveto-ask-gp *)`, `Bash(az containerapp show -g rg-aveto-ask *)`, `Bash(az containerapp revision list -g rg-aveto-ask *)`, `Bash(az containerapp revision activate -g rg-aveto-ask *)`, `Bash(az acr build -r acravetoaskgp *)`, `Bash(az bicep build *)`, `Bash(az deployment group what-if -g rg-aveto-ask *)`, `Bash(az deployment group create -g rg-aveto-ask *)`, `Bash(az monitor log-analytics query *)`, `Bash(git push -u origin claude/fix-service-accounting)`, `Bash(gh pr create *)`, `Bash(gh issue view *)`. Deploy commands are written with literal values (no shell variables), so they match these prefixes; the live smoke calls the service through a `uv run python` script, not `curl` | every stage | each read-only rule run once in setup with no prompt; the gated ones (`az acr build`, `az deployment group create`, `revision activate`, `git push`, `gh pr create`) are not run in setup, and a prompt on their first use is recorded in `END_REVIEW.md` |
| C6.1 | Branch `claude/fix-service-accounting` cut from `main` at 87178bd (pull request 5 merged; pack v28) | every stage | `grep packVersion .claude/agentic.config.json` prints 28 (done) |
| C6.2 | Agent teams on (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, tracked `.claude/settings.json`) | stages 1 to 11 | present in `.claude/settings.json` env (done) |
| C6.3 | `uv sync --locked` in the worktree; baseline regression | stages 3 to 8 | mypy clean, ruff clean, 636 passed, 1 failed (C1.4) (done) |
| C6.4 | Azure sign-in, subscription "Visual Studio Enterprise Subscription" | stages 9, 10 | `az account show` Enabled (done) |
| C6.5 | Key Vault `kv-aveto-ask-gp` holds secret `anthropic-api-key` | stages 9, 10 | `az keyvault secret list` prints the name; the value is never read (done) |
| C6.6 | Rollback target: active revision `ca-aveto-ask--0000006`, image `aveto-ask:879cae23690b`, kill switch off | stages 9, 10 | `az containerapp revision list` (done) |
| C6.7 | Event log writing to `/Users/gopalpatwa/opt/aveto-support/.claude/events/b964fb4e-04f7-4fbf-b787-36bfe8d105df.jsonl` | every stage | `events-verify.mjs` prints "chain intact" (done) |

## 7. Depth (may not be lowered)
- **C7.1** Security Review: standard (limited to the accounting code, the price defaults and the new tests)
- **C7.2** Release Gate tier: 3

## 8. Outcomes decided now
- **C8.1 If a pre-registered check fails:** before the deploy, a failed check or gate means no deploy, revision `ca-aveto-ask--0000006` keeps serving, a close-out is written, the run stops. After the deploy, if the new revision fails the live smoke on behaviour (an answer or refusal different from `retrieve`'s, question text in a log table, or a kill switch that does not take), the run activates revision `ca-aveto-ask--0000006` (or sets the kill switch on if activation fails), reports, and stops. A cost per question outside 15% of $0.0078 is reported as measured and is not a rollback by itself.
- **C8.2 At the end of a passing run:** push `claude/fix-service-accounting` to origin and open a pull request into `main` that closes issues #6, #7 and #8, with `END_REVIEW.md` linked; never merge.
- **C8.3 Irreversible actions allowed (rules 1 to 3):** in resource group `rg-aveto-ask` only: build and push one new image from the worktree root with `az acr build -r acravetoaskgp`; deploy the repository's `infra/main.bicep` with `az deployment group create -g rg-aveto-ask` (`deployApp=true`, the new image tag, `killSwitch` set explicitly, the new price defaults; creates a new revision of `ca-aveto-ask` only, no other resource added or removed); set the kill switch on, then off, through the same deployment command, for the smoke; on a smoke failure, activate revision `ca-aveto-ask--0000006`. Rollback: activate the previous revision, or set the kill switch on. Deleting any resource is not allowed. The branch push and pull request in C8.2.
- **C8.4 Human review of a Low-risk change at the end:** review
- **C8.5 Owner positions recorded by this Charter:** the five smoke questions are sent once through the real limits, no bypass; their spend counts against C2 as context and against the service's own day share as money.

## 9. Stops (the only reasons the run asks)
1. An action not covered by a line above (a new model, processor, data, file, invariant, or irreversible action).
2. Spend above the hard cap (C2.3).
3. A credential is needed (agents never handle credentials), including an expired `az login`.
4. Lowering a depth in section 7.
5. A change to this Charter (an amendment is a new approval of a new hash).

## 10. Notices (sent, never asked)
A push notification at each stage boundary with two lines: the stage, its result
and the spend. The full record stays in `runs/fix-service-accounting/`.
