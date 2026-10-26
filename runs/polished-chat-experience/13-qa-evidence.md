# QA Evidence - polished-chat-experience (stage 7, offline)

> Owner: QA Evidence Agent. Depth: standard. Date: 2026-10-26. Tree: branch `claude/interesting-shannon-67bff6` at `622f47e` (build commits through `f5c139c` plus run records); base `main` = `32e54a6` (`git rev-parse main` still prints 32e54a6, merge-base 32e54a6, `HEAD...main` = `11 0`). Tools: Read, Write, Edit, Bash, Grep, Glob; no browser, no network, no live call, no product file edited. Scratch work only under the scratchpad `.../1dbb5af3-2658-4b6f-ab7a-5c8d7e249de5/scratchpad/` (`base/`, `mut/`, `mutate.py`, `hdr_probe.py`, `canary_probe.py`).

## Verdict: GO WITH CONDITIONS (pass to Security)

No P0 and no P1 finding. Six P2 findings (section 9). Conditions: (1) everything the Charter gives to stage 8 and later (axe, 375 px, keyboard, timings, live behaviour, rollback) is **not verifiable** here and stays open; (2) per D8, the Orchestrator re-runs the full suite and the C1.4.1 and C1.4.7 commands on the final tree after the figures fill and the docs stage, because this evidence is for the tree above, not for those later edits.

## 1. Commands run, in order (each run alone, no `&&` chain)

| # | Command | Result | Tail |
|---|---|---|---|
| 1 | `uv sync --locked` | pass | `Resolved 39 packages ... Audited 36 packages` |
| 2 | `uv run mypy` | pass | `Success: no issues found in 53 source files` |
| 3 | `uv run ruff check` | pass | `All checks passed!` |
| 4 | `uv run pytest` | **pass** | `730 passed, 12 deselected in 16.28s` (0 failed; Charter C1.4.7 needs 668 + new; 668 + 62 new items = 730) |
| 5 | `git diff main --stat -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md` | pass | empty (0 lines) |
| 6 | same with `32e54a6` and the whole of `.agentic`; `git status --porcelain -- aveto_support prompts .claude .agentic` | pass | all empty |
| 7 | `uv run pytest tests/test_service_ask_bytes.py -v` | pass | 3 passed (`test_ask_json_bytes_equal_main`, `test_security_and_json_header_sets_are_byte_identical`, `test_new_routes_carry_existing_header_sets`) |
| 8 | `uv run pytest tests/test_service_pipeline.py::test_core_files_unchanged tests/test_service_pages.py tests/test_service_limits.py tests/test_service_logging.py tests/test_service_api.py` (tech spec bar 8) | pass | 169 passed |
| 9 | the 7 new/changed test files, three consecutive runs | pass | `87 passed` x3 (no flake) |
| 10 | `git diff --check 32e54a6 -- . ':(exclude)runs'` | pass | no output (the only whitespace complaints are in captured pytest output files under `runs/`) |
| 11 | `node .../charter-check.mjs runs/polished-chat-experience/CHARTER.md` | pass | `charter complete`, sha256 `a24c3c56...0312` = the approval record; `intent.md` sha256 `368bc3e4...e89a` = C1.1 |

## 2. C1.4.1 byte-equality, golden provenance re-derived independently

- `git log --diff-filter=A -- tests/golden/ask-json-32e54a6.json` gives `cd4d4b1`; `git diff --exit-code 32e54a6 cd4d4b1 -- aveto_service aveto_support prompts` is empty (the golden was written at a tree identical to base in those paths).
- Independent regeneration (no `git worktree`): `git archive main aveto_service aveto_support prompts tests/service_fakes.py tests/conftest.py evals pyproject.toml` into `scratchpad/base/` (no `counts.py`, `scorecard.py`: it is the base code), the branch's generator `tests/test_service_ask_bytes.py --write-golden` run there with the venv python, imports confirmed to resolve inside `scratchpad/base`. Output: `wrote ... with 39 cases`. `cmp` against the committed golden: **byte-identical**; both sha256 `56e4b77bc53c7e207c046141092d461f8ecfec061f6ca22e171260d0a05e281c`.
- Coverage of the golden: 12 spent-set questions x (answer, refusal) = 24, plus 8 malformed shapes, 2 judge-error cases, rate-limited 11th, paused, service-off, cross-site, plus `/health` = 39 (the spec said 36; D10 accepts 39). The test also asserts ids are complete and both outcomes occurred for every question.

## 3. Change set (tech spec 14.0)

`git diff --name-only 32e54a6 -- . ':(exclude)runs'` prints 22 paths, all inside the expected set: `aveto_service/{app,counts,pages,pipeline,render,scorecard}.py`, `scorecard.toml`, `suggestions.toml`, `static/enhance.js`, `static/style.css`, `docs/ARCHITECTURE.md`, `docs/adr/0010, 0011, 0012`, `tests/golden/ask-json-32e54a6.json`, `tests/test_page_cards.py`, `test_service_{ask_bytes,counts,new_routes,pages,scorecard,suggestions}.py`. No path outside the set (none of `aveto_support/`, `prompts/`, `.claude/`, `infra/`, `Dockerfile`, `pyproject.toml`, `uv.lock`, `limits.py`, `settings.py`, `abuse_log.py`, `tests/service_fakes.py`). Not yet changed, as expected for a later stage: `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md`.

## 4. Response headers (D): byte-identical to main

- `git diff main -- aveto_service/pages.py` shows no hunk inside `SECURITY_HEADERS` (the dict is not in any hunk; `STATIC_TYPES` and `Response(..., headers=dict(SECURITY_HEADERS))` unchanged).
- Own probe, run against the base tree (`scratchpad/base`) and against the branch, same fake runtime: header names and values for `GET /`, `POST /ask` (form 303 and a 400), `GET /result/<token>`, `GET /result/nope`, `GET /static/style.css`, `GET /static/enhance.js`, `POST /ask` JSON, `GET /health`. `diff` of the two dumps: the only differences are the random result token in `Location` and `GET /scorecard` (404 on base; on the branch 200 with exactly the `GET /` set: cache-control, CSP with `frame-ancestors 'none'`, referrer-policy, nosniff, text/html). Every other route: identical.
- `frame-ancestors 'none'` is in every HTML response. Result: pass.

## 5. Intent verification (Done means, verbatim)

| # | Done means (verbatim) | Result | Evidence |
|---|---|---|---|
| 1 | Starts from `main` with pack v29 installed (first use of v29 in a run; the Charter check passes for every role in the plan). | pass | merge-base = 32e54a6; `.claude/agentic.config.json` `packVersion` 29; `charter-check` prints `charter complete`, hash equals APPROVAL_RECORD-1. |
| 2 | **Quality bars, fixed before the build and not moved** (the Architect proposes the figures; the owner confirms them in the Charter): warm response time and cold-start time reported as measured; the page passes an automated accessibility check with no serious issue and works at 375 px wide and by keyboard alone; no open P0 or P1 finding; the answering behaviour is byte-identical. | **partly pass; rest not verifiable here** | Byte-identical: pass (sections 2, 4). No open P0 or P1: pass for `code-review.md` (F2 Important fixed in `f5c139c`, re-reviewed) and for this QA; the Security Review is still to come. Warm and cold timings: not verifiable (stage 8 local, stage 13 live; nothing measured yet). Accessibility, 375 px, keyboard: not verifiable (needs the browser; stage 8). |
| 3 | **Nothing about answering moves.** `git diff main -- aveto_support prompts .claude .agentic` is empty except the pack install; retrieval, the judge prompt, the corpus, the verbatim-only rule, INV-1 to INV-5 and the kill switch are unchanged. A test proves the answer card contains only text that appears in a listed source. If a safety-text change is needed, the run stops and says so. | pass | the diff (whole `.agentic` too) is empty, `SAFETY_INVARIANTS.md` sha256 `c4eac0e0...cc27` equals main's; `pipeline.py` hunk is add-only (0 removed lines: `WARM_QUESTION`, `_search_once`, `_warm_lock`, `_warm_result`, `resting()`, `warm()`); `test_core_files_unchanged` passes; `test_answer_card_holds_only_text_from_a_listed_passage` passes and bites (section 6). |
| 4 | **Embedding decision, stated by the Architect with the reason.** The page is served with `frame-ancestors 'none'` today (`aveto_service/pages.py`). Options: (a) keep the service on its own address and show it on aveto.dev as a recording plus a button; (b) allow framing by `https://aveto.dev` only. (b) changes a security header, so it is a Charter C5 safety-control item, needs the Security Review to cover it, and must name that one origin and no wildcard. **Decided by the owner: (a).** The `frame-ancestors 'none'` header does not change in this slice; an embedded panel (b) is a separate later intent if ever wanted. | pass | header unchanged on every route (section 4); `docs/adr/0012-service-not-framed-aveto-dev-links-to-it.md` exists; tech spec section 1 restates (a). |
| 5 | **Tests that fail first** for: the refusal card shows no model-written text; the resting state at the cap; the counts record no question text; the receipts drawer shows nothing the service did not already hold. | pass | section 6: all four fail on the base code for the stated reason and pass on the tree; each fails under a small mutation. |
| 6 | **Code review layer** (tier High: the service handles spend limits and a public page) and a **Security Review at standard depth**. **Release Gate at tier 3** because the run deploys. The Codex review (manual, blind, new chat) is run by the owner on the pull request and recorded as a trial review. | partly pass | code review: done (`code-review.md`, 2 rounds, 0 open). Security Review, Release Gate, Codex trial review: not verifiable yet (later stages / the owner). |
| 7 | **Deployed** by the run under the Charter's C8.3 (new revision only). **Rollback is a gate, decided by the owner 2026-10-26 (option 3):** after the deploy the run rolls back to the previous revision, checks that the previous page serves and `/health` answers, times it, then rolls forward again and checks the new revision. If the rehearsal fails, the release fails: the run keeps the previous revision serving, reports, and stops. The timing is reported as measured. | not verifiable | stages 12 and 13. `13-live/live.py` was only written; QA did not run it (live, credentials). |
| 8 | **The build is shown.** The pull request, the Charter, the event-log summary, the end review, cost and time, and what the owner decided are linked from the scorecard page. The aveto.dev change (a short section and the link) is a separate playbook commit with wording the owner approves first, and the site deploy approved in GitHub's production environment. | not verifiable | no `[links]` in `scorecard.toml` yet (D9); a later stage. The scorecard's reader fails closed to no links; tested. |
| 9 | README, `docs/runbooks/public-ask.md` and `.agentic/CURRENT_MVP_STATUS.md` state only recorded figures. | not verifiable | not yet edited (stage 10). Re-check after it. |

"Must not break" (INV-1 to INV-5; the service never shows generated text; no question stored or logged; kill switch; 500-character and ten-an-hour limits; daily cap; privacy wording): pass, see sections 7 and 8.

## 6. Fail-first and non-vacuity (Charter C1.4.7; test acceptance)

**Tests added: 62 items** (7 `test_page_cards`, 3 `ask_bytes`, 2 `counts`, 6 `new_routes`, 34 `scorecard`, 2 `suggestions`, 8 in `test_service_pages`). **Confirmed failing first on the base: 57.** I ran the branch's tests against the base product code in `scratchpad/base` (full `tests/` there): 22 failed, 29 passed, 2 collection errors (the modules `test_service_scorecard.py` and `test_service_suggestions.py`, 36 items, import `aveto_service.scorecard` or `SUGGESTIONS_PATH`, which the base lacks). 22 failures = 21 new + 1 existing test whose assertion was edited (`test_initial_page_has_empty_region_and_form`). The other 5 new items pass on base by design (guards, stated in their docstrings): `test_ask_json_bytes_equal_main`, `test_security_and_json_header_sets_are_byte_identical`, `test_disclosure_block_byte_identical`, `test_answer_page_names_its_region_by_the_heading_it_holds`, `test_script_tag_and_head_are_unchanged_by_the_new_blocks`. They prove nothing moved, not that something was added, and are not counted as proving the change.

**Generated tests kept: 62; removed: 0.** Each builds, passed three consecutive runs (87 passed x3 in the touched files), and maps to a Done-means line or a tech-spec bar (T-* ids in `05-tech-spec.md` section 10). No coverage tool in the project, so the Done-means link is the qualifier.

| Intent test | Test | Fails on base, reason | Mutation in a scratch copy (`scratchpad/mut`, pristine control passed first) | Mutated result |
|---|---|---|---|---|
| refusal card, no model text | `test_page_cards.py::test_refusal_card_shows_no_model_written_text` | `assert {...} <= {...}`: no suggestions, drawer or F1 on base | R1 show `result.signal` in the refusal; R2 same plus a fake pre block; R3 constant `<pre class="passage">nearest passage text</pre>` on a refusal | all 3 fail (R3: `['nearest passage text'] == []`) |
| resting at the cap | `::test_resting_state_at_the_cap` | `'Paused for today' in page` false on base | C1 `GET /` ignores `resting()`; C2 `resting()` ignores the closed-day flag (part b); C3 page load calls `service.warm()` (embedder call) | all 3 fail |
| counts, no question text | `test_service_counts.py::test_counts_record_no_question_text` | `404 != 204` on `/count/docs-click`; `AttributeError ... counts` | K1 a new slot holds the question; K2 `counts._started_at = raw` (question text reaches the snapshot) | both fail (slot-set equality; `CANARY not in repr(snap)`) |
| receipts drawer, only service-held data | `::test_receipts_drawer_shows_only_what_the_service_held` | `assert 0 == 1` (no drawer on base) | D1 add "Deciding signal" row; D2 drawer also on a judge error; D3 add "(judge verdict)" to the outcome | all 3 fail |
| answer card text is in a listed source (C1.4.2) | `::test_answer_card_holds_only_text_from_a_listed_passage` | listed-set assertion fails on base (no chip, caption, drawer) | A1 append text to the quoted passage; A2 add `result.signal` under the card | both fail |

After every mutation the file was restored from the worktree and `diff -rq` of `aveto_service aveto_support prompts tests` between the worktree and `scratchpad/mut` printed nothing; `git status` in the worktree stayed clean. The original fail-first record on commit 1 (`04-failfirst-32e54a6.txt`: 15 failed, 3 passed, 1 collection error) and `05-failfirst-base.txt` agree with this run.

## 7. No question text in counts or logs (F)

- Static: `git diff 32e54a6 -- aveto_service` added lines contain no `emit_`, `logging`, `print(`, file open or write. `UsageCounts` methods take an `Outcome` or nothing (`counts.py`); `record(result.outcome)` is the only call from `/ask`; `ScorecardPage` is given only a `UsageSnapshot` of ints and a start time.
- Tests: `test_counts_record_no_question_text`, `test_docs_click_rules`, `test_warm_never_reaches_the_judge_or_spends`, `test_new_routes_write_no_log_line`, `test_service_logging.py`: pass (59 passed in the four files).
- Own probe (`canary_probe.py`): a canary string inside questions sent by JSON and form, an over-length canary question, `/warm`, two docs-click beacons (one with a canary body), `/scorecard`, `/health`. Canary absent from every log record, stdout, stderr, `/scorecard` and `/health`; snapshot read `visits=1, answered=1, refused=1, docs_clicks=1`.
- Not verified here: the deployed service's log tables (stage 13, tech spec 12.5).

## 8. INV-1..INV-5, kill switch, limits, cap (G)

| Invariant or control | Check | Result |
|---|---|---|
| INV-1 to INV-5 text | `SAFETY_INVARIANTS.md` sha256 equals main's; `git diff main -- .agentic` empty | pass |
| INV-4(b): no passage, path or reason on a refusal | refusal test (no passage, no signal, no path of `DOCS`); D1 | pass |
| Kill switch | `pipeline._ask` step 1 unchanged (0 removed lines in `pipeline.py`); new routes check `kill_switch == "off"` (`/warm`, `/count/docs-click` tests); `GET /` still returns `SERVICE_OFF` first | pass |
| 500 characters and 10 an hour | `limits.py`, `settings.py`, `validate_question` not in the diff; rate-limited-11th and over-500 cases are in the byte-equal golden | pass |
| Daily cap | `limits.py` unchanged; `resting()` is a read only (no `roll`, no reserve; mutation C3 shows a page load that searches is caught) | pass |
| Privacy and Article 50 wording | `test_disclosure_block_byte_identical` on `GET /` and the resting page | pass |
| `/ask` JSON | 39-case golden, independent regeneration | pass |

## 9. Findings

No P0, no P1. These P2 findings are for `END_REVIEW.md`.

| id | sev | where | what | action |
|---|---|---|---|---|
| Q1 | P2 | `enhance.js` submit handler (base had a `n > LIMIT` and empty check at lines ~170 to 180) and `render.py` `too_long_copy`, `EMPTY` | The script no longer stops an empty or over-500 question before sending; it posts it and the server answers 400. The card still says "Nothing was sent." (copy pre-existing on main, where it was true for script users and already untrue for no-script posts). With the script the text now reaches the service (not stored, not logged, not sent to Anthropic, limits still enforced server-side). | Owner/Security to note; the privacy wording is byte-identical so this is not changed here. A one-line client-side pre-check would restore the old behaviour. Not a block. |
| Q2 | P2 | `enhance.js` W2 "It can take up to a minute" | A figure with no record: the code allows up to 2 attempts x 20 s judge timeout (`anthropic_judge.py:30`, `MAX_ATTEMPTS`), the longest recorded answer is 5.09 s. Labelled unconfirmed; W1 "usually takes a few seconds" is supported by 1.66 s median (RESULT.md). | list in the copy deck in `END_REVIEW.md` |
| Q3 | P2 | `scorecard.toml` speed `basis` texts | Values match `runs/public-ask-the-docs/18-gate/RESULT.md` (30.8 s, 1.66 s median, 5.09 s slowest, $0.00785 = 0.156902/20 from 71,151 in and 1,460 out at $2 and $10). Not confirmed: the phrase "sent one after another" (searched RESULT.md, final-report.txt and the head of batch1.txt: two batches of 10, order is not stated). The figures are for revision 0000006, an earlier release, and are labelled so; they are not this release's measurements (D7, D8). | reword when the figures are filled (stage 10b) |
| Q4 | P2 | `tests/test_service_pages.py` | The existing assertion `url.startswith(("/", "https://github.com/"))` now also allows `#` (skip link); `test_initial_page_has_empty_region_and_form` loses `aria-labelledby` on the empty region. Both reasoned in `05-frontend.md` and accepted in D11; a bare fragment names no origin. | none |
| Q5 | P2 | suggestions copy "Questions the docs do answer"; R1 | The four questions are checked offline for retrieval only (labelled file in the top 5, `04-retrieval-check.json`). No judge verdict is shown, so that the docs answer A1 to A3 and refuse R1 is unconfirmed until the stage 13 live check. | confirm at stage 13; if a suggestion misses, the page shows a wrong label |
| Q6 | P2 | tests | No JS test runner: swap, waiting, beacon, copy and warm paths in `enhance.js` are covered by `test_page_script_builds_no_result_card` (string checks only) and `node --check`. Same as review F5. | stage 8 browser checks |

## 10. UI verification

Not done by QA: this role has no browser. What I could check is the rendered HTML through the test client: answer, refusal, resting (`GET /` at the cap), paused after a post, rate-limited, judge-error, kill-switch, too-long and empty pages, and `GET /scorecard` all render with the expected structure and copy (the pytest assertions above; `test_every_aria_reference_resolves` shows every `aria-labelledby` and `aria-describedby` target exists on the five views). The CSS and the script contain no `url(`, `@import` or `://`. Screenshots, axe, 375 px, keyboard, focus rings, the waiting card timing and console errors are **not verifiable here and belong to stage 8**. Console errors: not observed (no browser).

## 11. Deferred

| Item | Why | Owner |
|---|---|---|
| axe, 375 px, keyboard, local timings (C1.4.3 to C1.4.5 local) | needs the browser | Orchestrator, stage 8 |
| Live behaviour of A1 to A3 and R1, log tables, cold and warm live timings, rollback rehearsal | live and credentialed | stage 13 |
| README, runbook, status figures; scorecard links | later stages | stage 10, D8, D9 |
| Re-run of regression and C1.4.1 on the final tree | edits after this tree | Orchestrator, D8 |
| Coverage of changed files | no coverage tool in the project | none |

## 12. Recommendation

- [x] Pass to Security & Privacy Agent, with the conditions at the top (GO WITH CONDITIONS).
- [ ] Block

For `END_REVIEW.md` counts: tests added 62; confirmed failing first 57 (the other 5 are guards that pass on base by design); generated tests kept 62, removed 0; intent tests 4 of 4 failing first, passing now, and failing under mutation; C1.4.1 byte-equality pass with the golden re-derived; C1.4.7 730 passed, 0 failed, mypy and ruff clean.

## Hand off

Next agent: Security & Privacy Agent. Read first: sections 4 (headers), 7 (no question text), 9 Q1 (the over-limit and empty post now reaches the service with the script on) and the review's F1 (result store bound), which Security was asked to confirm.
