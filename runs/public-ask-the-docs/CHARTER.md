# Charter: public-ask-the-docs

> The only human approval in this run. Approve it once, in your own words, naming this file and its sha256. After that the run proceeds to a finished result and asks nothing; it stops only for section 9.

## 1. Scope
- **C1.1 Intent:** `runs/public-ask-the-docs/intent.md`, sha256 `37a991ea2bc860a9d8463fa0c21a258b8ad2e52d4051eeb73ee246b2db0b2b49`
- **C1.2 Plan:** `runs/public-ask-the-docs/00-slice-plan.md`, sha256 `8ccaf00a32d3df67b916d16f744920a6c46c5fb43bca8709da77c239a1177908`
- **C1.3 Non-goals:** generated answers; multi-turn chat; GitHub intake or posting; visitor accounts or sign-in; a custom domain; changing retrieval, ranking, the judge prompt `answerability-judge-v1` or the corpus at its pinned commit; the aveto.dev link (a playbook-repo change after the run, on the owner's word); the drafting step.

## 2. Budget (unit: peak context summed per spawn)
- **C2.1 Plan total:** 2000k
- **C2.2 Ceiling:** 3000k. Above it the run continues and sends a notice.
- **C2.3 Hard cap:** 3600k. Above it the run stops. The run never raises it.

## 3. Models (rule 5)
- **C3.1** Answerability judge in the service: `claude-sonnet-5-5`, effort high (the request sends `high` explicitly if the Architect finds the API default is not high), the app at runtime via the Anthropic Messages API, no tools in the request, prompt `answerability-judge-v1` at its pinned sha256, the existing verdict-only parser.
- **C3.2** Orchestrator, Software Architect, Security & Privacy: `claude-opus-5-5`, effort high, the operator's session.
- **C3.3** AI Governance, Compliance Reviewer, QA Evidence, Release Manager: `claude-sonnet-5-5`, effort high, the operator's session.
- **C3.4** Engineering Manager, Product Manager, UX Researcher, UI Designer, Backend Architect, AI Engineer, Frontend Developer, Cloud Deployment, Tech Writer, Production Verification, Post-Launch Learning: `claude-sonnet-5-5`, effort medium, the operator's session.
- **C3.R Review rescore:** unchanged since the last rescore on 2026-10-17; the code review in this run is stated as unscored.

## 4. Data processors (rule 6)
- **C4.1** Anthropic (API, under its Commercial Terms, which incorporate its Data Processing Addendum by reference; the DPA text not read by an agent), receives per question exactly: the fixed judge prompt, the visitor's question (at most 500 characters) and the passages `retrieve` would show with their paths, headings and line ranges. No IP address, visitor identifier or visitor request header. Retention and training use per those terms, not verified by an agent.
- **C4.2** Microsoft Azure (the owner's subscription terms), receives: the container image, the Key Vault secret, the visitor's HTTPS request in transit through Container Apps ingress, and in Log Analytics only the service's abuse log lines (a hashed IP, a time and an outcome code, kept 7 days) and platform logs that carry no question text.

## 5. Safety controls (rule 4)
- **C5.1** `.agentic/SAFETY_INVARIANTS.md` INV-4: may replace the sentence "it runs only in the operator's own Claude Code session, and nothing in the program calls it" with words naming exactly two callers: the operator's session (unchanged) and the service's `POST /ask`, which calls the Anthropic Messages API with `claude-sonnet-5-5`, no tools in the request, prompt `answerability-judge-v1` at its pinned sha256 and the same verdict-only parser; may add the mapping of the service's JSON to outputs (a), (b) and (c); may add the names of new tests to its enforcement list. No other word removed or weakened.
- **C5.2** `.agentic/SAFETY_INVARIANTS.md` INV-5: may add one exception for the service alone: HTTPS POST to `api.anthropic.com` carrying only the data in C4.1, authenticated by the key the container reads from Key Vault; may add the names of new tests to its enforcement list. Every other sentence stays; `ingest`, `retrieve`, `eval`, `judge-input` and `judge-apply` stay as they are.
- **C5.3** INV-1, INV-2, INV-3: unchanged by this run; no word of them changes.
- **C5.4** `prompts/answerability-judge-v1.txt`, `.claude/agents/aveto-answerability-judge.md`, the skills `/aveto-judge` and `/aveto-judge-seen`, and `.claude/hooks/`: byte-identical to 2919c87.

## 6. Prerequisites (set once in the setup phase, each with its dry run)
| id | What | Why | Dry run that proves it |
|---|---|---|---|
| C6.P | No allow rules: `.claude/settings.local.json` is not created, because the driving session runs in bypass-permissions mode, set by the owner; role tool limits and the repo's hooks still apply | every stage | a shell command ran in setup with no prompt (done) |
| C6.1 | Pack v26, branch cut from `main` at 2919c87 | every stage | `grep packVersion .claude/agentic.config.json` prints 26 (done) |
| C6.2 | Agent teams on (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | stages 1 to 19 | `env` shows it (done) |
| C6.3 | `uv sync --locked` in the worktree | stages 8 to 13 | mypy and ruff clean, 425 passed (done) |
| C6.4 | Azure sign-in, subscription "Visual Studio Enterprise Subscription" | stages 11, 17, 18 | `az account show` Enabled; five resource providers Registered (done) |
| C6.5 | Owner created `rg-aveto-ask` (eastus2), Key Vault `kv-aveto-ask-gp`, secret `anthropic-api-key` | stages 17, 18 | `az keyvault secret list --vault-name kv-aveto-ask-gp --query "[].name" -o tsv` prints `anthropic-api-key`; the value is never read |
| C6.6 | Anthropic console monthly spend limit set to $10 | stages 17, 18 | the owner's statement in this session |
| C6.7 | Gate set at `/Users/gopalpatwa/opt/aveto-gates/public-gate-1.toml` | stage 18 | `shasum -a 256` prints `7eb4f588567d5b6fccea6dc59e2874f0d124777c9bde040c4e3a6de94786064f`; contents not read before stage 18 |
| C6.8 | Visible symlink `/Users/gopalpatwa/opt/aveto-support/public-ask-the-docs` to the worktree | owner's reading | `ls -l` resolves (done) |

## 7. Depth (may not be lowered)
- **C7.1** Security Review: adversarial
- **C7.2** Release Gate tier: 3

## 8. Outcomes decided now
- **C8.1 If a pre-registered check fails:** a failed Release Gate before the deploy means no deploy, a close-out, stop. A missed gate bar after the deploy means the kill switch is set on (the service answers nothing and calls no model), the miss is reported as a miss, the run stops; the service is turned back on only on the owner's word at the end review.
- **C8.2 At the end of a passing run:** push `claude/public-ask-the-docs` to origin and open a pull request into `main` with `END_REVIEW.md` linked; never merge.
- **C8.3 Irreversible actions allowed (rules 1 to 3):** in resource group `rg-aveto-ask` (eastus2) only: create one Azure Container Registry, one Log Analytics workspace, one Container Apps environment, one Container App (scale to zero, external HTTPS ingress) and one user-assigned managed identity; assign that identity `Key Vault Secrets User` on `kv-aveto-ask-gp` and `AcrPull` on that registry; build and push the image from the branch with `az acr build`; deploy the Bicep in the repo with `az deployment group create`; set the kill switch on or off. Rollback: activate the previous revision, or set the kill switch on; removing the resources is done only on the owner's word. The branch push and pull request in C8.2.
- **C8.4 Human review of a Low-risk change at the end:** review
- **C8.5 Owner positions recorded by this Charter:** the gate is scored through the real limits with no bypass, in batches of at most 10 at least one hour apart, continuing the next day when the day's spend share runs out; all QA, verification and gate spend counts against the caps.

## 9. Stops (the only reasons the run asks)
1. An action not covered by a line above (a new model, processor, data, file, invariant, or irreversible action).
2. Spend above the hard cap (C2.3).
3. A credential is needed (agents never handle credentials).
4. Lowering a depth in section 7.
5. A change to this Charter (an amendment is a new approval of a new hash).

## 10. Notices (sent, never asked)
A push notification at each stage boundary with two lines: the stage, its result and the spend. The full record stays in `runs/public-ask-the-docs/`.
