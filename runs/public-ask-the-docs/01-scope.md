# Scope review — public-ask-the-docs (stage 1, Engineering Manager, depth standard)

Read: `intent.md`, `00-slice-plan.md`, `CHARTER.md` (sha256 d0acc534…fa74c, unchanged), `.agentic/PROJECT_CONTEXT.md`, `CURRENT_MVP_STATUS.md`, `SAFETY_INVARIANTS.md` INV-4 and INV-5, plus four greps (below). I changed neither the intent, the plan nor the Charter.

## Verdict
**Proceed with changes.** The changes are recommendations to downstream stages. None needs a Charter amendment. No stop item (see "Outside the Charter").

## 1. Is the slice the right size?
By the letter of the scope rules (EM brief; `OPERATING_MODEL.md` Cadence) it is **over size**: a non-refactor change that will touch well over 10 files (service, adapter, page, Bicep, image definition, tests, `pyproject`/`uv.lock`, four docs, `SAFETY_INVARIANTS.md`), a user-facing behaviour change, new dependencies, and three verification surfaces (pytest, Bicep what-if, the live gate).
- Splitting is a change to the plan the Charter hashes (C1.2), so it would be a stop. I do not recommend it: the owner approved one slice, and the seams are inside it.
- Recommended instead, to keep each stage's context under ~10 files: the Architect's tech spec names the module boundaries (service, limits, adapter, page, infra) so stages 8 to 11 each read only their own files plus the spec.
- Fallback split if budget bites at the ceiling (a recommendation for the owner, not a plan change): A = stages 1 to 16 (service built and verified offline); B = 17 to 19 (deploy, verify, gate). The plan's own order already has this seam at the Release Gate.

## 2. Does the stage list and order hold?
**Holds**, with these flags (all handled by an instruction, not a re-plan):
1. **INV-4/INV-5 words are written after the adversarial check of them.** Stage 14 checks "the INV-4/INV-5 words" but stage 15 (Tech Writer) writes them. Security can review only the Architect's bound text at 14. Stage 16 must therefore diff `SAFETY_INVARIANTS.md` against `2919c87` and show that only the sentences C5.1 and C5.2 permit changed, and that C5.3 and C5.4 paths are byte-identical.
2. **Kill switch versus C8.3 and P10.** Intent: "turns the service off without a redeploy". P10 says no `containerapp` CLI extension is used, and C8.3 lists "set the kill switch on or off" without naming a mechanism. Stage 5 must pick a mechanism that C8.3's words cover and that an agent can run in C8.1's failure path. If it needs an action C8.3 does not list (an extension install, writing a Key Vault value), that is a Charter stop (9.1) found at stage 5.
3. **Stages 8 and 9 share an interface.** The adapter protocol (question + passages in, verdict token out) must be fixed in the tech spec so 8 and 9 do not collide. Order 8 then 9 is fine if so.
4. **Existing judge code is transport-file based** (block ids, input hash binding; `aveto_support/judge.py`, `parse_verdict(reply, block_id)`). The service needs an in-memory path to the same parser. `test_judge_modules_import_allow_list` and `test_program_offline_no_model` guard the existing modules; the Architect should add `anthropic` and `fastapi` imports only in new modules and keep those tests green unchanged.
5. **Live API is unused until stage 18**, yet the daily spend counter needs a cost per question. The tech spec must define a conservative pre-call estimate (max input + output tokens at a cited price), reconcile from the response's usage, and report "measured cost per question" only after stage 18.

## 3. Skips, with rationale
- **Market Research:** optional; the owner stated the problem, the visitor and the decision in `intent.md` ("What I want", "Who it's for"). Agree.
- **FinOps as a stage:** cost is one hard-capped line ($10 a month, plus the console backstop) and scale-to-zero Azure. The cost model sits in the tech spec, Security checks it, the Release Manager checks the reported figures. Agree, with a condition: the model's price per token must cite its source in the spec (unconfirmed by me; I looked only at the repo, which has no pricing file).
- **Data Governance as a stage:** folded into stage 7 (Compliance Reviewer). The data map is small: two processors, no stored question, 7-day hashed abuse log. Agree.
- **Compression not taken:** Stakes tick real data, money, irreversible, safety control and UI, so the full chain runs (stakes override completeness). The short path is not available; I did not use it.

## 4. Claims in the intent and status lines, checked against the repo
- Pack v26: `.claude/agentic.config.json` `packVersion` 26. **Confirmed.**
- "FastAPI is decided but not installed": `pyproject.toml` has no `fastapi`, `uvicorn` or `anthropic`. **Confirmed.** `CURRENT_MVP_STATUS.md` says runtime dependencies are `onnxruntime` and `numpy` only: true today, stale after this slice (stage 15).
- Judge prompt hash `24b244d2…9427`: `aveto_support/judge.py:24` `PROMPT_SHA256`, matches INV-4. **Confirmed.**
- No Dockerfile, no Bicep, no `infra/` in the tree (Glob). Everything for stages 11 to 17 is new.
- `intents/public-ask-the-docs.md` exists. `docs/runbooks/answerability-judge.md` and `REVIEW.md` exist (stage 12 input).
- **Stale or mismatched, required clarifications (the Charter governs each; none blocks):**
  - Intent says effort "as the API default"; Charter C3.1 says `high`, sent explicitly if the default differs. Use the Charter.
  - Intent table says INV-5 unchanged; Charter C5.2 grants a bounded change (intake decision). Use the Charter.
  - Intent table budget 1.8M/2.4M/3.0M; Charter 2.0M/3.0M/3.6M. Use the Charter.
  - Plan prerequisites table shows P6/P7 "pending"; `STATE.md` setup log (later) records C6.5 passed and C6.6 stated by the owner. P8/C6.7 remains open (gate file absent per the setup log; I did not look at the path, by design).
  - INV-4 text says retrieval "does not abstain" and `judge-apply` prints (a) to (d). The service JSON must map to (a), (b), (c) exactly, with (d) as a 4xx with no passage. Stage 5 states the mapping.

## 5. Risks to schedule and budget (plan 2000k, ceiling 3000k, hard cap 3600k)
Top three:
1. **Rework loops on a new public surface eat the margin.** The last tier 3 run here ended at 145% of plan, which is about 2.9M: just under this ceiling. Stage 5 (two Opus passes), 14 (adversarial Opus) and up to three review rounds at 12 each re-spawn 8 to 10 and 13. Mitigation: give stage 8's Backend Architect the Security-known weak points up front (client IP behind Container Apps ingress and `X-Forwarded-For`, in-memory limiter reset on scale-to-zero or multiple replicas, the 500-character check before any model call, no question in any log line, POST only so no question lands in URLs or access logs).
2. **Calendar time from the daily spend share, not tokens.** $10 a month is about $0.33 a day. A high-effort Sonnet call over five files of passages may cost cents (unconfirmed; no price or measurement in the repo), leaving roughly tens of questions a day. QA, verification and the 20-question gate all draw on it (C8.5), so stage 18 may span two or more days, and public visitors will exhaust the day's share quickly. Report it as a measured limit, not a defect. Verification and the gate share one hashed-IP quota (10 an hour): stage 18 must count its own verification calls inside the first batch.
3. **Cold start versus "within a few seconds".** The image carries the index and a local ONNX embedding model, loaded on a scaled-to-zero container. Cold start may exceed a few seconds (unmeasured; measured only at stage 18). The UI must show a waiting state, and the spec should say if min replicas 0 is kept. Changing it to min 1 changes the Azure cost estimate; that is a plan-level fact to report, not an action I may take.

Smaller: the image build must run `ingest` at the pinned commit inside `az acr build` (network egress to GitHub and huggingface.co at build time, covered by INV-5's `ingest` exception); `what-if` role-assignment permissions on the vault are unconfirmed (stage 11 will find out).

## 6. Outside the Charter
**None as written.** Conditional watch items, each a stop only if it occurs:
- The kill switch mechanism (flag 2 above).
- A dependency beyond `fastapi`, `uvicorn`, `anthropic` and their transitive packages (the plan's constraint; Architect names, Security reviews).
- Any live Anthropic call before stage 17 (stage 13 says not called; hold that).
- C6.7 (gate file, hash `7eb4f588…064f`) absent when stage 18 starts is a blocked prerequisite, owned by the support session; report it, do not work around it.

## 7. Hand-off to the Product Manager (stage 2, PRD, standard, ~70k)
Write `runs/public-ask-the-docs/02-prd.md`. Read only: `intent.md` (source of truth), `CHARTER.md`, `00-slice-plan.md`, this file, `.agentic/PROJECT_CONTEXT.md`, and the INV-4 and INV-5 paragraphs of `.agentic/SAFETY_INVARIANTS.md`. Do not read the codebase.
- Restate the visitor, the single job, and observable acceptance criteria taken from "Done means". Do not add scope; non-goals are the Charter's C1.3.
- Every figure the PRD asks for must be a bar fixed in the intent (gate bars, 10 per hour, 500 characters, 7 days, $10 a month). Do not invent thresholds or a "few seconds" number; if one is needed, state it as an open question for the Architect.
- Name the user-visible states for stage 3: answered, "The docs don't answer this" with the GitHub issue link, rate limited, paused for today, kill switch off, over 500 characters, judge error, cold start waiting.
- Carry forward, as PRD open questions rather than answers: kill switch mechanism, cost per question, cold start, and the per-day capacity limit (risks 1 to 3 above).
- Do not write copy, layout or architecture. Do not touch the gate set or its path.
- Exit: a PRD whose every criterion a QA role could check with a test or a measured figure.
