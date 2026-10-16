# Release Checklist, Tier 3 re-run — docs-answerability-2 (stage 13: Release Manager, fresh spawn)

> Owner: Release Manager Agent (fresh spawn; did not build, review, score, plan or draft anything in this slice). Depth: standard. Nothing here is an approval.
> Tier: **3**, as ruled by the owner in `APPROVAL_RECORD-9.md` (2026-10-16). The intent named 2. Tier and depth are not changed here.
> Worktree `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-answerability-2`, branch `claude/docs-answerability-2`. HEAD at the start of this spawn: `e7c623e` (from the session's commit list). Freeze `bca0e403a69a5cda7826ea36897734bc63dc7b87`.
> Read: `.agentic/SAFETY_INVARIANTS.md`; playbook `docs/RELEASE_GATES.md`, `docs/HUMAN_APPROVAL_RULES.md`, `templates/CHANGE_REQUEST_TEMPLATE.md`; `09-release-checklist.md`, `09-release-qa.md` section 5, `APPROVAL_RECORD-1` to `-9`, `STANDING_INSTRUCTIONS.md`, `STATE.md`, `08-security-review.md` (findings table and section 9), `11-monitoring-plan.md`, `11b-vendor-risk.md`, `11c-change-request.md`, `12-tier3-dryrun-audit.md`, `05-seen-check.md` and `07-gate-scoring.md` (figure lines only), `README.md` (judge-step section), `.agentic/CURRENT_MVP_STATUS.md` (lines 40 to 84), `SUPPORT_REPLIES.md` (Replies 3 and 4).
> Not opened, by the brief: `evals/retrieval-heldout-5*.toml`, `judge-check/batch-2.txt`, `judge-check/q/`, `06-label-review.md`, any `diffs.md`. `RELEASE_APPROVAL_PACKET.md` (untracked, set aside by the owner in record 9) was ignored and is not an approval of anything.

## 1. Verdict (read this first)

**GO WITH CONDITIONS — internally releasable as a branch candidate, not announced. The slice is NOT cleared to land.**

Said without the label:

- **Does it land (merge, push, PR, tag, deploy)? No.** At tier 3, today, six gate items are not met. Gates fail closed; read strictly, that is a no-go for landing, and I am not softening it into "go". The conditions below are the list of what has to change first. Every one is the owner's, or a named role's, to resolve. I resolve none.
- **Is the branch still an internal candidate? Yes**, on the same grounds as the tier 2 verdict: both registered judge bars were met once on the held-out set, nothing was voided, Security found 0 blocking issues, the freeze held, and every rule 4, 5 and 6 action the slice took has a typed owner record. That label allows the close-out and docs to continue. It authorises nothing outward.
- **The release action has not been asked of the owner, and the change request approval is PENDING.** Record 9 says in terms "Do not merge or push" and lists push, merge, deploy, announcement, unattended use, the S5 fix, the S6 disposition and the retrieval-gate acceptance (R-A) as **not approved**. A merge or a push is not approved.

**The six tier 3 items that are NOT MET (each blocks landing):**

1. **Human approval of the release action itself** — not requested, not given (rule 3).
2. **Change request approved** — recorded, approver named (Gopal Patwa), decision **PENDING**.
3. **Vendor risk: DPA in place** — **UNKNOWN**. The DPA, retention, training use, terms and plan are not stated by anyone. Nothing is treated as met on an unknown.
4. **Rollback tested** — never rehearsed. The change request template says "no → blocker for Tier 3".
5. **Monitoring plan thresholds** — the plan exists, but its thresholds are the SRE's proposals; the owner has set none. (The plan is MET WITH GAPS as a document; its stop rules are not binding until the owner adopts them. I count it here because a stop rule nobody adopted is not a control.)
6. **Final-tree regression on the commit that would be merged** — not run by me (no shell) and not recorded on `e7c623e`. See "What I ran".

**Met, or met with gaps:** the dry run on a fixture (MET); audit event coverage (MET WITH GAPS, G1 to G9); the monitoring plan as a document (MET WITH GAPS); explicit approval for every rule 4, 5 and 6 action the slice took (MET).

**Carried forward plainly (none is new, none is softened):**

- **Retrieval gate exit 1 on the fifth set: `answerable: 19/24 (79.2%) required >= 80% FAIL`.** Not a registered bar. **R-A is not accepted by the owner** (record 9 lists it as not approved). End to end only **16/24** answerable questions end with the right file shown after judging.
- **Bar 2 passed by one question at both stages** (stage 5: 24/28 against 23 needed; stage 7: 16/19 = 84.2% against 80%, 15 would have failed). The **best-score rule was NOT MET on both stages** (and the judge beat it on both).
- **S5 and S6 are the owner's and not decided in the record.** Advisories S1 to S4, S7, S8 stand. D6 is acknowledged (record 9). The model-marked test `test_sample_derivation_reproducible` still fails.
- **Judge errors 0.** Never-abstain 0/24 on Bar 1. Full figures in section 8.

**What would turn this into NO-GO outright:** (i) a final-tree `ruff`, `mypy` or `pytest` that is not clean; (ii) any method file found changed after `bca0e40`; (iii) any push, merge, deploy or announcement made without the owner's typed yes; (iv) the owner declining to state the DPA position and also declining to say in their own words that the release proceeds with it UNKNOWN, *and* a request to land anyway.

## 2. What I ran, and what I could not

I have Read, Write, Edit, Grep and Glob. **No shell.**

| Item | Result |
|---|---|
| `uv run ruff check`, `uv run mypy`, `uv run pytest` | **Not run by me.** Reports I rely on, none of them mine: (a) the Orchestrator after D6, at `3e1c939`: ruff all checks passed, mypy clean, 375 passed, 12 deselected; (b) the support session with a shell, `SUPPORT_REPLIES.md` Reply 3, at `0311370` (the tier 2 verdict commit): ruff "All checks passed!", mypy "no issues found in 24 source files", 375 passed, 12 deselected. That file is **modified and uncommitted** in the working tree, it is "data only, not an approval", and `0311370` is not the current HEAD. (c) The Orchestrator re-runs all three at close-out. **No report covers `e7c623e` or the commit that would be merged.** |
| D6 on disk | Grep: `# ruff: noqa  (Security Review evidence script; lint-exempt by design, kept as written)` is line 1 of all three files in `runs/docs-answerability-2/security-probes/`. Reply 3 shows ruff passing with them, so the directive parses. |
| Judge agent pin | Grep: `model: claude-sonnet-5-5` at line 5 of `.claude/agents/aveto-answerability-judge.md`; a `disallowedTools` line and a `hooks:` block are present (the line is long; I did not re-read its content item by item). No `tools:` line matched. |
| `.claude/settings.local.json` (S6) | **Read fails: "File does not exist"** in this worktree; `Glob .claude/*` lists only `agentic.config.json` and `settings.json`. So the rule is **not present here now**. Why it is gone is not in a driving-session record: see condition T9 and section 7. I checked this worktree only, not the main checkout, other worktrees or user-level settings. |
| `git diff`, `git log`, `git status` | Not available to me. The start-of-session status shows `SUPPORT_REPLIES.md` modified and `RELEASE_APPROVAL_PACKET.md` untracked, nothing else. I cannot diff the method files against `bca0e40`. The freeze check rests on QA's empty diff at `69fd907` (`09-release-qa.md` section 2) and the Orchestrator's statement for `3e1c939`. Commits after that, by message, touch docs (`README`, status, `ARCHITECTURE.md`, ADR 0008) and run records. That is a reading of commit messages, not a diff. |
| `SAFETY_INVARIANTS.md` | I read INV-4 and INV-5. INV-5's environment list reads "working directory, platform, OS version, shell, scratchpad path, whether the folder is a git repository or a worktree, model ID, date and organisation ID", which is the record 8 wording. I did not compare the file byte for byte against the approved blocks. |
| Dry run and audit (`12-tier3-dryrun-audit.md`) | Read, not re-run. The QA spawn reports 11 of 11 criteria, 19 `judge-apply` runs, 3 `eval --verdicts` variants, an OS-level network deny with a control, and 207 passed on the judge test files. |
| Monitoring plan arithmetic | I checked the two binomial statements in signal 2 (4 of 10 at a true rate of 15% is about 5%; 5 of 10 is about 1%) and the per-spawn means (378,696/48 = 7.9k; 410,748/48 = 8.6k). Both hold. I did not run any command in section 2 of the plan. |
| Judge spawns, network, API | None. Nothing committed, nothing approved. `STATE.md` not edited. |

## 3. Tier 3 additions, judged one by one

Legend: **MET** / **MET WITH GAPS** / **NOT MET**. "Evidence" is the file that proves it. I read it; where I say "taken from", I did not re-run it.

### 3.1 Explicit human approval per `HUMAN_APPROVAL_RULES.md`

| Part | Judgement | Evidence and reasoning |
|---|---|---|
| Rule 4 (safety controls): INV-4/INV-5 words, the two-line `NOT_ANSWERABLE` output, D1, the INV-5 environment edit, sequencing of the two stage 1 spawns | **MET** | Records 4, 5, 7, 8. Each quotes the owner's typed words and names the specific action. Dates 2026-10-12 and 2026-10-13. |
| Rule 5 (LLM in a deterministic path): judge pinned to `claude-sonnet-5-5` | **MET** | Record 2. |
| Rule 6 (data processor and what it receives): Anthropic through the owner's own session, attended only; then the session context named | **MET as an approval; the surfacing it requires is incomplete** | Records 3 and 6. Rule 6 says the agent surfaces "the processor, the data it would receive (with classification), and the DPA status" before the human approves. `02c-rule6-question.md` named the processor and the data. The DPA status was not surfaced then and is **UNKNOWN** now (`11b`). The approval stands, because the owner gave it in their own words. It was given without a stated DPA position, and that has not been repaired. |
| Tier ruling | **MET** | Record 9, "I rule tier 3". The tier is the owner's. |
| D6 acknowledged; `/aveto-judge-seen` held; `RELEASE_APPROVAL_PACKET.md` set aside | **MET** (acknowledgements, not safety approvals) | Record 9. |
| **Rule 3: the release action itself (merge, push)** | **NOT MET: not requested, not given** | No artefact shows the owner was asked the specific question `HUMAN_APPROVAL_RULES.md` "How to ask for approval" requires (what, why and which rule, what is reversed if denied, the smallest request). `11c` says in terms: "No merge or push has been requested of the owner... This request is the vehicle for asking; it is not the asking itself." Record 9: "Do not merge or push." There is nothing to confirm. |

**Approver identity (rule 3: "an identity, not a role").**
- Record 9 names **Gopal Patwa** ("the owner, in the driving session"). Records 1 to 8 say "owner". The link from "owner" to Gopal Patwa is record 9's own statement; I do not rewrite records 1 to 8.
- **There is no `trace.json` for this slice.** Glob over `runs/` finds `trace.json` for seven other slices and none in `runs/docs-answerability-2/`. Rule 3 asks for "the same handle used as the run's `operator` in `trace.json`". That handle is therefore not recorded where the rule says. A name in prose is the best the record offers. I do not infer one.
- All nine records carry a date, none a time of day. Rule 3 also asks the Release Manager to record the time. For the release action that will have to be captured at the moment of approval.

### 3.2 Dry run on a fixture before live: **MET**

Evidence: `12-tier3-dryrun-audit.md` part (a), taken from, not re-run.
- Criteria A1 to A11 were written before the run. The result is 11 of 11: three `judge-input` payloads (deterministic hash, one stderr line, nothing written); `judge-apply` on ANSWERABLE (stdout equals `retrieve`'s plus one signal line, compared with `diff` and a negative control); on NOT_ANSWERABLE (exactly two lines, no passage); on 5 bad-reply cases in the table plus 7 further exit paths (exit 4 or 2, one fixed category, reply text never echoed, a planted marker never seen); `eval --verdicts` on a synthetic 3-question file with hand-written expectations; and three refusals. `.aveto-judge/` was empty after every case. The commands were also run under an OS-level network deny, with a control that proved the deny.
- Fixtures were two questions from the dev eval file and a made-up one. The held-out fifth set was not touched. Replies were hand-written.
- **What the dry run does not cover (stated, not a defect):** no model ran in it. It proves the offline half (the program's behaviour on any reply). The model half was exercised live on eval questions only, at stages 5 and 7 (96 spawns, 0 judge errors, 0 tools). **The operator path `/aveto-judge`, where the main session retypes the payload into the judge prompt (spec 14.1), has never been measured** (`11-monitoring-plan.md` section 1, "What cannot be observed"). The bars describe the eval path. Any figure quoted from real use must say so.
- "Before live": nothing has been used live on the operator path. Order is respected.

### 3.3 Audit event coverage manually verified: **MET WITH GAPS**

Evidence: `12-tier3-dryrun-audit.md` part (b), 29 rows by reading code, the part (a) runs, the committed stage 5 audit files, and 207 passing judge tests; plus `08-security-review.md` section 8 from the tier 2 walk. Verdict there: PASS WITH GAPS. The gaps, as the QA spawn rates them:

| Id | Gap | My reading |
|---|---|---|
| G1 | The spawn (the INV-5 egress) on the operator path has no program-side record; only the harness transcript | By design (no event store, spec section 7). Disclosed. It means **no local log says a question was sent to Anthropic at a given time.** For a third-party data flow at tier 3 that is worth the owner's eye: the only trace is the operator's own transcript directory. |
| G2 | The printed result carries verdict, prompt id and hash, not the model, input hash, time or operator; on the operator path nothing checks the model or tool use (S4) | Low. The eval path checks; the operator path does not. |
| G3 | A refused judge tool call leaves only a hook message in the transcript | Low. The hook has never fired (0 tools offered). |
| G4 | Cleanup silently skips a symlink `reply.txt` (S2) | Low. |
| G5 | A void `record` into a stage directory that already holds a valid run leaves the earlier `verdicts.toml`, `diffs.md` and `audit.json` in place while the new `audit.md` says VOID. Confirmed by a scratch probe; no test | **Non-blocking eval-tool hazard.** No further `record` is planned. It matters only if someone reruns `record` into `stage5/` or `stage7/`. Not fixed; the fix is a later slice's. |
| G6 | An `ApplyError` inside `record` leaves no `audit.md` for that attempt | Low. |
| G7 | `diffs.md` stores the full, uncapped model reply for differing and errored rows, and is committed. Neither QA nor I opened any `diffs.md` | Low; deliberate. A reviewer should read it before any publication. I cannot say what it holds. |
| G8 | A non-domain exception in `judge-apply` ends in a traceback, exit 1, no fixed category | Low. Reading only; no test. |
| G9 | Context drift (what the harness attaches) is visible on the eval path and not on the operator path | Low; INV-5 already says the list is incomplete. |

None breaks INV-1, INV-4 or INV-5, and none is a missing record for an action that sends data in the program's own code. G1 is the one that is missing a record for the send, and it is a design choice, not an omission. Advisories S1 to S4, S7, S8 touch audit as listed in the QA file; unchanged.

### 3.4 Post-launch monitoring plan: **MET WITH GAPS**

Evidence: `11-monitoring-plan.md` (SRE, fresh spawn, depth standard).

What it does well: it says plainly there is no service, no telemetry and no on-call, and defines no availability SLO. It lists 14 signals each with a command that exists, a baseline copied from the recorded figures, a watch value and a stop value. It sets zero tolerance on offered tools and `tool_use`. It has a four-weekly offline re-check (steps A to F), re-evaluation triggers that require a new pre-registered check rather than a reused result, a runbook with the one pre-authorised mitigation (stop typing `/aveto-judge`; `retrieve` alone stays), a section of what is not monitored, and the open items. It collects no user data and proposes no collector. Its "stop" for the operator is to not run the judge; a revert of INV-4/INV-5 still needs the owner's own words (rule 4).

Gaps, each stated by the plan itself or visible in it:
1. **Every threshold is the SRE's proposal. The owner sets the final ones** and has not. A stop rule the owner has not adopted is a default, not a commitment. (Condition T5.)
2. **"Pre-authorised" mitigation is the SRE's wording.** An SRE agent cannot authorise anything; the owner's adoption of the plan is what would make "stop typing the command" a standing rule. (Condition T5.)
3. **The operator path is not measured and its accuracy cannot be observed** (the plan says so). The monitoring is therefore of the harness around the judge (model, offered tools, `tool_use`, base-dir line, prompt hash, pins, frozen files), and of the operator's own tally. It is not a measure of whether real answers are right. The plan names that limit; it must travel with any claim.
4. **No `docs/runbooks/` copy** (the plan lists it as a Tech Writer follow-up, not done). The runbook exists only in a run record, which a later user of the repo may not see.
5. **No revert has ever been rehearsed** (the plan proposes one; not done). See 3.5 below.
6. **The tally is manual, per operator, and self-reported**; a quiet period proves nothing (the plan says so). Cadence is four weeks. There is no one but the owner to read it, and the owner is also the only operator named.
7. **Corpus pin, key-prefix hash and git-diff checks (signals 12, 13, 14) need a shell and a person who runs them.** Nothing runs them automatically; the plan does not claim otherwise.

### 3.5 Change request with a named approver (enterprise contexts): **NOT MET** as an *approved* request; MET as recorded and named

Evidence: `11c-change-request.md`, status "submitted — approval PENDING".
- Recorded: yes. Change type Normal. Summary, risk, tier 3, rollback, validation, approvals table, communications, hand-off are all filled.
- Named approver: **Gopal Patwa (owner)**, per record 9. "Naming the approver is a designation, not a grant."
- Decision: **PENDING.** Release Manager row: "not yet named; tier 3 re-verdict pending". That row is mine to fill only when I sign off a landing, and I do not sign one.
- **Rollback "Tested?": no.** `11c` says so itself: "The tier 3 gate wording is 'no, not tested: blocker for Tier 3'". The template line is `Tested? <yes — when / no → blocker for Tier 3>`. I take that at its word. A recorded rehearsal of rollback step 3 on a scratch branch (nothing shared, no approval needed, the INV text revert not committed to the real branch) would close it, or the owner records in their own words that the plan is accepted as written. (Condition T4.)
- `11c` records one date-only fact I confirm: "Time of day is recorded nowhere in records 1 to 9".
- `11c` marks the monitoring plan "not yet read by me" and C6 "not re-verified by me". I have read the plan (3.4) and checked C6 (section 7 below).

## 4. Vendor risk and DPA (rule 6; the enterprise gate "New subprocessor risk-assessed + DPA in place")

Evidence: `11b-vendor-risk.md` (Compliance Reviewer; status "draft — for the owner's decision. Nothing here is approved, accepted or recorded as accepted").

**Judgement: NOT MET.**

What is established (sourced to artefacts and records): the vendor (Anthropic); the channel (the owner's own attended Claude Code session, subscription, no API key, no `claude -p`, nothing unattended); the data shared (question; payload of public documentation passages; the fixed prompt; and the harness-attached session context: project instruction files, **the owner's personal email, the git user name, a local username, an organisation ID**, git lines, environment lines; plus the main conversation's copy); that none of the harness-attached items can be removed by this repo; that no customer data, credential or held-out label was sent in any run; that the judge had no tools in 96 of 96 audited spawns. Rule 6 approvals exist (records 3, 6) and record 8 widened the named list.

What is **UNKNOWN — owner to state** in `11b`, and which I therefore treat as **not met**:

| Field | State |
|---|---|
| DPA in place | UNKNOWN |
| Anthropic terms and plan the owner's account is under (consumer, team, enterprise, other); whether the account is personal or a company's | UNKNOWN |
| Data retention by the vendor for this account | UNKNOWN |
| Use of this account's prompts for training or improvement | UNKNOWN |
| Whether the terms permit this use (an eval harness driving a subagent in an interactive session) | UNKNOWN, and a contract reading I do not make |
| Subprocessors, certifications (SOC 2, ISO 27001, ISO 42001), recent audit, status page | UNKNOWN |
| Data residency, cross-border transfer basis | UNKNOWN |
| Liability and breach notification | UNKNOWN |
| Export and deletion on termination | UNKNOWN |

The Compliance Reviewer's own position is "required-fix, conditional pass": it "should not be approved until the owner either states the DPA/retention/training position for the account or records in their own words that the release proceeds with those fields UNKNOWN". I agree and add one thing. Unknown is not "met" and it is not "waived". Skipping a gate is a rule 4 item and the bypass is the human's alone. If the owner chooses to proceed with the fields UNKNOWN, that has to be their recorded sentence, and the checklist will then say "gate waived by the owner, record N", not "MET".

Risk rating, as the Compliance Reviewer gives it and nobody has accepted: inherent low to medium; **residual low for the slice as run (public text, eval questions); medium-unknown for open-ended internal use** until the DPA, retention and training fields are stated. "Residual risk accepted by: nobody."

Two things the owner should see from `11b` as they bear on the release rather than the paperwork:
- **After release, the question stops being eval text and becomes whatever the operator types**, which the intent itself classes as real user data. The vendor file recommends an operating rule: public-docs questions only until the DPA and retention fields are stated, a policy control with no technical enforcement (no redaction, no classifier). The owner has not adopted it. Until the owner adopts or declines it, this verdict does **not** treat open-ended use on non-public text as released.
- The owner's personal email and name ride on every request. That is within what records 3 and 6 name. It is not within a stated DPA.

## 5. Enterprise and governance gates (`RELEASE_GATES.md`), walked

Record 9 ordered three of these artefacts (monitoring plan, vendor risk, change request). No overlay role was enabled in this run for the rest, and no artefact exists for them. Whether the slice sits in an "enterprise context" in which every row applies is the owner's ruling; I do not make it, and I do not mark a row "n/a" or "met" where I cannot show why.

| Gate | Owner role | Judgement | Basis |
|---|---|---|---|
| New data classified + retention set | Data Governance | **NOT MET** | Classification is the Compliance Reviewer's assignment in `11b` ("owner to confirm"); retention is UNKNOWN. No Data Governance review exists. |
| Catalog / RoPA updated for new data flows | Data Governance | **NOT MET** | None exists. `11b` condition 5: the owner keeps one or says in one line that none is kept. |
| Schema / data migration plan + rollback | Backend Architect | **n/a** | No schema, no migration, no stored product data. |
| Threat model for new attack surface | Security & Privacy | **MET WITH GAPS** | No `THREAT_MODEL_TEMPLATE` file. `08-security-review.md` is an adversarial review of eight surfaces with probes and eight rated findings, and covers the same ground in substance. It is not in the template's form. I did not compare the two. |
| Controls mapped + evidence; named approver | Compliance Reviewer | **NOT MET** | Mapping exists in `11b` (GDPR Art. 5, 28, 30; SOC 2 CC9.2; ISO 27001; EU AI Act Art. 50 flagged as a legal reading not made). Approver named; approval pending. Every supplier-assurance field is UNKNOWN. |
| New subprocessor risk-assessed + DPA in place | Compliance Reviewer | **NOT MET** | Section 4 above. |
| AI capability risk-tiered; obligations met | AI Governance | **NOT MET: not run** | No `AI_RISK_ASSESSMENT` artefact. The registered bars and the audit are the only eval content. `11b` flags the Art. 50 question for the owner or legal. |
| Eval coverage for AI safety invariants | AI Governance | **MET WITH GAPS** | Two pre-registered bars, both measured once; INV-4/INV-5 pinned by named tests; per-spawn audit with void rules. Gaps: bars are for the eval path only; the operator path is unmeasured; the hook never fired; Bar 2 passes by one question at both stages. |
| Cost-per-action estimated; kill-switch tested | FinOps | **n/a with a reason** | Subscription window, no metered API (and none is to be added). Cost per spawn is in the audit and in monitoring signal 10 (about 7.9k and 8.6k mean peak per spawn). The kill switch is "do not type `/aveto-judge`", or `git rm -r .claude/skills/aveto-judge/`; the second has not been rehearsed. |
| Docs match shipped behaviour; migration notes | Tech Writer | **MET WITH GAPS** | README, `CURRENT_MVP_STATUS.md`, `ARCHITECTURE.md` and ADR 0008 (Proposed) carry the recorded figures. They are **stale on the tier**: README and status say "run at tier 2" and list the tier as an open owner decision, and S6 as undecided. The tier is now 3 (record 9) and S6's rule is gone (T9). Fix after this verdict. |
| SLOs + runbook + tested rollback (production service) | SRE | **MET WITH GAPS** / part n/a | Not a production service: no SLO, said plainly in the plan. Runbook exists in a run record only. Rollback not tested. |
| Change request recorded + approved (CAB) | Release Manager | **NOT MET** (recorded; approval PENDING) | Section 3.5. |

## 6. Tier 2 gates, re-walked (delta from `09-release-checklist.md`)

I did not repeat the tier 2 evidence. Every tier 2 gate status below is the tier 2 walk's, with what has changed since stated. Nothing here was re-run by me.

| Gate | Tier 2 status | Now |
|---|---|---|
| Scope, non-goals, success criteria, adapter boundaries, audit events listed | MET | Unchanged. (Non-goals still sit in the intent, not a spec section.) |
| Typecheck | MET (reported) | Reported only; not re-run by me; no report on `e7c623e`. See section 2. |
| Targeted tests | MET | 207 passed on the judge test files, 2 deselected, in the tier 3 QA run (`12`). |
| Full test suite | MET for the registered regression, with one disclosed model-marked failure | 375 passed, 12 deselected in three reports (Orchestrator at `3e1c939`, support session at `0311370`, QA before D6). **`-m model` is red by one**: `test_sample_derivation_reproducible`, frozen, cause confirmed (the whole-file byte comparison cannot pass once the gate rows were appended to the key). A later slice must change it. |
| Build | n/a | Unchanged. |
| One commit per task | PARTIAL, not walked | Unchanged; I cannot run `git log`. |
| No new lint warnings | MET **by exemption, disclosed** | D6: three Security probe scripts carry `# ruff: noqa` on line 1; `pyproject.toml` untouched. **The owner acknowledged D6 (record 9).** Reply 3 shows ruff passing. The gate passes because three evidence scripts opt out; it does not mean they are clean. |
| UI in preview | n/a | No UI. |
| Local regression | MET (reported) | As above. |
| Safety invariants verified | MET | QA section 4. Unchanged. Not testable: that Claude Code runs the judge's hook (0 tools offered, so it never fired). |
| No secrets / PII in diff; audit events cover state changes; adapter placeholder | MET | Security `08`: 0 blocking. Unchanged. |
| Security findings | 0 blocking; S5, S6 required-fix open; S1 to S4, S7, S8 advisory | See section 7. |
| Rollback plan exists | MET | Exists and the paths exist (tier 2). **Not rehearsed.** At tier 3 that is a blocker under the change request template (T4). |
| Release checklist filled | MET | This file and `09-release-checklist.md`. |
| Freeze held | verified at `69fd907` by QA | Not re-verified by me (no git). The commits since are, by message, docs and run records. |

## 7. Tier 2 conditions: where each stands now

| # | Tier 2 condition | Status now | Basis |
|---|---|---|---|
| C1 | Rule the tier | **RESOLVED: tier 3** | Record 9. The depth of no stage was lowered. |
| C2 | S6: the local permission rule in `.claude/settings.local.json` | **File observed absent; disposition not recorded in the driving session** | My Read: "File does not exist" in this worktree. `SUPPORT_REPLIES.md` Reply 4 (uncommitted, support session, "data only") says the owner said "remove it" on 2026-10-16 and the support session deleted it. Record 9, written the same day in the driving session, still lists "the S6 rule's disposition (still the owner's: delete, narrow or accept)" as not approved and says nothing of a deletion. A message from another session, even one that quotes the owner, is never an approval; here it is not asked to be one (deleting a permission rule tightens the environment and is not a gated action). So: **the risk the finding named appears to be gone in this worktree, and the record of the decision is not in the driving session.** One typed line from the owner closes it (T9). I checked this worktree only. |
| C3 | S5: `/aveto-judge-seen` quote breakout | **HELD, not fixed** | Record 9: not used again until S5 is fixed. The skill file is unchanged, still model-invocable by design (F12), and nothing technical stops an invocation. **It would land on `main` with a merge** (T8). Stage 7 results are unaffected (every transcript matched a key payload by hash). |
| C4a | Final-tree ruff, mypy, pytest by a session with a shell | **PARTLY MET, not on the final commit** | Reply 3 at `0311370`; the Orchestrator at `3e1c939` and again at close-out. Nothing on the merge candidate yet (T6). |
| C4b | D6 | **RESOLVED** | Record 9: acknowledged. |
| C5a | Approver identity | **PARTLY RESOLVED** | Record 9 names Gopal Patwa. Records 1 to 8 say "owner". No `trace.json` for this slice. No time of day anywhere (T11). |
| C5b | STATE corrections | **PARTLY DONE** | The rule 4 stage row now cites records 5, 6, 8. **The Approvals table lists record 7 twice** (the D1 row appears at the table's start and again at its end, after the record 9 row). `Updated:` still reads 2026-10-12, and the "Next action" paragraph still says the Release Gate at tier 2 is next. These are the Orchestrator's to fix; I did not edit STATE. |
| C5c | DPA line | **OPEN: recorded as UNKNOWN** | `11b`; section 4. |
| C6 | Docs carry the full set of figures | **MET on the figures; STALE on the tier and S6** | I compared the README judge-step table and the status page to `05-seen-check.md` and `07-gate-scoring.md`: Bar 1 20/20 and 24/24; Bar 2 24/28 and 16/19 = 84.2%; judge errors 0; never-abstain 0/24 and 19/19; best-score rule 13/20, 17/28, 10/24, 13/19 NOT MET; over-abstention 4/28 and 3/19; end to end 16/24; retrieval gate 79.2% not a registered bar; one-question margin; D4 overlap; tool-use audit clean. All match. They make no capability claim and no pass claim on the retrieval gate. **Stale:** both files say the tier is an open owner decision and "run at tier 2"; both list S6 as an undecided too-wide rule. `ARCHITECTURE.md` says the verdict "is being re-run for tier 3", which is accurate until this file lands. |
| R-A | Retrieval gate exit 1 accepted or declared relevant | **NOT ACCEPTED** | Record 9. Carried. |
| R-B to R-F | Bar 2 margins; advisories; model-marked test; harness behaviour no test shows; self-reported telemetry | **Stated, not accepted** | Record 9 accepts none of them. `11c`: "They are not accepted by this request." |

## 8. Conditions before the slice may land

Each must be resolved, in the owner's own words where it is the owner's, **before any push or merge**. I can resolve none. "Whose" is the owner or role that can. A condition is closed only by an artefact, not by this file saying so.

| # | Condition | Whose | Closes when |
|---|---|---|---|
| **T1** | **Ask and obtain the owner's approval of the release action.** Today it is not requested. The ask must be the specific one in `HUMAN_APPROVAL_RULES.md` "How to ask for approval": what (for example "merge `claude/docs-answerability-2` into `main`, by merge commit, squash or fast-forward" and, separately, "push the branch"), why and which rule (rule 3, tier 3), what is reversed if denied, the smallest request. Merge and push are two actions with two yeses. The merge method must be named because the full-revert command assumes a merge commit. | Orchestrator raises it; owner decides in the driving session | An `APPROVAL_RECORD-N` quotes the owner's typed words, names the action, carries Gopal Patwa's name and a time of day. Not before the other conditions are resolved or waived. |
| **T2** | **Record the change request decision.** `11c` is "submitted — approval PENDING". | Owner (human owner row); Release Manager row after a landing sign-off | The approvals table in `11c` holds a decision and a time for the human owner. |
| **T3** | **State the vendor-risk position, or waive it in the owner's words.** The DPA, plan and account type, retention, training use, terms, subprocessors, certifications, residency (section 4). Adopt or decline the operating rule "public-docs questions only until stated". Say whether a RoPA or processor-inventory entry is kept. Accept or reject the risk rating. | Owner (a contract reading is the owner's or legal's) | `11b` is updated by a later session from the owner's own statement, or an `APPROVAL_RECORD` quotes the owner proceeding with the fields UNKNOWN. In the second case the gate is recorded as *waived*, not *met*. |
| **T4** | **Rehearse the rollback, or record acceptance of the plan as written.** A throwaway branch: `git revert` of the slice commits (or the step 3 full revert) plus the regression; nothing merged; the INV text revert not committed to the real branch. The change request template makes "not tested" a tier 3 blocker. | A session with a shell (Engineer or QA), no approval needed for a scratch branch; or the owner in words | The rehearsal's commands and output are in a run artefact, or an owner record accepts the untested plan. |
| **T5** | **Set the monitoring thresholds, cadence and stop rules** (the SRE's are proposals) and say who is the operator. Adopt "stop typing `/aveto-judge`, use `retrieve` alone" as the standing mitigation. Copy plan sections 2 and 5 into `docs/runbooks/` (Tech Writer; not done). | Owner; Tech Writer | The owner confirms or changes the thresholds in their own words; the runbook copy exists in the repo. |
| **T6** | **Final-tree regression on the exact commit to be merged**, by a session with a shell: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, output recorded. I could not; the Orchestrator re-runs at close-out. | Orchestrator | Output on the merge candidate is in `STATE.md` or a run artefact: ruff all checks passed, mypy clean, 375 passed, 12 deselected (any other count is a finding). The pre-merge commit also confirms an empty diff of every method file against `bca0e40`. |
| **T7** | **R-A: the retrieval gate exit 1 on the fifth set.** Accept in the owner's words, or declare it relevant to the release. It does not stop an internal release; it bounds what any document may claim. | Owner | A record in the owner's words. |
| **T8** | **S5, before the skill reaches `main`.** `/aveto-judge-seen` has a quote breakout in its `!` shell line, is eval-only and model-invocable by design, and would land on `main` with the merge. The hold in record 9 is a rule the owner follows, not a technical stop. Decide: fix (voids the freeze for any further eval use), disable or retire (`git rm -r` of the skill, same kind of change as rollback step 2), or accept in words. | Owner | A record in the owner's words. |
| **T9** | **S6 and the stale text.** (a) The owner states in the driving session that the S6 rule is deleted (the file is absent, the decision is recorded only by the support session). (b) README, `CURRENT_MVP_STATUS.md` and `ARCHITECTURE.md` stop saying the tier is open and "run at tier 2", stop listing S6 as an undecided rule, and carry this verdict; ADR 0008 stays Proposed. (c) `STATE.md`: remove the duplicate record 7 row, update `Updated:` and the "Next action" paragraph. | (a) Owner; (b), (c) Orchestrator | Files read correctly by the next Release Manager. |
| **T10** | **Rule which governance gates in section 5 apply**, and for each NOT MET row that applies, either the role's artefact or the owner's recorded waiver (Data Governance, AI Governance, a threat model in the template's form). I did not enable any role. | Owner rules; named roles if enabled | A line from the owner saying which apply. |
| **T11** | **Record hygiene for the approval trail.** A `trace.json` for this slice with the `operator` handle (rule 3 asks for the same handle), and a time of day on the release approval. Records 1 to 9 stand as they are. | Orchestrator; owner for the time | `runs/docs-answerability-2/trace.json` exists and names the operator. |

**Stated, not accepted, and they carry forward:** R-B (Bar 2 by one question at both stages), R-C (advisories S1 to S4, S7, S8), R-D (the failing `-m model` test), R-E (the hook never fired; the session-context list is not complete), R-F (telemetry is self-reported; several stages overran: Scope +78%, Architecture pass 2 +83%, Label review +105%). Spent 2469k of the 2600k plan (95%) and 73% of the 3400k ceiling at the start of this stage; the next planned stages fit under the ceiling per `STATE.md`. No spend above the ceiling.

## 9. Evidence figures to carry (verbatim from the scorers; not rounded up)

| Measure | Stage 5 (seen-set sample, `05-seen-check.md`) | Stage 7 (fifth set, scored once, `07-gate-scoring.md`) |
|---|---|---|
| Record valid | yes: 48 spawns, offered tools 0, `tool_use` 0, model `claude-sonnet-5-5` | yes: 48 spawns, offered tools 0, `tool_use` 0, model `claude-sonnet-5-5`, no anomaly |
| **Bar 1** (abstain on unanswerable) | **20/20**, registered at least 16: MET | **24/24** (100.0%), registered at least 20: MET |
| **Bar 2** (answerable with right file in top 5, not abstained) | **24/28** (85.7%), registered at least 23: MET, **one question of margin** | **16/19 = 84.2%**, registered 80%: MET, **one question of margin** (15 would have failed) |
| Judge errors (counted as failures on both bars) | **0** | **0** |
| Never abstain | not printed | Bar 1 **0/24**, Bar 2 19/19 |
| **Best-score rule** (`top1 < 0.67`) | Bar 1 13/20, Bar 2 17/28: **NOT MET** both | Bar 1 10/24, Bar 2 13/19: **NOT MET** both |
| Over-abstention | 4/28 | 3/19 (g09, g10, g24) |
| ANSWERABLE when the right file was not in the top 5 | 0/0 | 1/5 (g19) |
| Hard negatives abstained (diagnostic) | n/a | 18/18 |
| **End to end** (right file shown after judging, diagnostic) | n/a | **16/24** |
| Retrieval gate on the fifth set | n/a | **exit 1: 19/24 = 79.2%, required 80%** (misses g05, g06, g18, g19, g22); not a registered bar; R-A not accepted |

How to read it, without softening:
- The judge did what it was built to do on refusals: 24 of 24 unanswerable questions abstained, including all 18 hard negatives, with no judge error in 96 spawns.
- Bar 2 is met by exactly one question at both stages, on a denominator of 19 at stage 7. It is one scoring of one set, held out by rule and not repeatable. The fifth set's source files overlap earlier sets' (21 of 24 answerable questions), which may flatter Bar 2 (D4).
- After judging, 16 of 24 answerable questions end with the right file shown. Five are lost before the judge sees them, three more to over-abstention. By the intent's own standard, abstaining is "never worse than showing a wrong file", so this is lost coverage, not a wrong claim. The judge cannot repair a retrieval miss.
- The bars describe the eval path. The operator path (`/aveto-judge`) has never been measured.
- Stage 7 driver session began in the main checkout and was moved to the worktree by the owner before any spawn; the audit proves observed behaviour, not the load path.

## 10. Rollback plan

Source: `02-tech-spec.md` section 13, `09-release-checklist.md` and `11c`, checked against what exists. I could not run any of it.

1. **Before any merge: do not merge**, or `git revert` the slice commits on the branch in reverse order. Nothing has reached `main`; no agent pushed or merged anything in this run, and `11c` and record 9 agree.
2. **After a merge, disable the operator path only:** `git rm -r .claude/skills/aveto-judge/` and commit. `retrieve` is not in the diff against `main`. Consider the same for `.claude/skills/aveto-judge-seen/` if S5 is not fixed (T8).
3. **Full revert:** `git revert -m 1 <merge-commit>` and the regression. Assumes a merge commit; with a squash or fast-forward the target differs and must be named when the owner approves the merge. **INV-4 and INV-5 return to their pre-slice text, a safety-control change (rule 4): the owner's own words first.** README and `CURRENT_MVP_STATUS.md` revert with it.
4. **D1 only (the seven harness tools):** `git apply -R` of the fenced diff in `03a-d1-proposed-diff.md` (the spec's `D1-diff.md` name is wrong), with the owner's approval; `uv run pytest tests/test_judge_artefacts.py`; fresh-load session. The SRE advises stopping rather than reversing D1 alone.
5. **Eval data only:** `git rm -r runs/docs-answerability-2/judge-check/`.
6. **Outside git:** Claude Code transcripts in `~/.claude/projects/` hold full payloads and replies; no rollback touches them. **No repo rollback recalls data already sent to Anthropic**; its retention is UNKNOWN (section 4). The S6 rule, if it were ever re-created, is outside git.
7. The program writes nothing persistent except the gitignored `.aveto-judge/` (deleted on every `judge-apply`; a symlink survives, S2).

**Rollback gate: plan EXISTS and the named paths exist (tier 2: MET); NOT TESTED (tier 3: NOT MET, T4).** No revert has been executed or rehearsed by any agent. The INV revert is correctly marked as needing the owner's words.

## 11. What this verdict allows, and what it does not

**Allows:**
- Keeping `claude/docs-answerability-2` as an internal candidate branch, unmerged and unpushed.
- The Orchestrator's close-out: the docs corrections (T9), the final-tree regression (T6), and STATE.
- Writing the owner-facing ask for the release action (T1), once the owner wants it. Writing it is not asking it, and asking is not approval.
- The owner's attended use of the judge step in their own session as already approved by records 2, 3 and 6. This verdict neither grants nor withdraws those. It does **not** treat open-ended use on non-public text as released (section 4).

**Does not allow, and I have not done or approved:**
- **No push, merge, deploy, PR, tag or announcement.** Each needs the owner's own typed yes in the driving session, separately. The change request approval is PENDING. Record 9 says: "Do not merge or push."
- No external description of the result as a product capability. No claim that the product "answers questions". No claim of a pass on the retrieval gate. Nothing posted anywhere (INV-1).
- **No unattended, scheduled, API or `claude -p` use** of the judge; no metered API; no API key.
- **No invocation of `/aveto-judge-seen`** (record 9; S5 is open).
- No move of a bar, no rescore, no use of the reserve questions, no edit to any frozen method file. Any change to a method file voids the freeze.
- No reading of the Compliance Reviewer's "recommended disposition" or the SRE's thresholds as the owner's decisions. No approval is inferred from silence, from an agent's message, or from a message from the support session.
- No treatment of any UNKNOWN in `11b` as met.
- No revert of INV-4/INV-5 without the owner's words (rule 4).

## 12. Decision

- [ ] **Go: the slice lands now.** Not ticked. Nothing lands. Landing is the owner's, with its own approval, after T1 to T11.
- [x] **GO WITH CONDITIONS: internally releasable as a branch candidate, not announced, not cleared to land**, under T1 to T11 and the carried risks R-A to R-F. The conditions are not satisfied by this verdict.
- [ ] **No-go.** Not issued. It becomes the verdict on the triggers in section 1 ("What would turn this into NO-GO outright").

Sign-off rows in `11c`: Release Manager **not signed** (no landing is signed off); Compliance approver **PENDING**; human owner **PENDING**.

## 13. Hand off

- **To the Orchestrator:** the close-out (T6, T9b, T9c, T11); record this stage's spend (I record none); do not push, merge or open a PR. Raise T1 only when the owner asks for it, in the one-message form. Do not edit permission settings.
- **To the owner:** T1 to T3 and T7, T8, T9a, T10, plus whether T4 is required or accepted; T5 thresholds. Each is yours; none is satisfied by anything in this file.
- **To the Tech Writer:** the runbook copy (T5) and the stale tier and S6 lines (T9b).
- **To the SRE:** keep the plan consistent with whatever thresholds the owner sets.
- **To the Post-Launch Learning Agent:** not yet. After the owner lands the slice and shares a period note. Carry-forward list: R-C advisories, R-D test fix, G5 guard (a `record` valid-then-void test), QA's proposal that a later slice either gate `ruff` over `runs/` or keep probe scripts untracked, the unmeasured operator path.

