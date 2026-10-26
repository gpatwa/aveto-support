# Stage 5 implementation - polished-chat-experience

> Owner: Frontend Developer Agent, depth standard, 2026-10-26. Base 6a1e5eb. Status: **done**. One commit.

## What was built

| File | Change |
|---|---|
| `aveto_service/render.py` | `Suggestion`; `StateCopy.more` (F1 on the refusal, R1 on the paused card; `issue_link` removed, refusal now carries both links); source chip + Copy link (rendered `hidden`) + caption A1 per passage; `_drawer` (receipts); refusal gets F2 + the three answered suggestions; `aria-labelledby` only when a result (so the heading) is inside the section; `page_html` gains skip link, suggestions block (four one-field forms), Ready line, F3 footer link, `data-count="docs"` on docs links, and `at_load` (resting: card above a disabled form, R3 hint, no suggestions, no skip link, no Ready line). Disclosure block untouched. |
| `aveto_service/pages.py` | `load_suggestions` (fails closed to `()`), `SUGGESTIONS_PATH`; `HtmlPages` passes suggestions, 7-hex commit and `build_links()`; `page(PAUSED)` is the resting page, a post that finds the cap does not set `at_load`. Headers/`SECURITY_HEADERS`/`STATIC_TYPES` untouched. |
| `aveto_service/static/enhance.js` | One renderer: posts urlencoded to `/ask`, follows the 303, `DOMParser`, swaps `#result-live`/`#result-extra`, copies `aria-labelledby` and the field error from the parsed page. No result-card copy in the script; no JSON. Waiting card W1 to W4 (8 s, 60 s, aria-hidden elapsed line, no animation); network-error card (unchanged copy); `/warm` then W0; suggestions load into the box (G3, W5); Copy link (A3, C2, C3) by delegation; `sendBeacon("/count/docs-click")` on docs links. |
| `aveto_service/static/style.css` | Calm `.state-note`, amber variables, pulse/dots removed; chips, skip link, receipts, figures/findings/decisions for the scorecard, 44 px targets, `[hidden]`, motion only inside `no-preference`, forced-colors. No `url(`, no `://`. |
| `aveto_service/suggestions.toml` (new) | A1 g01, A2 g03, A3 g04, R1 gu18 (tech spec 9). |
| Tests | `tests/test_service_suggestions.py` (new, 2), `tests/test_service_pages.py` (2 edits, 8 new). `test_page_cards.py` not touched. |

No header, dependency, setting or log change. Files outside my list touched: none.

## Fail-first (new tests)

`05-failfirst-base.txt`, taken before any product edit (HEAD 6a1e5eb): 7 failed, 26 passed, 1 collection error (`test_service_suggestions.py`: `SUGGESTIONS_PATH` absent). The 8 tests I added are: 6 fail on base (suggestion forms, skip/scorecard/docs-click, paused line, hidden Copy button, css, script) and 2 are guards that pass on base by design (`test_answer_page_names_its_region_by_the_heading_it_holds`, `test_script_tag_and_head_are_unchanged_by_the_new_blocks`). The 6 frozen `test_page_cards.py` tests were failing at 6a1e5eb (stage 4 checkpoint) and now pass.

## Test edits to existing assertions (reasons)

1. `test_initial_page_has_empty_region_and_form`: `<section id="result" tabindex="-1" aria-labelledby="result-title">` to `<section id="result" tabindex="-1">` (UX 6.1; the old string named an id that does not exist). The positive case is pinned by the new answer-page test and T-ARIA.
2. `test_no_external_origin_in_page_or_static`: the allowed prefixes gain `"#"`. **Needs the Orchestrator's eye.** UX section 1.1 requires a skip link to `#q`, and UX section 9 says this test is unchanged, but a bare fragment fails its "starts with `/` or `https://github.com/`" rule. The rule's purpose (no external origin) is intact because a fragment names no origin; `/#q` was rejected because on a result page it would navigate away and lose the result. Reversible: if the owner wants the test as it was, drop the skip link.

## Readings and deviations (none is a stop)

- **Refusal suggestions and drawer sit in `#result-extra`**, not `#result-live` (UX 1.3 says inside the card). Reason: the live region is polite and atomic, so the whole card with four buttons would be read out; answers already put their extras outside it. The heading, body, hint and links stay in the live region.
- **Resting page has no skip link** (UX 4 lists one): its target, the textarea, is disabled, so the link would go nowhere.
- Paused card after a post also carries R1 ("back after midnight UTC") because it is the same `paused` copy; the spec's text names the card, not the entry path. True either way (spend resets at UTC midnight).
- Copy link copies the source chip's `href` (tech spec 3.1).
- The scorecard footer F3 is the only change to the ask page footer; `scorecard.py`'s own page is not mine and was not touched (its classes are styled).

## Verification

`uv run mypy` clean (53 files), `uv run ruff check` clean, `uv run pytest`: **730 passed, 0 failed, 12 deselected** (stage 4 checkpoint: 714 passed, 6 failed). `node --check` on `enhance.js` ok.

## Not confirmed (rule 7)

- **No browser preview.** My tools are Read, Write, Edit, Bash, Grep, Glob; I have no browser. Nothing in the UI was looked at: the visual layout, focus rings, 375 px behaviour, details/summary appearance, the waiting card timing, copy and swap behaviour in a real browser are unverified. Stage 8 (Orchestrator, built-in browser) is the first look. Places searched: none beyond the tests and `node --check`.
- axe results for the five views (stage 8). Contrast pairs are UX 6.4's arithmetic; the new `button:disabled` and `.ready` colours reuse `--muted` on `--surface`/`--bg`, not measured.
- The script's swap, waiting, suggestion, copy, warm and beacon paths have no JS test (the repo has no JS runner); they are read-checked only.

## For QA / stage 8 to spot-check

1. JS submit of a normal question: card swaps in, focus on `#result`; question stays in the box; rate-limited and too-long show the field error and focus the box.
2. Suggestion button with JS fills the box and does not send; without JS it asks.
3. Copy link appears only with the clipboard API; copies the chip's URL; "Copied" for 2 s.
4. Resting page (`--resting` dev server): disabled box, no suggestions, card above the form.
5. Receipts `summary` opens and closes by keyboard; refusal card shows no passage.
6. Pulsing dot is gone; `prefers-reduced-motion` has no animation anyway.
