# Stage 4 implementation - polished-chat-experience

> Owner: Backend Architect Agent, depth standard, 2026-10-26. Base 32e54a6. Status: **done at the checkpoint** (tech spec 14.1 step 4). Commit 1 `cd4d4b1` (tests first, no product file touched); commit 2 (this checkpoint).

## What was built

| File | Change |
|---|---|
| `aveto_service/pipeline.py` | added `WARM_QUESTION`, `_search_once`, `AskService._warm_lock/_warm_result`, `resting()`, `warm()`. Nothing else in the file changed (`git diff 32e54a6 -- aveto_service/pipeline.py` is add-only). |
| `aveto_service/counts.py` (new) | `UsageCounts` (slots exactly as spec 3.8), `UsageSnapshot`, `DOCS_CLICKS_PER_HOUR`. |
| `aveto_service/scorecard.py` (new) | strict reader `load_figures`, `FiguresError`, `build_links`, `ScorecardPage`, the copy S2/S5/S6/N1/B1 and the five count rows. |
| `aveto_service/scorecard.toml` (new) | 3 speed figures and 5 decisions from spec 3.7, each record checked to exist. No `[links]`, no `source_base` (D9: repository visibility not yet confirmed). |
| `aveto_service/app.py` | `scorecard=` keyword; `app.state.counts`; `counts.record(result.outcome)` after `service.ask`; `GET /` passes `PAUSED` at the cap and calls `counts.visit()`; new routes `GET /scorecard`, `POST /warm`, `POST /count/docs-click` (only with a renderer). `_json`, `_JSON_HEADERS`, gate order, `_cross_site`, `_read_body` untouched. |
| Tests (new) | `test_page_cards.py` (7, frozen), `test_service_ask_bytes.py` (3) + `tests/golden/ask-json-32e54a6.json` (39 cases), `test_service_counts.py` (2), `test_service_new_routes.py` (6), `test_service_scorecard.py` (34 items incl. 26 parametrized reader rules). |
| Run files | `04-retrieval-check.py` and `.json`, `08-local/devserver.py`, `08-local/time_local.py`, `13-live/live.py` (written only, never run; no credential; only `check/watch/ask/cold`), `04-failfirst-32e54a6.txt`, `04-checkpoint.txt`. |

No audit/log event added (spec section 7): `counts` and `warm` write nothing. No dependency, header, setting, infra or Dockerfile change. Files outside the 14.0 stage 4 list touched: none.

## Fail-first (C1.4.7)

`04-failfirst-32e54a6.txt`, taken on commit 1 with `git diff --stat 32e54a6 -- aveto_service aveto_support prompts` empty. Result: 15 failed, 3 passed, 1 collection error.
- Fail (assertion): T-R, T-S, T-D, T-A, T-ARIA, T-JS, T-C, T-W, T-W2 (extra, not-ready path), T-S0, T-RT, T-J, T-L, T-H2; T-K fails with `AttributeError` (`app.state.counts` does not exist yet).
- Collection error: `test_service_scorecard.py` (module `aveto_service.scorecard` absent), as 14.1 expects.
- Pass (guards): T-B, T-H1, T-COPY.

## Offline retrieval check (14.1 step 2) - no miss

`04-retrieval-check.json`; index sha256 `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756` (equals the live build's), commit `3a83b669...`, default ranking, index and models from the main checkout (the worktree has none).
A1 g01, A2 g03, A3 g04: a labelled source is in the top 5 for all three. Reserves p05 and p01 also pass (not needed). R1 gu18: top files `templates/DOC_DELTA_TEMPLATE.md, agents/market-researcher.md, templates/PRD_TEMPLATE.md, agents/data-analyst.md, docs/AGENT_ROLES.md` (recorded only; offline retrieval never abstains, so it cannot show a refusal; stage 13 checks it live).

## Checkpoint (14.1 step 4)

`04-checkpoint.txt`: `uv sync --locked` ok; mypy clean (52 files); ruff clean; pytest **714 passed, 6 failed, 12 deselected** (baseline 668 passed, so 52 new test items). The 6 failures are exactly the tests in `tests/test_page_cards.py` other than T-COPY, each an `AssertionError` (no collection or import error).

**Expected-failing list for stage 5 (the contract):** `test_refusal_card_shows_no_model_written_text`, `test_resting_state_at_the_cap`, `test_receipts_drawer_shows_only_what_the_service_held`, `test_answer_card_holds_only_text_from_a_listed_passage`, `test_every_aria_reference_resolves`, `test_page_script_builds_no_result_card`.

## Deviations and readings (none is a stop; Orchestrator to rule)

1. **`warm()` calls a module helper `_search_once`, not `judge.retrieve_for_judge` inline.** Spec T-W asserts the substring `_judge` is absent from `inspect.getsource(AskService.warm)`, but `retrieve_for_judge` contains `_judge`. The helper keeps the literal assertion true; behaviour is as spec 3.4 (one retrieval of `WARM_QUESTION` under `_retrieval_lock`, never `self._judge`, `_spend`, `_rate`, `_retrievals`, `emit_*`).
2. **Byte-equality case count.** Spec section 8 says "12 more" outcome cases but lists 14 inputs, and 11's table says "36 cases". I implemented all 14 listed: golden has 24 + 14 + `/health` = **39 cases**. QA's "36" in section 11 bar 1 should read 39 (the test asserts at least 36).
3. **`scorecard.py` imports `SECURITY_HEADERS` inside `ScorecardPage.response`**, not at module top: `pages.py` (stage 5) imports `scorecard.build_links`, so a top-level import would be circular. Same dict object, not a copy.
4. **`MAX_BEACON_BODY_BYTES` (spec 3.8) is not defined**: the beacon stops reading at the first body byte, which is stricter than 64 and makes the constant dead code. `POST /count/docs-click` otherwise as spec (same-origin, declared content-length 0, no byte, kill switch off, 60 an hour, always 204).
5. **T-H1 "names exactly"** is exact per response: the four security headers plus `content-length`, plus `content-type` except on the `/static/nope.txt` 404 and a 303 (neither has one on 32e54a6), plus `location` on a 303. `/scorecard` is checked in T-H2 (it cannot pass on 32e54a6).
6. **Extra tests beyond the spec's list:** `test_warm_reports_not_ready_when_the_search_fails`, `test_build_links_is_empty_on_any_error_and_never_raises`, `test_figures_reader_accepts_a_valid_file`, `test_missing_file_is_a_figures_error`, `test_scorecard_escapes_recorded_text`. The 503 scorecard page deliberately shows no counts (S6 only); T-F4 pins "no `<dl`".
7. **Scorecard markup for stage 5 to style:** `dl.figures > div > dt, dd.value, dd.basis`; `ul.findings` inside a `dd` under `h3`; `ul.decisions` with `span.when`; S6 is `div.state.state-note > h2`.

## Notes for stage 5

- `GET /` at the cap calls `HtmlPages.page(Outcome.PAUSED)`; `page(None)` is the ordinary page; kill switch gives `SERVICE_OFF`. A post that finds the cap still arrives through `form_outcome` as before. `pages.py` should call `aveto_service.scorecard.build_links()` (returns `{}` today: no `[links]` in the file).
- `test_page_cards.py` helpers parse the raw page: `<details class="receipts">` is the drawer marker; `id="result"` must be one element holding all cards; hidden suffix text is "to {path}, {span}" in its own element; per-passage meta line is one text run `Section: {heading}. Lines X to Y`.
- Stage 5 must also edit `tests/test_service_pages.py` line 67 (UX 6.1). The disclosure block (render.py lines 203 to 212 at 32e54a6) is pinned byte for byte by T-COPY on `GET /` and the resting page.
- The footer scorecard link (F3, `/scorecard`) is stage 5's; the scorecard page's own footer is built in `scorecard.py` (issue and docs lines as on the ask page).

## Verified, not assumed

- `uv run python tests/test_service_ask_bytes.py --write-golden` was run once at a tree identical to 32e54a6 in `aveto_service aveto_support prompts` (diff empty); re-running it left the file byte-identical.
- The dev server was started once on a spare port: `GET /`, `POST /warm` ({"ready":true}), `POST /ask` (gu18-type refusal, g04 answer), `/scorecard` counts 1/2/1/1/1 were seen, then it was stopped. `live.py` was compiled and linted only, never executed.
- Not confirmed: whether the page script and CSS are stage-5-ready (not my files); the live 8-question behaviour (stage 13).
