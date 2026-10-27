# Release Checklist - result-page-clarity

> Owner: Release Manager Agent (stage 8, a separate invocation from the engineer)
> Tier: **3** (the release deploys a public service; Charter C7.2)
> Candidate: branch `claude/objective-kapitsa-83d3ae`, HEAD `a506c44`, base `main` 6ab5548. Rollback target: revision `ca-aveto-ask--0000011`, image `aveto-ask:ffc2e2e5f39a` (Charter C6.5).
> Source artefacts: `intent.md`, `CHARTER.md`, `APPROVAL_RECORD-1.md`, `charter-check-output.txt`, `events-verify-output.txt`, `EVENTS.jsonl`, `00-slice-plan.md`, `00-setup-dryruns.md`, `05-tech-spec.md`, `06-implementation.md`, `06-failfirst-6ab5548.txt`, `06-test-count.txt`, `code-review.md`, `08-browser-checks.md`, `13-qa-evidence.md`, `14-security-review.md`, `15-docs-note.md`, `STATE.md`. All under `runs/result-page-clarity/`.
> Method note: this role has no shell. I read the files and the product source directly; I did not re-run any command. What I could not confirm, and where I looked, is marked UNCONFIRMED.

## Verdict: GO TO DEPLOY

All pre-deploy gates pass. No FAIL. Deploy is allowed under Charter C8.3 (three `az deployment group create` runs at most, one `az acr build`, `rg-aveto-ask` only).

The release is **not landed** by this verdict. The rollback rehearsal is a release gate that cannot be proven before the deploy, so it stays **OPEN-REQUIRED-AFTER-DEPLOY** (section 6), and so does the live half of C1.4 item 1. If either fails, Charter C8.1 applies and the release fails. The push and pull request (C8.2) wait for both.

## 1. Tier classification

**Tier 3.** The slice is a presentation change (no new route, input, header, dependency, model or processor), but the run deploys to a public service and the owner's intent and Charter C7.2 fix tier 3 with the rollback rehearsal as a gate. The tier is not lowered because the change "feels safe".

**Review-layer risk tier, re-derived by me from the diff** (`CODE_REVIEW.md` section 2). I could not run `git diff main...HEAD --stat`; I used the file lists in `code-review.md`, `13-qa-evidence.md` section 2 and `06-implementation.md`, and checked the product files against them by reading them and by comparing file modification order (UNCONFIRMED by git; see section 3, "Tested tree = candidate"). The diff touches product source (`aveto_service/pages.py`, `render.py`, `static/enhance.js`, `static/style.css`), tests and goldens, `docs/ARCHITECTURE.md`, `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md` (recorded figures only) and run records. It touches no hook, settings file, deny list, auth, model or processor line, CI file, invariant, or anything C5.0 names (headers byte-identical per QA).
**My tier: Medium. Same as `code-review.md`; no escalation.**
One item sits next to the High criteria and I name it so the owner reads it: `tests/test_service_pipeline.py:180` changes the integrity pin of `.claude/hooks/budget-guard.mjs` from `798c12fa...9922` to `222f39708d03770a33d09ba7579ee178fb78154ae60c1779239eab2cbf4a9b8e`. The hook itself is not in the diff (QA and Security both report `.claude` empty; I read the tracked `.claude/settings.json` whole and it carries no C6.P rule, section 3). The Charter names this exact value in this exact file (C1.7a) and the owner approved it by hash (`APPROVAL_RECORD-1.md`: "including both C1.7 fixes"). I read the pin and it equals the value the Charter names. I did not escalate because no control changes behaviour, but `code-review.md`'s tier paragraph does not mention this pin; `END_REVIEW.md` should list it as "the pack v30 install's doing" for the owner's read. If the owner treats it as High, the added requirements are the owner reading that line and a rehearsed rollback; the second is already a gate here.

## 2. Gates, tier 3 (`docs/RELEASE_GATES.md`)

Status: PASS, FAIL, OPEN, or n/a with a reason. A pre-deploy OPEN would block; there is none.

### Implementation

| Gate | Status | Evidence |
|---|---|---|
| Typecheck | PASS | `uv run mypy`: no issues in 54 source files (`13-qa-evidence.md` s1; `06-test-count.txt`) |
| Targeted tests | PASS | `tests/test_result_first.py`: 6 failed / 1 passed on 6ab5548 (`06-failfirst-6ab5548.txt`); 7 passed on HEAD, three consecutive runs (`13-qa-evidence.md` s4); Security re-ran 42 targeted, all passed (`14-security-review.md`) |
| Full test suite | PASS | `uv run pytest`: 738 passed, 12 deselected, 0 failed (`06-test-count.txt`, re-run by QA `13-qa-evidence.md` s1) |
| Build | n/a before deploy | `LOCAL_COMMANDS.md` has no local build step; the image is built by `az acr build` at stage 9 (Charter C8.3), and the build log with the new tag is stage 9's record. The new tag existing in `acravetoaskgp` is a stage 9 check |
| One commit per task | PASS, with a note | `a9c0bf0` fail-first tests, goldens, both C1.7 fixes; `cbbedfd` the product change; `aaf7bc1`, `d223e11`, `a506c44` run records. The C1.7 fixes share the tests commit (two small tasks in one commit); `a506c44` bundles four stages' records. No product code is mixed with records. The tech spec's rollback says the C1.7 fixes are independent; they are in the tests commit, so a revert of that commit would also undo them |
| No new lint warnings | PASS | `uv run ruff check`: all checks passed (QA s1). `git diff --check` was run by nobody I can find in the record; I grepped the changed product, test and doc files for trailing whitespace and conflict markers: 0 hits (UNCONFIRMED for the goldens, which are byte copies of rendered HTML) |

### QA

| Gate | Status | Evidence |
|---|---|---|
| UI verified in preview where observable | PASS (local); live OPEN-REQUIRED-AFTER-DEPLOY | `08-browser-checks.md`: built-in browser, stand-in judge, both sizes, answered and refused. Live is stage 10 |
| Local regression command | PASS | mypy, ruff, pytest in order (`13-qa-evidence.md` s1). The project has no `qa:mvp`; the regression is `LOCAL_COMMANDS.md` "Full local regression" |
| Safety invariants verified | PASS | `13-qa-evidence.md` s2 (empty diff over the invariant files, 16-state header comparison, golden byte-equal), `14-security-review.md` smoke table. INV-1 to INV-5: nothing under `aveto_support/`, `prompts/`, `.claude/` changed |

### Security (smoke, Charter C7.1)

| Gate | Status | Evidence |
|---|---|---|
| No secrets in diff | PASS | `14-security-review.md` "Not covered" (grep of added lines, none); my grep of `aveto_service/static` for key, secret, token patterns: 0 hits |
| No PII or question text logged | PASS | `14-security-review.md`: no `logging`, `print`, storage, cookie or beacon added. My grep of `pages.py`, `render.py`, `enhance.js` found only the existing `sendBeacon("/count/docs-click")`, which is content-free and not part of this diff |
| Audit events cover state changes | PASS (none owed) | `05-tech-spec.md` "Audit / feedback / usage events": none added or changed, no state-changing function added; Security confirms |
| Adapter boundary placeholder still throws | n/a, with evidence | No adapter file in the diff (`14-security-review.md` "Audit, adapter and approval checks"); the adapter tests are in the passing 738 |
| Security smoke result | PASS | No P0, P1 or P2; three P3 advisories. P3-3 (README) is closed below |

### Release

| Gate | Status | Evidence |
|---|---|---|
| Human approval points satisfied | PASS for the pre-deploy stages; the deploy-time rows are due when each action runs | Section 5 |
| Rollback plan exists | PASS | `05-tech-spec.md` "Rollback plan"; `docs/runbooks/public-ask.md` s2; `CHARTER.md` C8.1, C8.3. One wording point in section 6 |
| Release checklist filled | PASS | this file |

### Tier 3 only

| Gate | Status | Evidence |
|---|---|---|
| Human approval per `HUMAN_APPROVAL_RULES.md` | PASS (Charter) | Section 5 |
| Approval recorded: who, when, request, response | PASS | `APPROVAL_RECORD-1.md`: Gopal Patwa, 2026-10-27T06:13Z, verbatim words naming the file and its sha256. The record heads the time "When (UTC)", not "recorded at" as `APPROVAL_PROTOCOL.md` step 0 says; the time is taken from the environment by the Orchestrator per the record's author. UNCONFIRMED against a `date -u` output (none saved) |
| Dry run on a fixture before live | PASS | Product: stand-in judge local runs (`00-setup-dryruns.md`, `08-browser-checks.md`) and the 16-state fixture comparison with the suite's fakes (`13-qa-evidence.md` s2). Deploy commands: the `az bicep build` and `what-if` dry run is stage 9's first step (runbook s1: "what-if was run before each create") and is not yet done; not a gate on this verdict |
| Audit event coverage manually verified | PASS | `05-tech-spec.md`, `14-security-review.md`: no event added, removed, or renamed; the service's log lines are untouched |
| Post-launch monitoring plan | PASS | Section 8 |

### Enterprise and governance gates

All n/a: no overlay role is enabled for this slice (project pack `ai-agent-product`, no new data class, no schema or migration, no new subprocessor, no new AI capability, no change request process in the Charter). No gate is skipped without a reason.

### Skipped gates

| Gate | Reason | Approved by |
|---|---|---|
| (none skipped) | | |

## 3. Charter and run-integrity checks (Process v2)

| Check | Status | Evidence |
|---|---|---|
| Charter approved by sha256 in the owner's words | PASS | `APPROVAL_RECORD-1.md`: sha256 `8eacc407803700bece84af1a3344f02b871b02da10fe10a3ec620099cbd099bc`, words "I approve runs/result-page-clarity/CHARTER.md, sha256 8eacc407..., including both C1.7 fixes." Typed in the driving session by Gopal Patwa |
| Charter hash matches and file is complete | PASS | `charter-check-output.txt`: "charter complete", sha256 `8eacc407803700bece84af1a3344f02b871b02da10fe10a3ec620099cbd099bc`, identical to the approval record and to `STATE.md`. I cannot recompute a hash (no shell); the run was made by the Orchestrator just before this stage |
| C1.1 and C1.2 referenced hashes (intent `b9303e96...`, plan `1668e802...`) | UNCONFIRMED by hash | No shell. `intent.md` and `00-slice-plan.md` are the two oldest files in the run folder by modification order, older than the Charter, so not edited after it. `charter-check` does not re-hash them |
| Event log | PASS | `events-verify-output.txt`: chain intact, 387 lines, head `4b025df05af28d8d`; `EVENTS.jsonl` in the run folder has 387 lines, matching. No write outside the Charter's paths is listed. Alerts, reported, not blocking: seq 387 is `main`'s Bash call to the playbook path with no outcome recorded (the verifying call itself, same as at setup, `00-setup-dryruns.md` C6.6); `main` has 4 failed Bash calls, all before the Charter approval (seq 10, 12, 14 at about 05:47Z and seq 56 at 06:13Z, in the exploration/approval window) |
| No C6.P allow rule in a tracked settings file | PASS, direct read | The Orchestrator's saved `git diff main -- .claude/settings.json` is **not** in the run folder (only `charter-check-output.txt` and `events-verify-output.txt` are). I checked the condition itself: the tracked `.claude/settings.json` has hooks (budget guard, event log), `env` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), and a `deny` list; no `allow` key and none of the C6.P rules. QA and Security both report `git diff main -- .claude` empty. The worktree's gitignored `.claude/settings.local.json` holds old one-off rules (`git rev-parse`, `git fetch`, `git rev-list`, one compound `ls && cat`), not the C6.P list; the C6.P file is in the main checkout and is deleted after the pull request opens (stage 11). Asked of the Orchestrator: save the diff next to `charter-check-output.txt` for the audit trail |
| `code-review.md`: every finding fixed or carried with a reason | PASS | 0 Important, 2 Nits (R1-1, R1-2), both "Accepted, not fixed" with a reason and a pointer (tech spec open item 3; no data or answer affected). Neither is a correctness finding. Both go in `END_REVIEW.md` (CODE_REVIEW s5). The review is stated "unscored" per C3.R |
| Tested tree = candidate tree | PASS on my evidence; the exact command was not run by me | QA tested `d223e11`; the candidate is `a506c44`, whose message names records, docs and state only. I read the current `pages.py`, `render.py`, `enhance.js`, `style.css`: they match the tech spec and the line numbers Security and the code review cite (`enhance.js:66-80`, `:232`, `pages.py:24-33`), and every product file, test file, golden, `aveto_support/`, `prompts/`, `.claude/`, `infra/`, `Dockerfile`, `pyproject.toml` and `uv.lock` sorts older than `08-browser-checks.md` and `13-qa-evidence.md` by modification time. Not a git proof. Stage 9 should save `git diff --stat d223e11 HEAD -- aveto_service tests Dockerfile pyproject.toml uv.lock infra prompts aveto_support .claude` (expected empty) with the build record |
| Working tree | PASS | `git status` at the start of this stage showed only `EVENTS.jsonl` and `events-verify-output.txt` untracked. Both are run records outside the image (`Dockerfile` copies `aveto_support`, `aveto_service`, `prompts`, `docs-source.toml`, one eval file) |

## 4. Charter bars, C1.4 items 1 to 9

| # | Bar | Status | The record that proves it |
|---|---|---|---|
| 1 | Measured, not asserted: heading within the top 25% at 1280x800 and 375x667, answered and refused, before and after | **PASS (local); live half OPEN-REQUIRED-AFTER-DEPLOY** | `08-browser-checks.md` item 1, tree `aaf7bc1`, product commit `cbbedfd`. After: 16.1 / 16.1 px at 1280x800 (bar 200), 15.6 / 15.6 px at 375x667 (bar 166.75); 2.0% and 2.3% of the viewport. Before (main, same method): -2,820.9 / 292.1 and -4,182.9 / -2.9 (`00-setup-dryruns.md`). Stand-in judge, no model called, named in the record. The intent's 616 of 800 px is for a short live answer and is not re-measured. Docs say "NOT YET MEASURED live" (`15-docs-note.md`): no unmeasured figure is stated. The live figure is stage 10 |
| 2 | Home page byte-equal to main; order on a result page | PASS | `13-qa-evidence.md` s3: `GET /`, resting, service off, unknown token, scorecard, health byte-equal main vs HEAD; the three `GET /` goldens written on 6ab5548 equal both. DOM order on a result page: title and statement, form, result, "What to expect", suggestions (`08-browser-checks.md` "Order"; T1 passes) |
| 3 | Strings unchanged | PASS | `13-qa-evidence.md` s3: 0 added and 0 removed on all eight result states; the multiset of whole HTML lines is identical main vs HEAD (only reordered); T3 and T4 pin them. The script diff adds identifiers and the number 16 only. I read `render.py` and `enhance.js` and found no new visitor-facing literal |
| 4 | Nothing about answering moves | PASS | `13-qa-evidence.md` s2: `git diff main --stat -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md` empty; `/ask` golden sha256 `56e4b77b...e281c` on main and HEAD, 39 cases, not in the diff; all response headers equal in 16 states (CSP ends `frame-ancestors 'none'`), `test_ask_json_bytes_equal_main` passes. `.agentic/CURRENT_MVP_STATUS.md` is the one `.agentic` file changed (C1.3 allows it, recorded figures only); I read the entry and every figure traces to `08-browser-checks.md` or `13-qa-evidence.md` |
| 5 | Focus lands on the result | PASS | T5 asserts `region.focus({ preventScroll: true })` via `land()`, no bare `region.focus()`, `#result` keeps `tabindex="-1"`; the browser check confirms `document.activeElement.id` is `result` in all four runs. Limit: T5 to T7 are text checks on the script (no JS runtime in the suite), so the browser record is the behavioural proof. No-JavaScript focus was not tested (the pane cannot turn JavaScript off); it is browser behaviour unchanged from main (tech spec risk 4) |
| 6 | Accessibility | PASS | axe-core 4.10.2 (pinned in the scratchpad, never in the repo; QA confirms `pyproject.toml`, `uv.lock`, `Dockerfile` unchanged), tags wcag2a, wcag2aa, wcag21aa, wcag22aa: 0 violations of any impact on home, answer (server and after swap), refusal, resting. Keyboard-only flow works, no trap, 3 px focus outline. Reading order equals DOM equals visual order (no CSS `order`). No sideways scroll at 375 px on the swapped answer and refusal. Not covered: screen reader, dark scheme, hover, receipts drawer and copy-link by keyboard, no-JS flow |
| 7 | No open P0 or P1 at the gate | PASS | `code-review.md` 0 Important; QA no P0 to P2, three P3 (`13-qa-evidence.md` s6); Security no P0 to P2, three P3. P2 and below list: none at P2; the P3s and two Nits go in `END_REVIEW.md` |
| 8 | Tests: no failure, at least 731 plus the new ones; new tests fail first; mypy and ruff clean | **PASS, with one literal-reading miss recorded** | 738 = 731 + 7, 0 failed; mypy 54 files clean; ruff clean; both C1.7 reds green. Fail-first: order (T1), focus (T5), script (T6, T7) fail on 6ab5548; the home-unchanged test (T2) and strings test (T3) fail first through their order assertions only. **T4 passes on main by design** and so do the pin halves of T2 and T3: a test that pins unchanged behaviour cannot fail on the code it pins. My reading, which the tech spec (open item 1) asked the Orchestrator to confirm: the bar cannot be met literally for a pin, and it is met in intent, because QA's mutation table lists 12 mutations each killed by at least one test, plus 2 survivors (M2, M11) it judged behaviourally equivalent to show the pins are not vacuous. I grade it PASS. If the owner reads the bar as literal, this is a miss they decide in `END_REVIEW.md`; it is not a risk to visitors |
| 9 | Nothing else moves: INV-1 to INV-5, kill switch, 500-char and ten-an-hour limits, daily cap | PASS | `pipeline.py`, `limits.py`, `settings.py`, `app.py`, `result_store.py`, `abuse_log.py` not in the diff (`13-qa-evidence.md` s2; `14-security-review.md`); the passing suite includes their tests |

## 5. Approvals: needed versus held

| Action | Rule | Charter line | Held? | Record |
|---|---|---|---|---|
| Charter itself (all lines below) | Process v2 | all | HELD | `APPROVAL_RECORD-1.md`, Gopal Patwa, 2026-10-27T06:13Z, sha256 `8eacc407...99bc`; the `charter-check-output.txt` hash matches |
| `az acr build -r acravetoaskgp` one new image | 3 | C8.3 | HELD (Charter); row due when it runs | `STATE.md` Approvals has one row for the Charter only; each action adds its own row citing `CHARTER.md#C8.3` and the sha256 |
| Deploy 1: `az deployment group create -g rg-aveto-ask`, new image tag, `deployApp=true`, `killSwitch=off` set explicitly, price and cap values at their existing defaults | 3 | C8.3 | HELD (Charter); row due | as above |
| Deploy 2: rollback rehearsal, `imageTag=ffc2e2e5f39a` | 3 | C8.3 | HELD (Charter); row due | as above |
| Deploy 3: roll forward to the new image tag | 3 | C8.3 | HELD (Charter); row due | as above |
| Same command with `killSwitch=on`, only if C8.1 requires | 3 | C8.3 | HELD (Charter), conditional on C8.1 | as above |
| Live questions: at most 2, one answered, one refused, from spent eval sets, through the real limits | 5 | C3.1, C8.5 | HELD (Charter) | as above. No question has been sent to the live service yet |
| Push `claude/objective-kapitsa-83d3ae` and open a pull request into `main` | 1 to 3 (shared state) | C8.2 | HELD (Charter); not yet used. Never merge | as above |
| The two C1.7 fixes | 4-adjacent (a test pin, a script import order) | C1.7 | HELD, named in the approval words | `APPROVAL_RECORD-1.md`; done in `a9c0bf0` |
| Any other deploy, resource change or deletion | 2, 3 | none | **NOT held. Stops the run** (Charter section 9 item 1) | |

No gated action has been taken yet (no push, no build, no deploy, no live question; the local browser runs used a stand-in judge). The Approvals table must gain one row per action above at the time it runs, each citing `CHARTER.md#C<n>.<m>` and the sha256. A model in an unnamed role, a fourth deploy, or a changed string is outside the Charter.

## 6. Rollback plan and the rehearsal gate

**Plan, lifted from the tech spec and confirmed against the diff** (code-only, stateless; no data, schema, setting or file format changes):

1. Before merge: close the pull request; `main` is untouched.
2. After deploy: deploy `infra/main.bicep` with the previous `imageTag=ffc2e2e5f39a` (`killSwitch=off` explicitly) per `docs/runbooks/public-ask.md` s2. Because `activeRevisionsMode` is `'Single'` (`infra/main.bicep:154`), this starts a **new revision of the previous image**; it does not re-activate `ca-aveto-ask--0000011`. Charter C8.3 says the same. The tech spec's phrase "activate the previous revision `ca-aveto-ask--0000011`" is looser than the Bicep behaviour; the Charter and runbook govern.
3. Emergency stop: the same command with `killSwitch=on` (about 65 s measured on an earlier release, `17-deploy/e3-rollback.txt` as cited by the runbook).
4. In the repo: `git revert` of the merge commit restores the four product files; remove `tests/test_result_first.py` and its goldens with it.
5. `Cache-Control: no-store` on every response (headers unchanged), so a rolled-back revision serves the old script at once.
Confirmed against the actual diff: the changed product files are the four in `aveto_service/`; `infra/`, `Dockerfile`, `pyproject.toml`, `uv.lock` are untouched, so the rollback needs no data or infrastructure step.

### Rollback rehearsal: OPEN-REQUIRED-AFTER-DEPLOY (a release gate; Charter C7.2, C8.1, C8.3)

It cannot be proven before the deploy. The release is **not passed** until every item below is recorded in `runs/result-page-clarity/` by stage 10. Any miss is a failed release under C8.1.

| # | Pass criterion (from C8.1 and C8.3) | Status |
|---|---|---|
| R1 | After deploy 1, the new image tag is the active revision's image (`az containerapp show`), `/health` answers 200 `status: ok` with `kill_switch: "off"` | OPEN |
| R2 | **Live heading position**, C1.4 item 1 on the live revision: result heading top within the top 25% of the viewport at **1280x800 (0 to 200 px)** and **375x667 (0 to 166.75 px)**, for one answered and one refused question. Record next to the 616 px of the intent and the local 16.1 / 15.6 px. Not measured means not stated anywhere | OPEN |
| R3 | Live checks of C8.1: an answer or refusal not different from the previous page's; no question text in a log table (Log Analytics read); the kill switch takes (a measured switch-on, then back off, within C8.3's one allowed `killSwitch=on` run if used) | OPEN |
| R4 | Deploy 2 (`imageTag=ffc2e2e5f39a`): the **previous image serves**: the active revision's image is `aveto-ask:ffc2e2e5f39a` and the previous page is what is served (my reading of "previous page": `GET /` and a result page show the old order, "What to expect" above the question box, and the heading is not at the top as in the intent's 616 of 800 px). A page that does not serve fails the release | OPEN |
| R5 | `/health` answers on the previous image (200, `status: ok`) | OPEN |
| R6 | **Timed**: seconds from the deploy-2 command to a healthy `/health` on the previous image, recorded. The Charter sets no threshold; the earlier release measured 65 s and 66 s (+ about 6 s traffic) for a revision change. The figure is recorded, not graded; a number not measured is not stated in README, runbook or status | OPEN |
| R7 | Deploy 3 (roll forward to the new tag, `killSwitch=off`): the **new revision is restored** (new image tag active, `/health` ok, live heading again within the top 25% at both sizes). "The roll forward does not restore the new revision" fails the release | OPEN |
| R8 | On a failed R1 to R7 or any R2/R3 miss: C8.1 action: keep or restore the previous revision serving (deploy of `ffc2e2e5f39a`, or `killSwitch=on` if that fails), report, stop | n/a unless triggered |

Points for the Orchestrator at stage 10, inside the Charter. Each is a stop if it cannot be done within the line (section 9 item 1):

1. **Question budget (C3.1: at most 2 live questions).** R2 needs the heading at two sizes for an answered and a refused question (four submissions); R3's "different from the previous page's" would need the same questions on both revisions. Two questions do not cover that. Options inside the Charter: ask the two questions once and re-open the stored result URL (`GET /result/<token>`, which makes no model call, and which `08-browser-checks.md` shows measured at 18.1 / 16.1 px server-rendered) at the second viewport size; and take the comparison with the previous page from the recorded live outcomes of the earlier release. If that does not satisfy the owner's bar, ask; do not send more than two.
2. **Three deploys at most (C8.3).** A failure in deploy 2 (the previous image does not come up) would need a restoring deploy of `ffc2e2e5f39a`, which is a fourth. C8.3 allows `killSwitch=on` as the extra run; any other extra deploy is outside the Charter.
3. **Image provenance.** The runbook tags the image `git rev-parse --short=12 HEAD`. Commit the run records first (this file included) so the tag names a tree whose product files are the tested ones, and run the build from the worktree root, never the main checkout (runbook s1, Security S-C3).
4. **Pre-deploy dry run:** `az bicep build` and `az deployment group what-if -g rg-aveto-ask` with the literal values, saved; the C6.P rules allow both.
5. **Docs follow the record.** `README.md`, the runbook and `.agentic/CURRENT_MVP_STATUS.md` now say "not deployed" and "NOT YET MEASURED live". After stage 10 they must be updated from the record only (revision, timing, live figures), or left as written if a figure was not measured.

## 7. Charter misses and notes recorded for `END_REVIEW.md`

| # | Item | Class | Effect on the verdict |
|---|---|---|---|
| M1 | **Model.** C3.3 names `claude-sonnet-5-5` for the Software Architect; it ran on `opus-5-5` (usage.mjs, `STATE.md` trace row 1). A model not named in C3 is a Charter section 9 item 1 case in the letter; the agent file default caused it and the later spawns pass a `sonnet` override. The Architect produced a document only; no code, deploy or external effect, and Anthropic is already the approved processor | Charter miss | Recorded, not retroactively fixable. Not a C1.4 bar and not a C8.1 failure condition, so not a deploy blocker; the owner accepts or rejects it at the end review |
| M2 | **Models of stages 3 to 7 UNCONFIRMED.** `STATE.md` Trace has rows for stages 1 and 2 only. I looked in `STATE.md`, `events-verify-output.txt` (no model field) and the stage artefacts; none records the model or effort of the QA, Security, Tech Writer spawns. The Orchestrator states a `sonnet` override was passed. The Orchestrator should add the usage.mjs rows | Telemetry gap | None on the product; fix in `trace.json` |
| M3 | **Stage 1 spend 79k against a 40k estimate** (and stage 2: 69k against 50k) | Budget | `STATE.md`: spent 323k of the 400k plan, 77k remaining; stage 8 estimate 40k fits (363k). Remaining stages 8 to 11 estimate 150k, projection about 473k, above the plan total, below the 720k ceiling and the 800k hard cap. No notice due (C2.3). The spend is the Orchestrator's self-reported figure; I did not recompute it |
| M4 | **Tests that pin "unchanged" cannot fail first** (T4; the pin halves of T2 and T3) | Charter reading | Section 4 item 8; mutation record in `13-qa-evidence.md` s4 |
| M5 | Two Nits accepted unfixed: R1-1 (`resultFirst` selects the blocks by `nextElementSibling` twice from the `h1`; a template edit that adds an element after the title would move the wrong blocks) and R1-2 (the load-time `land()` overrides browser scroll restore on reload of `/result/<token>#result`) | Code review | List in `END_REVIEW.md` with the reason |
| M6 | Security P3-1 (first client read of the URL fragment, a strict compare to a literal), P3-2 (the pin proves file equals installed v30, not that v30's hook is what the owner intended), P3-3 (README uncommitted at review time) | Advisory | **P3-3 closed by me:** the README "Result first" paragraph, the runbook section and the status entry contain no new claim about privacy or limits; they state a reordering, "no wording changes", and point to `13-qa-evidence.md`; every figure traces to `08-browser-checks.md` or `13-qa-evidence.md`; live values are marked NOT YET MEASURED. README is committed (`git status` clean for it) |
| M7 | `docs/ARCHITECTURE.md` page row is in the diff (QA P3-3). C1.3 does not bar it, the slice plan listed README, runbook and status as the docs files | Scope note | Not a blocker; recorded so the owner sees it was intentional |
| M8 | Axe version for `END_REVIEW.md` (C1.5): axe-core 4.10.2, scratchpad only | Record | |
| M9 | The `.claude/settings.local.json` C6.P file (main checkout) is deleted after the pull request opens | Stage 11 | Due at stage 11 |
| M10 | Prompts and permission questions answered by the owner after the Charter: the record I can see shows none (`APPROVAL_RECORD-1.md` is the only record); `END_REVIEW.md` counts them (target 0). UNCONFIRMED for guard prompts, which are not in the files I read | Count | Orchestrator reports it |

## 8. Post-launch monitoring (Tier 3)

The service's standing plan is `docs/runbooks/public-ask.md` section 12 (source: `runs/public-ask-the-docs/06-ai-risk-assessment.md` section 7; "No threshold here is new"). Nobody is on call and nothing pushes an alert; the owner acts. For this slice the additions are small because no logging, limit or model path changed.

- **Signal 1 (this slice):** the result heading's top on the live page, at 1280x800 and 375x667, after one answered and one refused question. **Threshold:** outside 0 to 25% of the viewport at either size, on any re-check, is a regression. **Action:** roll back per section 6; kill switch on if the page is unusable. **When:** at deploy (R2), then once after the first live day and once in the first week by the owner.
- **Signal 2:** `GET /health` after each revision change: 200, `status: ok`, `kill_switch: "off"`. Failure: kill switch on, then rollback.
- **Signal 3:** `judge_error` share, token use per question, `answer` share, `rate_limited` per ip hash, `paused` days: unchanged thresholds from runbook s12. A move in `answer` share by more than 20 points over 100 or more calls is not expected from this slice (the answering path is untouched) and would point elsewhere.
- **Signal 4:** no question text in any log table (Log Analytics) at deploy (R3) and at the next 7-day read-back (runbook s6).
- **Cadence:** daily for the first 3 live days, then at least every 5 days (runbook s12).
- **Known gaps:** no push alerting (runbook M1); no screen reader, no-JavaScript or dark-scheme measurement for this change (`08-browser-checks.md` "Not measured").
- **Owner:** the repository owner acts; the Post-Launch Learning Agent reads this record, the stage 10 record and `END_REVIEW.md`.

## 9. Decision

- [x] **Go to deploy.** All pre-deploy gates pass; deploy allowed under Charter C8.3 as listed in section 5. The slice does **not** land and the push and pull request (C8.2) do **not** start until the rollback rehearsal (R1 to R7) and the live heading position (R2) are recorded as passed.
- [ ] No-go.

No FAIL. Pre-deploy OPEN items: none. OPEN-REQUIRED-AFTER-DEPLOY: R1 to R7 (the rollback rehearsal, the live heading position at both sizes, the C8.1 live checks, timing). Recorded misses for the owner: M1 (model), M3 (spend), M4 (pins). Unconfirmed by me, with where I looked: C1.1 and C1.2 hashes (no shell), the git range `d223e11..HEAD` (no shell; mtime and content reads only), `git diff --check` (grep only), models of stages 3 to 7 (STATE trace, events summary, artefacts).

## Hand off

If the rehearsal and live checks pass: the Orchestrator takes C8.2 (push, pull request, never merge), `END_REVIEW.md`, then the Post-Launch Learning Agent.
If any of R1 to R7 fails: C8.1 applies; the previous revision keeps or regains serving, the run reports and stops, and the release fails. This verdict does not carry over to a changed tree, a changed Charter hash, or a changed image tag.
