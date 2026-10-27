# ADR 0010: Results are rendered once, on the server; the page script swaps in the server's HTML

- **Status:** proposed
- **Date:** 2026-10-26
- **Slice:** `runs/polished-chat-experience/` (tech spec `05-tech-spec.md` sections 2 O2 and 3.0)

## Context

The public page of the ask service built every result card twice: in `aveto_service/render.py` for the no-JS form path, and in `static/enhance.js` from `POST /ask` JSON. The slice adds an answer card, a refusal card with suggestions, a resting state and a receipts drawer. Two builders would mean every rule ("no model-written text", "only text from a listed passage", the accessibility fix) is specified, tested and reviewed twice, and a drift between them would be invisible to the tests that run in Python. The intent also requires `POST /ask` JSON to stay byte-identical (Charter C1.4.1), and INV-4 allows only `POST /ask` to reach the judge.

## Decision

`render.py` is the only builder of anything that shows a result. The page script posts the question to the existing `POST /ask` as `application/x-www-form-urlencoded` (the no-JS path), lets `fetch` follow the 303 to `GET /result/<token>`, parses the returned page with `DOMParser`, and replaces the contents of `#result-live` and `#result-extra` and the field-error state with the server's. The script builds only what has no server response: the waiting card and the network-error card. The page never reads `/ask` JSON; the JSON route is unchanged for API clients.

## Alternatives considered

- **Keep two builders.** Rejected: double test and review surface, invisible drift.
- **A new route that returns a result fragment for a question.** Rejected: it would be a second route that reaches the judge (INV-4).
- **A new route that renders a fragment from a result the script sends back.** Rejected: the server would render text it cannot vouch for.
- **Render in the script only, with no-JS fallback dropped.** Rejected: the page must work without JS, and the Python tests could no longer see what visitors see.

## Consequences

- The JS and no-JS pages are the same HTML, so one set of Python tests (`tests/test_page_cards.py`) covers both, and the accessibility check covers both paths.
- The script no longer pre-checks empty or over-long questions; the server answers them with no model call, as it does for no-JS visitors.
- Results of JS-path questions now pass through the existing post-redirect-get store (10 minutes, at most 1,000 entries, no question text), as no-JS results already did.
- A result costs one extra same-origin GET (the 303 target) and a full-page parse in the browser; small at this page's size.
- Revisit if the page gains state the server cannot render (for example streaming), which the service's single-request design does not have.
