# Stage 4 — browser checks (Orchestrator, 2026-10-27, local, built-in browser)

Tree: `aaf7bc1` (product change `cbbedfd`). Same method as the before figures in `00-setup-dryruns.md`: `devserver.py` with the stand-in judge (no model called), real Ask button (or Ctrl+Enter), 3.5 s wait, `#result-title` top in CSS px, `document.activeElement.id`. A scratch copy of the dev server in the session scratchpad served `axe-core` 4.10.2 at `/__axe.js` (same origin; the repo, lockfile and image are untouched).

## C1.4 item 1 — heading position (bar: 0 ≤ top ≤ 25% of the viewport)
| Viewport | Question | Before (main) | After | Share of viewport | Focus | Verdict |
|---|---|---|---|---|---|---|
| 1280×800 | answered | −2,820.9 | **16.1** | 2.0% | `#result` | pass |
| 1280×800 | refused | 292.1 | **16.1** | 2.0% | `#result` | pass |
| 375×667 | answered | −4,182.9 | **15.6** | 2.3% | `#result` | pass |
| 375×667 | refused | −2.9 | **15.6** | 2.3% | `#result` | pass |
Also: the server-rendered result URLs (`POST /ask` then `/result/<token>#result`, loaded with JavaScript on): answered 18.1, refused 16.1 at 1280×800. `scrollBehavior` computed `auto` (no animation). Page width at 375 px: scrollWidth 375 (no sideways scrolling) on the swapped answer and refusal.
The intent's live figure was 616 of 800 for a short real answer; the stand-in's answer is long (6,463 px), which is why the before figure is off screen. The live figure after the deploy is stage 10's.

## Order (C1.4 item 2) — DOM children of `<main>`
- Home: `H1,P,H2(What to expect),UL,H2(Try a question),sugg-hint,suggestions,ask-form,ready,result` (unchanged).
- After Ask (JavaScript swap) and on the server-rendered result page: `H1,P,ask-form,ready,result,H2,UL,H2,sugg-hint,suggestions`.
- Resting view: `H1,P,H2,UL,result,ask-form` (unchanged: result above the disabled form, no suggestions).
- No CSS reorders content (`order`, reversed flex, fixed or sticky positions: none apart from the skip link and visually-hidden text), so reading order equals visual order.

## C1.4 item 6 — axe-core 4.10.2 (tags wcag2a, wcag2aa, wcag21aa, wcag22aa), 1280×800
| View | Serious or critical | Any violation | Incomplete |
|---|---|---|---|
| Home `GET /` | 0 | 0 | color-contrast on `#q` |
| Answer (server-rendered result page) | 0 | 0 | color-contrast (1 node) |
| Answer (after the JavaScript swap) | 0 | 0 | color-contrast on `#q` |
| Refusal (server-rendered) | 0 | 0 | color-contrast on `#q` |
| Resting (`--resting`) | 0 | 0 | none |
The `#q` incomplete is the textarea: computed text rgb(26,26,26) on rgb(255,255,255), ratio 17.4 (4.5 needed). Not checked: dark colour scheme, hover states.
**Keyboard only (real key events):** focus on the first suggestion, Enter loads the question into the box, Ctrl+Enter sends; focus is on `#result` with the heading at 16.1 px; the next Tab lands on the first source link inside the result, `:focus-visible` true, 3 px outline; no trap seen. Not tested here: the receipts drawer and copy-link, a screen reader, Tab out of the page, and the no-JavaScript flow (the pane cannot turn JavaScript off; the server-rendered result page was loaded with JavaScript on).
**Not measured:** the heading's offset with JavaScript off, a short error box at 1280×800 (the page may end below it), reduced-motion emulation (the script never animates; `scroll-behavior` is `auto`).
