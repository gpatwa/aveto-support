# Slice plan — result-page-clarity

> Orchestrator, 2026-10-27. **Proposed; confirmed with the Charter.** Units: peak context summed per spawn.
> Worktree `.claude/worktrees/objective-kapitsa-83d3ae`, branch `claude/objective-kapitsa-83d3ae`, at `main` 6ab5548 (pack v30 installed; 0 commits behind `main`, 0 ahead, checked 2026-10-27 with `git rev-list --left-right --count main...HEAD`). Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (absolute; the repo's relative path points nowhere from a worktree). Intent: `runs/result-page-clarity/intent.md`, a byte copy of `intents/result-page-clarity.md`, confirmed by the owner 2026-10-27 with every default accepted; its "Open questions" are none.

## Baseline read at setup (2026-10-27, on 6ab5548)
- mypy: clean (53 source files).
- pytest: **730 passed, 1 failed**, 12 deselected. The failure is `tests/test_service_pipeline.py::test_core_files_unchanged`: it pins the sha256 of `.claude/hooks/budget-guard.mjs` to the pre-v30 value (`798c12fa…9922`); the pack v30 install (a0af0f8) replaced the hook (now `222f3970…`). It is not caused by this slice.
- ruff: **1 error**, I001 (import order) in `runs/polished-chat-experience/13-live/tls-wrapper.py:1`, a recorded script of the last slice. Not caused by this slice.
- Both are red on `main` today. The intent does not mention them and "a red check is fixed first" (`CODE_REVIEW.md` §1). The Charter (C1.7) asks the owner to rule on the two small fixes, so that "mypy, ruff and tests pass" is a true bar.
- Live: active revision `ca-aveto-ask--0000011` (100% traffic; the rollback target); `az account show` Enabled (Visual Studio Enterprise Subscription). Key Vault read by the next slice's setup, not here (no deploy change to secrets).
- The last UI slice's peak-context total was 1,570k against a 1,000k plan (recorded in its `trace.json`). This plan's 400k is the owner's figure for a smaller change; the risk that it runs over is stated, and the ceiling and hard cap exist for it.

## Outcome (one line)
On a result page the result comes first (title and statement, question box, result, then "What to expect" and the suggestions), the page scrolls to it and focuses it so the heading lands in the top quarter of the screen at 1280×800 and 375×667, the home page and every string stay byte-identical, and answering is untouched; released under a rehearsed rollback.

## Success criteria
`intent.md` "Done means", by reference, not restated. Release Gate tier 3 with the rollback rehearsal as a release gate. Security Review smoke (and the review confirms there is no new route, no new input, no header change). Review layer tier Medium expected (product source and tests; the Orchestrator derives it from the diff). Quality bars are written into the Charter (C1.4) before any build and approved with its hash; no bar moves during the run.

## Non-goals
Any wording change (the privacy, limits and "What to expect" strings stay byte-identical; if the Architect thinks a string must change, the run stops: Charter section 9 item 1); multi-turn answers; an embedded panel (`frame-ancestors 'none'` stays); D1 (counters surviving a restart); the daily or monthly cap; new routes; the deferred `/warm` retry bound; any change under `aveto_support/`, `prompts/` or `.claude/`; any change under `.agentic/` except `.agentic/CURRENT_MVP_STATUS.md` (recorded figures only); the aveto.dev screenshots (a separate playbook commit with wording the owner approves).

## Constraints from `.agentic/`
INV-1 to INV-5 unchanged byte for byte (Charter C5.0). Python 3.12, uv, no new runtime dependency. Anthropic and Azure only. No third-party script, font or analytics on the service page; CSP stays `'self'`. No question text stored or logged. Agents never handle a credential. The offline commands stay offline; the default test suite makes no network call.

## Design notes the plan fixes now (the Architect decides the rest)
- **Two files carry the change.** `aveto_service/render.py` (the page template; `{above}`, `{try_block}`, the form and `{below}` are the pieces that move) and `aveto_service/static/enhance.js` plus `style.css` (focus and scroll after Ask). The Architect names the exact edits; any server-side change is to ordering only, and the home page's output must be byte-equal to `main`'s.
- **Scrolling and focus.** The result keeps `tabindex="-1"` and receives focus; the scroll must put the heading at the top of the viewport, honour `prefers-reduced-motion` (no animation when the visitor asks for none), and work with JavaScript off (the form posts to `/ask#result` and redirects to `/result/<token>#result`).
- **Measured, not asserted.** The Orchestrator runs the browser checks (the build roles have no browser tools): before and after figures for the result heading's top, at 1280×800 and 375×667, for one answered and one refused question on the local build (a stand-in judge, as in the last slice; the stand-in is named in the record).
- **Accessibility check.** `axe-core`, one pinned version, installed only into the session scratch directory (Charter C1.5); never added to the repository, the lockfile or the image.

## Stages (tier 3; Stakes tick real user data, irreversible, UI)

Compressed on purpose: no Engineering Manager scope stage (the intent already fixes scope, non-goals and the file area), no UI Designer stage (the intent fixes the order and the behaviour; the Architect writes the layout in the tech spec), no separate backend stage (no data, route or limit changes). Gates do not compress; none is dropped.

| # | Stage | Owner | Depth | Environment | Est. |
|---|-------|-------|-------|-------------|------|
| 1 | Tech spec: the exact reorder for a result page, home page unchanged, scroll and focus mechanism, every string listed and kept, the measurement method, fail-first tests named | Software Architect | standard | default | 40k |
| 2 | Build: fail-first tests (run on `main` first), then the reorder and the scroll and focus change; the two baseline fixes if the owner approves C1.7 | Frontend Developer | standard | default | 50k |
| 3 | Review layer: `/code-review` at `high` against `main`, `REVIEW.md` as rules, tier from the diff; findings to the writing role, three rounds at most | Orchestrator | high | default | 30k |
| 4 | Browser checks on a local run: before and after heading position, axe, 375 px, keyboard only, reading order | Orchestrator | standard | default | 40k |
| 5 | QA evidence on the final tree (offline), including "nothing about answering moves" (`git diff main -- aveto_support prompts .claude .agentic` empty except the pack install, none in this slice), the 39-case `/ask` golden file byte-equal, the headers and strings byte-identical | QA Evidence | standard | default | 40k |
| 6 | Security Review at smoke depth: no new route, no new input, no header change; confirm that | Security & Privacy | smoke | default | 25k |
| 7 | Docs: README, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md` with recorded figures only | Tech Writer | standard | default | 25k |
| 8 | Release Gate tier 3 (`charter-check` re-run and saved; event log verified and copied; rollback rehearsal is a gate) | Release Manager | standard | default | 40k |
| 9 | Deploy to `rg-aveto-ask` (C8.3): one `az acr build`, one Bicep deployment (new revision only); the command sheet and rollback first | Cloud Deployment, Orchestrator | standard | default | 35k |
| 10 | Rollback rehearsal (previous revision serves, `/health` answers, timed; roll forward; check again), live checks of the result position at both sizes on the deployed revision, verdict | Orchestrator, Production Verification | standard | default | 45k |
| 11 | Post-launch learning; `trace.json`, `END_REVIEW.md`, push, pull request (C8.2); STATE.md Status set to `done` when the pull request opens | Post-Launch Learning, Orchestrator | standard | default | 30k |

Estimated sum **400k; plan total 400k**. Ceiling 720k (about 90% of the owner's hard cap); hard cap **800k**, set by the owner as the one number (C2.3). No adversarial stage and no model proposal. No `fresh-load` stage.

Order and gates: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11. A failed gate sends the slice back per `FAILURE_LOOP.md` (two retries per stage, then escalate). The Orchestrator's own stages (3, 4, and the Orchestrator parts of 9, 10, 11) run in this session; their context is not counted in the peak-per-spawn sum, as in the last slice.

## Gated actions (scan of `HUMAN_APPROVAL_RULES.md`)
- Rule 3 (deploy): stage 9 (image build, new revision), stage 10 (activate the previous revision by Bicep, then roll forward), Charter C8.3; push and pull request, C8.2.
- Rule 5 (real model): stage 10 live checks send at most two questions (one answered, one refused, from spent eval sets) through the unchanged runtime judge, Charter C3.1.
- Rule 6 (processor): none new; Anthropic and Azure as already approved (Charter C4.0).
- Rule 4: none (no header change, no safety text; Charter C5.0).
- Rules 1 and 2: none.

## Prerequisites (setup phase; every row has a dry run before the first stage)

Dry runs marked *(after approval)* need a permission rule or a package download, so they run right after the Charter is approved and the C6.P rules are written, and before stage 1. Dry runs marked *(done)* ran before this plan was shown.

| id | What | Stage | Dry run |
|---|---|---|---|
| C6.P | Allow rules in the session project dir's `.claude/settings.local.json` (gitignored; exactly the Charter's list, including one `Agent(<role>)` rule per role in the stage table), written only after the Charter is approved, deleted after the pull request opens | every stage | each allowed read-only command run once in setup, no prompt *(after approval)*; `charter-check --plan` finds an `Agent(<role>)` rule for every role in the table *(done at drafting)* |
| C6.1 | Branch level with `main` 6ab5548, pack v30 | every stage | `git rev-list --left-right --count main...HEAD` prints `0 0`; `grep packVersion .claude/agentic.config.json` prints 30 *(done)* |
| C6.2 | Agent teams on | all | `.claude/settings.json` env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` *(done)* |
| C6.3 | `uv sync --locked`; baseline regression | stages 2 to 8 | mypy clean (53 files); pytest 730 passed, 1 failed; ruff 1 error: the two red items above, see C1.7 *(done)* |
| C6.4 | Azure sign-in | stages 9, 10 | `az account show` Enabled *(done)* |
| C6.5 | Rollback target: active revision `ca-aveto-ask--0000011` at 100% traffic; its image tag is read from `az containerapp show` and recorded in the deploy sheet | stages 9, 10 | `az containerapp revision list` prints it *(done)*; image tag read *(after approval)* |
| C6.6 | Event log writing for this session (`/Users/gopalpatwa/opt/aveto-support/.claude/events/88d804ad-ae70-4566-ac4b-186dbe5721e8.jsonl`) | every stage | `events-verify.mjs` prints "chain intact" *(after approval)* |
| C6.7 | Accessibility checker `axe-core`, pinned, in the scratch directory | stage 4 | installed and run once on the current page in the built-in browser *(after approval)* |
| C6.8 | Built-in browser reaches a local run of the service | stage 4 | a local `uvicorn` run answers `GET /` in the browser pane, no permission prompt *(after approval)* |
| C6.9 | Budget guard follows this worktree and the hard cap | stage 1 on | `STATE.md` carries `- **Hard cap:** 800k`; the first spawn raises no guard prompt *(after approval)* |
