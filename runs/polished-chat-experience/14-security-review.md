# Security & Privacy review: polished-chat-experience (stage 9)

- **Agent:** Security & Privacy, depth **standard** (Charter C7.1), `claude-opus-5-5`, 2026-10-26. Offline: no live service, no `az`, no network, no browser.
- **Scope (C7.1):** `git diff main...HEAD -- aveto_service tests` (base `32e54a6`, head `7a117e3`; product tree last changed at `6c32de1`): `POST /warm`, `POST /count/docs-click`, `GET /scorecard`, `counts.py`, the result region and receipts drawer (`render.py`), `scorecard.py` and `scorecard.toml`, `suggestions.toml`, `static/enhance.js`, the unchanged headers.
- **Read:** `intent.md`, `CHARTER.md` (C1.3, C1.4, C1.6, C4.0, C5.0, section 9), `05-tech-spec.md` (by section), `13-qa-evidence.md`, `code-review.md`, `08-browser-checks.md`, `DECISIONS.md`, `.agentic/SAFETY_INVARIANTS.md`, `REVIEW.md`; `aveto_service/{app,pages,pipeline,render,scorecard,counts,result_store,limits}.py`, `static/enhance.js`, `Dockerfile` CMD.

- **Checks I ran** (scratch only; no product file edited): `uv run pytest` on the 8 touched or related service test files (`new_routes, counts, scorecard, ask_bytes, page_cards, pages, suggestions, logging`): **92 passed**. Probe script `/private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-interesting-shannon-67bff6/1dbb5af3-2658-4b6f-ab7a-5c8d7e249de5/scratchpad/sec/probe.py` (plus `p5b.py`), run against the branch and, for P1, against `git archive main` in `scratchpad/sec/main`. Greps of the added lines for log calls, secrets, network imports and HTML sinks.

## Verdict: PASS WITH CONDITIONS

No P0, no P1. Two P2 findings and four advisories. Conditions: (1) the two P2s go into `END_REVIEW.md`; (2) the D8 fill of `scorecard.toml` happens after this review, so the Orchestrator re-runs `tests/test_service_scorecard.py` on the final tree and confirms any `[links]`/`source_base` is a `https://github.com/` address of a repository confirmed public (D9). The strict reader limits what a bad fill can do (P3), but I have not seen the filled file. **Go** to the Release Gate on those terms.

## 1. Questions from the brief

| Question | Answer | Evidence |
|---|---|---|
| New routes reach the judge, spend or a log line? | No. `/warm` runs one retrieval of a fixed question; `/count/docs-click` and `/scorecard` touch only `UsageCounts`. | `app.py:228-255`, `pipeline.py:330-341`; `test_warm_never_reaches_the_judge_or_spends`; added lines hold no `emit_`, `log`, `print`, `open(` or `write` (only `clipboard.writeText` in the JS) |
| `counts.py` content-free? | Yes: methods take an `Outcome` or nothing, `__slots__` fixed, four ints, a start time, a one-key timestamp limiter. Nothing on disk, no log. | `counts.py`; P6: a canary question (form, scripted, over-length, empty) is absent from logs, stdout/stderr, `/scorecard`, `/health` and the `ResultStore` |
| Receipts drawer shows only held data, no signal line (INV-4)? | Yes. Outcome title, docs commit, the listed file and line links; on a refusal "None", no path, no `<pre>`. | `render.py` `_drawer`; P2/P2b: `signal` canary absent on answer and refusal pages; `test_receipts_drawer_shows_only_what_the_service_held` |
| Scorecard reader strict, escaped, links limited to `https://github.com/`? | Yes. Unknown keys, wrong labels, multi-line text, over-length text, `..` or absolute record paths and any URL not starting `https://github.com/` or holding whitespace, `"`, `<`, `>` reject the whole file (503 fixed card). Every value is `escape()`d. | P3: `javascript:`, `data:`, `https://github.com.evil.example/`, `https://github.com@evil.example/`, a `"`-breakout and `../etc/passwd` all rejected; a valid PR URL accepted |
| `enhance.js` XSS surface (one renderer) | No `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `eval`, `new Function`, `document.write` or `location=`. The swap parses the same-origin response with `DOMParser` and `importNode`s only the children of `#result-live` and `#result-extra`; the field error is copied as `textContent`. Every server-held field is escaped (P2: passage text, heading, path, URL, commit, suggestion text and links carrying `"><script>` and `<img onerror>` produce no injected element or `on*` attribute). CSP `script-src 'self'` (no `'unsafe-inline'`) is a second layer against inline handlers; `connect-src 'self'` covers `/ask`, the followed 303, `/warm` and the beacon, so `'self'` is still sufficient. | grep of `enhance.js`; P2 |
| Scripted asks now follow the 303 and store a result: does code-review F1's bound hold? | **Not as stated; impact small and not new.** See S1. | P1, P1b |
| Abuse: `/warm` cost, beacon flood, rate limits, cross-site, size | `/warm`: one search per process when healthy; unbounded only while the search fails (A1). Beacon: one global 60/hour limit, so floods cost nothing but bend the count (S2). Cross-site: both POST routes refuse `Sec-Fetch-Site: cross-site` and a foreign `Origin` (checked); `Content-Length: 00` or any body byte is not counted. Size: `/warm` 15 bytes, beacon 0, scorecard about 3.5 kB fixed. | P4, P5, `p5b.py` |
| Privacy wording, INV-1..INV-5 | Unchanged. `SAFETY_INVARIANTS.md` sha256 `c4eac0e0…cc27` on `main` and the tree; `git diff main...HEAD -- .agentic aveto_support prompts .claude` empty; `test_disclosure_block_byte_identical` passes. New copy (`N1`, count bases, drawer, hints) makes no privacy, data-handling, legal or AI claim beyond the page's own content. | |
| Response headers | `SECURITY_HEADERS` is in no hunk; `/scorecard` sends exactly the `GET /` set including `frame-ancestors 'none'`; `/warm` and the beacon send the existing `_JSON_HEADERS` (`Cache-Control: no-store`, `nosniff`). | `test_security_and_json_header_sets_are_byte_identical`, `test_new_routes_carry_existing_header_sets`; `p5b.py` header dump |
| New dependency or processor | None. `pyproject.toml`, `uv.lock`, `Dockerfile`, `infra/` not in the diff; added imports are stdlib or in-repo. `PlaceholderJudgeClient` still raises (`judge_port.py:52-55`). C4.0 holds. | |
| Suggestions and scorecard data | Four questions copied from `evals/retrieval-heldout-5.toml`; no personal data; the loader rejects `<`, `>`, newline and over 90 characters, and they are escaped in the `value` attribute and button. Scorecard data names roles ("The owner", "The Orchestrator"), dates and repo paths; no name, email or secret. | `suggestions.toml`, `scorecard.toml`, `pages.py:35-52` |
| Prompt injection via passages or suggestions | No new path. A suggestion reaches the judge only as a visitor's question through the unchanged pipeline and prompt; the judge's output only selects the outcome, and the page shows no model text (INV-4). Passages are unchanged. | C1.4.1 golden (QA §2) |
| Log lines carry no question text | Yes; no log line added; Dockerfile keeps `--no-access-log`. | P6; `test_service_logging.py` |
| QA Q1 (scripted empty / over-500 posts) | Resolved in `6c32de1`: the submit handler checks empty and over-limit before `fetch`. | `enhance.js` submit handler |

## 2. Findings (P0 and P1 block release; none here)

| id | sev | where | finding | reproduction | disposition |
|---|---|---|---|---|---|
| S1 | P2 | `pipeline.py:54` (`_ADMITTED` includes `JUDGE_ERROR`), `:252-253`, `:281`; `pages.py:94`; `result_store.py:13-14` | Code-review F1 argues the 1000-entry `ResultStore` cannot fill because every stored result is bounded by the daily spend. That is true for `ANSWER` and `NO_CONFIDENT_MATCH` (a successful reply always costs usage), but **not for `JUDGE_ERROR`**, which is admitted and stored at zero spend when the judge fails in a never-billed category (`status_4xx`, `connection`; for example while the Anthropic console limit rejects requests) or when retrieval raises. Then the only bounds are 10 an hour (judge path) or 30 an hour (retrieval path) per client key, so about 100 client addresses inside the 10-minute TTL fill the store and evict older tokens. **Not new:** `main` stores every admitted no-script form post through the same `form_outcome`, and an attacker can post forms directly; this slice only adds honest scripted asks. Impact is small: a scripted visitor reads the result in the same `fetch` that followed the 303, so eviction only blanks a later reload of `/result/<token>`; the store holds no question (P6) and stays capped at 1000. | P1: judge raising `JudgeTransportError("status_4xx", attempts=2)`, 1005 form posts from distinct `X-Forwarded-For` addresses: 1005 × 303, store 1000, first token evicted, day spend 0. Same result on `git archive main`. P1b: a failing search, one address: 30 × 303 stored at spend 0, then 429. | Record the corrected bound in `END_REVIEW.md` (F1's wording); no fix in this slice. A later slice could store only `ANSWER`/`NO_CONFIDENT_MATCH` results, or key the store's cap per client. |
| S2 | P2 | `app.py` `index_page` (`counts.visit()`), `counts.py:17,55` | The counts that intent item 8 calls customer evidence are unauthenticated and easy to bend: every `GET /` counts a visit with no limit (a crawler, a health probe or a script inflates it); docs clicks share **one** global 60-an-hour budget, so a script can both add 60 an hour and crowd out real clicks; questions count JSON callers too (F4). No content or identifier is exposed. | P5: 70 empty same-origin posts to `/count/docs-click`: 60 counted, then real clicks are dropped until the hour rolls. | `END_REVIEW.md` and any public use of the numbers say they are raw, unauthenticated totals since the last restart, not verified visitors. No code change required. |

## 3. Advisories (not findings)

- **A1** `/warm` has no rate limit. Healthy, it runs one search per process and then answers from a flag. While the search keeps failing, every call runs one retrieval under `_retrieval_lock` (P4: 200 calls, 200 searches), contending with `/ask`. Only reachable when the service is already broken; it is the trade-off code-review F2 chose (retry after failure). A later slice could remember a failure for a few seconds.
- **A2** `/scorecard` is public and live: with about five users, polling it shows when someone asks and whether the docs answered, and the process start time to the minute (restarts, scale to zero). No content, no identifier. Acceptable in my reading (spec §16 asked); the owner may prefer coarser publication.
- **A3** The swap's safety rests on server escaping plus CSP plus the browser not running scripts from a `DOMParser` document. The first two I checked; the third is standard behaviour I did not test in a browser (see section 5).
- **A4** Spec §3 says the beacon reads up to 64 body bytes; the code stops at the first byte. Stricter than the spec; no action.

## 4. Release-gate confirmations

- Invariants touched (INV-4 page output; the no-question-stored/logged rule): hold; `SAFETY_INVARIANTS.md` byte-identical; C5.0 holds.
- No audit or abuse event removed, renamed or added (spec §7: the abuse line and three ops codes unchanged); usage counts are deliberately not audit events.
- No placeholder became a real client; no new model, processor (C4.0) or dependency. No secret or key-shaped literal in the added lines; tests use `"test-key"`.
- Response headers unchanged; `frame-ancestors 'none'` on every HTML response (C1.3).
- Agentic threats (ASI): not applicable; no agent, tool or memory surface changed (the runtime judge, its prompt and adapter are untouched).

## 5. What I did not check

- Browser behaviour: that `importNode`ed scripts from `DOMParser` stay inert, that the live page raises no CSP violation, and the real headers `sendBeacon` sends (stage 8 did not exercise the beacon end to end; `08-browser-checks.md` "Not checked here").
- Live: headers as served through Azure ingress, Azure platform logs for the new routes (I could not confirm offline whether ingress records request paths), and concurrency (thread-pool saturation by `/warm` or `GET /` floods; I reasoned about it but did not load-test).
- The `scorecard.toml` after the D8 fill, `docs/ARCHITECTURE.md` and the ADRs' wording, README/runbook/status edits (later stages), and `style.css` beyond QA's `url(`/`@import` grep.
- `05-tech-spec.md` I read by section (§1, §3, §7, §16), not end to end.

## Hand-off

To the Release Manager: **GO** from Security, PASS WITH CONDITIONS (top of file). Carry S1 and S2 into `END_REVIEW.md`; A1 to A4 are backlog or owner notes.
