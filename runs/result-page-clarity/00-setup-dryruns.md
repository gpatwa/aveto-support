# Setup phase — dry runs (Orchestrator, 2026-10-27, after Charter approval 06:13Z)

| id | Dry run | Result |
|---|---|---|
| C6.P | `settings.local.json` written at the main checkout with the Charter's 50 rules (9 `Agent(<role>)` rules); read-only commands below ran | no permission prompt shown for any of them |
| C6.1 | `git rev-list --left-right --count main...HEAD`; `packVersion` | `0 0`; 30 |
| C6.3 | `uv sync --locked`, mypy, ruff, pytest | mypy clean (53 files); ruff 1 error and pytest 1 failure = the two items of C1.7 (fixed in stage 2) |
| C6.4 | `az account show` | Enabled |
| C6.5 | `az containerapp show`, `revision list` | image `aveto-ask:ffc2e2e5f39a`; active revision `ca-aveto-ask--0000011`; tags in the registry include `ffc2e2e5f39a` |
| C6.6 | `events-verify.mjs` | chain intact; 53 lines; the one "no outcome" alert is the verifying call itself |
| C6.7 | `npm install --prefix <scratchpad>/axe axe-core@4.10.2` | installed (1 package), scratch only |
| C6.8 | `devserver.py --port 8765` (stand-in judge) loaded in the browser pane at 1280×800 and 375×667 | page loaded, forms submitted, no prompt |
| C6.9 | STATE.md carries `- **Hard cap:** 800k` | present |

# Before figures (taken on `main` 6ab5548 = this branch before any change)

Method: local `runs/polished-chat-experience/08-local/devserver.py` (stand-in judge: answers by label, shows the whole listed passages; no model called), built-in browser pane, suggestion 1 (answered: "Does saying "looks good" to an agent count as approving something?") and suggestion 4 (refused: "Does it support right-to-left languages?") sent with the real Ask button, then 3.5 s wait. Value = `#result-title` `getBoundingClientRect().top` in CSS px; focus was on `#result` in all four.

| Viewport | Question | Heading top | Share of viewport | Result region height |
|---|---|---|---|---|
| 1280×800 | answered | **−2,820.9** (off screen above) | — | 6,463 px (page 7,795) |
| 1280×800 | refused | **292.1** | 36.5% | 516 px |
| 375×667 | answered | **−4,182.9** (off screen above) | — | 9,053 px |
| 375×667 | refused | **−2.9** (cut off by 3 px) | — | 688 px |

Observation for the Architect: the browser's `focus()` on a region taller than the viewport scrolls to its far end, so a long answer lands with its heading far above the screen, not at the 616 px the live revision showed for a short answer. The fix must scroll the heading to the top itself and stop `focus()` from scrolling.
Reading of Charter C1.4 item 1 ("within the top 25%"): `0 ≤ top ≤ 25% of the viewport`; a heading cut off above the screen (negative) does not pass. This is the natural meaning of the bar, not a change to it.
