# UX spec: public-ask-the-docs (stage 4, UI Designer, depth standard)

> **Amendment 2026-10-21 (smoke depth).** Only section 2 copy changed; states, layout and all other copy are unchanged.
> - Header statement now says "an AI model" (06 R1 / T2; 07 G1 item 1).
> - Anthropic is named as the recipient of the question and passages, handled under its own terms (06 R1 / T1; 07 G1 item 3).
> - New bullet: no personal or confidential information in a question (06 R1 / T3; 07 G1 item 2).
> - "not stored or logged" is now "This service does not store or log your question" (07 section 6 item 3; G5 keeps it true for this service only).
> - Retention kept and widened because 07 section 6 items 4 and 5 require them (G1): the address is read to apply the limits, kept 7 days as a scrambled form; the service runs in the US. 07 item 6 (short privacy notice link) is not added: whether a notice is due is the owner's legal call (07 G8); the issue link already exists.
> - Wording is mine; facts are 07's. No legal conclusion is stated on the page.

Sources: `03-feature-spec.md` sections 2, 6, 7; `02-prd.md` section 5; `intent.md` "A public page". Plain HTML and CSS written by hand, one stylesheet inlined or served by the service, no CDN, no web fonts, no tracking. No component library exists for this page (new service); everything below is new and small. Feasibility of the no-JS path and the Back/reload rule is the Architect's to confirm (see Open items).

## 1. Delivery model (binds the layout)

- The form is a real `<form method="post" action="/ask#result">`. Works with JavaScript off: the server answers with the full page and the matching state rendered. The question travels in the POST body only, never in a URL, title or storage.
- JavaScript enhances: it intercepts submit, calls the same endpoint, swaps the result region, shows the waiting state, and keeps the typed text. Without JS the browser's own page load is the waiting state, and states H and E are caught by the server and rendered in the same markup.
- A `<noscript>` line is not needed because asking works without JS. Do not add one.

## 2. Page layout (one column, max width 42rem, centred, 1rem side padding)

Top to bottom, one `<main>`; reading order equals tab order.

1. `<h1>` "Ask the Aveto docs"
2. Statement `<p>`: "Verbatim passages from Aveto's docs; an AI model decides only whether they answer. Nothing on this page is written by an AI model."
3. `<ul>` "What to expect":
   - "You get passages copied word for word from the docs, with the file and line numbers, or a plain note that the docs don't answer your question."
   - "Limits: 10 questions an hour and 500 characters a question. The service pauses for the day when the day's allowance is used."
   - "Please don't put personal or confidential information in your question."
   - "This service does not store or log your question. To decide whether the passages answer, your question and the passages found are sent to Anthropic, the company that makes the AI model. Anthropic handles them under its own terms, which this page does not control."
   - "To apply the limits we read your address, then keep only a scrambled form of it, the time and the outcome for 7 days. The service runs in the United States (Azure, East US 2)."
   - "The docs are in English. One question at a time; nothing is remembered between questions."
4. The form (section 3).
5. `<section id="result">` result region (section 4), always in the DOM, empty at first.
6. `<footer>`: link "Open a GitHub issue" (generic, section 5) and link "Read the docs on GitHub" (pinned commit root).

No tooltips carry required information; no placeholder carries a label.

## 3. The form

- `<label for="q">Your question about Aveto</label>`, visible, above the field.
- `<textarea id="q" name="question" rows="4" autocomplete="off" spellcheck="true" aria-describedby="q-hint q-count q-error">`. Multi-line, so Enter adds a line; submit is by the button, or Ctrl/Cmd+Enter (JS only, stated in the hint). No `maxlength` attribute (a paste past 500 must be seen and named, not silently cut).
- `<p id="q-hint">Up to 500 characters. Press Ctrl+Enter or Cmd+Enter to send.</p>` (the second sentence is added by JS only).
- `<p id="q-count">0 of 500 characters</p>`: visible, updated on input. Counts characters as the visitor sees them (code points, grapheme-aware where `Intl.Segmenter` exists). Not a live region; a separate visually-hidden `role="status"` node announces only at 450 ("50 characters left") and at 501 ("Over the limit by N characters"), and again only when crossing back.
- Over 500 while typing: the count turns to error style with text "N characters over the limit of 500. Shorten your question." Submit stays enabled and the refusal is the rule below (never disabled-grey buttons that hide why).
- `<button type="submit">Ask</button>`, minimum 44 by 44 CSS px, full width at 320 px.
- The textarea is never cleared by the page after any state.

## 4. States and exact copy

The result region is `<section id="result" tabindex="-1" aria-labelledby="result-title">`. Each state sets `result-title` (an `<h2>`) and a body. A state also sets a class (`state-answer`, `state-note`, `state-error`) and a text prefix so colour is never alone. Visitor text never contains "judge", "verdict", "model said", or error codes.

| State | `<h2>` (exact) | Body (exact) | Announce |
|---|---|---|---|
| Initial | (region empty) | (empty) | none |
| Waiting, normal | "Looking through the docs" | "This usually takes a few seconds." | polite, once |
| Waiting, long (after 8 s) | "Still working" | "The service may be waking up. This can take up to a minute. Please keep this page open." | polite, once |
| Answer shown | "The docs answer this" + (1 passage) "Found 1 passage." / (n) "Found n passages." | Passage list (section 5) | polite, heading text only |
| No confident match | "The docs don't answer this" | "No confident match was found, so nothing is shown. You can change your question and ask again, or open a GitHub issue." + link "Open a GitHub issue" | polite |
| Could not decide | "We couldn't decide this time" | "Something went wrong while checking the passages, so none are shown. Please try again." | assertive (role="alert") |
| Rate limited | "Question limit reached" | "You can ask 10 questions an hour. Please try again later. Your question is still in the box." | assertive |
| Paused for today | "Paused for today" | "Ask the Docs has a daily limit and today's has been used. This is not a fault. You can read the docs on GitHub or open an issue." + both footer links repeated | polite (it is a known limit, not an error) |
| Question too long | "Your question is too long" | "Questions can be up to 500 characters. Yours is N. Shorten it and ask again. Nothing was sent." | assertive; focus to field |
| Empty question | "Please enter a question" | "Type a question about Aveto, then press Ask. Nothing was sent." | assertive; focus to field |
| Service off | "The service is off" | "Ask the Docs is switched off right now. You can read the docs on GitHub or open an issue." + both links | assertive |
| Network failure (JS only) | "We couldn't reach the service" | "Check your connection and try again. Your question is still in the box." | assertive |

- Over-500 and empty: the message is in the result region and also inline under the field in `<p id="q-error" class="error">` with the same first sentence, so `aria-describedby` ties it to the field and `aria-invalid="true"` is set. Cleared on the next input.
- Prefix glyphs (decorative, `aria-hidden`, plus the words above carry the meaning): answer "Found", note none, error a bold "Error:" is not added; the heading text is the signal, and error states also get a 4px left border in the error colour and a solid (not colour-only) "!" in a circle icon with `aria-hidden="true"`.
- Waiting: while in flight the button gets `aria-disabled="true"` and the label "Asking..."; further activations are ignored (not `disabled`, so focus is not lost). A static text "Looking through the docs" is always present; the indicator is a 12px pulsing dot only under `prefers-reduced-motion: no-preference`, otherwise a static "..." after the heading. At 8 s the wording changes in place (one announcement).
- Approval/safety states: none exist; "Paused for today" and "The service is off" use `state-note` (amber boundary) so they are visibly different from errors.

## 5. Passage rendering (Answer shown)

`<ol class="passages">`, in the order `retrieve` returns files; each passage is `<li><article aria-labelledby="p1-title">`:

1. `<h3 id="p1-title">` is the file path, as text in `<code>`, e.g. `docs/getting-started.md`.
2. Meta line `<p class="meta">`: "Section: " + heading trail joined with " > " (text exactly as returned; if no heading, "Section: (top of file)"), then "Lines 40 to 58" (en words, not a dash; a single line is "Line 40").
3. Link: `<a href="{permalink}">View lines 40 to 58 of docs/getting-started.md on GitHub</a>`; the permalink is the pinned-commit URL with `#L40-L58`. Opens in the same tab (no `target`, no new-tab warning needed).
4. Verbatim text: `<pre class="passage" tabindex="0" role="region" aria-label="Passage text from docs/getting-started.md, lines 40 to 58"><code>...</code></pre>`. HTML-escaped text node only; `white-space: pre-wrap; overflow-wrap: anywhere`, so lines wrap rather than scroll at 320 px and nothing is reflowed into prose; line breaks and indentation are kept exactly. Max height none (never clip); if a long code line still overflows, `overflow-x: auto` on the `pre`, hence `tabindex="0"`.
5. Several best passages from one file are separate cards under the same file heading repeated; each carries its own lines and link. If a file has more than one passage, the `<h3>` is the path and the meta line differentiates them.
6. Nothing else: no scores, no ranking words, no "best", no summary, no generated sentence.

## 6. Focus and live-region rules (one rule for every state)

- JS path: after a result renders, focus moves to `#result` (its `tabindex="-1"`), and the browser scrolls it into view; the `<h2>` is the first thing read. Exception: Empty and Too long, where focus goes to `#q`.
- The live region is the result region's inner wrapper `<div aria-live="polite" aria-atomic="true">`; assertive states use `role="alert"` on the `<h2>`. The wrapper is in the DOM from page load (empty), so changes are announced. Announce the heading only (for answers: "The docs answer this, found 2 passages"), never the passage text.
- Waiting is announced once on entry and once on exit (the result); no repeating status.
- No-JS path: the action's `#result` fragment scrolls to the result; the new page's `<h2>` is reachable immediately after the form in tab order.
- Tab order: skip nothing, hidden-from-view nodes (the status node) are not focusable. Focus ring: 3px solid `--focus` with 2px offset on every control, link and `pre`; never `outline: none`.
- Targets at least 24 px, buttons 44 px. Links are underlined always.

## 7. Over-500 rule

Counted client-side (code points) and server-side (code points, authoritative). Over 500: submit is not blocked on the client; on press the client does not send and shows "Your question is too long" with N, focus to the field. Without JS, the server returns the same state and sends nothing to the model. The text stays in the field in both cases. A very long paste (tens of thousands) is counted without rendering it back in the message beyond N.

## 8. Colours and tokens (CSS custom properties; ratios to be verified in stage 11)

| Token | Light | Dark (`prefers-color-scheme: dark`) | Use / approx. ratio |
|---|---|---|---|
| `--bg` | #ffffff | #121212 | page |
| `--text` | #1a1a1a | #ececec | body, over 15:1 |
| `--muted` | #4a4a4a | #b8b8b8 | meta, hint; over 8:1 |
| `--link` | #0b57d0 | #8ab4f8 | links; over 6:1 |
| `--border` | #767676 | #8a8a8a | field, card edges; at least 3:1 against bg |
| `--surface` | #f4f5f7 | #1e1e1e | passage block; text on it still over 12:1 |
| `--focus` | #0b57d0 | #8ab4f8 | focus ring; 3:1 against bg and surface |
| `--error-fg` / `--error-bg` | #a50e0e / #fdecea | #ffb4ab / #3b1412 | error states; over 7:1 |
| `--note-fg` / `--note-bg` | #5c3d00 / #fff4ce | #ffd88a / #3a2c00 | paused/off; over 8:1 |
| `--ok-border` | #1e6e3a | #7bd194 | answer card 4px left border (decorative; heading carries meaning) |

Type: system stack (`system-ui, sans-serif`; `ui-monospace, Menlo, Consolas, monospace` for paths and passages), base 1rem/1.5, `<h1>` 1.75rem, `<h2>` 1.25rem, `<h3>` 1rem bold, passage 0.9375rem/1.45. Spacing scale 0.25, 0.5, 1, 1.5, 2rem. Set `color-scheme: light dark`. `@media (forced-colors: active)`: borders on cards and the button use `CanvasText`; keep outlines, drop background tints. Reduced motion: no transitions at all (the only motion is the pulsing dot).

## 9. Page meta

`<html lang="en">`, `<title>Ask the Aveto docs</title>` (never changes), `<meta name="viewport" content="width=device-width, initial-scale=1">`, `<meta name="referrer" content="no-referrer">`. Links to GitHub carry `rel="noopener noreferrer"`. No cookies set by the page; no analytics; no external fonts or scripts (a strict CSP is the Architect's).

## 10. Links

- "Open a GitHub issue" opens the repo's new-issue page with a generic title only (`?title=Docs+question+not+answered`), never the visitor's question; text beside it: "Add your question to the issue yourself if you wish." Same tab.
- "Read the docs on GitHub" goes to the docs directory at the pinned commit.

## 11. Component list for the Frontend Developer (all new; no existing components to reuse, checked: this service has no UI)

1. `Layout` (html shell, `main`, `footer`, tokens stylesheet)
2. `IntroBlock` (statement + expectations list)
3. `QuestionForm` (label, textarea, hint, count, error slot, submit)
4. `CharCounter` (visible count + hidden threshold status; JS)
5. `ResultRegion` (live wrapper, `h2`, body, state class; server-rendered and JS-swappable from the same template)
6. `PassageList` and `PassageCard` (section 5)
7. `StateNote` (icon + heading + body variants: answer, note, error)
8. `WaitIndicator` (text plus dot; JS)
9. `Enhance.js` (about 80 lines, no dependencies): submit interception, waiting, long-wait timer at 8 s, focus rule, Ctrl/Cmd+Enter, network-failure state, count thresholds.

## 12. Open items for the Architect

- Back/reload after a no-JS POST: a plain POST response makes the browser offer to resend on reload. Recommend answering the POST with a 303 redirect to a state-less `GET /` plus a one-time result cookie is not allowed (no cookies); so instead render directly from the POST and set `Cache-Control: no-store`; confirm the resend prompt is acceptable or choose a better mechanism (a reload re-asks and spends allowance, contrary to feature spec section 5).
- Whether "Could not decide" counts against the hourly allowance; whether the page loads when the kill switch is on; pause reset time (copy above promises none).
- Server must supply per passage: path, heading trail, line range, permalink, text, and the count.
