# 01 Scope review - polished-chat-experience

> Engineering Manager, stage 1, depth standard, 2026-10-26. Read: intent.md, 00-slice-plan.md, CHARTER.md (sha256 a24c3c56...), STATE.md, setup-dryruns.md, `.agentic/` (SAFETY_INVARIANTS, CURRENT_MVP_STATUS), REVIEW.md, and in `aveto_service/` app.py, pages.py, render.py, pipeline.py, result_store.py, static/enhance.js, plus the Dockerfile, `.dockerignore`, `tests/test_infra_static.py`, `test_core_files_unchanged`. No code written. intent.md, CHARTER.md and 00-slice-plan.md not edited.

## 1. Verdict

**STOP-FLAG: one item needs the Orchestrator and the owner before stage 2 (section 3, S1). Otherwise the slice proceeds as planned.**

Size: **over the EM limit.** Scope rule "touches more than 10 files for a non-refactor change" is tripped (about 18 to 24 files, section 2). The intent also bundles two surfaces (the chat page and a new scorecard page) and a deploy with a rollback gate. Per the rule I would propose a split: slice A = server side (counts, warm-up, receipts data, resting state, figures reader, new routes, their tests), slice B = page, cards, drawer, scorecard page, docs, deploy. I do **not** recommend taking it, because: the Charter (hash a24c3c56...) is approved for one slice and a split is a Charter change (stop 5); a single deploy plus one rollback rehearsal is cheaper than two; the UI cannot be judged without the data behind it. The cost of accepting the oversize is recorded here: the Orchestrator should treat stage 4 as a checkpoint (backend tests green and committed before stage 5 starts), and no downstream role is given more than about 10 files (section 5). This is a recorded deviation, for the Orchestrator to accept or overrule; it is not a stop by itself.

Risk: **high**, as the plan says (real user data, irreversible redeploy, UI). Short path does not apply: Stakes tick real user data, irreversible and UI, so the full chain runs (Stakes override completeness).

## 2. Files the intent implies touching (with the ones it forgot)

Facts behind the list: `Dockerfile` copies the whole `aveto_service/` directory (lines 14, 34), so new files placed under `aveto_service/` ship with no Dockerfile change. `.dockerignore` excludes `runs/`, `docs/`, `evals/*` (except `calibration-offtopic.toml`), `.agentic/`, `infra/`, `tests/`. `STATIC_TYPES` in `pages.py` is an allowlist of two files (`enhance.js`, `style.css`).

**Product code (under `aveto_service/`)**
| File | Change | Note |
|---|---|---|
| `render.py` | answer card, refusal card, suggested questions, waiting, resting state, receipts drawer markup, scorecard markup | main rewrite; privacy/Article 50 text in `page_html` must stay byte-identical (Charter C1.6) |
| `pages.py` | new routes' responses, new static types, headers dict unchanged | `SECURITY_HEADERS` must not change (C5.0); new responses must carry it |
| `app.py` | new routes (scorecard, counts, warm-up, click beacon); resting state needs `GET /` to read the spend counter (today `page()` only reflects the kill switch, so "paused" appears only after a POST) | new routes must not reach the judge (INV-4: no route but `POST /ask`) |
| `pipeline.py` | likely: a read-only accessor for "paused now", counters hook | `AskResult.to_json()` must stay byte-identical |
| `static/style.css`, `static/enhance.js` | rewrite for cards, drawer, waiting, 375 px, focus | `enhance.js` re-implements every state in JS (STATES table, `showAnswer`, `showState`): each card is built twice, server HTML and JS. Doubles the "no model-written text" and a11y surface |
| new `aveto_service/counts.py` (name the Architect's) | in-memory counters: visits, asked, answered, refused, docs clicks | no question text; reset on restart (D1 out of scope) |
| new `aveto_service/figures.json` (or `.toml`) + reader | committed scorecard figures | **must live under `aveto_service/`**: `docs/`, `runs/`, `evals/` are not in the image. A figures file outside it needs a `.dockerignore`/`Dockerfile` edit and `test_infra_static.py` change, which I advise against |
| new suggested-questions data (inside `aveto_service/`) | 3 answered + 1 refused, copied from spent eval sets | `evals/*` is not in the image, so the four questions are copied text, not read at runtime; name the source set and ids in the file |
| possibly new `static/*.js` for the scorecard/drawer | | any new type must be added to `STATIC_TYPES`; CSP stays `'self'` |

**Tests (existing and new)**
`tests/test_service_pages.py` (25 tests; exact-copy assertions such as line 85 will break on a rewrite and need deliberate updating, not weakening), `test_service_api.py`, `test_service_pipeline.py`, plus new files for: refusal card has no model text; resting state at the cap; counts hold no question text; receipts drawer shows only held data; answer-card text is in a listed source; scorecard shows no line without a record. `tests/test_service_logging.py` (`test_abuse_line_shape_exact`) must still pass: **do not add Outcome values or log lines for counts.**

**Forgotten by the intent (flagged)**
1. Figures file location (above): must be inside `aveto_service/`.
2. Suggested questions cannot be read from `evals/` at runtime (not in the image).
3. Dockerfile: no change needed if the above holds. If anyone moves data outside `aveto_service/`, `test_dockerfile_static`, `test_dockerignore_excludes_models_index` apply.
4. `infra/main.bicep`: no change needed (no new env var is implied). Any new setting would be a Charter C8.3 question ("no other resource added"; a new app setting is arguably a change to the deployed resource). Architect: avoid.
5. `tests/test_service_pipeline.py::test_core_files_unchanged` pins hashes of `aveto_support/*`, `prompts/*`, `docs-source.toml` and the `.claude/hooks` file list; it is the standing proof of "answering unchanged" and must stay green.
6. `README.md` public-service section (lines ~119 to 215), `docs/runbooks/public-ask.md` (add: new routes, counts reset on restart, rollback rehearsal result with measured time), `.agentic/CURRENT_MVP_STATUS.md` (recorded figures only; it is the only `.agentic` file the Charter lets us touch).
7. `runs/polished-chat-experience/` artefacts the scorecard links to (PR, Charter, event-log summary, end review): these links are URLs to GitHub, so the page needs the PR/branch URL at build time. The PR does not exist until stage 14, after the image is built. **The scorecard can link only to files at a known ref; the Architect must decide which ref (branch name) and accept that links may 404 until the PR/branch is pushed.** No figure for these is shown without a record.
8. A copy-link control and source chip need the commit permalink already in `p.url`; no change.

Count: product 7 to 9, tests 6 to 9, docs 3, = roughly 18 to 22 files.

## 3. Stop-flags (need a Charter change or the owner; not for me to resolve)

**S1 - Refusal card "the nearest passages" contradicts INV-4(b). STOP before stage 2.**
- `SAFETY_INVARIANTS.md` INV-4 (b): on `NOT_ANSWERABLE` the service returns "`no confident match` ... and nothing else (no passage, path or reason)"; "It never prints passages on (b)"; "The service shows passages only on (a)". Enforced by `test_not_answerable_is_exactly_no_confident_match`. The public gate's Bar 1 was scored as "no confident match, no passage".
- The intent's item 2 (refusal card shows nearest passages) is therefore a safety-text change. Intent Done means says: "If a safety-text change is needed, the run stops and says so." Charter C1.3, C1.4.8, C5.0 and section 9.1 say the same, and C1.3 forbids edits to `.agentic/SAFETY_INVARIANTS.md`.
- Also practical: today a refusal's `AskResult` holds no files (`pipeline.py` line ~300), and `/ask` JSON for it must stay byte-identical, so the JS path (which reads `/ask`) has no passages to show; a new data path would be needed.
- **Options for the owner:** (A) refusal card without nearest passages: the message, a rephrasing hint, the issue link and the "Read the docs on GitHub" link (and suggested questions). No Charter change; INV-4(b) intact. **Recommended.** (B) amend INV-4(b), the Charter (new hash, a rule-4 safety-control approval) and rerun the public gate logic; large and outside this slice's tier-3 plan. Orchestrator to put (A) or (B) to the owner; the UX spec (stage 2) must not be written until answered.

**S2 - Receipts "the judge's verdict" (conditional).** INV-4 says the page shows "the same passages as the JSON and no deciding-signal line". Showing the `signal` string (prompt name and hash) on the page would contradict that sentence. Showing only the outcome the page already shows ("The docs answer this" / "do not answer"), the docs commit, and the file/line list the response already holds does not. Recommendation: receipts show no `signal` line. If the owner wants it, it is the same stop as S1. Not a stop if the recommendation is taken.

**S3 - "docs search still visible" (clarification, not a stop).** Intent item 5 says the resting state keeps "the docs search still visible". The service has no docs search; the page has links ("Read the docs on GitHub", "Open a GitHub issue"). Reading taken: the docs link stays visible. A new search feature would be a new feature and is out of scope. Orchestrator to confirm with the owner if a different meaning was intended.

No other Charter flag found: no new runtime dependency is implied; no header change (C5.0: `frame-ancestors 'none'` and the `'self'` CSP stay; tests at `test_service_pages.py:357` pin it); no new processor (counts are in memory; warm-up must not call the judge); no new infra. If the Architect proposes any of those, that is a stop (section 9.1).

## 4. Claims in the intent and status lines, checked against the repo

| Claim | Where | Check | Result |
|---|---|---|---|
| "The first load today takes about 26 seconds" | intent item 4 | grep README.md, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md`: recorded cold start is **30.8 s** to the first `/health` answer (README 213, runbook 104, status file) | **Differs; 26 s has no record found.** Unconfirmed (searched those three files only; not `runs/`). The scorecard must show only a measured figure with date and method (C1.4.5), not 26 s. |
| "honest waiting ... warmed when the page loads" | intent item 4 | `main.py`/`load_runtime` loads the index and ONNX model at startup, before the service accepts requests. The 26-30 s of scale-from-zero is spent before `GET /` is answered, so the page's own waiting state cannot show it; the browser tab spins. What the page can warm is the first retrieval/inference only. | **Architect/UX note:** do not promise a wait display for the container start. Whether the first inference is measurably slow is unconfirmed (no measurement found; searched pipeline/app code and the three docs). |
| "Pack v29 installed" | intent, Done means | `.claude/agentic.config.json` line 2 `"packVersion": 29` | true |
| "`frame-ancestors 'none'` in `pages.py`" | intent | `pages.py` line 24 | true |
| "No question is stored or logged"; counters in memory | status, INV | `pipeline.py` docstring, `ResultStore` holds `AskResult` only | true |
| `git diff main -- aveto_support prompts .claude .agentic` "empty except the pack install" | intent Done means | The branch is level with main (plan: 0 0), so it is empty now. But the Charter permits an edit to `.agentic/CURRENT_MVP_STATUS.md`, so the intent's literal command will not be empty at the end. **Charter C1.4.1 is the narrower command and binds** (it excludes `CURRENT_MVP_STATUS.md`). QA must use C1.4.1's command, not the intent's. | reconcile |
| Status file: service "is not on main", "deployed from branch ... not merged" | `.agentic/CURRENT_MVP_STATUS.md` (lines ~3, ~209) | `aveto_service/` exists at main 32e54a6 (plan says branch level with main; git log shows PR #9 merged) | **stale**; record in the docs stage, rewrite only what a record supports. |
| "Previous-revision rollback not rehearsed" | status, runbook (lines 109, 282) | consistent with the intent making it a gate | true; stage 10 or 13 must update after the rehearsal with the measured time. |
| Test baseline | plan | 668 passed, from setup-dryruns.md (not rerun by me) | taken from the record |
| Baseline axe | setup-dryruns.md C6.9 | 1 serious `aria-prohibited-attr` (1 node) on the current page, 25 passes | true as recorded; I did not rerun it. See below. |

**Baseline accessibility finding (binds C1.4.3):** the current page already has one serious violation, `aria-prohibited-attr`. Reading `render.py`, the likely cause is the `<span class="icon" aria-hidden>` / `role="alert"` on the `<h2>`, or `aria-label` on `<pre role="region">`, or `aria-label`/`aria-labelledby` on an element with no role; that is a guess, not confirmed (I cannot run the browser). The new page must fix it; the Frontend Developer should be told the finding and the node, and stage 8 re-runs axe on all five views. A fix is not "pre-existing, so out of scope": C1.4.3 requires zero serious on all five views.

## 5. The three things the build must reconcile

1. **`/ask` JSON byte-identical vs the new cards.** `AskResult.to_json()` and `_STATUS` are frozen by C1.4.1. Anything the cards or receipts need beyond today's JSON (counts, nearest passages [S1], warm-up, receipt fields) must travel on new routes or on `AskResult` fields that `to_json()` does not emit, never by adding keys to the JSON. The proof is the byte-equality test over at least 10 questions (C1.4.1). `enhance.js` reads `/ask` JSON today; the Architect should decide whether the JS path keeps doing that or fetches server-rendered fragments from a new route, which would remove the double implementation of every card.
2. **Scorecard figures from a committed figures file plus service-own measurements.** Image is built once (C8.3), so the file is fixed at build time and cannot hold post-deploy figures (live warm/cold timing, rollback timing). Those go to the run record and PR and enter the scorecard only by a later change (plan design note). The service's own figures (its cold-start time since process start, warm latency, counts) are measured in-process; the page shows a line only when a record exists. The scorecard must label in-process figures with their basis ("since this replica started"), because the app scales 0 to 1 and every cold start resets them.
3. **Counts without content, in memory.** Visits, asked, answered, refused, docs clicks; no text, no identifiers beyond today's hashed prefix (which counts must not use). In-memory, like the spend counters, so they reset at each restart and scale-to-zero: with about five internal customers the numbers will often be small or zero after idle. D1 is out of scope, so the page must say "since the service last started" and never present a total as lifetime. "Clicks to the docs" needs a client beacon (a `fetch`/`sendBeacon` to a new same-origin route, allowed by `connect-src 'self'`); the beacon carries no question and the route needs a body-size cap and a rate limit so it cannot inflate counts cheaply (Security stage 9 to review). The counts route must not be public in a way that adds an unreviewed disclosure; Architect decides, Security reviews (D3 on `/health` is still open with the owner).

## 6. Lifecycle: confirmed, with small edits (gates never compress)

The 14-stage list in the plan stands; nothing is dropped and no gate is compressed. Skips already in the plan (Market Research, PRD, UX Researcher, AI Governance, Compliance and Data Governance, Analytics, FinOps) are reasonable: the intent states problem, users and Done means; no model/prompt change; no new processor. Rationale line for the short path: **not taken**, because Stakes tick real user data and irreversible (Stakes override).

Recommended adjustments (Orchestrator's to apply; none changes the Charter):
- **Hold stage 2 until S1 is answered.** Everything in the UX spec's refusal card depends on it.
- **Stage 3 (Architect)** also states: S1/S2 outcome applied; file-by-file contract (so Backend and Frontend each read at most about 10 files); where the figures file and suggested questions live (inside `aveto_service/`); JS-vs-server rendering choice; the fixed question set for the byte-identical test (at least 10, answered and refused, from spent eval sets, ids named); how each C1.4 bar is measured.
- **Stage 4 is a checkpoint:** backend tests green and committed before stage 5. Fail-first tests run on 32e54a6 first and the failing output is saved (C1.4.7).
- **Stage 5 estimate (140k) is the tightest.** It rewrites page, CSS and JS for five views at two renderings, plus the scorecard page. Watch it against the 1,300k ceiling; if stage 5 passes about 170k, stop and report before stage 6 rather than continuing.
- **Stage 8** (Orchestrator, browser): five views are fixed (page, answer, refusal, resting, scorecard). The resting view needs a way to reach the paused state locally with the fake judge; the Architect should specify it (a test-only setting is a hazard if it ships; use the fake service in the scratch dev server, as in setup, not a product flag).
- **Stage 10** also corrects the stale lines in `CURRENT_MVP_STATUS.md` named in section 4, only with a record behind each.
- **Stage 12** has no Dockerfile change expected; if the image build needs one, that is outside the plan and goes to the Orchestrator.

Gate tier: 3 (Release Gate), Security standard, review layer tier High, as in the Charter. Human approval points: none new beyond the Charter (deploy and rollback C8.3, push/PR C8.2, live checks C3.1); S1 option (B) would add a rule-4 approval and a new Charter hash.

## 7. Acceptance for this stage

Done when the Orchestrator has (1) read S1 and put (A) or (B) to the owner, (2) accepted or overruled the recorded oversize deviation, (3) confirmed the S3 reading, and (4) told the UX stage it may start. Context for stage 2 (UI Designer): intent.md items 1 to 8, Charter C1.4 and C1.6, `aveto_service/render.py`, `static/enhance.js`, `static/style.css`, the baseline axe finding, section 3 above. Not the rest of the repo.
