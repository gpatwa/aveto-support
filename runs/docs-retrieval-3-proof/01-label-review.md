# Label review: retrieval-heldout-4 (draft) — docs-retrieval-3-proof

> Owner: QA Evidence (fresh spawn #1, label review only). Rule applied: pack "Held-out gates" rule 4.
> Standard, applied to every question: a file is a source if a person reading **that file alone** could answer the question from it. Questions and the bar (13 of 16) are unchanged. No drafter source was dropped.

Abbreviations: **SDLC** = docs/AGENTIC_SDLC.md, **ROLES** = docs/AGENT_ROLES.md, **GATES** = docs/RELEASE_GATES.md, **ENT** = project-packs/enterprise-saas-future.md, **GS** = docs/GETTING_STARTED.md.

## Per-question table (answerable)

| id | Drafter's sources | Final sources | Added / dropped (reason) |
|----|-------------------|---------------|--------------------------|
| f01 | templates/PRD_TEMPLATE.md, agents/product-manager.md | + prompts/product-brief.md, SDLC, templates/INTENT_TEMPLATE.md | Added: product-brief prompt (PRD quality bar); SDLC stage 4 lists the PRD's contents; INTENT_TEMPLATE is the "requirements" page the agents say replaces the feature spec on the short path (see flag). Dropped: none |
| f02 | agents/compliance-reviewer.md, templates/COMPLIANCE_REVIEW_TEMPLATE.md, prompts/compliance-review.md | + ENT, SDLC, ROLES, GATES | Added: ENT and SDLC name the Compliance Reviewer mapping changes to SOC 2 / ISO 27001; ROLES overlay entry says it maps a change to named controls; GATES row "Controls mapped + evidence | Compliance Reviewer". Dropped: none |
| f03 | templates/COST_BUDGET_TEMPLATE.md, prompts/cost-review.md | + agents/finops.md, SDLC, ROLES, ENT | Added: the owning FinOps brief (cost model, monthly cost at projected volume) was missing; SDLC/ENT/ROLES say FinOps models cost-per-action and unit economics. Dropped: none |
| f04 | templates/RELEASE_CHECKLIST_TEMPLATE.md, prompts/release-gate.md | + agents/release-manager.md, GATES, SDLC | Added: owning Release Manager brief (checklist + rollback plan); GATES is the gate list incl. "Rollback plan exists"; SDLC stage 11 plus "Rollback is drilled". Dropped: none |
| f05 | agents/backend-architect.md, prompts/developer-task.md | unchanged | None added. ROLES/SDLC only name the role without stating server-side duties |
| f06 | templates/UX_SPEC_TEMPLATE.md, agents/ui-designer.md | + SDLC | Added: SDLC stage 6 lists "states (loading, empty, error, success)" in the UX spec. FEATURE_SPEC_TEMPLATE considered and left out: it names states for the designer, not the final treatment "for the developer" |
| f07 | agents/customer-success.md, templates/CUSTOMER_SIGNAL_REVIEW_TEMPLATE.md, prompts/customer-signal.md | unchanged | None added. SDLC/ENT/ROLES mention the signal review but not turning themes into candidate slices |
| f08 | agents/market-researcher.md, templates/DISCOVERY_BRIEF_TEMPLATE.md, prompts/market-research.md | + SDLC, agents/product-manager.md | Added: SDLC stage 2 ("first defence against building the wrong thing"); PM brief says never invent a problem, say so if the data doesn't show one (borderline, see flag) |
| f09 | templates/TECH_SPEC_TEMPLATE.md, agents/software-architect.md, prompts/architect-plan.md | + SDLC, ROLES | Added: SDLC stage 7 and ROLES row name the tech spec as the Architect's output |
| f10 | agents/security-privacy.md, prompts/security-review.md | + templates/THREAT_MODEL_TEMPLATE.md, SDLC, GATES | Added: threat model owned by Security & Privacy (attack surface); SDLC stage 10 (secrets, log leaks, data flows); GATES Security rows (secrets, PII logged) |
| f11 | agents/analytics-engineer.md, prompts/analytics-contract.md | + SDLC, ROLES | Added: SDLC stage 7 paragraph (turns success criteria into an event contract); ROLES row (PRD success criteria to event contract) |
| f12 | agents/post-launch-learning.md, templates/POST_LAUNCH_REVIEW_TEMPLATE.md | + SDLC, agents/data-analyst.md | Added: SDLC stage 12; Data Analyst brief covers post-launch readout of success criteria |
| f13 | agents/orchestrator.md, prompts/orchestrator.md | + SDLC, execution/pack/commands/agentic-slice.md, execution/pack/AGENTS.md, execution/README.md, GS | Added: each states the Orchestrator session delegates every stage to the role subagents (agentic-slice step 7; AGENTS "delegates each stage to a role"; README "delegates each lifecycle stage"; GS; SDLC "owns the agenda") |
| f14 | project-packs/enterprise-saas-future.md | unchanged | None added; no other file mentions SSO or enterprise buyers (see flag on "selling") |
| f15 | agents/ai-engineer.md | + SDLC, project-packs/ai-agent-product.md, prompts/developer-task.md, agents/ml-engineer.md | Added: SDLC stage 8 ("AI Engineer, who wires hosted-LLM adapters and prompts"); AI pack ("AI Engineer is a separate role... prompt versioning, adapter boundaries"); developer-task prompt covers the AI engineer role (same reasoning as f05's drafter label); ml-engineer states the AI Engineer wires LLM adapters and prompts |
| f16 | docs/PIPELINE_ANALYTICS.md | + GS, execution/README.md, agents/post-launch-learning.md, execution/pack/protocols/SLICE_STATE.md, docs/VALIDATION_MATRIX.md | Added: each states `analyze.mjs` renders `runs/ANALYTICS.md` + `dashboard.html` across runs (GS lines 28-29 "cost, density, DORA-style metrics across every run"; execution/README; Post-Launch brief; SLICE_STATE regeneration line; VALIDATION_MATRIX row 6) |

Totals: 40 sources added across 13 questions; 0 dropped; f05, f07, f14 unchanged. Source count: drafter 33, final 73.

## Unanswerable entries (structure unchanged)

| id | Status check |
|----|--------------|
| fu01 Bitbucket | Correctly unanswerable: no Bitbucket/GitLab/git-host statement anywhere. Note: GS and verify-approvals mention checking GitHub-PR references, a near-miss a retriever may surface; it does not answer the question |
| fu02 GitHub Marketplace | Correctly unanswerable: no Marketplace/listing mention (README mentions the aveto.dev site only) |
| fu03 SOC 2 certified | Correctly unanswerable: SOC 2 appears only about the product under build, plus GS lines 31 (the conformity export "mapped to what a SOC 2 auditor asks") which is a tool feature, not Aveto's certification status. The drafter's hard_negative note is accurate but omits GS and ENT; it is a diagnostic note and was left as written |
| fu04 Japanese | Correctly unanswerable: no language/localisation/translation-of-docs statement |

No "unanswerable" question was found to be answered by the docs.

## Flags

1. **f01 ambiguous.** "Requirements doc" can mean the PRD (drafter) or the Intent (the human's requirements page; Architect brief: on the short path the intent "replaces the feature spec as the source of requirements"). Both are labelled; the question was not rewritten.
2. **f03 mild.** "Cost to run" could be read as the cost of running the pipeline (RUN_ECONOMICS, GS cost figures); "a new feature" points to FinOps, so those were not labelled. "cost" also overlaps the file names COST_BUDGET_TEMPLATE / cost-review (low severity, the question is otherwise a paraphrase).
3. **f08 borderline label.** product-manager.md added on "never invent a problem / say so if the data doesn't show one". The strong answer is the Market Researcher; if the owner finds PM too loose it is the one addition to remove (before commit, not after).
4. **f12 borderline, not labelled.** production-verification.md (live health vs success criteria right after deploy) and customer-success.md ("did the last slice land for customers?") partly answer; left out because neither is the post-release success-criteria review. Same for ADR_TEMPLATE under f09.
5. **f13 ambiguous.** "Hands out the work to all the others" could also point at the Engineering Manager (scope and sequencing). The Orchestrator brief and delegation docs fit best; EM not labelled.
6. **f14 wording.** "Selling to large companies" vs a pack about *building* enterprise-ready SaaS (ROLES says go-to-market is out of build-time scope). The pack still answers the SSO/audit-trail part; single source kept.
7. **Examples excluded by a uniform rule.** examples/saved-items-bulk-delete/artefacts/* are filled instances (e.g. 02-prd.md, 05-tech-spec.md). Excluded everywhere: they show an example, not guidance. If the scorer finds one retrieved as a top hit this is the reason it is not a source.
8. **Scoring consequence.** SDLC (docs/AGENTIC_SDLC.md) is now a source for 12 of 16 questions, because it restates each stage's owner and output. This makes the gate easier to pass than the drafter's labels; it is the consistent application of "defensibly answers", not a tuning choice, and is stated so the owner can see it before committing.
9. Trivially filename-matched questions: none found beyond f03 (above); the drafter paraphrased throughout.

Flagged answerable questions: f01, f03, f08, f12, f13, f14 (6); wrong "unanswerable" statuses: 0.

## What I read and did not read

Read: the draft set; the pinned-docs corpus (123 .md files; I also saw the 20 non-markdown files in the directory listing but used none), via full reads of the lifecycle/roles/gates/README/GS docs, the owning agent, template and prompt for each question, the enterprise and AI packs, and keyword searches across the whole corpus for each question and each unanswerable topic; the playbook "Held-out gates" section. Did not read: any code, specs, run artefacts, evals/, other tests, STATE files of other slices (I read only this slice's STATE.md to update my row), ADRs; did not run retrieve, eval, ingest or any code; did not look up how retrieval works. Only paths under runs/docs-retrieval-3-proof/ were written.
