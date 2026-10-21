# Slice plan — public-ask-the-docs

> Orchestrator, 2026-10-20. **Proposed; confirmed with the Charter.** Units: peak context summed per spawn.
> Worktree `.claude/worktrees/public-ask-the-docs`, branch `claude/public-ask-the-docs`, cut from `main` at 2919c87 (pack v26; `main` level with `origin/main`). Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (absolute). Baseline on 2919c87: mypy clean, ruff clean, `pytest` 425 passed, 12 deselected.

## Outcome (one line)
A public page served by a small HTTP service on Azure Container Apps answers a visitor's question with either the verbatim passages `retrieve` shows (when the answerability judge, called through the Anthropic API, says ANSWERABLE) or `no confident match`, under hard cost and abuse limits, and is scored once on a pre-registered 20-question gate.

## Success criteria
`intent.md` "Done means", by reference, not restated. Tier 3 Release Gate. The pre-registered gate's two bars as fixed in the intent: all 10 non-answerable and hostile questions show no passage; at least 8 of 10 answerable get the right passages.

## Owner decisions at intake (2026-10-20, in this session, answers to four questions)
- **INV-5:** "Grant bounded INV-5 change (Recommended)". The intent's table said INV-5 unchanged; the service sends the question and passages to Anthropic, which INV-5 as written forbids. The Charter's C5.2 bounds the change.
- **Azure:** "eastus2, Key Vault (Recommended)": resource group `rg-aveto-ask` in eastus2, subscription "Visual Studio Enterprise Subscription"; the owner creates the group, the Key Vault `kv-aveto-ask-gp` and the secret `anthropic-api-key` before the run (commands in the Charter review message); the run checks the secret by name only.
- **Gate scoring:** "Through real limits (Recommended)": no bypass; batches of at most 10 at least one hour apart; when the day's spend share would run out, scoring continues the next day; all QA, verification and gate spend counts against the caps.
- **Gate set:** "~/opt/aveto-gates/ (Recommended)": `/Users/gopalpatwa/opt/aveto-gates/public-gate-1.toml`, sha256 `7eb4f588567d5b6fccea6dc59e2874f0d124777c9bde040c4e3a6de94786064f`. Setup checks its hash only; no builder role is given the path; it enters the repo only after the method freezes at stage 16, in stage 18.

## Non-goals
Generated answers; multi-turn chat; GitHub intake or posting; visitor accounts or sign-in; a custom domain; changing retrieval, ranking, the judge prompt `answerability-judge-v1` or the corpus at its pinned commit; the aveto.dev link (a playbook-repo change after the run, on the owner's word); the drafting step (`intents/draft-replies-attended.md`).

## Constraints from `.agentic/`
INV-1 and INV-3 unchanged. INV-2 unchanged. INV-4 and INV-5 change only within Charter C5.1 and C5.2. Every word shown to a visitor is copied from the docs. Python 3.12, uv; FastAPI is the decided stack (PROJECT_CONTEXT); new runtime dependencies are limited to what the Architect names in the tech spec and Security reviews (expected: `fastapi`, `uvicorn`, `anthropic`). Agents never handle a credential: the API key exists only in Key Vault and in the running container. The attended `/aveto-judge` path keeps working; the offline commands stay offline.

## Stages (tier 3; Stakes tick real user data, money, irreversible, safety control and UI, so the full chain runs)

| # | Stage | Owner | Depth | Environment | Est. |
|---|-------|-------|-------|-------------|------|
| 1 | Scope review: confirm size, stage list, skip of Market Research (optional stage; problem stated by the owner) | Engineering Manager | standard | default | 100k |
| 2 | PRD | Product Manager | standard | default | 70k |
| 3 | Feature spec: visitor journeys, edge cases (limits hit, paused, kill switch, errors), accessibility | UX Researcher | standard | default | 70k |
| 4 | UX spec for the one page: layout, states, exact copy | UI Designer | standard | default | 70k |
| 5 | Tech spec: service surface, Anthropic adapter reusing the verdict-only parser, limits and their fail-closed order, logging contract, kill switch, image with pinned models and index, Bicep for Container Apps + ACR + Log Analytics + managed identity reading Key Vault, cost model, the exact bounds for INV-4/INV-5 words, confirmation of the API's default effort; two passes | Software Architect | standard | default | 190k |
| 6 | AI risk tier for a public, unattended verdict model; eval obligations | AI Governance | standard | default | 70k |
| 7 | Processors (Anthropic Commercial Terms with DPA by reference; Azure), data map, 7-day abuse-log retention, no question stored | Compliance Reviewer (Data Governance folded in, reason recorded) | standard | default | 90k |
| 8 | Service, limits, logging, kill switch, tests (incl. byte-identical passages and no-question-in-logs) | Backend Architect | standard | default | 180k |
| 9 | Anthropic API judge adapter: same prompt, no tools, verdict-only parser; tests with a fake client; no live call | AI Engineer | standard | default | 100k |
| 10 | Public page served by the service | Frontend Developer | standard | default | 90k |
| 11 | Infrastructure as code (Bicep) and image build definition; `az deployment group what-if` only, no create | Cloud Deployment | standard | default | 130k |
| 12 | Review layer: `/code-review` at `high` against `main`, `REVIEW.md` as rules, risk tier from the diff; findings to the author role, three rounds at most | Orchestrator | high | default | 60k |
| 13 | QA evidence on the final tree (offline; live API not called) | QA Evidence | standard | default | 130k |
| 14 | Security Review: hostile questions, input handling, what the API receives, key exposure, rate-limit bypass; adversarial check of the INV-4/INV-5 words against C5.1/C5.2 | Security & Privacy | **adversarial** | default | 190k |
| 15 | Docs: README, CURRENT_MVP_STATUS, ARCHITECTURE, runbook, SAFETY_INVARIANTS words (written by the Tech Writer from the Architect's bounds so the reviewer in 14 is a different model) | Tech Writer | standard | default | 70k |
| 16 | Release Gate tier 3 (method frozen here; `charter-check` re-run and saved for the Release Manager) | Release Manager | standard | default | 170k |
| 17 | Deploy to `rg-aveto-ask` (Charter C8.3); rollback ready | Cloud Deployment | standard | default | 80k |
| 18 | Production verification of the live service, then the gate set committed (hash checked) and scored once through it, under the real limits | Production Verification | standard | default | 100k |
| 19 | Post-launch learning; `trace.json`, `END_REVIEW.md`, push, pull request (Charter C8.2) | Post-Launch Learning, Orchestrator | standard | default | 50k |

Estimated sum 2,000k; **plan total 2.0M**. Ceiling proposed at 3.0M (1.5×, adversarial Security and a model in the product path, per `RUN_ECONOMICS.md` §2); hard cap 3.6M. The intent recommended 1.8M / 2.4M / 3.0M; the stage sum above exceeds 1.8M, and the last tier 3 run in this repo ran at 145% of plan.
Skipped on purpose: Market Research (optional; the owner stated the problem and users in the intent), FinOps as its own stage (the cost model is in the Architect's spec and checked by Security), Data Governance as its own stage (folded into stage 7). Gates do not compress; none is dropped. No `fresh-load` stage.

Order and gates: 1 → 2 → 3 → 4 → 5 → (6, 7) → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19. A failed gate sends the slice back per `FAILURE_LOOP.md` (two retries per stage, then escalate).

## Gated actions (scan of `HUMAN_APPROVAL_RULES.md`)
- Rule 3 (deploy): stage 17, Charter C8.3; the push and pull request, C8.2.
- Rule 4 (safety control): INV-4 and INV-5 words, Charter C5.1 and C5.2.
- Rule 5 (model in a deterministic path, real client): the judge at runtime, Charter C3.1.
- Rule 6 (processor): Anthropic API, Microsoft Azure, Charter C4.1 and C4.2.
- Rules 1 and 2: none (nothing sent on anyone's behalf; no destructive change to shared state outside the named resource group).

## Prerequisites (setup phase; every row has a dry run before the first stage)

| id | What | Why | Dry run | Result |
|---|---|---|---|---|
| P1 | Pack v26 on `main`; branch cut from `main` at 2919c87 | every stage | `grep packVersion .claude/agentic.config.json` prints 26 in the worktree | done 2026-10-20: 26 |
| P2 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | stages 1 to 19 | `env` shows it set | done: set |
| P3 | No permission prompt: the driving session runs in bypass-permissions mode (Charter C6.P); no allow rules written | every stage | a shell command runs with no prompt | done |
| P4 | `uv sync --locked` in the worktree | 8 to 13 | mypy, ruff, pytest | done: clean, 425 passed |
| P5 | Azure sign-in | 11, 17, 18 | `az account show` → "Visual Studio Enterprise Subscription", Enabled; providers Microsoft.App, ContainerRegistry, OperationalInsights, KeyVault, ManagedIdentity Registered | done |
| P6 | Owner creates `rg-aveto-ask`, `kv-aveto-ask-gp` and secret `anthropic-api-key` | 17, 18 | `az keyvault secret list --vault-name kv-aveto-ask-gp --query "[].name" -o tsv` prints `anthropic-api-key` (names only; the value is never read) | pending the owner |
| P7 | Anthropic console monthly limit $10 | 17, 18 | owner's statement in this session (an agent cannot see the console) | pending the owner |
| P8 | Gate set in place, hash matches | 18 | `shasum -a 256 /Users/gopalpatwa/opt/aveto-gates/public-gate-1.toml` prints `7eb4f588…064f` | pending the support session |
| P9 | `/code-review` skill available | 12 | listed in the session's skills | done: listed |
| P10 | Image built remotely with `az acr build` (no local Docker needed); deploy with `az deployment group create` (no `containerapp` CLI extension needed) | 11, 17 | `az acr build --help` and `az deployment group what-if --help` run | done in setup |
| P11 | Visible symlink to the worktree for the owner | owner's reading | `ls -l /Users/gopalpatwa/opt/aveto-support/public-ask-the-docs` resolves | done in setup |
