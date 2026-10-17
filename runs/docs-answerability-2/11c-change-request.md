# Change Request — docs-answerability-2: merge of branch `claude/docs-answerability-2` into `main`, and internal use of the attended judge step

> Owner: Release Manager (drafted by the Compliance Reviewer at the owner's order, APPROVAL_RECORD-9 C1; the Release Manager's tier 3 re-verdict is separate and not made here).
> Status: **submitted — approval PENDING. Nothing in this request is approved.**
> Release tier: **3** (owner's ruling, APPROVAL_RECORD-9, 2026-10-16; replaces the intent's tier 2).
> Depth: standard. Date of drafting: 2026-10-16. Branch HEAD when drafted: `66e73a2`.

## Read this first: what is and is not approved

- **The release action (merge to `main`, and any push) is NOT approved.** APPROVAL_RECORD-1 to -9 approve specific rules and decisions, none of them a merge or a push: budget and plan (1); rule 5 judge model (2); rule 6 processor (3, 6); stage 1 sends (4); rule 4 INV-4/INV-5 words (5) and one INV-5 edit (8); D1 deny list (7); tier 3, D6 acknowledged, `/aveto-judge-seen` held, packet set aside (9). Record 9 says in terms: "Do not merge or push", and lists "push, merge, deploy, announcement, unattended use ... the S5 fix, the S6 rule's disposition, the retrieval-gate acceptance (R-A)" as **not approved**.
- **No merge or push has been requested of the owner** in any artefact I read, so there is no record to confirm. This request is the vehicle for asking; it is not the asking itself (the owner's typed yes in the driving session is, and it has not happened).
- **Named approver of the release action: Gopal Patwa (owner).** Recorded at the owner's order (record 9: "record me as the named approver of the release action"). Naming the approver is a designation, not a grant. Decision: **PENDING.**
- `RELEASE_APPROVAL_PACKET.md` (an untracked support-session draft) was set aside by record 9 as out of scope and unsigned. It is not part of this request and not evidence of anything.

## Change summary

In operator terms:

1. **Code (`aveto_support/`):** three files change relative to `main`: `__main__.py`, `judge.py`, `judge_eval.py` (QA, `09-release-qa.md`; Release Checklist rollback step 2). They add two offline commands, `judge-input` and `judge-apply`, and an `eval --verdicts` mode. The program has no model client, makes no network call and starts no process in these commands (`test_program_offline_no_model`). `retrieve` and ingestion are untouched.
2. **Operator path (`.claude/`):** a Claude Code subagent `aveto-answerability-judge` pinned to `claude-sonnet-5-5` (record 2), with a deny list extended by D1 (record 7), and the skill `/aveto-judge` that the operator types to run it in their own attended session. This is where data leaves the machine (to Anthropic, through the owner's own session; records 3 and 6; see `11b-vendor-risk.md`).
3. **Safety-control text:** INV-4 and INV-5 in `.agentic/SAFETY_INVARIANTS.md` rewritten to describe the judge (record 5), plus one INV-5 edit (record 8). Reverting them later is itself a rule 4 action (below).
4. **Eval material and run records:** `runs/docs-answerability-2/` (records, audits, the fifth gate set and key, three Security probe scripts that carry a `# ruff: noqa` first line, D6), the eval-only skill `/aveto-judge-seen` (on hold, see C3), docs (`README`, `.agentic/CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md`, ADR 0008).
5. **Behaviour the operator sees:** after `judge-apply`, either `retrieve`'s output unchanged plus a `Deciding signal` line, or exactly `no confident match` plus a `Deciding signal` line. Plain `retrieve` never abstains and is unchanged.

**What it is not:** no service, no unattended or scheduled use, no API key, no `claude -p`, no deploy, no announcement. Nothing is posted (INV-1).

## Change type

- [ ] **Standard**
- [x] **Normal** — needs review and approval before the action. Tier 3 and a safety-control change; not eligible for Standard.
- [ ] **Emergency**

## Risk & tier

- **Release tier: 3** (record 9). Tier 3 adds, over tier 2: explicit human approval, a dry run on a fixture before live, audit event coverage manually verified, a post-launch monitoring plan, and a change request with a named approver (record 9, "Recorded effect"). Status of each is in "Tier 3 requirements" below.
- **Risk if it fails:**
  - *Product:* the judge over-abstains (3/19 and 4/28 seen) or under-abstains; only the operator reading `no confident match` or a shown file is affected. Abstaining is "never worse than showing a wrong file" (intent), so the failure is lost coverage, not a wrong claim. End to end only **16 of 24** answerable questions end with the right file shown after judging (5 lost to retrieval, 3 to over-abstention).
  - *Data:* a question typed by the operator, with the session context (owner's email and name, git lines, environment lines, instruction files), goes to Anthropic. Vendor assurance fields are UNKNOWN (`11b-vendor-risk.md`).
  - *Safety text:* INV-4 and INV-5 on `main` would describe a system that sends data through the operator's session. If the words ever stop matching the code, the safety control is false.
  - *Operator environment:* S6 and S5 (below).
- **Affected systems / tenants:** this repository's `main`; the owner's own Claude Code sessions. No tenants, no customers, no hosted system, no deployed system, no shared infrastructure. No other operator is named in any artefact.

## Tier 3 requirements: where each stands

| Requirement | State | Evidence |
|---|---|---|
| Explicit human approval per the rules | **Met for every gated action the slice took** (rules 4, 5, 6: records 2 to 8). **Not met for the release action itself: PENDING.** | `09-release-checklist.md` approvals walk; records 1 to 9 |
| Dry run on a fixture before live | Met (as the Release Manager found for the tier 2 walk): two public eval-set questions before the INV words (record 4; `01-measurement.md`), the smoke r049 (`05a-smoke.md`), then 48 seen-set spawns before the 48 gate-set spawns | `01-measurement.md`, `05a-smoke.md`, `05-seen-check.md` |
| Audit event coverage manually verified | Met: Security cross-checked the spec's audit events against the code | `08-security-review.md` section 8 |
| Post-launch monitoring plan | **In progress in parallel; not yet read by me.** Pointer: `runs/docs-answerability-2/11-monitoring-plan.md` (being written by the SRE). I did not see it and do not count it as met. | `runs/docs-answerability-2/11-monitoring-plan.md` |
| Change request with a named approver | This document; approver named, **approval PENDING** | here |
| Vendor risk and DPA status for the third-party flow (enterprise overlay; HUMAN_APPROVAL_RULES rule 6) | Recorded "from what we know": vendor and scope established; **DPA, retention, training terms, certifications, subprocessors and residency are UNKNOWN, owner to state** | `11b-vendor-risk.md` |
| Release Manager verdict re-run for tier 3 | Not yet done at drafting. The prior verdict (`09-release-checklist.md`) was GO WITH CONDITIONS under tier 2 and said it would revert to NO-GO on the monitoring plan and the named approver if tier 3 were ruled. | `09-release-checklist.md` C1 |

## Open conditions (carried from the Release Manager's verdict, status as of drafting)

I could confirm only what an artefact shows. "Open" means no artefact I read records a resolution.

| # | Condition | Status | Basis |
|---|---|---|---|
| **C1** Rule the tier | **Resolved:** tier 3 | Record 9 |
| **C2** S6: `.claude/settings.local.json` rule `Bash(uv run -q --project * python * seen_payload.py *)` auto-approves arbitrary `python <anything> seen_payload.py <anything>` in this worktree; removes a permission prompt that INV-5's session exception relies on | **OPEN.** Record 9 expressly leaves "the S6 rule's disposition (still the owner's: delete, narrow or accept)" undecided. The file is gitignored, so no git rollback removes it. Not actioned by any agent (the Orchestrator does not edit permission settings). | `08-security-review.md` S6; record 9 |
| **C3** S5: quote breakout in `/aveto-judge-seen` (`$ARGUMENTS` inside single quotes in a `!` line) | **Held, not fixed.** The owner ruled the seen-set skill "is not used again until S5 is fixed". The fix edits a frozen method file and is a separate, later decision. The code path stays on `main` if merged. A hold is a rule the owner follows; nothing technical stops the skill from being invoked (it is model-invocable by design, F12). | Record 9; `08-security-review.md` S5 |
| **C4(a)** One run of `uv run ruff check`, `uv run mypy`, `uv run pytest` by a session with a shell, on the final tree | **OPEN as far as the artefacts show.** The Release Manager had no shell and relied on the Orchestrator's report after D6 (ruff all checks passed, mypy clean, 375 passed, 12 deselected). I have no shell either and did not run it. Re-run it on the exact commit that would be merged. | `09-release-checklist.md` C4a |
| **C4(b)** D6 (`# ruff: noqa` first line in three Security probe scripts, commit `3e1c939`) | **Acknowledged by the owner.** | Record 9 |
| **C5(a)** Approver identity, a person and not a role | **Partly resolved:** record 9 names the approver as "Gopal Patwa (the owner, in the driving session)". Records 1 to 8 say "owner" without the name; the link from "owner" to Gopal Patwa is record 9's statement, not a change to those records. The `trace.json` operator handle: I did not check; the Release Manager found no `trace.json`. | Record 9; `09-release-checklist.md` |
| **C5(b)** STATE corrections (record 8 in the Approvals table; stale stage row) | **Done per STATE:** the Rule 4/rule 6 stage row says "corrected by the Orchestrator per release condition C5", citing records 5, 6, 8. I did not audit the Approvals table. | `STATE.md` line 23 |
| **C5(c)** One owner line on the DPA and vendor-risk position | **OPEN.** `11b-vendor-risk.md` records the position as UNKNOWN on every field except vendor, channel, data and scope. The owner states the rest. | `11b-vendor-risk.md` |
| **C6** Stage 10 docs carry the full set of figures and no capability claim | Docs stage ran (`10-docs.md`, `10b-architecture-docs.md` present). **Not re-verified by me**; the Release Manager's re-verdict should check that README and `CURRENT_MVP_STATUS.md` state only the recorded figures. | `09-release-checklist.md` C6 |
| **R-A** Retrieval gate exit 1 on the fifth set (19/24 = 79.2% answerable, required at least 80%; not a registered bar) | **NOT ACCEPTED.** Record 9 lists it as not approved. The owner accepts it in their own words, or declares it relevant. It bounds what any document may claim. | `09-release-checklist.md` R-A; record 9 |

Accepted-by-design risks R-B to R-F (bar 2 passes by one question at both stages; advisories S1 to S4, S7, S8; the failing `-m model` test `test_sample_derivation_reproducible`; harness behaviour no test shows; self-reported telemetry) are as stated in `09-release-checklist.md`. They are not accepted by this request.

## Evidence figures (verbatim from the Release Manager; not rounded)

| Measure | Stage 5 (seen-set sample) | Stage 7 (fifth gate set, scored once) |
|---|---|---|
| Bar 1 (abstain on unanswerable) | 20/20, registered at least 16: MET | 24/24, registered at least 20: MET |
| Bar 2 (answerable with right file in top 5, not abstained) | 24/28 (85.7%), registered at least 23: MET, one question of margin | 16/19 (84.2%), registered 80%: MET, one question of margin |
| Judge errors | 0 | 0 |
| Best-score rule, same set | NOT MET on both bars | NOT MET on both bars |
| End to end (diagnostic) | n/a | 16/24 |
| Retrieval gate on the fifth set | n/a | 19/24 = 79.2%, required 80%: exit 1 |

## Implementation plan

- **Steps:** none are authorised. If and when the owner types a yes to the release action, the action is a merge of `claude/docs-answerability-2` into `main` (and, separately, any push, each needing its own owner yes: `09-release-checklist.md`, "What internally releasable allows"). Method (merge commit versus squash versus fast-forward) is the owner's. **It must be named at merge time because the full-revert command in the rollback plan assumes a merge commit.**
- **Before the action (preconditions I recommend; the owner may waive any):** C4(a) final-tree run recorded; C2 disposition recorded; monitoring plan read and accepted; `11b` UNKNOWN fields answered or explicitly accepted as UNKNOWN; R-A accepted or declared relevant; the Release Manager's tier 3 re-verdict.
- **Estimated duration:** one git operation; minutes. No build, no migration, no deploy.
- **Maintenance window:** none. No downtime; nothing is running that the merge could interrupt. The product is a local command-line program and an operator's Claude Code session.
- **After the merge, to use the judge step:** Claude Code loads `.claude/agents` and `.claude/skills` at session start, so a session opened on `main` after the merge is the one that has the new files. Attended only, typed by the operator, as `/aveto-judge`. Do not use `/aveto-judge-seen` (C3).

## Rollback plan

Source: `02-tech-spec.md` section 13, checked against the tree by the Release Manager (`09-release-checklist.md`, "Rollback plan", gate MET). I have not re-checked the paths.

- **Trigger to roll back:** any of: the judge step misbehaves in attended use (a judge error, an unexpected tool offered or used, `no confident match` printed where passages were due, or passages shown after a `NOT_ANSWERABLE`); the INV-4 or INV-5 text found false against the code; a session-context item found sent that INV-5 does not name; a monitoring signal crossing a threshold the owner sets in the monitoring plan; the owner's decision.
- **Steps, least to most:**
  1. **Before any merge:** do not merge, or `git revert` the slice commits on the branch in reverse order. Nothing reaches `main` until the owner merges.
  2. **After a merge, disable the operator path only:** `git rm -r .claude/skills/aveto-judge/` and commit. `judge-input` and `judge-apply` stay offline and inert without a reply; `retrieve` is untouched.
  3. **Full revert:** `git revert -m 1 <merge-commit>` and the regression command. This assumes a merge commit. **INV-4 and INV-5 return to their pre-slice text, which is a safety-control change (rule 4): it needs the owner's own words before the revert lands. The revert is never applied on an assumed approval.** README and `CURRENT_MVP_STATUS.md` revert with it.
  4. **D1 only (the seven harness tools):** `git apply -R` of the fenced diff in `runs/docs-answerability-2/03a-d1-proposed-diff.md` (the spec's `D1-diff.md` name is wrong; no such file), with the owner's approval; run `uv run pytest tests/test_judge_artefacts.py`; start a fresh-load session.
  5. **Eval data only:** `git rm -r runs/docs-answerability-2/judge-check/`; no product effect.
  6. **Outside git (rollback cannot reach these):** the gitignored `.claude/settings.local.json` rule (C2) and Claude Code transcripts in `~/.claude/projects/` (hold the full payloads and replies) are the owner's to remove or keep. Anything Anthropic retains is governed by terms that are UNKNOWN (`11b`); no repo rollback recalls data already sent.
- **Tested?** The rollback is a plan; the Release Manager marks the gate MET on the existence of the spec section and its paths. Reverts were **not executed** by any agent (rules 2 and 3: nothing was reverted, pushed or merged). A dry run of step 2 or 3 on a throwaway branch has not been recorded. **The tier 3 gate wording is "no, not tested: blocker for Tier 3".** The owner should rule whether a recorded dry run of step 3 on a scratch branch is required before the merge, or accept the plan as written. I recommend the dry run, since it costs minutes and needs no approval (it touches nothing shared) except that its INV text revert must not be committed to the real branch.

## Validation

- **How success is confirmed after the action:** `git log` and diff on `main` show the branch's commits; `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest` clean on the merged tree (LOCAL_COMMANDS regression; the `-m model` suite has one known failure, R-D); `INV-4`/`INV-5` on `main` are byte-equal to records 5 and 8 as applied; the first attended `/aveto-judge` run after the merge shows judge model `claude-sonnet-5-5`, 0 offered tools, 0 `tool_use`, and an output of one of the two shapes above.
- **Who watches, and for how long:** the signals, thresholds, owner and watch window are in `runs/docs-answerability-2/11-monitoring-plan.md` (SRE, in progress; not read by me). The Release Manager's minimum content for that plan was: the operator's own observations of the two outputs, the judge-error count, the over-abstention rate against 3/19 and 4/28, and any run where offered tools is not 0. Thresholds are the owner's; none is set here.

## Approvals

| Role | Name | Decision | Time (UTC) |
|------|------|----------|------------|
| Release Manager | not yet named; tier 3 re-verdict pending | **PENDING** | n/a |
| Compliance approver | Gopal Patwa (owner) is the only human named in any record; the Compliance Reviewer agent recommends and does not approve | **PENDING** (compliance disposition: see below) | n/a |
| Human owner (Tier 3 per `docs/HUMAN_APPROVAL_RULES.md`) | **Gopal Patwa** (named approver of the release action, record 9) | **APPROVED, as given by the Charter** (slice `land-answerability`, C8.5 and C8.2; `runs/land-answerability/APPROVAL_RECORD-1.md`): approve landing by pull request into `main`; the merge is the owner's own act and is not covered. Date 2026-10-17; time of day not recorded. Tested rollback: **yes**, see `runs/land-answerability/02-rollback-rehearsal.md`. (Supersedes the PENDING originally recorded here.) | 2026-10-17, time of day not recorded |

**Compliance Reviewer position (recommendation, not an approval):** **required-fix, conditional pass.** From a compliance standpoint the merge is not blocked by anything the artefacts show about the product itself: the rule 4, 5 and 6 approvals exist, the program is offline, the Security review has 0 blocking findings. It should not be approved until the owner either states the DPA/retention/training position for the account (`11b`) or records in their own words that the release proceeds with those fields UNKNOWN. A new third-party data flow without a stated DPA position is the exact case the compliance role does not pass silently. This is an owner decision; if closing the gap needs a DPA or terms change, that is the owner's and legal's, not a drafting fix.

Time of day is recorded nowhere in records 1 to 9 (dates only). The owner may add it when approving.

## Communications

- **Before:** the owner is the only stakeholder named in any artefact. No customers, no status page, no team. If others are to be told, the owner says who.
- **After:** nothing is posted or announced. The verdict is "internally releasable, not announced" (`09-release-checklist.md`). Any external description of the result as a product capability needs figures as stated above (16/24 end to end; retrieval gate exit 1) and the owner's own word.

## Hand off

- **To the owner:** this request; C2 and the other open conditions; R-A; the `11b` UNKNOWN fields; whether to require a recorded rollback dry run; and, separately and only if wanted, whether and how to merge or push.
- **To the SRE:** keep `11-monitoring-plan.md` consistent with the triggers above.
- **To the Release Manager:** re-run the tier 3 verdict once the monitoring plan is read and this request's conditions are in view.
- **To the engineer (execution) and Post-Launch (the record closes after the validation window):** only after the owner approves the release action. Neither has anything to execute now.
