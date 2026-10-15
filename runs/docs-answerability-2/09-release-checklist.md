# Release Checklist — docs-answerability-2 (stage 9, spawn 2 of 2: Release Manager verdict)

> Owner: Release Manager Agent (fresh spawn; did not build, review or score this slice)
> Tier: **2** as the intent names it (not changed here; see "Tier" for a finding the owner must rule on)
> Depth: standard. Worktree `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-answerability-2`, branch `claude/docs-answerability-2`, HEAD at the start of this stage `3e1c939` (the commit that applied D6). Freeze `bca0e403a69a5cda7826ea36897734bc63dc7b87`.
> Source artefacts: `intent.md`, `STATE.md`, `STANDING_INSTRUCTIONS.md`, `APPROVAL_RECORD-1` to `-8`, `02-tech-spec.md` (section 13 only), `02c-rule6-question.md`, `05-seen-check.md`, `07-gate-scoring.md`, `08-security-review.md`, `09-release-qa.md`; playbook `docs/RELEASE_GATES.md`, `docs/HUMAN_APPROVAL_RULES.md`.
> Not opened, by the brief: `evals/retrieval-heldout-5*.toml`, `batch-2.txt`, `judge-check/q/`, `06-label-review.md`, any `diffs.md`. `RELEASE_APPROVAL_PACKET.md` (untracked, a support-session draft) was ignored and is not an approval of anything.

## Verdict: GO WITH CONDITIONS (internally releasable, not announced)

Read this first.

- **What I am saying go to:** the branch is an internally releasable candidate for tier 2. Both registered judge bars were met once on the held-out set, nothing was voided, Security found 0 blocking issues, the freeze held, and every rule 4, 5 and 6 action the slice needed has a typed owner record.
- **What I am not saying:** nothing here is an approval and nothing here authorises a push, a merge, a deploy or an announcement. Those are the owner's and none has been requested or recorded (see "What 'internally releasable' allows").
- **Conditions are the owner's to resolve, not mine.** Section "Conditions and accepted risks" lists them. The three that matter most:
  1. **Tier.** I think tier 3 plausibly applies (the slice rewrites safety-control text INV-4/INV-5 and adds a third-party data flow). The tier is the owner's. This verdict is **conditional on the owner ruling tier 2**. If the owner rules tier 3, the verdict reverts to no-go on one missing item (a post-launch monitoring plan) until one exists.
  2. **Open Security findings S5 and S6**, both rated required-fix, both the owner's decision, neither actioned. They are open risks in the operator environment and an eval-only skill, not in the product. Stated plainly in the conditions.
  3. **Retrieval gate exit 1 on the fifth set (19/24 answerable questions with the right file in the top 5 = 79.2%)**. It is not a registered bar and I do not treat it as one, but it is a real product fact: after judging, only 16 of 24 answerable questions end with the right file shown.
- **Not softened:** the judge's bars are met by one question of margin on bar 2 at both stages, the best-score rule is NOT MET on both stages, and the end-to-end diagnostic is 16/24. Full figures are in "Evidence figures to carry".
- **What I could not do:** I have no shell. I did **not** re-run `uv run ruff check`, `uv run mypy` or `uv run pytest`. I rely on the Orchestrator's reported output (ruff all checks passed, mypy clean, 375 passed, 12 deselected) and on the QA spawn's earlier run. See "What I ran".

## What I ran (and did not)

| Item | Result |
|---|---|
| `uv run ruff check`, `uv run mypy`, `uv run pytest` | **Not run by me: this role has Read, Write, Edit, Grep, Glob only, no shell.** Reported by the Orchestrator after D6: ruff "All checks passed", mypy clean, 375 passed, 12 deselected. The QA spawn's own run (HEAD `69fd907`, before D6): mypy clean, 375 passed, 12 deselected, ruff exit 1 with 23 errors, all under `runs/docs-answerability-2/security-probes/`; with that directory excluded ruff passed. The only change since is D6, so the two reports are consistent. |
| D6 present on disk (Grep) | `# ruff: noqa  (Security Review evidence script; lint-exempt by design, kept as written)` is line 1 of all three files: `probe_skill_quoting.py`, `test_probe_judge.py`, `test_probe_retrieve_echo.py`. |
| `pyproject.toml` | Grep finds `[tool.ruff]` at line 32 and no `exclude` or `per-file-ignores`. Consistent with "no pyproject change" (I cannot diff it against the prior commit without git). |
| `git diff` / `git log` | Not available to me. The start-of-session status shows only `SUPPORT_REPLIES.md` modified and `RELEASE_APPROVAL_PACKET.md` untracked, so no method file has an uncommitted change. I did not verify what files `3e1c939` touched beyond its commit message and the Orchestrator's statement (three probe scripts plus records). The QA spawn's freeze diff (empty for every method file) was taken at `69fd907`. |
| Read, not re-derived | All bar figures below are copied from `05-seen-check.md` and `07-gate-scoring.md`. I did not open the set, the key, the questions or any reply. |

**Residual doubt I cannot close:** the D6 directive carries trailing prose after `# ruff: noqa`. The Orchestrator reports it works (a directive ruff failed to parse would leave the 23 errors in place), so I accept the report, but condition C4 asks for one run by a session with a shell on the final tree.

## Tier

**Classification used: tier 2**, because the intent names it and the brief binds it ("Behavioural change with no external effect": the program is offline, makes no network call and calls no model; the judge step is run by the operator, attended, in their own Claude Code session).

**Finding for the owner (not a reclassification):** the playbook's tier 3 reads "change to anything that sends, submits, posts, publishes, pushes, deploys, or destroys; change that touches an integration with a third party; change that alters auth/permissions". This slice (a) rewrites two safety-control texts (INV-4, INV-5), (b) adds a data flow, the question, the shown passages and the session context, to Anthropic via the operator's own session (rules 5 and 6), and (c) edits the judge agent's deny list. One can fairly read that as tier 3. The counter-reading, which the intent takes: the product itself sends nothing, every send is a deliberate operator act in a session that was already sending to the same provider, and nothing is posted (INV-1 holds).

**What tier 3 would add, and where each stands:**

| Tier 3 requirement | State |
|---|---|
| Explicit human approval per the rules | Present for every gated action the slice took (records 2 to 8, below). Not yet requested for the release action itself (merge or push). |
| Dry-run on a fixture before live | Effectively present: two public eval-set questions before the INV words (record 4, `01-measurement.md`), then the smoke r049 before the batch (`05a-smoke.md`), then 48 seen-set spawns before the gate set. |
| Audit event coverage manually verified | Present: Security `08` section 8 cross-checked the spec's audit events against the code. |
| **Post-launch monitoring plan** | **Absent.** Nothing in the slice defines a signal, threshold or owner for after release. |
| Enterprise overlay gates (change request, vendor risk, data governance, DPA) | Not run; no overlay role was enabled in this run. See "Enterprise and governance gates". |

**Consequence:** the verdict is conditional on the owner ruling tier 2 (condition C1). A tier 3 ruling means: monitoring plan written, a named approver recorded for the release action, and the vendor-risk and DPA-status gap closed. I do not write those here.

## Gates, tier 2 (walked top to bottom; evidence named)

"Taken from" means I read the artefact that records the result and did not re-run it.

### Earlier-stage gates (from the gate map; owners are other roles)

| Gate | Status | Evidence |
|---|---|---|
| Slice fits one pass | MET | STATE: Scope row "one slice, no split". |
| Non-goals explicit | MET | Intent "Out of scope" and "What this deliberately is not"; `01-scope.md` line 79 quotes the out-of-scope line and flags the judge as needing a precise statement at stage 10. The tech spec has no section headed non-goals (grep found none); the intent carries them. Not a blocker. |
| Success criteria observable | MET | Two numeric bars fixed before any run (R3, `02-tech-spec.md`), unchanged since the freeze. |
| Adapter boundaries identified | MET | Tech spec; the judge is outside the program (ADR 0008, Security `08` section 8). |
| Audit, feedback, usage events listed | MET | Tech spec section 7; Security cross-checked against the code. |

### Implementation

| Gate | Status | Evidence |
|---|---|---|
| Typecheck | MET (reported, not re-run by me) | mypy "no issues found in 24 source files" (QA, `09-release-qa.md` row 2); Orchestrator reports clean after D6. |
| Targeted tests | MET | QA row 6: 11 named tests passed (agent pin, deny hook, offline test, network block). Security: 207 passed on the judge test files, 2 deselected. |
| Full test suite | MET for the registered regression; **one model-marked failure disclosed** | `uv run pytest`: 375 passed, 12 deselected (QA, and Orchestrator after D6). `LOCAL_COMMANDS.md` defines the full regression as `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`; `-m model` is not in it. `uv run pytest -m model` gives 8 passed, 1 failed: `test_sample_derivation_reproducible`, cause confirmed by QA (the whole-file byte comparison cannot pass once the 48 gate rows were appended to the key, as R8 allows; the frozen key is a byte-identical prefix, same sha256 `33109e85...ca5c38`). The test is frozen and was not edited. It no longer proves sample reproducibility in the committed tree; QA verified that property by the prefix match instead. A later slice must change it. |
| Build | n/a | Python package, no build step in `LOCAL_COMMANDS.md`; `uv sync --locked` passes (QA row 1). |
| One commit per task | PARTIAL, not walked per task | The commit history is per stage (freeze `bca0e40`, record `c4a8e90`, set `b692ffc`, label review `c0da63e`, gu09 `9b28c08`, key rows `032cadc`, scoring `f60c1dd`, Security `69fd907`, D6 `3e1c939`; first code commit `5eb2a8a`). I cannot run `git log`, so I did not check task granularity inside implementation. Not a safety matter. |
| No new lint warnings | MET **by exemption, disclosed** | `uv run ruff check` was red at `69fd907` (23 errors in the committed probe scripts, not in product, tests or tools). D6 added a first-line `# ruff: noqa` to each of the three scripts. The product, tests and tools are linted as before. The gate passes because three Security evidence scripts opt out of it, not because they are clean. See condition C4 and the "Not approvals" list in the approvals walk. |

### QA

| Gate | Status | Evidence |
|---|---|---|
| UI verified in preview | n/a | No UI (intent Stakes: "Adds a screen or UI" unchecked). |
| Local regression command | MET (reported, not re-run by me) | As above. |
| Safety invariants verified | MET | QA section 4: INV-4 and INV-5 text equals the approved blocks plus the record-8 edit; INV-1 to INV-3 untouched; offline test passes. Not testable: that Claude Code runs the judge's hook (0 tools were ever offered, so it never fired); disclosed in INV-4, INV-5 and Security section 9. |

### Security (adversarial depth, bound by the intent, never lowered)

| Gate | Status | Evidence |
|---|---|---|
| No secrets or credentials in diff | MET | Security section 6: pattern scan, one hit, a test sentinel `secretsentinel`; no `.env`, key or `settings.local.json` committed; `.gitignore` covers them. The set files, `batch-2.txt` and `q/` were excluded from that scan and `diffs.md` was scanned by pattern only. |
| No PII or sensitive data logged | MET, with a disclosure | Security section 5: audit and verdict files hold tokens, hashes and sha16 of replies, no reply text; `diffs.md` holds reply text for differing rows only (disclosed; scanned for secrets and emails, none). Records name the session-context items without their values, except the OS version string `Darwin 25.3.0`. |
| Audit events cover state changes | MET | Security section 8: deciding signal, judge error with fixed category, payload hash on stderr, transport cleanup, eval audit files; none removed or weakened since the freeze. |
| Adapter boundary placeholder still throws | MET, with a note | Security section 8: no placeholder adapter became a real client; the product still has no model client; the judge is a Claude Code subagent outside the program (rule 5, record 2). `test_program_offline_no_model` and `test_default_network_is_blocked` pass (QA row 6). |
| Findings | 0 blocking; **S5 and S6 required-fix open**; S1 to S4, S7, S8 advisory | See conditions C2 and C3. |

### Release

| Gate | Status | Evidence |
|---|---|---|
| Human approval points satisfied | MET for everything the slice has done; **the release action itself is not requested** | See "Approvals walk". |
| Rollback plan exists | MET | `02-tech-spec.md` section 13; confirmed below. |
| Release checklist filled | MET | This file. |

### Enterprise and governance gates (overlay roles)

n/a: the run enabled no Data Governance, Compliance, AI Governance, FinOps, SRE or change-request role, and STATE has no spawn for any of them. Two notes, because they bear on tier 3:
- **Vendor risk and DPA status (rule 6 asks for it):** rule 6 says the agent surfaces the processor, the data with its classification and the DPA status before the human approves, and that a new subprocessor is risk-assessed with `VENDOR_RISK_TEMPLATE.md` first. `02c-rule6-question.md` names the processor and the data; it does not mention classification, DPA or vendor risk (grep: no match). Record 3 and 6 approve Anthropic through the operator's own session, attended only. The owner approved with that information; the gap is that "DPA status" was never stated in any artefact. Condition C5 asks for one owner line.
- **AI capability risk-tiering and eval coverage:** the registered bars and the audit are the eval; no separate AI Governance artefact exists.

## Approvals walk (rules 1 to 6)

Each record is a file the Orchestrator wrote quoting the owner's typed words in the driving session. I can read the records; I cannot see the conversation they came from. I treated a record as an approval only if it quotes the owner's own words, names the specific action, and does not claim more than that action.

| Rule | Fired in this slice? | Action | Typed owner record | Words (short) | Date | Approver as recorded |
|---|---|---|---|---|---|---|
| 1 Send or submit for a user | **No.** The program has no send path; nothing posts (INV-1; Security section 8). The judge step's send to the model provider is covered under rules 5 and 6, and no metered API is used. | n/a | n/a | n/a | n/a | n/a |
| 2 Destructive on shared state | **No.** The program deletes only its own gitignored `.aveto-judge/` files. The rollback plan's `git rm` and `git revert` are plans, not actions taken. | n/a | n/a | n/a | n/a | n/a |
| 3 Deploy, release, external effect | **Not yet.** Push, merge and deploy have not been requested or taken. This rule fires at the owner's merge or push. | n/a | **none, correctly** | n/a | n/a | n/a |
| 4 Safety control | **Yes**, four times | (a) sequencing: two public questions before the INV words; (b) INV-4/INV-5 exact words plus the two-line `NOT_ANSWERABLE` output (F10); (c) D1, seven harness tools added to `disallowedTools` and the same in `DENY_LIST`; (d) one INV-5 edit, environment list gains OS version and worktree flag | records 4, 5, 7, 8 | "Stage 1 may send exactly two public eval-set questions..."; "I approve the INV-4 block ... and the INV-5 block ... exactly as written"; "Approved: apply the D1 diff ... exactly as written"; "I approve exactly one edit to INV-5 ..." | 2026-10-12 (records 4, 5, 7); 2026-10-13 (record 8) | "owner" |
| 5 LLM into a deterministic path | **Yes** | judge agent model `claude-sonnet-5-5`, prompt unchanged, tools omitted, `mcp__*` deny list and match-all hook unchanged | record 2 (and 7 for D1) | "Rule 5: change the judge agent to claude-sonnet-5-5 (full ID) ..." | 2026-10-12 | "owner" |
| 6 New data processor or commitment | **Yes** | Anthropic as data processor through the owner's own session, attended only; then extended to name the session context exactly as listed in INV-5 | records 3, 6 | "Rule 6: Anthropic as data processor through my own session, attended only."; "record 3 is reaffirmed and extended to name the session context exactly as listed in the INV-5 block ..." | 2026-10-12 | "owner" |
| Budget (not rules 1 to 6) | yes | Plan 2.6M, ceiling 3.4M, stop and ask above it, no hard cap | record 1 | "Approved: (1) the intent and the plan; plan 2.6M, ceiling 3.4M ..." | 2026-10-12 | "owner" |

**Sequencing check (rule 4: approval before implementation):** record 4 allowed exactly r001 and r002 before the words; records 5 and 8 precede r001 of the batch (`ef9ad1e` before r001, per the freeze record); record 7 precedes the smoke; no commit touches `.agentic/SAFETY_INVARIANTS.md` after `ef9ad1e` (QA section 2). I find no data-sending spawn that ran ahead of its approval.

**Not approvals, listed so nobody reads them as such:**
- **SI-1 defaults** (A1 to A13, D1 first-commit method, D2, D2', D3, D3', D4' ... D6, D4 source reuse, D5 source additions). The standing instruction lets the Orchestrator proceed on a recommended default for a design question outside rules 1 to 6; the owner vetoes by exception. None is a rule 1 to 6 approval and I do not count any as one.
- **SI-2** (adopting Support Reply defaults) and **SI-3** (continue between stages without waiting). SI-3 is the owner's standing instruction about run flow. It is **not** a safety-control approval and it does not authorise push, merge or deploy; its own text lists those as stops.
- **D5b** (replace gu09 with reserve gr02) is the owner's typed decision (`STANDING_INSTRUCTIONS.md`), recorded there and not as an `APPROVAL_RECORD` file. It is an eval-data change by the owner, taken after the label review and before scoring. Not a rule 1 to 6 item.
- The intent's own opening says its confirmation "is not an approval of anything"; record 1 is where the owner approved the plan.

**Gaps in the approval record (none invalidates a rule 4, 5 or 6 approval; all are condition C5):**
1. **Approver identity.** Every record says "owner", a role, not a person. `HUMAN_APPROVAL_RULES.md` rule 3 requires an identity, the same handle as the run's `operator` in `trace.json`. There is no `trace.json` in `runs/docs-answerability-2/` (Glob finds no JSON there), so no operator handle is recorded. The session context shows a git user ("Gopal Patwa"), but nothing in the records says the typist is that person, and I will not infer it. The owner should state the handle once.
2. **Time of day.** Records carry dates only. Fine for audit by date; thin for "approved at".
3. **STATE.md is behind the records.** Its Approvals table stops at record 7 (record 8 is missing), and its stage row "Rule 4 approval (INV-4/INV-5) ... pending" is stale (record 5 approved it). The Orchestrator should correct both; I may edit only my own stage row and the Next stage line.
4. **DPA status** was never stated (see enterprise note above).

## Evidence figures to carry (verbatim from the scorers; do not round up)

| Measure | Stage 5 (seen-set sample, `05-seen-check.md`) | Stage 7 (fifth gate set, scored once, `07-gate-scoring.md`) |
|---|---|---|
| Record valid | yes: 48 spawns, offered tools 0, `tool_use` 0, model `claude-sonnet-5-5` | yes: 48 spawns, offered tools 0, `tool_use` 0, model `claude-sonnet-5-5`, no anomaly |
| **Bar 1** (abstain on unanswerable) | **20/20**, registered at least 16: MET | **24/24** (100.0%), registered at least 20: MET |
| **Bar 2** (answerable with right file in top 5, not abstained) | **24/28** (85.7%), registered at least 23: MET, **one question of margin** (22 would fail) | **16/19** (84.2%), registered 80%: MET, **one question of margin** (15 would fail) |
| Judge errors (own number, counted as failures on both bars) | **0** | **0** |
| Never abstain (today) | not printed in the stage 5 record | bar 1 0/24, bar 2 19/19 |
| **Best score rule** (`top1 < 0.67`), same set | bar 1 13/20 and bar 2 17/28: **NOT MET** on both | bar 1 10/24 and bar 2 13/19: **NOT MET** on both |
| Over-abstention (answerable with a hit called NOT_ANSWERABLE) | 4/28 | 3/19 (g09, g10, g24) |
| ANSWERABLE when the right file was not in the top 5 | 0/0 | 1/5 (g19) |
| Hard negatives abstained (diagnostic) | n/a | 18/18 |
| **End to end** (answerable questions whose right file is shown after judging, diagnostic) | n/a | **16/24** |
| Usage (peak sum from transcripts) | 378,696 (in-equivalent 439,564); smoke r049 adds 7,784 | 410,748 (in-equivalent 479,870) |

**Retrieval gate on the fifth set: `answerable: 19/24 (79.2%) required >= 80% FAIL`, `eval` exit 1.** Misses (right file not in the top 5): g05, g06, g18, g19, g22. One more hit would have been 20/24 = 83.3%. This is not a registered bar (R3's bars are the two judge bars) and I did not make it one. The dev set also scores 19/24 = 79.2% on this ranking and exits 1 by design (`LOCAL_COMMANDS.md`), so retrieval is unchanged in kind from `main`.

**How to read the figures, without softening them:**
- The judge does what it was built to do on refusals: it abstained on all 24 unanswerable questions, including all 18 hard negatives, with no judge error in 96 spawns.
- The **second bar is met narrowly, at both stages, by exactly one question**, on a denominator of 19 (stage 7). It is one run, scored once, by design. A single different verdict would have failed it. This is the number that determines how far "internally releasable" can be pushed.
- Bar 2's denominator excludes the 5 questions where retrieval already missed. The user-facing consequence is the end-to-end diagnostic: **16 of 24 answerable questions (66.7%)** end with the right file shown after judging. 5 are lost to retrieval, 3 more to over-abstention. Abstaining is by the intent "never worse than showing a wrong file", so this is a coverage loss, not a safety loss.
- The best-score rule, the cheap alternative the judge had to beat, fails both bars at both stages. The judge beats it on both. That supports using the judge; it does not make the judge's bar 2 margin larger.
- **Possible optimism on bar 2 (D4):** the fifth set's answerable questions reuse source files that earlier sets cite (21 of 24 answerable questions cite at least one file an earlier set cites), disclosed in the set's header. No question or topic repeats. The support session judged that no-reuse could not hold.
- **Process points that bear on how much to trust the numbers:** the fifth set was committed unopened after the freeze; its labels were reviewed by a fresh QA spawn before scoring; 10 answerable questions received source additions (D5, additions only, nothing dropped) and gu09 was replaced by a reserve on the owner's typed word (D5b); both happened before scoring. Scored once, no rerun, no void. The scorer of stage 5 read the first three differing replies by an unrequested `head` on `diffs.md` (flagged in `05-seen-check.md`; no number depends on it).
- **Session-load deviation (stage 7 driver):** the driver session began in the main checkout and was moved to the worktree by the owner before any spawn; the agent and skill files became available only after the move. The audit's model, offered-tool count, `tool_use`, base-dir line length (137) and payload attribution match stage 5 on all 48 rows, but no audited field records the load path. It proves observed behaviour, not how the files loaded.

## Conditions and accepted risks

Conditions are things that must be resolved, in the owner's words or by the named role, **before the owner pushes or merges anything**. I can resolve none of them. "Accepted risk" means the risk exists today, is stated, and goes forward only if the owner accepts it in their own words.

| # | Condition | Whose | Why it is a condition |
|---|---|---|---|
| **C1** | **Rule on the tier.** I read tier 3 as plausible (INV-4/INV-5 text changed, third-party data flow added, deny list edited). The intent names tier 2 and this verdict is written for tier 2. If the owner rules tier 3, the verdict is **NO-GO until a post-launch monitoring plan exists** and the release action has a named approver. | Owner | The tier is the owner's, not mine and not the Orchestrator's. |
| **C2** | **S6: the local permission rule.** `.claude/settings.local.json` (gitignored, 87 bytes, owner-specified, written by the stage 5 session) holds `Bash(uv run -q --project * python * seen_payload.py *)`. Read by Claude Code's documented `*` semantics it allows without a prompt arbitrary `python <anything> seen_payload.py <anything>`, which is arbitrary local code, in any session opened in this worktree. INV-5's operator-session exception says the session "acts under its own permission prompts"; this rule removes the prompt for that class. Security rates it required-fix and recommends deleting it now that the stage 7 driver is done, or narrowing it to the one exact command with no `*` before `seen_payload.py`. It was still present when QA ran. I could not test the matcher; the risk is a reading, not a measurement. **The owner records: deleted, narrowed, or kept as an accepted risk.** The Orchestrator does not edit permission settings. | Owner | The INV-5 words describe the product and are true of it. The environment the owner would run this in is weaker than those words assume until this is decided. |
| **C3** | **S5: quote breakout in `/aveto-judge-seen`.** `.claude/skills/aveto-judge-seen/SKILL.md:9` puts `$ARGUMENTS` inside single quotes in a `!` shell line; Security's probe shows `r101' ; echo INJECTED ; '` running a second command under `/bin/sh`. Whether Claude Code escapes `$ARGUMENTS` or splits and prompts was not testable offline. The skill is eval-only and model-invocable by design (F12). Stage 7 results are unaffected (all 48 transcripts matched a key payload by hash; an injected prompt would have voided the batch). The fix edits a frozen method file, so it voids the freeze for any future use. **Until the owner decides (fix, disable or retire, or accept), `/aveto-judge-seen` is not invoked again**, and only the owner types it, as `r` plus three digits. | Owner | Required-fix by Security; a potential command-injection path into the operator's session, with the main conversation reading untrusted passages and replies (S3). |
| **C4** | **Confirm the lint gate on the final tree, and acknowledge D6.** (a) A session with a shell runs `uv run ruff check`, `uv run mypy`, `uv run pytest` on the final commit and records the output (I could not; the Orchestrator's report is what I relied on, and D6's directive has trailing prose after `# ruff: noqa`). (b) D6 is an Orchestrator default under SI-1: the lint gate now passes because three committed Security evidence scripts exempt themselves. The product, tests and tools are not exempted and `pyproject.toml` was not touched. I do not read this as skipping a release gate in the rule 4 sense (the gate still runs on everything the product ships), but it is exactly the kind of change the owner should see. The owner may veto it; the alternatives QA named were to fix the 23 lint errors or to untrack the scripts (`git rm --cached`). | Orchestrator (a); owner by exception (b) | A gate that went red and was turned green by a suppression comment is a thing to show, not bury. |
| **C5** | **Record hygiene.** (a) Add the owner's identity (the handle used as `operator` in `trace.json`) to the approvals, and a time of day if the owner wants one. (b) Correct STATE: add record 8 to the Approvals table; the stage row "Rule 4 approval (INV-4/INV-5) ... pending" should read approved by record 5 and 8. (c) One owner line stating the DPA and vendor-risk position for Anthropic through the owner's own session (rule 6 says the DPA status is surfaced; no artefact states it). None of this changes any approval's validity. | Owner (a, c); Orchestrator (b) | Rule 3: "who approved is an identity, not a role". |
| **C6** | **Stage 10 (docs) carries the full set of figures, not the bar results alone.** README and `CURRENT_MVP_STATUS.md` state only recorded figures (intent Done means): Bar 1 stage 5 20/20 and stage 7 24/24; Bar 2 stage 5 24/28 and stage 7 16/19 (84.2%, one question of margin at both); judge errors 0; never-abstain figures; best-score rule NOT MET on both stages; **end to end 16/24**; retrieval gate exit 1 (19/24 = 79.2%); D4 source reuse; one run only. The scope review also asked stage 10 for a precise line separating this judge step from "any generative model call", which the intent keeps out of scope. No claim of "answers questions" or of a pass on the retrieval gate. | Tech Writer (stage 10), checked by the owner | The intent: "state only the recorded figure and only after the verdict." |

**Accepted risks (stated now; they carry forward unless the owner objects):**

| # | Risk | State |
|---|---|---|
| R-A | **Retrieval gate exit 1 on the fifth set** (19/24 = 79.2%, not a registered bar). The judge cannot repair a retrieval miss: 5 answerable questions are lost before the judge sees them, 3 more to over-abstention. | Open. Same 79.2% as the dev set, by design. **The owner accepts it in their own words, or declares it relevant to the release.** It does not stop an internal release; it bounds what any document may claim. |
| R-B | **Bar 2 passes by one question at both stages.** The verdict rests on one scoring of 19 questions, held-out by rule, not repeatable. | Accepted by the registered design; named so nobody reads "MET" as "comfortably". |
| R-C | **S1, S2, S3, S4, S7, S8 advisories** (normalised-question echo; a `reply.txt` symlink survives cleanup; passage text can imitate payload structure and carry Cc/Cf characters; any model can spawn the judge, with a `model` override, so on the operator path the "judged" label proves the prompt, not the model; `retrieve` echoes a raw question; a docstring cites a record not on this branch). | Carry forward to a later slice or close-out. Not blocking per Security. S3 and S4 sit with C2 and C3: they are why the main session's permissions matter. |
| R-D | **Model-marked test failing in the committed tree** (`test_sample_derivation_reproducible`, cause confirmed, test frozen). | A later slice changes it to compare the frozen prefix. Until then `-m model` is red by 1. |
| R-E | **What Claude Code does that no test shows:** that the judge's `PreToolUse` hook runs (0 tools were offered, so it never fired); the exact session-context list beyond what was measured. | Disclosed in INV-4 and INV-5. |
| R-F | **Telemetry is self-reported**; stage estimates were overrun (Scope +78%, Architecture pass 2 +83%, Label review +105%, others less). | Total 1903k of the 2600k plan (73%) before this stage; ceiling 3400k not approached. Orchestrator records this stage's spend. |

## Rollback plan

Lifted from `02-tech-spec.md` section 13, checked against what exists in the tree.

1. **Before any merge: do not merge**, or `git revert` the slice commits on the branch in reverse order. Nothing reaches `main` until the owner merges (spec section 13). Nothing has been pushed or merged by any agent in this run.
2. **After a merge, disable the operator path only:** `git rm -r .claude/skills/aveto-judge/` and commit. The directory exists (`.claude/skills/aveto-judge/SKILL.md`). `judge-input` and `judge-apply` stay offline and inert without a reply; `retrieve` is untouched (it is not in the diff against `main`: only `__main__.py`, `judge.py`, `judge_eval.py` changed under `aveto_support/`, per QA).
3. **Full revert:** `git revert -m 1 <merge-commit>` and the regression. This assumes a merge commit; if the owner squashes or fast-forwards, the revert target differs and must be named at merge time. **INV-4 and INV-5 return to their pre-slice text, which is a safety-control text change (rule 4): it needs the owner's own words before the revert lands. The revert must not be applied on an assumed approval.** README and `CURRENT_MVP_STATUS.md` revert with it.
4. **D1 only** (the seven harness tools): reverse the two hunks (agent file and `DENY_LIST`), with the owner's approval, run `uv run pytest tests/test_judge_artefacts.py`, start a fresh-load session. **Correction to the spec:** it names `D1-diff.md`; no such file exists. The diff is `runs/docs-answerability-2/03a-d1-proposed-diff.md` (STATE; record 7 says it was applied with `git apply`, so `git apply -R` of its fenced diff is the reverse).
5. **Eval data only:** `git rm -r runs/docs-answerability-2/judge-check/`; no product effect.
6. **Outside git (added by me):** the gitignored `.claude/settings.local.json` rule (C2) is not in any commit, so no git rollback removes it. Its removal is the owner's. Claude Code transcripts in `~/.claude/projects/` are the owner's session data and no rollback touches them.
7. The program writes nothing persistent except `.aveto-judge/` (gitignored, deleted on every `judge-apply`; a symlink there survives, S2).

Rollback gate: MET. The spec has the section, the paths it names exist (one name corrected above), and the INV revert is correctly marked as needing rule 4 approval.

## Post-launch monitoring

Not required at tier 2 and not written. If the owner rules tier 3 (C1) it is required and absent. Minimum content for that case, for whoever writes it: the signals are the attended operator's own observations of the two outputs, the judge-error count (stderr category, exit 4), the over-abstention rate against the 3/19 and 4/28 seen so far, and any run where the judge's offered-tool count is not 0; owner of the monitoring is the Post-Launch Learning Agent. Thresholds are the owner's to set; I invent none.

## What "internally releasable" allows, and what it does not

**Allows:** treating the branch `claude/docs-answerability-2` as a tier 2 release candidate; stage 10 (docs and status) proceeding on this verdict, under C6; the close-out; the owner using the product in their own attended sessions as already approved by records 2, 3 and 6 (this verdict neither grants nor withdraws those).

**Does not allow, and I have not done or approved:**
- no `git push`, no merge to `main`, no deploy, no PR, no tag. All are the owner's and each needs the owner's own typed yes in the driving session (rule 3 and the standing instructions). No such request has been surfaced, so there is no record to confirm.
- no announcement, no external description of the result as a product capability, nothing posted anywhere (INV-1).
- no unattended, scheduled or API use of the judge; no `claude -p`; no metered API.
- no invocation of `/aveto-judge-seen` (C3), and no further session in this worktree without the owner having decided C2.
- no move of a bar, no rescore, no use of the reserve questions, no edit to any frozen method file (the freeze is verified to hold at `69fd907` by QA; D6 touched only the three probe scripts).
- no relabelling of the retrieval-gate exit 1 or the 16/24 figure as anything but what they are.

## Decision

- [ ] **Go**: slice lands now. **Not ticked: nothing lands. Landing (merge or push) is the owner's, with its own approval.**
- [x] **GO WITH CONDITIONS: internally releasable, not announced**, under C1 to C6 and the accepted risks R-A to R-F. The conditions are not satisfied by this verdict; they are the owner's and the named roles' to resolve before any push or merge.
- [ ] **No-go**: not issued. It becomes the verdict if (i) the owner rules tier 3 and no monitoring plan exists, (ii) the final-tree ruff, mypy and pytest run (C4a) is not clean, or (iii) any method file is found changed after `bca0e40`.

I could not verify (ii) or (iii) at this commit with my tools; (ii) is C4a, (iii) rests on QA's empty freeze diff at `69fd907` and the Orchestrator's statement about `3e1c939`.

## Hand off

- **To the Orchestrator now:** the conditions list; STATE corrections (C5b); the Orchestrator's own spend for this stage (I recorded none). Stage 10 (Tech Writer, est. 30k) may proceed under C6.
- **To the owner:** C1 (tier), C2 (S6), C3 (S5), C4b (D6), C5a and c (identity, DPA line), R-A (retrieval gate), and, separately, whether and when to push or merge.
- **To the Post-Launch Learning Agent:** after the owner lands the slice and there is a signal to learn from. Not before. Carry-forward list: R-C advisories, R-D test fix, QA's proposal that a later slice either gate `ruff` over `runs/` or keep probe scripts untracked.

