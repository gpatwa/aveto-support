# 15a Safety text and architecture note: public-ask-the-docs (Software Architect, depth standard)

> Model `claude-opus-5-5`, effort high (Charter C3.2). Worktree HEAD b860183. Files edited:
> `.agentic/SAFETY_INVARIANTS.md` (INV-4, INV-5 only) and `docs/ARCHITECTURE.md`. Nothing committed.
> **(U)** marks what I could not confirm, with where I looked.

**Status: done. No STOP taken.** Every change is inside Charter C5.1 / C5.2 as I read them; four
reading risks for the 15c checker are listed in section 5.

## 0. Sources read

`CHARTER.md` (C4.1, C4.2, C5.1 to C5.4, C8.3), `05-tech-spec.md` §1, §2, §3, §11, `14-security-review.md`
(all; §3, §8a to §8c, S-A2, S-A4, S-A12), `09-ai-adapter-note.md`, `08-backend-note.md` (incl. the
security rounds), the whole current `.agentic/SAFETY_INVARIANTS.md`, `docs/ARCHITECTURE.md`; code:
`aveto_service/{anthropic_judge,app,pipeline,abuse_log,main}.py`, `limits.py` constants,
`result_store.py` constants, `settings.py` env reads, `infra/main.bicep` (names, env, scale), the
`Dockerfile` (ingest line, USER, CMD), `aveto_support/judge.py` (`parse_verdict`, `MAX_REPLY_BYTES`,
`format_judge_input`); tests: every `def test_` in `tests/test_service_*.py`,
`tests/test_anthropic_judge.py`, `tests/test_infra_static.py`, and the bodies of the tests whose
coverage the words lean on (section 3).

## 1. The new INV-4 words, in full

**1a. The agent sentence, scoped by insertion, and the replacement of the C5.1 sentence** (file lines
40 to 57; the words `on the operator's path,` are inserted, no word of that sentence removed; the text
from `the judge has exactly two callers` to `returns the reply.` replaces "it runs only in the
operator's own Claude Code session, and nothing in the program calls it."):

```
  The judge, on the operator's path, is the agent `aveto-answerability-judge`, pinned to the full model
  ID `claude-sonnet-5-5`, with no `tools` entry, a deny list ending in
  `mcp__*`, and a hook that refuses every tool call; the judge has exactly
  two callers. (1) The operator's own Claude Code session, which runs that
  agent; nothing in the program (`python -m aveto_support`) calls it.
  (2) The public service's `POST /ask` (package `aveto_service`, which is not
  the program, although it imports the program's code; no other route of the
  service reaches the judge), which does not run that agent and has no deny
  list or hook: it calls the Anthropic Messages API with the model
  `claude-sonnet-5-5`, no `tools` in the request, the system prompt
  `answerability-judge-v1` at sha256
  `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427` (checked
  at startup, where a mismatch stops the service from starting, and again
  before every call, where a mismatch is a judge error with nothing sent), and
  as its one user message exactly the payload `judge-input` would print for the
  same question and index; it reads the reply with the same verdict-only
  parser (`parse_verdict`: the token from the last non-empty line) and never
  logs, stores or returns the reply.
```

**1b. The service's JSON mapping to (a), (b), (c) and the transcript counterpart** (added after the
existing parenthetical "(The operator's Claude Code session keeps its own transcript ... not the
program's.)", file lines 81 to 109; pure addition):

```
  The service maps the judge's result to the same three outputs, as JSON for
  a JSON request to `POST /ask`, and as its page for a form post or the page's
  own script:
  (a) on `ANSWERABLE`, HTTP 200, `outcome` `answer`: the files and passages
  of the same `retrieve` result (default ranking) whose payload was sent, in
  the same order, each with its path, heading, line range and pinned-commit
  permalink and **each passage's full verbatim text** (where `judge-apply`
  prints `retrieve`'s CLI output, which shows an excerpt of each passage); no
  scores; and, in the JSON, the deciding-signal line of (a) above in `signal`;
  (b) on `NOT_ANSWERABLE`, HTTP 200: the JSON `outcome` `no_confident_match`,
  `text` `no confident match` and the deciding-signal line of (b) above in
  `signal`, and nothing else (no passage, path or reason);
  (c) HTTP 502: the JSON `outcome` `judge_error` and `text` `judge error`, and
  nothing else, on any reply it cannot use (over 4096 bytes in UTF-8, the
  limit `judge-apply` applies; empty, containing a control or format
  character, malformed, or with a wrong block id or more than one verdict
  token), on any call that yields no usable reply (a timeout, a connection
  error, an HTTP error status, a stop reason other than `end_turn`, a
  `tool_use` or `server_tool_use` block, a prompt-hash mismatch, or no key
  configured), and when the payload cannot be built or any other error
  occurs. The service names no cause: it writes no stderr line, and its log
  lines carry only fixed codes, never the cause.
  The service shows passages only on (a); the page shows the same passages as
  the JSON and no deciding-signal line.
  (The service holds the reply in memory only to check its length and parse
  it; it never logs, stores or returns it, and of the reply it keeps only the
  verdict token. What Anthropic keeps of the request and the reply is kept under
  Anthropic's terms, not verified by an agent; that is the provider's record,
  not the service's.)
```

**1c. The enforcement names for the service's caller** (added after the existing enforcement
parenthetical, file lines 133 to 156; pure addition):

```
  *(For the service's caller, enforced by
  `test_service_passages_byte_identical_to_retrieve`,
  `test_passages_byte_identical_inside_the_page`,
  `test_payload_sent_is_format_judge_input_of_same_result`,
  `test_ask_json_contract`, `test_not_answerable_is_exactly_no_confident_match`,
  `test_judge_error_shows_nothing_bad_reply`,
  `test_judge_error_shows_nothing_transport`,
  `test_judge_error_shows_nothing_unexpected_adapter_error`,
  `test_judge_error_shows_nothing_payload_marker`,
  `test_placeholder_judge_raises_and_pipeline_maps_to_judge_error`,
  `test_oversize_reply_is_judge_error_and_charged`,
  `test_oversize_reply_shows_no_model_text_over_http`,
  `test_reason_never_leaves_parser_service`, `test_request_has_no_tools`,
  `test_request_model_and_effort_pinned`, `test_prompt_hash_mismatch_fails_closed`,
  `test_pinned_hash_is_the_core_pin`,
  `test_startup_fails_closed_on_prompt_hash_mismatch`,
  `test_extract_reply_text_blocks_only`,
  `test_stop_reason_not_end_turn_is_judge_error`,
  `test_sdk_errors_map_to_fixed_categories`, `test_health_never_calls_model`
  and `test_core_files_unchanged`. Not shown by any test: that no route but
  `POST /ask` reaches the judge (read in the code;
  `test_health_never_calls_model` covers `GET /health` only); that
  `claude-sonnet-5-5` accepts the request as sent (no live call is made
  before deployment); and what Anthropic keeps.)*
```

## 2. The new INV-5 words, in full

**2a. Beside "The program never sends ..." (8a item 6)**: inserted after `anywhere.**`, no word removed
(file lines 173 to 177; the original continuation `` `retrieve`, `eval` (with or `` moves to its own
line, unchanged):

```
  a question, passage or any user text anywhere.** (The public service,
  package `aveto_service`, is not the program, although it imports the
  program's code; its own exception is stated below, after the operator's
  session.)
  `retrieve`, `eval` (with or
```

**2b. "The one exception" (8a item 7)**: the words `on the attended judge step` inserted, no word
removed (file line 182):

```
  **The operator's session is the one exception on the attended judge step, and it is not the program.**
```

**2c. The service exception** (added after "...is outside this invariant and was not measured.",
before the existing enforcement parenthetical; pure addition):

```
  **The public service is the other exception, for the service alone, and it
  is not the program.** The service (package `aveto_service`, run by uvicorn
  in the Azure Container App) makes one kind of network call of its own: for
  a question that has passed its limits, an HTTPS POST to
  `https://api.anthropic.com/v1/messages`, the host fixed in code
  (`ANTHROPIC_BASE_URL` is ignored, and if `ANTHROPIC_CUSTOM_HEADERS` is set
  at all the adapter's construction fails), through the `anthropic` Python
  SDK 1.7.0 pinned by `uv.lock`, with at most two attempts per question and a
  20-second timeout per attempt. Of the question and the docs, each request
  carries only the data in Charter C4.1 of
  `runs/public-ask-the-docs/CHARTER.md`: the fixed judge prompt
  `answerability-judge-v1` (as `system`) and, as the one user message, the
  payload `judge-input` would print for the question (the normalised
  question, at most 500 characters on one line, and the passages `retrieve`
  would show with their paths, headings and line ranges). Beside that data it
  carries only protocol fields that are the same in every request (`model`
  `claude-sonnet-5-5`, `max_tokens` 1024, `output_config.effort` `high`) and
  the SDK's own headers, exactly `host`, `accept`, `accept-encoding`, `connection`,
  `content-length`, `content-type`, `user-agent`, `anthropic-version`,
  `x-api-key`, `x-stainless-arch`, `x-stainless-async`, `x-stainless-lang`,
  `x-stainless-os`, `x-stainless-package-version`,
  `x-stainless-read-timeout`, `x-stainless-retry-count`,
  `x-stainless-runtime`, `x-stainless-runtime-version` and
  `x-stainless-timeout`. Apart from the key, these headers describe the
  request and the service's own runtime (SDK version, operating system, CPU
  architecture, Python runtime and version, timeout and retry settings),
  never a visitor. No IP address, visitor identifier or visitor request
  header is sent, and the request offers the model no tool. The request is
  authenticated by the key the container reads from Key Vault
  `kv-aveto-ask-gp` (secret `anthropic-api-key`, resolved by Container Apps
  through the app's user-assigned identity into the environment variable
  `ANTHROPIC_API_KEY`); the key is never in the image, the repo or a log.
  Anthropic receives this as data processor under its Commercial Terms
  (Charter C4.1); what it keeps, and for how long, was not verified by an
  agent. The service's index and embedding model come from `ingest`'s two
  GETs above, made while the image is built (without `--with-reranker`); the
  service makes no other network call. The service logs neither the request
  nor the reply: its only log lines are the abuse line (a time, the first 16
  hex characters of a salted per-process hash of the visitor's address, and
  an outcome code) and the fixed ops lines `startup_ok`, `startup_failed`
  with one fixed category (`prompt_hash`, `index` or `model`), and
  `unhandled`; none carries a question, passage, payload, reply, header, URL
  or exception text, and every library logger is silenced.
```

**2d. The enforcement names for the service** (added after the existing enforcement parenthetical,
at the end of the file; pure addition):

```
  *(For the service, enforced by
  `test_base_url_env_cannot_redirect_and_header_set_is_exact`,
  `test_custom_headers_env_fails_closed`, `test_request_body_only_c41_data`,
  `test_request_has_no_tools`, `test_request_model_and_effort_pinned`,
  `test_retry_once_only_on_retryable`, `test_no_retry_on_timeout`,
  `test_real_client_config`, `test_real_client_blocked_offline`,
  `test_anthropic_judge_import_allow_list`,
  `test_aveto_support_imports_no_service_deps`,
  `test_each_limit_fails_closed_no_model_call`,
  `test_pipeline_kill_switch_refuses_without_retrieval_or_model`,
  `test_cross_site_post_is_refused_before_retrieval_and_model`,
  `test_health_never_calls_model`, `test_question_never_logged`,
  `test_abuse_line_shape_exact`, `test_ops_lines_fixed_codes_only`,
  `test_library_loggers_silenced`, `test_adapter_mutes_sdk_loggers`,
  `test_fastapi_telemetry_auto_configure_is_off`,
  `test_settings_repr_and_str_hide_the_api_key`,
  `test_bicep_no_secret_literals`, `test_dockerfile_static`, and the autouse
  network block. Not enforced by any test: the values of the SDK's headers
  (the names are asserted; the values were captured once, offline, with SDK
  1.7.0, at stage 14 of public-ask-the-docs); the path `/v1/messages` (the
  SDK's; the test asserts scheme and host); that the service makes no other
  network call (read in the code and the dependencies at stage 14); what the
  Container Apps ingress does with the visitor's address; that the build-time
  `ingest` ran and matched (the image build log); and what Anthropic keeps.)*
```

## 3. Removed lines (what `git diff -U0 .agentic/SAFETY_INVARIANTS.md` should show as `-`)

**(U) I could not run `git diff`:** my tool boundary is Read, Write, Edit, Grep, Glob (no shell). The
list below is from reading the file before the first edit and after the last, line by line. The
Orchestrator (or 15c / stage 16) should run `git diff -U0 .agentic/SAFETY_INVARIANTS.md` and compare
it with this list; any `-` line not below is a defect of mine.

Lines 1 to 39 (header, INV-1, INV-2, INV-3, the start of INV-4 incl. its bold principle) are
untouched, as are original lines 41, 44 to 105, 107 to 110 and 112 to 166. **Five original lines
change**; I expect `git diff -U0` to show exactly these five as removed:

| # | Original line (number in the file at b860183) | Why it changes | Words removed | Bound |
|---|---|---|---|---|
| 1 | 40 `  The judge is the agent `aveto-answerability-judge`, pinned to the full model` | `, on the operator's path,` inserted after `The judge` (8a item 2: scope to the operator's caller) | none | C5.1: no word removed or weakened; the scoping is the Orchestrator's instruction from 8a item 2 |
| 2 | 42 `` `mcp__*`, and a hook that refuses every tool call; it runs only in the `` | holds the first half of the C5.1 sentence | `it runs only in the` | C5.1 "may replace the sentence" |
| 3 | 43 `  operator's own Claude Code session, and nothing in the program calls it.` | the second half of the C5.1 sentence | the whole line, i.e. `operator's own Claude Code session, and nothing in the program calls it.` (the new words say again "The operator's own Claude Code session" and "nothing in the program (`python -m aveto_support`) calls it") | C5.1 "may replace the sentence" |
| 4 | 106 `  a question, passage or any user text anywhere.** `retrieve`, `eval` (with or` | text inserted after `anywhere.**`; the rest of the line moved, unchanged, to its own line (a local reflow of one line) | none | C5.2 "every other sentence stays": it stays, word for word; 8a item 6 asked for the exception beside it |
| 5 | 111 `  **The operator's session is the one exception, and it is not the program.**` | `on the attended judge step` inserted after `the one exception` | none | C5.2 "every other sentence stays": it stays, every word kept, and is now true with two exceptions (8a item 7) |

So the only words removed from the file are the C5.1 sentence ("it runs only in the operator's own
Claude Code session, and nothing in the program calls it"). Every other change is an insertion.
INV-1, INV-2, INV-3 (C5.3) are byte-identical: no edit touched lines 1 to 39. I made no change to
`prompts/`, `.claude/` or the skills (C5.4); I have no write access to them.

## 4. Each Charter bound and the words that satisfy it

| Bound | Words |
|---|---|
| C5.1 "may replace the sentence ... with words naming exactly two callers" | 1a: "the judge has exactly two callers. (1) ... (2) ..." |
| C5.1 "the operator's session (unchanged)" | 1a (1): "The operator's own Claude Code session, which runs that agent; nothing in the program (`python -m aveto_support`) calls it." The agent, its pin, `tools`, deny list and hook are the existing words, scoped by "on the operator's path" |
| C5.1 "the service's `POST /ask`, which calls the Anthropic Messages API with `claude-sonnet-5-5`" | 1a (2): "The public service's `POST /ask` ... calls the Anthropic Messages API with the model `claude-sonnet-5-5`" |
| C5.1 "no tools in the request" | 1a (2): "no `tools` in the request"; also "does not run that agent and has no deny list or hook", so the agent's guarantees are not claimed for it |
| C5.1 "prompt `answerability-judge-v1` at its pinned sha256" | 1a (2): the id and the full sha256, with when it is checked |
| C5.1 "the same verdict-only parser" | 1a (2): "reads the reply with the same verdict-only parser (`parse_verdict` ...) and never logs, stores or returns the reply"; 1b parenthetical: "of the reply it keeps only the verdict token" |
| C5.1 "may add the mapping of the service's JSON to outputs (a), (b) and (c)" | 1b (a), (b), (c); (a) says "each passage's full verbatim text (where `judge-apply` prints ... an excerpt ...)" (Orchestrator setup note 4, 8a item 3); (c) lists the service's own causes incl. the 4096-byte limit now applied (S-A4), transport failures, stop reason, `tool_use`, prompt hash (8a item 4) |
| C5.1 "may add the names of new tests" | 1c; every name verified (section 6) |
| C5.1 "No other word removed or weakened" | section 3: only the C5.1 sentence's words removed. Nothing weakened: the operator path's words are all kept, and the program's "nothing ... calls it" is kept for the program |
| C5.2 "may add one exception for the service alone" | 2c: "**The public service is the other exception, for the service alone, and it is not the program.**" |
| C5.2 "HTTPS POST to `api.anthropic.com`" | 2c: "an HTTPS POST to `https://api.anthropic.com/v1/messages`, the host fixed in code (`ANTHROPIC_BASE_URL` is ignored, and if `ANTHROPIC_CUSTOM_HEADERS` is set at all the adapter's construction fails)", at most two attempts, 20 s each |
| C5.2 "carrying only the data in C4.1" | 2c: "Of the question and the docs, each request carries only the data in Charter C4.1 ...: the fixed judge prompt ... the payload ... (the normalised question, at most 500 characters ..., and the passages ... with their paths, headings and line ranges)." The protocol fields and the 19 header names are named beside it, as Security ruled (14 §3, §8b): they describe the request and the service's runtime, never a visitor. "No IP address, visitor identifier or visitor request header is sent" is C4.1's own exclusion |
| C5.2 "authenticated by the key the container reads from Key Vault" | 2c: "authenticated by the key the container reads from Key Vault `kv-aveto-ask-gp` (secret `anthropic-api-key`, ...)" |
| C5.2 "may add the names of new tests" | 2d; every name verified (section 6) |
| C5.2 "Every other sentence stays" | section 3 rows 4 and 5: both flagged sentences stay word for word, with insertions only |
| C5.2 "`ingest`, `retrieve`, `eval`, `judge-input` and `judge-apply` stay as they are" | their sentences are untouched; 2c says the image build runs `ingest`'s same two GETs without `--with-reranker` |
| C5.3 INV-1, INV-2, INV-3 unchanged | lines 1 to 39 untouched |
| C4.2 / S-A12 (ops lines reach Log Analytics) | 2c: "its only log lines are the abuse line ... and the fixed ops lines `startup_ok`, `startup_failed` with one fixed category (...), and `unhandled`" |

## 5. Reading risks for the 15c checker, and what I could not confirm

Reading risks (my judgement that each is inside the bound; the checker rules):

- **R1. A sentence I may not touch.** INV-4's bold principle ends "the verdict decides only whether
  `retrieve`'s whole output is printed." For the service, what is shown on (a) is every passage of
  `retrieve`'s result in full, on a page or in JSON, not the CLI's printed output. I read "`retrieve`'s
  whole output" as the result `retrieve` returns, which holds the full passage text, so the sentence
  stays true; the (a) mapping states the difference explicitly. C5.1 lets me replace only the one
  sentence, so if the checker reads this sentence as false for the service, the fix is a Charter
  amendment (Charter section 9, stop 5), not an edit here.
- **R2. Additions to INV-4 beyond C5.1's literal list** (callers, mapping, test names): the insertion
  "on the operator's path" (8a item 2), the line "The service shows passages only on (a); the page
  shows the same passages as the JSON and no deciding-signal line." (part of the mapping), the
  service transcript parenthetical (8a item 5) and the "Not shown by any test" sentence. Each was asked
  for by the Orchestrator's brief, removes no word and weakens nothing. If the checker rules any of
  them outside C5.1, deleting that addition returns the text to a state inside the bound.
- **R3. Insertions into two existing INV-5 sentences** (section 3 rows 4 and 5). C5.2 says "every
  other sentence stays". Both stay word for word; row 5 adds a qualifier ("on the attended judge
  step") without which the sentence is false (8a item 7). If the checker reads "stays" as
  byte-identical, row 5 cannot be both unchanged and true, and that is a Charter question.
- **R4. Gate order.** The brief listed "kill switch, body cap, cross-site refusal". The code checks
  the cross-site refusal **before** reading the body (`app.py:158-164`; 08 note, S-A8: "Checked after
  the kill switch and before the body read"). `docs/ARCHITECTURE.md` states the code's order.

Not confirmed (**U**), with where I looked:

- **(U) the diff.** No shell; section 3 is from reading the file. Run `git diff -U0` to confirm.
- **(U) the SDK's header values and the `/v1/messages` path** are from Security's one offline capture
  (14 §3, SDK 1.7.0); `test_base_url_env_cannot_redirect_and_header_set_is_exact` asserts the header
  names, scheme and host only (read: `tests/test_anthropic_judge.py:331-366`). Stated as such in 2d.
- **(U) "the service makes no other network call"** rests on the code (only `anthropic_judge.py`
  builds a client) and Security's dependency grep (14 §7); no test proves it. Stated in 2d.
- **(U) "no other route reaches the judge"** rests on the code (`app.py`: only `POST /ask` calls
  `service.ask`; Security 14 §9) and `test_health_never_calls_model` for `/health` only. Stated in 1c.
- **(U) what happens to the process when `ANTHROPIC_CUSTOM_HEADERS` is set.** The adapter raises in
  its constructor (`anthropic_judge.py:108-109`), which `main.py` calls at import. I wrote only "the
  adapter's construction fails"; that uvicorn then exits was not checked.
- **(U) deployment facts in ARCHITECTURE.md** (ingress, retention 7/7, probes, image contents) are as
  the Bicep and Dockerfile declare them; nothing is deployed or built yet (stage 17).
- **(U) whether `claude-sonnet-5-5` accepts the request**: no live call yet (stage 17). Stated in 1c.

## 6. Test names cited: all verified to exist

Each name in 1c and 2d was found as `def test_<name>` by a Grep of `tests/` (files
`test_service_{pipeline,limits,api,logging,pages}.py`, `test_anthropic_judge.py`,
`test_infra_static.py`). 23 names in 1c, 24 in 2d (several in both). For the claims that lean on a
test's coverage I read the test body: `test_service_passages_byte_identical_to_retrieve`,
`test_payload_sent_is_format_judge_input_of_same_result`,
`test_not_answerable_is_exactly_no_confident_match`, the four `test_judge_error_shows_nothing_*`,
`test_placeholder_judge_raises_and_pipeline_maps_to_judge_error`,
`test_reason_never_leaves_parser_service`, `test_request_has_no_tools`,
`test_request_body_only_c41_data`, `test_request_model_and_effort_pinned`,
`test_extract_reply_text_blocks_only` (covers `tool_use` and `server_tool_use`),
`test_stop_reason_not_end_turn_is_judge_error`, `test_sdk_errors_map_to_fixed_categories`,
`test_retry_once_only_on_retryable` (two failures stop at two requests), `test_no_retry_on_timeout`,
`test_prompt_hash_mismatch_fails_closed` (no request sent), `test_real_client_config` (`max_retries`
0, timeout 20), `test_real_client_blocked_offline`,
`test_base_url_env_cannot_redirect_and_header_set_is_exact`, `test_custom_headers_env_fails_closed`,
`test_bicep_no_secret_literals`, `test_dockerfile_static` (no `--with-reranker`, `aveto_support
ingest` present).

Not cited because no such test exists: `test_judge_error_shows_nothing` (spec §11's name; it was built
as four suffixed tests, cited instead). The INV-4 and INV-5 names already in the file are existing
words and were not re-checked.

## 7. `docs/ARCHITECTURE.md`

Updated to describe the system as it stands on this branch, not appended history:

- Header: a paragraph for branch `claude/public-ask-the-docs` (not merged, not yet deployed; ADR 0009
  proposed).
- "What exists": the program still has no server; the separate `aveto_service` package does.
- New section **"Public ask service"**: package layout (one table, module → responsibility); the
  request flow in the code's order (kill switch, cross-site refusal, body cap and shape, question,
  per-visitor limits incl. the 30-retrievals-per-hour cap and the spend peek, retrieval, admission
  with reservation, judge, parse, map) with a mermaid diagram; what is stored (in-memory counters and
  the 10-minute, 1,000-entry result store; nothing on disk; stdout holds only abuse and ops lines);
  the C8.3 Azure resources by name from `infra/main.bicep`; known limits stated plainly (CR-3/D1
  counters reset with the replica and the $10 console limit as the only monthly bound, D4, CR-4, the
  kill switch as a new revision, S-A11, CR-8). No cost, latency, cold-start or gate figure: "measured
  at stage 18 and recorded in `runs/public-ask-the-docs/`".
- Model adapter boundaries: the service's `JudgeClient` port, the placeholder that throws by default
  and is used with no key, the real adapter; the stale "FastAPI routes, once an HTTP surface is
  needed" line updated.
- Safety stance: the INV-4 summary names the service as the second place a verdict decides; the INV-5
  summary's "the one exception" gains "on the attended judge step" and a sentence for the service's
  exception; a note that the service's words were added within Charter C5.1/C5.2. The file still
  says the invariants file wins.
- Decisions: ADR 0009 listed as proposed. No new ADR: the decisions this stage records (retrieval
  cap, cross-site refusal, host pin) are security fixes inside ADR 0009's design, and I may write only
  the two files the brief names.

## 8. Hand-off

To 15c (Compliance Reviewer, different model): check sections 1 and 2 against C5.1, C5.2, C5.3 and
rule on R1 to R3. To stage 16 (Release Manager): diff `.agentic/SAFETY_INVARIANTS.md` against
`2919c87` and compare the `-` lines with section 3. To 15b (Tech Writer): README and runbook wording
on the service should follow INV-4/INV-5 as written here; `docs/ARCHITECTURE.md` "Known limits" holds
the plain statement of CR-3/D1.

## Round 2 (depth smoke): the 15c checker's curable rewordings

Source: `15c-words-check.md` sections 2, 3 and 8, items S1, F1, F2, F3. Edited only
`.agentic/SAFETY_INVARIANTS.md`. **S10 and S11b not touched** (Charter stops for the owner): line 182
(`... the one exception on the attended judge step, ...`) and the header/"Of the question and the
docs" words stay exactly as in round 1. Nothing committed; STATE.md not edited.

| Item | Applied | Lines now (file after round 2) | Change |
|---|---|---|---|
| S1 | yes | 40, 42 | Line 40 restored to `  The judge is the agent `aveto-answerability-judge`, pinned to the full model` (`, on the operator's path,` deleted). Line 42: `the judge has exactly` -> `judging has exactly`. The retained agent sentence now has no edited word; item (2) still says the service "does not run that agent and has no deny list or hook". |
| F1 | yes | 100 to 102 | (c) last clause: `and when the payload cannot be built or any other error occurs.` -> `and on any other error once the question is accepted (a question with no searchable words is refused earlier with HTTP 400 and shows nothing).` (checker's wording verbatim; the payload-marker case is inside "any other error once the question is accepted"). |
| F2 | yes | 245, 246 (new) | Added after "...never in the image, the repo or a log.": `The key is the one credential the service sends; "No credentials are sent" above is about the program's two GET downloads.` The retained "No credentials are sent." (line 172) is unchanged. |
| F3 | yes, as the checker worded it | 307 to 309 | Added to the INV-5 service "Not enforced by any test" list, before "and what Anthropic keeps": `the Key Vault wiring (vault, secret, identity, environment variable), read from `infra/main.bicep`;`. The exception's sentence "authenticated by the key the container reads from Key Vault `kv-aveto-ask-gp` (...)" stays: C5.2 names "authenticated by the key the container reads from Key Vault" as the exception's words, and the checker found the facts true against `infra/main.bicep`; only the claim of test enforcement is withdrawn. |

**(U) Source of the line-40 original.** No shell, so `git show main:.agentic/SAFETY_INVARIANTS.md`
was not run. The original wording was taken from the `-` line of `15c-invariants.diff` (index
`15c89e6`, the pre-round-1 file). Confirm with `git diff main -- .agentic/SAFETY_INVARIANTS.md` that
line 40 shows no change.

**(U) No diff result claimed.** Expected round-2 effect against round 1: lines 40, 42, 100 to 102
changed; 245, 246 and 307 to 309 added or rewrapped (line 307 rewrapped to carry the F3 words). Against
the pre-run file, the `-` lines should now be original 42, 43 (the C5.1 sentence), 106 (reflow, no
word removed) and 111 (S10, pending the owner) only; original 40 should no longer appear.
