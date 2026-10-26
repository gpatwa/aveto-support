# Tech Spec - polished-chat-experience

> Owner: Software Architect Agent. Stage 3, depth standard, 2026-10-26. Status: **ready for implementation** (stage 4 first; see section 14).
> Sources: `intent.md` (source of truth), `CHARTER.md` sha256 a24c3c56... (C1.4 bars, C1.5, C1.6, C5.0, C8, section 9 bind), `00-slice-plan.md`, `01-scope.md`, `DECISIONS.md` D1 to D5 (bind), `03-ux-spec.md` (section 11 answered in section 2 here), `.agentic/*.md`, `REVIEW.md`, `runs/fix-service-accounting/05-tech-spec.md` (model).
> Code read: `aveto_service/` (all .py, `static/enhance.js`), `tests/test_service_pages.py`, `tests/test_service_api.py`, `tests/service_fakes.py`, `tests/conftest.py`, `Dockerfile`, `.dockerignore`, `infra/main.bicep`, `infra/main.parameters.json`, `docs/ARCHITECTURE.md`, `docs/runbooks/public-ask.md` (sections 1 to 4), `evals/retrieval-heldout-5.toml`, `evals/public-gate-1.toml`, the headers of the other eval files, `runs/public-ask-the-docs/18-gate/{RESULT.md,final-report.txt}`, `runs/fix-service-accounting/10-smoke/{smoke-result.json,log-search.txt}`, `runs/fix-service-accounting/09-deploy/7.2-whatif-ruling.md`, `runs/docs-answerability-2/07-gate-scoring.md` (lines 40 to 69).
> No product code written. Files written by me: this spec, `docs/ARCHITECTURE.md`, `docs/adr/0010-*`, `0011-*`, `0012-*`, and my rows in `STATE.md`.

## What I could not do, and where I looked (rule 7)

- **I ran nothing.** My tools are Read, Write, Edit, Grep, Glob; I have no shell. The brief asks me to "verify by running the offline retrieval" that the four suggested questions behave as labelled. I did not run it. Section 9 gives the **recorded** evidence I found (offline retrieval at docs-answerability-2 stage 7, the attended judge's verdicts, and a live run on the current revision) and hands the fresh offline run to stage 4 as a named step with a pass rule. Nothing in this spec says a retrieval was run today.
- **Whether `gpatwa/aveto-support` is a public GitHub repository: unconfirmed.** Looked: README, `docs/`, `.agentic/`, `runs/*/END_REVIEW.md` (pull request URLs exist, visibility is not stated anywhere). Every link this slice ships into the image depends on it (section 3.7, O6). A pre-build check is specified (section 12.0).
- **The JSON field `properties.replicas` on `az containerapp revision list`: from memory, unconfirmed.** Used only to know the replica has scaled to zero before the cold-start timing; a fallback is given (section 12.6).
- **Whether the first retrieval in a fresh process is measurably slower than later ones: no record found** (looked: `LOCAL_COMMANDS.md`, runbook, `18-gate/RESULT.md`, the 2026-10-24 smoke). The warm-up is specified so that its one claim (W0) is true either way, and stage 8 measures what it absorbs (section 3.4).

## Summary

The page around the unchanged answering becomes a product: answer and refusal cards, four suggested questions, an honest waiting state with a warm-up, a resting state that shows on page load, a receipts drawer, a scorecard page built from committed records, and content-free counts. Nothing that decides or produces an answer changes: `aveto_support/`, `prompts/`, the judge adapter, the pipeline's gates, `AskResult.to_json()`, the response headers and INV-1 to INV-5 stay byte-identical. The design has **one renderer**: the server builds every card, and the page script, instead of rebuilding cards from `/ask` JSON, sends the question through the existing form path and swaps in the server's result region. Three routes are added (`GET /scorecard`, `POST /warm`, `POST /count/docs-click`); none reaches the judge, none writes a log line, and none takes a header set the service does not already send. New state is five integers and a start time in memory, plus a once-per-process warm-up flag. No dependency, header, processor, infrastructure setting or safety text changes; section 15 lists what I checked and the two readings the Orchestrator should rule on (neither is a stop in my reading).

## Done means -> design (trace)

| Done means line | Where it is satisfied |
|---|---|
| Starts from `main` with pack v29 | Plan and C6.1 (done before this stage); nothing here |
| Quality bars fixed, not moved | Section 11: how each C1.4 bar is measured, by whom, with which command; no stricter figure proposed |
| Nothing about answering moves; a test proves the answer card holds only listed text | Sections 8 (byte equality), 10 (answer-card test T-A), 15 (no safety-text change) |
| Embedding decision stated with the reason | Section 1 |
| Tests that fail first (four named) | Section 10 (T-R, T-S, T-C, T-D), run on the untouched 32e54a6 product code in stage 4's first commit (section 14) |
| Review layer, Security standard, Release Gate tier 3, Codex trial review | Not changed here; section 16 lists what Security reads |
| Deployed under C8.3; rollback rehearsed as a gate and timed | Section 12 (deploy sheet, rehearsal, roll forward, timing method, live checks) |
| The build is shown: linked from the scorecard | Sections 3.7 (figures file, build links), 12.0 (the public-repository check that decides whether links ship) |
| README, runbook, status file state recorded figures only | Stage 10; section 3.7 gives the figure rows and their records |

## 1. Embedding decision: option (a), restated with the reason

**Decision (the owner's, 2026-10-26, in the intent): option (a).** The service stays on its own address (`https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`); aveto.dev shows it as a recording plus a button that opens the service in its own tab. `frame-ancestors 'none'` and the rest of `SECURITY_HEADERS` in `aveto_service/pages.py` lines 20 to 28 do not change in this slice; a test pins them byte for byte (T-H, section 10).

Why (a) is right for this slice, as the architecture sees it:
1. **No safety-control change.** (b) edits a response header, which is a Charter C5 item, needs the Security Review to cover it, and would need a new Charter hash (C5.0 says "none"; section 9 stop 5). (a) needs none of that.
2. **The page's protections assume it is top-level.** The form posts, the 303 to `/result/<token>`, `Referrer-Policy: no-referrer` and the same-origin check on `POST /ask` (`app.py` `_cross_site`) were reviewed for a top-level page. Framed inside another site, the request would carry `Sec-Fetch-Site: cross-site` only in some browsers and the `Origin` would still be the service's own, so the cross-site rule would need re-reading; clickjacking defence would rest on one allowed origin being trustworthy. None of that is needed under (a).
3. **The aveto.dev change is decoupled.** Under (a) the site change is a link and a recording in the playbook repository (a separate commit with owner-approved wording, out of this slice). Under (b) a site deploy and a service deploy would have to agree on an origin.
4. **Cost of (a):** a visitor leaves aveto.dev to use the service. Accepted by the owner. (b) remains a separate later intent; ADR 0012 records the decision so it is not silently reopened.

## 2. Decisions on the UX spec's open items (03-ux-spec.md section 11)

| # | Item | Decision |
|---|---|---|
| O1 | "What to expect" above the form at 375 px | **Owner's item, not decided here.** Architecture has no objection either way. The text stays byte-identical (C1.6); any change of how it is shown goes to the owner (UX spec's reading). Default: unchanged position. |
| O2 | One renderer or two | **One renderer, server-side, with no new route.** `enhance.js` stops building cards from `/ask` JSON. On submit it posts the question as `application/x-www-form-urlencoded` to the existing `POST /ask` (the no-JS path), lets `fetch` follow the 303 to `GET /result/<token>`, parses the returned page with `DOMParser`, and swaps in the contents of `#result-live` and `#result-extra` plus the field-error state. A non-admitted outcome (too long, empty, rate limited, paused, off) already answers the form post with the full page and a 4xx/5xx status; the script swaps that the same way. The script keeps only what has no server response: the waiting card (W1 to W4) and the network-error card (copy unchanged). Detail and reasons in section 3.0; record in ADR 0010. |
| O3 | What "warm" does; can W0 be said | **`POST /warm` runs one retrieval of a fixed internal question, once per process, and never reaches the judge, the spend counter, the rate limiters or a log line.** It answers `{"ready":true}` only after the index and the embedding model have answered that search in this process, so W0 "Ready to search the docs." is true when shown. It does not and cannot warm the container start (30.8 s recorded; D5). Section 3.4. |
| O4 | Resting state on `GET /`; scorecard path; are counts and scorecard public | `GET /` reads the spend state through a new read-only `AskService.resting()` and passes `Outcome.PAUSED` to the existing `HtmlRenderer.page()` (section 3.5). Scorecard path: **`/scorecard`**. Counts and scorecard are **public**, on `/scorecard` only, totals only (no new JSON route); reason: the same kind of aggregate `/health` already publishes (`judged_today`). Security (stage 9) reviews this against the owner's open D3 on `/health`; the fallback if Security objects is to stop rendering the counts section (a render change, no route change). |
| O5 | The four questions | A1 `g01`, A2 `g03`, A3 `g04` (answered), R1 `gu18` (not answered), all from `evals/retrieval-heldout-5.toml`, spent. Copied as text into `aveto_service/suggestions.toml`. Evidence and its limits: section 9. |
| O6 | Link targets for Charter and run record | GitHub URLs on the **branch ref `claude/interesting-shannon-67bff6`** in repository `gpatwa/aveto-support`, shipped as data in `aveto_service/scorecard.toml` `[links]`. They resolve once stage 14 pushes the branch (between the stage 12 deploy and the push they return 404). They break if the branch is deleted after a merge; END_REVIEW tells the owner, and a later change can repoint them to `main`. **If the repository is not confirmed public before the build (section 12.0), no link ships** (`[links]` and `source_base` are left out) and the Release Manager records the Done-means line "linked from the scorecard" as not met. |
| O7 | Commit value for the drawer | From the runtime index the service already holds (`runtime.searcher.index.commit`, the same value `HtmlPages` already puts in the docs link), rendered server-side. Not from `/ask` JSON. |
| O8 | Docs-click beacon | `POST /count/docs-click`: same-origin only, **empty body only** (reading stops at 64 bytes; any byte means not counted), not counted with the kill switch on, and a **global** limit of 60 counted clicks per rolling hour. It reads no address and keeps no key, so the counts hold no identifier at all. Always answers 204 with no body, so it reveals nothing about counting. Section 3.8. |
| O9 | W2 "up to a minute" | **Kept.** Basis: recorded cold start 30.8 s plus recorded slowest live answer 5.09 s (`18-gate/RESULT.md`) is about 36 s, under a minute; a request only meets a cold start if the replica scaled to zero while the page sat open. Stage 13 measures cold start again; if cold start plus slowest warm answer exceeds 60 s, that is a P2 copy finding for END_REVIEW and a later change (the deploy is not undone for it). |
| O10 | Reaching the resting state locally | No product flag. The stage-8 dev server (stage 4 writes it under `runs/`, section 14.3) takes `--resting`, which builds `Settings(monthly_cap_usd="0.000001")`: the day's share (32 nano-dollars) is below the floor, so `GET /` shows the resting card. The same thing the existing `ASK_MONTHLY_CAP_USD` setting does in production; nothing new ships. |

## 3. Design per intent item: routes, data, files

### 3.0 The one renderer (applies to items 1, 2, 5 and 6)

Today every card is built twice: in `render.py` and in `enhance.js` (`STATES`, `showAnswer`, `showState`). After this slice, `render.py` is the only builder of anything that shows a result.

**The script's request (stage 5, `enhance.js`):**
```
fetch("/ask", { method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ question: q.value }),
  credentials: "omit", cache: "no-store", referrerPolicy: "no-referrer", redirect: "follow" })
  .then(res => res.text())
  .then(html => swap(new DOMParser().parseFromString(html, "text/html")))
  .catch(() => showNetworkError());
```
`swap(doc)`: replace the children of `#result-live` and `#result-extra` with imported copies of the parsed document's; set or remove `aria-labelledby` on `#result` exactly as the parsed `#result` has it; copy the parsed `#q-error` text and the presence of `aria-invalid` on `#q`; never touch the textarea's value (the question stays in the box on every outcome). Focus: `#q` if the parsed `#q-error` is non-empty, else `#result` (as today).

**Why this and not a new fragment route:**
- No new route reaches the judge, so INV-4's "no other route of the service reaches the judge" stays true with no new surface to review. A fragment route that took a question would be a second judge route (not allowed); one that took a result from the client would render text the server cannot vouch for.
- The page path already exists, is already reviewed, already writes the one abuse line, and already uses the PRG store; INV-4 already names it ("as its page for a form post or the page's own script").
- The JS-on and JS-off pages are then the same server HTML, so the "no model text", "only listed text" and accessibility tests run once and cover both.
- `/ask` JSON is no longer read by the page at all, which makes its byte-equality (section 8) trivially independent of the page work.

**Consequences, accepted:**
- The script no longer pre-checks empty or over-500 questions; the server answers them (no model call, no retrieval, one abuse line, as for a no-JS visitor today). The copy "Nothing was sent." already describes the no-JS case the same way.
- Every admitted JS question now puts its `AskResult` in the existing `ResultStore` (10 minutes, at most 1,000, no question text), as no-JS posts already do. Same data type, same bounds; listed for Security.
- `DOMParser` documents run no script; the server escapes every value; the CSP is unchanged.
- The waiting card and the network-error card stay JS-built (they have no server response). Their copy is W1 to W4 and the unchanged "We couldn't reach the service" card.

### 3.1 Answer card (item 1)

- **Route:** unchanged (`POST /ask` form path, `GET /result/{token}`).
- **Data:** only `AskResult.files` (path, passage heading, line range, permalink, text) and fixed copy. The Copy link button copies the source chip's `href` (the passage permalink already in the page).
- **Files:** `render.py` `_passages()` (stage 5), `enhance.js` copy handler, `style.css`.
- **Test:** T-A (section 10).

### 3.2 Refusal card (item 2, reduced by D1)

- **Route:** unchanged.
- **Data:** none from the request beyond the outcome. Fixed copy (title, body, F1, F2), the issue and docs URLs `HtmlPages` already builds, and the three answered suggestions (A1 to A3) from `suggestions.toml`. **No passage, path or line number** (INV-4(b), D1).
- **Files:** `render.py` (`STATES["no_confident_match"]` gains the hint and the docs link; refusal adds the suggestions and the drawer), stage 5.
- **Test:** T-R (intent test 1).

### 3.3 Suggested questions (item 3)

- **Data file:** `aveto_service/suggestions.toml` (new, stage 5), shipped by the existing `COPY aveto_service/` lines of the Dockerfile; no Dockerfile or `.dockerignore` change. Shape:
  ```toml
  # Four suggested questions, copied word for word from a spent eval set
  # (evals/ is not in the image). Chosen in runs/polished-chat-experience/05-tech-spec.md section 9.
  schema = 1
  [[suggestion]]
  slot = "A1"
  set = "evals/retrieval-heldout-5.toml"
  id = "g01"
  expect = "answer"
  text = "Does saying \"looks good\" to an agent count as approving something?"
  ```
  and A2 `g03`, A3 `g04` (`expect = "answer"`), R1 `gu18` (`expect = "no_confident_match"`). Exact texts in section 9.
- **Reader:** `pages.py` (stage 5) reads it with the standard library's `tomllib` at construction, like the static files today. Any reading or shape error means the suggestions block is not rendered (the page still works); a test on the committed file (T-Q) prevents shipping a broken one.
- **Markup:** per UX section 2 (one tiny form per suggestion, `method="post" action="/ask#result"`, hidden `question` input, `button.chip`). With JS the script loads the text into the box and does not send.

### 3.4 Honest waiting and the warm-up (item 4)

- **Waiting card:** JS only (W1 at 0 s, W2 at 8 s, W3 at 60 s, W4 elapsed line); no animation; the pulsing dot and its keyframes are removed (UX 1.5).
- **Route `POST /warm`** (registered only with a renderer, like the page routes):
  1. With the kill switch on, a cross-site request (`_cross_site`), or `service.resting()` true: answer `{"ready":false}` at once, no retrieval.
  2. Otherwise `await run_in_threadpool(service.warm)` and answer `{"ready":true}` or `{"ready":false}`.
  3. Status 200 either way, body exactly `{"ready":true}` or `{"ready":false}`, headers `_JSON_HEADERS` (the set `/ask` JSON and `/health` already use). The body is never read.
- **`AskService.warm() -> bool`** (`pipeline.py`, stage 4): under a new `self._warm_lock`, if no result is remembered, runs `judge.retrieve_for_judge(self._runtime.searcher, WARM_QUESTION)` under the existing `self._retrieval_lock`, discards the result, remembers `True` (or `False` on any exception, caught and not logged), and returns the remembered value. Later calls do no work. `WARM_QUESTION` is a module constant (proposed: `"How do I get started?"`); it is never a visitor's text.
- **What it never touches (and the proof):** `self._judge`, `self._spend`, `self._rate`, `self._retrievals`, `self._lock`, `emit_abuse`, `emit_ops`. Proof is test T-W (section 10): with a `FakeJudgeClient` and a `CountingEmbedder`, 21 calls make exactly one query embedding and zero judge calls; `/health` is byte-equal before and after; a visitor can still be admitted ten times in the hour afterwards; nothing is written to stdout; and the source of `AskService.warm` names none of the attributes above.
- **What it does for a visitor:** absorbs the first retrieval's cost in a fresh process, if any (unmeasured; stage 8 records the first and second `POST /warm` durations on a fresh local process). It cannot shorten the container start, which happens before `GET /` is answered.
- **Script:** on load, if `#ask-button` is not disabled, one `fetch("/warm", {method: "POST", credentials: "omit", cache: "no-store"})`; only on `{"ready":true}` it writes W0 into the empty Ready line. Failure shows nothing.

### 3.5 Resting state (item 5)

- **Route change, `GET /` (`app.py`, stage 4):**
  ```python
  state = Outcome.SERVICE_OFF if settings.kill_switch != "off" else (Outcome.PAUSED if service.resting() else None)
  counts.visit()
  return pages.page(state)
  ```
  The `HtmlRenderer.page(state)` signature is unchanged; `page(Outcome.PAUSED)` from `GET /` means "resting at load" (form disabled, card above the form, no suggestions; UX 1.4). A `PAUSED` result after a post still comes through `form_outcome` as today.
- **`AskService.resting() -> bool`** (`pipeline.py`, stage 4), a pure read under `self._lock`:
  ```python
  day = utc_day(self._clock()); s = self._spend
  today = s.day == day
  return (today and s.closed) or ((s.spent if today else 0) + self._floor > s.cap)
  ```
  It does not call `roll`, `peek`, `reserve` or a limiter, so it changes no counter; it calls no model and no retrieval. It is true only when settled spend already leaves no room for the smallest request, which can only stay true until midnight UTC, so "back after midnight UTC" is true whenever the card shows. (A transient refusal caused by in-flight reservations is not shown at load; a post in that moment still gets the existing `paused` card.)
- **Test:** T-S (intent test 2, end to end, stage 5 makes it pass) and T-S0 (app level, stage 4).

### 3.6 Receipts drawer (item 6, per D2)

- **Route:** none new; part of the answer and refusal result regions.
- **Data, all already held for this request:** the outcome (as one of the two existing titles); the docs commit from the runtime index (first 7 hex, linking to the docs tree URL `HtmlPages` already builds); for an answer, the count and each listed passage as "{path}, {line X / lines X to Y}" linking to that passage's permalink from `AskResult`; for a refusal, D5. Plus two static links (Charter, run record) from `scorecard.toml` `[links]` when present (O6). **Not shown:** `signal`, the prompt name or hash, any score, any text the result does not hold.
- **Nothing stored:** the drawer re-renders from the `AskResult` the page already has; `AskResult`'s fields do not change (T-D asserts the field list); the `ResultStore` stores what it stored before.
- **Files:** `render.py` (stage 5); `pages.py` gets the two links from `aveto_service.scorecard.build_links()` (stage 4 provides it; stage 5 calls it).
- **Test:** T-D (intent test 4).

### 3.7 Quality scorecard (item 7)

**Route `GET /scorecard`** (registered only with a renderer). Server-rendered, no script, the one stylesheet link, headers exactly `SECURITY_HEADERS` (imported from `pages.py`, not copied). Status 200; **503** with the S6 card when the figures file could not be read (a committed-file test makes that a broken build, not a runtime event). Layout and copy: UX 1.7 and 1.8.

**Module `aveto_service/scorecard.py`** (new, stage 4): `load_figures(path) -> Figures` (strict reader), `build_links(path) -> dict[str, str]` (the Charter and run-record links for the drawer; `{}` on any error), and `ScorecardPage(runtime, path=FIGURES_PATH)` with `response(usage: UsageSnapshot) -> Response`. `create_app` builds one `ScorecardPage(runtime)` when a renderer is given (overridable by a keyword argument for tests), so `main.py` and the `HtmlRenderer` protocol do not change (`test_main_module_composes_the_app` pins `main.py`).

**Figures file `aveto_service/scorecard.toml`** (new; committed; in the image through the existing `COPY aveto_service/`; read once at startup). Recorded figures only:
```toml
# Recorded figures only. Every row names the repository file that records it.
# A row with no record is not written here, so it is not shown.
schema = 1
source_base = "https://github.com/gpatwa/aveto-support/blob/claude/interesting-shannon-67bff6/"  # optional

[[figure]]
section = "speed"                      # speed | checks | reviews
label = "Cold start"                   # one of the UX copy deck's S7 labels for that section
value = "30.8 s"
basis = "Measured 2026-10-22 on an earlier release (revision 0000006): ..."   # starts "Measured " or "Recorded "
record = "runs/public-ask-the-docs/18-gate/RESULT.md"                         # repo path of the record
# findings = ["..."]                   # only for "Independent Codex review"

[[decision]]
who = "The owner"
when = "2026-10-26"
what = "..."
record = "runs/polished-chat-experience/intent.md"

[links]                                # optional; each key optional; every value https://github.com/...
pull_request = "..."
charter = "..."
event_log = "..."
end_review = "..."
cost_and_time = "..."
owner_decisions = "..."
run_record = "..."
```
**Reader rules (fail closed; any violation makes the whole file unreadable, so the page shows S6):** top-level keys only those above, `schema = 1`; `section` in `{speed, checks, reviews}`; `label` in that section's S7 labels (Speed: Cold start, Warm response time, Cost per question; Checks: Accessibility checks, Mobile checks (375 px), Tests, Open findings; Reviews: Independent Codex review), so no row can carry a label the owner has not seen in the copy deck (C1.6); `value` a non-empty single line of at most 120 characters; `basis` starts with `Measured ` or `Recorded `, at most 300 characters; `record` a relative POSIX path matching `^[A-Za-z0-9._/-]+$` with no `..` segment; `findings` only on the Codex row, each at most 300 characters; `when` is `YYYY-MM-DD`; `who` at most 40 characters, `what` at most 300; every URL (each `[links]` value and `source_base`) starts with `https://github.com/` and contains no whitespace, `"`, `<` or `>`; `source_base` ends with `/`. A row's "Source" link is `source_base + record` when `source_base` is present. Rows with the same label are allowed (a local and a live figure), each with its own basis.

**"No record, not shown", enforced three ways:** the reader refuses a row without `record` and `basis`; test T-F2 checks that every `record` path in the committed file exists in the repository (`(REPO_ROOT / record).is_file()`); the renderer emits a row only for a row in the file, a section only if it has a row, "Who decided what" only if there is a decision, "How this was built" items only for present links, S5 when there is no row and no decision at all. No placeholder text, dash or "n/a" is ever rendered (T-F3).

**Service-own measurements: the counts and the start time only.** The plan's design note says figures only the service can know are reported from its own measurements. I read that as a rule for whatever the service reports, not as a requirement to add latency or cold-start instruments, and I do not add them, because: an in-process "cold start" cannot see the container scheduling, image pull and process start a visitor waits through (30.8 s recorded), so it would show a much smaller figure under the copy deck's label "Cold start"; a server-side latency excludes the network and would sit beside the client-side live record under the same label "Warm response time"; and both would add state and code to a page whose rule is "no figure without a record". Cold and warm timings come from recorded measurements (section 11, C1.4.5), with date and method in the basis. **Flag for the Orchestrator (not a stop):** if you read the plan's note as requiring in-service timing, say so and it becomes a stage 4 item (a deque of the last 100 server-side durations of answered or refused questions, median and slowest, shown with "Measured inside the service since it last started" as basis).

**Rows known now, written by stage 4 into the initial file** (each record exists today; I read them):

| section | label | value | basis | record |
|---|---|---|---|---|
| speed | Cold start | `30.8 s` | `Measured 2026-10-22 on an earlier release (revision 0000006): time to the first answer from /health after more than an hour with no replica running, from one client.` | `runs/public-ask-the-docs/18-gate/RESULT.md` |
| speed | Warm response time | `1.66 s median, 5.09 s slowest` | `Measured 2026-10-22 on an earlier release (revision 0000006): 20 questions sent one after another from one client, network included.` | `runs/public-ask-the-docs/18-gate/RESULT.md` |
| speed | Cost per question | `$0.00785` | `Measured 2026-10-22 on an earlier release: 20 questions, token counts reported by the API, priced at the published $2 per million input and $10 per million output tokens (read 2026-10-23).` | `runs/public-ask-the-docs/18-gate/RESULT.md` |

Decisions known now (each `who`, `when`, `what`, `record`):
1. `The owner`, `2026-10-26`, `Kept the service on its own address; aveto.dev links to it instead of showing it inside the site.`, `runs/polished-chat-experience/intent.md`
2. `The owner`, `2026-10-26`, `Made a rehearsed rollback a release gate: roll back to the previous version, check it, time it, roll forward.`, `runs/polished-chat-experience/intent.md`
3. `The owner`, `2026-10-26`, `Approved the Charter for this build: its scope, budget, models and the actions the run may take.`, `runs/polished-chat-experience/APPROVAL_RECORD-1.md`
4. `The Orchestrator`, `2026-10-26`, `The refusal card shows no passages, because the service shows passages only when the docs answer.`, `runs/polished-chat-experience/DECISIONS.md`
5. `The Orchestrator`, `2026-10-26`, `The receipts show the outcome, the docs version and the listed passages, and no internal decision line.`, `runs/polished-chat-experience/DECISIONS.md`

**Rows added before the build (the "figures fill", after stage 9, before stage 11):** Tests (stage 7: `N passed, 0 failed`, basis `Measured <date> on the final code: uv run pytest, mypy and ruff clean.`, record `runs/polished-chat-experience/07-qa-evidence.md` or the file QA names); Accessibility checks (stage 8: `0 serious or critical issues on 5 views`, basis naming axe-core's pinned version and the five views, record the stage 8 file); Mobile checks (375 px) (stage 8: `No sideways scrolling on 5 views; every control at least 24 by 24 px`); Warm response time, local (stage 8: `<median> s median, <slowest> s slowest`, basis `Measured <date> on a local run of this release with a stand-in for the model, 10 questions one after another: the service's own work, without the model call.`); Open findings (stages 6 and 9: `No open P0 or P1 finding; <k> lower findings listed`, record `code-review.md` and the Security review file). `[links]` and `source_base` are written only if section 12.0 confirms the repository is public; link values:
- `pull_request`: `https://github.com/gpatwa/aveto-support/pulls?q=is%3Apr+head%3Aclaude%2Finteresting-shannon-67bff6` (a search that lists this branch's pull request once stage 14 opens it; the number is not known at build time)
- `charter`: `https://github.com/gpatwa/aveto-support/blob/claude/interesting-shannon-67bff6/runs/polished-chat-experience/CHARTER.md`
- `owner_decisions`: `https://github.com/gpatwa/aveto-support/blob/claude/interesting-shannon-67bff6/runs/polished-chat-experience/APPROVAL_RECORD-1.md`
- `end_review` and `cost_and_time`: `https://github.com/gpatwa/aveto-support/blob/claude/interesting-shannon-67bff6/runs/polished-chat-experience/END_REVIEW.md` (written at stage 14; it holds cost and time)
- `event_log`: the event-log summary file stage 11 writes, at the same ref (the Release Manager names the path before the fill; if no such file is named, the key is left out)
- `run_record`: `https://github.com/gpatwa/aveto-support/tree/claude/interesting-shannon-67bff6/runs/polished-chat-experience`

Rows that enter only by a later change (they do not exist before the image is built): this run's live cold start, live warm timing, rollback rehearsal time, the live cost per question, and the Codex review (only after the owner records it). Stage 13 records them in `runs/`; the pull request lists them.

**Who writes the fill.** The Tech Writer's write scope does not include `aveto_service/` (`.claude/hooks/write-scope-guard.mjs`). Recommended: the Tech Writer lists the rows (value, basis, record) in `runs/polished-chat-experience/10-figures.md` at stage 10, and the Orchestrator re-spawns the Backend Architect for one narrow edit of `aveto_service/scorecard.toml` (about 15k); the Release Manager at stage 11 checks every row against its record and re-runs the full suite (T-F2 checks the records exist). The plan already says these figures go into the committed file before the build, so this is who does a planned step, not a new step. The Orchestrator rules.

### 3.8 Counts without content (item 8)

**Module `aveto_service/counts.py`** (new, stage 4):
```python
DOCS_CLICKS_PER_HOUR = 60
MAX_BEACON_BODY_BYTES = 64

@dataclass(frozen=True)
class UsageSnapshot:
    visits: int
    answered: int
    refused: int
    docs_clicks: int
    started_at: datetime          # UTC, when create_app built this app (process start in production)
    @property
    def asked(self) -> int: return self.answered + self.refused

class UsageCounts:
    __slots__ = ("_lock", "_visits", "_answered", "_refused", "_docs_clicks", "_started_at", "_clicks", "_mono")
    def __init__(self, started_at: datetime, monotonic: Callable[[], float]) -> None: ...
    def visit(self) -> None: ...                        # +1 visits
    def record(self, outcome: Outcome) -> None: ...     # +1 answered on ANSWER, +1 refused on NO_CONFIDENT_MATCH, else nothing
    def docs_click(self) -> bool: ...                   # +1 docs_clicks if fewer than 60 counted in the rolling hour; returns whether counted
    def snapshot(self) -> UsageSnapshot: ...
```
`_clicks` is a `limits.RateLimiter(limit=60, window=3600.0, max_keys=1)` used with one constant key (`"docs"`): timestamps only. **What exactly is stored:** four integers, one UTC datetime, at most 60 monotonic floats. No question, no passage, no address, no hashed key, no outcome list, no time per event. Every method takes only an `Outcome` or nothing, so no caller can hand it text (mypy enforces the signatures).

**Where it is called (`app.py`, stage 4):** `counts.visit()` in `GET /` (every state, including off and resting); `counts.record(result.outcome)` in `POST /ask` right after `service.ask` returns, for both JSON and form requests (so "Questions asked" means questions that reached an answer or a refusal, the UX basis text); `counts.docs_click()` in the beacon route. Not called on `/result/{token}`, `/static`, `/warm`, `/scorecard`, `/health`. The app keeps the object at `app.state.counts`.

**Route `POST /count/docs-click`** (registered only with a renderer): kill switch on, `_cross_site(request)`, a declared `content-length` other than `0`, or any body byte read (reading stops after 64 bytes) means "not counted"; otherwise `counts.docs_click()`. Always `Response(status_code=204, headers=_JSON_HEADERS)`. Never a log line. The script sends it with `navigator.sendBeacon("/count/docs-click")` (no data) on click of the links marked `data-count="docs"` (the "Read the docs on GitHub" links on the ask page: footer and cards). Source chips are not counted: the UX basis text says "the docs link".

**"Since the service last started":** the counts live in the process. Every revision change, restart and scale to zero resets them (D1 of an earlier slice keeps that out of scope). The page says so (N1) and shows the start time (N2) from `started_at`. With about five internal customers and scale to zero, small numbers and zeros are normal; a 0 is shown as "0" because the service did count it.

**Visits are page loads, not people.** Anyone can raise "Visits" by reloading; the basis text says "Each load of the ask page counts once", which stays true. Clicks are capped at 60 an hour, so an automated client can add at most 60 an hour; under normal use the cap never binds.

## 4. Data model deltas

No database, no disk write, no migration. All new state is in memory or in committed read-only files.

| Type / file | Change | Rationale |
|---|---|---|
| `AskResult` (`pipeline.py`) | **unchanged** (fields `outcome, docs_repo, docs_commit, files, signal, length`; `to_json()` unchanged) | C1.4.1; T-D pins the field list |
| `AskService` (`pipeline.py`) | new private `_warm_lock`, `_warm_result: bool | None`; new methods `resting()`, `warm()` | Items 4 and 5 |
| `UsageCounts`, `UsageSnapshot` (`counts.py`) | new | Item 8; section 3.8 |
| `Figures`, `Figure`, `Decision`, `ScorecardPage` (`scorecard.py`) | new | Item 7; section 3.7 |
| `aveto_service/scorecard.toml` | new, committed | Recorded figures, decisions, build links |
| `aveto_service/suggestions.toml` | new, committed | Item 3; section 9 |
| `ResultStore` | unchanged code; now also holds results of JS-path questions | Section 3.0 |
| `SECURITY_HEADERS`, `_JSON_HEADERS`, `STATIC_TYPES` | **unchanged** | C5.0; no new static file (the scorecard page has no script) |
| `Settings`, `infra/main.bicep`, `Dockerfile`, `.dockerignore` | **unchanged** | No new setting, resource or build step |

## 5. Service surface

| Function | Signature | Invariant |
|---|---|---|
| `pipeline.py:AskService.resting` | `() -> bool` | Pure read under `_lock`; no `roll`/`peek`/`reserve`, no limiter, no retrieval, no judge, no log line. True only if today's day is closed or settled spend plus the floor exceeds the cap |
| `pipeline.py:AskService.warm` | `() -> bool` | At most one retrieval of `WARM_QUESTION` per process, under `_retrieval_lock`; never `_judge`, `_spend`, `_rate`, `_retrievals`, `_lock`, `emit_abuse`, `emit_ops`; exceptions caught, result remembered |
| `counts.py:UsageCounts.visit / record / docs_click / snapshot` | see 3.8 | Integers only; `record` ignores every outcome but `ANSWER` and `NO_CONFIDENT_MATCH`; `docs_click` counts at most 60 in a rolling hour |
| `scorecard.py:load_figures` | `(path: Path = FIGURES_PATH) -> Figures` | Raises `FiguresError` on any rule in 3.7; reads nothing but the one file |
| `scorecard.py:build_links` | `(path: Path = FIGURES_PATH) -> dict[str, str]` | Returns `{"charter": ..., "run_record": ...}` (each only if present) or `{}` on any error; never raises |
| `scorecard.py:ScorecardPage.response` | `(usage: UsageSnapshot) -> Response` | Headers exactly `SECURITY_HEADERS`; 200, or 503 with S6 when the file was unreadable at construction; output contains no question text (it receives none) |
| `app.py:create_app` | adds keyword `scorecard: ScorecardPage | None = None` (default: built from `runtime` when `html` is given) | `main.py` unchanged; with no renderer, no new route exists |
| `html_port.py:HtmlRenderer` | **unchanged** | `page(Outcome.PAUSED)` now also arrives from `GET /` |
| `pages.py:HtmlPages` | constructor stays callable as `HtmlPages(runtime)` (new keyword-only arguments with defaults allowed) | Stage 5 |

### Route inventory after this slice

| Route | Registered | Reaches the judge | Runs retrieval | Changes state | Response headers |
|---|---|---|---|---|---|
| `POST /ask` | always | **yes (the only one)** | yes | as today, plus `counts.record(outcome)` | unchanged (`_JSON_HEADERS` for JSON; `SECURITY_HEADERS` for the page) |
| `GET /health` | always | no | no | no (as today) | unchanged |
| `GET /` | with renderer | no | no | `counts.visit()`; reads `resting()` | `SECURITY_HEADERS` |
| `GET /result/{token}` | with renderer | no | no | no | `SECURITY_HEADERS` |
| `GET /static/{name}` | with renderer | no | no | no | `SECURITY_HEADERS` (still two files) |
| `GET /scorecard` | with renderer | no | no | no (reads a snapshot) | `SECURITY_HEADERS` |
| `POST /warm` | with renderer | no | once per process, fixed text | warm flag only | `_JSON_HEADERS` |
| `POST /count/docs-click` | with renderer | no | no | `docs_click` (bounded) | `_JSON_HEADERS`, 204, no body |

Trailing-slash variants stay 404 (`redirect_slashes=False`). `GET /ask` stays 405.

## 6. Adapter boundaries

| Boundary | Default adapter | Placeholder behaviour |
|---|---|---|
| Answerability judge (`judge_port.JudgeClient`) | `AnthropicJudgeClient` when a key is set | `PlaceholderJudgeClient` raises `JudgeNotConfiguredError` ("answerability judge LLM adapter is not configured in this build."). **Unchanged.** The new routes do not hold a reference to it: `warm()` and `resting()` are methods on the service that never read `self._judge`, and the counts and scorecard objects are built without it |
| Embedding (`aveto_support.embed`) | `OnnxEmbedder` | `PlaceholderEmbedder` raises. **Unchanged.** `warm()` uses it through the existing `Searcher`, exactly as `/ask` does |
| HTML (`html_port.HtmlRenderer`) | `HtmlPages` | Without a renderer, no page route exists, including the three new ones (as today for `/`, `/result`, `/static`) |

No new model, no new external call. The scorecard and drawer link to GitHub as plain hyperlinks the visitor may click; the service itself makes no request to GitHub.

## 7. Audit, feedback and usage events

The service's only log events are the abuse line and three fixed ops codes (`abuse_log.py`); `test_abuse_line_shape_exact` pins the abuse line. **This slice adds no log event, no outcome value and no ops code.** The state-changing functions and what records them:

| State change | Emitted from | Record |
|---|---|---|
| Question answered or refused (existing) | `pipeline.py:AskService._finish` | the existing abuse line `{"t","ip","o"}`, unchanged, one per `POST /ask` |
| `counts.record` (usage) | `app.py` `POST /ask` | in-memory counter only; shown as a total on `/scorecard`; no log line (a log line per count would be a new event and a new log shape) |
| `counts.visit` (usage) | `app.py` `GET /` | in-memory counter only |
| `counts.docs_click` (usage) | `app.py` `POST /count/docs-click` | in-memory counter only |
| `AskService.warm` (warm flag) | `app.py` `POST /warm` | none; the flag is visible only as `{"ready":...}` |

The usage events are deliberately not audit events: the intent asks for counts "computed in the service" with "no identifiers beyond what the service already keeps", and the Charter's "no question is stored or logged" rules out per-event lines. The audit trail for the deploy itself is the run record (section 12).

## Integration points

- `aveto_support.judge.retrieve_for_judge` (unchanged) — called by `warm()` with a fixed question.
- `aveto_service.limits.RateLimiter`, `utc_day` (unchanged) — the click limit and `resting()`'s day.
- `AskService` (extended, not wrapped), `HtmlPages` (extended by stage 5), `ResultStore` (unchanged), `abuse_log.Outcome` (unchanged).
- Standard library only: `tomllib` (both data files), `html.parser` (tests). **No new dependency.**

## 8. `/ask` JSON stays byte-identical: the argument and the test

**Why it holds by construction.** The JSON body is `JSONResponse(result.to_json(), status_code=result.status, headers=_JSON_HEADERS)` (`app.py` `_json`). This slice changes none of `AskResult`, `to_json`, `_STATUS`, `_JSON_HEADERS`, `_json`, the gate order in `AskService._ask`, `_judged`, `validate_question`, `_question_of`, `_read_body`, `_cross_site`, or anything under `aveto_support/` or `prompts/`. The extras the page needs travel elsewhere:

| Extra | Carried by | Not by |
|---|---|---|
| Card markup, hint, suggestions, drawer, resting card | the server-rendered page (`GET /`, `GET /result/{token}`, the form post's HTML responses) | `/ask` JSON |
| Docs commit for the drawer | `HtmlPages` from the runtime index | `/ask` JSON |
| Counts | `GET /scorecard` HTML | `/ask` JSON, `/health` |
| Ready state | `POST /warm` | `/ask` JSON |
| Build links | `scorecard.toml`, rendered in the drawer and the scorecard | `/ask` JSON |

The only change on the `POST /ask` path is one call, `counts.record(result.outcome)`, after the result exists and before the response is built; it takes the outcome enum and returns nothing.

**The test (T-B, `tests/test_service_ask_bytes.py`, stage 4; a guard, it must pass on 32e54a6 and on the final tree).**

- **Golden:** `tests/golden/ask-json-32e54a6.json`, written by the same module run as a script, `uv run python tests/test_service_ask_bytes.py --write-golden`, in stage 4's first commit, when `git diff --exit-code 32e54a6 -- aveto_service aveto_support prompts` is empty (that output is saved beside it, section 14.1). Format: `{"base": "32e54a6", "cases": [{"id", "status", "headers": [[name, value], ...], "body": "<UTF-8 text>"}]}`; headers are `response.headers.raw` decoded as latin-1, in order.
- **Harness:** each case builds a fresh app with `service_fakes.make_app` (fake runtime `make_runtime()`, `FakeClock()`, no renderer: the JSON route does not depend on one), a `TestClient(app, client=("203.0.113.7", 5000))`, and one `FakeJudgeClient` whose reply the case fixes. Fresh app per case, so no limit state carries over.
- **The fixed question set (12, from spent eval sets, read by id from the eval files at test time):** `evals/retrieval-heldout-5.toml` `g01`, `g03`, `g04`, `gu15`, `gu18`; `evals/public-gate-1.toml` `p01`, `p05`, `p06`, `p11`, `p12`, `p17`, `p20`. Each is sent twice, once with the judge reply `Q1 ANSWERABLE` + a reason and once with `Q1 NOT_ANSWERABLE` + a reason, so every question yields one `answer` body (with that question's retrieval) and one `no_confident_match` body: 24 cases. Both sets are spent: `retrieval-heldout-5` was scored once at docs-answerability-2 stage 7 and its intent and monitoring plan call it spent (`runs/docs-answerability-2/11-monitoring-plan.md` line 71); `public-gate-1` was scored once through the deployed service on 2026-10-22 (`runs/public-ask-the-docs/18-gate/RESULT.md`). Not used: `retrieval-heldout-5-reserves.toml` (its header: never run or scored unless a replacement was needed, so not spent) and `calibration-offtopic.toml` (not an eval set; it calibrates the index).
- **Outcome cases (12 more, fixed inputs):** `{"question": ""}`; `{"question": "   "}`; 501 × `a`; `{"question": "?!"}`; `{"question": "x", "x": 1}`; `{"question": 5}`; `["question"]`; a 20,000-byte body; reply `garbage` (judge_error); an over-4,096-byte reply; the 11th question in an hour (rate_limited); a question after `app.state.service._spend.cap = 0` (paused); one with `make_settings(kill_switch="on")` (service_off); one with `Origin: https://evil.example` (bad_request). Plus `GET /health` after one answered question.
- **Assertions:** for every case, `r.status_code == case["status"]`, `r.content == case["body"].encode("utf-8")`, and `[(k.decode("latin-1"), v.decode("latin-1")) for k, v in r.headers.raw] == case["headers"]`; and the case ids equal the golden's ids (no case silently dropped).
- **Second proof, at stage 7 (QA):** the golden's provenance: `git log --diff-filter=A --format=%H -- tests/golden/ask-json-32e54a6.json` gives commit X; `git diff --exit-code 32e54a6 X -- aveto_service aveto_support prompts` must print nothing. Then the test passes on the final tree. Together these are C1.4.1's "bodies from `main` and from the branch, offline, same fake judge, byte-equal".

**Headers byte-identical (T-H, same file, guard plus the new routes):**
```python
EXPECTED_SECURITY = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}
assert pages.SECURITY_HEADERS == EXPECTED_SECURITY
assert app_module._JSON_HEADERS == {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
```
and, with a renderer: for each HTML response (`GET /`, `GET /` with the kill switch on, `GET /` resting, a result page, an unknown token, form posts with an empty, a too-long and a rate-limited question, `/static/style.css`, `/static/enhance.js`, `/static/nope.txt`, `GET /scorecard`), every `EXPECTED_SECURITY` header is present with exactly that value, and the set of header names is exactly those four plus `content-type` and `content-length` (plus `location` on a 303); no `set-cookie`. For `POST /warm`: names exactly `cache-control`, `x-content-type-options`, `content-type`, `content-length`. For `POST /count/docs-click`: status 204, `r.content == b""`, names exactly `cache-control`, `x-content-type-options`.

## 9. The four suggested questions: choice and evidence

**Chosen (texts copied word for word from `evals/retrieval-heldout-5.toml`, pinned commit `3a83b669...`, the same commit `docs-source.toml` pins):**

| Slot | Id | Text | Chars | Expected |
|---|---|---|---|---|
| A1 | g01 | `Does saying "looks good" to an agent count as approving something?` | 67 | answer |
| A2 | g03 | `Can I keep a long-lived feature branch going while the agents work on it?` | 73 | answer |
| A3 | g04 | `If a deploy of the Aveto website goes wrong, how do I undo it?` | 62 | answer |
| R1 | gu18 | `Does it support right-to-left languages?` | 40 | no confident match |

All under 90 characters, plain text, English, no personal data. Reserves (used only by a later change if a live check disagrees): answered `p05` "Will an agent ever force-push to a shared branch without checking with me?", `p01`; refused `gu15` "Who founded Aveto?", `p12`.

**Spent, not in use.** `retrieval-heldout-5` is the fifth held-out set, scored once (docs-answerability-2 stage 7), called spent in that slice's monitoring plan; no later slice registered it as a gate. These four were also sent once through the live service on 2026-10-24 by fix-service-accounting's smoke, so their exposure to the live judge is not new.

**Evidence that they behave as labelled, and what kind each piece is:**

| Evidence | What it shows | Kind |
|---|---|---|
| docs-answerability-2 stage 7 (`07-gate-scoring.md` lines 56 to 62): retrieval misses were g05, g06, g18, g19, g22 | **Offline retrieval** put a labelled source in the top 5 for g01, g03, g04 at the pinned commit | recorded offline run (deterministic retrieval; same `aveto_support` code, pinned by `test_core_files_unchanged`) |
| Same file: verdicts differing from the key were only g09, g10, g24; no unanswerable question differed | The attended judge (same model, same prompt) said ANSWERABLE for g01, g03, g04 and NOT_ANSWERABLE for gu18 | recorded model verdicts, one call each, attended path |
| `runs/fix-service-accounting/10-smoke/smoke-result.json` (2026-10-24, revision `ca-aveto-ask--0000008`, image `d067b9a95ac6`, the current live revision) | Live API: g01, g03, g04 `answer`, each **byte-equal** to local `retrieve`; gu18 `no_confident_match`; index sha256 `f36ef5d4...a756` | recorded live run, one call each, the exact build this slice replaces |
| Fresh offline retrieval run (stage 4, section 14.1 step 2) | Will show again whether a labelled source is in the top 5 for A1 to A3, and record R1's top files | **not yet run**; I could not run it |

**What is not evidence.** Offline retrieval never abstains (INV-4), so no offline run can show that R1 is refused; only the judge decides that, and the judge is not callable offline. The model's verdict on a given day is not guaranteed by one past call: the public gate saw 2 of 10 answerable questions refused (over-abstention). So "three are answered and one is not" (copy G2/G3) rests on the three recorded observations above and is re-checked live at stage 13 (section 12.4). If at stage 13 an A question is refused or R1 is answered with passages, the rule is fixed now: neither is one of C8.1's behaviour failures (the passages shown are still `retrieve`'s, and the judge, prompt and model are unchanged, so the previous revision would answer the same way; rolling back would not change it). Both are reported as measured. An A question refused is a P2 finding for END_REVIEW (a known judge behaviour). R1 answered with passages is reported to the owner in END_REVIEW as the first item, with the recommendation to swap R1 for reserve `gu15` by a later change, because the page's hint G2/G3 would then promise a refusal the visitor does not see. Whether that warrants the kill switch is not decided by the run: C8.3 allows `killSwitch=on` only when C8.1 requires it, and C8.1 does not cover this case.

## 10. Tests: every fail-first test and guard, with the exact assertion

### 10.0 Conventions

- All tests are offline (the autouse network block in `tests/conftest.py`), use `tests/service_fakes.py` (`make_app`, `make_runtime`, `FakeJudgeClient`, `CountingEmbedder`, `FakeClock`, `CANARY`, `DOCS`, `ANSWERABLE_REPLY`, `NOT_ANSWERABLE_REPLY`), and go through the HTTP surface with `fastapi.testclient.TestClient(app, client=("203.0.113.9", 5000), follow_redirects=False)`.
- **`tests/test_page_cards.py` must collect on 32e54a6:** it imports only `service_fakes`, `fastapi.testclient`, the standard library, `aveto_service.pages.HtmlPages`, `aveto_service.pipeline` (`AskResult`, `TOP_OF_FILE`), `aveto_service.judge_port.JudgeCall`, and `aveto_support.judge`. Everything new is reached over HTTP, so on 32e54a6 each test fails on an assertion, not at import.
- Helper (in `test_page_cards.py`, and a copy in stage 4's scorecard tests): `ResultText(html.parser.HTMLParser)` with `convert_charrefs=True`, fed the whole document once. Inside the element with `id="result"` it records (a) **text runs**: the data between two tags, concatenated, stripped, empty runs dropped; (b) whether a run is inside `pre`; (c) every `href`; (d) the same three for the subtree of `details.receipts`. `followed(client, text)` posts the form and GETs the 303 target, as in `test_service_pages.py`.
- Fixed strings (from the UX copy deck and section 9): `F1 = "Rephrasing can help: name the command, setting or feature you mean, and ask about one thing at a time."`, `F2 = "Questions the docs do answer"`, `REST1 = "Ask the Docs is back after midnight UTC."`, `REST3 = "Questions open again after midnight UTC."`, `CAPTION = "Quoted from the docs, word for word"`, `COPY = "Copy link"`, `D1 = "How this answer was made"`, `D2 = "How this result was made"`, `D5 = "None. Nothing is listed when the docs don't answer."`, `D7 = "Read the Charter for this build (the plan approved before it was built)"`, `D8 = "Read the run record"`, `G1 = "Try a question"`, the four suggestion texts `SA1`, `SA2`, `SA3`, `SR1` (section 9), `MODEL_CANARY = "zqxmodelwords5521"`, `QUESTION = "how do I install the tool"`.
- `c7 = runtime.searcher.index.commit[:7]`; `docs_url = f"https://github.com/{idx.repo}/tree/{idx.commit}"`; for a passage, `span` = `line X` or `lines X to Y`, `Span` = `Line X` or `Lines X to Y`, `heading` = `" > ".join(heading_path)` or `TOP_OF_FILE`.

### 10.1 The four intent tests (fail first on 32e54a6; C1.4.7)

**T-R `test_page_cards.py::test_refusal_card_shows_no_model_written_text`** (intent test 1; C1.4.2 second half). Judge reply `f"Q1 NOT_ANSWERABLE {MODEL_CANARY}"`; `page = followed(client, QUESTION)`.
```python
assert MODEL_CANARY not in page
for s in ("Deciding signal", "NOT_ANSWERABLE", "answerability-judge-v1", judge.PROMPT_SHA256):
    assert s not in page
assert pre_runs == [] and 'class="passages"' not in result_html
assert not any(path in result_html for path in DOCS)
required = {"The docs don't answer this",
            "No confident match was found, so nothing is shown. You can change your question and ask again, or open a GitHub issue.",
            F1, "Open a GitHub issue", "Read the docs on GitHub", F2, SA1, SA2, SA3,
            D2, "Outcome", "Docs version", f"Commit {c7} on GitHub", "Passages listed", D5}
assert required <= set(runs) <= required | {D7, D8}
assert SR1 not in runs
```
Fails on 32e54a6: F1, F2, the docs link, the suggestions and the drawer are missing. (On 32e54a6 the card already holds no model text; the test fails first because it pins the whole new card, which is the only way a "no model text" test can fail before the change. Stated so no one reads the failure as a defect on `main`.)

**T-S `test_page_cards.py::test_resting_state_at_the_cap`** (intent test 2). Two variants.
```python
# (a) the day's share cannot fit one more request
embedder = CountingEmbedder(); client, fake, runtime = make_client(runtime=make_runtime(embedder=embedder))
service = client.app.state.service
service._spend.cap = service._floor - 1
before = client.get("/health").json()
r = client.get("/"); text = html.unescape(r.text)
assert r.status_code == 200
assert "Paused for today" in text and REST1 in text and REST3 in text
assert ("Ask the Docs has a daily limit and today's has been used. This is not a fault. "
        "You can read the docs on GitHub or open an issue.") in text
assert has_attr(r.text, tag="textarea", id="q", attr="disabled")
assert has_attr(r.text, tag="button", id="ask-button", attr="disabled")
assert G1 not in text and SA1 not in text
assert text.count("Read the docs on GitHub") == 2
assert 'role="alert"' not in text and "state-error" not in text
assert client.get("/health").json() == before
assert fake.calls == [] and embedder.queries == 0
# (b) the day closed by a refused reservation, then a page load
client2, fake2, _ = make_client(); s2 = client2.app.state.service
s2._spend.cap = s2._floor          # peek passes, the two-attempt reservation closes the day
assert "Paused for today" in html.unescape(post_form(client2, QUESTION).text)
r2 = client2.get("/")
assert REST1 in html.unescape(r2.text) and has_attr(r2.text, tag="textarea", id="q", attr="disabled")
assert fake2.calls == []
```
Fails on 32e54a6: `GET /` shows the ordinary page.

**T-C `test_service_counts.py::test_counts_record_no_question_text`** (intent test 3; stage 4 makes it pass).
```python
fake = FakeJudgeClient([JudgeCall(ANSWERABLE_REPLY, 2400, 20), JudgeCall(NOT_ANSWERABLE_REPLY, 2400, 20)])
runtime = make_runtime(); app = make_app(fake, runtime=runtime, html=HtmlPages(runtime))
c = TestClient(app, client=("203.0.113.9", 5000), follow_redirects=False)
secret = f"{QUESTION} {CANARY}"
assert c.get("/").status_code == 200
assert c.post("/ask", json={"question": secret}).json()["outcome"] == "answer"
assert c.post("/ask", content=urlencode({"question": secret}), headers=FORM).status_code == 303
r = c.post("/count/docs-click"); assert (r.status_code, r.content) == (204, b"")
r = c.post("/count/docs-click", content=CANARY.encode()); assert (r.status_code, r.content) == (204, b"")
snap = app.state.counts.snapshot()
assert (snap.visits, snap.asked, snap.answered, snap.refused, snap.docs_clicks) == (1, 2, 1, 1, 1)
assert all(type(getattr(snap, f)) is int for f in ("visits", "answered", "refused", "docs_clicks"))
assert CANARY not in repr(snap)
assert set(type(app.state.counts).__slots__) == {"_lock", "_visits", "_answered", "_refused",
                                                 "_docs_clicks", "_started_at", "_clicks", "_mono"}
page = c.get("/scorecard"); assert page.status_code == 200
assert CANARY not in page.text and QUESTION not in page.text
rows = figure_rows(page.text)   # dt text -> dd.value text, from the counts section
assert [rows[k] for k in ("Visits", "Questions asked", "Answered", "Not answered", "Clicks to the docs")] == ["1", "2", "1", "1", "1"]
```
Fails on 32e54a6: `/count/docs-click` is 404.

**T-D `test_page_cards.py::test_receipts_drawer_shows_only_what_the_service_held`** (intent test 4).
```python
# answer
page = followed(client, QUESTION); exp = judge.retrieve_for_judge(runtime.searcher, QUESTION)
listed = [(f.path, m) for f in exp.files for m in f.passages]; n = len(listed)
assert drawer_count(page) == 1                     # exactly one details.receipts inside #result
req = {D1, "Outcome", "The docs answer this", "Docs version", f"Commit {c7} on GitHub",
       "Passages listed", str(n)} | {f"{p}, {span(m)}" for p, m in listed}
assert req <= set(drawer_runs) <= req | {D7, D8}
own = {m.url for _, m in listed} | {docs_url}
assert own <= set(drawer_hrefs)
assert all(h in own or h.startswith("https://github.com/gpatwa/aveto-support/") for h in drawer_hrefs)
assert not any(w in " ".join(drawer_runs).lower() for w in ("judge", "verdict", "signal", "score", "model"))
# refusal
req = {D2, "Outcome", "The docs don't answer this", "Docs version", f"Commit {c7} on GitHub", "Passages listed", D5}
assert req <= set(drawer_runs) <= req | {D7, D8}
assert all(h == docs_url or h.startswith("https://github.com/gpatwa/aveto-support/") for h in drawer_hrefs)
# nothing new is held
assert [f.name for f in dataclasses.fields(AskResult)] == ["outcome", "docs_repo", "docs_commit", "files", "signal", "length"]
# not rendered where the service held nothing about an answer
for p in (judge_error_page, rate_limited_post_page, paused_post_page, kill_switch_get_page,
          too_long_post_page, empty_post_page):
    assert 'class="receipts"' not in p
```
Fails on 32e54a6: no drawer.

### 10.2 The other fail-first tests

**T-A `test_page_cards.py::test_answer_card_holds_only_text_from_a_listed_passage`** (C1.4.2). Judge reply `f"Q1 ANSWERABLE {MODEL_CANARY}"`; `page = followed(client, QUESTION)`; `listed` as in T-D.
```python
assert pre_runs == [m.passage.text for _, m in listed]          # every quoted block is a listed passage, verbatim, in order
assert MODEL_CANARY not in page
for s in ("Deciding signal", "ANSWERABLE", "answerability-judge-v1", judge.PROMPT_SHA256):
    assert s not in page
found = "Found 1 passage." if n == 1 else f"Found {n} passages."
required = {"The docs answer this", found, D1, "Outcome", "Docs version", f"Commit {c7} on GitHub", "Passages listed"}
allowed = required | {CAPTION, COPY, str(n), D7, D8}
for path, m in listed:
    per = {path, f"Section: {heading(m)}. {Span(m)}", f"View {span(m)} of {path} on GitHub",
           f"to {path}, {span(m)}", f"{path}, {span(m)}"}
    required |= per; allowed |= per
assert required <= set(non_pre_runs) <= allowed
assert non_pre_runs.count(CAPTION) == n and non_pre_runs.count(COPY) == n
```
Read plainly: every sentence inside a quoted block is a listed passage's text, byte for byte; every other run on the card is fixed copy or a field (path, heading, line numbers, commit) of a listed passage. Fails on 32e54a6: caption, Copy link and drawer missing.

**T-ARIA `test_page_cards.py::test_every_aria_reference_resolves`** (the `aria-prohibited-attr` fix, UX 6.1).
```python
docs = {"get": client.get("/").text, "answer": followed(client, QUESTION),
        "refusal": followed(refusing_client, QUESTION), "resting": resting_client.get("/").text,
        "scorecard": client.get("/scorecard").text}
for name, d in docs.items():
    ids = set(re.findall(r'\sid="([^"]+)"', d))
    for attr in ("aria-labelledby", "aria-describedby"):
        for value in re.findall(rf'\s{attr}="([^"]+)"', d):
            assert set(value.split()) <= ids, (name, attr, value)
assert '<section id="result" tabindex="-1">' in docs["get"]
assert 'aria-labelledby="result-title"' not in docs["get"]
assert '<section id="result" tabindex="-1" aria-labelledby="result-title">' in docs["answer"]
assert 'id="result-title"' in docs["answer"]
```
Fails on 32e54a6: `GET /` names `result-title`, which does not exist. Stage 5 also changes `test_service_pages.py` line 67 to the corrected markup (a deliberate edit, not a weakening; UX 6.1).

**T-JS `test_page_cards.py::test_page_script_builds_no_result_card`** (one renderer, O2).
```python
js = client.get("/static/enhance.js").text
for s in ("The docs answer this", "The docs don't answer this", "Paused for today", "The service is off",
          "Question limit reached", "We couldn't decide this time", "Your question is too long",
          "Please enter a question", "Found ", "Section: ", "No confident match"):
    assert s not in js
assert "DOMParser" in js and "application/x-www-form-urlencoded" in js
assert '"/warm"' in js and '"/count/docs-click"' in js
assert "JSON.stringify" not in js and "application/json" not in js     # the page never posts JSON to /ask
```
Fails on 32e54a6: the script holds the `STATES` table.

**Stage 4's own fail-first tests** (fail on 32e54a6 because the routes or modules do not exist):
- **T-W `test_service_new_routes.py::test_warm_never_reaches_the_judge_or_spends`:**
  ```python
  embedder = CountingEmbedder(); fake = FakeJudgeClient()
  c = client with html=HtmlPages(make_runtime(embedder=embedder))
  h0 = c.get("/health").json(); capfd.readouterr()
  r = c.post("/warm"); assert (r.status_code, r.content) == (200, b'{"ready":true}')
  assert embedder.queries == 1 and fake.calls == []
  for _ in range(20): assert c.post("/warm").content == b'{"ready":true}'
  assert embedder.queries == 1 and c.get("/health").json() == h0
  assert capfd.readouterr().out == ""
  for _ in range(10): assert c.post("/ask", json={"question": QUESTION}).json()["outcome"] == "answer"
  assert len(fake.calls) == 10                                   # warm used none of the hour's ten
  src = inspect.getsource(AskService.warm)
  for name in ("_judge", "_spend", "_rate", "_retrievals", "emit_abuse", "emit_ops"): assert name not in src
  # kill switch on, cross-site Origin, resting: {"ready":false} and embedder.queries stays 0 (fresh apps)
  ```
- **T-S0 `test_service_new_routes.py::test_get_root_at_the_cap_passes_paused_without_spending`:** with a local `RecordingHtml` (as in `test_service_api.py`), `service._spend.cap = service._floor - 1`, `GET /` gives `html.pages[-1] is Outcome.PAUSED`; with the kill switch on as well, `Outcome.SERVICE_OFF` (precedence); `vars(service._spend)` is equal before and after; `/health` equal before and after; `fake.calls == []`; `embedder.queries == 0`. And `service.resting()` is `False` on a fresh service with the default cap.
- **T-RT `test_service_new_routes.py::test_route_inventory`:**
  ```python
  routes = sorted((r.path, sorted(r.methods)) for r in app.routes if isinstance(r, APIRoute))
  assert routes == [("/", ["GET"]), ("/ask", ["POST"]), ("/count/docs-click", ["POST"]), ("/health", ["GET"]),
                    ("/result/{token}", ["GET"]), ("/scorecard", ["GET"]), ("/static/{name}", ["GET"]), ("/warm", ["POST"])]
  assert plain_routes == [("/ask", ["POST"]), ("/health", ["GET"])]       # no renderer
  ```
- **T-J `test_service_new_routes.py::test_no_route_but_ask_reaches_the_judge`:** one app with a renderer; call `GET /`, `GET /result/x`, `GET /static/style.css`, `GET /scorecard`, `POST /warm` twice, `POST /count/docs-click`, `GET /health`; then `fake.calls == []`. (This also gives INV-4's "no other route of the service reaches the judge" a test for every route that exists; the invariant's text, which says no test shows it, is not edited, C1.3.)
- **T-L `test_service_new_routes.py::test_new_routes_write_no_log_line`:** after `configure_logging()`, the four new or changed non-ask routes write nothing to stdout (`capfd`), with the `logging_state` fixture.
- **T-K `test_service_counts.py::test_docs_click_rules`:** counted once for an empty same-origin post; not counted for `Origin: https://evil.example`, for `Sec-Fetch-Site: cross-site`, for a one-byte body, or with the kill switch on; the 61st within an hour is not counted, and after `FakeClock.advance(3601)` one more is; every response is `(204, b"")`.
- **T-H2 `test_service_ask_bytes.py::test_new_routes_carry_existing_header_sets`:** section 8's header-name sets for `/scorecard`, `/warm`, `/count/docs-click`.
- **T-F1 `test_service_scorecard.py::test_figures_reader_rules`** (parametrized; each invalid file raises `FiguresError`): unknown label; a valid label in the wrong section; missing `record`; `basis` not starting `Measured `/`Recorded `; `record` with `..` or a leading `/`; a link not on `https://github.com/`; `findings` on a non-Codex row; an unknown key; `schema = 2`.
- **T-F2 `test_service_scorecard.py::test_committed_figures_file_is_valid_and_every_record_exists`:** `load_figures()` on the committed file succeeds; every figure's and decision's `record` is a file under the repository root.
- **T-F3 `test_service_scorecard.py::test_scorecard_shows_only_rows_with_a_record`:** with a temporary file holding one `checks`/`Tests` row: "Checks", "Tests", its value and basis are on the page; "Speed", "Cold start", "Reviews", "Independent Codex review", "Who decided what", "How this was built", "n/a", "coming soon" and the characters "—" and "–" are not. With a file holding only `schema = 1`: S5 "No figures have been recorded yet." is shown and no figure section heading. The counts section is rendered in both cases (the counts are the service's own measurement, not a recorded figure; this narrows UX 1.7's "only S5" to the recorded figures, flagged for stage 5 and Security).
- **T-F4 `test_service_scorecard.py::test_unreadable_figures_show_s6_with_503`:** an invalid file gives status 503, S6 "The scorecard can't be shown right now. Please try again later.", the back link, `SECURITY_HEADERS`, and no figure row.
- **T-F5 `test_service_scorecard.py::test_scorecard_markup`:** no `<script`; exactly one `<link`, which is `<link rel="stylesheet" href="/static/style.css">`; every `href`/`src`/`action` starts with `/` or `https://github.com/`; the first `href` in `<main>` is `/`; N1 present; N2 equals `The service started 2026-10-21 07:00 UTC.` under `FakeClock()`; no `style=`, `<style`, ` onclick=`.

### 10.3 Guards (pass on 32e54a6 and on the final tree; they prove nothing moved)

- **T-B** `test_service_ask_bytes.py::test_ask_json_bytes_equal_main` (section 8).
- **T-H1** `test_service_ask_bytes.py::test_security_and_json_header_sets_are_byte_identical` (section 8, existing routes and the two literal dicts).
- **T-COPY** `test_page_cards.py::test_disclosure_block_byte_identical`: the raw `GET /` HTML contains, as one substring, lines 203 to 212 of `git show 32e54a6:aveto_service/render.py` (the intro paragraph through `</ul>`, joined with `\n`), copied into the test as a literal; also on the resting page.
- Existing tests that must stay green unmodified: `test_core_files_unchanged`, `test_ask_json_contract`, `test_not_answerable_is_exactly_no_confident_match`, `test_health_never_calls_model`, `test_abuse_line_shape_exact`, `test_disclosure_copy_is_verbatim`, `test_paused_state`, `test_service_off_state_on_get_and_post`, `test_prg_reload_does_not_re_ask`, `test_main_module_composes_the_app`, `test_page_routes_exist_only_with_a_renderer`, `test_dockerfile_static` and the rest of `test_infra_static.py`.

### 10.4 Stage 5's own tests

- **T-Q `tests/test_service_suggestions.py::test_suggestions_are_copied_from_spent_sets`:** `aveto_service/suggestions.toml` has exactly slots A1, A2, A3, R1 in that order; each `text` equals the eval file's `question` for its `set` and `id` (read with `tomllib`); A slots have `expect = "answer"`, R1 `expect = "no_confident_match"`; each text at most 90 characters with no `<`, `>` or newline; and the four equal the literals `SA1`, `SA2`, `SA3`, `SR1` in `test_page_cards.py`.
- Updates in `tests/test_service_pages.py`: line 67 as T-ARIA says; any copy assertion the new markup breaks is changed to the new exact string, never removed (C1.4.7 "not weakened"); the count of tests may only grow.

Eval cases: none scored (no retrieval, prompt or judge change). The eval files are read by T-B and T-Q for question text only.

## 11. How each C1.4 bar is measured, by whom, with which command

Base commit for every diff: **32e54a6** (= `main` at setup). Where the Charter's literal command says `main`, QA runs it as written and also with `32e54a6`, and states that `git rev-parse main` still equals 32e54a6 (if `main` has moved, the 32e54a6 form is the evidence and the move is reported). All commands run from the worktree root.

| Bar | Who, stage | Command or method | Pass |
|---|---|---|---|
| **1** Answering byte-identical | QA, 7 | `git diff main --stat -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md`; the same with `32e54a6`; `git status --porcelain -- aveto_support prompts .claude .agentic`; `uv run pytest tests/test_service_ask_bytes.py -v`; golden provenance: `git log --diff-filter=A --format=%H -- tests/golden/ask-json-32e54a6.json` then `git diff --exit-code 32e54a6 <that hash> -- aveto_service aveto_support prompts` | both diffs print nothing; status shows nothing or only ` M .agentic/CURRENT_MVP_STATUS.md`; 36 cases plus `/health` byte-equal, ids complete; provenance diff empty |
| **2** Answer card holds only listed text; refusal card no model text | Stage 4 writes (commit 1, fails), stage 5 makes pass; QA re-runs, 7 | `uv run pytest tests/test_page_cards.py -k "answer_card or refusal_card" -v` | T-A and T-R pass on the final tree; both appear failing in `04-failfirst-32e54a6.txt` |
| **3** Accessibility | Orchestrator, 8 (built-in browser) | Local dev server (section 14.3) on `http://127.0.0.1:8765`, and a second instance with `--resting` on port 8767. axe-core, one pinned version, from `npm install --prefix <scratchpad>/axe axe-core@<version>` (C1.5), injected and run through `mcp__Claude_Browser__javascript_tool` exactly as in the C6.9 dry run, with `axe.run(document, {runOnly: {type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]}})`, on five views: `GET /`; an answer result (ask SA1); a refusal result (ask SR1); the resting `GET /` (port 8767); `GET /scorecard`. Save each result's `violations` (id, impact, node targets) to `runs/polished-chat-experience/08-browser/axe-<view>.json` | zero violations with impact `serious` or `critical` on each of the five views; axe version recorded in END_REVIEW |
| **4** 375 px and keyboard | Orchestrator, 8 | `mcp__Claude_Browser__resize_window` to 375 x 812; on each of the five views run in `javascript_tool`: `({scroll: document.documentElement.scrollWidth - document.documentElement.clientWidth, small: [...document.querySelectorAll("a[href], button, summary, textarea, input:not([type=hidden]), select")].filter(e => e.getClientRects().length && !e.disabled && !e.hidden).map(e => [e.tagName, e.textContent.trim().slice(0, 40), Math.round(e.getBoundingClientRect().width), Math.round(e.getBoundingClientRect().height)]).filter(([, , w, h]) => w < 24 \|\| h < 24)})`. Keyboard only (`computer` tool key presses, no pointer), at desktop width and at 375 px: Tab from the top to a suggestion, Enter (loads it), Tab to Ask, Enter, wait for the result, focus is on `#result`, Tab to the receipts `summary`, Enter (opens), Enter (closes), Shift+Tab back to the first source chip, Enter (follows the link; the tab URL changes to the passage permalink); a screenshot of the focus ring at each stop | `scroll` is 0 and `small` is empty on all five views; each keyboard step reached with a visible focus indicator and focus never stuck |
| **5** Timings, as measured, no pass figure | Local: Orchestrator, 8. Live: Orchestrator and Production Verification, 13 | Local: `uv run python runs/polished-chat-experience/08-local/time_local.py --url http://127.0.0.1:8766` against a **fresh** dev server instance on port 8766 used for nothing else (the hourly limit of 10 is per visitor): one `POST /warm` (its duration recorded as "first retrieval absorbed by the warm-up"), a second `POST /warm` (recorded), then 10 consecutive `POST /ask` JSON with the first ten questions of section 8's set, each timed with `time.perf_counter()` from send to full body; writes `08-local/timing.json` (date, method, n, each time, median, slowest). Live: section 12.4 and 12.6 | figures reported with date and method; a figure with no measurement is not shown |
| **6** No open P0 or P1 | Release Manager, 11 | Reads `code-review.md` (stage 6), the QA evidence (7) and the Security review (9) | none open; P2 and below listed in END_REVIEW |
| **7** Tests | QA, 7; Release Manager re-runs, 11 | `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`; and `04-failfirst-32e54a6.txt` (section 14.1) | 0 failed; passed at least 668 plus the new test items; T-R, T-S, T-C, T-D each listed as failing in the fail-first file and passing now; mypy and ruff clean |
| **8** Nothing about answering moves | QA, 7 | Bar 1's diffs; `uv run pytest tests/test_service_pipeline.py::test_core_files_unchanged tests/test_service_pages.py tests/test_service_limits.py tests/test_service_logging.py tests/test_service_api.py -v`; `git diff --exit-code 32e54a6 -- aveto_service/pipeline.py` shows only the added `WARM_QUESTION`, `_warm_lock`, `_warm_result`, `resting()` and `warm()` (QA reads the hunk); T-COPY | all pass; the pipeline hunk adds and changes nothing else; INV text untouched |

**Stricter figures: none proposed.** Bars 3, 4 and 7 are already the strict form of their check; bar 5 deliberately has no pass figure, and a figure for it now would rest on one cold-start record (30.8 s) and a model latency the slice does not control. A proposal would also need a new Charter hash (stop 5) for no gain in what is checked.

## 12. Deploy sheet (stages 12 and 13; Orchestrator's session; Charter C8.1, C8.3, C3.1)

Every command is literal so it matches a C6.P allow rule. **One placeholder, `<TAG12>`**: the Orchestrator replaces it with the literal output of `git log -1 --format=%h --abbrev=12` on the gated HEAD before running anything (never `$(...)`, never a shell variable). `W` below is written out in full in every command: `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6`. The build context is the worktree root, never the main checkout. Save every output under `runs/polished-chat-experience/12-deploy/` and `13-live/`, search it for `sk-ant` and key-shaped strings before committing, and mask the subscription id. Never run a command that prints a secret value. Prices, `monthlyCapUsd` and `clientKey` come from the Bicep defaults, which equal the live values (C6.6: 2000/10000, cap 10, `xff_last`); `killSwitch` is always passed; `configureLogRetention=true` is passed as in the previous runs so the tables' retention stays declared.

**Deployments allowed (C8.3): at most three `create` commands for the release, (1) new tag, (2) rehearsal to `d067b9a95ac6`, (3) roll forward to `<TAG12>`, plus `killSwitch=on` only if C8.1 requires it.** `what-if` is read-only and is run before each `create`.

### 12.0 Pre-flight (read-only), stage 12

```
git status --porcelain
git log -1 --format=%h --abbrev=12
git rev-list --left-right --count main...origin/main
az account show --query "{name:name,state:state}" -o tsv
az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].{name:name,traffic:properties.trafficWeight,health:properties.healthState}" -o tsv
az containerapp show -g rg-aveto-ask -n ca-aveto-ask --query "properties.template.containers[0].{image:image,env:env[].{n:name,v:value,s:secretRef}}" -o json
az acr repository show-tags -n acravetoaskgp --repository aveto-ask -o tsv
az bicep build --file /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.bicep --stdout
```
Pass: no uncommitted change; `<TAG12>` read; `Visual Studio Enterprise Subscription  Enabled` (an expired sign-in is stop 3); exactly `ca-aveto-ask--0000008  100  Healthy` (anything else: stop, the rollback target is not C6.6's); image `acravetoaskgp.azurecr.io/aveto-ask:d067b9a95ac6`, env `ASK_KILL_SWITCH off`, `ASK_CLIENT_KEY xff_last`, `ASK_PRICE_IN_NANO_PER_TOKEN 2000`, `ASK_PRICE_OUT_NANO_PER_TOKEN 10000`, `ASK_MONTHLY_CAP_USD 10`, `ANTHROPIC_API_KEY` as `secretRef anthropic-api-key` with no value (saved as the before-state); the tag list contains `d067b9a95ac6` (the rehearsal needs it) and not `<TAG12>` (tags are never overwritten); the Bicep compiles.

**Public-repository check (decides whether links ship; must happen before the figures fill, so in practice the Orchestrator runs it at stage 10):** `mcp__Claude_Browser__navigate` to `https://github.com/gpatwa/aveto-support/blob/main/README.md`. Confirmed public only if the page renders the README **and** the GitHub header shows a "Sign in" control (the browser is not signed in). Anything else (404, a sign-in wall, or a signed-in browser) is "not confirmed": the fill leaves out `[links]` and `source_base` (section 3.7), and END_REVIEW says so. The `git rev-list` line above shows whether local `main` equals `origin/main` (the earlier records the Source links point at exist on `main`); if it is not `0 0`, Source links are left out too.

### 12.1 Build one image (C8.3)
```
az acr build -r acravetoaskgp -t aveto-ask:<TAG12> --platform linux/amd64 -f Dockerfile /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6
```
(The same form fix-service-accounting ran in its section 7.1.) Pass: build and push succeed; the log's ingest line `wrote index/docs-index.json  sha256 <hex>` equals `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756` (nothing in `aveto_support/`, `docs-source.toml` or the Dockerfile changed). A different hash is reported, and stage 13's byte comparison is then reported as "not established" rather than passed. The log shows `aveto_service/scorecard.toml` and `aveto_service/suggestions.toml` were sent (they are under `aveto_service/`, which the Dockerfile copies whole).

### 12.2 Deployment (1): the new image, kill switch off
```
az deployment group what-if -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.parameters.json -p deployApp=true imageTag=<TAG12> killSwitch=off configureLogRetention=true
```
What-if pass rule, fixed now: no `Create`, no `Delete` at resource level; no type outside C8.3; on `ca-aveto-ask` the only real change is the image `d067b9a95ac6` to `<TAG12>`. The lines `runs/fix-service-accounting/09-deploy/7.2-whatif-ruling.md` ruled as representation noise (server-populated `ingress.exposedPort`, `ingress.traffic`, `runningStatus`; `registries.0.server` as an unresolved reference; the probe order; table `plan`/`schema` "Delete" properties; `Modify` on environment, registry, role assignments) are listed in the record, not a stop. Any other app property change, any env change, or a retention change is a failed check: no deploy (C8.1). Then:
```
date -u +%Y-%m-%dT%H:%M:%SZ
az deployment group create -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.parameters.json -p deployApp=true imageTag=<TAG12> killSwitch=off configureLogRetention=true
az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].{name:name,traffic:properties.trafficWeight,health:properties.healthState}" -o tsv
az containerapp show -g rg-aveto-ask -n ca-aveto-ask --query "properties.template.containers[0].{image:image,env:env[].{n:name,v:value,s:secretRef}}" -o json
```
Pass: one new revision (expected `ca-aveto-ask--0000009`; the number is a prediction) at 100 and Healthy; image `acravetoaskgp.azurecr.io/aveto-ask:<TAG12>`; env exactly the before-state. A revision that does not become Healthy within 10 minutes: whether single-revision mode keeps `ca-aveto-ask--0000008` serving meanwhile is unconfirmed (from memory of the platform, not checked); the run checks with `live.py check old`, and either way runs deployment (2) as the restore (C8.1), checks `check old`, reports and stops.

### 12.3 The live script (written by stage 4, reviewed at stage 6, run here)

`runs/polished-chat-experience/13-live/live.py`, run as `uv run python runs/polished-chat-experience/13-live/live.py <mode> ...` from the worktree root (not `curl`, C6.P). Standard library HTTP only, plus local `aveto_support`/`aveto_service` for the comparison; no `az` call; no host but `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`. It never retries a `POST /ask`. It writes ids, codes, counts and times only, never question or passage text. Adapted from `runs/fix-service-accounting/10-smoke/smoke.py` (its `watch` and `ask` modes).
- `check new`: `GET /health` 200 with `"kill_switch":"off"`; `GET /` 200, contains `Skip to the question box` and the four suggestion texts; `GET /scorecard` 200; `GET /static/enhance.js` 200; the four `SECURITY_HEADERS` on `/` and `/scorecard` equal section 8's literal exactly; `POST /warm` answers `{"ready":true}`. No question is sent.
- `check old`: `GET /health` 200 `"kill_switch":"off"`; `GET /` 200 and does **not** contain `Skip to the question box`; `GET /scorecard` 404. No question is sent.
- `watch old` / `watch new` (timeout 600 s, poll every 2 s): records its start time; polls `GET /health` and `GET /scorecard`; "old serving" is `/health` 200 and `/scorecard` 404, "new serving" is both 200; records the first time the wanted state is seen on three consecutive polls (traffic moves over a few seconds). Writes `13-live/watch-<mode>-<n>.json`. Exit 1 on timeout.
- `ask --index <path> --models <path>`: section 12.4.
- `cold`: section 12.6.

### 12.4 Live behaviour checks on the new revision, before the rehearsal (C3.1: 7 questions, under the cap of 8)

Run straight after `check new` passes, in one replica lifetime. Index and models: the worktree's `index/` and `models/` if present, else the main checkout's `/Users/gopalpatwa/opt/aveto-support/index/docs-index.json` and `/Users/gopalpatwa/opt/aveto-support/models`, read only; the index sha256 must equal 12.1's ingest hash, else byte equality is "not established".

| # | Path | Set, id | Expected outcome |
|---|---|---|---|
| 1 | JSON | heldout-5 `g01` (A1) | `answer` |
| 2 | JSON | heldout-5 `g03` (A2) | `answer` |
| 3 | JSON | heldout-5 `g04` (A3) | `answer` |
| 4 | JSON | heldout-5 `gu18` (R1) | `no_confident_match` |
| 5 | JSON | public-gate-1 `p05` | `answer` |
| 6 | JSON | heldout-5 `gu15` | `no_confident_match` |
| 7 | form, then `GET` of the 303 target | heldout-5 `g01` | the result page holds exactly the local `retrieve` passages |

`ask` mode: (1) loads the seven questions by id from the eval files; (2) computes local `retrieve(searcher, judge.normalise_question(q))` for each **before sending anything**; (3) `GET /health` and `GET /scorecard` (reads the counts before); (4) sends the seven in order, once each, recording HTTP status, outcome and seconds from send to full body (`time.perf_counter()`); for each JSON `answer`, compares every file and passage field (`rank`, `path`, `url`, `heading`, `line_start`, `line_end`, `url`, `text` as UTF-8 bytes) with the local result; for request 7, follows the 303 and compares the text of every `pre.passage > code` with the local passages, byte for byte, in order; (5) `GET /health` and `GET /scorecard` after; (6) writes `13-live/ask-result.json` (start and end UTC, index sha256, per id: status, outcome, expected, seconds, `byte_equal`; the `/health` and counts deltas).

Verdict rules (fixed now):
- **Behaviour failure, C8.1, restore and stop:** any of the seven not answered with HTTP 200 (or 303 then 200 for #7) and `answer` or `no_confident_match`; any `answer` whose passages are not byte-equal to the local `retrieve` (when the hashes match); question words in a log table (12.5). Then deployment (2) is the restore: run 12.7's command, check `check old`, report, **do not roll forward**, stop.
- **Reported as measured, not a rollback:** an A question or `p05` refused (over-abstention); R1 or `gu15` answered with passages (section 9); an index hash mismatch.
- **Warm timing (C1.4.5):** report median and slowest of requests 2 to 7 (six warm live requests; request 1 also reported on its own). The counts delta on `/scorecard` is expected to be +7 asked unless a visitor asked meanwhile or the replica restarted; reported, not a gate.
- **Spend:** seven questions at about $0.0085 (2026-10-24 record) is about $0.06 of the day's $0.3226 share, through the real limits (C8.5).

### 12.5 No question text in a log table

At least 5 minutes after request 7, first confirm the run's own abuse rows have arrived (else a zero proves nothing; re-query up to three times over 30 minutes). Workspace id `4c594f2b-4b78-4d27-9f9e-3dbe5b4c3047` (recorded in `runs/fix-service-accounting/09-deploy/7.2-whatif-ruling.md`); `<D1_START_UTC>` is the `date -u` output recorded before deployment (1), written as a literal.
```
az monitor log-analytics query -w 4c594f2b-4b78-4d27-9f9e-3dbe5b4c3047 --analytics-query 'ContainerAppConsoleLogs_CL | where TimeGenerated > datetime(<D1_START_UTC>) | where Log_s has "ip" | project TimeGenerated, Log_s' -o tsv
az monitor log-analytics query -w 4c594f2b-4b78-4d27-9f9e-3dbe5b4c3047 --analytics-query 'search "looks good" or "long-lived feature branch" or "website goes wrong" or "right-to-left" or "force-push" or "Who founded Aveto" | where TimeGenerated > datetime(<D1_START_UTC>) | summarize hits=count() by $table' -o tsv
```
Pass: the first lists only abuse lines of the shape `{"t":...,"ip":"<16 hex>","o":...}` (seven for this run, plus any visitors'), nothing shaped like request data; the second returns no rows. (These are the same query forms fix-service-accounting ran and recorded in `10-smoke/log-search.txt`.)

### 12.6 Cold start (after the roll forward, the last measurement)

Wait for the replica to scale to zero with no request sent: every 60 s, `az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].properties.replicas" -o tsv` until it prints `0` (field name from memory, unconfirmed), for at most 30 minutes. If the field does not exist, wait 20 minutes with no request and record "replica count not read". Then `uv run python runs/polished-chat-experience/13-live/live.py cold`: one `GET /health` with a 180 s timeout, timed from send to the 200 (the method of the 30.8 s record), then one `GET /` timed. Writes `13-live/cold.json` with the UTC date and method. If the replica never reaches 0 in 30 minutes (visitors), cold start is "not measured" and is not retried.

### 12.7 Rollback rehearsal: deployment (2), the previous image (release gate, intent; C8.1, C8.3)

Start `live.py watch old` in the background, then:
```
az deployment group what-if -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.parameters.json -p deployApp=true imageTag=d067b9a95ac6 killSwitch=off configureLogRetention=true
date -u +%Y-%m-%dT%H:%M:%SZ
az deployment group create -g rg-aveto-ask -f /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.bicep -p @/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/infra/main.parameters.json -p deployApp=true imageTag=d067b9a95ac6 killSwitch=off configureLogRetention=true
az containerapp revision list -g rg-aveto-ask -n ca-aveto-ask --query "[?properties.active].{name:name,traffic:properties.trafficWeight,health:properties.healthState}" -o tsv
uv run python runs/polished-chat-experience/13-live/live.py check old
```
What-if pass: the only app change is the image `<TAG12>` to `d067b9a95ac6`. This deploys a **new revision of the previous image** (the runbook's section 2 rollback; C8.3's words), not a reactivation of `--0000008`.
**Rollback time (the Charter's definition):** from the `date -u` printed immediately before `create` to the watcher's first of three consecutive "old serving" polls, in seconds. Pass: old serving within 600 s; one new revision at 100 and Healthy with image `d067b9a95ac6` and the before-state env; `check old` passes. **Fail** (the previous page does not serve, `/health` does not answer, or 600 s pass): C8.1, keep or restore the previous revision serving; if `/health` does not answer at all, the kill switch on with this same command and `killSwitch=on` (the one extra deployment C8.3 allows), report, stop; the release fails.

### 12.8 Roll forward: deployment (3), the new image again

Start `live.py watch new` in the background, then the what-if and create of 12.2 exactly (`imageTag=<TAG12> killSwitch=off configureLogRetention=true`), with `date -u` immediately before `create`, then the revision list, `az containerapp show` and `live.py check new`. Roll-forward time is measured the same way ("new serving", three consecutive polls). Pass: new serving within 600 s; one new revision at 100 and Healthy with image `<TAG12>` and the before-state env; `check new` passes. **Fail** (the roll forward does not restore the new revision): C8.1, the previous image keeps serving (deployment (2)'s revision); if it is not, the kill switch on; report; stop; the release fails. No question is sent after the roll forward (behaviour was checked in 12.4 on the same image); then 12.6.

Order at stage 13: 12.3 `check new` -> 12.4 questions -> 12.5 log query (wait at least 5 minutes; no question is sent after 12.4, so its window is complete) -> 12.7 rehearsal -> 12.8 roll forward -> 12.6 cold start. A failure in 12.4 or 12.5 is restored by deployment (2) and the run stops without rolling forward, so no fourth deployment is ever needed; a failure after 12.8 can only be met with the previous revision still serving (12.8's fail rule) or the kill switch.

Not checked live, stated plainly: the kill switch. A live kill-switch toggle needs a deployment C8.3 allows only when C8.1 requires it; the kill-switch code is unchanged and its offline tests stay green (`test_service_off_state_on_get_and_post`, T-W, T-K).

## 13. Rollback plan (executable from this spec alone)

1. **The service, fastest:** the kill switch on. Run 12.2's `create` with `killSwitch=on` (and the current `imageTag`). Visitors see "The service is off"; no retrieval or model call happens. About 65 s recorded.
2. **The service, previous version:** 12.7's `create` with `imageTag=d067b9a95ac6 killSwitch=off configureLogRetention=true` (rehearsed in this slice; timed in `13-live/`). The previous image is in the registry (tags are never overwritten). Nothing else to undo: no resource, setting or secret changed.
3. **The code:** the run never merges (C8.2). If the owner has merged, revert the merge commit on `main`; no data migration exists (all new state is in memory and restarts with each revision; the two `.toml` files are part of the code).
4. **The links in the scorecard and drawer** point at the branch; if the branch must go, a later change repoints them to `main` (or removes `[links]`); until then they 404, which shows a broken link, not wrong content.

## 14. Work split, the stage 4 checkpoint, and the dev server

### 14.0 Who owns which file (no file is edited by both stages)

| Stage, role | Owns (creates or edits) | Reads only |
|---|---|---|
| **4 Backend Architect** | `aveto_service/app.py`, `aveto_service/pipeline.py`, `aveto_service/counts.py` (new), `aveto_service/scorecard.py` (new), `aveto_service/scorecard.toml` (new); `tests/test_service_new_routes.py`, `tests/test_service_counts.py`, `tests/test_service_scorecard.py`, `tests/test_service_ask_bytes.py`, `tests/golden/ask-json-32e54a6.json` (all new); **`tests/test_page_cards.py` (new, written in commit 1 and then frozen, see below)**; runs files: `runs/polished-chat-experience/04-retrieval-check.py`, `08-local/devserver.py`, `08-local/time_local.py`, `13-live/live.py`, `04-implementation.md`, `04-failfirst-32e54a6.txt`, `04-checkpoint.txt` | this spec, `03-ux-spec.md` sections 1, 8, 9; `pages.py`, `render.py`, `html_port.py`, `limits.py`, `abuse_log.py`, `tests/service_fakes.py`, `tests/test_service_api.py`, the two eval files |
| **5 Frontend Developer** | `aveto_service/render.py`, `aveto_service/pages.py`, `aveto_service/static/enhance.js`, `aveto_service/static/style.css`, `aveto_service/suggestions.toml` (new); `tests/test_service_pages.py`, `tests/test_service_suggestions.py` (new); `runs/polished-chat-experience/05-frontend.md` | this spec, `03-ux-spec.md` (whole), `tests/test_page_cards.py` (its contract), `aveto_service/scorecard.py` (`build_links`, the markup class names) |
| **10b Backend Architect (re-spawn, about 15k)** | `aveto_service/scorecard.toml` only (the figures fill, section 3.7) | `runs/polished-chat-experience/10-figures.md` |

Stage 4: 5 product files and 6 test files (plus run scripts). Stage 5: 5 product files and 2 test files. Both are near the EM's "about 10 files" guideline (D4).

**Expected change set** (QA, stage 7: `git diff --name-only 32e54a6 -- . ':(exclude)runs'` must be a subset of exactly these, any other path is a finding): the stage 4 and 5 files above; `docs/ARCHITECTURE.md`, `docs/adr/0010-server-rendered-results-one-renderer.md`, `docs/adr/0011-content-free-counts-and-recorded-figures-scorecard.md`, `docs/adr/0012-service-not-framed-aveto-dev-links-to-it.md` (this stage); `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md` (stage 10). Not in it: `aveto_support/`, `prompts/`, `.claude/`, `aveto_service/{html_port,limits,abuse_log,judge_port,anthropic_judge,settings,result_store,main}.py`, `infra/`, `Dockerfile`, `.dockerignore`, `pyproject.toml`, `uv.lock`, `tests/service_fakes.py`, `tests/test_service_api.py`.

**`tests/test_page_cards.py` is the stage 5 contract.** Stage 4 writes it in its first commit from section 10's exact assertions, so that it fails against the untouched 32e54a6 product code (C1.4.7 says the four intent tests fail on 32e54a6 first, which only a run before any product edit can show). After commit 1, stage 4 does not edit it. Stage 5 does not edit it either: if stage 5 finds an assertion that contradicts `03-ux-spec.md` or this spec, it stops and reports to the Orchestrator, who routes the fix back to stage 4 (a FAILURE_LOOP retry, recorded).

**Seams:** `pages.py` calls `aveto_service.scorecard.build_links()` (stage 4's function) for the two drawer links; the scorecard page's markup uses the class names stage 5 styles (`dl.figures`, `dd.value`, `dd.basis`, `ul.findings`, `state state-note` for S6), as named in UX 1.7; `HtmlRenderer.page(Outcome.PAUSED)` from `GET /` means resting at load (section 3.5). `render.page_html` may gain keyword parameters (suggestions, links, commit, `at_load`); `pages.py` is the only caller, and both are stage 5's.

### 14.1 Stage 4 sequence

1. **Commit 1, tests first** (no product file touched). Write every stage 4 test file and `tests/test_page_cards.py`; run `uv run python tests/test_service_ask_bytes.py --write-golden`. Record into `04-failfirst-32e54a6.txt`: `git rev-parse HEAD`; `git diff --stat 32e54a6 -- aveto_service aveto_support prompts` (must be empty); then `uv run pytest --continue-on-collection-errors tests/test_page_cards.py tests/test_service_counts.py tests/test_service_new_routes.py tests/test_service_scorecard.py tests/test_service_ask_bytes.py -v` (collection errors are expected for the modules that import the not-yet-existing `aveto_service.counts` and `aveto_service.scorecard`; `--continue-on-collection-errors` keeps them from stopping the run). Expected: T-B and T-H1 and T-COPY pass; T-R, T-S, T-C, T-D, T-A, T-ARIA, T-JS, T-W, T-S0, T-RT, T-J, T-K, T-H2 fail or error; anything else is reported. Commit with a message naming it tests-first.
2. **Offline retrieval check of the suggestions** (section 9's missing evidence): `uv run python runs/polished-chat-experience/04-retrieval-check.py`, which loads the index and models (the worktree's if present, else the main checkout's, read only, recording the index sha256), runs `retrieve` at the default ranking for A1 to A3, R1 and the four reserves, and writes `04-retrieval-check.json` (id, top-5 file paths, whether a labelled `sources` file is among them). Pass rule for A1 to A3: a labelled source in the top 5 (as recorded at stage 7 of docs-answerability-2). A miss is reported to the Orchestrator before stage 5, with the reserve that passes. For R1, the top files are recorded only (nothing offline can show a refusal).
3. Implement sections 3.4, 3.5, 3.7, 3.8, the `counts.record` call, and the three routes; write `scorecard.toml` with the rows and decisions known now (section 3.7) and, if not yet confirmed public, no `[links]` and no `source_base`; write the three run scripts.
4. **Checkpoint (commit 2):** `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, saved as `04-checkpoint.txt`. Pass: mypy and ruff clean; **every test passes except exactly the tests in `tests/test_page_cards.py` other than T-COPY**, each failing on an assertion (no collection error, no import error). Committed before stage 5 starts (D4).

### 14.2 Stage 5 sequence

Implement the page against UX and `tests/test_page_cards.py`; write `suggestions.toml` (section 9) and T-Q; update `test_service_pages.py` (line 67 and any copy assertion, never weakened). Done when the full regression is green (0 failed), mypy and ruff clean; one focused commit. Watch for the EM's 170k signal on this stage (01-scope.md section 6).

### 14.3 The stage 8 dev server (O10)

`runs/polished-chat-experience/08-local/devserver.py --port <n> [--resting]` (stage 4 writes it; the Orchestrator runs it in the background at stage 8 with `uv run python ...`). It builds `Settings(kill_switch="off", api_key="", client_key="peer", monthly_cap_usd="0.000001" if --resting else "10", index_path=..., models_path=...)` (index and models as in 12.4), `runtime = load_runtime(settings)`, and a `DevJudge` (defined in the script, never shipped) that returns `JudgeCall("Q1 NOT_ANSWERABLE", 2400, 20)` when the payload's `Question:` line equals one of the unanswerable questions of `retrieval-heldout-5.toml` or `public-gate-1.toml`, else `JudgeCall("Q1 ANSWERABLE", 2400, 20)`; then `create_app(runtime, DevJudge(), settings, html=HtmlPages(runtime))` under `uvicorn.run(app, host="127.0.0.1", port=n, log_level="critical")`. Instances: 8765 (browser checks), 8766 (timing only), 8767 (`--resting`). Nothing in the product changes for this; `ASK_MONTHLY_CAP_USD` already does the same in production.

## 15. Charter check and flags for the Orchestrator

**STOP-FLAGs: none.** What I checked against Charter section 9 and C1 to C8:

| Possible stop | Finding |
|---|---|
| New runtime dependency | None. `tomllib` and `html.parser` are standard library; FastAPI, Starlette and uvicorn are already locked |
| Header change (C5.0) | None. New HTML route uses `SECURITY_HEADERS` (imported); new JSON routes use the existing `_JSON_HEADERS`; T-H1 and T-H2 pin both byte for byte |
| Safety text (C5.0, stop 1) | None needed. Checked INV-4's text: "no other route of the service reaches the judge" stays true (T-J); "as its page for a form post or the page's own script" covers the script now using the form path; "the page shows the same passages as the JSON and no deciding-signal line" stays true (T-A, T-D). INV-1 to INV-3 and INV-5 are untouched by every change here. One sentence of INV-4 ("Not shown by any test: that no route but `POST /ask` reaches the judge") becomes out of date when T-J lands; it is not edited (C1.3 forbids it) and is listed for a later slice |
| Privacy or Article 50 wording | Unchanged byte for byte (T-COPY, `test_disclosure_copy_is_verbatim`). The beacon reads no address, so "To apply the limits we read your address..." needs no change |
| New processor (C4.0) | None. GitHub appears only as hyperlinks a visitor may follow; the service makes no request to it |
| Extra infrastructure, setting or resource (C8.3) | None. No Bicep, environment variable, Dockerfile or `.dockerignore` change |
| New model (C3) | None |
| Irreversible action beyond C8.3 | None. Section 12 uses at most the three deployments plus the conditional kill switch |

**Two readings for the Orchestrator to rule on (not stops in my reading):**
1. **C1.6 and data strings.** C1.6 says the new visitor-facing strings are the UX copy deck. The UX spec (section 8) names the four suggestions, figure values and basis text, decision text and link targets as data the Architect supplies, not copy. The suggestions are fixed in section 9 and the initial figures and decisions in section 3.7, now, before the build; the figures filled before the build follow the basis templates in section 3.7. All of them obey C1.6's rule (no claim about privacy, data handling, the law or AI beyond the live page) and all go to the owner in END_REVIEW beside the copy deck. If you read C1.6 as "copy deck only", these strings are a Charter question (stop 5) and the scorecard would ship with counts only and no suggestions.
2. **The plan's note on service-own measurements** (section 3.7): I add counts and the start time, not in-service timing. If you read the note as requiring in-service timing, it is a stage 4 item, already specified in 3.7.

**One item for the owner in END_REVIEW (not a stop):** the page's existing intro says "Nothing on this page is written by an AI model." The four suggested questions were drafted by Claude in the support session (the eval files' provenance) and committed by the owner, as the page's copy was drafted by agents and approved. The sentence has always meant "no text shown in answer to a question is written by the model", and that stays true; the owner may want it read with that in mind.

## 16. Risks, open items, and what Security (stage 9) reads

| # | Risk | Handling |
|---|---|---|
| R1 | Branch-ref links 404 between deploy and push, and after branch deletion | Accepted (O6); END_REVIEW tells the owner; a later change repoints to `main` |
| R2 | Repository visibility unconfirmed | 12.0 check; no links ship unless confirmed |
| R3 | A suggested question gets a different verdict live | Section 9 rules; reserves named |
| R4 | `fetch` + `DOMParser` swap has a browser-specific gap (for example focus or live-region announcement after a swap) | Stage 8 keyboard and axe checks run on the JS path; the no-JS path is the same HTML |
| R5 | Public counts and the start time disclose usage and restart times | Same kind as `/health`'s public counters (owner's D3 still open); Security decides; fallback: do not render the counts section or N2 (render-only change) |
| R6 | Visits can be inflated by reloads; clicks by up to 60 an hour | Stated in the basis text and here; the counts are loads and clicks, not people |
| R7 | The warm-up may absorb nothing measurable | W0 is still true; stage 8 records both warm durations |
| R8 | The figures fill needs a re-spawn not in the stage table | Section 3.7; the Orchestrator rules |
| R9 | JS-path results now go through the PRG store | Same data and bounds as no-JS posts; listed for Security |
| R10 | Earlier-release timings on this release's scorecard | Each basis names the earlier revision and date; this run's live figures follow by a later change |

**Security (standard, C7.1) reads:** `app.py` (the three routes, the `GET /` change, the `counts.record` call); `pipeline.py` `resting` and `warm`; `counts.py`; `scorecard.py` (reader rules, escaping, headers, 503 path); `scorecard.toml`, `suggestions.toml`; `enhance.js` (DOMParser swap, beacon, warm-up, no `://`, no storage APIs); `render.py` drawer and suggestion forms (escaping of the `value` attribute); `pages.py`; T-RT, T-J, T-W, T-K, T-H1, T-H2. Questions for it: can any new route reach the judge, the spend counter or a log line; can the beacon or warm-up be used to burn CPU or memory beyond the stated bounds; does any new page response differ in headers; does the drawer or scorecard render any value not escaped; is publishing the counts and the start time acceptable next to D3.

## 17. Living architecture record

- `docs/ARCHITECTURE.md`: the "Public ask service" section is rewritten for the system after this slice (routes, one renderer, counts, scorecard, warm-up, what is stored; the stale "not yet deployed" and "nothing measured" lines replaced with pointers to the records). Marked as the specified design until stage 13 confirms the deploy.
- New decision records (one decision each): `docs/adr/0010-server-rendered-results-one-renderer.md` (proposed), `docs/adr/0011-content-free-counts-and-recorded-figures-scorecard.md` (proposed), `docs/adr/0012-service-not-framed-aveto-dev-links-to-it.md` (accepted: the owner's decision of 2026-10-26, option (a)). No earlier ADR is edited.

## 18. Hand off

**Next: Backend Architect, stage 4** (then Frontend Developer, stage 5, after the checkpoint in 14.1). Artefacts: section 14.0's files; the tests-first commit with `04-failfirst-32e54a6.txt`; `04-retrieval-check.json`; the checkpoint commit with `04-checkpoint.txt`; `04-implementation.md` listing anything that deviated from this spec and why. Context for stage 4: this spec (sections 3 to 14), `03-ux-spec.md` sections 1, 8 and 9 (for `test_page_cards.py`), `DECISIONS.md`. Context for stage 5: this spec (sections 0, 2, 3, 10, 14), `03-ux-spec.md` (whole), `tests/test_page_cards.py`, `04-implementation.md`.
