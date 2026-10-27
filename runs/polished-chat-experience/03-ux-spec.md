# UX Spec - polished-chat-experience

> Owner: UI Designer Agent. Stage 2, depth standard, 2026-10-26. Status: **ready for architecture**.
> Source: `intent.md` (items 1 to 8), `CHARTER.md` (C1.4 bars 3 and 4, C1.6, C5.0, section 9), `01-scope.md`, `DECISIONS.md` D1 to D5 (all bind this spec), `.agentic/SAFETY_INVARIANTS.md` INV-4.
> Read for the current page: `aveto_service/render.py`, `static/style.css`, `static/enhance.js`, `pages.py`, `app.py` (routes only), `tests/test_service_pages.py`. No code written.
> Not confirmed by me (I have no browser or shell): the axe node in section 6.1 is read from the source, not run. Places searched: `render.py` (all), `enhance.js` (all), `setup-dryruns.md` and `01-scope.md` (they record "1 serious `aria-prohibited-attr`, 1 node, on the current page" with no selector).

## 0. Decisions applied (not reopened)

| Decision | What it does to this spec |
|---|---|
| D1 | The refusal card shows **no passages**: message, rephrasing hint, issue link, docs link, suggested questions. |
| D2 | The receipts drawer shows outcome, docs commit, and the file and line list the request already held. **No `signal` line, no prompt name or hash.** |
| D3 | "Docs search" means the **docs link stays visible** in the resting state. No search feature is designed. |
| D5 | The "26 seconds" figure appears nowhere. Waiting copy states no duration it cannot back. The scorecard shows only recorded timings. |
| C5.0 | Response headers are unchanged. The page is not framed. Nothing here needs a header change. |
| C1.6 | Section 8 is the whole copy deck. It contains no new claim about privacy, data handling, law or AI. Strings that touch those topics today are listed in section 9 and stay byte-identical. |

Single-turn only. No chat transcript, no history, no avatar bubbles. "Chat" here means one question box and one result.

---

## 1. Layout per screen

Common frame (all views): one centred column, `max-width: 42rem`, `1rem` side padding (the current `main, footer` rule, reused). System font stack, no web font, no image, no icon font. Light and dark colour schemes follow the existing `prefers-color-scheme` variables. All decoration is CSS borders and text; nothing needs `url()` (a test forbids it in the CSS).

### 1.1 Ask page (`GET /`, and the same page after a result)

Top to bottom, in DOM order (DOM order is the keyboard order; nothing is reordered with CSS):

1. **Skip link** "Skip to the question box" (visible only on focus; targets `#q`).
2. `<h1>` Ask the Aveto docs; the one-paragraph intro (existing, byte-identical).
3. "What to expect" list (existing, byte-identical, **same position as today: before the form**). See open item O1 for the owner.
4. **Suggested questions block** (new): small heading, one hint sentence, four full-width question buttons (three answered, one not).
5. **Question form** (existing `#ask-form`): label, textarea, hint, count, status, field error, Ask button. Ask is full width at 375 px, as today.
6. **Ready line** (new, JS only, empty until the warm-up returns): one muted line under the Ask button.
7. **Result region** (`#result`): empty on a fresh page; otherwise one of the cards in 1.2 to 1.6.
8. Footer: issue link line, docs link line (both existing), plus one new line: link to the scorecard.

Hierarchy: the h1 and the question box dominate; the suggestions are secondary (outlined buttons); the result card is the visual climax when present (heavier border, larger heading, `1.5rem` above it).

- **375 px:** single column, every block full width, no horizontal scroll. Suggestion buttons are stacked and left-aligned, text wraps (long question: at most 3 lines). Long file paths wrap anywhere (`overflow-wrap: anywhere`). Passage text keeps its own horizontal scroll inside the `pre`; the page never scrolls sideways.
- **Desktop (42rem column, centred):** same order; the source chip and Copy link sit on one row; suggestion buttons stay full column width (four short stacked lines read better than a wrapped grid).

### 1.2 Answer card (outcome `answer`)

Inside `#result-live`: the existing `div.state.state-answer` with the h2 "The docs answer this" and the line "Found N passage(s)." (both unchanged).

Below it (inside `#result-extra`, outside the live wrapper, as today) an ordered list of **passage cards**, one per listed passage, in the order the response lists them. Each card, top to bottom:

1. `<h3>` with `<code>{path}</code>` (unchanged element and text).
2. Meta line: "Section: {heading}. Lines X to Y" (unchanged; `Line X` when the range is one line).
3. **Action row** (flex, wraps, `0.5rem` gap): the **source chip** (an `<a>`, the existing "View lines X to Y of {path} on GitHub" link, text unchanged, styled as an outlined pill, min-height 44 px) and the **Copy link** `<button type="button">` (secondary style, min-height 44 px).
4. Caption "Quoted from the docs, word for word" (muted, small).
5. The quoted passage: the existing `<pre class="passage" tabindex="0" role="region" aria-label="..."><code>{text}</code></pre>`, restyled as a quotation (4 px left rule in `--link`, `--surface` background). Markup inside the `pre` is unchanged, so `<code>{text}</code></pre>` stays byte-identical to `retrieve`'s text.

After the last card: the **receipts drawer** (1.6).

Nothing on the card is composed by the page: every sentence in the quoted block is the passage text; the headings, labels and links are fixed copy from section 8 or the path, section, line numbers and URL of a listed passage. (Test target for the Architect: every sentence in `pre.passage` appears in a listed passage; the surrounding labels are fixed strings, not sentences from a model.)

### 1.3 Refusal card (outcome `no_confident_match`), per D1

Inside `#result-live`: `div.state.state-note` (restyled calm card, see 6.4), h2 "The docs don't answer this" (unchanged), then:

1. The existing body sentence, unchanged: "No confident match was found, so nothing is shown. You can change your question and ask again, or open a GitHub issue."
2. **Rephrasing hint** paragraph (new, fixed text).
3. Links row: "Open a GitHub issue" and "Read the docs on GitHub" (both `<a>`, both min 44 px tall as pills; today the refusal shows only the issue link).
4. `<h3>` "Questions the docs do answer" and the **three answered suggestions** as the same buttons as in 1.1 (slots A1 to A3, never the refused one).
5. Receipts drawer (1.6), closed.

There is **no `ol.passages`, no `pre`, no path, no line number** on this card (`'class="passages"' not in text` is pinned today and stays true). The card shows no text that came from the model: the title, sentence, hint and labels are fixed strings; the only variable parts are the four suggestions' fixed text and the two URLs.

It must read as a deliberate, calm outcome and not as a fault: no red, no "!" icon, no `role="alert"` (today's refusal already has none). The visual cue is a 4 px `--link` (blue) left rule on a `--surface` background.

### 1.4 Resting state (outcome `paused`, daily allowance used)

The card is today's `paused` card with a calmer look and one more fact. Two entry paths, same card:

- **At page load (`GET /` while the allowance is used).** Needs the Architect's route change (today `GET /` shows "The service is off" only for the kill switch). The resting card renders **above the form**. The suggestions block is **not rendered** (nothing can be tried). The textarea and the Ask button are rendered with the `disabled` attribute and a one-line explanation replaces the hint (copy R3). The docs link and the issue link are in the card; the footer repeats both.
- **After a submit that finds the allowance used (`POST /ask`).** The card appears in the result region; the form stays enabled and keeps what the visitor typed (as today). The suggestions block stays.

Card content: h2 "Paused for today" (unchanged), body sentence (unchanged), **new paragraph** "Ask the Docs is back after midnight UTC.", then the links row (`Open a GitHub issue`, `Read the docs on GitHub`). Style `state-note` (calm), **not** `state-error`: no "!" icon, no red, no `role="alert"` (pinned by `test_paused_state`). The exact count of "Read the docs on GitHub" on a paused result page must remain 2 (card + footer), so the card holds exactly one docs link and no third is added anywhere on that page.

The resting card is the only thing that reads "midnight UTC". The allowance resets at UTC midnight (`tests/test_service_limits.py::test_spend_resets_at_utc_midnight`), so the sentence is true.

### 1.5 Waiting state (JS path only)

Replaces the result region while a request is in flight; `div.state.state-note` (calm card) with:

- h2 (title), one paragraph, and one **elapsed line** "Waiting: N seconds" that updates once a second as plain text (`aria-hidden`; it is a visual aid, not announced).
- **No progress bar, no percentage, no spinner or pulsing dot, no streaming text, no step list.** The current pulsing dot and the "..." fallback are removed: an animation implies progress the page cannot see. Because the service answers in one request, the page can truthfully know only: the question was sent, how long it has waited, and whether a reply has come. The copy states exactly that.
- The button reads "Asking..." and is `aria-disabled` (existing behaviour); the form stays visible, the question stays in the box.

Time thresholds (client clock, the only thing the page measures): 0 s, 8 s, 60 s. Copy W1 to W3 in section 8. The heading text changes at each threshold; because the heading sits in the existing polite live region, the change is announced once per threshold (3 announcements at most). The elapsed line is outside that announcement.

**Warm-up on page load (JS only):** on load the script makes one silent same-origin request to the warm-up route the Architect defines. Nothing is shown while it runs. Only if it returns success, the Ready line (copy W0) appears under the Ask button. If it fails or never returns, nothing is shown: the page does not claim readiness and does not claim a failure. The Ready line is a status of the warm-up call, so the Architect must confirm what "warm" means (loads the index and the embedding model's first run, and **never calls the judge**) before W0 ships; if it cannot be said truthfully, W0 is dropped and the warm-up stays silent.

**What the page cannot show and so does not:** the container start (30.8 s recorded in README, runbook and status file; D5). It is spent before `GET /` is answered, in the browser's own loading state. The scorecard may show a cold-start figure only from a recorded measurement (1.7). The text "The service may be waking up" in today's JS is removed because the page cannot know it.

**Without JS:** the form posts natively; the browser's own loading indicator is the waiting state; nothing is rendered by the page. No warm-up, no Ready line.

### 1.6 Receipts drawer ("How this answer was made"), per D2

A native `<details class="receipts">` with `<summary>`: closed by default, expands **inline** (not an overlay, so no focus trap and no scroll lock at 375 px). Works with no JS and with no ARIA.

Rendered after the passage list on an answer card and after the links on a refusal card; not rendered on error, rate-limit, too-long, empty, paused or service-off cards (the service held nothing about an answer for those).

Contents as a `<dl>` (label then value):

| Label | Answer | Refusal |
|---|---|---|
| Outcome | "The docs answer this" | "The docs don't answer this" |
| Docs version | link "Commit {first 7 hex} on GitHub" (to the pinned docs URL the page already holds) | same |
| Passages listed | count, then an `<ul>` with one `<li>` per passage: link "{path}, lines X to Y" to the passage's permalink | "None. Nothing is listed when the docs don't answer." |

Then a short list of two links: "Read the Charter for this build (the plan approved before it was built)" and "Read the run record". Each is rendered **only if the Architect supplies its URL**; a link with no target is not rendered. All targets are `https://github.com/` URLs (a test pins that every `href` is `/...` or `https://github.com/...`).

Forbidden in the drawer (visitor-facing, any state): the `signal` line, "judge", "verdict", "model said" (a test asserts those three strings are absent from everything after `id="result"` on the could-not-decide page; the drawer is not rendered there, but the same words stay out everywhere to keep the rule simple), the prompt name or hash, any score, any text the request did not already hold. Nothing is stored for the drawer: it re-renders from the result the page already has.

The commit value comes from the page's own docs URL (server-rendered, e.g. in a `data-` attribute or read from the docs link), **not** from `/ask` JSON, whose body must stay byte-identical (C1.4.1).

### 1.7 Scorecard page (new route, path is the Architect's; this spec writes `/scorecard`)

Same frame, header and footer styles; **no `enhance.js`**, no script at all on this page. Server-rendered only, so it works with no JS and nothing needs a fallback.

Top to bottom:

1. `<h1>` "Quality scorecard".
2. Intro paragraph (S2) and a link back "Back to Ask the Aveto docs" (first link in DOM, so it is the first Tab stop).
3. **Figure sections**, each an `<h2>` and a `<dl class="figures">`. Sections, in this order, each rendered only if at least one of its rows has a record:
   - "Speed": Cold start; Warm response time; Cost per question.
   - "Checks": Accessibility checks; Mobile checks (375 px); Tests; Open findings.
   - "Reviews": Independent Codex review.
   - "Who decided what": a list of decisions the record names.
   - "Use since the service last started": Visits; Questions asked; Answered; Not answered; Clicks to the docs (1.8).
4. **"How this was built"**: an unordered list of links (pull request, Charter, event log summary, end review, cost and time, what the owner decided), each rendered only if its URL is known.
5. Footer: the existing issue and docs lines.

**A figure row** (`<div>` inside the `<dl>`): `<dt>` label; `<dd class="value">` the recorded value (text from the figures file, escaped); `<dd class="basis">` how and when it was measured, prefixed "Measured" or "Recorded", plus an optional source link `<a>` "Source". A row is **not rendered at all** when its record is missing: no blank value, no dash, no "n/a", no "coming soon". If no row at all has a record, the page shows only the empty-page text (S5) and the links list. If a whole section has no rows, its `<h2>` is not rendered either.

**Codex review row:** rendered only after the owner has recorded the review. Value is the recorded verdict text; below it, a `<ul class="findings">` of what it found (one `<li>` per recorded finding, text as recorded). If it found nothing the record says so in its own words; the page adds none.

- **375 px:** each row stacks: label, value (larger, tabular), basis (muted). No table, no horizontal scroll.
- **Desktop (min-width 40rem):** each row is a two-column grid: label and basis on the left (`1fr`), value on the right (`auto`, right-aligned, wraps if long). Sections separated by a 1 px `--border` rule.
- Headings: h1, then h2 per section; no heading levels skipped.

### 1.8 Counts without content (on the scorecard page)

Section "Use since the service last started" with the five rows below. The section carries a short note (N1) and, only if the service knows its start time, a line "The service started {YYYY-MM-DD HH:MM} UTC." The counts are totals only: **no question text, no answer text, no per-visitor line, no outcome list beyond the two named, no chart**. A count of `0` is a recorded value and is shown as "0" (the service did measure it); the counts are reset by restart (D1 is out of scope) and the labelling says so on the page.

| Label | Basis text |
|---|---|
| Visits | "Each load of the ask page counts once." |
| Questions asked | "Questions that reached an answer or a refusal." |
| Answered | "The docs answered." |
| Not answered | "The docs did not answer." |
| Clicks to the docs | "Clicks on the docs link from the ask page, counted only when the page's script is running." |

Note on the last row: a click is counted by a same-origin beacon from `enhance.js`, so visitors without JS are not counted; the basis line says so rather than hiding it.

---

## 2. Suggested questions (item 3)

- **Slots:** A1, A2, A3 (the docs answer them) and R1 (the docs do not). The Architect picks the four from the repository's spent evaluation sets, copies the text into a data file inside `aveto_service/` (evals are not in the image), and names the set and ids. **The Architect also confirms each against the unchanged runtime behaviour before release**, because the sentences G2 and G3 say three are answered and one is not.
- **Constraints on the text:** plain text, one question each, at most 90 characters (so at most 3 lines at 375 px), no markup, no personal data, English.
- **Order:** A1, A2, A3, R1. No badge, colour or icon marks R1 (nothing signals the outcome with colour alone; the hint sentence says what to expect).
- **Markup (works with no JS):** each suggestion is its own tiny `<form method="post" action="/ask#result">` holding one `<input type="hidden" name="question" value="{text}">` and one `<button type="submit" class="chip">{text}</button>`. A separate form per suggestion is deliberate: putting `name=question` on a button inside `#ask-form` would send two `question` fields with the textarea's, and `app.py` would treat that as a bad request. The server receives exactly one `question` field.
- **With JS:** `enhance.js` listens on the suggestions container; on submit of any suggestion form it calls `preventDefault`, writes the text into the textarea, updates the count, moves focus to the textarea and sets the status line (W5). It does **not** send. The visitor then presses Ask (or Ctrl/Cmd+Enter, existing). This is the keyboard path Bar 4 checks (load a suggestion, submit).
- **Without JS:** pressing a suggestion asks it straight away (that is what its hint sentence says, G2).
- **Refusal card** repeats A1 to A3 only. Those forms carry no `id`, so no duplicate-id issue.

## 3. States per view

Legend: V = visible treatment; K = keyboard/focus; the copy ids are in section 8.

### 3.1 Ask page

| State | Trigger | Visible treatment | Focus and announcement |
|---|---|---|---|
| Empty (first visit) | `GET /` | Intro, expectations, suggestions, empty form, empty `#result` (a plain `section`, no ARIA name; see 6.1) | Focus starts at the document; first Tab is the skip link |
| Ready (warm-up done) | warm-up call returned OK (JS) | Muted line W0 under Ask | Not announced (decoration) |
| Waiting | submit with JS | Section 1.5 | Heading change announced at 0 s, 8 s, 60 s; Ask is `aria-disabled`; focus stays on Ask |
| Answer | `outcome: answer` | Section 1.2 | JS: focus moves to `#result` (existing); heading read. No-JS: browser follows 303 to `/result/{token}#result`, jumping to the region |
| Refusal | `no_confident_match` | Section 1.3 | Same as Answer; no alert role |
| Resting | `paused` | Section 1.4 | Same as Answer; no alert role (pinned) |
| Service off | `service_off` (kill switch) | `state-note` calm card, copy unchanged; **keeps `role="alert"`** (pinned by `test_service_off_state_on_get_and_post`); form rendered as today (not disabled) | Heading announced assertively (existing) |
| Could not decide | `judge_error` | `state-error` card, unchanged copy, h2 `role="alert"` (pinned) | Alert announced; focus to `#result` |
| Question limit | `rate_limited` | `state-error`, unchanged copy; question stays in the box (pinned) | As above |
| Too long / empty | field errors | Unchanged: `state-error` card, `aria-invalid`, text under the field; focus returns to the textarea | Unchanged |
| Network error (JS) | fetch failed | `state-error`, copy unchanged ("We couldn't reach the service") | As above |
| Copy link result | Copy link pressed | Button text "Copied" for 2 s, then back to "Copy link"; status line C2 | Status line is the page's existing `#q-status` `role="status"` region, so no new live region is added; failure uses C3 |
| Unknown result token | `GET /result/{bad}` | Empty page (unchanged; pinned) | none |

No state introduces a new colour pair that is not in section 6.4. Errors stay red with the "!" icon; calm outcomes (refusal, resting, waiting, service off) share one blue-ruled style, so "error" is always visually different from "the service is behaving as designed".

### 3.2 Scorecard

| State | Treatment |
|---|---|
| Some records | Sections 1.7 and 1.8; rows only where a record exists |
| No records at all | h1, intro, empty text S5, links list; no section headings |
| Figures could not be read | Single card (`state-note`) with S6 and the back link; the Architect chooses the HTTP status. No partial rows. |
| Counts unavailable | The "Use since the service last started" section is not rendered |

## 4. Interactions

- **Focus order, ask page (default, no result):** skip link, suggestions A1 to A3, R1, textarea, Ask, (nothing in the empty result region), footer issue link, footer docs link, footer scorecard link. After a result: ... Ask, then `#result` is programmatically focused (existing, `tabindex="-1"`); Tab then goes to, per passage, source chip, Copy link, passage `pre` (focusable, so it can be scrolled by keyboard), then the receipts `summary`, then footer.
- **Focus order, resting at load:** skip link, docs link in the card, issue link in the card, footer links. The disabled textarea and button are out of the order by design.
- **Focus order, scorecard:** back link, any links in "How this was built", footer links.
- **Keyboard:** Enter/Space on the suggestion buttons, Copy link, receipts `summary` (native). Ctrl/Cmd+Enter in the textarea sends (existing). `Esc` does nothing special (the drawer is inline, not modal, so there is nothing to escape). No keyboard trap anywhere.
- **Focus indicator:** existing 3 px `--focus` outline with 2 px offset; extend the selector list to `summary`, `.chip`, `button`. Never `outline: none` without a replacement.
- **After a suggestion is loaded (JS):** focus moves to the textarea; status W5 is spoken. After Copy link: focus stays on the button.
- **Motion:** none required. The only transition allowed is a 120 ms colour change on hover/focus inside `@media (prefers-reduced-motion: no-preference)`. The CSS keeps a `prefers-reduced-motion` block because `test_static_files_and_types` asserts the string is present. The pulsing dot and its keyframes are removed.
- **Hover/active:** chips and buttons darken by one step; no movement.

## 5. Without JS (parity table)

| Feature | With JS | Without JS (server-rendered) |
|---|---|---|
| Ask | fetch to `/ask`, result in place | form POST, 303 to `/result/{token}#result` (existing) |
| Answer card, refusal card, resting, errors, receipts | built as in section 1 | same markup from `render.py`; `<details>` needs no script |
| Suggestions | fill the box, do not send | each one asks straight away (own form); hint text G2 says so |
| Copy link | button un-hidden if `navigator.clipboard` exists | button is rendered with `hidden`; **not shown** (a button that does nothing is worse than none); the source chip is the fallback |
| Waiting display, elapsed line, Ready line | yes | not available; the browser's own loading indicator |
| Docs-click count | beacon | not counted (stated in the basis line) |
| Resting at page load | same | same (server-rendered) |
| Scorecard | n/a (no script) | identical |

**One renderer is recommended** (decision for the Architect, stage 3): today `render.py` and `enhance.js` both build every card, so every card is specified, tested and audited twice, and a new card means two places where "no model text" and the accessibility rules must hold. Preferred: a new same-origin route that returns the server-rendered fragment for a result, and `enhance.js` only swaps it in. If the Architect keeps two builders, the markup in section 1 is the contract for both and the test that proves "answer card text is in a listed source" must run against both. Whichever route is chosen, `POST /ask` JSON bodies stay byte-identical (C1.4.1).

## 6. Accessibility, contrast, size, security of markup

### 6.1 The existing serious violation, `aria-prohibited-attr` (cause and fix)

Baseline (setup dry run C6.9): axe 4.10.2 on `GET /`: one serious violation, `aria-prohibited-attr`, one node. **Cause, read from `render.py` `result_region()` (not run):** on a page with no result the markup is

`<section id="result" tabindex="-1" aria-labelledby="result-title">`

and no element with `id="result-title"` exists (the heading is only emitted when there is a result; the existing test even asserts `'id="result-title"' not in text`). A `section` whose `aria-labelledby` resolves to nothing has no accessible name, so it has no landmark role and is a generic element, and `aria-labelledby` is prohibited on a generic role. No other element on the initial page fits: the `aria-live`, `aria-atomic`, `aria-describedby`, `aria-hidden` and `role="status"` uses are global attributes or valid on their roles, and the `pre` (role region) and `article` carry their names legitimately. Confidence: high by reading, not confirmed by a run; **stage 8 re-runs axe on all five views and, if the reported node differs, fixes that node instead** and records it.

**Fix (specified, applies to server markup and `enhance.js` equally):**
1. `result_region()` emits `aria-labelledby="result-title"` **only when the heading with that id is inside the section**. With no result: `<section id="result" tabindex="-1">` (no ARIA attribute). With a result: unchanged from today.
2. `enhance.js` `clear()` removes `aria-labelledby` from `#result` and `box()` sets it when it inserts the h2; so the attribute is present exactly when the target exists, on every path, including the waiting card.
3. General rule for every new element in this slice: `aria-label` or `aria-labelledby` only on an element that has a role that allows a name (`region` on the passage `pre`, `article`, `section` with a heading, `nav`); never on a bare `div`, `span`, `p`, `dl`, `ul`, `li`. Do not use ARIA where a native element or a visually-hidden text does the job (Copy link uses visually-hidden text, not `aria-label`).

Test impact: `test_initial_page_has_empty_region_and_form` asserts the exact string `<section id="result" tabindex="-1" aria-labelledby="result-title">`. That assertion must be **changed deliberately** to `<section id="result" tabindex="-1">` (and a new assertion added that the attribute is present when a result is shown). Not weakened: it pins the corrected markup.

### 6.2 Landmarks, headings, names

`<main>` wraps content (existing); `<footer>` exists. h1 once per page; h2 for card titles and scorecard sections; h3 for passage paths and the refusal's "Questions the docs do answer". The existing `h2.plain` "What to expect" stays. Every control has a visible text label; Copy link's visually-hidden suffix makes each of the N buttons uniquely named (WCAG 2.5.3: the visible text "Copy link" is the start of the accessible name). Links are underlined and distinguishable without colour (existing `a` rule). The skip link target `#q` is the textarea itself.

### 6.3 Target size and 375 px

All buttons and chips: min-height 44 px (WCAG 2.2 AA needs 24; the bar C1.4.4 is 24). Footer links get `padding-block: 0.5rem` and `display: inline-block`. Inline links in a sentence are exempt. At 375 and 320 px: no `min-width` wider than the viewport, `overflow-wrap: anywhere` on `code`, `.figures` and chip text, `pre` scrolls inside itself.

### 6.4 Colour and contrast (existing variables reused; one change)

Pairs checked by arithmetic, to be re-measured by axe in stage 8:

| Use | Light | Dark | Ratio (approx.) |
|---|---|---|---|
| Body text on page | `#1a1a1a` on `#ffffff` | `#ececec` on `#121212` | 17:1 / 15:1 |
| Muted text on page or card | `#4a4a4a` on `#ffffff` or `#f4f5f7` | `#b8b8b8` on `#121212` or `#1e1e1e` | 8:1 / 9:1 |
| Link on page or card | `#0b57d0` on `#ffffff` / `#f4f5f7` | `#8ab4f8` on `#121212` / `#1e1e1e` | 6.6:1 / 5.9:1 / 9:1 / 8:1 |
| Primary button | `#ffffff` on `#0b57d0` | `#121212` on `#8ab4f8` | 6.6:1 / 9:1 |
| Secondary button and chip text | `--link` on `--bg` or `--surface` | same | as links |
| Error card | `#a50e0e` on `#fdecea` | `#ffb4ab` on `#3b1412` | existing, unchanged |

**One change:** `.state-note` (today amber `#5c3d00` on `#fff4ce`, which reads as a warning) becomes the calm notice style: `--text` on `--surface`, 4 px left rule in `--link`. It is used by refusal, resting, waiting and service off. The amber variables `--note-fg` and `--note-bg` are no longer used and are removed. Meaning is never carried by colour alone: every card has a distinct h2 title.

`forced-colors: active`: keep the existing block; add `summary`, `.chip` to the border rules; the left rules use `CanvasText`.

### 6.5 Content security (CSP `'self'`, unchanged)

No third-party script, font, image, analytics or iframe. No inline `<style>`, no `style=` attribute, no inline handlers (tests forbid these). No `url()` or `@import` in CSS; no `://`, `cookie`, `localStorage` or `sessionStorage` in `enhance.js` or the CSS (tests forbid these strings: build URLs from `href` values already in the page, not from literals). **One script tag only**: `raw.count("<script") == 1` is pinned, and `<script src="/static/enhance.js" defer></script>` and the single stylesheet link are the only ones allowed. So the beacon, warm-up, suggestions, copy and waiting code all live in `enhance.js`, and the scorecard page carries the stylesheet only. The `hidden` attribute is allowed (not a style attribute).

All dynamic strings are escaped (`html.escape`) in Python and set with `textContent` in JS (as today). The suggestions' `value="..."` attribute is escaped like any attribute.

## 7. Item map (intent items to this spec)

| Intent item | Where |
|---|---|
| 1 Answer card | 1.2 |
| 2 Refusal card (D1) | 1.3 |
| 3 Suggested questions | 2 |
| 4 Honest waiting | 1.5 |
| 5 Resting state | 1.4 |
| 6 Receipts drawer (D2) | 1.6 |
| 7 Scorecard | 1.7 |
| 8 Counts without content | 1.8 |

---

## 8. Copy deck (every new visitor-facing string, final)

`{x}` marks a value filled from a listed passage, the page's own data or a recorded figure; nothing else varies. "JS" = built or changed by `enhance.js` only. Strings the Architect supplies from data (the four questions, figure values and their basis text, finding text, link targets) are data, not copy; their constraints are in sections 2 and 1.7.

### Ask page

| Id | Element | Copy |
|---|---|---|
| K1 | Skip link | Skip to the question box |
| G1 | Suggestions heading (`h2.plain`) | Try a question |
| G2 | Suggestions hint, server (no JS) | Choose one to ask it straight away. Three are answered in the docs and one is not, so you can see both outcomes. |
| G3 | Suggestions hint, replaces G2 when JS runs | Choose one to put it in the box, then press Ask. Three are answered in the docs and one is not, so you can see both outcomes. |
| W5 | Status after a suggestion is loaded (JS, `#q-status`) | Question loaded. Press Ask to send it. |
| W0 | Ready line (JS, only after the warm-up returns OK) | Ready to search the docs. |
| F3 | Footer scorecard link | See the quality scorecard |

### Waiting (JS)

| Id | Element | Copy |
|---|---|---|
| W1 | 0 s, title | Looking through the docs |
| W1 | 0 s, body | Your question has been sent. This usually takes a few seconds. |
| W2 | 8 s, title | Still working |
| W2 | 8 s, body | This is taking longer than usual. It can take up to a minute. Please keep this page open. |
| W3 | 60 s, title | Still waiting |
| W3 | 60 s, body | This is taking more than a minute. You can keep waiting. If nothing changes, reload the page and ask again. |
| W4 | Elapsed line (not announced) | Waiting: {N} seconds (singular: Waiting: 1 second) |

The Ask button text while busy stays "Asking..." (existing). Removed strings: "The service may be waking up. This can take up to a minute. Please keep this page open." and "This usually takes a few seconds." as a stand-alone line (replaced by W1/W2).

### Answer card

| Id | Element | Copy |
|---|---|---|
| (unchanged) | Title, count | The docs answer this / Found {n} passage. / Found {n} passages. |
| (unchanged) | Source chip | View {line or lines X to Y} of {path} on GitHub |
| A1 | Quote caption | Quoted from the docs, word for word |
| A2 | Copy button (visible) + hidden suffix | Copy link + (visually hidden) " to {path}, {line or lines X to Y}" |
| A3 | Copy button after success, 2 s | Copied |
| C2 | Status after success (`#q-status`, JS) | Link copied. |
| C3 | Status after failure (JS) | Couldn't copy the link. Use the source link instead. |

### Refusal card

| Id | Element | Copy |
|---|---|---|
| (unchanged) | Title | The docs don't answer this |
| (unchanged) | Body | No confident match was found, so nothing is shown. You can change your question and ask again, or open a GitHub issue. |
| F1 | Rephrasing hint | Rephrasing can help: name the command, setting or feature you mean, and ask about one thing at a time. |
| (unchanged) | Links | Open a GitHub issue / Read the docs on GitHub |
| F2 | Suggestions heading (`h3`) | Questions the docs do answer |

### Resting state

| Id | Element | Copy |
|---|---|---|
| (unchanged) | Title | Paused for today |
| (unchanged) | Body | Ask the Docs has a daily limit and today's has been used. This is not a fault. You can read the docs on GitHub or open an issue. |
| R1 | New paragraph after the body | Ask the Docs is back after midnight UTC. |
| R3 | Replaces the field hint when the form is disabled at load | Questions open again after midnight UTC. |
| (unchanged) | Links | Open a GitHub issue / Read the docs on GitHub |

### Receipts drawer

| Id | Element | Copy |
|---|---|---|
| D1 | Summary on an answer | How this answer was made |
| D2 | Summary on a refusal | How this result was made |
| D3 | Row labels | Outcome / Docs version / Passages listed |
| D4 | Docs version value (link) | Commit {7 hex} on GitHub |
| D5 | Passages listed on a refusal | None. Nothing is listed when the docs don't answer. |
| D6 | Passage list item (link) | {path}, {line X or lines X to Y} |
| D7 | Charter link (only if a URL is supplied) | Read the Charter for this build (the plan approved before it was built) |
| D8 | Run record link (only if a URL is supplied) | Read the run record |

The Outcome value reuses the two existing titles (unchanged strings).

### Scorecard page

| Id | Element | Copy |
|---|---|---|
| S0 | Document title | Quality scorecard - Ask the Aveto docs |
| S1 | h1 | Quality scorecard |
| S3 | Back link | Back to Ask the Aveto docs |
| S2 | Intro | Figures recorded while this service was built and released. A figure is shown only when a record sits behind it, with how and when it was measured. |
| S4 | Section headings | Speed / Checks / Reviews / Who decided what / Use since the service last started / How this was built |
| S7 | Row labels, shown only with a record | Cold start / Warm response time / Cost per question / Accessibility checks / Mobile checks (375 px) / Tests / Open findings / Independent Codex review |
| S8 | Codex findings sub-heading (`h3`, only if findings are recorded) | What it found |
| S9 | Basis prefix; source link | Measured {when and how} or Recorded {when and how}; Source |
| S5 | No record at all | No figures have been recorded yet. |
| S6 | Figures unreadable | The scorecard can't be shown right now. Please try again later. |
| B1 | Build links, each only if a URL is supplied | The pull request / The Charter / The event log summary / The end review / Cost and time / What the owner decided |
| N1 | Counts note | These are totals since the service last started. They go back to zero each time it restarts, so they are not lifetime totals. This page lists totals only; it shows no question and no answer. |
| N2 | Start line, only if the start time is known | The service started {YYYY-MM-DD HH:MM} UTC. |
| N3 | Count labels and basis | Visits - Each load of the ask page counts once. / Questions asked - Questions that reached an answer or a refusal. / Answered - The docs answered. / Not answered - The docs did not answer. / Clicks to the docs - Clicks on the docs link from the ask page, counted only when the page's script is running. |

C1.6 check: no string above makes a claim about privacy, data handling, law or AI beyond the live page. The five phrases nearest the line, for the owner's eye in `END_REVIEW.md`: W1 "Your question has been sent" (states the action, not where it goes), N1 (describes the counters and what the page lists), N3 last row (limits of a count), A1 (the existing "copied word for word" claim, restated), G2/G3 "Three are answered in the docs and one is not" (a statement about the docs, true only if the Architect checks it).

## 9. Existing strings and markup the tests pin (do not change; "update" means a deliberate test edit)

All in `tests/test_service_pages.py` unless stated.

| Pinned item | Test | Consequence |
|---|---|---|
| Disclosure sentences (intro; "Please don't put personal..."; "This service does not store or log your question..."; "To apply the limits we read your address..."; "Limits: 10 questions an hour..."; "The docs are in English...") word for word | `test_disclosure_copy_is_verbatim` | **Byte-identical (C1.6).** Keep the `<ul>` items and order. |
| `<form id="ask-form" method="post" action="/ask#result">`, `<title>Ask the Aveto docs</title>`, `<html lang="en">` | `test_initial_page_has_empty_region_and_form` | keep |
| `<section id="result" tabindex="-1" aria-labelledby="result-title">` on the **empty** page | same | **update to `<section id="result" tabindex="-1">`** (6.1); assert `'id="result-title"' not in text` stays |
| "The docs answer this", `Found \d+ passages?\.`, `class="state state-answer"` | `test_answer_state` | keep |
| Refusal title and body sentence, `>Open a GitHub issue</a>`, no `class="passages"` | `test_no_confident_match_state` | keep; hint F1 is a separate paragraph |
| `<h2 id="result-title" role="alert">We couldn't decide this time</h2>`, its body, and no "judge", "verdict", "model said" anywhere after `id="result"` | `test_could_not_decide_state` | keep; **no new string after `id="result"` may contain those three words** (footer F3, receipts) |
| Rate-limit title, body, `>{QUESTION}</textarea>` | `test_rate_limited_state_keeps_the_question` | keep |
| Paused title, body, `Read the docs on GitHub` exactly 2 times, no `role="alert"` after `id="result"`, `class="state state-note"` | `test_paused_state` | keep; R1 is added; no third docs link |
| Too-long copy, `id="q-error" class="error">Questions can be up to 500 characters.`, `aria-invalid="true"`, "1 characters over the limit of 500. Shorten your question." | `test_too_long_state_names_the_count` | keep |
| Empty-question copy and field message | `test_empty_question_state` | keep |
| Service-off title, body, `role="alert"` on GET and POST | `test_service_off_state_on_get_and_post` | keep (the card turns calm in colour but keeps its alert role) |
| `<code>{passage text}</code></pre>`, `<code>{path}</code>`, `m.url`, "Lines X to Y" / "Line X", "Found N passage" | `test_passages_byte_identical_inside_the_page`, `test_markup_bearing_passage_is_escaped` | keep the `pre > code` and `h3 > code` structure |
| Question not in any URL; Location `/result/{token}#result` | `test_question_is_in_no_url_or_location` | keep; suggestion `value` attributes are fixed public text, but must not appear as `href`, `src` or `action` |
| Two GETs of one result page are byte-equal; textarea present, question absent | `test_prg_reload_does_not_re_ask` | **The result page HTML must not contain anything that varies between two GETs** (no counts, times, nonces) |
| Every `src`/`href`/`action` starts with `/` or `https://github.com/`; only the one stylesheet link and one `<script src="/static/enhance.js" defer></script>`; no `<style`, ` style=`, ` onclick=` | `test_no_external_origin_in_page_or_static` | keep; the scorecard link is `/scorecard` (or the Architect's path), receipts links are GitHub |
| `raw.count("<script") == 1` | `test_markup_question_is_escaped_when_echoed` | one script tag only |
| CSS/JS contain no `://`, `cookie`, `localStorage`, `sessionStorage`, `@import`, `url(` | same | keep; CSS keeps `prefers-color-scheme: dark` and `prefers-reduced-motion` (`test_static_files_and_types`) |
| `STATIC_TYPES` allows only `enhance.js` and `style.css` | `pages.py`, `test_static_files_and_types` | this spec adds no static file |
| Security headers and CSP parts on every response | `test_security_headers_on_every_page_response` | unchanged (C5.0); the scorecard response carries the same dict |

## 10. Component reuse map

Checked against `render.py`, `style.css`, `enhance.js`, `pages.py`. The page has no component library; the "components" are Python functions and CSS classes.

| Component | Decision | Notes |
|---|---|---|
| `StateCopy`, `STATES`, `copy_for`, `too_long_copy` | reuse, extend | Add the R1 paragraph to `paused` and the F1 hint to `no_confident_match` (new optional fields). No existing string changes. |
| `_links()` | reuse | Refusal card switches to both links (`links=True`-like); resting unchanged. |
| `_passages()` | extend | Add action row (chip class on the existing link, Copy link button, caption A1); keep `article`, `h3`, `meta`, `pre` markup. |
| `result_region()` | extend | Conditional `aria-labelledby` (6.1); append the receipts drawer; refusal's suggestions. |
| `page_html()` | extend | Skip link, suggestions block, Ready line, scorecard footer link, disabled-form variant for resting at load. The disclosure block is untouched. |
| Receipts drawer, suggestions block, scorecard page, figure row, counts section | new | No equivalent exists. The scorecard is a second small page function beside `page_html` sharing the frame. |
| `.state`, `.state-answer`, `.state-error` | reuse | Unchanged look. |
| `.state-note` | extend (restyle) | Calm blue-ruled card; amber variables removed. |
| `.visually-hidden`, `.meta`, `pre.passage`, `.passages`, `article`, `.links` | reuse | `pre.passage` gains the quotation rule; `article` heavier border for the answer view. |
| `button` | reuse | Primary style kept for Ask. |
| `.chip` (source chip, suggestion buttons, link pills), `.secondary` button, `details.receipts`, `.skip`, `dl.figures`, `.value`, `.basis`, `.ready` | new CSS | All plain CSS; no image, font or `url()`. |
| `.dots`, `.dot`, `@keyframes pulse` | remove | Fake-progress indicator (1.5). |
| `enhance.js`: `el`, `link`, `chars`, `lines`, `lowerLines`, `box`, `showState`, `showAnswer`, `settle`, `update`, `fieldError` | reuse | Keep names and behaviour. |
| `enhance.js`: `STATES` table | extend | Add F1 and R1 text to the two entries (or remove if the Architect adopts the fragment route, section 5). |
| `enhance.js`: `showWaiting` | replace | Elapsed timer, three thresholds, no animation. |
| `enhance.js`: warm-up call, suggestion handler, copy handler, docs-click beacon, `aria-labelledby` set and clear | new | Same file; no new script (6.5). |
| `HtmlPages` and `SECURITY_HEADERS` | reuse | New pages go through the same header dict. |

## 11. Open items for the Architect (stage 3) and the owner

| # | Item | Owner of the answer |
|---|---|---|
| O1 | The "What to expect" privacy list stays above the form, as today, because the data notice should be read before sending. On a 375 px phone it pushes the form down about a screen. Collapsing it would change how the owner-approved wording is shown; not done here. Owner may say. | Owner |
| O2 | One renderer (fragment route) versus two builders (section 5). | Architect |
| O3 | What "warm" does, and whether W0 can be said truthfully; the warm-up route must never reach the judge (INV-4). | Architect |
| O4 | `GET /` must read the spend state to render the resting card at load (scope doc, `app.py`). Route path for the scorecard. Whether counts and the scorecard are public (scope doc section 5; D3 on `/health` is still open with the owner). | Architect, Security |
| O5 | The four questions (A1 to A3, R1), checked against unchanged behaviour; data file inside `aveto_service/`. | Architect |
| O6 | Link targets for Charter and run record: a ref that exists only after the pull request opens. Links render only when a URL is supplied and may 404 until the branch is pushed; the page must not render a link it cannot resolve. | Architect |
| O7 | The commit value for the drawer comes from the page, not `/ask` JSON. | Architect |
| O8 | The docs-click beacon: same-origin, no body text, size cap and rate limit (scope doc section 5). | Architect, Security |
| O9 | Copy W2 "up to a minute" is carried over from today's page; if the Charter's measured warm timings show a different bound, W2 follows the record. | Architect |
| O10 | How stage 8 reaches the resting state locally (fake service in the scratch server, not a product flag). | Orchestrator |

## 12. Checklist against the quality bar

- Every state in the intent has a layout note: answer, refusal, suggestions, waiting, resting, receipts, scorecard, counts (section 1); errors and field states (3.1); scorecard empty and unreadable (3.2).
- Copy is final in section 8; the four suggested questions are data supplied by the Architect, with constraints.
- Reuse is checked against the real files (section 10).
- Calm outcomes and errors are visually distinct; refusal and resting are not styled as errors; errors keep their alert role and red.
- Not in this spec: data model, routes, figure file format, the choice of questions, visual polish beyond the journey.

## Hand off

Next agent: Software Architect (stage 3). Artefact to produce: tech spec (`04-tech-spec.md`). Read this file, `01-scope.md`, `DECISIONS.md` and the baseline axe finding in section 6.1.


