# 15c Words check: INV-4 and INV-5 against Charter C5.1 to C5.4 (Compliance Reviewer, adversarial check of the Architect's words)

> Checker model `claude-sonnet-5-5` (different from the author, `claude-opus-5-5`, Charter section 5). No shell: diffs read from `15c-invariants.worddiff` and `15c-invariants.diff`; code and tests read directly. **(U)** marks what I could not confirm and where I looked. I edited nothing but this file.

## Verdict: FAIL as written (Charter stop on two items only the owner can settle), otherwise PASS WITH REQUIRED REWORDINGS

- **Stops (stretches of the letter; Orchestrator may not waive):** S10 (INV-5 sentence edited), S11b (SDK runtime-fingerprint headers disclosed beyond C4.1 "exactly"). S1 is a stretch too but is cured by reverting it (a revert is in bounds, not a waiver).
- **Blocker (false sentence):** F1.
- **Required rewordings:** F2, F3.
- Everything else is advisory. INV-1 to INV-3 and C5.4 files: untouched (the diff's first hunk is at line 40; `.claude/`, `prompts/` absent from `git status`; `test_core_files_unchanged` pins them, not run by me).

## 1. Words removed (the word diff's four `[-x-]`)

| # | Removed | Re-added? | Inside C5.1 "replace only the sentence"? |
|---|---|---|---|
| 1 | `judge` (line 40) | yes, as `judge, on the operator's path,` | the word is kept; only a comma and 4 words inserted. **Not a removal, but an edit of a sentence C5.1 does not let be edited: see S1.** |
| 2 | `it runs only in` (42) | no | yes, this is the C5.1 sentence ("it runs only in the operator's own Claude Code session, and nothing in the program calls it") |
| 3 | `and` (43) | no | yes, same sentence |
| 4 | `exception,` (INV-5, 111) | yes, as `exception on the attended judge step,` | word kept; **an edit of a sentence C5.2 says stays: see S10.** |

Net: the only words genuinely gone are `it runs only in` and `and`, both inside the one sentence C5.1 lets be replaced. The retained words of that sentence ("the operator's own Claude Code session", "nothing in the program ... calls it") are kept, so nothing is removed beyond the allowance. The Architect's section 3 (five changed original lines: 40, 42, 43, 106, 111) matches the line diff exactly. INV-1, INV-2, INV-3: byte-identical (no hunk before line 40). **No removal beyond C5.1.**

Weakening test (C5.1 "no other word removed or weakened"): the replacement sentence keeps "nothing in the program calls it" for the program, and adds a second caller that is stated to have no deny list and no hook. Honest, not weaker. The one scope-narrowing of a control sentence is S1.

## 2. Additions, ruled one by one

Test applied (from `APPROVAL_PROTOCOL.md` "never widen a line by reading it generously"): an addition is a **bounded clarification** if it only restates, narrows or discloses facts about the callers, the JSON mapping, the test names or the one exception that the Charter names, and changes no word of a retained sentence. It is a **stretch** if it edits a retained sentence, or describes data or an actor the Charter line does not name.

| id | Addition (quoted) | Ruling |
|---|---|---|
| S1 | INV-4 `The judge, on the operator's path, is the agent` | **STRETCH.** It inserts into a retained control sentence and narrows its scope (deny list and hook now apply only "on the operator's path"). C5.1 allows replacing one named sentence and adding the mapping and test names; this is neither. **Cure in bounds:** delete `, on the operator's path,` and say `the judge has exactly two callers` as `judging has exactly two callers`. Item (2) already says it "does not run that agent and has no deny list or hook", so the agent description is not claimed for the service and the text stays true. Reverting is not a waiver. |
| S2 | `(package aveto_service, which is not the program, although it imports the program's code; no other route of the service reaches the judge)`, `does not run that agent and has no deny list or hook` | Bounded. Describes the named second caller; every word is a restriction or an honest limit. The program is already defined in INV-5 as `python -m aveto_support`. |
| S3 | the sha256 and "checked at startup ... and again before every call", `never logs, stores or returns the reply` | Bounded. Elaborates "pinned sha256" and "verdict-only parser", both named in C5.1. |
| S4 | the mapping (a), (b), (c) incl. "full verbatim text", the cause lists, the 4096-byte limit | In the list ("the mapping of the service's JSON to outputs (a), (b) and (c)"). "full verbatim text" is required for truth (Security 8a item 3). |
| S5 | `as its page for a form post or the page's own script`, `The service shows passages only on (a); the page shows the same passages as the JSON and no deciding-signal line.` | Bounded, but past the literal ("the service's JSON"): the page is not JSON. Every claim is a restriction that matches the JSON mapping (page code: `render.py`, no `signal` anywhere). Removable without making anything false. See A3 for what it leaves unsaid. |
| S6 | the service transcript counterpart `(The service holds the reply in memory only ... not the service's.)` | Bounded (restates S3 plus a disclosure that the provider keeps what it keeps). Not in C5.1's literal list; deleting it leaves no falsehood. |
| S7 | `Not shown by any test: ...` in both enforcement lists | Bounded. It is a limit on the test-name list C5.1/C5.2 allow, and is the honest form of rule 7. |
| S8 | INV-5 `(The public service, package aveto_service, is not the program, ...)` after `anywhere.**` | Bounded. A new sentence between two retained ones (both stay word for word); it is the signpost to the exception C5.2 adds. |
| S9 | INV-5 service paragraph: POST, host, path, SDK, attempts, timeout, key location, "makes no other network call", build-time `ingest`, logging sentence | Bounded. Each is a restriction on, or a description of, the one exception (HTTPS POST to `api.anthropic.com` with the Key Vault key) and its data. The logging and the "no other call" sentences add commitments, not permissions; they widen nothing. Note for the owner (advisory A1): these make SDK version, header names, timeout and attempts "MUST hold across releases". |
| S10 | INV-5 `The operator's session is the one exception on the attended judge step, and it is not the program.` | **STRETCH, and no in-bounds text is clean.** C5.2: "Every other sentence stays." Words were added inside it. Reverting leaves "the one exception" beside "The public service is the other exception": self-contradicting. Avoiding the word "exception" for the service (so the old sentence stays byte-identical) is possible but leaves a reader asking what the service is, since the session is also "not the program" and still counted. The Charter asks for both things (add an exception; keep the sentence), so this is a **Charter question for the owner**. Smallest amendment: C5.2 allows the words `on the attended judge step` in that one sentence. Fallback if not amended: revert it and open the service paragraph with `The public service is not the program and is not the operator's session; it has its own rule, for the service alone:`, accepting the reading risk. |
| S11a | `model`, `max_tokens` 1024, `output_config.effort` `high`, and the HTTP framing headers (`host`, `accept`, `accept-encoding`, `connection`, `content-length`, `content-type`, `anthropic-version`, `x-api-key`) | In bounds: model and effort are named by C3.1/C5.1; the rest cannot be removed from "an HTTPS POST ... authenticated by the key". |
| S11b | the SDK runtime-fingerprint headers `user-agent`, `x-stainless-arch`, `-os`, `-package-version`, `-runtime`, `-runtime-version`, `-read-timeout`, `-retry-count`, `-timeout`, `-async`, `-lang`, and the sentence `Of the question and the docs, each request carries only the data in Charter C4.1` | **STRETCH of the letter.** C5.2 says "carrying only the data in C4.1"; C4.1 says "exactly". The words restrict "only" to "the question and the docs" and then add OS, CPU architecture, Python version and SDK version. They are accurate (checked: 19 names, test asserts them) and not visitor data, and Security ruled at stage 14 that C4.1 is not breached; but that is Security's reading, not the owner's, and Charter 9.1 names "new data". Do **not** delete the words (INV-5 would then be false for the built service). Cure: the owner ratifies (amend C4.1/C5.2 or accept at END_REVIEW before the deploy). |

## 3. Truth: findings

### F1 (blocker, false sentence) INV-4 (c): "and when the payload cannot be built or any other error occurs"
Not always HTTP 502. `pipeline.py:242-243`: a `QuestionFormatError` from `retrieve_for_judge` (a question with no searchable words, `search.py:457-458`) is `unusable_question`, **HTTP 400**, before any model call (test `test_each_limit_fails_closed_no_model_call[3-unusable]` asserts `unusable_question` with 0 retrievals). Only `PayloadMarkerError` and other exceptions are 502 `judge_error`.
Minimal rewording: `and on any other error once the question is accepted (a question with no searchable words is refused earlier with HTTP 400 and shows nothing)`.

### F2 (required) INV-5 retained "No credentials are sent." now collides with the service
The service sends the API key (`x-api-key`). The retained sentence sits in the program paragraph, but the S8 signpost says only "its own exception is stated below". Add inside the service exception (an addition, in bounds): `The key is the one credential the service sends; "No credentials are sent" above is about the program's two GET downloads.`

### F3 (required) Key Vault wiring is stated as fact and listed under tests that do not test it
The words: "authenticated by the key the container reads from Key Vault `kv-aveto-ask-gp` (secret `anthropic-api-key`, resolved by Container Apps through the app's user-assigned identity into the environment variable `ANTHROPIC_API_KEY`)". Facts match `infra/main.bicep` (44-45, 162-169, 183). But the only cited tests are `test_bicep_no_secret_literals` (asserts no literal and the string `keyVaultUrl` present; `ANTHROPIC_API_KEY` absent from the Dockerfile) and `test_dockerfile_static`. No test asserts the vault name, secret name, identity or `secretRef`. Grep of `tests/test_infra_static.py` for `ANTHROPIC_API_KEY|secretRef|anthropic-api-key|kv-aveto|identity`: one hit, the Dockerfile line. Add to "Not enforced by any test": `the Key Vault wiring (vault, secret, identity, environment variable), read from infra/main.bicep`.

### Facts checked and found true
- Model `claude-sonnet-5-5`, `max_tokens` 1024, effort `high`, timeout 20.0, `max_retries=0`, `MAX_ATTEMPTS` 2, base URL pinned with `base_url=BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS` set at all raises (`anthropic_judge.py:22-28,108-112`). SDK source: an explicit `base_url` beats `ANTHROPIC_BASE_URL` (`_client.py:232-234`); with an explicit `api_key`, `ANTHROPIC_AUTH_TOKEN` and profile credentials are not consulted (`_client.py:211-225`), so no `authorization` header is added: the 19-name claim holds as deployed.
- 19 header names counted: 9 non-stainless + 10 `x-stainless-*` = 19; same set in `EXPECTED_HEADER_NAMES` (test_anthropic_judge.py:332-352) and in 09 note and 14 section 3.
- Payload is `judge.format_judge_input(judge.retrieve_for_judge(...))`, which is what `judge-input` prints (`__main__.py:152-157`); test asserts equality with the fake's recorded call.
- Parser: `judge.parse_verdict(call.reply, judge.BLOCK_ID)`, last non-empty line; `Verdict` carries only the token (`judge.py:69-71`). Length check `len(reply.encode("utf-8")) > judge.MAX_REPLY_BYTES` (4096) before parse (`pipeline.py:293`).
- (c) causes: empty, control/format char, malformed, wrong block id, multi-token (`judge.py:144-167`); timeout, connection, 4xx/5xx, stop reason, `tool_use`/`server_tool_use`, prompt hash, no key (`anthropic_judge.py`, `pipeline.py:269-298`). `to_json` for (b) has exactly `outcome`, `text`, `signal`; for (c) exactly `outcome`, `text`.
- Gate order in code: kill switch, cross-site, body cap, shape (`app.py:158-167`).
- Logging: abuse line `{"t","ip","o"}` with a 16-hex prefix; ops codes `startup_ok`, `startup_failed` (+ category `prompt_hash|index|model`), `unhandled` (`abuse_log.py`). stderr empty is asserted.
- Startup hash check mismatch is `SystemExit(1)` with one ops line (`app.py:43-56`); per-call check in the adapter before any request (`anthropic_judge.py:117-118`).
- Build-time `ingest` without `--with-reranker`: `Dockerfile:20`; `test_dockerfile_static` asserts presence of `aveto_support ingest` and absence of `--with-reranker`.

## 4. The bold INV-4 sentence (R1)

"No model ever produces, selects among, or alters the text shown: the verdict decides only whether `retrieve`'s whole output is printed."

Ruling: **reads true for the service; advisory, no stop.** Part 1 (no model produces, selects among or alters the text) is true and tested: `_files_out(found)` passes every `retrieve` hit and passage through, `test_service_passages_byte_identical_to_retrieve` compares `text.encode("utf-8")` and heading, lines, urls; `test_judge_error_shows_nothing_*` and `test_not_answerable_is_exactly_no_confident_match` show nothing on (b)/(c). Part 2 holds if "`retrieve`'s whole output" means the whole result `retrieve` returns (all files, all passages); it fails only if it means the CLI's printed excerpts, which the service does not print (it shows the full text, no scores, plus links). The (a) mapping in the same section names that difference in terms ("where `judge-apply` prints `retrieve`'s CLI output, which shows an excerpt"). The service shows a superset in content, never a model-chosen subset, so the sentence's purpose is intact. I cannot edit the sentence (C5.1). If the owner wants it literally true, the amendment is to allow `(for the service: every passage of that result, in full)` after "printed". Record the reading in `END_REVIEW.md`.

## 5. The INV-5 exception: can it be read wider than C5.2?

- **Any host:** no. The host and path are named (`https://api.anthropic.com/v1/messages`), "the host fixed in code". `ANTHROPIC_BASE_URL` ignored (tested with an evil URL).
- **Any data:** the data sentence is bounded by C4.1 plus the protocol and header list. A future SDK that adds a header breaks the "exactly" list (the test would fail) rather than silently widening it. Open point: S11b.
- **The operator's session:** no. "for the service alone, and it is not the program"; the session keeps its own paragraph, unchanged apart from S10.
- **The build:** the build performs `ingest`'s existing two GETs (allowed since before this run); the exception does not cover any other build-time call. The text says "the service makes no other network call" (not test-enforced; disclosed). The build's own egress (ACR Tasks pulling base images, `uv sync` fetching packages) is not mentioned and not covered: (U) not checked here; it is not a data flow of the service and Charter C8.3 allowed `az acr build`.
- **A second kind of call** (batch, token counting, another path): "one kind of network call of its own ... POST to /v1/messages" excludes it; the path itself is not test-enforced (disclosed).
- **A local run of the package with a key:** "run by uvicorn in the Azure Container App" ties it to the deployment. A local run with a real key is not covered by the words; the QA and gate stages use the deployed service or fakes.

## 6. Advisory findings (no action needed to pass)

- **A1** The exception turns operational details (SDK 1.7.0, 20 s, two attempts, 19 header names, 1024 tokens) into "MUST hold across releases" commitments. Fine if intended; an SDK bump will need an INV edit.
- **A2** "a 20-second timeout per attempt": `timeout=20.0` is httpx's per-phase timeout (connect, read, write, pool each), not a wall-clock cap. Say "a 20-second timeout (per phase)" or leave. `test_real_client_config` asserts `sdk.timeout == 20.0` only.
- **A3** The page for (b) and (c) shows fixed copy ("No confident match was found, so nothing is shown.", "We couldn't decide this time") plus an issue link, not the exact strings `no confident match` / `judge error`. The mapping's preamble ("as its page") might be read to promise them. Removing `and as its page for a form post or the page's own script` from the preamble is in bounds and removes the question; or add "its fixed copy and links".
- **A4** (a) is not exhaustive: the JSON also carries `docs.repo`, `docs.commit` and each file's `rank` (`pipeline.py:101-120`). Not contradicted by the words ("no scores" true); add "and the docs repo and commit" if completeness is wanted.
- **A5** "every library logger is silenced": the code silences 10 named loggers and the only handler passes only the two service loggers (`_AllowListFilter`). `test_library_loggers_silenced` also checks `some.other.module` and the root logger. True in effect; wording is stronger than the list. Python `warnings` to stderr are not logging; `test_question_never_logged` asserts stderr empty on its paths.
- **A6** "no other route of the service reaches the judge": read, not tested, and the enforcement list says so. A route-table test (the only route whose handler reaches `AskService.ask` is `POST /ask`) would close it cheaply.
- **A7** `test_pinned_hash_is_the_core_pin` asserts a constant equals a literal; it enforces nothing about the prompt file. The pin is really enforced by `test_prompt_hash_mismatch_fails_closed`, `test_startup_fails_closed_on_prompt_hash_mismatch` and `test_core_files_unchanged` (prompt sha256). Harmless in the list.
- **A8** (U) If `ANTHROPIC_CUSTOM_HEADERS` is set, `AnthropicJudgeClient(...)` raises at import in `main.py:19`, outside `load_runtime`'s try: no `startup_failed` ops line is written, and uvicorn's exit behaviour was not checked (Architect's same (U)). The words say only "the adapter's construction fails", which is true.
- **A9** The INV-5 text cites `runs/public-ask-the-docs/CHARTER.md` for the data definition and also restates it; keep both (the restatement carries the truth if the run folder moves).
- **A10** (U) Not confirmed: that `claude-sonnet-5-5` accepts the request as sent (no live call; disclosed), the SDK header values (captured once offline; disclosed), what Anthropic keeps (disclosed), that uv.lock pins `anthropic` 1.7.0 (read in 08 note and 14 section 7, not re-read in `uv.lock`).

## 7. Tests: cited names and what they assert

All 44 distinct cited names exist as `def test_<name>` (23 in the INV-4 list + 24 in the INV-5 list, 3 in both); found by Grep under `tests/`. I read the body of 36; each asserts what the words say it enforces, with the limits noted.

| Test | Asserts | Fit to the claim |
|---|---|---|
| `test_service_passages_byte_identical_to_retrieve` | text bytes, heading, line range, urls, rank, key sets, signal | yes (a) |
| `test_payload_sent_is_format_judge_input_of_same_result` | judge got exactly `(system_prompt, format_judge_input(retrieve(normalised)))`; prompt bytes = file; sha256 = pin | yes |
| `test_not_answerable_is_exactly_no_confident_match` | exact JSON of (b), `files == ()` | yes |
| `test_judge_error_shows_nothing_bad_reply` (7 replies) | exact 502 JSON; covers wrong id, multi-token, control char, malformed, empty | yes (c) replies |
| `..._transport` (7 categories), `..._unexpected_adapter_error`, `..._payload_marker`, `test_placeholder_judge_raises...` | exact (c) JSON; marker case makes no judge call; placeholder maps to `judge_error` | yes; does **not** cover the 400 corner (F1) |
| `test_reason_never_leaves_parser_service` | canary reason absent from JSON, repr, health, stdout/stderr, caplog, for both tokens | yes |
| `test_oversize_reply_is_judge_error_and_charged`, `..._over_http` | 200 KB reply that parses is 502, usage charged; exactly at 4096 still parsed; no model text over HTTP | yes |
| `test_request_has_no_tools`, `test_request_model_and_effort_pinned`, `test_request_body_only_c41_data` | kwargs have no `tools`/`tool_choice`/`metadata`; body key set; model/effort/1024 | yes, at the kwargs level (the real wire body is Security's offline capture, disclosed) |
| `test_extract_reply_text_blocks_only`, `test_stop_reason_not_end_turn_is_judge_error`, `test_sdk_errors_map_to_fixed_categories` | thinking dropped, `tool_use`/`server_tool_use` raise, six stop reasons, 4xx/timeout/other, no text leak | yes |
| `test_retry_once_only_on_retryable`, `test_no_retry_on_timeout` | two requests at most; none after timeout/4xx | yes ("at most two attempts") |
| `test_prompt_hash_mismatch_fails_closed`, `test_startup_fails_closed_on_prompt_hash_mismatch` | zero requests; `SystemExit(1)` with `startup_failed`/`prompt_hash` | yes |
| `test_pinned_hash_is_the_core_pin` | constant equals literal | weak (A7) |
| `test_real_client_config`, `test_real_client_blocked_offline` | `max_retries` 0, timeout 20.0; no key/payload in logs with the network blocked | yes (timeout caveat A2) |
| `test_base_url_env_cannot_redirect_and_header_set_is_exact`, `test_custom_headers_env_fails_closed` | host/scheme with an evil `ANTHROPIC_BASE_URL`; exact 19 names; construction raises, no request | yes; values and path not asserted (disclosed) |
| `test_anthropic_judge_import_allow_list` | import roots of the adapter module | yes |
| `test_ask_json_contract`, `test_health_never_calls_model` | key sets per outcome and status; `/health` makes no judge call and no embed | yes; does not show other routes (disclosed) |
| `test_passages_byte_identical_inside_the_page` | `<code>{text}</code></pre>`, path, url, lines, count | yes (plain text; escaping is covered by `test_markup_bearing_passage_is_escaped`, not cited) |
| `test_each_limit_fails_closed_no_model_call`, `test_pipeline_kill_switch_...`, `test_cross_site_...` | no judge call and no embed on each refusal; one abuse line | yes |
| `test_question_never_logged`, `test_abuse_line_shape_exact`, `test_ops_lines_fixed_codes_only`, `test_library_loggers_silenced` | canary in many forms absent from stdout/stderr/caplog; exact line shapes; stderr empty | yes |
| `test_settings_repr_and_str_hide_the_api_key`, `test_fastapi_telemetry_auto_configure_is_off` | repr/str lack the key; auto-configure False even with the env var set | yes |
| `test_core_files_unchanged` | sha256 of 18 core files and C5.4 files, file sets of `aveto_support/` and `.claude/hooks/` | yes (C5.3/C5.4 side) |
| `test_bicep_no_secret_literals`, `test_dockerfile_static` | no secret literal, no `ARG/ENV` key, no `--with-reranker`, `ingest` present | partly: see F3 |
| `test_aveto_support_imports_no_service_deps` | `aveto_support` imports no service/SDK package | yes |

Not read in full (names confirmed to exist only): `test_adapter_mutes_sdk_loggers` (one-line body read), `test_sdk_errors_map_to_fixed_categories` body read; none in the two lists unread beyond these.

## 8. Required rewordings, in one place

1. **S1**: delete `, on the operator's path,`; write `judging has exactly two callers` for `the judge has exactly two callers`.
2. **F1**: (c) last clause as above.
3. **F2**: one sentence in the service exception naming the key as the one credential sent.
4. **F3**: add the Key Vault wiring to the INV-5 "Not enforced by any test".
5. **S10, S11b**: owner. Either amend the Charter (new hash) for the two narrow additions, or take the fallbacks; S11b has no fallback that keeps INV-5 true.
6. Optional: A2, A3, A4.

After 1 to 4 and an owner ruling on 5 the words are inside C5.1/C5.2 and true for the built service as far as I could check.
