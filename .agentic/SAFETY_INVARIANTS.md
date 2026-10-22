# Safety Invariants

> **PARTIAL — seeded by hand from the owner's own statements in `README.md`,
> nothing inferred.** The Architect + Security stages still own this file and
> must extend it from the PRD/UX before any delivery stage runs. A missing
> invariant is not a permission.
>
> Each invariant: one line, testable, stated as what MUST hold across releases.

## Posting

- **INV-1** — Nothing is written to GitHub (issue comment, Discussion reply,
  or any other write) unless a person approved that specific reply first, and
  the approval is recorded. There is no code path that posts without one.
  *(README: "It never posts on its own: every reply is approved by a person
  first.")*

## Grounding

- **INV-2** — Every answer is drawn from Aveto's own documentation, and every
  drafted reply names the passages it came from.
  *(README: answers "from Aveto's own documentation"; step 3 drafts "a grounded
  reply".)*
- **INV-3** — A draft is checked against its sources by a different model from
  the one that wrote it; a claim the sources do not support is removed or the
  question is escalated — never posted as-is.
  *(README, step 4. Applies once drafting exists.)*

## Retrieval and network

- **INV-4** — Retrieval returns only verbatim passages from the configured
  source at its pinned commit, each with path, heading and line range; it does
  not abstain (a question the docs do not answer still returns its top files,
  and `eval` reports unanswerable questions as a diagnostic). It never returns
  generated or reworded text. **A model may be used only to rank passages, to
  decide confidence, and, for the answerability judge alone, to judge whether
  the passages `retrieve` would show answer the question, by returning only a
  verdict. No model ever produces, selects among, or alters the text shown:
  the verdict decides only whether `retrieve`'s whole output is printed.**
  The judge is the agent `aveto-answerability-judge`, pinned to the full model
  ID `claude-sonnet-5-5`, with no `tools` entry, a deny list ending in
  `mcp__*`, and a hook that refuses every tool call; judging has exactly
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
  The program keeps only the verdict token, read from the last non-empty line
  of the judge's reply; it never prints or stores the reason or any earlier
  line. `judge-apply` prints exactly one of:
  (a) on `ANSWERABLE`, exit 0: the output `retrieve` prints for the same
  question at the default ranking, unchanged, followed by the one line
  `Deciding signal: answerability judge verdict ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427)`;
  (b) on `NOT_ANSWERABLE`, exit 0: exactly these two lines and nothing else
  (no passage, path or reason):
  `no confident match`
  `Deciding signal: answerability judge verdict NOT_ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427)`;
  (c) on any reply it cannot use (missing, unreadable, too long, not UTF-8,
  empty, containing a control or format character, malformed, with a wrong
  block id or more than one verdict token, or bound to a different input), or
  when a transport file cannot be deleted: `judge error` on stdout, one fixed
  category on stderr, exit 4;
  (d) on an input error (a bad question or a missing index), exit 2: nothing
  on stdout.
  It never prints passages on (b), (c) or (d), and never passes `retrieve`'s
  output through without a verdict. `retrieve`, and `eval` without
  `--verdicts`, never print a verdict, a deciding signal or
  `no confident match`. (The operator's Claude Code session keeps its own
  transcript, which holds the judge's full reply; that is the session's
  record, not the program's.)
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
  configured), and on any other error once the question is accepted (a
  question with no searchable words is refused earlier with HTTP 400 and
  shows nothing). The service names no cause: it writes no stderr line, and its log
  lines carry only fixed codes, never the cause.
  The service shows passages only on (a); the page shows the same passages as
  the JSON and no deciding-signal line.
  (The service holds the reply in memory only to check its length and parse
  it; it never logs, stores or returns it, and of the reply it keeps only the
  verdict token. What Anthropic keeps of the request and the reply is kept under
  Anthropic's terms, not verified by an agent; that is the provider's record,
  not the service's.)
  *(Enforced by `test_result_invariant_enforced`,
  `test_retrieved_text_is_verbatim_slice_of_file`,
  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
  `test_reranked_hits_are_verbatim_passages`,
  `test_reranked_result_invariant_enforced` and
  `test_reranker_returns_only_scores`; for the judge, by
  `test_judge_input_matches_retrieve_selection`,
  `test_judge_input_full_text_not_excerpt`, `test_parse_verdict_table`,
  `test_verdict_carries_only_the_token`, `test_reason_never_leaves_parser`,
  `test_apply_answerable_is_retrieve_plus_signal`,
  `test_apply_not_answerable_exact`, `test_apply_judge_error_shows_nothing`,
  `test_apply_missing_verdict_file`, `test_apply_hash_mismatch`,
  `test_apply_after_reingest_is_refused`,
  `test_apply_outside_transport_dir_untouched`,
  `test_apply_deletion_failure_is_judge_error`,
  `test_apply_deletes_transport_files_every_path`,
  `test_unjudged_outputs_never_look_judged`,
  `test_judge_modules_import_allow_list`, `test_program_offline_no_model`,
  `test_agent_definition`, `test_deny_hook_refuses_every_input` and
  `test_prompt_file_hash_pinned`. Not shown by any test: that Claude Code
  runs the hook for the judge (the hook test runs the command only), and that
  the judge never calls a tool in a live run; the latter is checked per run by
  the eval audit, which voids a batch on any tool use.)*
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

- **INV-5** — The program's (`python -m aveto_support`) network egress is
  limited to two kinds of read-only HTTPS GET download, both made only by
  `ingest`:
  (a) the archive of the configured GitHub repo at a full 40-hex commit, with
  redirects only to `github.com` / `codeload.github.com`; and
  (b) the pinned files of exactly two local models — the configured embedding
  model (`docs-source.toml`) and the reranker model pinned in
  `aveto_support/rerank.py` — each requested from `huggingface.co` at its own
  full 40-hex revision, with redirects only to hosts under `hf.co` (for example
  `us.aws.cdn.hf.co`).
  Of the two models, the default path fetches only the embedding model's files:
  **`ingest`** fetches the reranker's files only when run with **`--with-reranker`**.
  Every model file is checked against its committed sha256 **before it is
  used**. On a mismatch the file is deleted and ingest fails. Trust rests on the
  hash, never on the host. No credentials are sent. **The program never sends
  a question, passage or any user text anywhere.** (The public service,
  package `aveto_service`, is not the program, although it imports the
  program's code; its own exception is stated below, after the operator's
  session.)
  `retrieve`, `eval` (with or
  without `--verdicts`), `judge-input` and `judge-apply` make no network call,
  start no process and call no generative model (the only models they run are
  the local embedding model and, with `--ranking file-rerank-v1`, the local
  reranker); the default test suite makes no network calls.
  **The operator's session is one of two exceptions, the other being the service, and it is not the program.**
  When the operator runs the judge step (`/aveto-judge`, which runs only when
  the operator types it), the operator's own Claude Code session sends data to
  that session's model provider (Anthropic, approved as data processor in
  `runs/docs-answerability-2/APPROVAL_RECORD-3.md`): the question; the payload
  `judge-input` prints (the passages `retrieve` would show, with their file
  paths, headings and line ranges), which the operator can inspect first by
  running `judge-input`; the judge's fixed system prompt; and the session
  context the harness attaches to the judge. As measured on 2026-10-12
  (`runs/docs-answerability-2/01-measurement.md`), that context includes the
  project instruction files `CLAUDE.md` and `AGENTS.md` as read from the main
  checkout's path (a different checkout sends different text); the user's
  email address; the git branch, git user name, working-tree status and five
  most recent commit subjects; and environment lines (working directory,
  platform, OS version, shell, scratchpad path, whether the folder is a git
  repository or a worktree, model ID, date and organisation ID). The
  question, the payload and the judge's reply also enter the session's main
  conversation, which sends to the same provider whatever that session
  carries. The list is as measured and is not complete: about 2.7k of the
  measured first request's 14.2k tokens were not itemised, no setting that
  removes the session context was found, and the harness may change what it
  attaches; whatever the operator's session carries goes with it. The list is
  re-measured at stage 4 of docs-answerability-2, after the deny-list
  decision; the tool schemas the harness offers the judge are not part of it.
  The eval-only skill `/aveto-judge-seen` sends the same kinds of data in the
  same way, only for a question its key file lists by run id, plus a line
  naming the skill's local directory path. The program sends none of this
  anywhere, and the judge cannot use a tool to send it elsewhere (its deny
  list, and a hook that refuses every tool call); what the harness sends for
  its own purposes is outside this invariant and was not measured.
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
  `runs/public-ask-the-docs/CHARTER-v2.md`: the fixed judge prompt
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
  The key is the one credential the service sends; "No credentials are sent"
  above is about the program's two GET downloads.
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
  *(Enforced by `test_redirect_to_other_host_refused`,
  `test_hf_redirect_outside_hf_co_refused`, `test_short_sha_rejected`,
  `test_model_revision_must_be_40_hex`,
  `test_model_hash_mismatch_rejected_and_deleted`,
  `test_cached_file_rehashed_before_use`,
  `test_retrieve_is_offline_with_cached_model`,
  `test_reranker_revision_must_be_40_hex`,
  `test_reranker_hash_mismatch_rejected_and_deleted`,
  `test_reranker_cached_file_rehashed_before_use`,
  `test_reranker_redirect_outside_hf_co_refused`,
  `test_retrieve_is_offline_with_cached_reranker`,
  `test_default_ingest_fetches_no_reranker`,
  `test_default_ingest_makes_no_reranker_request`,
  `test_ingest_with_reranker_fetches_and_rehashes`,
  `test_reranker_absent_fails_closed_without_download`, and the autouse network
  block; for the judge step, by `test_program_offline_no_model`,
  `test_judge_modules_import_allow_list`, `test_judge_input_layout_exact`,
  `test_judge_input_has_no_scores_urls_labels`, `test_command_definition`,
  `test_agent_definition`, `test_deny_hook_refuses_every_input`,
  `test_refuses_bad_ids`, `test_refuses_id_not_in_key`,
  `test_refuses_wrong_argument_count` and `test_ids_match_key`. Not enforced
  by any test: the session-context list (measured live, and re-measured live
  at stage 4); that the operator's session sends it only to its model
  provider; what the session's main conversation does with the payload and
  the reply (it acts under the session's own permission prompts); and that
  Claude Code runs the judge's hook.)*
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
  `ingest` ran and matched (the image build log); the Key Vault wiring
  (vault, secret, identity, environment variable), read from
  `infra/main.bicep`; and what Anthropic keeps.)*
