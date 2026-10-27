# Release Checklist - polished-chat-experience

> Owner: Release Manager Agent (stage 11, `claude-sonnet-5-5`, standard). Date: 2026-10-26. Tier: **3**.
> No shell: every "pass" below is read from a record, not re-run by me. Source artefacts: `intent.md`, `CHARTER.md`, `00-slice-plan.md`, `01-scope.md`, `05-tech-spec.md` (section 12 deploy sheet), `13-qa-evidence.md`, `14-security-review.md`, `code-review.md`, `08-browser-checks.md`, `10-test-count.txt`, `10-figures.md`, `15-docs-note.md`, `DECISIONS.md`, `APPROVAL_RECORD-1.md`, `charter-check-output.txt`, `events-verify-output.txt`, `EVENTS.jsonl`, `13-live/live.py`, `aveto_service/scorecard.toml`.

## Verdict: GO WITH CONDITIONS

No gate failed and no P0 or P1 is open. The deploy may start only when the five **pre-deploy preconditions** (section 4) are done and their output saved in the run folder; if one fails, that is a failed check before the deploy (C8.1: no deploy, `ca-aveto-ask--0000008` keeps serving, close-out, stop). The post-deploy items (section 5) are not release blockers now; each is listed with its C8.1 consequence.

## 1. Tier classification

Tier 3, and I agree with the recorded Tier 3 and the review tier High. Re-derived from the change set (QA section 3: 22 paths; tech spec 14.0): the slice adds three public routes (`POST /warm`, `POST /count/docs-click`, `GET /scorecard`), edits `app.py` and `pipeline.py` (the spend-limited ask path, add-only), `pages.py`, `render.py`, `enhance.js` on a public page; the run itself deploys to a public Azure service, and C5.0 names the headers and invariants that must not move. Deploy plus public surface is Tier 3 under `RELEASE_GATES.md`; `CODE_REVIEW.md` section 2 gives High (a Charter C5.x line is named; the rollback is rehearsed before the change is offered). No higher tier exists. Nothing in the diff is a safety-text, processor, model or header change.

## 2. Charter, approvals, event log, review layer

| Check | Result | Evidence |
|---|---|---|
| `charter-check` says complete, hash = approved hash | PASS | `charter-check-output.txt`: "charter complete", sha256 `a24c3c56e430aed399ea88d4adaee8838694e5fd1950c776c5c49a1564b10312`; same string in `APPROVAL_RECORD-1.md` and STATE |
| Approval is the human's own, by hash, in the driving session | PASS | `APPROVAL_RECORD-1.md`: Gopal Patwa, verbatim sentence naming the file, hash and budget; recorded 2026-10-26T20:08:31Z |
| Every approval used is recorded | PASS for now | STATE Approvals: one row (Charter). No gated action has run yet (only read-only `az`). Each gated action needs its own row citing `CHARTER.md#C<n>.<m>` and the sha256 when it runs: `az acr build` and deployments (1) (2) (3), C8.3; the seven live questions, C3.1 and C8.5 (limit 8); push and pull request, C8.2; a `killSwitch=on` deployment only if C8.1 requires it. Nothing else is covered: no merge, no deletion, no fourth deployment other than the kill-switch case |
| Event log | PASS | `events-verify-output.txt`: "chain intact; 1043 lines". The one alert (seq 1043, `main` Bash with no outcome) is the verifier's own in-flight call. I also searched `EVENTS.jsonl` for Write/Edit targets under `aveto_support/`, `prompts/`, `infra/`, `.claude/`, `Dockerfile`, `pyproject`, `uv.lock`, `.agentic/{SAFETY_INVARIANTS,PROJECT_CONTEXT,LOCAL_COMMANDS}`: none. The log must be re-verified at close-out (stages 11 to 14 add events) |
| No C6.P allow rule in a tracked settings file | PASS (by my read) | the worktree `.claude/settings.json` holds none of `Agent(`, `az acr`, `az deployment`, `git push`, `gh pr`, `uv run`; the rules are only in the gitignored `settings.local.json`. The saved `git diff 32e54a6 -- .claude/settings.json` output is not in the run folder: see P1 |
| `code-review.md` | PASS | F1 intentional with a correction (Security S1), F2 Important fixed `f5c139c` and re-reviewed, F3 to F5 intentional with reason, F6 F7 cleanup-only rejected; 0 open. Note: the Q1/Q2 script fix (`6c32de1`) came after round 2 and was read by Security, not by the review layer |

## 3. Gates

### Implementation
- [x] Typecheck: mypy "no issues found in 53 source files" (`10-test-count.txt`)
- [x] Targeted tests: QA rows 7 to 9 (byte-equality 3, tech-spec bar 8 169, new files 87 x3)
- [x] Full suite: **731 passed**, 0 failed, 12 deselected on the final tree (`10-test-count.txt`; 730 at QA plus the Q1 test added in `07-fix-Q1Q2.md`); ruff clean
- [ ] Build: **NOT YET.** There is no local build; the build is `az acr build` (sheet 12.1, stage 12). Its pass rule includes the ingest hash `f36ef5d4...a756`
- [x] One commit per task: tests-first `cd4d4b1`, checkpoint, one stage 5 commit, `f5c139c`, `6c32de1`, `3be0620`, `8667d80` and following (by the records; I cannot run `git log`)
- [x] `git diff --check`: pass at `622f47e` (QA row 10). Re-run at the gated HEAD: P1

### QA
- [x] UI verified in preview: stage 8, built-in browser, local dev server with a stand-in judge (shows the page, not live model behaviour)
- [x] Local regression command: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, 731 passed
- [x] Safety invariants verified: QA section 8 (INV-1 to INV-5 text sha256 equal to main's, kill switch, 500 chars, 10 an hour, daily cap, privacy wording, 39-case `/ask` golden independently regenerated byte-identical)

### Security
- [x] No secrets in the diff (Security section 4; live outputs are grepped for `sk-ant` before commit, sheet intro)
- [x] No PII or sensitive data logged (Security P6 canary probe; QA section 7)
- [x] Audit events cover state changes (Security section 4: none added, removed or renamed; counts are not audit events)
- [x] Adapter boundary placeholder still throws (`PlaceholderJudgeClient`, Security section 4)

### Tier 3 only
- [x] Human approval per `HUMAN_APPROVAL_RULES.md`: the Charter (section 2). Per-action rows at action time
- [x] Approval recorded: Gopal Patwa, 2026-10-26T20:08:31Z, `APPROVAL_RECORD-1.md`
- [ ] Dry-run on a fixture before live: PASS for the page and the service (offline golden, local dev server). **NOT DONE for `13-live/live.py`**, which is the instrument that decides a C8.1 restore: its header says "WRITTEN, NOT RUN". P4
- [x] Audit event coverage manually verified: Security section 4 (tech spec 7 against the diff)
- [x] Post-launch monitoring plan (section 6)
- n/a Enterprise and governance gates and a CAB change request: no enterprise overlay is enabled for this repo; Compliance, Data Governance, AI Governance, FinOps were skipped on purpose in the plan (no new processor, no new data, no model or prompt change). The Charter is the recorded, hash-approved change authority.
- [x] Docs match shipped behaviour (Tech Writer): README, runbook, status file say nothing about a deploy, health, timings, rollback timing or Codex review. Spot-check of three figures against their records: **731 tests** = `10-test-count.txt` line 5 (also README line 207, status line 173, `scorecard.toml`); **30.8 s cold, 1.66 s median, 5.09 s slowest** = `runs/public-ask-the-docs/18-gate/RESULT.md` lines 25 and 26, labelled "earlier release (revision 0000006)"; **axe-core 4.10.2, zero serious or critical on 5 views** = `08-browser-checks.md`. The stage 10 flag (731 against a record saying 730) is resolved: the row now cites the final-tree record.

### Charter bars C1.4 (fixed; none moved)

| # | Bar | Result | Basis |
|---|---|---|---|
| 1 | Answering byte-identical | PASS (re-run at gated HEAD: P1) | `git diff main --stat` on the named paths empty at `622f47e`; 39-case golden regenerated independently, sha256 `56e4b77b...e281c`; `test_ask_json_bytes_equal_main` passes in the 731 run. Later commits touched README, runbook, status, `scorecard.toml`, `enhance.js`: none on the ask path |
| 2 | Answer card holds only listed text; refusal card no model text | PASS | `test_answer_card_holds_only_text_from_a_listed_passage` and `test_refusal_card_shows_no_model_written_text`; each fails under 2 or 3 mutations (QA section 6) |
| 3 | axe: zero serious/critical on 5 views | PASS (local, stand-in judge) | `08-browser-checks.md`, axe-core 4.10.2 (for `END_REVIEW`). Raw per-view axe JSON was not saved (spec asked for `08-browser/axe-<view>.json`); the record is the summary table and a hand contrast sweep. Contrast of the disabled resting form and hover states not measured by hand |
| 4 | 375 px and keyboard | PASS for what was measured; **one clause unexecuted** | no horizontal scroll on 5 views, no control under 24x24 on 4 views (scorecard: inline links only, not measured), keyboard path to the result, receipts open/close, visible 3 px focus, no trap. "Follow the source link" was reached with focus but **not activated** ("Not tested by hand"). P3 |
| 5 | Timings as measured, no pass figure | PARTIAL, as designed | local: n = 10, median 0.0143 s, slowest 0.0164 s, 2026-10-26T22:48Z, stand-in judge (`08-local/timing.json`); not shown as a response time. Live warm and cold: NOT YET (stage 13). No figure without a measurement is shown; the scorecard's speed rows are labelled earlier-release |
| 6 | No open P0/P1 | PASS | code review 0 open; QA 0 P0/P1, 6 P2; Security 0 P0/P1, 2 P2 |
| 7 | Tests | PASS | 731 passed (at least 668 + new); the four intent tests fail on `32e54a6` first (`04-failfirst-32e54a6.txt`; QA re-ran the branch tests on base: 57 of 62 fail first, the other 5 are guards) and pass now; mypy and ruff clean |
| 8 | Nothing about answering moves | PASS | `pipeline.py` hunk add-only; header sets byte-identical on every route (`/scorecard` carries exactly the `GET /` set); `frame-ancestors 'none'` everywhere; limits files not in the diff; `test_disclosure_block_byte_identical` |

### Skipped gates
None skipped. Not yet applicable: Build (stage 12), live parts of bar 5.

## 4. Pre-deploy preconditions (Orchestrator; output saved under `runs/polished-chat-experience/`; resolve before `az acr build`)

- **P1. Gated-HEAD re-run** (one pass, saved as `16-gate-head-output.txt`): `git status --porcelain` (empty); `git log -1 --format=%h --abbrev=12` (this is `<TAG12>`; commit this checklist, the STATE update and the saved outputs first, then read it; commit nothing after the build); `uv run mypy`, `uv run ruff check`, `uv run pytest` (0 failed, at least 731); `git diff 32e54a6 --stat -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md` (empty); `git diff 32e54a6 -- .claude/settings.json` (empty); `git diff --check 32e54a6 -- . ':(exclude)runs'` (silent). Reason: `scorecard.toml` was edited in `a318d7c` after the 731 run, and Security's condition 2 asked for `tests/test_service_scorecard.py` on the final tree. A bad file is a 503 fixed scorecard on the live service.
- **P2. Clean tree.** The session started with `M runs/fix-service-accounting/STATE.md` uncommitted. It is another slice's file, not in this run's event log, and sheet 12.0 requires "no uncommitted change". The Orchestrator finds out what changed it (`git diff` on that file) and settles it by the owner's route; I did not touch it. A tag built from a dirty tree is not allowed.
- **P3. Bar 4 clause.** On the local dev server, press Enter on a source link with the keyboard alone and record that the URL changes to the passage permalink. A fail is a missed bar (C8.1).
- **P4. Dry-run `live.py` on the fixture.** Run `check new` and `ask --index ... --models ...` against the local dev server (port 8765, stand-in judge) with `SERVICE_URL` pointed at `http://127.0.0.1:8765` by a one-line wrapper, not by editing the file; expect `check new` all true, `ask` seven rows with `behaviour_ok`, no crash. Write outputs to a scratch path. I read `live.py` once: it sends exactly seven questions, never retries a POST, takes no credential, writes ids, codes and times only, and matches sheet 12.3 and 12.4. It has no test of `first_difference` or the two HTML parsers, so a script bug could fake a C8.1 trigger or a pass.
- **P5. Sheet substitution.** Replace `<TAG12>` and `<D1_START_UTC>` with literals; the tag list must not already hold `<TAG12>`; the 12.0 pre-flight must show exactly `ca-aveto-ask--0000008  100  Healthy`, image `d067b9a95ac6`, env `kill switch off`, prices 2000 and 10000, cap 10 (C6.6). Anything else is stop 1, the rollback target is not C6.6's.

## 5. Deploy sheet check (tech spec section 12) and post-deploy conditions

**Literal and within C8.3: yes.** One `az acr build -r acravetoaskgp` from the worktree root; deployments (1) new tag, (2) rehearsal `imageTag=d067b9a95ac6`, (3) roll forward, all `az deployment group create -g rg-aveto-ask` with `deployApp=true killSwitch=off configureLogRetention=true` and `infra/main.parameters.json`; `killSwitch=on` only if C8.1 requires it; `what-if` before each `create`. Every command begins with a C6.P allow prefix. `infra/main.bicep` defaults match the live values (`priceInNanoPerToken` 2000, `priceOutNanoPerToken` 10000, `monthlyCapUsd` 10, `clientKey` `xff_last`) and `infra/` is not in the diff. Failure handling never needs a fourth ordinary deployment: a failure at 12.4 or 12.5 is restored by deployment (2) with no roll forward; a failed (3) leaves (2)'s revision serving. Live questions: 7, under the cap of 8, through the real limits (C8.5). One reading to carry: the sheet treats an over-abstention (an answerable suggestion refused, or R1 answered) as reported-as-measured and not a C8.1 behaviour failure; C8.1's trigger is a result "different from `retrieve`'s", which the sheet checks byte for byte on every `answer`.

Rollback plan (tech spec 13, confirmed against the diff): (1) fastest, kill switch on, about 65 s recorded; (2) previous version, deployment (2) with `imageTag=d067b9a95ac6` into a new revision, rehearsed in this slice; the image tag exists (12.0 checks); (3) code: the run never merges; if merged, revert the merge commit. No data, resource, secret, setting or migration changed (diff has no `infra/`, `Dockerfile`, `pyproject.toml`, `uv.lock`; new state is in memory). Rollback time is measured from the `date -u` before `create` to three consecutive "old serving" polls.

| Post-deploy / owner item | Consequence |
|---|---|
| `check new` (health, kill switch off, skip link, four suggestions, `/scorecard` 200, headers equal the literal, `/warm` ready) | fail: C8.1, deployment (2), `check old`, report, stop |
| Seven live questions: HTTP and outcome valid, every `answer`'s passages byte-equal to local `retrieve` (when the index hash matches) | fail: C8.1 restore and stop. Over-abstention or hash mismatch: reported only |
| Log-table search: abuse rows arrived, then no question text | question words found: C8.1 restore and stop |
| Rollback rehearsal: old page serves, `/health` answers, within 600 s; roll forward restores the new revision | either fails: C8.1, previous revision kept or restored (kill switch on if it cannot be), the release fails |
| Live warm (requests 2 to 7) and cold start | reported as measured; not a failure. They reach the scorecard only by a later change (D7) |
| Kill switch not tested live (code unchanged, offline tests green) | stated plainly in `END_REVIEW.md` |
| Live-browser look (CSP console errors, `DOMParser` swap inert, beacon end to end): Security A3 and section 5 and `08-browser-checks.md` "Not checked here" | not in the sheet; recommended read-only look at stage 13; a finding is reported, and is C8.1 only if it is an answer/refusal or privacy failure |
| Codex review of the pull request | the owner's, after the PR; not a blocker; no scorecard row until the owner records it |
| Scorecard and drawer links point at commit `8667d80`, which exists only locally until the push (C8.2) | between deploy and push they 404 (D13); stated to the owner |

## 6. Post-launch monitoring (Tier 3)

- Signals: `/health` (200, `kill_switch` off) and revision health; `/scorecard` counts (raw, unauthenticated, since last restart: S2); the abuse-line rows and spend share against the day's $0.3226 and the $10 console limit; Log Analytics for any question text (the 12.5 queries).
- Thresholds for concern: any question text in a log table, any answer not equal to `retrieve`'s, `/health` not 200, or a refused suggestion shown with a wrong label: kill switch on or deployment (2) (owner's call after the run).
- Owner: Post-Launch Learning Agent for the run record; the owner for anything after the run.

## 7. Carry to `END_REVIEW.md` (nothing here is dropped)

- Security **S1** (result store bound: F1's wording corrected; zero-spend `JUDGE_ERROR`, same on `main`) and **S2** (counts raw, inflatable, since restart), per D12; **A1 to A4** as notes.
- QA P2 **Q1 to Q6** with their dispositions (Q1 and Q2 fixed `6c32de1`; Q3 reworded; Q4 accepted; Q5 open until the live check; Q6 browser-only coverage). All P2 are listed (bar 6). The scorecard row "two at P2" is the Security count and its basis says so; the full P2 list is longer.
- **D13**: links ship, pinned to `8667d80`, 404 until the push; the pull request, end review, event-log summary, cost and time and owner-decisions links are not shipped, so "the build is shown" is partly met on day one. **D5**: "about 26 seconds" has no record. **D1**: the refusal card shows no passages (Option B is the owner's later choice). **D2, D3, D6, D7**: drawer without the signal line; "docs search" read as the docs link; data strings listed for the owner; no live timing on the scorecard on day one.
- The copy deck, including the Q1/Q2 strings in `07-fix-Q1Q2.md` and the unconfirmed "It can take up to a minute" line (Q2) status after the fix, for the owner's read (C1.6). The 375 px first screen is filled by the approved "What to expect" list (owner's call).
- Axe version 4.10.2; first-use prompts on the gated commands (C6.P); the debt noted in `15-docs-note.md` (runbook sections 5, 7, 8 describe the earlier release).
- High tier: the owner reads the change itself, and the rehearsal result is stated before the pull request is offered.

## 8. Decision

- [x] **Go with conditions**: the slice may be built and deployed once P1 to P5 are recorded; the post-deploy items run under C8.1 as listed.
- [ ] No-go.

## Hand off

To the Orchestrator for P1 to P5, then stage 12 (Cloud Deployment). If any precondition fails: no deploy, `ca-aveto-ask--0000008` keeps serving, close-out, stop (C8.1). After the slice lands and produces a signal: Post-Launch Learning Agent.
