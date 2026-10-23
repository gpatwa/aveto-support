# Feature spec: public-ask-the-docs (stage 3, UX Researcher, depth standard)

Sources: `02-prd.md` section 5 and hand-off, `intent.md`, `01-scope.md` section 7, `CHARTER.md` C1.3. Lines marked **(inferred)** are mine. No layout, no final copy (stage 4), no mechanism choice (kill switch, cold start, pause reset belong to the Architect). "Passage card" below means one verbatim passage with its file and line link; how it looks is stage 4's.

## 1. The visitor

**Evaluator.** Someone deciding whether to use Aveto, with one specific question the site does not answer at a glance, who would rather read the source passage than a summary (intent, "Who it's for"). Arrives by a link (the aveto.dev link comes after the run; until then by the Azure address (inferred)). Reads English documentation. Expects a plain page, no sign-in. Wants a verdict in seconds: "does the doc answer this, and where".

Secondary, not designed for separately: **a hostile or curious tester** (injection, off-topic, a request for generated text, "reveal your instructions"). They get the same states as everyone: no passage, no explanation of why (R15). **A keyboard or screen-reader user** is not a persona; section 5 binds every journey.

Not in scope: returning-user history, accounts, multi-turn follow-up (C1.3).

## 2. What the visitor must be told up front

Present on the page before any question is sent, reachable without scrolling past the result (inferred), and not only in a tooltip or placeholder:

1. What it is: verbatim passages from Aveto's docs; a model decides only whether they answer. Nothing on the page is written by a model (R13, INV-4).
2. What they will get: either passages with file and lines, or "The docs don't answer this" (the two outcomes).
3. Limits: 10 questions an hour, 500 characters a question, a daily pause when the day's spend is used (R6, R7, R8). The pause may happen often (PRD O2).
4. Privacy: questions are not stored or logged; a hashed address, a time and an outcome are kept 7 days for abuse control (R12). That the question and the shown passages go to a model provider (Anthropic) to decide answerability, as the data map says (inferred; Charter C4, stage 7 confirms wording).
5. It is a questions-about-Aveto tool, one question at a time, with no history (C1.3) (inferred).

## 3. Primary journey: ask, get passages (state "Answer shown", R2)

| # | Visitor does | System responds |
|---|---|---|
| 1 | Opens the page. | Page loads with the up-front information (section 2), an empty question field with an accessible name, and a submit control. No model call. |
| 2 | Types a question of 1 to 500 characters. | A character count against 500 is available to the visitor and to assistive technology (inferred). Nothing is sent. |
| 3 | Submits by the button or by the keyboard's submit gesture in the field. | The submit control becomes unavailable to a second activation; a waiting state appears (section 6); focus stays where the visitor can reach it. |
| 4 | Waits. | On ANSWERABLE, the waiting state is replaced by the result region: a short statement that passages were found, then each passage verbatim. |
| 5 | Reads the passages. | Each shows its file path, heading and line range, with a link to that file and those lines. No text appears that is not copied from the docs. |
| 6 | Follows a link. | The file opens at the lines on GitHub, in the same or a new tab per stage 4. The visitor's question is not in the URL. |
| 7 | Asks another. | Field and previous result are still present (inferred); a new submit replaces the result. No history is kept. |

How a visitor judges that these are the "right" passages (PRD O6): they judge by reading the passage and following the link to its surrounding text. The page must not claim "best answer" or rank-order confidence; it says only that the docs answer this and shows where (inferred). The number of passages shown is whatever `retrieve` returns; the spec assumes more than one is possible and a long passage must remain readable (section 4, long passages).

## 4. Alternate journeys (one per remaining PRD state)

Common to all: the question is not echoed into a URL, a title or any storage by the page; the field keeps the visitor's own text after a refusal so they can edit it, except where noted (inferred; held in page memory only).

**A. No confident match (R3).** Steps 1 to 3 as above. System: result region says the docs don't answer this, with a link to open a GitHub issue. No passage, no near-miss, no "did you mean". The link opens a new-issue page only; it does not post (INV-1). It must not carry the question text in the URL (inferred, PRD O6); whether the visitor can copy their own question into the issue is theirs to do. The link's pre-filled title, if any, is generic (stage 4/5). The visitor can edit and re-ask at once.

**B. Judge error (R4).** System: result region says it could not be decided, and that trying again may work. No passage, no reason line, no stack trace, no error code the visitor must interpret. Re-submit is possible. This counts against the hourly allowance (inferred; Architect confirms).

**C. Rate limited (R6).** On the 11th question in an hour: result region states the limit (10 an hour) and that trying later works. No model call. The question text stays in the field. Does not say "in N minutes" unless the design fixes it (inferred; same caution as O4).

**D. Paused for today (R7).** Says "Paused for today" and that it is a daily limit, not a fault. No promise of a reset time or time zone unless O4 fixes one. May be seen often; it is a first-class state, not an error (inferred). The visitor is offered the alternative the page already has: the GitHub issues link and the docs themselves (inferred).

**E. Question too long (R8).** The visitor learns before submit when they cross 500 (the count in step 2), and, if they still submit or paste past it, after submit with the limit named. The text is not truncated or sent; it remains in the field so they can shorten it. No model call.

**F. Service off (R9).** Says the service is off. No reason, no timeline (inferred). Still shows the up-front information and the GitHub issues link (inferred). Whether the page itself loads when off is the Architect's O1; if the service answers nothing at all, the visitor sees a browser error and nothing in this spec can change that.

**G. Cold start / slow (O3).** After step 3, a waiting state appears within about a second of submit (inferred) and stays until a result or a failure. If the wait is long, the same state remains and gets a longer-wait wording; it never turns into an error by itself, and a long wait is not the "Judge error" state. If the request finally fails at the network level, see edge case "slow or lost network".

**H. Empty question (inferred).** Submit with blank or whitespace-only input: the page stays, says a question is needed, and returns focus to the field. No request is sent.

## 5. Edge cases

"Must still work" is what the visitor can rely on; "may fail gracefully" is what the design may refuse, provided the visitor is told.

| Case | Required behaviour |
|---|---|
| Blank / whitespace only | State H. Designed for. |
| Exactly 500 chars; 501 chars | 500 accepted; 501 refused with the limit named (E). Count by what the visitor sees as characters (inferred); emoji and combining marks must not make a visibly short question refuse without the count agreeing. |
| Very long paste (thousands of chars) | Refused as E without the page freezing. Not sent. |
| Non-English question | Not blocked. The docs are English; a non-English question may well end in "The docs don't answer this". The page says up front the docs are in English (inferred). Right-to-left and non-Latin text must display and be selectable in the field. Whether such questions retrieve well is the gate's business, not a UX promise. |
| Pasted markup or code (HTML, script tags, Markdown, backticks) | Treated as plain text. Nothing the visitor typed is ever rendered as markup, in the field, the count or any message. Passages from the docs are shown as text, not interpreted: a passage containing HTML or Markdown syntax is displayed literally and cannot inject into the page. Designed for (Security-sensitive). |
| Hostile text (injection, "ignore instructions", "reveal your prompt", "write me an essay") | Gets the same states as any question, normally "The docs don't answer this". The page never shows a refusal that explains the defences, and never shows generated text. |
| Repeated submits (double click, Enter held down, button then Enter) | One request per question while one is in flight. Further activations do nothing and are not queued. A repeat does not spend extra allowance. If the visitor deliberately submits the same text again after the result, it is a new question and counts. |
| Resubmitting after an error | Allowed at once, except C and D where the state says why not. |
| Back button | The page is one screen: submit does not create a history entry the Back key must step through (inferred). Leaving and returning via Back must not resubmit a question, and must not show a stale result as if fresh (inferred; a blank page is acceptable). Forward/reload prompts to resend a form are an anti-pattern here: a reload never silently re-asks. |
| Reload during wait | The in-flight question is abandoned. No second model call is made from the reload. A fresh blank page. |
| Slow or lost network | If no response arrives, the waiting state ends in a distinct "could not reach the service, check your connection and try again" state (inferred), different from "Judge error" (the service did answer). The question stays in the field. The visitor is not told whether the question was counted. |
| Back/offline then retry | Works as a new question. |
| Cold start | State G. First-ever view and first-ever ask after idle are both covered. |
| JavaScript off | Must still work: the page loads, the up-front information (section 2), the limits and the GitHub issues link are readable, and a message says that asking needs JavaScript. May fail gracefully: asking itself. Reason: the intent says the page "calls the service"; a no-JS form post would also have to show every state as a page and is a design choice for stage 4 and 5, not required here (inferred). If stage 5 chooses a server-rendered form, every state in section 4 must then exist as a full page too. |
| Very long or many passages | Remain readable at 200% zoom and 320 CSS pixels wide with no horizontal scrolling of the page (code lines inside a passage may scroll within their own region, which must be keyboard-reachable). A passage is never cut so a line range no longer matches the text shown. |
| Small screen, zoom to 400%, text-only spacing | No loss of content or function (WCAG 1.4.10, 1.4.12). |
| Slow reader, copy and paste | Passages and paths are selectable text, so they can be copied into an issue. |
| GitHub link target missing / file moved | The link is built from the pinned corpus commit (inferred); it may open a page that no longer matches only if the repo is rewritten. Not designed for. |
| Two tabs | The hourly allowance is per visitor, not per tab; a refusal in one is independent of the other. No cross-tab state to design. |

## 6. States per screen

One screen (the ask page). Each region lists the states stage 4 must lay out and stage 11 must test renders.

| State | What the visitor can do next | Req |
|---|---|---|
| Initial / empty | Type. Info visible; no result region content. | R13 |
| Typing (count visible, within limit) | Submit. | R8 |
| Over limit (typing) | Shorten; submit is allowed to refuse with the limit or is held off, either way the limit is named (stage 4's choice). | R8 |
| Waiting (normal) | Nothing required. Can reload to abandon. | G |
| Waiting (long; cold start) | Same, with a longer-wait wording. | O3 |
| Answer shown | Read, follow links, ask again. | R2 |
| No confident match | Edit and ask again, or open the issue link. | R3 |
| Judge error | Ask again. | R4 |
| Rate limited | Wait; read the docs. | R6 |
| Paused for today | Come back later; read the docs or open an issue. | R7 |
| Service off | Nothing but the info and the issue link. | R9 |
| Empty question | Type. | inferred |
| Network failure | Retry. | inferred |
| Scripting unavailable | Read; no ask. | inferred |

Loading: the Waiting states. Empty: Initial, and Empty question. Error: Judge error, Network failure, Service off. Every state's text is a real text node, not an image.

## 7. Accessibility floor (WCAG 2.2 AA, this slice)

Keyboard
- Every function works by keyboard alone: the field, submit, every passage link, any scrolling code region, the issue link. Tab order follows reading order: info, field, submit, result.
- Submit by Enter in the field is supported where the field is single-line; if multi-line, a visible button is reachable and the gesture is stated (inferred).
- No keyboard trap. Visible focus indicator on every control (2.4.7, 2.4.11 focus not obscured, 2.4.13 appearance where it applies); target size at least 24 by 24 CSS pixels (2.5.8).
- Skip link is not required for a one-screen page; if the page grows a header with links, add one (inferred).

Focus management
- After submit, focus is not lost. It stays on the submit control or moves to the result region once the result exists; it must never go to the top of the document or to `body` (inferred). Pick one and keep it for every state.
- On a client-side validation message (E, H), focus goes to the field, and the message is tied to the field in the accessibility tree.
- A reload or Back never leaves focus on a control that no longer exists.

Screen-reader announcement
- The result region is announced when it changes, politely (not assertive) for the answer states and the waiting state; error states (judge error, network failure, rate limited, too long, service off, paused) are announced as errors. Announcement says the state and the count of passages, e.g. that two passages were found, without reading all passages unprompted (inferred).
- The waiting state is announced once at its start and once at its end; a repeating announcement while waiting is not allowed.
- The field has a visible label, not just a placeholder; the up-front limits are associated with it by description. The character count is available to assistive technology but is not announced on every keystroke (announce at thresholds, e.g. near and over 500 (inferred)).
- Each passage is a distinct unit with a heading or label giving its file, heading and line range; each link's accessible name says which file and lines it opens, not "link" or "here" (2.4.4). Links that open a new tab say so.
- Page has a language attribute; passages in the docs' language are English. Page title says what the page is and does not change with the question.

Contrast and colour
- Text 4.5:1, large text and UI component boundaries 3:1 (1.4.3, 1.4.11), in every state, including error and disabled-looking states, focus rings, and links inside passages. State is never conveyed by colour alone (1.4.1): each carries text and, if an icon is used, an accessible name.
- Works in forced-colours/high-contrast mode and in the visitor's dark-mode preference without losing any state's meaning (inferred).

Motion and time
- No auto-start animation that cannot be paused. The waiting indicator is static or reduced under the visitor's reduced-motion preference (prefers-reduced-motion), and a text status is always present, so the indicator is never the only signal.
- No time limit on the visitor: the page does not expire or clear the typed text on a timer. No auto-refresh.

Text and reflow
- Usable at 200% text, at 320 CSS pixels width without two-dimensional scrolling (1.4.10), with user text spacing (1.4.12). Relative units are a design matter; the behaviour is the requirement.
- Plain language for state messages; no jargon such as "judge" or "verdict" in visitor text (inferred, stage 4 owns the words).

Forms
- Errors identify the field and say what to do (3.3.1, 3.3.3). Do not clear a field on error. Do not require re-entry of the question for any retry (3.3.7 redundant entry).
- No CAPTCHA or cognitive-test gate (3.3.8) (inferred; if Security later asks for one, that is a new decision, not this spec's).

## 8. Open items for downstream (not decided here)

- Stage 4 (UI Designer): all copy, layout, which of focus-to-result or focus-stays; waiting wording at normal and long wait; whether over-limit blocks submit or refuses it.
- Stage 5 (Architect): kill switch (O1) and whether the page loads when off; cold start and min replicas (O3); pause reset (O4); whether errors count against the hourly allowance; no-JS form post or not.
- Stage 7 (Compliance): the up-front sentence about the model provider; keep consistent with the data map.
- Stage 11 (QA): each state in section 6 renders; keyboard-only run through every journey; screen-reader announcement check for the answer, no-match and each error state; reduced-motion and 320 px checks.
- Unconfirmed: whether `retrieve` returns a fixed number of passages (looked at: PRD, intent, scope review only; I did not read the codebase, by design). The passage-count behaviour above is written to hold for one or many.
