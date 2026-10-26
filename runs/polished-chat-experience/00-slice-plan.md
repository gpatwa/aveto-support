# Slice plan — polished-chat-experience

> Orchestrator, 2026-10-26. **Proposed; confirmed with the Charter.** Units: peak context summed per spawn.
> Worktree `.claude/worktrees/interesting-shannon-67bff6`, branch `claude/interesting-shannon-67bff6`, at `main` 32e54a6 (pack v29 installed; 0 commits behind `main`, 0 ahead, checked 2026-10-26). Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (absolute; the repo's relative path points nowhere from a worktree). Baseline on 32e54a6: mypy clean (45 files), ruff clean, `pytest` **668 passed**, 12 deselected.

## Live state read at setup (2026-10-26)
Active revision `ca-aveto-ask--0000008` (100% traffic; the rollback target); `az account show` succeeds (Visual Studio Enterprise Subscription); Key Vault `kv-aveto-ask-gp` lists `anthropic-api-key` (value never read).

## Outcome (one line)
The live ask-the-docs service becomes a polished reference product (answer and refusal cards, suggested questions, honest waiting, resting state, receipts drawer, recorded-figures scorecard, content-free counts) with answering behaviour byte-identical, released under a rehearsed rollback, and the build shown through the scorecard.

## Success criteria
`intent.md` "Done means", by reference, not restated. Release Gate tier 3. Security Review standard. Review layer tier High. Quality bars are written into the Charter (C1.4) before any build and approved with its hash; the Architect (stage 3) states how each is measured and may propose a stricter figure, which takes effect only through a new Charter hash (stop 5). No bar moves during the run.

## Non-goals
Option (b) embedding and any change to `frame-ancestors 'none'` or another header; multi-turn conversation; answers written by a model; accounts or login; a second product; changing the daily or monthly cap; decision D1 (counters surviving a restart); any change under `aveto_support/`, `prompts/`, `.claude/` or `.agentic/` except the status line in `.agentic/CURRENT_MVP_STATUS.md` that Done means names; the page's privacy or Article 50 wording; the aveto.dev change (a separate playbook commit, wording first approved by the owner).

## Constraints from `.agentic/`
INV-1 to INV-5 unchanged byte for byte (Charter C5.0). Python 3.12, uv, no new runtime dependency. Anthropic and Azure only. No third-party script, font or analytics on the service page; CSP stays `'self'`. No question text stored or logged; counts computed in the service. Agents never handle a credential. The offline commands stay offline; the default test suite makes no network call.

## Design notes the plan fixes now (the Architect decides the rest)
- **Scorecard figures.** The image is built once (C8.3). Figures known before the build (test count, local timings, accessibility and mobile checks, open findings) go into a committed figures file the page reads; figures only the service can know (its own cold-start time, warm latency, counts) it reports from its own measurements; live external timings and the rollback timing go to the run record and the pull request, and enter the scorecard only through a later change. A line with no record behind it is not shown. The Codex review enters the scorecard only after the owner records it.
- **Accessibility check.** `axe-core`, one pinned version, installed only into the session scratch directory (Charter C1.5), run by the Orchestrator through the built-in browser (the build roles have no browser); never added to the repo, the lockfile or the image.
- **Browser checks** (375 px width, keyboard-only, axe) are run by the Orchestrator in stage 8, because only the Orchestrator has the browser tools.

## Stages (tier 3; Stakes tick real user data, irreversible, UI)

| # | Stage | Owner | Depth | Environment | Est. |
|---|-------|-------|-------|-------------|------|
| 1 | Scope review: size, compressed stage list, any file the intent forgot | Engineering Manager | standard | default | 40k |
| 2 | UX spec: the eight items, states (waiting, answer, refusal, resting, error), copy deck (no privacy/Article 50 change), 375 px and keyboard behaviour | UI Designer | standard | default | 90k |
| 3 | Tech spec: embedding decision (a) restated with reasons; quality-bar figures proposed; routes and data (counts, receipts, warm-up, scorecard figures file); fail-first tests named (refusal card has no model text; resting state at the cap; counts hold no question text; receipts drawer shows only held data; answer card text is in a listed source); suggested questions chosen from spent eval sets (three answered, one refused); deploy sheet | Software Architect | standard | default | 90k |
| 4 | Backend: counts, receipts data, warm-up, resting-state data, scorecard figures reader; fail-first tests run on 32e54a6 first | Backend Architect | standard | default | 110k |
| 5 | Frontend: page, cards, drawer, scorecard page, CSS and JS under `'self'`; fail-first tests | Frontend Developer | standard | default | 140k |
| 6 | Review layer: `/code-review` at `high` against `main`, `REVIEW.md` as rules, tier from the diff; findings to the writing role, three rounds at most | Orchestrator | high | default | 50k |
| 7 | QA evidence on the final tree (offline), including "answering is byte-identical" (`git diff main -- aveto_support prompts .claude .agentic` empty except the pack install) | QA Evidence | standard | default | 70k |
| 8 | Browser checks on a local run: axe, 375 px, keyboard only, cold and warm timing as measured | Orchestrator | standard | default | 40k |
| 9 | Security Review (limited to the new routes, counts, receipts, scorecard, page JS, headers unchanged) | Security & Privacy | standard | default | 70k |
| 10 | Docs: README, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md` with recorded figures only | Tech Writer | standard | default | 50k |
| 11 | Release Gate tier 3 (`charter-check` re-run and saved; event log verified and copied) | Release Manager | standard | default | 70k |
| 12 | Deploy to `rg-aveto-ask` (C8.3): one `az acr build`, one Bicep deployment (new revision only); the command sheet and rollback first | Cloud Deployment, Orchestrator | standard | default | 60k |
| 13 | Rollback rehearsal (previous revision serves, `/health` answers, timed; roll forward; check again), live checks, cold and warm timing; verdict | Orchestrator, Production Verification | standard | default | 70k |
| 14 | Post-launch learning; `trace.json`, `END_REVIEW.md`, push, pull request (C8.2) | Post-Launch Learning, Orchestrator | standard | default | 50k |

Estimated sum 1,000k; **plan total 1,000k**. Ceiling proposed at 1,300k (1.3×; no adversarial stage and no model proposal, per `RUN_ECONOMICS.md` §2); hard cap 2,000k, set by the owner.
Skipped on purpose: Market Research, PRD, UX Researcher (the intent states the problem, users and Done means), AI Governance (no model or prompt change), Compliance and Data Governance (no new processor or data; counts hold no content), Analytics Engineer and FinOps (counts and cost figures sit with the Architect and Backend). Gates do not compress; none is dropped. No `fresh-load` stage.

Order and gates: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14. A failed gate sends the slice back per `FAILURE_LOOP.md` (two retries per stage, then escalate).

## Gated actions (scan of `HUMAN_APPROVAL_RULES.md`)
- Rule 3 (deploy): stage 12 (image build, new revision), stage 13 (activate previous revision, then roll forward), Charter C8.3; push and pull request, C8.2.
- Rule 5 (real model): stage 13 live checks send a few questions through the unchanged runtime judge, Charter C3.1.
- Rule 6 (processor): none new; Anthropic and Azure as already approved (Charter C4.0).
- Rule 4: none (option (a): no header change; Charter C5.0).
- Rules 1 and 2: none.

## Prerequisites (setup phase; every row has a dry run before the first stage)

| id | What | Stage | Dry run |
|---|---|---|---|
| C6.P | Allow rules in `.claude/settings.local.json` (gitignored; main checkout, the session project dir), including one `Agent(<role>)` rule per role in the stage table; written only after the Charter is approved, deleted after the pull request opens | every stage | each allowed command run once in setup, no prompt |
| C6.1 | Branch level with `main` 32e54a6, pack v29 | every stage | `git rev-list --left-right --count HEAD...main` prints `0 0`; `grep packVersion .claude/agentic.config.json` prints 29 (done) |
| C6.2 | Agent teams on | stages 1 to 14 | `.claude/settings.json` env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (done) |
| C6.3 | `uv sync --locked`; baseline regression | stages 4 to 11 | mypy and ruff clean; 668 passed (done) |
| C6.4 | Azure sign-in | stages 12, 13 | `az account show` Enabled (done) |
| C6.5 | Key Vault secret exists | stages 12, 13 | `az keyvault secret list` lists `anthropic-api-key`; value never read (done) |
| C6.6 | Rollback target: active revision `ca-aveto-ask--0000008`, image `aveto-ask:d067b9a95ac6` (the rollback is a Bicep deployment with that `imageTag`, as the runbook section 2 says) | stages 12, 13 | `az containerapp revision list` (done) |
| C6.7 | Event log writing | every stage | `events-verify.mjs` prints "chain intact" |
| C6.8 | Accessibility checker `axe-core`, pinned, in the scratch directory | stage 8 | installed and run once on the current page in the built-in browser |
| C6.9 | Built-in browser reaches the local service on localhost | stage 8 | a local `uvicorn` run answers `GET /` in the browser pane |
