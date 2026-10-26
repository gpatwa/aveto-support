# Charter: polished-chat-experience

> The only human approval in a Process v2 run. The Orchestrator drafts this file
> at plan confirmation; the human reads it whole and approves it once, in their
> own words, naming this file and its sha256 (`node <playbook>/execution/charter-check.mjs
> runs/polished-chat-experience/CHARTER.md` prints both). After that the run proceeds to a
> finished result and **asks nothing**. It stops only when an action is outside
> this Charter (section 9). Every gated action cites the line id that allows it.

## 1. Scope
- **C1.1 Intent:** `runs/polished-chat-experience/intent.md`, sha256 `368bc3e470ff66854cb0558c05d90dc50fd9aa64ebedd122ca05486e43ffb89a` (a byte copy of `intents/polished-chat-experience.md`, confirmed by the owner 2026-10-26)
- **C1.2 Plan:** `runs/polished-chat-experience/00-slice-plan.md`, sha256 `cea610e3c1a729b69eb665802b076eb000f44e7a8867c95c91fe5ab3954b8069`
- **C1.3 Non-goals:** Option (b) embedding and any change to `frame-ancestors 'none'` or another response header; multi-turn conversation; answers written by a model; accounts or login; a second product; changing the daily or monthly cap; decision D1 (counters surviving a restart); any change under `aveto_support/`, `prompts/` or `.claude/`; any change under `.agentic/` except `.agentic/CURRENT_MVP_STATUS.md` (recorded figures only); the page's privacy or Article 50 wording (byte-identical); the aveto.dev change (a separate playbook commit, wording first approved by the owner).
- **C1.4 Quality bars, fixed now and not moved by the run.** Each is checked at the stage named and recorded in `END_REVIEW.md`; a miss fails the gate and sends the slice back (C8.1 before the deploy).
  1. *Answering is byte-identical.* `git diff main --stat -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md` is empty; and, for the fixed question set the Architect lists (at least 10, drawn from spent eval sets, answered and refused), `POST /ask` JSON bodies from `main` and from the branch, run offline against the same fake judge, are byte-equal (QA, stage 7).
  2. *The answer card holds only listed text.* A test proves every sentence on the answer card appears in a passage the response lists; the refusal card holds no model-written text (fail-first, stages 4 and 5).
  3. *Accessibility.* `axe-core` (tags `wcag2a`, `wcag2aa`, `wcag21aa`, `wcag22aa`) reports **zero violations of impact `serious` or `critical`** on `GET /`, an answer result, a refusal result, the resting state and the scorecard page (Orchestrator, stage 8).
  4. *375 px and keyboard.* At 375×812 there is no horizontal scrolling on any of those five views and every control is at least 24×24 CSS px; with the keyboard alone a visitor can load a suggested question, submit, reach the result, open and close the receipts drawer and follow the source link, with a visible focus indicator and no keyboard trap (stage 8).
  5. *Timings are reported as measured, with no pass figure.* Warm response time (median and slowest of at least 10 consecutive warm requests, local, offline fake judge, and 5 live) and cold-start time (a timed request after scale to zero, live), in seconds, each with the date and method. A figure with no measurement is not shown anywhere.
  6. *No open finding of severity P0 or P1* in `code-review.md`, QA or the Security Review at the Release Gate. P2 and below are listed in `END_REVIEW.md`.
  7. *Tests.* The suite passes with no failures and at least 668 tests plus the new ones; the four tests in the intent (refusal card without model-written text; resting state at the cap; counts record no question text; receipts drawer shows nothing the service did not hold) each fail on `main` 32e54a6 first and pass on the final tree; mypy and ruff clean.
  8. *Nothing about answering moves:* INV-1 to INV-5, the kill switch, the 500-character and ten-an-hour limits, the daily cap and the privacy wording are unchanged; a needed change to safety text stops the run (section 9, item 1).
- **C1.5 Dev-only accessibility tool:** `axe-core`, one pinned version (the Orchestrator records it in `END_REVIEW.md`), may be fetched with `npm install --prefix` into this session's scratchpad directory only. It is never added to the repository, `pyproject.toml`, `uv.lock` or the image, and loads on no served page.
- **C1.6 Public wording:** the new visitor-facing strings are the UX spec's copy deck (stage 2) and may contain no claim about privacy, data handling, the law or AI beyond what the live page already says. The pre-existing privacy and Article 50 text stays byte-identical. The owner sees the whole copy deck in `END_REVIEW.md`, after the deploy; if the owner dislikes any string, the remedy is the rollback (C8.3) or the kill switch. If the owner wants the wording seen before the deploy, they say so before approving this hash and the Charter is amended.

## 2. Budget (unit: peak context summed per spawn)
- **C2.1 Plan total:** 1,000k
- **C2.2 Ceiling:** 1,300k. Above it the run continues and sends a notice.
- **C2.3 Hard cap:** 2,000k. Above it the run stops. The run never raises it.

## 3. Models (rule 5)
- **C3.1** Runtime answerability judge (unchanged): `claude-sonnet-5-5`, effort high, the app at runtime via the Anthropic Messages API; called live only by the stage 13 checks (at most 8 questions, through the real limits, no bypass) and by visitors.
- **C3.2** Orchestrator and the review layer (`/code-review`): `claude-sonnet-5-5`, effort high, the operator's session (the model the owner set for this session; the trace records the effort it actually ran at).
- **C3.3** Software Architect and Security & Privacy: `claude-opus-5-5`, effort high, the operator's session.
- **C3.4** QA Evidence and Release Manager: `claude-sonnet-5-5`, effort high, the operator's session.
- **C3.5** Engineering Manager, UI Designer, Backend Architect, Frontend Developer, Tech Writer, Cloud Deployment, Production Verification and Post-Launch Learning: `claude-sonnet-5-5`, effort medium, the operator's session. A failure escalation may raise a role's effort per `MODEL_ROUTING.md`; it never changes its model.
- **C3.R Review rescore:** no rescore since 2026-10-17; the review in this run is `unscored`, and `code-review.md` says so.

## 4. Data processors (rule 6)
- **C4.0** None beyond those already approved: Anthropic (Commercial Terms, DPA by reference) and Microsoft Azure, as in `runs/public-ask-the-docs/CHARTER-v2.md` C4.1 and C4.2. In this run Anthropic receives, from the run itself, only the stage 13 live questions (at most 8, taken from spent eval sets) and the passages `retrieve` shows for them, through the deployed service; no personal data. The `axe-core` fetch (C1.5) is a package download to a scratch directory, not a data processor.

## 5. Safety controls (rule 4)
- **C5.0** None. INV-1 to INV-5 stay byte-identical; the response headers (including `frame-ancestors 'none'` and the `'self'` CSP) stay byte-identical; if a change to safety text turns out to be needed, the run stops (section 9, item 1).

## 6. Prerequisites (set once in the setup phase, each with its dry run)
| id | What | Why | Dry run that proves it |
|---|---|---|---|
| C6.P | Allow rules written to the main checkout's `/Users/gopalpatwa/opt/aveto-support/.claude/settings.local.json` (gitignored; the session's project dir), after this Charter is approved, deleted after the pull request opens; exactly: `Agent(engineering-manager)`, `Agent(ui-designer)`, `Agent(software-architect)`, `Agent(backend-architect)`, `Agent(frontend-developer)`, `Agent(qa-evidence)`, `Agent(security-privacy)`, `Agent(tech-writer)`, `Agent(release-manager)`, `Agent(cloud-deployment)`, `Agent(production-verification)`, `Agent(post-launch-learning)`, `Bash(uv run *)`, `Bash(uv sync --locked)`, `Bash(git status *)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git show *)`, `Bash(git rev-list *)`, `Bash(git merge-base *)`, `Bash(git add *)`, `Bash(git commit *)`, `Bash(shasum -a 256 *)`, `Bash(date -u *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/charter-check.mjs *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/events-verify.mjs *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/usage.mjs *)`, `Bash(npm install --prefix /private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-interesting-shannon-67bff6/1dbb5af3-2658-4b6f-ab7a-5c8d7e249de5/scratchpad/axe *)`, `Bash(az account show *)`, `Bash(az keyvault secret list --vault-name kv-aveto-ask-gp *)`, `Bash(az containerapp show -g rg-aveto-ask *)`, `Bash(az containerapp revision list -g rg-aveto-ask *)`, `Bash(az acr repository show-tags -n acravetoaskgp *)`, `Bash(az acr build -r acravetoaskgp *)`, `Bash(az bicep build *)`, `Bash(az deployment group what-if -g rg-aveto-ask *)`, `Bash(az deployment group create -g rg-aveto-ask *)`, `Bash(az monitor log-analytics query *)`, `Bash(git push -u origin claude/interesting-shannon-67bff6)`, `Bash(gh pr create *)`, `Bash(gh pr view *)`, `mcp__Claude_Browser__navigate`, `mcp__Claude_Browser__preview_start`, `mcp__Claude_Browser__computer`, `mcp__Claude_Browser__javascript_tool`, `mcp__Claude_Browser__read_page`, `mcp__Claude_Browser__get_page_text`, `mcp__Claude_Browser__find`, `mcp__Claude_Browser__resize_window`, `mcp__Claude_Browser__read_console_messages`. Deploy commands are written with literal values (no shell variables), so they match these prefixes; live checks call the service through a `uv run python` script, not `curl` | every stage | each read-only rule run once in setup with no prompt; the gated ones (`az acr build`, `az deployment group create`, `git push`, `gh pr create`) are not run in setup, and a prompt on their first use is recorded in `END_REVIEW.md` |
| C6.1 | Branch `claude/interesting-shannon-67bff6` level with `main` 32e54a6, pack v29 | every stage | `git rev-list --left-right --count HEAD...main` prints `0 0`; `grep packVersion .claude/agentic.config.json` prints 29 (done) |
| C6.2 | Agent teams on (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, tracked `.claude/settings.json`) | stages 1 to 14 | present in `.claude/settings.json` env (done) |
| C6.3 | `uv sync --locked`; baseline regression | stages 4 to 11 | mypy clean (45 files), ruff clean, 668 passed (done) |
| C6.4 | Azure sign-in, subscription "Visual Studio Enterprise Subscription" | stages 12, 13 | `az account show` Enabled (done) |
| C6.5 | Key Vault `kv-aveto-ask-gp` holds secret `anthropic-api-key` | stages 12, 13 | `az keyvault secret list` prints the name; the value is never read (done) |
| C6.6 | Rollback target: active revision `ca-aveto-ask--0000008`, image `aveto-ask:d067b9a95ac6`, kill switch off, prices 2000/10000 | stages 12, 13 | `az containerapp show` and `revision list` (done) |
| C6.7 | Event log writing to `/Users/gopalpatwa/opt/aveto-support/.claude/events/1dbb5af3-2658-4b6f-ab7a-5c8d7e249de5.jsonl` | every stage | `events-verify.mjs` prints "chain intact" |
| C6.8 | `axe-core` pinned in the scratchpad (C1.5) | stage 8 | installed and run once on the current page in the built-in browser |
| C6.9 | Built-in browser reaches a local run of the service | stage 8 | a local `uvicorn` run answers `GET /` in the browser pane, no permission prompt |

## 7. Depth (may not be lowered)
- **C7.1** Security Review: standard (new routes, counts, receipts, scorecard, page JS and the unchanged headers)
- **C7.2** Release Gate tier: 3

## 8. Outcomes decided now
- **C8.1 If a pre-registered check fails:** before the deploy, a failed check or gate (including any C1.4 bar) means no deploy, revision `ca-aveto-ask--0000008` keeps serving, a close-out is written, the run stops. After the deploy, if the new revision fails the live checks on behaviour (an answer or refusal different from `retrieve`'s, question text in a log table, a kill switch that does not take), or the rollback rehearsal fails (the previous page does not serve, `/health` does not answer, or the roll forward does not restore the new revision), the run keeps or restores the previous revision serving (deploy of image `d067b9a95ac6`, or the kill switch on if that fails), reports, and stops; the release fails. Timings are reported as measured and are not a failure by themselves.
- **C8.2 At the end of a passing run:** push `claude/interesting-shannon-67bff6` to origin and open a pull request into `main` with `END_REVIEW.md` linked; never merge (the owner merges; the owner runs the Codex review on the pull request).
- **C8.3 Irreversible actions allowed (rules 1 to 3):** in resource group `rg-aveto-ask` only: build and push one new image from the worktree root with `az acr build -r acravetoaskgp`; deploy the repository's `infra/main.bicep` with `az deployment group create -g rg-aveto-ask` (`deployApp=true`, `killSwitch=off` set explicitly, the existing price and cap values unchanged) three times at most for the release: (1) the new image tag, (2) the rollback rehearsal, which deploys `imageTag=d067b9a95ac6` (a new revision of the previous image, as `docs/runbooks/public-ask.md` section 2 says), (3) the roll forward to the new image tag; plus the same command with `killSwitch=on` only if C8.1 requires it. No other resource is added or removed; deleting any resource is not allowed. The branch push and pull request in C8.2. The Charter's rollback timing for the release gate is measured from the command to a healthy `/health` on the previous image.
- **C8.4 Human review of a Low-risk change at the end:** review
- **C8.5 Owner positions recorded by this Charter:** the live questions are sent through the real limits, no bypass; their spend counts against C2 as context and against the service's own day share as money; the $10 console limit is unchanged.

## 9. Stops (the only reasons the run asks)
1. An action not covered by a line above (a new model, processor, data, file, invariant, or irreversible action).
2. Spend above the hard cap (C2.3).
3. A credential is needed (agents never handle credentials), including an expired `az login`.
4. Lowering a depth in section 7.
5. A change to this Charter (an amendment is a new approval of a new hash).

## 10. Notices (sent, never asked)
A push notification at each stage boundary with two lines: the stage, its result
and the spend. The full record stays in `runs/polished-chat-experience/`.
