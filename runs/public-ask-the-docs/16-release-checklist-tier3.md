# Release Checklist: public-ask-the-docs (stage 16, Release Gate, tier 3, depth standard)

> Owner: Release Manager (`claude-sonnet-5-5`, effort high, Charter C3.3). Tree: worktree `.claude/worktrees/public-ask-the-docs`, HEAD 9f40e9a. I have no shell: every command result below is the Orchestrator's saved output (`16-final-tree-checks.txt`, `charter-check-output.txt`) or a file I read myself. **(U)** marks a claim I could not confirm, with where I looked. The held-out gate set was not opened (Charter C6.7); this stage scores nothing.
> Tier: **3**. Source artefacts: `intent.md`, `CHARTER-v2.md`, `APPROVAL_RECORD-1/2.md`, `05-tech-spec.md`, `06-ai-risk-assessment.md`, `07-compliance-data.md`, `code-review.md`, `13-qa-evidence.md`, `14-security-review.md`, `15a-safety-text-note.md`, `15c-words-check.md`, `.agentic/SAFETY_INVARIANTS.md` (final text), `docs/runbooks/public-ask.md`, `aveto_service/render.py`.

## 0. Verdict (details and numbered conditions in section 9)

**GO WITH CONDITIONS, for stage 17 steps 1 to 4 only: deploy with the kill switch ON.** Nothing is NOT MET that stops a deploy whose kill switch is on. Two items are NOT MET as written (the Approvals rows for the gated actions; the processor record in the runbook) and one check is stale (the saved final-tree checks name b0cf09d, HEAD is 9f40e9a); the pre-deploy conditions P1 to P4 (section 9A) cure them. If any P-condition is not met when stage 17 starts, this verdict reverts to NO-GO.

**This verdict does NOT authorise stage 17 step 5 (kill switch OFF).** That step is the first time the service answers a visitor and calls the model. It needs the switch-on gate in section 9B (S1 to S9), evidenced in the stage 17 artefact. I recommend one smoke-depth Release Manager re-spawn to confirm 9B from that artefact, because the decision "does the slice go live" is this role's, not the executor's.

**Not covered by this verdict:** how the live service behaves (no Azure resource exists, the image has never been built, no Anthropic call has ever been made); the gate result (stage 18, the set is unopened); the owner decisions D1 to D7 and the legal items OI-1 and G8 (owner, at the end review); the merge (never in the run, Charter C8.2).

## 1. Tier classification

**Tier 3, as recorded.** The slice deploys a public service to Azure (rule 3), wires a real model client behind a placeholder that threw (rule 5), routes visitors' questions to a third-party processor the owner is billed by (rules 1 and 6), edits two safety invariants (rule 4) and grants two RBAC roles (rule 3). `docs/RELEASE_GATES.md` Tier 3: "anything that sends, submits, deploys ... touches a third party ... alters permissions". Nothing lowers it.

**Code-review tier re-derived from the diff: High, same as `code-review.md`.** `CODE_REVIEW.md` section 2 puts "safety invariants", "a model or processor line" and "anything a Charter line (C5.x) names" in High. The final diff vs main (`16-final-tree-checks.txt`) contains `.agentic/SAFETY_INVARIANTS.md` (C5.1/C5.2: +151 lines), which `code-review.md` said was not yet in the diff at e08befc; the model call (`anthropic_judge.py`, C3.1), the processor path (C4.1) and the infra (`infra/main.bicep`, `Dockerfile`) were already there. There is no tier above High. Consequences of High that I carry: the owner reads the change itself (the final INV-4/INV-5 words, section 3 here), and a rollback is rehearsed before it is offered (section 6).

## 2. Charter and run-record checks (Process v2)

| Check | Evidence | Result |
|---|---|---|
| Approval of Charter v2 holds the human's verbatim approval by sha256 | `APPROVAL_RECORD-2.md`: "I approve runs/public-ask-the-docs/CHARTER-v2.md, sha256 e04b8253...ead4", Gopal Patwa, 2026-10-21T20:29:11Z, hash re-computed before recording | MET |
| `charter-check-output.txt` shows the same sha256 and "charter complete" | `charter-check-output.txt`: `charter complete: runs/public-ask-the-docs/CHARTER-v2.md`, sha256 `e04b82539e1fe17ed86d945a93b761dafef4f19c1af30dc4353f31743fc8ead4`; same hash in STATE.md Charter line and in `16-final-tree-checks.txt` | MET (I compared the three strings; I did not compute the hash) |
| v2 differs from v1 only in C4.1 and C5.2 | `APPROVAL_RECORD-2.md` states exactly two lines; I read v2 in full and v1 only through that record and the 15c stops, not line by line against v1 | MET on the record; **(U)** no v1/v2 line diff (no shell) |
| No allow rule in a tracked settings file (C6.P) | `16-final-tree-checks.txt`: "method files vs main (must be empty): aveto_support prompts .claude" prints nothing, which includes `.claude/settings.json`; the Orchestrator's separate `git diff <base> -- .claude/settings.json` file was not among the saved files | MET (via the `.claude` diff); **(U)** the separate settings.json output is not in the run folder |
| `code-review.md`: every finding fixed with a commit, or carried with the reason | CR-1, CR-2, CR-5, CR-6 fixed in 052b36c; CR-3 intentional (outside the Charter, owner decision D1); CR-4 intentional until the stage 17 check S-C1; CR-7 rejected (UX spec defines no expired-result state; noted for END_REVIEW); CR-8 intentional (needed by stage 18, owner decision D3). No correctness finding is unaddressed without a reason | MET |
| Approvals table cites a Charter line for every gated action | STATE.md Approvals holds two rows only (the two Charter approvals). No row yet for the rule 4 safety-text change (done at stage 15), nor for the rules 3, 5, 6 actions | **NOT MET as recorded**: cure P1. The Charter lines exist (section 4); the rows do not |
| Spend vs the Charter caps | STATE.md: 2004k spent vs plan 2000k, ceiling 3000k, hard cap 3600k (C2). Above plan total, under the ceiling: the run continues, no stop | MET |
| Depths not lowered (C7) | Security stage 14 ran at adversarial (`14-security-review.md`, title); Release Gate tier 3 | MET |

## 3. Safety-text changes (rule 4): the final words against Charter v2 C5.1 to C5.4

Sources: the saved word-level removals in `16-final-tree-checks.txt`; `15c-words-check.md` (checked the round-1 words; its stops S10 and S11b were resolved by the v2 amendment, APPROVAL_RECORD-2); `15a-safety-text-note.md` round 2; and I read the whole final `.agentic/SAFETY_INVARIANTS.md` at HEAD.

**Removed words (vs main = 2919c87), complete list from the saved check:** `it runs only in the`, `and`, `exception,`. Nothing else is removed or reworded.

| Removed or changed | Inside which Charter line | Result |
|---|---|---|
| `it runs only in the` and `and` (original lines 42 and 43): the C5.1 sentence is replaced by "judging has exactly two callers. (1) The operator's own Claude Code session, which runs that agent; nothing in the program (`python -m aveto_support`) calls it. (2) The public service's `POST /ask` ..." naming `claude-sonnet-5-5`, no `tools` in the request, `answerability-judge-v1` at the pinned sha256 and the same verdict-only parser | C5.1 "may replace the sentence ... with words naming exactly two callers" | MET. The retained words ("operator's own Claude Code session", "nothing in the program ... calls it") are kept; the program's guarantee is not weakened |
| Original line 40 ("The judge is the agent ...") | C5.1 does not allow editing it; round 1 had inserted words (15c S1) | MET: round 2 reverted it; the saved word diff shows no change to line 40, and I read line 40 as the original |
| `exception,` -> `exception on the attended judge step,` (INV-5, the sentence "The operator's session is the one exception ... and it is not the program.") | C5.2 as amended in v2: that one sentence "may be reworded only to say that the operator's session is one of two exceptions, the other being the service; no other word of it changes" | **MET WITH A READING NOTE, N1** (below) |
| INV-5 service exception, mapping (a) to (c), test names, "Not enforced by any test" lists, the F2 sentence ("The key is the one credential the service sends; 'No credentials are sent' above is about the program's two GET downloads.") | C5.1 mapping and test names; C5.2 "may add one exception for the service alone ... carrying only the data in C4.1 ... may add the names of new tests" | MET: additions only (the saved check lists no removal). The 19 header names in INV-5 equal the 19 in v2 C4.1 name for name (I compared the two lists) |
| INV-1, INV-2, INV-3 (C5.3) | no word changes | MET: the first hunk of the diff starts at line 42; INV-1 to INV-3 are lines 10 to 27 |
| `prompts/answerability-judge-v1.txt`, `.claude/agents/aveto-answerability-judge.md`, the two judge skills, `.claude/hooks/` (C5.4) | byte-identical to 2919c87 | MET: `git diff main` over `aveto_support prompts .claude` is empty; the prompt's sha256 equals `PROMPT_SHA256` (`24b244d2...a159427`, both strings printed in the saved output) |

**Reading notes the owner must see at the end review (Approval by Charter, item 6: the human sees the final words).** None is a stop; each is an advisory I carry.
- **N1 (the S10 sentence).** The reworded sentence says "the one exception on the attended judge step"; the words "one of two" are not in it. The second exception is stated in the next, added sentence ("The public service is the other exception"). The added words are exactly the smallest amendment 15c named for S10 ("C5.2 allows the words `on the attended judge step`") and the v2 line was drafted from that finding, but the sentence taken alone still says "the one exception". If the owner reads "reworded only to say one of two exceptions" literally, this is a stretch by one qualifier; if not, it is inside. I rule it inside the line, because every retained word is kept and the paragraph as a whole says two exceptions; I do not widen it further.
- **N2 (past the literal).** 15c S5 and S6: the page mapping ("as its page for a form post or the page's own script"; "the page shows the same passages as the JSON and no deciding-signal line") and the service-transcript parenthetical are not in C5.1's literal list ("the service's JSON"). 15c ruled them bounded restrictions, removable without making anything false. Carry to END_REVIEW.
- **N3 (the bold INV-4 sentence, 15c R1).** "the verdict decides only whether `retrieve`'s whole output is printed" is a retained sentence the service reads differently: it shows each passage's full text, not the CLI's excerpt. The (a) mapping says so. Reads true if "whole output" means the whole result; fails only if it means the CLI's printed excerpts.
- **N4 (new, from me): a stale pointer.** INV-5 says each request carries "only the data in Charter C4.1 of `runs/public-ask-the-docs/CHARTER.md`". That is the superseded v1. v1's C4.1 does not list the protocol fields or the 19 headers; v2's does. The sentence still holds because INV-5 lists the headers itself two lines later, but the pointer names the wrong file. Cure after the deploy: the Architect (the only writer of that file) changes the pointer to `CHARTER-v2.md`. That edit is to the added service exception, which C5.2 lets be written; it needs no Charter change. Not worth a pre-deploy commit.
- **N5 (the round-2 words were checked by me, not by the 15c checker).** 15c read the round-1 words. The round-2 edits are S1 (a revert), F1 and F3 (the checker's own wording) and F2 (one sentence). I read the final file against C5.1/C5.2 and find every changed word inside; I am Sonnet, the author was Opus (Charter C5 intro). **(U)** The commit message of 9f40e9a says "safety-word alignment"; the saved removals list and the file I read agree, but I did not see that commit's diff.

## 4. Human approvals (HUMAN_APPROVAL_RULES; Approval by Charter, Charter v2 sha256 `e04b8253...ead4`, approver Gopal Patwa, 2026-10-21T20:29:11Z, `APPROVAL_RECORD-2.md`)

Each gated action names a line of Charter v2 that names it exactly. "Row" is whether STATE.md's Approvals table has it today (it has none of them: P1).

| Gated action | Rule | Charter v2 line (exact words) | Happens | Row in Approvals |
|---|---|---|---|---|
| Real model client behind the placeholder: `claude-sonnet-5-5`, effort high, no tools, prompt `answerability-judge-v1`, verdict-only parser, via the Messages API at runtime | 5 (and 1: a third-party API the owner is billed for) | C3.1; C5.1 for the INV-4 side; C6.6 ($10 console limit, owner's statement) | built (stage 9); first live call at stage 17 after step 5 | no (P1) |
| Anthropic as processor: question (at most 500 characters), fixed prompt, passages, plus the protocol fields and the 19 SDK header names; no IP, visitor id or visitor header | 6 | C4.1 (as amended in v2). DPA text unread: recorded as "in place by reference per the owner's statement; text unread", never MET (G9) | first live call | no (P1) |
| Microsoft Azure as host: image, vault secret, HTTPS in transit, abuse log lines 7 days | 6 | C4.2 | stage 17 | no (P1) |
| INV-4 and INV-5 words | 4 | C5.1, C5.2 (as amended in v2); C5.3 and C5.4 held | done at stage 15 | no (P1) |
| Create ACR, Log Analytics workspace, Container Apps environment, Container App (scale to zero, external HTTPS), user-assigned identity, in `rg-aveto-ask` (eastus2) | 3 | C8.3 | stage 17 steps 1 and 3 | no (P1) |
| Role assignments `Key Vault Secrets User` on `kv-aveto-ask-gp` and `AcrPull` on the registry | 3 (RBAC) | C8.3 | stage 17 step 1 | no (P1) |
| `az acr build` from the branch | 3 (and 5: a network call in the build path; the build runs `ingest`'s existing two GET downloads, no user data) | C8.3 "build and push the image from the branch with `az acr build`"; INV-5 (a) and (b) | stage 17 step 2 | no (P1) |
| `az deployment group create` of the repo's Bicep | 3 | C8.3 | stage 17 steps 1, 3, 4, 5 | no (P1) |
| Kill switch ON | 3 (feature flag) | C8.3 "set the kill switch on or off"; C8.1 | stage 17 steps 3 to 4 and any rollback | no (P1) |
| Kill switch OFF (the service answers visitors) | 3 (feature flag for real users) | C8.3 "set the kill switch on or off". The Charter names the action; this checklist sets the conditions before it (9B) | stage 17 step 5 | no (P1) |
| Push `claude/public-ask-the-docs` to origin; open a PR into `main` with `END_REVIEW.md` linked | 3 (push) | C8.2 (never merge) | end of run | no (at the action) |
| Removing resources | 2 | C8.3: only on the owner's word. Not in this run | never | n/a |
| Merge | 3 | not covered by any line | never in the run | n/a |

Nothing in the diff or the plan needs a line the Charter lacks. Not covered, and so a STOP if it comes up (Charter section 9, stop 1): an Azure budget alert (S-A11/D5), `minReplicas: 1` or a counter store (CR-3/D1), narrowing the vault role (S-A9/D6), any second model, any other resource, a second image registry, any DNS or custom-domain step. A deployer without rights to create the two role assignments at the vault scope is a credential or ownership matter (stop 3), not something to work around.

**Approver identity** (HUMAN_APPROVAL_RULES rule 3): Gopal Patwa, the person; recorded in `APPROVAL_RECORD-1.md` (v1, 2026-10-21T06:42:08Z) and `APPROVAL_RECORD-2.md` (v2). The timestamps are the Orchestrator's `date -u` at recording; the owner's messages carry none (stated in the record).
**(U)** `verify-approvals.mjs` (approval records against GitHub) was not run by me and its output is not in the run folder; the Orchestrator may run it.

## 5. Gates, Tier 1 + 2 + 3 (RELEASE_GATES.md), each with its proof

Key: MET / MET WITH GAPS / NOT MET / NOT YET (needs the live service or the deploy; the stage that proves it is named).

### Implementation (Tier 1 and 2)

| Gate | Proof | Status |
|---|---|---|
| Typecheck | `16-final-tree-checks.txt`: mypy "no issues found in 45 source files" | MET |
| Targeted tests | the new test files `test_service_{api,limits,logging,pages,pipeline}.py`, `test_anthropic_judge.py`, `test_infra_static.py` are inside the 636; QA ran mutations a to f on them | MET |
| Full suite | `16-final-tree-checks.txt`: 636 passed, 12 deselected, three consecutive runs (425 on main + 211 new). The 12 deselected are the `network`/`model` marks (`addopts`), never run in this slice | MET; **(U)** the 12 deselected tests were not run (they need the network or a model) |
| Build passes | A Python package has no compile step; the container image was never built (Docker daemon down at 11c; `az acr build` is stage 17 step 2). `bicep build` exit 0 | **NOT YET (stage 17 step 2)**: "ingest runs inside the build", the venv copy and a non-root start are unverified |
| One commit per task | The five commits visible in the session header are one per stage or round (`stage 14`, `security round 2`, `stage 15`, `Charter v2`, `runbook ...`). The full `git log` was not saved | MET WITH GAPS **(U)** (no shell; only 5 commits seen) |
| No new lint warnings (`git diff --check`) | ruff "All checks passed!"; the `git diff --check` output is not in the saved checks | MET for ruff; **(U)** `git diff --check` not run: condition P2 |

### QA

| Gate | Proof | Status |
|---|---|---|
| UI verified in preview | `13-qa-evidence.md` addendum: enhance.js path, no external origins, contrast (light at least 6.39:1, dark at least 8.89:1), 320 px, keyboard focus, in the built-in browser against a local copy with a FAKE judge | MET WITH GAPS: screen reader, forced-colors and reduced-motion not checked; the no-JS form post covered by curl only, not re-run in a browser |
| Local regression passes | the four-command regression above, three runs identical | MET |
| Safety invariants verified | INV-1: no code posts to GitHub (grep, QA and Security 8c). INV-2: byte-identity test and mutation (e). INV-3: vacuous, no drafting. INV-4: verdict-only; 25 hostile replies, answer bodies byte-identical (Security 1a). INV-5: names, host, headers (Security 3, offline capture). The words: section 3 | MET WITH GAPS: INV-4/INV-5 hold in behaviour offline; the real judge's behaviour on hostile text is the gate (stage 18); the header values and `/v1/messages` path are not test-enforced (disclosed in INV-5's own text) |

### Security

| Gate | Proof | Status |
|---|---|---|
| No secrets or credentials in the diff | `16-final-tree-checks.txt` scan: 3 hits, all in test files and all dummy strings (`sk-ant-test-key-zzz999`, two `assert ... not ... sk-ant`); Security 4: no key in image recipe, Bicep, outputs or `runs/` | MET |
| No PII or sensitive data logged | `test_question_never_logged`, `test_abuse_line_shape_exact`, `test_ops_lines_fixed_codes_only`, `test_library_loggers_silenced`; QA local run: 185 stdout lines all abuse or ops lines, stderr empty; Security 12 runs the same | MET offline. The platform's own logs: **NOT YET (stage 17, G3 and S-C1 step 3)** |
| Audit events cover state changes | Every `POST /ask` writes exactly one abuse line (`_finish` on every pipeline path, `refuse` on every route refusal; Security section 10 closing note); the outcome set is closed in `abuse_log.Outcome`. No audit event removed or weakened. The service has no other state change of its own | MET WITH GAPS: see section 7 (kill-switch toggles and deploys are ARM activity records, not app events **(U)**) |
| Adapter boundary placeholder still throws | `PlaceholderJudgeClient` raises and is used when no key is set; `test_placeholder_judge_raises_and_pipeline_maps_to_judge_error`, `test_placeholder_judge_when_no_key`; the 425 base tests including `test_program_offline_no_model` pass | MET |
| Security Review at adversarial depth (Charter C7.1) | `14-security-review.md`: PASS WITH REQUIRED FIXES, 0 blockers. S-R1 (retrieval cap), S-R2 (kill-switch test), S-A1 fixed in 8b3c978; round 2 S-A2, S-A4, S-A6, S-A8 and telemetry off. The fix tests exist: `test_retrieval_cap_counts_requests_turned_away_after_retrieval`, `test_health_answers_while_the_thread_pool_is_saturated`, `test_pipeline_kill_switch_refuses_without_retrieval_or_model`, `test_cross_site_post_is_refused_before_retrieval_and_model`, `test_base_url_env_cannot_redirect_and_header_set_is_exact` (I grepped the names; I did not run them) | MET WITH GAPS: the S-R1 fix and the round-2 fixes were re-checked by the Orchestrator (suite green, diff read), not re-attacked by Security (U). The 30-a-hour retrieval cap and the async `/health` are in the code (`limits.py:20`, `app.py:175`) |

### Release (Tier 2)

| Gate | Proof | Status |
|---|---|---|
| Human approval points satisfied | section 4 | MET in the Charter; **NOT MET as recorded (P1)** |
| Rollback plan exists | tech spec section 7 "Rollback" and `docs/runbooks/public-ask.md` section 2 (kill switch ON; previous image tag; before step 3 nothing is public) | MET; confirmed against the diff in section 6 |
| Release checklist filled | this file | MET |

### Tier 3 only

| Gate | Proof | Status |
|---|---|---|
| Explicit human approval per HUMAN_APPROVAL_RULES | Charter v2 by hash; section 4 | MET (Charter), recording P1 |
| Dry-run on a fixture before live | section 6 | MET WITH GAPS |
| Audit event coverage manually verified | section 7 | MET WITH GAPS |
| Post-launch monitoring plan | section 7 | MET WITH GAPS |
| Rollback drill executed (deploy-half gate in RELEASE_GATES) | not yet: no Azure resource exists | **NOT YET**: kill-switch revisions rehearsed at stage 17 (S5, E3); previous-image rollback cannot be rehearsed with one image (section 6) |
| Post-deploy smoke that re-asserts the safety invariants | stage 17 and 18 (Production Verification) | NOT YET |
| Eval-gated merge (AI slice) | the 20-question gate, pre-registered, at stage 18; hash `7eb4f588...6064f` | NOT YET (stage 18) |

## 6. Dry run before live, and the rollback confirmed against the diff

**What the plan is.** Tech spec section 7 steps 1 to 5 and the runbook: steps 1 to 4 leave the kill switch ON; after the off-state, health, headers, XFF (S-C1), retention (S-C2) and build (S-C3) checks, step 5 switches it OFF, and the first judge call follows.

**Does that satisfy "dry-run on a fixture before live"? Partly, and the part that cannot be dry-run is stated, not hidden.**

- *The fixture for everything that can have one.* (i) `tests/service_fakes.py` `FakeJudgeClient` (records every `(system_prompt, payload)`, returns a scripted reply or raises) with the real index and embedding model: QA's local run (127.0.0.1, 100 passages byte-identical, hostile questions, limits, logs) and Security's attacks (25 crafted replies). (ii) An offline capture of the real SDK request through an in-process mock transport (Security section 3): host, 5 body keys, 19 headers, no visitor data. (iii) Azure: `bicep build` exit 0 and `what-if` with `deployApp=false` creating only the six non-app resources (STATE note after stage 11, run by the Orchestrator; nothing was created). (iv) The deployed-but-OFF service at stage 17 steps 3 and 4: the page, `POST /ask` and `/health` in the off state, headers, retention, the XFF check, with no retrieval and no model call (each POST writes a `service_off` line).
- *What has no fixture.* The Anthropic call itself. With the kill switch ON, `POST /ask` refuses before it reads the body, so there is no path that makes a real call while the switch is on. The first real call is therefore made after step 5, with the service reachable by anyone who has the unlisted URL (no link from aveto.dev; 06 section 9 records this as accepted by the Charter, C8.1 and C8.5). That call carries the (U) items that only it settles: the model id and `output_config.effort` accepted, usage fields, price.
- *Why this is acceptable here, and what bounds it.* A request the API rejects (a 4xx) is charged $0 (CR-2: `status_4xx` and `connection` charge 0) and the visitor sees only `judge error` with nothing else (tested, INV-4 (c)); the money is bounded by the $10 console limit (owner's statement, C6.6; unverifiable by an agent, D7) and by the day's share. The failure shapes of the first call are fail-closed. I rule: **MET WITH GAPS**, on the conditions S6 (a single canary question is the first call, made by the operator, with the stop rules in S6) and S7 (kill-switch ON is the response to any unexplained result, C8.1).
- *Gap, stated for the owner:* a fixture-checked offline path does not tell us the real judge's answers; the gate (stage 18) measures that.

**Rollback, confirmed against the diff.** The tech spec's rollback is: (1) kill switch ON by re-running command 5 with `killSwitch=on`; (2) previous version by command 5 with `imageTag=<previous tag>`, which starts a revision of the previous image under `activeRevisionsMode: 'Single'`; (3) before step 3 nothing is public. The diff agrees: `infra/main.bicep` takes `killSwitch` (`on`|`off`, default `on`) and `imageTag`; `test_bicep_kill_switch_default_on` pins the default; `test_bicep_scale_and_ingress` pins `minReplicas: 0`, `maxReplicas: 1`, single revision. The runbook (section 2, section 3) restates the same two moves, and says the toggle makes a new revision and replaces the replica (counters reset), which differs from the intent's "without a redeploy" (no build, same image, new revision): the owner was told at the tech spec (section 4) and it is reported, not stretched. Removal of resources is only on the owner's word (C8.3); the runbook command list (section 10) now says not to delete the resource group because it holds the owner's vault. Rollback needs only commands C8.3 names.

**Rollback rehearsal (High tier: "a rollback is rehearsed before it is offered").** Not yet possible in full: (a) the kill-switch ON direction is rehearsed twice before switch-on as a side effect of steps 3 and 4 (two revisions with the switch ON; verify `/health` shows `kill_switch: "on"` after each); (b) the OFF-to-ON rollback is the one that matters and can only be rehearsed once the switch has been OFF: do it straight after the first call and before the first gate batch (E3); (c) the previous-image rollback cannot be rehearsed with a single image tag; it is rehearsed only if a second tag is built (for example after a defect fix); otherwise it stays a recorded gap for the owner.

## 7. Audit-event coverage and the post-launch monitoring plan (Tier 3)

**Where each audit event exists** (checked by reading `aveto_service/abuse_log.py`, Security section 10's closing note, and the tests named in `15c-words-check.md`; not by a live run):

| What | Where | Status |
|---|---|---|
| One line per `POST /ask`, whatever the outcome | `abuse_log.abuse_line` takes only `(ip16, outcome, now)` and writes `{"t","ip","o"}`; `Outcome` is a closed set of 11 codes: `answer`, `no_confident_match`, `judge_error`, `empty_question`, `too_long`, `unusable_question`, `body_too_large`, `bad_request`, `rate_limited`, `paused`, `service_off`. Security: `_finish` on every pipeline path and `refuse` on every route refusal, so none of them is silent. `test_abuse_line_shape_exact` pins the shape | MET (offline) |
| Process-level events | ops lines `startup_ok`, `startup_failed` (+ one of `prompt_hash`, `index`, `model`), `unhandled`; `test_ops_lines_fixed_codes_only`; named in INV-5 and in the C4.2 words (S-A12 is therefore closed in the safety text, and C4.2 itself still names only abuse lines and platform logs: the ops lines carry no visitor data) | MET |
| Cost and state counters | `GET /health`: `kill_switch`, `day`, `judged_today`, `input_tokens_today`, `output_tokens_today`, `spend_today_usd`, `daily_cap_usd` (runbook section 4). Per replica lifetime | MET WITH GAPS: reset at scale to zero (CR-3/D1); public (CR-8/D3) |
| Kill-switch changes, deploys, role grants | Azure's own deployment and activity records for the resource group; each new revision logs `startup_ok` in `ContainerAppConsoleLogs_CL` (7 days once S2 holds) | MET WITH GAPS **(U)**: the retention of the ARM activity log and whether the owner reads it were not checked (no Azure documentation read) |
| Cause of a `judge_error` | deliberately not logged (L1/M2; INV-4 (c): "The service names no cause"). The cause is found in `/health`, the runbook section 7 steps and the Anthropic console | GAP, accepted by design and stated in INV-4 |
| Page loads and `GET /health` | write no line (by design: no visitor data); the platform's ingress records are the only trace | By design; whether the ingress keeps per-request records elsewhere is **(U)** and is G3/S3 |
| Platform logs hold no raw visitor address | G3 / S-C1 step 3 / S3 | NOT YET (stage 17) |

**Post-launch monitoring plan.** It exists: `06-ai-risk-assessment.md` section 7 (signals and actions). Signals: `judge_error` share of admitted calls (over 5% in 50 calls, or 3 in a row: check Anthropic status, console cap and key, kill switch ON if unexplained); input and output tokens per judged question from `/health` deltas (over 2x the stage 18 figure: kill switch ON); `answer` share (moves 20 points from the stage 18 baseline over 100+ calls); `paused` days (more than 2 a week: owner decides on the cap); `rate_limited` on one `ip` hash (any day above 30: abuse); console spend and Azure bill vs estimate (a month over $10, or Azure over $10: stop and report); a monthly canary of 6 spent-gate questions (3 answerable, 3 not; any not-answerable question shown: switch off, new pre-registered check before re-enable); control integrity at zero tolerance (a request with `tools`, a model other than `claude-sonnet-5-5`, a prompt-hash mismatch, any shown text differing from `retrieve`: kill switch ON). Cadence: daily for the first 3 days, then at least every 5 days, weekly after a quiet month. Owner: the repository owner acts (there is no on-call); the Post-Launch Learning Agent reads the stage 18 record and each review.

- **Gap M1 (open):** push alerting is outside C8.3; detection depends on someone looking. The owner is to accept that in words at the end review.
- **Gap (mine):** the thresholds sit in a run-folder artefact only. I searched `docs/runbooks/public-ask.md`, `README.md`, `docs/ARCHITECTURE.md` and `CURRENT_MVP_STATUS.md` for "06-ai-risk" and "screening": no match. A reader of the runbook cannot find them. Cure P4.
- **Gap:** the baselines the thresholds need (tokens per question, `answer` share) do not exist before stage 18; the plan is a draft until they are recorded (E2).
- **Gap (06 M3):** stage 18 is to compare live passages with local `retrieve` byte for byte on a sample; not yet done.

## 8. Intent "Done means", line by line; enterprise and governance gates

### 8.1 Intent `intent.md` "Done means"

| # | Line | Status | Proof, or the stage that proves it |
|---|---|---|---|
| 1 | Starts from `main` (pack v26); retrieval, ranking, judge prompt, corpus unchanged | MET | method files diff vs main empty; prompt sha256 = pin; `.agentic` diff is `SAFETY_INVARIANTS.md` and `CURRENT_MVP_STATUS.md` only; no file changed outside the allowed paths (`16-final-tree-checks.txt`) |
| 2 | HTTP service `POST /ask`, `GET /health`; output exactly `judge-apply`'s, as JSON; passages byte-identical | MET | `test_service_passages_byte_identical_to_retrieve`; QA local run (100 passages); the JSON shows each passage's full text where the CLI prints an excerpt: stated in INV-4 (a) (N3) |
| 3 | Judge through the Anthropic API, `claude-sonnet-5-5`, no tools, same prompt and parser; only the question and the shown passages sent; reason never leaves the parser | MET WITH GAPS | offline proofs in 13 and 14; **NOT YET (stage 17, first call):** the API accepting the model id, `effort`, the request shape |
| 4a | 10 questions per visitor per hour by hashed IP, memory only | MET WITH GAPS | tests; **NOT YET (S-C1):** what the ingress does with `X-Forwarded-For` (CR-4) |
| 4b | Daily spend counter; "Paused for today"; no model call | MET WITH GAPS | tests; price assumed ($3/$15 per MTok, (U)); per replica lifetime (D1); measured at stage 18 |
| 4c | Over 500 characters refused before any model call | MET | `test_question_500_accepted_501_refused` and the local run |
| 4d | Kill switch, "without a redeploy" | MET WITH GAPS | env var `ASK_KILL_SWITCH` via the Bicep parameter, default on, unparsable means on; a toggle is a new revision with the same image, no build: stated to the owner (tech spec section 4), not stretched. **NOT YET (stage 17):** the toggle on Azure in both directions |
| 4e | Anthropic console limit $10 a month, set by the owner | NOT YET (owner statement only) | "c6.6 is set" (setup log); no agent can verify it (G10, D7) |
| 5 | No visitor data kept; abuse logs hashed IP, time, outcome, 7 days; a test that a question never reaches a log line | MET WITH GAPS | `test_question_never_logged` (caught by mutation d); **NOT YET (S2, S3):** 7-day retention applied and read back, no raw address in any table |
| 6 | Deployed to Azure Container Apps, scale to zero, image built from the repo with pinned models; IaC in the repo; rollback | NOT YET (stage 17) | Bicep compiles; what-if (no app) clean; image never built; rollback written (section 6) |
| 7 | Public page, plain and accessible, says what it is, its limits, that questions are not stored | MET WITH GAPS | `render.py` lines 203 to 210 say: an AI model decides; question sent to Anthropic, named, under its terms; do not enter personal or confidential information; address read, scrambled form kept 7 days; hosted in the United States (Azure East US 2): 06 R1 and 07 G1 items 1 to 5 are present in the source. Browser checks in section 5; screen reader, forced-colors, reduced-motion unchecked. **NOT YET:** the served HTML (S8) |
| 8 | A gate, pre-registered, 20 questions, scored once through the deployed service | NOT YET (stage 18) | set unopened; sha256 `7eb4f588...6064f` to be matched there (C6.7) |
| 9 | Cost per question, response time (median, slowest), cold start, monthly Azure cost, gate result, measured and reported | NOT YET (stage 18) | local figures in 13 are labelled local |
| 10 | Security at adversarial depth, code review High, Release Gate tier 3, Production Verification | MET for Security and code review; Release Gate is this file; Production Verification NOT YET (stage 18) | `14-security-review.md`, `code-review.md` |
| 11 | README, `CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md` state only recorded figures; stop saying "attended, internal" only for this service | MET | README header block ("built, not yet deployed or measured ... Every cost, speed and gate figure ... not yet measured"), CURRENT_MVP_STATUS "What exists" (nothing deployed, no figure measured), ARCHITECTURE "Public ask service"; README line 196 lists the figures as pending. **(U)** I read the opening blocks and grepped for figures (`$0.`, `ms`, `cold start`: only the "pending" list matched); I did not read every line |

"Must not break": INV-1, INV-2, INV-4 hold (section 5, Safety invariants). The attended `/aveto-judge` path: `.claude/` and `aveto_support/` are byte-identical to main; the 425 existing tests pass.

### 8.2 Enterprise and governance gates (RELEASE_GATES.md; 06 and 07 conditions)

| Gate | Status | Note |
|---|---|---|
| New data classified, retention set | MET WITH GAPS | 07 section 4; retention 7/7 is written in the Bicep and applied only at step 4; read-back S2 |
| Catalog or RoPA updated | MET WITH GAPS | no catalog exists in the repo; the entry is 07 section 9 (the runbook copy is P3) |
| Migration plan | n/a | no schema or data migration |
| Threat model for new attack surface | MET | `14-security-review.md` is the adversarial review (attacks 1 to 4, section 6 rulings); no separate THREAT_MODEL file **(U)** |
| Controls mapped; named approver | MET WITH GAPS | 07 section 8 (reference points, no certification claimed); approver is the owner, named |
| New subprocessor risk-assessed; DPA in place | **NOT MET as a DPA row; recorded as G9 requires:** "in place by reference per the owner's statement; DPA text unread" | never marked MET. Anthropic Commercial Terms incorporate the DPA by reference (C4.1); no agent read the text |
| AI capability risk-tiered; obligations met | MET WITH GAPS | 06: limited, provisional on Art. 50 applicability (OI-1) for the owner and legal |
| Eval coverage for AI safety invariants | MET WITH GAPS | the gate has 4 hostile questions, 1 of 4 testing injection through the question; the invisible-character carrier (S-A5) is not covered; the 8-of-10 bar may miss by chance (06). Bars are not changed |
| Cost-per-action estimated; kill-switch tested | MET WITH GAPS | estimate $0.008 a question, reservation about $0.046 (tech spec section 8, price (U)); kill switch tested offline; on Azure NOT YET |
| Docs match shipped behaviour | MET | 15b; runbook status banner says "not deployed ... never executed"; the vault statement fixed in 9f40e9a |
| SLOs, runbook, tested rollback | MET WITH GAPS | runbook exists; no SLO is defined (single owner, no on-call: stated in 06 section 7); rollback drill NOT YET |
| Change request (CAB) | n/a | project pack `ai-agent-product` (STATE.md); no change-advisory process exists in this repo **(U)**: I looked at STATE.md and the Charter only. The recorded, named approval is the Charter v2 by hash (Gopal Patwa) |
| 06 R1 (page copy) | MET in source; NOT YET served | S8 |
| 06 R2 / 07 G8 (owner's line on OI-1 and the legal items, in his own words in `END_REVIEW.md`) | NOT YET (owner, end review) | stays open, not accepted, until then |
| 06 R3 (Security rules on counters reset and the forwarded address) | MET | Security: CR-3 owner decision D1; CR-4 hard check S-C1 |
| 07 G2, G3, G4 | NOT YET (stage 17: S2, S3, S1) | |
| 07 G5 | MET offline; live canary NOT YET (S6) | |
| 07 G6 | MET | |
| 07 G7 (processor record in the runbook) | **NOT MET as written** | the record is in `07-compliance-data.md` section 9, not in `docs/runbooks/public-ask.md` (searched for "processor": no match). Cure P3 |
| 07 G9 | applied (row above) | |
| 07 G10 / C6.6 | NOT YET (owner's statement only; unverifiable) | D7 |

## 9. Conditions (numbered; each is testable by reading a file or a command's output)

### 9A. Before stage 17 starts (a failure of any one reverts this verdict to NO-GO)

- **P1. Approvals rows.** STATE.md Approvals holds one row per gated action in section 4, each citing `CHARTER-v2.md#C<n>.<m>` and sha256 `e04b82539e1fe17ed86d945a93b761dafef4f19c1af30dc4353f31743fc8ead4` as the record (rule 4 safety text: C5.1, C5.2; rule 5: C3.1; rule 6: C4.1, C4.2; rule 3: C8.3 for the identity, registry, workspace, environment, app, the two role assignments, the build, the deployments, the kill switch). Test: grep the table for `C3.1`, `C4.1`, `C4.2`, `C5.1`, `C5.2`, `C8.3`. The row for "kill switch OFF" is added before step 5 runs; the rows for C8.2 before the push.
- **P2. Re-check at the commit that will be built.** The saved checks name HEAD b0cf09d; HEAD is 9f40e9a. After P3 and P4 are committed, the Orchestrator saves: `git status` empty; `git rev-parse --short=12 HEAD` (this is the image tag); `git diff --check` empty; `git diff b0cf09d HEAD --stat` listing no file under `aveto_service/`, `infra/`, `tests/`, `aveto_support/`, `prompts/`, `.claude/` and `Dockerfile`; `uv run mypy`, `uv run ruff check`, `uv run pytest` once (636 passed or more); `git diff main -- aveto_support prompts .claude` empty; the word-level removals in `.agentic/SAFETY_INVARIANTS.md` still exactly `it runs only in the`, `and`, `exception,`. A different result is a NO-GO.
- **P3. Runbook processor record (G7).** `docs/runbooks/public-ask.md` gains the processor entry from `07-compliance-data.md` section 9 (Anthropic and Azure, what each receives, the DPA row worded "in place by reference per the owner's statement; text unread", retention UNKNOWN except the two named tables at 7 days). Tech Writer, docs only. Test: grep the runbook for "text unread".
- **P4. Runbook monitoring pointer.** The same pass adds a "Monitoring" section to the runbook pointing to `06-ai-risk-assessment.md` section 7 and restating its thresholds and cadence in one table, naming gap M1 (no push alerting). Test: grep the runbook for "5%" and "M1".

### 9A.2 During stage 17 steps 1 to 4 (the kill switch stays ON)

- **D1. Order and place.** Commands run in the tech spec section 7 order, from the worktree root only (S-C3), tag `aveto-ask:<12-hex HEAD>`; no command prints a secret (`az containerapp secret list --show-values`, `az keyvault secret show`, `az monitor log-analytics workspace get-shared-keys`); the saved output of every command is searched for `sk-ant` and for a key-shaped string before it is committed, and nothing is committed that contains one.
- **D2. What-if before step 3.** After step 2 and before step 3, `az deployment group what-if` with step 3's exact arguments (`deployApp=true imageTag=<TAG> killSwitch=on`) is saved. It lists only resource types in C8.3 and the secret only as a Key Vault reference. (The saved what-if covers `deployApp=false` only.)
- **D3. Off-state after step 3 and again after step 4.** `GET /` loads and says the service is off; `POST /ask` returns 503 `service_off`; `GET /health` returns `status: "ok"` and `kill_switch: "on"`, `judged_today` 0; no `Set-Cookie`; `Cache-Control: no-store`, nosniff, a CSP and `Referrer-Policy: no-referrer` on the page. Recorded with the revision names.
- **D4. Stop and hand back, never work around.** Any `startup_failed` ops line (any category); a role-assignment authorisation error (Charter stop 3); a resource appearing outside the C8.3 list (stop 1); any need to change code, Bicep or the Dockerfile. A change means a new commit, P2 again, and this checklist is reopened (the method freeze): no gate set is opened until it is frozen again.

### 9B. Switch-on gate: all of these before step 5 (`killSwitch=off`). This verdict does not authorise step 5 without them.

- **S1. S-C1, steps 1 to 3 of `14-security-review.md` section 6, with the kill switch ON,** inside one replica lifetime (a request at least every 4 minutes): ten header variants from machine A all log the same 16-hex `ip`; one request from machine B on a different public network logs a different `ip`; KQL over `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL` for A's and B's raw public addresses returns 0 hits. If step 1 fails: redeploy with `clientKey=peer` and redo step 2. If step 2 fails under either mode: do not switch on, report to the owner (D2). **If the driving session has no second public network, S1 is unconfirmed and the switch stays ON**: no Charter line covers using the owner's device or any new cloud resource for it.
- **S2. S-C2.** Both tables read back retention `7` and total `7` (runbook section 6 commands), after step 4. Anything else: the switch stays ON.
- **S3. G3.** `az monitor log-analytics workspace table list` is saved; every non-empty table is queried for A's and B's raw public addresses after the S1 requests: 0 hits; an extra table holding either with 30-day retention is a block and a report (C4.2 would be wider than its words).
- **S4. S-C3.** The build log is kept; its last `ingest` line (`wrote index/docs-index.json  sha256 <hex>`) is recorded and compared with the local index sha256, match or mismatch reported (not hidden); base image digests recorded.
- **S5. Rollback, kill-switch direction.** Both ON revisions (steps 3 and 4) verified per D3; the time from the deploy command to `/health` answering `kill_switch: "on"` is recorded (the runbook says "not yet measured").
- **S6. First call protocol.** Immediately after step 5 the operator asks one docs question containing no personal data, and nothing else, and saves the response. Pass: HTTP 200 with `answer` or `no_confident_match`; `/health` then shows `judged_today` 1, non-zero token counters and `spend_today_usd` above 0. On `judge_error` or any unexpected status: kill switch ON at once (C8.1), diagnose per runbook section 7 step 2 (the `effort` field not accepted, key missing so the placeholder judge answers), at most three further calls, and a code change reopens P2. The same call is the live canary for G5: after log ingestion, the workspace tables are searched for the question's words: 0 hits.
- **S7. Kill switch ON is the response to any unexplained result,** with no one asked first (C8.1, C8.3).
- **S8. Page copy served (06 R1, 07 G1).** The served `GET /` HTML (saved) contains: "an AI model decides", "Anthropic", "personal or confidential", "7 days", "United States". A string missing: do not switch on.
- **S9. Cap.** The owner's statement for C6.6 ($10 console limit) is in the setup log (it is: "c6.6 is set"). Labelled owner's word, not verified (D7). No change to C6.6 may be assumed.

### 9C. For the end review (`END_REVIEW.md`), and for the Orchestrator before it

- **E1. The final safety words are shown to the owner** (Approval by Charter, item 6): `END_REVIEW.md` quotes or links the diff of `.agentic/SAFETY_INVARIANTS.md` against 2919c87 and lists N1 to N5 of section 3, including the stale pointer (N4), which the Architect fixes (one file, within C5.2).
- **E2. Baselines recorded:** cost per question, median and slowest time, cold start, monthly Azure estimate, tokens per question and `answer` share, from stage 18, so the monitoring thresholds in 06 section 7 have numbers; M3 (live passages vs local `retrieve`, byte for byte, on a sample) done or listed as undone.
- **E3. Rollback rehearsal, OFF-to-ON:** after the first call and before the first gate batch, `killSwitch=on` is applied, `POST /ask` returns `service_off` and `/health` shows `kill_switch: "on"`, then `killSwitch=off`; revision names and times saved. The previous-image rollback is rehearsed only if a second tag exists; otherwise listed as an untested gap.
- **E4. Owner items listed as open, in this order:** D1 (counters reset with the replica; $10 in 3 to 18 hours), D2 (if S1 failed), D3 (`/health` public), D4 (about 40 questions pause the day for everyone), D5 (Azure spend uncapped; budget alert), D6 (vault role at vault scope), D7 (the console limit rests on the owner's word); OI-1 and the legal items (G8, 06 R2) in the owner's own words; M1; CR-7 (an expired result link shows a blank form); S-A3 (the "paused ... not a fault" copy is false during an outage), S-A5, S-A7, S-A10; the "without a redeploy" wording; the unchecked accessibility items (screen reader, forced-colors, reduced motion); the 12 deselected tests never run; the DPA text unread.
- **E5. The gate result is reported as scored.** A missed bar is a miss and the C8.1 outcome applies (kill switch ON, run stops, back on only on the owner's word).

## 10. Decision

- [x] **GO WITH CONDITIONS, for stage 17 steps 1 to 4 (deploy, kill switch ON), once P1 to P4 are recorded.**
- [ ] **Go for kill switch OFF:** not given here. Needs 9B (S1 to S9), evidenced in the stage 17 artefact; I recommend a smoke-depth Release Manager re-spawn to confirm it from that artefact.
- [ ] **No-go:** not issued. Return to the Orchestrator with the failing item if a P-condition is unmet at stage 17 start.

**NOT MET, plainly:** (1) the Approvals table rows for the gated actions (P1); (2) 07 G7, the processor record in the runbook (P3). The Build gate is NOT YET, not NOT MET: the image has never been built (stage 17 step 2). Everything else is MET, MET WITH GAPS, or NOT YET with the proving stage named in sections 5, 6 and 8.

**Could not verify (and where I looked):** the live service, Azure and the Anthropic API (none exists or was called); `git log`, `git diff --check`, the v1/v2 line diff, the diff of commit 9f40e9a and `verify-approvals.mjs` output (no shell, not among the saved files); the settings.json diff output (covered only by the `.claude` diff); that the 12 deselected tests pass; that Security re-attacked the S-R1 and round-2 fixes (STATE.md says the Orchestrator re-ran and read them); Envoy and ingress behaviour, ARM activity-log retention, probe defaults, the model's acceptance of `effort`, prices, what Anthropic keeps (the places searched are the Security review, the runbook and the tech spec; no vendor documentation was read).

## 11. Hand off

To the Orchestrator for stage 17 steps 1 to 4 after P1 to P4. After the stage 17 artefact records S1 to S9: a smoke-depth Release Manager invocation (recommended) confirms the switch-on gate, then step 5. After the slice lands (the end of the run): Post-Launch Learning Agent, with 06 section 7 and the stage 18 baselines. On a no-go: back to the Engineering Manager with the failing items listed in section 10.
