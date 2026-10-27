2 findings (0 Important, 2 Nits), round 1. Unscored review (no rescore since 2026-10-17, Charter C3.R).

- **Tier:** Medium. The diff touches product source (`aveto_service/pages.py`, `render.py`, `static/enhance.js`, `static/style.css`) and tests; nothing under `.claude/`, `aveto_support/`, `prompts/`, `.agentic/`, no header, route or invariant.
- **Method:** the local `/code-review` skill at `high` against `main`, `REVIEW.md` as rules, no `--fix`. Reviewed `git diff main...HEAD`: 15 files, 920 insertions, 20 deletions (the run's tests and goldens included).
- **Checked and found sound:** the guard `region.compareDocumentPosition(form) & FOLLOWING` keeps the resting page (result above the form) untouched; on a server result-first page the move is a no-op; on the home page after Ask it appends the blocks after `ready` and the result, giving the server's order; `first` is false for `GET /`, resting, service off and an unknown token, so those stay in home order; the `EXPECT` constant is the removed block moved verbatim, and the golden strings test pins it.

| id | severity | file:line | what and what triggers it | how to reproduce | disposition |
|---|---|---|---|---|---|
| R1-1 | Nit | `aveto_service/static/enhance.js:67` | `resultFirst` finds the blocks to move by `h1.nextElementSibling.nextElementSibling`; a later template change that adds an element after the h1 would move the wrong blocks. | Add an element between the statement and "What to expect" in `render.py`, then ask a question with JavaScript on. | Accepted, not fixed: the dependency is recorded in the tech spec (open item 3), T1-T3 pin the server order. |
| R1-2 | Nit | `aveto_service/static/enhance.js:232` | The load-time `land()` on `#result` scrolls to the heading on a reload or back navigation, overriding the browser's scroll restore. | Scroll down a long answer on `/result/<token>#result`, reload. | Accepted, not fixed: first visits behave as intended; no data or answer is affected. |

Round 1 only; no finding is open at Important, so no round 2 is needed.
