# 06 Label review of the fifth gate set (docs-answerability-2, stage 6)

- **Reviewer:** fresh QA Evidence spawn, depth adversarial on the unanswerable labels, standard on the answerable ones.
- **Files reviewed (committed b692ffc, method frozen at bca0e40):** `evals/retrieval-heldout-5.toml`, `evals/retrieval-heldout-5-reserves.toml`.
- **Corpus:** the 123 `.md` files of `gpatwa/agentic-sdlc-playbook` at `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`, selected by `docs-source.toml` (checked: `git archive` of the allow-list at that commit yields exactly 123 `.md` files; `.mjs` files under `execution/` are not corpus). All reads and greps were of an extract of that commit, never the working tree. Line numbers below are lines of the file at the pinned commit.
- **Not done, by rule:** no `retrieve`, `eval`, `judge-input`, `judge-apply`, `tools.judge_run`, index or judge spawn was run on any question in either file. No eval file was edited. Stage 5 result files were not read.
- **Status of this document:** complete (sections 0 to 7).

## 0. Summary

**Result: the fifth set is usable. One unanswerable label is contestable (gu09, AMBIGUOUS) and the owner should decide whether to swap it for reserve gr02; ten answerable labels are too narrow and get additions only. No unanswerable question was found answerable. The slice does not stop.**

| Measure | Result |
|---|---|
| Unanswerable, CONFIRMED UNANSWERABLE | **23 of 24** (gu01-gu08, gu10-gu24) |
| Unanswerable, ANSWERABLE-IN-DOCS | **0** |
| Unanswerable, AMBIGUOUS | **1** (gu09; recommendation: replace with gr02) |
| Hard negatives tagged | 18 of 18 present (gu01-gu14, gu19, gu22, gu23, gu24); trap named for every one; all real, gu23 the mildest |
| Unanswerable questions carrying `sources` or `where` | 0 |
| Reserves (6) | gr01, gr02, gr03 CONFIRMED; gr04 AMBIGUOUS (do not use); gr05, gr06 answerable (cannot replace an unanswerable question) |
| Answerable questions, sources all exist and are in the corpus | 24 of 24 |
| Answerable questions where a listed source does not state the answer | 1 source (`docs/VALIDATION_MATRIX.md` for g08; weakest, keep or drop is the owner's call) |
| Answerable questions needing additions | 10 of 24 (g01, g02, g07, g08, g09, g14, g17, g18, g19, g21), 13 files added, 0 dropped |
| Answerable questions that are really unanswerable or ambiguous | 0 |
| Seen-set question repeated | none; near-topic cases listed in section 3 |
| Format | all single plain lines; g01 is the first question with embedded double quotes (not rejected by `normalise_question`) |
| Unanswerable count and hard-negative count after the recommended swap | 24 and 18 (rule 9 minimum holds) |

Judge risks to disclose (the key stays; these are where a lenient judge could say ANSWERABLE and be scored as a miss): gu03, gu08, gu10 (medium: the docs describe a different tool, scope or format, so "no" can be inferred); gu05, gu13, gu19, gr02, gr03 (low to medium).

The finding with most consequence for the answerable side: **g09**. `docs/VALIDATION_MATRIX.md:90-94` says `install.mjs --greenfield` scaffolds a stub `.agentic/`, which sits beside `docs/GETTING_STARTED.md:72-73,180` ("no scaffolding tool"). Both answer the question, in different ways.

Exact proposed edits are in section 6. Nothing was applied.


## 1. Structural checks

- `evals/retrieval-heldout-5.toml`: 48 questions, parses as TOML, ids g01..g24 and gu01..gu24, no duplicates; 24 with sources and `where`, 24 with `answerable = false`; `pinned_commit` equals the corpus commit in `docs-source.toml`.
- Hard negatives: 18 with `hard_negative = true` (gu01-gu14, gu19, gu22, gu23, gu24); 6 unanswerable without the tag (gu15-gu18, gu20, gu21).
- `evals/retrieval-heldout-5-reserves.toml`: 6 questions, ids gr01..gr06; 4 unanswerable (gr01 plain; gr02, gr03, gr04 hard negatives) and 2 answerable (gr05, gr06). Note for the owner: of the six reserves only four can replace an unanswerable question, and only three of those are hard negatives.
- Corpus: 123 `.md` files at the pinned commit from the allow-list in `docs-source.toml`; `.mjs`, `.json` and `.sh` files are not corpus. Statements in the docs that live only in a non-corpus file (for example `execution/package.json` engines, `docs/BACKLOG.md`) cannot answer a question and were not relied on.
- Rule 9 asks each hard negative to be tagged with the file it overlaps and the shared terms. The committed file carries no such tag. This review supplies it per question in section 2 ("Hard-negative claim"). No edit to the eval file is proposed for it, because the loader's schema is not mine to change; the Orchestrator can copy these lines into the run record.
- Not verifiable here: the header's provenance claims (regenerated from a generator script; recorded sha256 `9cca11aeb4cd66eb` of the base) and its count of earlier-set source reuse (21 of 24). Reply 2 is treated as data; reuse is not flagged.


## 2. Unanswerable questions (attacked hardest)

Standard used for the verdict. CONFIRMED UNANSWERABLE means no passage in the corpus states, or necessarily entails, the answer. ANSWERABLE-IN-DOCS means a passage answers it fully or substantially (cite path:line; replace the question). AMBIGUOUS means the docs give a partial answer that a reasonable reader could call an answer. Where the docs only describe something different from what the question asks about (so "no" could be inferred from silence), that is recorded as a **judge risk** and is not by itself a reason to call the label wrong: the docs never claim the description is exhaustive.

Hard-negative check: for each `hard_negative = true` the topical or lexical trap is named. Pack rule 9 asks each hard negative to be tagged with the file it overlaps and the shared terms; the committed file carries no such tag, so this review supplies it (see section 6, proposed edit E0).

### gu01 "Which cloud region does the Aveto website run in?" (hard_negative = true)

- **Searched:** region, data cent*, availability zone, AWS, GCP, Azure, CDN, edge, anycast, geograph*, hosted/hosting/served from, Cloudflare, aveto.dev, website, public site.
- **Nearest passage:** `docs/DEPLOYMENT.md:3` "`aveto.dev` is served from Cloudflare Pages, deployed by `.github/workflows/deploy-site.yml`" and the whole file (Cloudflare Pages project, token, rollback). `README.md:143-148` repeats the `site/` layout and "CSP + security headers for Cloudflare Pages". No region, zone, edge location or data-centre statement anywhere. `agents/cloud-deployment.md` is Azure and says nothing about the Aveto site; `agents/data-governance.md:20` and `templates/DATA_GOVERNANCE_REVIEW_TEMPLATE.md:14` mention "region"/"residency" for a user's product, not this site.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real, strong.** Overlap file `docs/DEPLOYMENT.md` (also `README.md`); shared terms "Aveto website", "deployed", "Cloudflare Pages", "hosting". Second trap: `agents/cloud-deployment.md` ("cloud", "deploy").

### gu02 "What uptime does the Aveto website guarantee?" (hard_negative = true)

- **Searched:** uptime, SLA, availability, 99.x, nines, guarantee, status page, "Verify live".
- **Nearest passage:** `docs/DEPLOYMENT.md:14` and `:85-87` (post-deploy live verification, "HTTP 200 + expected content, 5 retries"; "a deploy is not 'done' because the command exited 0"). That is a deploy check, not an availability guarantee. `agents/sre.md:12,52,58` discuss SLOs/SLAs in general ("a product with uptime commitments", "Accepting a contractual SLA (PM + human own)"), not Aveto's site. `agents/production-verification.md:56` "not a generic uptime threshold".
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real.** Overlap `docs/DEPLOYMENT.md` (shared "Aveto website", "live", "verify") and `agents/sre.md` (shared "uptime", "SLA", "SLO", "guarantee").

### gu03 "Does the Security agent run penetration tests against my live site?" (hard_negative = true)

- **Searched:** penetration, pen test, pentest, DAST, red team, fuzz, vulnerability scan, exploit, offensive, "live site/system/environment/production", "against prod". Read `agents/security-privacy.md` and `prompts/security-review.md` in full.
- **Nearest passages:** `agents/security-privacy.md` defines the Security agent as a reviewer of the implementation diff, QA evidence and tech spec; its operating constraints are "Read the diff. Don't read the whole repo" and "Use grep over Read". It lists secrets, PII-in-logs, approval bypass, audit events, adapter boundary, CAPTCHA, agentic threats. `prompts/security-review.md` is the same. Traps: `templates/VENDOR_RISK_TEMPLATE.md:36` "Recent penetration test / audit?" (a question about a vendor); `docs/VALIDATION_MATRIX.md:24` "Red-team slices" (refusal tests of the pipeline, not pen tests); `agents/production-verification.md:27,80` "read-only against the live environment" (a different role, queries only).
- **Verdict: CONFIRMED UNANSWERABLE.** No passage mentions penetration testing by the Security agent, for or against.
- **Judge risk: medium.** The agent file describes a diff-review scope. A judge could reason "Security reads the diff, so it does not pen-test", an answer by inference. Nothing states it. The label holds under the standard above; the owner should know this is the most inference-prone of the agent-scope negatives.
- **Hard-negative claim: real.** Overlap `agents/security-privacy.md` (shared "Security", "agent") plus `templates/VENDOR_RISK_TEMPLATE.md` ("penetration test") and `agents/production-verification.md` ("live").

### gu04 "How long does Aveto keep my run records before deleting them?" (hard_negative = true)

- **Searched:** retention, retain, purge, expire, prune, how long, TTL, days, archive, rotate, cleanup, older than, history, accumulate, forever, permanent. Read `execution/pack/protocols/RUN_INVENTORY.md`, `TELEMETRY.md`, the "Telemetry retention" block of `templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md:58-63`.
- **Nearest passages:** `agents/data-governance.md`, `agents/compliance-reviewer.md:24,35`, `templates/DATA_GOVERNANCE_REVIEW_TEMPLATE.md:32-34` and `templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md:58` ("Logs: <period> ..." a placeholder) are about retention policy for a user's product data. `execution/pack/protocols/RUN_INVENTORY.md` says `runs/INDEX.md` is the fleet view and `STATE.md` wins on disagreement; no deletion or expiry. Run records are files in the user's repo (`runs/<slice-id>/`); the docs never say Aveto keeps or deletes them for anyone.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real, strong.** Overlap `agents/data-governance.md` and `templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md` (shared "retention", "records"); `execution/pack/protocols/RUN_INVENTORY.md` and `SLICE_STATE.md` (shared "run", "records").

### gu05 "What time zone do scheduled runs use?" (hard_negative = true)

- **Searched:** time zone, timezone, UTC, GMT, cron, schedul*, nightly, recurring, periodic, unattended, cadence, weekly.
- **Nearest passages:** every timestamp the pack asks for is UTC (`execution/pack/protocols/SLICE_STATE.md:31,44,81`, `APPROVAL_PROTOCOL.md:42`, `docs/HUMAN_APPROVAL_RULES.md:144`, incident and change templates). `templates/CHANGE_REQUEST_TEMPLATE.md:32` "Maintenance window: <date/time + timezone, ...>" is a placeholder for a user's change. The only "scheduled" run is future work: `docs/PIPELINE_ANALYTICS.md:62-63` "Loop 2 — the external watch, scheduled and seeded with this output" listed under "Not yet", and `docs/PIPELINE_ANALYTICS.md:9-10` "Cadenced ... deferred". `docs/DEPLOYMENT.md:8` "What runs unattended" lists a CI deploy pipeline triggered by push or dispatch, not a schedule.
- **Verdict: CONFIRMED UNANSWERABLE.** The docs record timestamps in UTC but never say anything about when or in which zone a scheduled run executes; scheduled runs are described as not built.
- **Judge risk: low to medium.** A lenient reader may say "everything is UTC".
- **Hard-negative claim: real.** Overlap `execution/pack/protocols/SLICE_STATE.md` (shared "UTC", "run"), `docs/PIPELINE_ANALYTICS.md` ("scheduled", "Loop 2").

### gu06 "How do I send run alerts to PagerDuty?" (hard_negative = true)

- **Searched:** pagerduty, opsgenie, pager, alert, notify, notification, webhook, slack, email, routing.
- **Nearest passages:** `agents/sre.md:35,60-61` (alert wiring, symptom-based alerts mapped to runbook steps), `templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md:45-49` ("Alert routing ... Cause-based signals go to dashboards, not pagers. Routing: <where pages go ...>"), `templates/COST_BUDGET_TEMPLATE.md:38`, `agents/finops.md:13`. All concern alerts for a product's own service or spend, and leave routing to a placeholder. `PagerDuty` appears nowhere; the pipeline's own detectors flag outliers in a generated report (`docs/PIPELINE_ANALYTICS.md:40-44`) and send nothing.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real, strong.** Overlap `templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md` and `agents/sre.md` (shared "alert", "pagers", "routing", "on-call").

### gu07 "Can I connect Sentry for error tracking?" (hard_negative = true)

- **Searched:** sentry, error track*, exception, crash, APM, datadog, new relic, honeycomb, observability tool/platform/backend, OTLP, OpenTelemetry.
- **Nearest passages:** `execution/pack/protocols/TELEMETRY.md:36-37` "Any OTLP backend receives it — MLflow, Langfuse, Arize Phoenix, LangSmith and Laminar all accept OTLP, so no viewer needs building." It names backends for the pipeline's own telemetry and does not list or exclude Sentry, and it is not error tracking. `docs/GETTING_STARTED.md:183` (telemetry is self-reported unless OpenTelemetry is on). `agents/sre.md` and the observability template cover a product's observability without naming vendors.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real.** Overlap `execution/pack/protocols/TELEMETRY.md` (shared "connect", a named list of third-party tools) and `templates/OBSERVABILITY_BOOTSTRAP_TEMPLATE.md` ("error", "alert").

### gu08 "Is there a Grafana dashboard for the pipeline analytics?" (hard_negative = true)

- **Searched:** grafana, prometheus, dashboard, visual, OTLP viewer, ANALYTICS, analyze.mjs. Read `docs/PIPELINE_ANALYTICS.md` in full.
- **Nearest passages:** `docs/PIPELINE_ANALYTICS.md:17-31` the analytics are rendered by `analyze.mjs` to `runs/ANALYTICS.md` and `runs/dashboard.html` ("human · visual · self-contained, theme-aware"); `:64-65` "the dashboard's categorical colors ..."; `docs/GETTING_STARTED.md:29`; `TELEMETRY.md:36-37` (any OTLP backend, no viewer needs building). Grafana is not mentioned anywhere.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Judge risk: medium.** The docs describe a different dashboard (self-contained HTML). A judge may answer "no, the dashboard is `dashboard.html`", an answer by description. The docs do not say a Grafana dashboard does or does not exist, so the label holds. Of the 24, this and gu10 are the two where a lenient judge is most likely to say ANSWERABLE.
- **Hard-negative claim: real, strong.** Overlap `docs/PIPELINE_ANALYTICS.md` (shared "dashboard", "pipeline analytics").

### gu09 "Can the Release Manager require two people to approve a release?" (hard_negative = true)

- **Searched:** two people/approvers/reviewers, second approver, four eyes, dual/co-sign, multiple approvers, quorum, required reviewer, separation of duties, named approver, RBAC, Tier 3. Read `agents/release-manager.md`, `docs/HUMAN_APPROVAL_RULES.md:40-65`, `templates/CHANGE_REQUEST_TEMPLATE.md`, `docs/RELEASE_GATES.md:93-107`, `project-packs/enterprise-saas-future.md`.
- **What the docs give (partial, in three directions):**
  1. For the enterprise overlay the Release Manager owns a change request whose `## Approvals` table (`templates/CHANGE_REQUEST_TEMPLATE.md:45-51`) has three rows: Release Manager, "Compliance approver (if applicable)", and "Human owner (Tier 3 per `docs/HUMAN_APPROVAL_RULES.md`)". `docs/RELEASE_GATES.md:104-106` requires "a recorded, approved change request ... with a named approver" for enterprise Tier 3, and `project-packs/enterprise-saas-future.md:69` "Any RBAC change: Tier 3 + named compliance approver". So a reader can find a documented route in which a release records two human approvers (compliance approver plus human owner).
  2. `docs/HUMAN_APPROVAL_RULES.md:57-63` calls "who approved" an identity and names "RBAC Tier 3 named approvers, separation of duties" as controls that this field is the foundation for: they are described as later work.
  3. Against it: `README.md:21-24` "Today it is built for one person on one subscription; shared team gates ... are roadmap, not shipped"; `docs/GETTING_STARTED.md:177-179` "Single-operator proven, not multi-operator".
- **Verdict: AMBIGUOUS.** The docs neither say "yes, the Release Manager can require two approvers" nor "no". A reasonable reader could assemble either answer ("yes, in the enterprise change request" or "no, shared team gates are roadmap"). Part 1 comes close to a positive answer to "two people approve a release" for enterprise Tier 3, which makes an "unanswerable" key contestable.
- **Recommendation: REPLACE** (use a hard-negative reserve, see section 5). Keeping it risks a correct ANSWERABLE verdict being scored as a miss, which would be tuning the key after a result.
- **Hard-negative claim: real, strong** (that is also why it is ambiguous). Overlap `templates/CHANGE_REQUEST_TEMPLATE.md` and `docs/HUMAN_APPROVAL_RULES.md` (shared "approve", "Release Manager", "named approver").

### gu10 "Can I get the analytics report as a PDF?" (hard_negative = true)

- **Searched:** PDF, export, csv, spreadsheet, xlsx, download, printable, print, html, "report", ANALYTICS.
- **Nearest passage:** `docs/PIPELINE_ANALYTICS.md:24-31` (renders `runs/ANALYTICS.md` and `runs/dashboard.html`), `docs/GETTING_STARTED.md:28-29`, `agents/post-launch-learning.md:32`, `execution/pack/protocols/SLICE_STATE.md:226`. `README.md:22-23` and `execution/README.md:15` mention a "conformity export" (`CONFORMITY.md`, SOC 2 mapped, roadmap) which is a different report. The string "PDF" occurs nowhere in the corpus.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Judge risk: medium** (same shape as gu08): the docs name exactly two formats, so a judge could answer "no, markdown and HTML". The docs do not say these are the only formats.
- **Hard-negative claim: real.** Overlap `docs/PIPELINE_ANALYTICS.md` (shared "analytics", "report", "dashboard") and the "export" language of `execution/README.md:15` / `README.md:22-23`.

### gu11 "What is the Aveto pack's own test coverage percentage?" (hard_negative = true)

- **Searched:** coverage, percent signs near test, "tests pass/over/cover", node:test, npm test, mutation, test suite.
- **Nearest passages:** `docs/VALIDATION_MATRIX.md:107-116` "48 tests over `install.mjs`, `analyze.mjs`, and `budget-guard.mjs`" and "proven non-vacuous by mutation" (a test count and mutation checks, no coverage figure); `:162` "a test-presence signal (explicitly **not** coverage)" describing `quality.mjs` for a user's code; `:233` "now covered by the test suite and CI". Other "coverage" hits are eval, audit-event or control coverage (`agents/ai-governance.md:39`, `docs/RELEASE_GATES.md:60,102`).
- **Verdict: CONFIRMED UNANSWERABLE.** No percentage is stated. The count is stale-looking (48 at the 2026-07-28 audit) but no coverage figure exists.
- **Hard-negative claim: real, strong.** Overlap `docs/VALIDATION_MATRIX.md` (shared "test suite", "pack's own", "coverage", "tests").

### gu12 "Can I vote on what goes on the Aveto roadmap?" (hard_negative = true)

- **Searched:** roadmap, vote/voting, poll, upvote, community, contribut*, feature request, bug report, GitHub issues, discussions, maintainer.
- **Nearest passages:** `docs/VALIDATION_MATRIX.md:4` "This file is the roadmap and the scorecard"; `README.md:22-23` "roadmap, not shipped"; `docs/PIPELINE_ANALYTICS.md:12` (feedback path changes "the roadmap"); `docs/STANDARDS_WATCH.md` (watch list with triggers, decided by the owner); `templates/CUSTOMER_SIGNAL_REVIEW_TEMPLATE.md:25` "Feature requests -> underlying problems" (about the user's own customers). Nothing about outside input to Aveto's roadmap.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real.** Overlap `docs/VALIDATION_MATRIX.md` (shared "roadmap") and `templates/CUSTOMER_SIGNAL_REVIEW_TEMPLATE.md` ("feature requests", "prioritise").

### gu13 "How do I add my own custom role to the 28 agents?" (hard_negative = true)

- **Searched:** add/new/custom/own role or agent, extend, overlay, "28", how many agents, "write a brief". Read `docs/AGENT_ROLES.md:108-150`, `execution/README.md:1-60`, `execution/ADAPTERS.md:22`, `TELEMETRY.md:114-120`.
- **Nearest passages:** `README.md:12` "28 specialist agents" (the count is correct: `agents/` holds 28 files); `execution/README.md:47` and `execution/ADAPTERS.md:22` describe the installer generating "one Claude Code subagent per playbook brief" with per-role tool scoping; `docs/AGENT_ROLES.md:110-125` "Roles you will not see here" explains why four roles were left out; `docs/VALIDATION_MATRIX.md:240-244` "How to add a phase" (a validation phase, not a role). No passage tells a user how to add a role of their own; the per-role tool scoping the installer applies is not documented as extensible.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Judge risk: low to medium.** A reader can infer "write a brief in `agents/` and re-run install" from "one subagent per brief". The docs do not say new briefs are picked up.
- **Hard-negative claim: real, strong.** Overlap `docs/AGENT_ROLES.md` ("roles", "overlay roles"), `docs/VALIDATION_MATRIX.md` ("How to add a phase": shared "how to add"), `execution/README.md` ("agents", "install").

### gu14 "How many experiments can I run at the same time?" (hard_negative = true)

- **Searched:** concurrent, simultaneous, at the same time, in parallel, overlapping, collision, interaction, one/multiple experiments, maximum, at most, limit. Read `templates/EXPERIMENT_SPEC_TEMPLATE.md`, `agents/data-analyst.md`.
- **Nearest passages:** `templates/EXPERIMENT_SPEC_TEMPLATE.md:62-64` "What could confound this read? <seasonality, concurrent launches, selection effects>" (names concurrent launches as a confounder to consider, sets no limit); `agents/data-analyst.md:78-80` (no readout before the pre-registered duration). The "in parallel" hits (`docs/AGENTIC_SDLC.md:27,147`) concern the Analytics Engineer running alongside Architecture, not experiments.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real.** Overlap `templates/EXPERIMENT_SPEC_TEMPLATE.md` and `agents/data-analyst.md` (shared "experiment(s)", "concurrent"); `docs/AGENTIC_SDLC.md` ("in parallel").

### gu15 "Who founded Aveto?" (no hard_negative tag)

- **Searched:** founder, founded, created by, built by, authors, credits, acknowledg*, company, organisation, "our team", "I built", the owner handle `gpatwa`, `README.md:1-14`, history/origin.
- **Nearest passage:** `README.md:5-14` (tagline and what Aveto encodes) and `docs/VALIDATION_MATRIX.md:8-9,21` which link to `github.com/gpatwa/stash-seed` and `streak-seed` (reference apps, a repo owner handle in a URL; no statement of who made Aveto). `agents/cloud-deployment.md:21` "Microsoft-maintained skills" is about a third party.
- **Verdict: CONFIRMED UNANSWERABLE.**

### gu16 "Does it work in a monorepo?" (no hard_negative tag)

- **Searched:** monorepo, multi-repo, multiple repos, workspace, packages/, submodule, "each repo", "one repo", cross-repo, several products, subdirectory, nested, repo root.
- **Nearest passage:** `execution/README.md:39` "From the product repo root (which must have a `.agentic/` folder)"; `docs/GETTING_STARTED.md:70-96` one `.agentic/` per product repo; `execution/pack/protocols/RUN_INVENTORY.md:23-28` one product repo's slices fit one index, cross-repo inventory is above the pack. "Monorepo" occurs nowhere.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Judge risk: low.** A monorepo is a repo, so "install at the root" is a guess the docs do not make.

### gu17 "Can I run the agents inside Docker?" (no hard_negative tag)

- **Searched:** docker, container, devcontainer, sandbox, VM, kubernetes, isolation, codespaces, worktree.
- **Nearest passage:** none. `project-packs/browser-automation-product.md:36` "manual smoke on a sandbox site" (a test target); `docs/GETTING_STARTED.md:109-114` and `execution/ADAPTERS.md:79-95` describe running in a Claude Code session and per-role tool scoping. No container statement.
- **Verdict: CONFIRMED UNANSWERABLE.**

### gu18 "Does it support right-to-left languages?" (no hard_negative tag)

- **Searched:** RTL, right-to-left, i18n, l10n, locali[sz]ation, internationali[sz]ation, language(s), unicode, bidi, translation, multilingual, Arabic, Hebrew, non-English, locale.
- **Nearest passage:** none. All "language" hits are "the user's language" (`agents/market-researcher.md:28`, `templates/DISCOVERY_BRIEF_TEMPLATE.md:9`), "language's escape hatches" (`agents/frontend-developer.md:64`) or "Translate" in role missions.
- **Verdict: CONFIRMED UNANSWERABLE.**

### gu19 "Is there a nonprofit discount?" (hard_negative = true)

- **Searched:** discount, nonprofit, pricing, price, free, paid, subscription, licence/license, per seat, per month, metered, "marginal cost", sponsor, donation.
- **Nearest passage:** `README.md:19-21` "It runs on the **Claude Code subscription you already pay for** — not a metered API bill — so a slice carries no marginal cost"; `docs/AGENT_ROLES.md:122-125` "Go-to-market / marketing / pricing — out of build-time scope"; `agents/finops.md` (pricing for a user's product). No Aveto price list, plan or discount exists.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Judge risk: low to medium.** README line 19-21 implies Aveto itself costs nothing beyond the reader's own subscription, so a judge could say "there is no pricing, hence nothing to discount". The docs state no price for Aveto and nothing about eligibility or discounts.
- **Hard-negative claim: real.** Overlap `README.md` ("subscription", "pay", "cost") and `agents/finops.md` / `docs/AGENT_ROLES.md` ("pricing").

### gu20 "How do I report a bug in Aveto itself?" (no hard_negative tag)

- **Searched:** report bug, bug report, file/open/raise an issue, GitHub issues, feedback, support, contact, defect, "found a bug", BACKLOG.
- **Nearest passage:** none. `docs/GETTING_STARTED.md:185,201` point to `docs/BACKLOG.md` (not in the corpus, and a parked-work list, not a reporting route); `docs/VALIDATION_MATRIX.md:115,175,189` describe defects the pack found in itself, with no reporting process. "Feedback" hits are product feedback events or the Post-Launch loop.
- **Verdict: CONFIRMED UNANSWERABLE.**

### gu21 "How many people contribute to Aveto?" (no hard_negative tag)

- **Searched:** contributor(s), contributing, community, maintainers, authors, credits, team, "built for one person".
- **Nearest passage:** `README.md:21-22` "Today it is built for one person on one subscription" and `docs/GETTING_STARTED.md:177-179` "Every real run to date was driven by one person". Both are about operators/runs of the pack, not contributors to it. A weak lexical trap even though it is not tagged.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Judge risk: low.**

### gu22 "Can I give the Orchestrator voice commands?" (hard_negative = true)

- **Searched:** voice, speech, speak, audio, dictation, microphone, verbal, chat, conversation, command, slash command.
- **Nearest passages:** `agents/orchestrator.md:6,51` (the only direct conversation with the human), `execution/pack/commands/agentic-slice.md` and `docs/GETTING_STARTED.md:124,133` (the `/agentic-slice "<ask>"` command, typed), `docs/OPERATING_MODEL.md:70-73` "Hand off through artefacts, not chat". `agents/compliance-reviewer.md:34,63` "never confirmed verbally" is evidence quality, unrelated. `agents/tech-writer.md:21` "product voice" is a lexical false friend. Nothing about voice input.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real.** Overlap `agents/orchestrator.md` and `docs/GETTING_STARTED.md` (shared "Orchestrator", "commands", "conversation with the human").

### gu23 "Is there a mobile version of the Aveto website?" (hard_negative = true)

- **Searched:** mobile, responsive, viewport, breakpoint, phone, tablet, iOS, Android, touch, "narrow screen", app, `site/`, theme.
- **Nearest passages:** `README.md:143-148` (`site/index.html`, headers for Cloudflare Pages), `docs/DEPLOYMENT.md:8-14` (site gates check "structure, theme tokens, dead anchors, external origins"), `project-packs/b2c-saas.md:25` "Most B2C users hit the product on mobile" (about a user's B2C product). Nothing on how the site renders on phones or a separate mobile site.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real but mild.** Overlap `docs/DEPLOYMENT.md` and `README.md` ("website", "site"); `project-packs/b2c-saas.md` ("mobile"). Less tempting than gu01 or gu02 because only the first overlap is about the Aveto site.

### gu24 "Which Node.js version does the installer need?" (hard_negative = true)

- **Searched:** node version, Node.js, nvm, engines, ">= 18/20/22", prerequisites, requirements, dependency-free, npm install, python. Read `docs/GETTING_STARTED.md:96-125`, `execution/README.md:36-60`.
- **Nearest passages:** the installer is run as `node <playbook>/execution/install.mjs <product-repo>` (`docs/GETTING_STARTED.md:102`, `README.md:197`, `execution/README.md:42`); `docs/PIPELINE_ANALYTICS.md:26` calls `analyze.mjs` "dependency-free"; `docs/VALIDATION_MATRIX.md:107` mentions "`node:test`". No version number or minimum is stated in any `.md` file (a `package.json` under `execution/` is not corpus).
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real, strong.** Overlap `docs/GETTING_STARTED.md` and `execution/README.md` (shared "installer", "install", "node", "dependency-free").

### Unanswerable block, interim tally

CONFIRMED 23, AMBIGUOUS 1 (gu09), ANSWERABLE-IN-DOCS 0. Hard negatives tagged: 18 (gu01-gu14, gu19, gu22, gu23, gu24). No unanswerable question carries `sources`. Judge-risk items to disclose: gu03, gu08, gu10 (medium); gu05, gu13, gu19 (low to medium).

## 3. Answerable questions (standard depth)

For each: every `sources` path exists at the pinned commit and is a corpus file (all 24 questions' sources were checked by extracting the allow-list from the pinned commit; every path below is present). Then: does each source contain the answer, and which dedicated file (owning agent, its template or prompt, a doc dedicated to the topic; not a cross-cutting overview) is missing. Proposed additions are written `+path`. Nothing is proposed for removal except where stated.

| id | sources exist and in corpus | each source answers | additions proposed |
|---|---|---|---|
| g01 | yes | `docs/HUMAN_APPROVAL_RULES.md:165-168` ("NOT inferred from 'looks good' ... acknowledgements, not approvals") | `+execution/pack/protocols/APPROVAL_PROTOCOL.md` (line 55: "NOT inferred from 'looks good', 'nice', or a thumbs-up"; the protocol whose subject is approval). Not proposed: `prompts/release-gate.md:29`, `agents/release-manager.md:88` (Release Gate role, "do not infer approval from acknowledgement"), which are release-scoped restatements. |
| g02 | yes | `docs/GETTING_STARTED.md:49-50` ("~756k tokens per slice on average (520k-947k observed range)") | `+execution/pack/protocols/RUN_ECONOMICS.md` (what a run costs; `:67-68` "more than 6 stages or ~600k is a signal the slice is too big"; GETTING_STARTED itself points to it), `+execution/pack/protocols/PIPELINE_SLOS.md` (slice token envelope `:18`, measured totals 110k to 884k `:36-40`), `+docs/OPERATING_MODEL.md` (`:19-29` "Typical slice sizes ... Est. tokens" 30k to 200k). Note the figures differ (measured peak-context sums vs estimated work tokens); each is a defensible answer to "roughly how many". |
| g03 | yes | `docs/OPERATING_MODEL.md:128-129` ("Trunk-based by default ... No long-lived feature branches") | none found |
| g04 | yes | `docs/DEPLOYMENT.md:92-102` (Cloudflare Pages keeps every deployment; revert the commit) | none found |
| g05 | yes | `docs/OPERATING_MODEL.md:140-146` (only the Orchestrator communicates with the human; others produce artefacts, not status updates); `agents/orchestrator.md:6,51` | none (`execution/pack/commands/agentic-slice.md:53` "Report back to the human at natural pauses" is the Orchestrator's command; not proposed) |
| g06 | yes | `docs/STANDARDS_WATCH.md:37-47` (Article 50: "disclose to users that they are interacting with AI"); `agents/compliance-reviewer.md:76-80` (precondition on any rule-5 slice) | none (`templates/AI_RISK_ASSESSMENT_TEMPLATE.md:33` has a "Transparency / disclosure to users" row only; not proposed) |
| g07 | yes | `docs/RELEASE_GATES.md:130-147` ("CI enforces the mechanical gates; it does not replace the judgment ones"); `docs/HUMAN_APPROVAL_RULES.md` rule 3 (`:44-55`, deploy/release needs a named human) | `+agents/release-manager.md` (the owning role: `:5-6` confirms every gate and every approval, `:59-66` approval verification, `:73-75` no conditional release) |
| g08 | yes | `docs/GETTING_STARTED.md:177-179` ("Single-operator proven, not multi-operator ... Every real run to date was driven by one person"). **`docs/VALIDATION_MATRIX.md` does not state it**: it records the runs (all on the author's two seed apps, phase 5 multi-tenancy not done, `:22`) and the audit bar "another team installs the pack ... without us" (`:99`) but never says how many people ran it. Defensible only by inference. | `+execution/pack/protocols/SLICE_STATE.md` (`:203-207` "Every run to date was driven by one person, so the field costs nothing today and is the prerequisite for anything multi-operator later"). Keep `docs/VALIDATION_MATRIX.md` (its subject is what has been proven on real projects) but it is the weakest listed source; the owner may drop it, which only makes the gate stricter. README `:21-22` also states "built for one person on one subscription"; not proposed (overview). |
| g09 | yes | `docs/GETTING_STARTED.md:72-73,180` ("no scaffolding tool yet"; "No `.agentic/` scaffolding tool") | **`+docs/VALIDATION_MATRIX.md`**: `:90-94` "`execution/install.mjs --greenfield` scaffolds a stub `.agentic/` so a brand-new repo can install the pack". So the corpus contains a command that creates a stub of the folder, alongside the statement that no tool generates real content. The docs conflict in part; the question is still answerable, but the key's `where` ("no scaffolding tool") is not the only defensible answer. This is the one finding in this section that could change what a correct answer looks like. |
| g10 | yes | `docs/VALIDATION_MATRIX.md:228-233` ("No uninstall for the pack, and none planned ... revert is `git checkout`") | none found |
| g11 | yes | `agents/data-analyst.md:5,37-38` and `prompts/experiment-readout.md:34` (decision ship / hold / kill / extend); `templates/EXPERIMENT_SPEC_TEMPLATE.md` names the Data Analyst as who reads out (`:15`, readout plan) but does not list the outcomes (answers half the question) | none |
| g12 | yes | `agents/ux-researcher.md:5,20-23` ("Translate the PRD into a feature spec that names users, journeys ..."); `prompts/ux-audit.md:13`; `templates/FEATURE_SPEC_TEMPLATE.md:7-13` (personas, journeys) | none |
| g13 | yes | `agents/engineering-manager.md:61` ("the EM proposes a split — usually 2-4 smaller slices"); `prompts/em-scope-review.md:14,49` | none (`docs/OPERATING_MODEL.md:28-29,41` say the EM splits oversized slices but give no count; half the question; not proposed) |
| g14 | yes | `agents/ml-engineer.md:47,74,88-89` (beats the incumbent; shadow before canary); `prompts/ml-training.md:16,42,64,71` | `+templates/MODEL_CARD_TEMPLATE.md` (the ML Engineer's output: `:47` "Comparison to incumbent ... whether new model wins", `:4` status shadow / canary / live, approvals list) |
| g15 | yes | `agents/ai-governance.md:5,8,50,81` (owns the eval suite; Eval Curator; "must stay representative"); `prompts/ai-risk-review.md:15-16,40` | none |
| g16 | yes | `agents/sre.md:27-28,43` (error budget = 1 - SLO; policy; feature freeze); `prompts/reliability-review.md:28-29` | none (`templates/INCIDENT_REVIEW_TEMPLATE.md:65` asks whether the policy triggers a freeze; does not define it; not proposed) |
| g17 | yes | `prompts/developer-task.md:28` ("Read only the files you will touch and the files those depend on"); `docs/OPERATING_MODEL.md:52-55` | `+agents/frontend-developer.md` (`:57` "Read the files you'll touch and the files they depend on. Don't pre-..."; the developer agent's own brief). `agents/engineering-manager.md:93,118` says the same from the EM side; not proposed. |
| g18 | yes | `examples/.../05-tech-spec.md:27-28` ("Wrapped in one transaction: if any write fails, the whole batch rolls back"); `examples/.../07-security-review.md:30` (all-or-nothing, partial failure cannot leave a misleading state) | `+examples/saved-items-bulk-delete/artefacts/03-feature-spec.md` (`:38-39` "Network/save error mid-batch: nothing is partially shown as deleted"), `+examples/saved-items-bulk-delete/artefacts/04-ux-spec.md` (`:35-37` error copy reassures nothing was removed, "all-or-nothing behaviour"). Optional, not proposed: `06-qa-evidence.md:28`. |
| g19 | yes | `examples/.../02-prd.md:39,44,59` (in-session Undo now; trash view later); `examples/.../04-ux-spec.md:16-18` (30-day recovery, Undo toast) | `+examples/saved-items-bulk-delete/artefacts/03-feature-spec.md` (`:30-31` "Undo is in-session only; once the toast is gone, recovery is via the 30-day soft-delete window (support for now)", the most direct statement of both halves). Optional, not proposed: `05-tech-spec.md:30-36`, `.agentic/CURRENT_MVP_STATUS.md:19-20`. |
| g20 | yes | `docs/OPERATING_MODEL.md:80-87` (prompt cache short TTL; long mid-slice pauses expensive; re-pay replaying context) | none (`execution/pack/protocols/MODEL_ROUTING.md:85` says model switching mid-stage forfeits the cache: a different cause) |
| g21 | yes | `agents/ai-governance.md:24-26` (NIST AI RMF, GenAI Profile AI-600-1, EU AI Act, ISO 42001, ISO 42005); `templates/AI_RISK_ASSESSMENT_TEMPLATE.md:5-6`; `docs/STANDARDS_WATCH.md:13-14` | `+prompts/ai-risk-review.md` (the agent's prompt: `:28` NIST AI RMF, EU AI Act tiers; `:43` ISO 42001; names fewer standards than the brief, so it answers in part) |
| g22 | yes | `examples/.../05-tech-spec.md:55,70` and `08-release-checklist.md:25,33` (toggle `bulkDelete` off) | none |
| g23 | yes | `templates/CHANGE_REQUEST_TEMPLATE.md:15-20` (Standard / Normal / Emergency) | none (`docs/RELEASE_GATES.md:64,105` mention the change request but not the types) |
| g24 | yes | `docs/HUMAN_APPROVAL_RULES.md:111-127` ("Allowed without approval") | none |

### Answerable questions that are really unanswerable or ambiguous

None of the 24. g09 is answerable on two defensible readings (see above), and g02 has two different defensible figures, but each has a stated answer in the docs.

### Sources that do not answer

`docs/VALIDATION_MATRIX.md` for g08 (does not state the operator count, see table). All other listed sources contain the answer or the part of it the key's `where` states. No source path is missing and none is outside the corpus.

### Repeat and format checks on the answerable and unanswerable questions

- **No question repeats a seen-set question verbatim or in substance.** Read as question text only against the 93 questions of the four earlier sets. Near-topic cases, reported as information and not as defects (source reuse is accepted and disclosed; this is about topic):
  - g23 against "If a release needs sign-off from a change board, what do we fill in?" (same file, `templates/CHANGE_REQUEST_TEMPLATE.md`; different fact, the three change types).
  - g24 against "Which things will the agents never do without asking me first?" (the converse list in the same file) and g01 against "When I say yes to something the agents asked about, how is that written down?" (same topic cluster, different fact).
  - g09 against "What files does my own repo need before the agents can work on it?" (same section of `docs/GETTING_STARTED.md`; different fact).
  - g08 against "What has actually been tested on real projects, and what hasn't?" (validation evidence; different fact).
  - g04 against "How is the Aveto website itself published?" (same file, `docs/DEPLOYMENT.md`; rollback instead of publishing).
  - g13, g17 against "How does it stop an agent from losing track on a really big task?" (context and slice sizing; whether the earlier key points to `docs/OPERATING_MODEL.md` or the EM was not checked, since only question text of earlier sets was read).
  - g14, g15, g21, g16 reuse owners that earlier sets also ask about (ML Engineer, AI Governance, SRE) with different duties.
  - Unanswerable side: gu17 resembles "How do I deploy Aveto on Kubernetes?", gu18 resembles the Japanese and Spanish questions, gu19 resembles "Is there a free trial?" and the licence-price question, gu23 resembles the phone-app question, gu24 resembles "Does Aveto run on Windows?" and the Raspberry Pi question, gu12/gu20/gu21 resemble the Discord question. Same genre, different asks. None is a repeat.
- **Format.** All 48 + 6 questions parse as TOML, are single lines, have no control or format characters, no duplicate ids, and use only the keys `id`, `question`, `sources`, `where`, `answerable`, `hard_negative`. Only g01 contains double quotes (two, TOML-escaped; no earlier question has any) and apostrophes occur in g09, gu11, gr01, gr02 (15 earlier questions have apostrophes). `aveto_support/judge.py:normalise_question` rejects only control and format characters, so none of these is rejected; g01's quotes are the first of that kind to reach the judge payload. Low risk; reported, no edit proposed.
- **Counts.** 24 answerable (g01..g24), 24 unanswerable (gu01..gu24), 18 `hard_negative = true` (gu01-gu14, gu19, gu22, gu23, gu24), 6 without the tag (gu15, gu16, gu17, gu18, gu20, gu21). No unanswerable question carries `sources` or `where`. `pinned_commit` equals the corpus commit.

## 4. Reserves (gr01 to gr06)

The reserves file holds 6 questions: **4 unanswerable** (gr01 plain; gr02, gr03, gr04 hard negatives) and **2 answerable** (gr05, gr06). Only the four unanswerable ones can replace an unanswerable question; the two answerable ones cannot, so the usable pool is 1 plain and 3 tagged hard negatives, before this review.

### gr01 "Can I put my company's logo on the documents the agents generate?" (no tag)

- **Searched:** logo, brand/branding, letterhead, white-label, customise/custom templates, house style, style guide, company name, "edit the templates". `agents/tech-writer.md:21,29` uses "product voice and terminology" for copy, not logos or document styling; the templates are fixed markdown with placeholders.
- **Verdict: CONFIRMED UNANSWERABLE.** Usable as a plain unanswerable replacement.

### gr02 "Can I export a run's trace as a spreadsheet?" (hard_negative = true)

- **Searched:** spreadsheet, csv, xlsx, excel, export, download, trace, trace.json, ANALYTICS, OTLP.
- **Nearest passage:** `execution/pack/protocols/SLICE_STATE.md:100-120` (`trace.json` schema, machine-readable JSON), `docs/PIPELINE_ANALYTICS.md:24-31` (`ANALYTICS.md`, `dashboard.html`), `docs/GETTING_STARTED.md:166-170` (`usage.mjs --write` saves `usage.json`), `execution/pack/protocols/TELEMETRY.md:36-37` (any OTLP backend). No spreadsheet or CSV output exists in the corpus; "export" appears only for audit export and the conformity export.
- **Verdict: CONFIRMED UNANSWERABLE.**
- **Hard-negative claim: real.** Overlap `docs/PIPELINE_ANALYTICS.md` and `execution/pack/protocols/SLICE_STATE.md` (shared "trace", "run", "export"). Same shape and the same judge risk as gu10 (docs name other formats; they never say these are the only ones).

### gr03 "Which database does the Aveto website use?" (hard_negative = true)

- **Searched:** database, D1, KV, Postgres, SQLite, MySQL, Dynamo, Mongo, "static site", index.html, serverless, Workers, Pages functions.
- **Nearest passage:** `docs/DEPLOYMENT.md:3-14` and `README.md:143-148` (the site is `site/index.html` with `_headers`, deployed to Cloudflare Pages). Nothing says the site has, or lacks, a database. The word "database" occurs once outside the examples (`docs/HUMAN_APPROVAL_RULES.md:33`, "Deleting a database row"); data-model talk in `agents/backend-architect.md` and `templates/MIGRATION_PLAN_TEMPLATE.md` is about a user's product.
- **Verdict: CONFIRMED UNANSWERABLE.** A reader may infer "static page, so no database" from `site/index.html` and Cloudflare Pages; that is inference, not a statement.
- **Hard-negative claim: real.** Overlap `docs/DEPLOYMENT.md` and `README.md` (shared "Aveto website", "deployed", Cloudflare Pages). The lure is the site description, not the word "database", which is nearly absent from the corpus, so this is a topical rather than a lexical trap and a milder one than gu01. Same family as gu01 and gu02 (website infrastructure).

### gr04 "Can I start a slice from a webhook or from another program?" (hard_negative = true)

- **Searched:** webhook, API call, trigger a slice, start a slice, programmatic, headless, non-interactive, scripted, SDK, "parent agent", `/agentic-slice`.
- **What the docs give:** `docs/AGENTIC_SDLC.md:44-45` and `agents/orchestrator.md:10` define Intake input as "Free-form ask from a human or a parent agent, or a path to an intent file". The documented entry point is the slash command `/agentic-slice "<ask>"` or a path to an intent (`docs/GETTING_STARTED.md:124,133`, `execution/pack/commands/agentic-slice.md:3`), typed in a Claude Code session. Webhooks appear nowhere; `workflow_dispatch` in `docs/DEPLOYMENT.md:89` starts the site deploy, not a slice.
- **Verdict: AMBIGUOUS.** "Another program" is partly answered: a parent agent is a documented source of the ask. A reasonable reader could say "yes, an orchestrating agent can hand it a request" and call the webhook half unaddressed. **Recommendation: do not use as a replacement**; keep in the reserve pool only as a last resort.
- **Hard-negative claim:** real (the "parent agent" line is the lure), which is also why it is ambiguous.

### gr05 "Does anything run at the same time as the engineers, or is every stage strictly one after another?" (answerable)

- **Sources:** `agents/analytics-engineer.md:10` ("runs alongside Architecture and re-enters during QA Evidence"); `docs/AGENTIC_SDLC.md:27,146-148` ("plus the Analytics Engineer in parallel"; "runs alongside this stage"). Both exist, both answer. The key's `where` says "alongside Architecture and Implementation"; the docs say Architecture in `analytics-engineer.md:10` and the Implementation handoff in `docs/AGENTIC_SDLC.md:146-148`, so the `where` is a fair merge.
- **Possible additions:** `agents/data-governance.md:12` ("runs alongside Architecture for any slice that adds or changes data"), an enterprise overlay that also runs in parallel; not alongside the engineers, not proposed.
- **Note:** same agent as the earlier question "Who makes sure the product sends the events we need to measure success?". Answerable, not ambiguous. Not usable as a replacement for an unanswerable question.

### gr06 "What does an agent have to include when it asks me for approval?" (answerable)

- **Sources:** `docs/HUMAN_APPROVAL_RULES.md:131-141` (what, why, what is reversed if denied, the smallest request). Answers.
- **Proposed addition if the reserve is ever used:** `+execution/pack/protocols/APPROVAL_PROTOCOL.md` (`:31-37`, the same four items; the protocol whose subject is the approval request).
- **Note:** same file cluster as g01, g24 and the earlier approval questions. Not usable as a replacement for an unanswerable question.

## 5. Replacement mapping and capacity

Replacement protocol used (the reserves file's own): in id order, unchanged, same kind (hard negative for hard negative).

| Replace | With | Reason | Status |
|---|---|---|---|
| gu09 (hard negative) | **gr02** (hard negative, CONFIRMED) | gu09 is AMBIGUOUS and the docs include a change-request approvals table with a compliance approver and a human owner (`templates/CHANGE_REQUEST_TEMPLATE.md:45-51`); recommendation is to replace | **Recommended; owner decides** (AMBIGUOUS cases are the owner's call) |

No question is ANSWERABLE-IN-DOCS and none is mislabelled, so no mandatory replacement exists. If the owner takes the recommendation:

- Unanswerable count stays **24** (23 original CONFIRMED + gr02). Hard negatives stay **18** (17 original + gr02). No stop condition (pack held-out rule 9).
- Reserves left afterwards: gr01 (plain), gr03 (hard negative, CONFIRMED), gr04 (AMBIGUOUS, not recommended). Capacity for further swaps: **one more hard negative** (gr03) and **one plain** (gr01). A second plain-for-plain swap, or a third hard-negative swap, could not be made without using gr04.
- If the owner instead keeps gu09, nothing changes: 24 unanswerable (23 CONFIRMED and gu09 AMBIGUOUS), 18 hard negatives, all reserves untouched.
- **Capacity in general.** Confirmed reserves: 2 hard negatives (gr02, gr03) and 1 plain (gr01). The unanswerable set therefore stays at 24 with 18 hard negatives after any combination of up to 2 hard-negative swaps and 1 plain swap. A third hard-negative swap, or a second plain swap, could be filled only with gr04 (AMBIGUOUS) or not at all; in that case the slice stops (pack held-out rule 9: the bar does not shrink). Nothing in this review forces such a swap: no unanswerable question was found answerable.

## 6. Exact proposed edits (none applied)

Edits to `evals/retrieval-heldout-5.toml` (additions to `sources` only; nothing dropped):

| # | id | Change | Priority |
|---|---|---|---|
| E1 | gu09 | Replace the question with **gr02** unchanged ("Can I export a run's trace as a spreadsheet?", `hard_negative = true`), per the reserves file's id-order rule. AMBIGUOUS, so the owner decides; recommendation: replace. | owner decision |
| E2 | g01 | add `execution/pack/protocols/APPROVAL_PROTOCOL.md` | default |
| E3 | g02 | add `execution/pack/protocols/RUN_ECONOMICS.md`, `execution/pack/protocols/PIPELINE_SLOS.md`, `docs/OPERATING_MODEL.md` (the last answers a different quantity, estimated tokens by slice size, and is the lowest priority of the three; OPERATING_MODEL is already a source for g03, g05, g17 and g20) | default (OPERATING_MODEL optional) |
| E4 | g07 | add `agents/release-manager.md` | default |
| E5 | g08 | add `execution/pack/protocols/SLICE_STATE.md`. Keep `docs/VALIDATION_MATRIX.md` (flagged: does not itself state the operator count; the owner may drop it, which would only make the gate stricter) | default |
| E6 | g09 | add `docs/VALIDATION_MATRIX.md` (the `--greenfield` stub scaffolding at `:90-94`) | default; the owner should read the finding |
| E7 | g14 | add `templates/MODEL_CARD_TEMPLATE.md` | default |
| E8 | g17 | add `agents/frontend-developer.md` | default |
| E9 | g18 | add `examples/saved-items-bulk-delete/artefacts/03-feature-spec.md`, `examples/saved-items-bulk-delete/artefacts/04-ux-spec.md` | default |
| E10 | g19 | add `examples/saved-items-bulk-delete/artefacts/03-feature-spec.md` | default |
| E11 | g21 | add `prompts/ai-risk-review.md` | default |

Edits to `evals/retrieval-heldout-5-reserves.toml`: none now. If gr06 is ever used, add `execution/pack/protocols/APPROVAL_PROTOCOL.md` to its sources.

Not proposed (considered and left out): additions that are cross-cutting overviews or restatements in other roles' briefs (`docs/AGENT_ROLES.md`, `docs/AGENTIC_SDLC.md`, `README.md` for the facts above; `prompts/release-gate.md`; `agents/engineering-manager.md` for g17; `templates/AI_RISK_ASSESSMENT_TEMPLATE.md` for g06; `templates/INCIDENT_REVIEW_TEMPLATE.md` for g16).

Wording of the questions: no edits proposed. g01's embedded double quotes are the one unusual character class; the code accepts them.

## 7. Method and limits

- Every unanswerable question got at least two keyword sweeps (terms and synonyms are listed per question) over all 123 corpus `.md` files, then the nearest files were read, not only matched lines. Answerable sources were each opened at the cited lines. Line numbers are from the pinned commit's files.
- A negative result is only as good as the searches: a passage that answers in vocabulary I did not try would be missed. The residual risk is concentrated where the docs describe a neighbouring thing (the judge-risk list in section 0), not in a missed document.
- No retrieval, eval, judge or index command was run on any question of either file, and no stage 5 result was read. Only question text of the four earlier eval files was read for the repeat check.
- Probe scripts: one-off TOML parse and character check of the two eval files (not worth landing as a test; the set is frozen data and the product's own loader already validates it). No test was added.
