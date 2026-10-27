# Tech Spec — result-page-clarity

> Software Architect, stage 1, depth standard, 2026-10-27. Inputs: `intent.md`, `CHARTER.md` (C1.4, C1.6, C1.7),
> `00-slice-plan.md`, `00-setup-dryruns.md`, `.agentic/`, `aveto_service/render.py`, `pages.py`, `static/enhance.js`,
> `static/style.css`, `tests/test_service_pages.py`, `tests/test_page_cards.py`, `tests/test_service_ask_bytes.py`,
> all read on `main` 6ab5548 (this worktree, 0 ahead / 0 behind).

**STOP-FLAG: none.** No visitor-facing string needs to change (section 3). No new route, input, header, dependency,
model or processor (section 5).

## Summary

Two mechanisms, presentation only:

1. **Server order.** `page_html` gains one keyword, `result_first: bool = False`. Only the two handlers that render a
   response to a question pass `True`; every `GET /` state (normal, service off, resting/paused) and the unknown-token
   page keep `False` and render byte-equal to `main`.
2. **Landing.** `enhance.js` replaces the scrolling `region.focus()` with a `land()` step: put the page in the
   result-first order (once), focus `#result` with `preventScroll: true`, then jump (no animation, for anyone) so the
   result heading's top sits 16 px below the viewport top. `style.css` adds `scroll-margin-top` on `#result` so the
   no-JS fragment jump leaves the same small gap.

Grounded on the setup finding: `focus()` on a region taller than the viewport scrolled to its far end (heading at
−2,820.9 px and −4,182.9 px for the answered question; −2.9 px for the refusal at 375×667). The design therefore
never lets `focus()` scroll and positions the heading itself. Cause is stated only as far as the four before figures
show; the after figures (stage 4) decide whether it worked.

## Data model deltas

None. No schema, store, migration, setting or file format changes. `ResultStore`, `AskResult`, the `/ask` JSON and
the 39-case golden file are untouched.

## Service surface

### 1. The exact reorder (render.py, pages.py)

**Signature change (the only one):**

```python
def page_html(result, raw, issue_url, docs_url, *, suggestions=(), commit="", links=None,
              at_load=False, result_first=False) -> str
```

**Condition:** `first = result_first and result is not None and not at_load`. When `first` is false the function
returns exactly the bytes it returns on `main` (same template, same pieces, same order, same newlines).

**Pieces.** Extract, as literal constants with no byte change, the block that today sits at render.py lines 305-313:

- `EXPECT` = `'<h2 class="plain">What to expect</h2>\n<ul>\n' + the six <li> lines + '</ul>\n'` (copied byte for byte;
  the one-line statement `<p>Verbatim passages …</p>` on line 304 stays in the template, it is not part of `EXPECT`).
- `try_block` (unchanged code, lines 280-286).
- `region` (unchanged `result_region(...)` call).

**Home and resting (`first` false):** `…{statement}\n{EXPECT}{above}{try_block}<form …>…</form>\n{ready}{below}\n</main>`
— identical to today.

**Result page (`first` true):** `…{statement}\n<form …>…</form>\n{ready}{region}\n{EXPECT}{try_block}</main>`
(newlines between pieces are the Frontend Developer's choice; only the home bytes are pinned). Resulting order in the
HTML, which is also the visual and reading order (no CSS `order`, flex reordering or absolute positioning):

1. skip link `Skip to the question box` (unchanged, before `<main>`)
2. `<h1>` title, then the one-line statement
3. `<form id="ask-form">` (label, textarea, hint, count, status, `#q-error`, Ask button), then `<p id="ready">`
4. `<section id="result" tabindex="-1">` (unchanged markup, unchanged contents, including the refusal's
   "Questions the docs do answer" chips and the receipts drawer)
5. `What to expect` heading and its six bullets
6. `Try a question`, `#sugg-hint`, `#suggestions` (only when suggestions loaded, as today)
7. `</main>`, footer (unchanged)

**Who passes `result_first=True` (pages.py):**

| Handler | Today | Change |
|---|---|---|
| `HtmlPages.page(state)` — `GET /` in every state | `_html(None, "")` / `_html(AskResult(state), "", at_load=…)` | none (`False`) |
| `HtmlPages.form_outcome` non-admitted branch (no-JS `POST /ask`: empty, too long, body too large, unusable, bad request, rate limited, paused, service off, judge error) | `_html(result, raw, result.status)` | `result_first=True` |
| `HtmlPages.result_page(token)` — `GET /result/<token>` | `_html(result, "")` | `result_first=True` (an unknown or expired token gives `result=None`, so the page stays the empty home page, byte-equal to `GET /`, as `html_port.py` documents) |

`_html` gains the same keyword and forwards it. `html_port.py` (the Protocol) is unchanged: its method signatures do
not change.

Why a keyword and not `result is not None`: `GET /` with the kill switch on renders `AskResult(SERVICE_OFF)` with
`at_load=False`; keying the reorder on `result is not None` would change that `GET /` and break C1.4 item 2.

### 2. Scroll and focus

**enhance.js (JS path: fetch + swap).** Constants and one new function; no new string shown to a visitor.

```js
var TOP_GAP = 16; // px between the viewport top and the result heading
function resultFirst() {            // same order the server gives a result page; runs at most once
  if (moved || region.compareDocumentPosition(form) & Node.DOCUMENT_POSITION_FOLLOWING) { return; } // resting layout
  var main = form.parentNode, n = main.querySelector("h1").nextElementSibling.nextElementSibling, take = [];
  while (n && n !== form) { take.push(n); n = n.nextElementSibling; }
  take.forEach(function (e) { main.appendChild(e); });   // after #result, in their order
  moved = true;
}
function land() {
  resultFirst();
  region.focus({ preventScroll: true });
  var t = document.getElementById("result-title") || region;
  window.scrollTo(0, Math.max(0, t.getBoundingClientRect().top + window.pageYOffset - TOP_GAP));
}
```

- `settle(field)`: the non-field branch calls `land()` instead of `region.focus()`. The field branch (`q.focus()`)
  is unchanged: a field error keeps focus in the box, which is now directly above the result.
- On a page served as a result page (statement then form), `resultFirst` finds no nodes between the statement and the
  form and moves nothing. On the home page it moves `What to expect`, its list, `Try a question`, `#sugg-hint` and
  `#suggestions` to after `#result` — the same order as the server's result page, so both paths look and read alike.
  The move happens in `settle`, together with the jump, never while waiting, so the page does not shift under the
  visitor during the wait.
- On load, if `location.hash === "#result"` and `#result-title` exists (a reload of `/result/<token>#result` with
  JS on), call `land()` once, so the JS-on server-rendered path behaves like the swap path.
- **Motion.** `window.scrollTo(x, y)` with two numbers is an instant jump, and neither `style.css` nor the script sets
  `scroll-behavior: smooth`. There is no animation for anyone, so `prefers-reduced-motion: reduce` is honoured by
  construction (the brief's "no motion that cannot be turned off"). Decided against a smooth scroll for
  `no-preference`: a 3,000–9,000 px animated scroll is the motion the intent warns about, and it would make the
  stage 4 measurement timing-dependent.
- **Why not `scrollIntoView`:** it honours `scroll-margin-top` but its behaviour on a focused tall region is what
  failed at setup; an explicit `scrollTo` on the heading's measured position is deterministic.
- **Short pages:** a document cannot scroll past its end. Moving the expectations and suggestions below the result
  (about 500-700 px at 1280 wide) gives the refusal enough page below it to reach the top. Stage 4 measures this.
- **Sticky/anchored:** nothing in `style.css` is `position: sticky` or `fixed`; the skip link is `absolute` and off
  screen until focused. So no header can cover the heading and `TOP_GAP` needs no header allowance. Scroll anchoring
  (`overflow-anchor`) is not involved because the move and the jump happen in one synchronous step after the swap.

**style.css (no-JS path, and any fragment jump).** Add `#result { scroll-margin-top: 0.5rem; }` (extend the existing
`#result { margin-top: 1.5rem; }` rule). The browser's fragment navigation to `#result` then puts the section's top
8 px below the viewport top; the heading sits a further `.state` padding (0.5 rem) plus its own margin lower, well
inside the 25% bar; stage 4 measures it.

**No-JS path.** Form and suggestion chips post to `/ask#result`. Admitted: 303 to `/result/<token>#result`, which the
browser follows and then jumps to `#result` on the result-first page (question box above, off screen, one scroll up).
Not admitted: a 200 result-first page at `/ask#result`, same jump. Keyboard: fragment navigation makes `#result`
(`tabindex="-1"`) the sequential-focus starting point, so the next Tab goes to the first control inside or after the
result; browsers do not move `document.activeElement` on a fragment jump. That is the no-JS behaviour on `main`
today and is not changed. Shift+Tab from there reaches the Ask button and the box.

**Keyboard focus, JS path.** After Ask, `document.activeElement` is `#result` (unchanged target; only scrolling is
suppressed). Its `aria-labelledby="result-title"` gives screen readers the outcome heading; the live wrapper still
announces the heading. The visible focus ring (`#result:focus-visible`) is unchanged; programmatic focus after a
keyboard-initiated submit shows it in Chromium and Firefox.

## Adapter boundaries

None touched. The judge adapter, retrieval and the Anthropic client are not on this slice's path; the stand-in judge
in `runs/polished-chat-experience/08-local/devserver.py` is used only for stage 4 measurement, unchanged.

## Audit / feedback / usage events

None added or modified. The change does not alter any state: no new state-changing function exists, so no audit
event is owed. The `/count/docs-click` beacon and the abuse log are untouched (the moved nodes carry no
`data-count`; the footer and drawer links that do are not moved).

## Integration points

`render.page_html` (extended by one keyword), `pages.HtmlPages._html`, `.form_outcome`, `.result_page` (pass the
keyword). Nothing under `aveto_support/`, `prompts/`, `.claude/`, `.agentic/` (except the Tech Writer's figures in
`CURRENT_MVP_STATUS.md`). No new service file.

## 3. Strings that stay byte-identical (C1.4 item 3, C1.6)

Conclusion: **no string changes, none is added, none is removed.** The reorder moves whole elements; `land()` and
`resultFirst()` set no `textContent`. The only new literals in `enhance.js` are identifiers and numbers
(`"result-title"`, `"#result"`, `"h1"`, `16`), none shown to a visitor.

**A. Server HTML, every page (render.py template and constants).**
`<title>Ask the Aveto docs</title>`; skip link `Skip to the question box`; `<h1>Ask the Aveto docs</h1>`; the statement
`Verbatim passages from Aveto's docs; an AI model decides only whether they answer. Nothing on this page is written by
an AI model.`; `What to expect` and its six bullets (exactly `DISCLOSURE_LINES[1:]` in `tests/test_page_cards.py`);
`Try a question`; `SUGGEST_HINT`; the four suggestion texts (`SA1`-`SA3`, `SR1` in `test_page_cards.py`, from
`suggestions.toml`); `Your question about Aveto`; `Up to 500 characters.`; `RESTING_HINT`; `N of 500 characters` and
`N characters over the limit of 500. Shorten your question.`; `Ask`; footer `Open a GitHub issue`, `. Add your
question to the issue yourself if you wish.`, `Read the docs on GitHub`, `See the quality scorecard`.

**B. Result region (render.py).** Every `StateCopy` title, body and `more` in `STATES`, `EMPTY`, `too_long_copy`
(`Yours is N.` / `Yours is much longer.`), the `#q-error` first sentence; `Found N passage(s).`; passage cards
(`Section: …`, `Line(s) …`, `View … of … on GitHub`, `Copy link` + ` to …`, `Quoted from the docs, word for word`,
`aria-label="Passage text from …"`); `Questions the docs do answer`; drawer (`How this answer was made`, `How this
result was made`, `Outcome`, `Docs version`, `Commit … on GitHub`, `Passages listed`, `None. Nothing is listed when the
docs don't answer.`, `CHARTER_LINK`, `RUN_RECORD_LINK`); in-body links `Open a GitHub issue`, `Read the docs on
GitHub`. render.py's result-region code is not edited, so these cannot move within the region.

**C. Script (enhance.js).** The three `WAITING` pairs; `Waiting: N second(s)`; `Up to 500 characters. Press Ctrl+Enter
or Cmd+Enter to send.`; `Choose one to put it in the box, then press Ask. Three are answered in the docs and one is
not, so you can see both outcomes.`; `We couldn't reach the service`; `Check your connection and try again. Your
question is still in the box.`; `Enter a question before you press Ask.`; `Shorten your question to 500 characters or
fewer.`; `Asking...`; `Ask`; the count and status strings (`characters over the limit of`, `Over the limit by`,
`characters left`); `Question loaded. Press Ask to send it.`; `Copied`; `Copy link`; `Link copied.`; `Couldn't copy the
link. Use the source link instead.`; `Ready to search the docs.`

**How tests pin them** (section 4): (i) every `GET /` state is byte-equal to a golden written on 6ab5548 (A on the
home page, plus resting and service-off); (ii) for each result page, the multiset of visible text nodes and
`aria-label` values equals a golden multiset written on 6ab5548 — so nothing added, removed or reworded, only moved;
(iii) list C is asserted present verbatim in `enhance.js`, and the reviewer checks the diff adds no visitor-facing
literal. The existing `test_disclosure_block_byte_identical`, `test_page_script_builds_no_result_card` and the state
tests in `test_service_pages.py` stay as they are and must still pass.

## 4. Test plan (fail-first; stage 2 writes and runs them on 6ab5548 before any product edit)

New file `tests/test_result_first.py` (keeps the existing files' diffs small). Goldens are written on 6ab5548 by a
`write_goldens()` function in that file, following `tests/test_service_ask_bytes.py::write_golden`, run once before
`render.py` is edited; their sha256 and the command go in the build artefact. Clients come from
`tests/test_service_pages.py::make_client` (stub judge, fixed runtime, real `suggestions.toml`).

| # | Test | What it asserts | Fails on 6ab5548? |
|---|---|---|---|
| T1 | `test_result_page_order_question_box_result_then_expectations` | For `/result/<token>` (answer and refusal, via `followed`) and for no-JS `POST /ask` error pages (empty, too long, rate limited 11th, paused): index of `<h1>` < statement < `<form id="ask-form"` < `<section id="result"` < `What to expect` < `Try a question` < `<footer>` | yes (expectations precede the form) |
| T2 | `test_reorder_applies_only_to_answers_of_a_question` | (a) `GET /` normal, `GET /` resting (cap below floor), `GET /` service off (`kill_switch="on"`), and `GET /result/unknown` are each byte-equal to their golden (`tests/golden/home-6ab5548.html`, `home-resting-6ab5548.html`, `home-off-6ab5548.html`; unknown token compared to the home golden); (b) the answer page from (T1) does **not** have `What to expect` before `<form id="ask-form"` | yes, through (b); (a) alone is a no-change pin and passes on main by design |
| T3 | `test_result_pages_keep_every_string_only_moved` | For answer, refusal, judge error, rate limited, paused (POST), service off (POST), empty, too long: multiset of visible text nodes + `aria-label` values equals `tests/golden/result-strings-6ab5548.json`; and the ordered sequence `[statement, "Your question about Aveto", result title, "What to expect", "Try a question"]` appears in that order | yes, through the ordered sequence; the multiset part is a no-change pin |
| T4 | `test_script_strings_unchanged` | every string in list C is in `enhance.js` verbatim | no (pin; passes on main by design) |
| T5 | `test_focus_lands_on_the_result_without_scrolling_it` | `settle`'s non-field branch reaches `region.focus({ preventScroll: true })` (via `land`); `enhance.js` has no bare `region.focus()`; the result section keeps `id="result" tabindex="-1"`; form action and 303 `Location` end in `#result` | yes (`preventScroll` absent) |
| T6 | `test_script_scrolls_the_heading_to_the_top_without_motion` | `enhance.js` contains `scrollTo(`, `getElementById("result-title")`, `TOP_GAP`; neither `enhance.js` nor `style.css` contains `smooth`; `style.css` has `scroll-margin-top` in the `#result` rule | yes |
| T7 | `test_script_puts_result_first_once_after_ask` | `enhance.js` defines `resultFirst`, guards it with the moved flag and `compareDocumentPosition`, calls it from `land`, and `land` is called from `settle` and from the `location.hash === "#result"` load check | yes |

T5-T7 are static checks on the script's text (the suite has no JS runtime; adding one is a new dependency and is
out). What only a browser can show — **stage 4, Orchestrator**: the heading position at both sizes; that
`document.activeElement` is `#result` after Ask; that the jump has no animation (and none with reduced motion
emulated); that the JS-path DOM order after Ask matches T1's order; the keyboard-only flow; reading order; axe.

Existing tests unchanged and expected to pass: all of `test_service_pages.py`, `test_page_cards.py`,
`test_service_ask_bytes.py` (the `/ask` golden is JSON-only, built without the HTML port, so the reorder cannot touch
it). Suite bar: ≥ 731 + 7 new, 0 failures, mypy and ruff clean.

## 5. What does not change

- **No new route** (`app.py` untouched), **no new input** (no form field, query parameter or header read), **no
  header change** (`SECURITY_HEADERS` untouched; static files served with the same set), **no new dependency**
  (`pyproject.toml`, `uv.lock`, image unchanged; axe-core stays in the scratchpad per C1.5). No change under
  `aveto_support/`, `prompts/`, `.claude/`.
- **INV-1** (nothing written to GitHub without recorded approval): the service page has no write path; unchanged.
- **INV-2** (answers drawn from Aveto's docs, passages named): passage cards and drawer are emitted by unedited code;
  unchanged.
- **INV-3** (draft checked by a different model): no drafting on this path; judge untouched; unchanged.
- **INV-4** (retrieval returns only verbatim passages at the pinned commit): retrieval untouched; unchanged.
- **INV-5** (program egress limited): no new origin, script, font or request; the CSP `'self'` holds; unchanged.
- Kill switch, 500-character and ten-an-hour limits, daily cap, no question stored or logged: untouched code paths.

## 6. C1.7 items for the Frontend Developer

1. In `tests/test_service_pipeline.py`, `CORE_SHA256`, change only the pinned value for `.claude/hooks/budget-guard.mjs`
   to `222f39708d03770a33d09ba7579ee178fb78154ae60c1779239eab2cbf4a9b8e`. Do not touch the hook. Record it in the build
   artefact as the pack v30 install's doing.
2. Run `uv run ruff check --fix runs/polished-chat-experience/13-live/tls-wrapper.py` (import order only); confirm the
   diff is import order only.

## Rollback plan

Code-only, stateless change; no data to migrate back.

- **Before merge:** close the pull request; `main` is untouched.
- **After deploy:** activate the previous revision `ca-aveto-ask--0000011` (image `aveto-ask:ffc2e2e5f39a`) at 100%
  traffic by the Bicep path Charter C8.3 names; check `/health` and `GET /`; this is the stage 10 rehearsal. Kill switch
  remains the emergency stop.
- **In the repo:** `git revert` of the slice's merge commit restores `render.py`, `pages.py`, `enhance.js`,
  `style.css`; delete `tests/test_result_first.py` and its goldens with it. The C1.7 fixes are independent and stay.
- Browser caches: `Cache-Control: no-store` on every response, so a rolled-back revision serves the old script at once.

## 7. Risks, open items, measurement method

**Measurement (stage 4, Orchestrator; same method as the before figures).** Local `devserver.py` (stand-in judge,
named in the record), built-in browser pane at 1280×800 and 375×667, suggestion 1 (answered) and suggestion 4
(refused) loaded and sent with the real Ask button, wait 3.5 s, read `#result-title.getBoundingClientRect().top` and
`document.activeElement.id`. Pass: `0 ≤ top ≤ 200` (1280×800) and `0 ≤ top ≤ 166.75` (375×667), focus `result`.
Also record: the same with JS disabled (or by loading `/result/<token>#result` directly) for one answer; reduced
motion emulated (expect the same figure, no animation); DOM order after Ask. Expected top ≈ 16 px on the JS path.

**Risks / open items.**

1. *Reading of C1.4 item 8.* A no-change pin (home golden, string multiset, list C) cannot fail on the code it pins.
   T2 and T3 are made fail-first by their order assertions; T4 is a pure pin. The Orchestrator should confirm this
   reading in `END_REVIEW.md`.
2. *Short results may not reach the top.* An error box (for example "Please enter a question") on a short page at
   1280×800 may leave the heading lower than 16 px because the page ends; the expectations and suggestions below
   the result make this unlikely, and it is still inside the 25% bar if it happens. Not part of the measured bar
   (answered and refused only); stage 4 may note it.
3. *Structural selection in `resultFirst`.* It relies on `<h1>` then the statement then the moved nodes then the form;
   T1-T3 pin the server structure it depends on, and T7 pins the function. If the template changes later, the move
   silently does less, never more (it only moves siblings strictly between statement and form).
4. *No-JS focus.* Fragment navigation sets the focus starting point, not `activeElement` — browser behaviour, as on
   `main`. C1.4 item 5's browser confirmation is for the JS path; stage 4 should state the no-JS result as observed.
5. *Unconfirmed:* the exact heading offset inside `.state` (padding plus `h2` margin) on the no-JS path was not
   measured; only `style.css` was read. Stage 4 records it.

## Hand off

**To: Frontend Developer (stage 2), sole owner** of `aveto_service/render.py`, `aveto_service/pages.py`,
`aveto_service/static/enhance.js`, `aveto_service/static/style.css`, `tests/test_result_first.py`,
`tests/golden/home-6ab5548.html`, `home-resting-6ab5548.html`, `home-off-6ab5548.html`,
`result-strings-6ab5548.json`, and the two C1.7 items. Order: write goldens on 6ab5548 → write T1-T7 → run them,
record which fail (expected: T1, T2, T3, T5, T6, T7) → product edits → full suite, mypy, ruff. If any string looks as
though it must change, stop and report (Charter section 9 item 1).
