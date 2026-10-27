# Security & Privacy Review - result-page-clarity

> Stage 6, depth **smoke** (Charter C7.1). Tree: branch `claude/objective-kapitsa-83d3ae` at HEAD `d223e11` plus the uncommitted QA file. Base `main` 6ab5548. Method: read `git diff main...HEAD` for `aveto_service`, `docs/ARCHITECTURE.md`, `tests/test_service_pipeline.py`, `runs/polished-chat-experience`; grep for the patterns below; re-ran `uv run pytest -q tests/test_service_pipeline.py tests/test_result_first.py tests/test_service_ask_bytes.py` (42 passed) and `uv run ruff check` (clean). No product code was edited.

## Verdict: PASS (no finding of P0, P1 or P2; three P3 notes)

## Smoke checklist (each confirmed with evidence)

| Claim | Result | Evidence |
|---|---|---|
| No new route | Confirmed | `git diff main...HEAD -- aveto_service/app.py` is empty (0 lines). The route table lives there; the diff to `pages.py` adds a keyword parameter only (`pages.py` `_html(..., result_first: bool = False)`), no `add_route`/decorator. |
| No new input (form field, query, header read, cookie) | Confirmed | Form markup in `render.py` is unchanged (the `<form id="ask-form">` block is moved text, same single `question` textarea). `result_first` is hard-coded `True` in exactly two callers (`pages.py` `form_outcome` refusal branch, `result_page`), never derived from a request. No `Request`, header, cookie or query read added (grep of the aveto_service diff). The one client-side read added is `location.hash === "#result"` (`enhance.js:232`): a strict compare to a constant; the fragment is not sent to the server (browsers do not send it), not stored, not rendered, not used as a selector. Advisory P3-1. |
| No header change | Confirmed | `SECURITY_HEADERS` (`pages.py:24-33`) is not in the diff; still `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'`, `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`. `_html` and the 303 still use `dict(SECURITY_HEADERS)`. QA (13-qa-evidence section 2) compared all response headers for 16 states main vs HEAD: equal; `test_security_and_json_header_sets_are_byte_identical` passes (re-run). |
| No new third-party script, font or analytics | Confirmed | Grep of added lines in `aveto_service` for `http`, `src=`, `<script`, `<link`, `import`, `sendBeacon`, `XMLHttp`: no hit except the existing code context; the only added `fetch`-like hit is none. `pyproject.toml`, `uv.lock`, `Dockerfile`, `infra/` are not in the diff. The CSP (`'self'` only) would also block any such load. |
| No change to what is logged or stored; no question text | Confirmed | `abuse_log.py`, `pipeline.py`, `settings.py`, `app.py`, `result_store.py` not in the diff. `pages.py` and `render.py` have no `logging`/`print` call (grep). `enhance.js` adds no `console`, storage, cookie or beacon call. `raw` (the question) is still emitted only through `escape(raw)` in the textarea, as on main. |
| Nothing under `aveto_support/`, `prompts/`, `.claude/` (or `.agentic/`) | Confirmed | `git diff main...HEAD --stat -- aveto_support prompts .claude .agentic` prints nothing. |
| INV-1..INV-5 unchanged | Confirmed | Their text lives in `.agentic/SAFETY_INVARIANTS.md` and code under `aveto_support/`, `prompts/`, `.claude/agents` (all empty in the diff). INV-4 (verbatim passages, judge verdict only): the result cards come from `result_region`, not in the diff; the page change only reorders existing blocks (QA: the multiset of HTML lines is identical main vs HEAD for all eight result states). INV-5 (egress): no new network call; the service's one Anthropic POST path is untouched. INV-1: no GitHub write path in the diff. The `/ask` JSON golden is not in the diff and `test_ask_json_bytes_equal_main` passes. |
| No new XSS path | Confirmed | See below. |

## XSS analysis of the script change

- `resultFirst()` (`enhance.js:66-74`): reads node references with `querySelector("h1")` / `nextElementSibling` and re-parents existing elements with `appendChild`. It reads no text, `innerHTML` or attribute, and constructs no markup. The moved nodes are the server-rendered "What to expect" block and suggestion forms, which are constant strings in the `EXPECT` constant and `try_block`; none contains visitor text. Re-parenting a node does not execute anything.
- `land()` (`enhance.js:75-80`): `region.focus({ preventScroll: true })`, `getElementById("result-title")`, `getBoundingClientRect()`, `window.scrollTo(0, <number>)`. All arguments are numbers computed from layout. No string from the DOM or URL flows into a sink.
- Load-time check (`enhance.js:232`): `location.hash === "#result"` is a boolean compare against a literal; the fragment is not interpolated into any selector, HTML or `scrollTo` argument. A hash such as `#<img onerror=...>` fails the compare and nothing happens. `getElementById` is called with a literal.
- Pre-existing `swap()`/`adopt()` (parses the server's reply with `DOMParser` and `importNode`s server-rendered result nodes) is not changed in this diff; the new `land()` is called after it, not on its output. `box()`, `el()` use `textContent`. The CSP `script-src 'self'` with no `unsafe-inline` also stops inline handlers.
- Server side: `render.py` change moves the same f-string pieces (`EXPECT + above + try_block` into `lead` or `tail`); every visitor-controlled value (`raw`, error text) still goes through `escape(...)` exactly where it did. `EXPECT` is a module constant with no interpolation. `result_first` is a bool, not echoed.

## The two C1.7 changes

1. `tests/test_service_pipeline.py:180`: the pinned sha256 of `.claude/hooks/budget-guard.mjs` goes from `798c12fa...9922` (pre-v30) to `222f3970...9b8e`. I ran `shasum -a 256 .claude/hooks/budget-guard.mjs` now and it prints `222f39708d03770a33d09ba7579ee178fb78154ae60c1779239eab2cbf4a9b8e`, equal to the new pin. `git diff main...HEAD -- .claude` is empty, so the hook is the file that pack v30 installed on main and this slice does not touch it. Updating the pin to the installed v30 hash is a safe change: the test's purpose (detect any change to the guard files after the pins were set) still works, it is the same one-value update that any pack reinstall requires, the Charter (C1.7a) names this one value in this one file, and only the pack-install change is being recorded, not a slice change. It does not weaken a control: the other pinned core files (the judge agent, write-scope guard, skill files) are unchanged in the diff, and the test still fails on any further change to the hook. Residual note (P3-2): the pin proves the tree file equals the installed v30 file; it cannot show that v30's hook content is itself the content the owner intended, which was decided when v30 was installed on main (`a0af0f8`) and is outside this slice.
2. `runs/polished-chat-experience/13-live/tls-wrapper.py`: import order only (`import importlib.util` / `os` / `sys` split onto separate lines, sorted, blank line). The statements after the imports are unchanged (the `SSL_CERT_FILE` assignment, the `sys.path` insert, the `spec` lines are context lines in the diff). It is a recorded script of a past slice, not imported by the product or the tests. No control is weakened and no behaviour changes.

## Audit, adapter and approval checks

- Audit events: none added, removed or renamed (no event/log code in the diff). The service's log lines (abuse line, `startup_ok`, `startup_failed`, `unhandled`) are untouched.
- Placeholder/real client: `aveto_service` adapter files not in the diff; no new client; no model-call change.
- Approval bypass: no send/submit/publish/deploy path added. `requireApprovalBeforeSubmit`-style settings: not touched. (The deploy is gated by the Charter, not by this code.)
- CAPTCHA / anti-bot: nothing added. `scrollTo` is instant, no motion.
- Agentic threats: this slice adds no agent, tool or memory; the judge request is untouched (`test_request_has_no_tools` etc. are in the passing suite).

## Findings

| Sev | Finding | Action |
|---|---|---|
| P3-1 | `enhance.js:232` is the first read of the URL fragment by the script. Harmless (literal compare, never sent or rendered), but it is a client-side input in the strict sense. | Advisory. None needed. |
| P3-2 | The pin in `tests/test_service_pipeline.py` proves file-equals-installed-v30, not that v30's hook is what the owner intended; that was decided at the pack install. | Advisory. Release Manager may note the pin change as "pack install's doing" in `END_REVIEW.md`, as Charter C1.7 says. |
| P3-3 | `README.md` shows as modified in the working tree (uncommitted, 8 lines added) while this review ran; it was not in the diff `main...HEAD` and not in the git status at the start of the stage. I did not review it. Whatever stage owns it (Tech Writer) must keep to recorded figures (intent "Done means"), and the Security smoke does not cover public-claim review of it. | Advisory. Confirm at the Release Gate that README changes contain only recorded figures and no new claim about privacy/limits. |

## Not covered at smoke depth

- No browser run: the live focus, DOM order after Ask and rendering were not re-observed by me; I rely on `08-browser-checks.md` and QA. I read the script rather than ran it; the suite has no JS runtime, so T5-T7 are text checks.
- No adversarial pass: no fuzzing of `#result`/fragment variants, no hostile-HTML replies through `swap`, no review of `swap`/`adopt` (unchanged code), no review of `result_region` escaping (unchanged code).
- No dependency/CVE scan (no dependency changed), no secret scan beyond the grep of the added lines (no `.env`, token or key pattern in the diff; the added content is HTML text, JS identifiers and a hash).
- No review of the deployment, Bicep, image or live revision (stage 9-10); the rollback rehearsal is the Release Gate's.
- README.md working-tree change not reviewed (P3-3).
- Header equality is taken from QA's 16-state comparison and the passing header test plus my read of `SECURITY_HEADERS`; I did not rebuild the main tree myself.

## Recommendation to the Release Manager

GO from Security. No blocker or required fix.
