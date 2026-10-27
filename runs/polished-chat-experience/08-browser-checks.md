# Stage 8 — browser checks (Orchestrator, 2026-10-26, local, built-in browser)

Tree: `6c32de1` (all fixes through Q1/Q2). Servers: the stage 4 `devserver.py` on the real index and embedding model with a stand-in judge (no model called), ports 8765, 8766 (timing), 8767 (`--resting`); a scratch copy served `axe-core` 4.10.2 at `/__axe.js` from the session scratchpad (same origin, so the CSP `'self'` held; nothing added to the repo). The stand-in judge answers or refuses by label, so these checks show the page, not live model behaviour.

## C1.4.3 Accessibility (axe tags wcag2a, wcag2aa, wcag21aa, wcag22aa)
| View | Violations | Note |
|---|---|---|
| `GET /` | 0 | `color-contrast` returned "incomplete" (axe could not decide); measured by hand below |
| Answer result | 0 | same |
| Refusal result | 0 | same |
| Resting state (`--resting`, `GET /`) | 0 | nothing incomplete |
| `GET /scorecard` | 0 | `color-contrast` incomplete (40 nodes); measured by hand below |
**Zero serious or critical on all five views: bar met.** The baseline violation (`aria-prohibited-attr`, serious, on the old page) is gone.
Manual contrast sweep (every text node, computed colours, WCAG ratio against the nearest opaque background; 4.5 for normal text, 3 for large): `/` 25 nodes, minimum 6.39; answer 114 nodes, minimum 6.39; refusal 41 nodes, minimum 5.85; scorecard: no node under its threshold. The resting page was fully decided by axe. Not measured: contrast of the `:disabled` form on the resting page by hand (axe decided it, no incomplete); hover states.

## C1.4.4 375 px and keyboard
- At 375×812 no horizontal scrolling (scrollWidth 375 = clientWidth) on home, answer, refusal, resting and scorecard; no non-inline control under 24×24 CSS px on home, answer, refusal and resting. (Scorecard targets not measured separately: it holds only inline links and no controls.)
- Keyboard only (real key events): Tab order skip link, suggestion chips; Enter on a chip loads the question into the box and moves focus to it; Ctrl+Enter sends; focus lands on the result region; the next Tab is the source link, with a visible 3 px outline; 30 Tabs later the receipts summary is focused (`:focus-visible` true); Enter opens it, Enter closes it; no trap seen. Not tested by hand: following the source link (it leaves the page), the copy-link button (needs the clipboard), and Tab out of the page.
- **Seen, not a bar failure:** at 375 px the "What to expect" list (the approved privacy wording) fills the first screen, so the suggestions and the form start below the fold. UX spec section 11 flagged this; collapsing it would change how the approved wording is shown, so it is the owner's call.

## C1.4.5 Timings (local only, reported as measured, no pass figure)
2026-10-26T22:48Z, a local run of this release with a stand-in judge, 10 questions one after another from one client: **median 0.0143 s, slowest 0.0164 s** (the service's own work without the model call). A first `POST /warm` took 0.0488 s on a fresh process and the second 0.0008 s. These are not warm response times with the real model and are not shown on the scorecard as such; the live warm and cold figures are stage 13's. Record: `08-local/timing.json`.

## Not checked here
The waiting state at 8 and 60 seconds (needs a slow judge), the copy-link button, the docs-click beacon end to end, real touch gestures, and any real-device rendering. Screenshots: one taken at 375 px of the top of `/` (the privacy list above).
