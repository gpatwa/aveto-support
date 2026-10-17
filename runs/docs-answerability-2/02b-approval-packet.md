# 02b — Rule 4 approval packet: INV-4 and INV-5 exact words (docs-answerability-2)

> Owner: Software Architect Agent, Architecture pass 2, depth standard, 2026-10-12.
> **This file is a request, not an approval.** Nothing here is approved, applied or assumed. `.agentic/SAFETY_INVARIANTS.md` is **not edited** by this pass. The owner approves the exact words, in their own words, in the driving session (rule 4, `HUMAN_APPROVAL_RULES.md` section 4). The Orchestrator then pastes the approved blocks verbatim and records the approval as the next APPROVAL_RECORD.
> Sources: `intent.md` (Done means, INV-4/INV-5 lines), `02-tech-spec.md` sections 5, 9 and 14, `01-scope.md` section 4, `01-measurement.md` (context report), SUPPORT_REPLIES Reply 1 D3, APPROVAL_RECORD-1 to 4, the current `.agentic/SAFETY_INVARIANTS.md`. Checked against: `aveto_support/judge.py`, `aveto_support/__main__.py` (judge-input, judge-apply), `tests/conftest.py` (the network block), `tests/test_judge.py`, `tests/test_judge_artefacts.py`, `tests/test_judge_seen_skill.py` (test names), `.claude/skills/aveto-judge/SKILL.md`, `.claude/skills/aveto-judge-seen/SKILL.md` and `seen_payload.py`. I ran nothing; every "true of the code" below is from reading.

## 0. What the owner is asked, in one message

1. **What:** replace the INV-4 block and the INV-5 block in `.agentic/SAFETY_INVARIANTS.md` with the two blocks in sections 1 and 2, exactly as written (the diff is section 3).
2. **Why:** rule 4 (a safety control changes). The current INV-4 ("does not abstain"; "a model may be used only to rank passages and to decide confidence") and INV-5 ("No question, passage or user text ever leaves the machine") are contradicted by the code already on this branch (commit `5eb2a8a`: `judge-apply` prints `no confident match`; the operator's session sends the payload to the model provider). The intent requires approved words **before any code that sends data runs**; no judge spawn beyond stage 1's two may run until then (tech spec section 9), including the stage 4 smoke.
3. **If denied:** the current text stays. No spawn runs: no smoke, no stage 5, no stage 7. The slice cannot pass "Done means" and stops, or the owner sends back edits and a revised packet comes back to the owner.
4. **Smallest request:** two blocks, one decision each. The owner may approve one and not the other; both are needed before the smoke.
5. **Separate questions, not part of this approval** (section 6): the rule 6 scope question (`02c-rule6-question.md`), the reading of "exactly" (A9), D1, tier and depth.

## 1. Proposed INV-4 (paste-ready)

Replaces the whole current INV-4 bullet (lines 31 to 42 of the current file), including its enforcement paragraph.

```markdown
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
```

### 1.1 INV-4: each claim, the code that makes it true, the test that enforces it

| Claim in the words | True of the code? (read) | Enforcing test | State |
|---|---|---|---|
| Retrieval: verbatim, path/heading/lines, never abstains, never generated | Unchanged on this branch (`search.retrieve` docstring "Never abstains. No text is generated."); this slice touches no retrieval file | the six existing retrieval tests (carried over; all six names found in `tests/`) | exists |
| Model may only rank, decide confidence, or (judge) return a verdict | The program has no model client; the judge's only effect on output is via `parse_verdict` returning a `Verdict(token)` (`judge.py` 144-167) | `test_verdict_carries_only_the_token`, `test_judge_modules_import_allow_list` | exists |
| Judges "the passages `retrieve` would show" | `retrieve_for_judge` calls `retrieve` with the default ranking; `format_judge_input` prints every shown file and passage in full | `test_judge_input_matches_retrieve_selection`, `test_judge_input_full_text_not_excerpt` | exists |
| Never produces, selects among, or alters text shown; verdict decides only whether the whole output is printed | `render_applied` (`judge.py` 177-183) returns `format_result(result, index)` unchanged or the fixed two lines | `test_apply_answerable_is_retrieve_plus_signal` (asserts `out == retrieve.out + signal`), `test_apply_not_answerable_exact` | exists |
| Pinned `claude-sonnet-5-5`, no `tools` entry, deny list ending `mcp__*`, refuse-all hook | Agent frontmatter as pinned by the test's `FRONTMATTER` (byte for byte) | `test_agent_definition`, `test_deny_hook_refuses_every_input` | exists; **hook live-run not tested** (stated in the words) |
| Runs only in the operator's session; nothing in the program calls it | No model client in `__main__`, `judge`, `judge_eval` (imports allow-listed); no process, no socket during the five commands | `test_judge_modules_import_allow_list`, `test_program_offline_no_model` | exists (allow-list covers the three judge modules only, which is what the sentence needs) |
| Keeps only the token from the last non-empty line; never prints or stores reason or earlier lines | `parse_verdict` reads `non_empty[-1]`; returns `Verdict(token)` only | `test_parse_verdict_table`, `test_verdict_carries_only_the_token`, `test_reason_never_leaves_parser` (also scans every file in the work dir) | exists |
| (a) ANSWERABLE output, exact signal line | `render_applied` + `signal_line`; `PROMPT_ID`, `PROMPT_SHA256` constants (`judge.py` 23-24) | `test_apply_answerable_is_retrieve_plus_signal`, `test_prompt_file_hash_pinned` | exists |
| (b) NOT_ANSWERABLE: exactly two lines | `render_applied` line 180 | `test_apply_not_answerable_exact` (asserts the exact two lines; checks no path or passage word leaks) | exists |
| (c) unusable reply: `judge error`, fixed category, exit 4 | `_judge_apply` (`__main__.py` 185-210); the eleven categories (`judge.py` 31-41) | `test_apply_judge_error_shows_nothing` (7 categories in 9 cases), `test_apply_missing_verdict_file` (unreadable), `test_apply_hash_mismatch`, `test_apply_after_reingest_is_refused` (different input), `test_apply_outside_transport_dir_untouched` (outside), `test_apply_deletion_failure_is_judge_error` (not deleted) | exists; all 11 categories covered across these |
| (d) input error: exit 2, nothing on stdout | exceptions re-raised after deletion; the CLI maps them to exit 2 | `test_apply_deletes_transport_files_every_path` (asserts `(2, "")` for a bad question and a missing index) | exists |
| `retrieve` and `eval` without `--verdicts` never look judged | no judge code on those paths | `test_unjudged_outputs_never_look_judged` | exists |
| Session transcript holds the full reply | Harness behaviour, outside the program | none | **no test** (stated as a fact about the session, not a guarantee) |

## 2. Proposed INV-5 (paste-ready)

Replaces the whole current INV-5 bullet (lines 44 to 75 of the current file), including its enforcement paragraph. Points (a) and (b), the model sentence, the hash sentences and the 22 existing test names are carried over **unchanged**.

```markdown
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
```

### 2.1 INV-5: each claim, the code that makes it true, the test that enforces it

| Claim in the words | True of the code? (read) | Enforcing test | State |
|---|---|---|---|
| (a), (b), model fetch, hashes, no credentials | Unchanged text and code (this slice touches no ingest file) | the 16 existing ingest/rerank tests, the autouse network block | exists (all 16 names, and the 6 INV-4 ones, found in `tests/`: 22 matches) |
| The program never sends question, passage or user text | No socket use outside `ingest`; the judge modules import only stdlib + `aveto_support` | `test_program_offline_no_model`, the autouse network block (`conftest.py` 22-34 blocks `connect`, `create_connection`, `getaddrinfo`), `test_judge_modules_import_allow_list` | exists. Stage 4 adds one in-body assertion to `test_program_offline_no_model` that the guard is active (tech spec T6, A11), so removing the fixture fails the test. **The name does not change.** |
| The five commands make no network call, start no process | `test_program_offline_no_model` runs `retrieve`, `eval`, `eval --verdicts`, `judge-input`, `judge-apply` with `subprocess.Popen` and the `os` spawn functions replaced by a failing stub, under the socket block | `test_program_offline_no_model` | exists |
| "call no generative model; the only models they run are the local embedder and, with `--ranking file-rerank-v1`, the reranker" | `retrieve` runs the local embedder (`search.retrieve` docstring); the judge path builds `Searcher(index, embedder)` without a reranker | `test_retrieve_is_offline_with_cached_model`, `test_retrieve_is_offline_with_cached_reranker`, `test_judge_modules_import_allow_list` | exists. The intent's "call no model" is **not** true as written (the embedder is a model); the words say "no generative model". |
| `/aveto-judge` runs only when the operator types it | `disable-model-invocation: true` in the skill's frontmatter | `test_command_definition` (pins the frontmatter byte for byte) | exists; the harness honouring the flag is harness behaviour |
| What the payload contains (question, paths, headings, line ranges, passage text; no scores, URLs, commit, repo) | `format_judge_input` (`judge.py` 112-134) | `test_judge_input_layout_exact`, `test_judge_input_has_no_scores_urls_labels` | exists |
| Inspectable first via `judge-input` | `judge-input` prints the payload to stdout and its sha256 to stderr; `judge-apply` refuses a reply bound to another payload | `test_judge_input_deterministic_and_hash_on_stderr` (not named in the words), `test_apply_hash_mismatch` (named under INV-4) | exists |
| Session-context list, as measured | `01-measurement.md` context report (two spawns), Reply 1 D3 | none | **no test** (stated in the words). Re-measured live at stage 4 from the smoke spawn's transcript (tech spec 9.5, section 10 step 4) |
| Question, payload and reply enter the main conversation | `/aveto-judge` steps 2 to 4: the main session runs `judge-input`, passes its stdout to the judge, receives the reply and writes it; the forked `/aveto-judge-seen` returns its result to the invoking conversation | none | **no test**; true by the skill text. **New relative to pass 1 section 9**, which listed only what the judge receives |
| The eval-only skill sends only a question its key lists, plus the base-dir line | `seen_payload.prepare` refuses an id not in `key/key.toml` or without a batch line, exit 2, so no judge starts; the base-dir line is the harness's (R1) | `test_refuses_bad_ids`, `test_refuses_id_not_in_key`, `test_refuses_wrong_argument_count`, `test_ids_match_key` | exists. **`test_ids_match_key` fails on the tree today** (it asserts 93 rows; the key has 2) and is rebuilt at stage 4 (tech spec S1). It is named because after stage 4 it checks that every key row is a real eval question |
| Judge cannot use a tool | No `tools` entry; deny list ending `mcp__*`; hook `exit 2` on every input | `test_agent_definition`, `test_deny_hook_refuses_every_input` | exists for the files and the command; **live: not a pytest test**. Stage 1: 0 tool calls in 2 spawns (no call was attempted, so the hook was not exercised). Stages 5 and 7: `judge_run record` voids a batch on any `tool_use` (to be written at stage 4, tech spec T3) |
| "goes to the model provider ... and nowhere else" (intent) | The program: enforced above. The judge: no usable tool. The session's main conversation: has the operator's normal tools under permission prompts. The harness's own traffic: not measured | partial | **The intent's "nowhere else" cannot be backed for the whole session.** The words therefore say: the program sends none of it; the judge cannot use a tool; the harness's own traffic is outside the invariant and not measured |

## 3. Diff against the current `.agentic/SAFETY_INVARIANTS.md`

Against the file as read on 2026-10-12 at `e6b7c78` (lines 31 to 75). The rest of the file (header, INV-1 to INV-3, section headings) is unchanged. Line wrapping in the `+` lines is as in sections 1 and 2; the blocks in sections 1 and 2 are what gets pasted.

### 3.1 INV-4

```diff
-- **INV-4** — Retrieval returns only verbatim passages from the configured
-  source at its pinned commit, each with path, heading and line range; it does
-  not abstain (a question the docs do not answer still returns its top files,
-  and `eval` reports unanswerable questions as a diagnostic). It never returns
-  generated or reworded text. **A model may be used only to rank passages and to decide confidence. It
-  never produces, selects fragments of, or alters the text returned.**
-  *(Enforced by `test_result_invariant_enforced`,
-  `test_retrieved_text_is_verbatim_slice_of_file`,
-  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
-  `test_reranked_hits_are_verbatim_passages`,
-  `test_reranked_result_invariant_enforced` and
-  `test_reranker_returns_only_scores`.)*
+- **INV-4** — Retrieval returns only verbatim passages from the configured
+  source at its pinned commit, each with path, heading and line range; it does
+  not abstain (a question the docs do not answer still returns its top files,
+  and `eval` reports unanswerable questions as a diagnostic). It never returns
+  generated or reworded text. **A model may be used only to rank passages, to
+  decide confidence, and, for the answerability judge alone, to judge whether
+  the passages `retrieve` would show answer the question, by returning only a
+  verdict. No model ever produces, selects among, or alters the text shown:
+  the verdict decides only whether `retrieve`'s whole output is printed.**
+  The judge is the agent `aveto-answerability-judge`, pinned to the full model
+  ID `claude-sonnet-5-5`, with no `tools` entry, a deny list ending in
+  `mcp__*`, and a hook that refuses every tool call; it runs only in the
+  operator's own Claude Code session, and nothing in the program calls it.
+  The program keeps only the verdict token, read from the last non-empty line
+  of the judge's reply; it never prints or stores the reason or any earlier
+  line. `judge-apply` prints exactly one of:
+  (a) on `ANSWERABLE`, exit 0: the output `retrieve` prints for the same
+  question at the default ranking, unchanged, followed by the one line
+  `Deciding signal: answerability judge verdict ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427)`;
+  (b) on `NOT_ANSWERABLE`, exit 0: exactly these two lines and nothing else
+  (no passage, path or reason):
+  `no confident match`
+  `Deciding signal: answerability judge verdict NOT_ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427)`;
+  (c) on any reply it cannot use (missing, unreadable, too long, not UTF-8,
+  empty, containing a control or format character, malformed, with a wrong
+  block id or more than one verdict token, or bound to a different input), or
+  when a transport file cannot be deleted: `judge error` on stdout, one fixed
+  category on stderr, exit 4;
+  (d) on an input error (a bad question or a missing index), exit 2: nothing
+  on stdout.
+  It never prints passages on (b), (c) or (d), and never passes `retrieve`'s
+  output through without a verdict. `retrieve`, and `eval` without
+  `--verdicts`, never print a verdict, a deciding signal or
+  `no confident match`. (The operator's Claude Code session keeps its own
+  transcript, which holds the judge's full reply; that is the session's
+  record, not the program's.)
+  *(Enforced by `test_result_invariant_enforced`,
+  `test_retrieved_text_is_verbatim_slice_of_file`,
+  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
+  `test_reranked_hits_are_verbatim_passages`,
+  `test_reranked_result_invariant_enforced` and
+  `test_reranker_returns_only_scores`; for the judge, by
+  `test_judge_input_matches_retrieve_selection`,
+  `test_judge_input_full_text_not_excerpt`, `test_parse_verdict_table`,
+  `test_verdict_carries_only_the_token`, `test_reason_never_leaves_parser`,
+  `test_apply_answerable_is_retrieve_plus_signal`,
+  `test_apply_not_answerable_exact`, `test_apply_judge_error_shows_nothing`,
+  `test_apply_missing_verdict_file`, `test_apply_hash_mismatch`,
+  `test_apply_after_reingest_is_refused`,
+  `test_apply_outside_transport_dir_untouched`,
+  `test_apply_deletion_failure_is_judge_error`,
+  `test_apply_deletes_transport_files_every_path`,
+  `test_unjudged_outputs_never_look_judged`,
+  `test_judge_modules_import_allow_list`, `test_program_offline_no_model`,
+  `test_agent_definition`, `test_deny_hook_refuses_every_input` and
+  `test_prompt_file_hash_pinned`. Not shown by any test: that Claude Code
+  runs the hook for the judge (the hook test runs the command only), and that
+  the judge never calls a tool in a live run; the latter is checked per run by
+  the eval audit, which voids a batch on any tool use.)*
```

What changed in substance: the "only rank and decide confidence" sentence gains the verdict permission; "selects fragments of ... the text returned" becomes "selects among ... the text shown", with the verdict's whole-output effect stated; the judge, the parser and `judge-apply`'s four outcomes are new; 20 judge test names are added. Retrieval's own sentence ("does not abstain") is unchanged and still true of `retrieve`.

### 3.2 INV-5

Only the changed and added lines are shown with `-`/`+`; unchanged lines carry a leading space.

```diff
-- **INV-5** — The product's network egress is limited to two kinds of
-  read-only HTTPS GET download, both made only by `ingest`:
+- **INV-5** — The program's (`python -m aveto_support`) network egress is
+  limited to two kinds of read-only HTTPS GET download, both made only by
+  `ingest`:
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
-  hash, never on the host. No credentials are sent. **No question, passage or
-  user text ever leaves the machine.** `retrieve`, `eval` and the default test
-  suite make no network calls.
+  hash, never on the host. No credentials are sent. **The program never sends
+  a question, passage or any user text anywhere.** `retrieve`, `eval` (with or
+  without `--verdicts`), `judge-input` and `judge-apply` make no network call,
+  start no process and call no generative model (the only models they run are
+  the local embedding model and, with `--ranking file-rerank-v1`, the local
+  reranker); the default test suite makes no network calls.
+  **The operator's session is the one exception, and it is not the program.**
+  When the operator runs the judge step (`/aveto-judge`, which runs only when
+  the operator types it), the operator's own Claude Code session sends data to
+  that session's model provider (Anthropic, approved as data processor in
+  `runs/docs-answerability-2/APPROVAL_RECORD-3.md`): the question; the payload
+  `judge-input` prints (the passages `retrieve` would show, with their file
+  paths, headings and line ranges), which the operator can inspect first by
+  running `judge-input`; the judge's fixed system prompt; and the session
+  context the harness attaches to the judge. As measured on 2026-10-12
+  (`runs/docs-answerability-2/01-measurement.md`), that context includes the
+  project instruction files `CLAUDE.md` and `AGENTS.md` as read from the main
+  checkout's path (a different checkout sends different text); the user's
+  email address; the git branch, git user name, working-tree status and five
+  most recent commit subjects; and environment lines (working directory,
+  platform, shell, scratchpad path, model ID, date and organisation ID). The
+  question, the payload and the judge's reply also enter the session's main
+  conversation, which sends to the same provider whatever that session
+  carries. The list is as measured and is not complete: about 2.7k of the
+  measured first request's 14.2k tokens were not itemised, no setting that
+  removes the session context was found, and the harness may change what it
+  attaches; whatever the operator's session carries goes with it. The list is
+  re-measured at stage 4 of docs-answerability-2, after the deny-list
+  decision; the tool schemas the harness offers the judge are not part of it.
+  The eval-only skill `/aveto-judge-seen` sends the same kinds of data in the
+  same way, only for a question its key file lists by run id, plus a line
+  naming the skill's local directory path. The program sends none of this
+  anywhere, and the judge cannot use a tool to send it elsewhere (its deny
+  list, and a hook that refuses every tool call); what the harness sends for
+  its own purposes is outside this invariant and was not measured.
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
-  block.)*
+  block; for the judge step, by `test_program_offline_no_model`,
+  `test_judge_modules_import_allow_list`, `test_judge_input_layout_exact`,
+  `test_judge_input_has_no_scores_urls_labels`, `test_command_definition`,
+  `test_agent_definition`, `test_deny_hook_refuses_every_input`,
+  `test_refuses_bad_ids`, `test_refuses_id_not_in_key`,
+  `test_refuses_wrong_argument_count` and `test_ids_match_key`. Not enforced
+  by any test: the session-context list (measured live, and re-measured live
+  at stage 4); that the operator's session sends it only to its model
+  provider; what the session's main conversation does with the payload and
+  the reply (it acts under the session's own permission prompts); and that
+  Claude Code runs the judge's hook.)*
```

## 4. Where the words depart from the intent's phrasing, and why (flags)

Each item is a sentence the intent or pass 1 section 9 asks for that I **could not back as phrased** against the code, with what the words say instead. The owner decides whether the replacement is acceptable; none of these is a design change.

| # | Intent / pass 1 phrasing | Problem found by reading the code | What the words say |
|---|---|---|---|
| F1 | "the program makes no network call" (intent, INV-5) | False as written: `ingest` makes the two approved GETs | Keeps the two GETs; says the five judge-relevant commands make no network call and the program never sends question, passage or user text |
| F2 | "call no model" (intent, Done means) | False as written: `retrieve` runs the local embedding model (and the reranker with `--ranking file-rerank-v1`) | "call no generative model", naming the two local models |
| F3 | "tools omitted" (intent) / "no tools" | True only of the agent file's keys. The judge **is offered 7 harness tools** (measured, `01-measurement.md`) that the deny list does not name; only the hook refuses them | "no `tools` entry, a deny list ending in `mcp__*`, and a hook that refuses every tool call". Stays true whether or not D1 is applied |
| F4 | The hook as an enforced layer | `test_deny_hook_refuses_every_input` runs the hook **command** only; its own docstring says it does not show Claude Code runs it. Stage 1 exercised no call. The `/aveto-judge` skill notes it runs only in a trusted workspace | The words say so, in the "not shown by any test" sentence |
| F5 | "and nowhere else" (intent, INV-5) | Backable for the program (tests) and the judge (no usable tool). **Not backable for the operator's session as a whole**: its main conversation has the operator's own tools under permission prompts, and the harness's own traffic (whatever it sends besides model requests) was not measured and is not this repo's to control | Program: nowhere. Judge: cannot use a tool. Session: sends to its model provider; harness's own traffic is outside the invariant and not measured |
| F6 | Pass 1 section 9 lists only what **the judge** receives | Reading `/aveto-judge` steps 2 to 4: the **main conversation** also receives the payload (it runs `judge-input` and passes the stdout on) and the judge's reply (the Agent result), and resends them with everything else it carries. The forked `/aveto-judge-seen` likewise returns the reply to the invoking conversation | Added one sentence: payload and reply also enter the main conversation. This also bears on the rule 6 question (02c) |
| F7 | "the reason ... never shown or stored" | True of the program (`test_reason_never_leaves_parser` scans output and every file in the work dir). **Not true of the session**: Claude Code's transcript in `~/.claude/projects/` holds the full reply. And the eval run records keep a reply's full text for rows that differ from the key (A1, `diffs.md`, eval-only) | INV-4 says "the program ... never prints or stores"; adds the transcript parenthesis. The eval run records are not mentioned in the words (they are not the program's output); listed here so the owner sees it |
| F8 | Pass 1 section 9 (d) lists "OS version" | Not in `01-measurement.md`'s item notes (working directory, platform, shell, scratchpad path, model id, date, org uuid) | Left out of the measured list; the "not complete" sentence and the stage 4 re-measure cover it. If the re-measure itemises it, that is a new item: the Orchestrator stops and brings it to the owner (tech spec 9.5) |
| F9 | `judge-apply` on ANSWERABLE = "`retrieve`'s output unchanged" | True for the **default ranking only**: the judge path builds its searcher without a reranker, and the test compares with plain `retrieve` | "the output `retrieve` prints for the same question at the default ranking" |
| F10 | A9: "exactly `no confident match`" | Code prints two lines (A9, option A, adopted under SI-1) | The words state both lines in full, so approving the words approves the two-line output. If the owner reads "exactly" strictly, **do not approve INV-4 as drafted**; option B (drop the signal line on NOT_ANSWERABLE) is a stage 4 change to `judge.py` and its test, and INV-4 (b) would be redrafted |
| F11 | Prompt hash in the words | Writing the full sha256 into INV-4 means any change to `prompts/answerability-judge-v1.txt` makes INV-4 false until the owner approves new words | Kept on purpose: the prompt is the judge's safety text and is already hash-pinned by two tests. The owner may prefer `<the sha256 pinned in judge.PROMPT_SHA256>`; that reads less exactly |
| F12 | "attended only" | Enforced for `/aveto-judge` (`disable-model-invocation: true`, pinned). **Not** for the agent itself: any model in a Claude Code session in this repo could spawn `aveto-answerability-judge` through the Agent tool (its description says "Never delegate to it otherwise", an instruction, not a control). `/aveto-judge-seen` is model-invocable by design (the test asserts it lacks the flag), limited to key-listed ids | The words claim "runs only when the operator types it" for `/aveto-judge` only, and "runs only in the operator's own Claude Code session" for the judge, which holds either way. The data still goes only to that session's provider. Named for Security (adversarial) |
| F13 | `tools/judge_run.py` offline (pass 1 T5) | The file does not exist until stage 4 | **Not in the words**: approved text should not name an artefact that does not yet exist. Its offline property is pinned by T5 at stage 4. The owner may ask to add it |

## 5. What stage 4 must keep true, and what would make the words false

The words are written to be true of the tree at `e6b7c78` **and** of what stage 4 builds (tech spec 12.2). Stage 4 changes no `aveto_support/` file.

- **`test_ids_match_key`** fails today (asserts 93; the key has 2 rows). It is named in INV-5 because stage 4 rebuilds it (S1). If stage 4 renames it, the INV-5 text is wrong and needs the owner's word.
- **`test_program_offline_no_model`** gains one in-body assertion at stage 4 (A11, T6). Its name must not change.
- **D1.** Neither block depends on the outcome. "No `tools` entry, a deny list ending in `mcp__*`" stays true if the seven names are inserted before `mcp__*`. "The tool schemas ... are not part of it" stays true whether 7 or 0 are offered.
- **Re-measure at stage 4.** If the smoke spawn's transcript shows a session-context item not named in INV-5 (for example OS version, F8), or the main checkout's instruction files are not what is attached, the Orchestrator stops before stage 5 and brings it to the owner. The approved words are not edited by anyone else (tech spec 9.5).
- **A9 / F10.** If the owner vetoes A9, INV-4 (b) is redrafted and re-approved before the smoke.
- **The seen-check move (A6).** INV-5 says "its key file", not a path, so moving the directory to `runs/docs-answerability-2/judge-check/` does not change the words.
- **The prompt.** Unchanged in this slice; any change makes INV-4 (a) and (b) false (F11).

## 6. What this packet does NOT approve

Approving sections 1 and 2 approves **those words only**. It does not approve, imply or pre-empt:

1. **D1**, the seven-tool deny-list diff. Stage 4 brings an exact diff (`D1-diff.md`) to the owner separately (rule 4 / 5 territory, STANDING_INSTRUCTIONS "Not adopted").
2. **The rule 6 question** about the session context: whether the email, git commit subjects, project instruction files, environment lines and (F6) the main conversation's copy of the payload and reply are within APPROVAL_RECORD-3. Asked separately in `02c-rule6-question.md`. **If the owner answers that this is an expansion needing a new rule 6 approval, that approval is needed before the smoke, and INV-5 may need redrafting.**
3. **The release tier.** Tier 2 versus the tier 3 trigger is the Release Manager's to justify at the gate (`01-scope.md` section 3); the intent says tier 2.
4. **Any depth.** Security stays adversarial (bound by the intent and APPROVAL_RECORD-1). Nothing here lowers it.
5. **The A9 reading of "exactly"** as a design default: it is adopted under SI-1 and stated in INV-4; the owner's approval of the words is also the moment to veto it (F10). Not a separate approval.
6. **Any spawn.** Approval of the words is a precondition for the smoke and stage 5, not a go-ahead for them. The fresh-load session request is the Orchestrator's, separately.
7. **Budget, push, merge, deploy**, and any post-merge revert of INV text.
8. **ADR 0008** stays Proposed. It is not accepted by approving these words.

## 7. How the approved words are applied (for the Orchestrator)

1. The owner approves (or edits) in their own words in the driving session. The Orchestrator records it as the next APPROVAL_RECORD, quoting the owner.
2. The Orchestrator replaces lines 31 to 42 (INV-4) and 44 to 75 (INV-5) of `.agentic/SAFETY_INVARIANTS.md` with the fenced blocks of sections 1 and 2, **verbatim**, and commits that change alone, citing the record.
3. If the owner edits the words, the edited text is what gets pasted, and the edit is recorded as the owner's.
4. `docs/ARCHITECTURE.md` "Safety stance" then points at the new text; its pending note (pass 2) is replaced at stage 10, not before.
