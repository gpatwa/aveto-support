# QA Evidence - result-page-clarity

> QA Evidence, stage 5, depth standard. Tree verified: HEAD `d223e11` (branch `claude/objective-kapitsa-83d3ae`), base `main` 6ab5548. Worktree clean at start.
> Browser items (C1.4 items 1 and 6) were measured by the Orchestrator in `08-browser-checks.md`; they are cited, not re-measured here.
> Scratch work (tree copies, dump and compare scripts, mutation copies) is under the session scratchpad
> `/private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-objective-kapitsa-83d3ae/88d804ad-ae70-4566-ac4b-186dbe5721e8/scratchpad/` (`tools/dump.py`, `tools/cmp.py`, `tools/mut.sh`). No product code or test was modified.

## Verdict: GO (no P0, P1 or P2 finding; two P3 notes)

## 1. Local regression sequence (each run separately, in order)

| # | Command | Result |
|---|---|---|
| 1 | `uv run mypy` | `Success: no issues found in 54 source files` |
| 2 | `uv run ruff check` | `All checks passed!` |
| 3 | `uv run pytest` | `738 passed, 12 deselected in 16.24s`, 0 failed |

C1.4 item 8: bar is at least 731 plus the 7 new tests = 738; met exactly. Both C1.7 red items are green (ruff clean; `test_service_pipeline.py` passes).
C1.7 changes inspected in the diff: one pinned value in `tests/test_service_pipeline.py` (`budget-guard.mjs` to `222f3970...9b8e`; `shasum -a 256 .claude/hooks/budget-guard.mjs` prints that value, so the pin matches the file in the tree and the hook itself is untouched); `runs/polished-chat-experience/13-live/tls-wrapper.py` import order only.

## 2. C1.4 item 4: nothing about answering moves

- `git diff main --stat -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md` prints nothing (empty). `git diff main --name-only` outside `runs/` and `tests/` lists only `aveto_service/pages.py`, `render.py`, `static/enhance.js`, `static/style.css`, `docs/ARCHITECTURE.md`. Also unchanged vs main: `pyproject.toml`, `uv.lock`, `Dockerfile`, `infra/`, `aveto_service/app.py`. Nothing under `.agentic/` changed at all.
- `/ask` golden: sha256 of `tests/golden/ask-json-32e54a6.json` on main and on HEAD are both `56e4b77bc53c7e207c046141092d461f8ecfec061f6ca22e171260d0a05e281c` (the file is not in the diff); it holds 39 cases. `uv run pytest tests/test_service_ask_bytes.py` passes (3 tests, including `test_ask_json_bytes_equal_main` and `test_security_and_json_header_sets_are_byte_identical`).
- Response headers, privacy and limits strings, what I did: `git archive main` into a scratch directory (a full copy of 6ab5548), and a script (`tools/dump.py`) that builds the app from a given tree with the suite's own fakes (`tests/service_fakes.py`, `HtmlPages`) and records status, all response headers and body for 16 states: `GET /`, resting, service off, `GET /result/unknown-token`, `GET /scorecard`, `GET /health`, the headers of `enhance.js` and `style.css`, `POST /ask` for answer (303 plus followed page), refusal, judge error, rate limited (11th), paused, service off, empty, too long. The script asserts it imported `aveto_service` from the tree it was given. Main rendered twice gave identical JSON (deterministic). Then HEAD vs main (`tools/cmp.py`):
  - Every state: status equal, all response headers equal (including `content-security-policy` ending `frame-ancestors 'none'`, `cache-control: no-store`, `referrer-policy`, `x-content-type-options`), the 303 `Location` header equal after masking the token. The only header difference anywhere is `content-length` of the two static files, as expected.
  - "What to expect" block (the limits line, the "does not store or log your question" privacy line and the retention line): present byte-identical (as a verbatim substring) in every page on HEAD where it is on main.
- Safety invariants: INV-1 to INV-5 live in `aveto_support/`, `prompts/` and the `.agentic` files, all empty in the diff; the CSP and headers are equal above (INV-5 egress, `'self'`). Verified by the empty diff and the header comparison; no behavioural change to the kill switch, 500-character, ten-an-hour or daily-cap paths is in the diff (`pipeline.py`, `limits.py`, `settings.py` untouched).

## 3. C1.4 items 2 and 3: home byte-equal, strings unchanged

From the same dump (main vs HEAD):

| State | Bytes equal main | Visible text and attribute strings added / removed |
|---|---|---|
| `GET /` | yes | 0 / 0 |
| `GET /` resting | yes | 0 / 0 |
| `GET /` service off | yes | 0 / 0 |
| `GET /result/unknown-token` | yes | 0 / 0 |
| `GET /scorecard`, `GET /health` | yes | 0 / 0 |
| answer, refusal, judge error, rate limited, paused, service off (POST), empty, too long | no (reordered by design) | 0 / 0 on all eight |

The visible-text comparison uses my own parser (text nodes outside script and style, plus `aria-label`, `alt`, `title`, `placeholder`, `value`, `href` and `data-count` attribute values) as multisets. Stronger: for all eight result states the multiset of whole HTML lines is identical between main and HEAD, so the change is only a reordering of unchanged lines. The three `GET /` goldens written on 6ab5548 equal both main's and HEAD's render. A string was neither added nor removed or reworded in any page state. The script diff (`git diff main -- aveto_service/static/enhance.js`) adds only identifiers, the number 16 and `"result-title"`/`"h1"`/`"#result"` selectors; no visitor-facing literal.

## 4. Test acceptance (pack v26) and mutation check

**Fail first, independently.** I copied main (`git archive main`) to a scratch directory, added only `tests/test_result_first.py` and the four goldens, confirmed the import comes from that copy, and ran: `6 failed, 1 passed` (T1, T2, T3, T5, T6, T7 fail; T4 passes). Same as `06-failfirst-6ab5548.txt`. **Three consecutive runs on HEAD:** `7 passed` each time (not flaky).

**Honest limit (spec open item 1).** Tests that pin "unchanged" behaviour cannot fail first on the code they pin: T4 passes on main by design, and the home-golden part of T2 and the string-multiset part of T3 also pass there. T2 and T3 qualify as fail-first only through their order assertions. For those pins I used mutations instead (below), which shows they are not vacuous.

**Mutation check.** Each mutation applied to a scratch copy of the HEAD tree (`git archive HEAD`, never the worktree), `tests/test_result_first.py` run, copy discarded. Unmutated copy: 7 passed.

| Mutation | Tests that fail |
|---|---|
| M1 `pages.py`: both callers `result_first=True` to `False` (revert the reorder) | T1, T2, T3 |
| M2b `pages.py`: `GET /` with a state also passes `result_first=True` | T2 |
| M10 `render.py`: home order changed (home bytes move) | T2 |
| M9 `render.py`: one "What to expect" string reworded | T2, T3 |
| M3 `enhance.js`: remove `preventScroll` | T5 |
| M7 `enhance.js`: `settle` back to bare `region.focus()` | T5, T7 |
| M4 `enhance.js`: remove `scrollTo` | T6 |
| M4b `enhance.js`: add `scrollBehavior = 'smooth'` | T6 |
| M5 `style.css`: remove `scroll-margin-top` | T6 |
| M6 `enhance.js`: `land()` no longer calls `resultFirst()` | T7 |
| M12 `enhance.js`: no `land()` on `#result` load | T7 |
| M8 `enhance.js`: reword `Link copied.` | T4 |

Survivors, both judged equivalent or immaterial: M2 (`page()` home passes `result_first=True` with `result=None`): the render guard `result is not None` already makes it a no-op, so no observable change. M11 (drop the `moved` run-once guard): T7 only checks that the text `moved` and `compareDocumentPosition` appear; behaviourally the guard is redundant because a second call finds nothing between the statement and the form. Not a defect (see P3-2).

**Generated tests:** 7 added (T1 to T7), 6 confirmed failing first on main, 1 pin (T4) that cannot; 0 removed. Each links to a "Done means"/Charter line (T1, T2: order and home-unchanged; T3, T4: strings; T5: focus; T6, T7: no motion, result first). No coverage tool in the project, so the Done-means link is the qualification. All build and pass three consecutive runs.

## 5. "Done means" lines (verbatim) and status

| Line | Status | Evidence |
|---|---|---|
| "Starts from `main` with pack v30 installed. First run under v30: the guard follows this worktree and the hard cap below; the end review counts every guard prompt ..." | Not verifiable by QA | Process measure for the end review; branch is 3 commits ahead of 6ab5548 with `.claude` diff empty vs main (pack v30 already on main) |
| "Measured, not asserted: in the browser pane at 1280 by 800 and 375 by 667, ... the result heading's top is within the top 25% of the viewport; before and after figures are recorded ..." | Cited, not re-measured by QA | `08-browser-checks.md` (Orchestrator: heading 16 px at both sizes) |
| "Nothing about answering moves. `git diff main -- aveto_support prompts .claude .agentic` is empty except the pack install; the 39-case `/ask` golden file is byte-equal; the response headers (including `frame-ancestors 'none'`) and the privacy and limits strings are byte-identical; INV-1 to INV-5 unchanged." | Pass | Section 2. The diff of `aveto_support prompts .claude .agentic` is empty in full (not only the listed subset) |
| "Tests that fail first: on a result page the question box precedes the result and the expectations follow it; on the home page the order is unchanged; every previously tested string still appears; keyboard focus lands on the result." | Pass, with the limit in section 4 | T1 to T7 fail first on main (6 of 7); home and string pins checked by mutation and by the whole-page comparison in section 3. Focus is asserted in the script text (T5); the live focus is the Orchestrator's browser check |
| "Accessibility: axe-core, zero serious or critical on the home and result views ...; keyboard-only flow; reading order matches the visual order." | Cited, not re-measured by QA | `08-browser-checks.md`. Server reading order = DOM order = visual order (no CSS `order`), asserted by T1 and shown by my line-multiset check |
| "Code review layer ... Security Review at smoke depth ... Release Gate tier 3 ... rollback rehearsal ... pull request ... screenshots retaken" | Not in QA scope | Later stages; code review is `code-review.md` (0 Important, 2 Nits). QA confirms for the Security smoke: no new route (`app.py` unchanged), no new input, no header change (section 2), no dependency change |
| "README, runbook and `.agentic/CURRENT_MVP_STATUS.md` state only recorded figures; STATE.md set to `done` ..." | Not verifiable yet | Tech Writer stage not run. Neither README nor the status file is touched on this tree |

## 6. What I could not verify, and findings

Not verified by me (and where I looked): anything that needs a browser (heading position, live `document.activeElement`, no animation, axe, keyboard flow, no sideways scroll at 375 px, JS-path DOM order after Ask). I read the script diff and rely on `08-browser-checks.md` for these; T5 to T7 are text checks on `enhance.js` (no JS runtime in the suite), so a behavioural JS regression would be caught by the browser check only. Unconfirmed from the tech spec: the no-JS fragment-jump heading offset (spec open item 5); I did not look at it, and it is not a Charter bar. Live-revision behaviour is stage 10.

| Sev | Finding |
|---|---|
| P3-1 | T5, T6 and T7 are string checks on the script, not behaviour. They prove the code is present (each fails under its mutation) but not that it works; the browser measurement is the behavioural proof. Accepted in the spec. |
| P3-2 | Mutation M11 survives: T7 does not test the `moved` run-once guard behaviourally. The guard is redundant in practice, so there is no user-visible risk. |
| P3-3 | `docs/ARCHITECTURE.md` (page row) is in the diff. Not forbidden by C1.3 (which lists `.agentic/` and the code directories); noting it so the Release Manager sees it is intentional. |

No P0, P1 or P2 findings. Recommendation to the Security Agent: GO. The change set is presentation only; the response headers, routes, inputs, dependencies and safety text are byte-identical to main, and nothing outside the five `aveto_service` and docs files plus tests and run records changed.
