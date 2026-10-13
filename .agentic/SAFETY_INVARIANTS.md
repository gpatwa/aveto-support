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
  `mcp__*`, and a hook that refuses every tool call; it runs only in the
  operator's own Claude Code session, and nothing in the program calls it.
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
  a question, passage or any user text anywhere.** `retrieve`, `eval` (with or
  without `--verdicts`), `judge-input` and `judge-apply` make no network call,
  start no process and call no generative model (the only models they run are
  the local embedding model and, with `--ranking file-rerank-v1`, the local
  reranker); the default test suite makes no network calls.
  **The operator's session is the one exception, and it is not the program.**
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
  platform, shell, scratchpad path, model ID, date and organisation ID). The
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
