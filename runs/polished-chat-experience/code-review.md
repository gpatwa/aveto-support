7 findings (round 1): 1 Important, 3 Nit, 1 test-coverage, 2 cleanup (dropped as cleanup-only per REVIEW.md). Unscored review (C3.R: no rescore since 2026-10-17).

**Tier: High.** Paths that set it: `aveto_service/app.py`, `pipeline.py` (spend limits and the public page's routes), `render.py`, `pages.py`, `static/enhance.js`, and the Charter C5.0 line naming headers and invariants that must not change. Reviewer: the local `/code-review` skill at `high`, run by the Orchestrator on `git diff main...HEAD` (22 files, tests and golden included), `REVIEW.md` as rules, no `--fix`. The reviewer did not write the code.

| id | severity | file:line | what and what triggers it | reproduce | disposition |
|---|---|---|---|---|---|
| F1 | Nit | aveto_service/static/enhance.js:160 | Scripted asks now follow the 303 and store a result in the shared 1000-entry `ResultStore`; a flood could evict others' tokens. | Not reproducible: `form_outcome` stores only admitted results, and admission is bounded by the daily spend cap (about 33 judged questions a day at the live price) and 10 per visitor per hour, so the store cannot reach 1000 entries within the 10-minute TTL. | intentional: bounded by the daily cap; recorded for the Security Review to confirm |
| F2 | Important | aveto_service/pipeline.py:340 | `warm()` caches a failed warm-up for the life of the process; the Ready line never appears and the search is never retried. | A first `warm()` call whose search raises, then a second call that would succeed, still returns False. | fixed f5c139c (round 1; re-review of the new diff: only `warm()` changed, failure no longer cached, lock and `_search_once` unchanged) |
| F3 | Nit | aveto_service/static/enhance.js:193 | Docs clicks counted on `click` only; middle-click and open-in-new-tab are missed. | Middle-click the docs link: no beacon. | intentional: the count's note already says it counts only with the script running; undercount is stated in `END_REVIEW.md` |
| F4 | Nit | aveto_service/app.py:184 | `counts.record` also counts JSON `/ask` callers, not only the page. | POST JSON to `/ask`; the answered count rises. | intentional: those are questions asked of the same service; the intent counts "questions asked" |
| F5 | test-coverage | aveto_service/static/enhance.js:1 | No JS test runner; swap, beacon, warm and copy are not exercised by pytest. | n/a | intentional: covered by the stage 8 browser checks on a real page; stated in `END_REVIEW.md` |
| F6 | cleanup | aveto_service/scorecard.py:224 | Duplicated issue and docs URLs; lazy import of `SECURITY_HEADERS`. | n/a | rejected: cleanup-only (REVIEW.md "Report only" bugs) |
| F7 | cleanup | aveto_service/app.py:29 | Imports private `pipeline._utcnow`. | n/a | rejected: cleanup-only |

Round 1 of at most 3. Round 2 (new diff only, f5c139c): 0 new findings; F2 confirmed fixed. Review closed after 2 rounds.
