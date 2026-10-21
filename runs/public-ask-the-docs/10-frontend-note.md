# Frontend note: public-ask-the-docs, stage 10 (Frontend Developer, depth standard)

Status: done, nothing committed. `uv run mypy && uv run ruff check && uv run pytest`: all green, 584 passed, 12 deselected (includes the AI Engineer's files, present by the end).

## Built
- `aveto_service/render.py`: all HTML, `html.escape` on every dynamic string (f-strings, not `string.Template`; same effect, simpler). Passages in `<pre class="passage" tabindex="0" role="region"><code>` as one escaped text node. Passages sit outside the `aria-live` wrapper so only the heading is announced.
- `aveto_service/pages.py` (`HtmlPages`), `result_store.py` (token, 10 min, 1,000 entries, no question), `main.py` (exactly the tech spec line; the Anthropic adapter is imported lazily, only when a key is set; placeholder otherwise).
- `static/style.css` (tokens light/dark, forced-colors, reduced motion), `static/enhance.js` (no dependencies, DOM built with `textContent`, no storage, `credentials: omit`).
- Headers on every `HtmlPages` response (pages, 303, static, static 404): no-store, CSP as the tech spec, no-referrer, nosniff; no cookies.

## Tests (`tests/test_service_pages.py`, 25)
Every state's exact copy; disclosure sentences verbatim; passages byte-identical (unescaped page vs `retrieve_for_judge`); markup in a passage and in an echoed question escaped; no question in any URL/Location; PRG and reload does not re-ask; unknown token; store expiry/bound; headers on every response; no external origin or cookie/storage use in page and static; static types; pinned links and generic issue title.
Fail first: at the base commit (HEAD exported to a scratch dir) collection fails, `ModuleNotFoundError: No module named 'aveto_service.pages'`.

## Deviations / decisions
1. Copy for outcomes the UX table lacks: `unusable_question` and `bad_request` show the Empty state ("Please enter a question"); `body_too_large` shows "Your question is too long" with "Yours is much longer." instead of a count. Wording is the nearest existing copy, not new copy; UI Designer may want to rule.
2. Client count uses code points, not graphemes (the server is authoritative and the same unit; avoids a mismatch).
3. Non-admitted states return the outcome's HTTP status (400/413/429/503) with the page body.
4. An unmatched route (for example `/static/..%2Fx`) is answered by FastAPI's default JSON 404 from `app.py`, without the page headers; `app.py` is not mine. Not reachable to any file: only two names are served.
5. The "Found n passages." text is inside the `<h2>` (a block span) so the live announcement carries the count.

## Unconfirmed
- Browser preview not done: no browser tool in this role. `enhance.js` passed `node --check` only; its behaviour (waiting, 8 s swap, focus, thresholds, network failure) is untested here. QA should exercise it.
- Contrast ratios are the UX spec's approximate figures, not measured by me; the white-on-blue button text uses `--bg` on `--link` (dark mode: dark text on light blue), unmeasured.
- `main.py` was not imported against the real index and models (needs `index/` and `models/`).
- Forced-colors and 320 px layout were not rendered.
