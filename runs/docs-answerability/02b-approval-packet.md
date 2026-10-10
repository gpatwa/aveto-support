# Approval packet — docs-answerability (Architecture pass 2 of 2)

> Software Architect, **standard** depth. Repo at 56b4723 (worktree `claude/aveto-docs-answerability-85eb6d`). Playbook `/Users/gopalpatwa/opt/agentic-sdlc-playbook` @ 00d491a.
> This is a **proposal**. It edits no safety control and no status text. Approvals count only when the owner gives them directly in the session driving the run (AGENTS.md rule 1).

## 1. Digest (read this first)

1. **Decision needed:** two approvals, in this session. **Rule 4**: the exact new INV-4 and INV-5 words (section 2). **Rule 5**: a Haiku-class judge subagent added to the abstention decision (section 3). Rule 6 (Anthropic, through your own session) is already approved: `APPROVAL_RECORD-2.md`. It is cited here, not asked again.
2. **Recommendation:** approve both as written. Six design questions (section 4) each have a default. The reply "defaults" accepts all six.
3. **Exact reply:** `Approve rule 4: INV-4 and INV-5 words as in 02b section 2. Approve rule 5: the judge step as in 02b section 3. Design questions: defaults.`
4. **What changes:** `retrieve` and `eval` stay unchanged. A new `/aveto-judge`, which runs only when you type it, sends the question and the full text of the shown passages to your session's model provider. It prints `no confident match` when the judge returns `NOT_ANSWERABLE`.
5. **Not approved by this reply:** a metered API, a key, `claude -p`, unattended use, a different prompt or model, the release, or edits to README, ARCHITECTURE or status. Those edits come after the verdict.
6. **Still unverified** (the support session is researching them, and 3b does not start until they are settled): the zero-tool syntax and deny hook (8.1); what `haiku` resolves to (8.2); who can spawn the judge, and where its transcripts are (8.5); whether model invocation of the command can be barred (8.6); how pack hooks behave on a judge spawn (8.14).
7. **What waiting costs:** no spend. Implementation (3a, 3b) and the seen-set check wait. No code or data-sending artefact exists yet.
8. **If you deny either one:** the slice stops before any code is written. There is nothing to undo.
9. **Checked by** the Architect (pass 2, Read/Grep only): the words against `.agentic/SAFETY_INVARIANTS.md` and tech spec sections 1-4 and 8, rules 4-6, and the mirrored sentences in the README, ARCHITECTURE and PROJECT_CONTEXT (found by grep). The prompt's sha256 was computed by the Orchestrator. I did not recompute it (no shell). 3a's test pins it.

## 2. Rule 4 — the exact INV-4 and INV-5 words

Source of "current": `.agentic/SAFETY_INVARIANTS.md` at 56b4723, lines 31-42 (INV-4) and 44-75 (INV-5), copied verbatim. **Nothing in this file has been edited.** Who edits it, and when, is in 2.4.

### 2.1 INV-4

**Current (lines 31-42, verbatim):**

```
- **INV-4** — Retrieval returns only verbatim passages from the configured
  source at its pinned commit, each with path, heading and line range; it does
  not abstain (a question the docs do not answer still returns its top files,
  and `eval` reports unanswerable questions as a diagnostic). It never returns
  generated or reworded text. **A model may be used only to rank passages and to decide confidence. It
  never produces, selects fragments of, or alters the text returned.**
  *(Enforced by `test_result_invariant_enforced`,
  `test_retrieved_text_is_verbatim_slice_of_file`,
  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
  `test_reranked_hits_are_verbatim_passages`,
  `test_reranked_result_invariant_enforced` and
  `test_reranker_returns_only_scores`.)*
```

**Proposed (replaces lines 31-42 exactly):**

```
- **INV-4** — Retrieval returns only verbatim passages from the configured
  source at its pinned commit, each with path, heading and line range; it does
  not abstain (`retrieve` still returns its top files for a question the docs
  do not answer, and `eval` reports unanswerable questions as a diagnostic). It
  never returns generated or reworded text. **A model may be used only to rank
  passages, to decide confidence, and, in the judge step an operator runs, to
  judge whether the shown passages answer the question by returning only a
  verdict. No model produces, selects fragments of, or alters the text
  returned, and the judge never produces, selects or alters the text shown.**
  Only `judge-apply` acts on a verdict, and it only chooses between two
  outputs the program builds itself: for `ANSWERABLE`, `retrieve`'s output
  unchanged plus one deciding-signal line; for `NOT_ANSWERABLE`, exactly
  `no confident match` plus that line, and no passage. Any other reply is a
  judge error: `judge-apply` prints `judge error`, exits 4 and shows nothing
  as judged, and the product neither shows nor stores the reply's text. The
  deciding-signal line names the prompt the judge step specifies; the program
  cannot verify which prompt or model a session actually used.
  *(Enforced by `test_result_invariant_enforced`,
  `test_retrieved_text_is_verbatim_slice_of_file`,
  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
  `test_reranked_hits_are_verbatim_passages`,
  `test_reranked_result_invariant_enforced` and
  `test_reranker_returns_only_scores`; for the judge step,
  `test_judge_input_matches_retrieve_selection`,
  `test_apply_answerable_is_retrieve_plus_signal`,
  `test_apply_not_answerable_exact`, `test_apply_judge_error_shows_nothing`,
  `test_apply_hash_mismatch`, `test_parse_verdict_table`,
  `test_reason_never_leaves_parser` and
  `test_unjudged_outputs_never_look_judged`.)*
```

**Diff (lines 31-42 → proposed):**

```diff
 - **INV-4** — Retrieval returns only verbatim passages from the configured
   source at its pinned commit, each with path, heading and line range; it does
-  not abstain (a question the docs do not answer still returns its top files,
-  and `eval` reports unanswerable questions as a diagnostic). It never returns
-  generated or reworded text. **A model may be used only to rank passages and to decide confidence. It
-  never produces, selects fragments of, or alters the text returned.**
+  not abstain (`retrieve` still returns its top files for a question the docs
+  do not answer, and `eval` reports unanswerable questions as a diagnostic). It
+  never returns generated or reworded text. **A model may be used only to rank
+  passages, to decide confidence, and, in the judge step an operator runs, to
+  judge whether the shown passages answer the question by returning only a
+  verdict. No model produces, selects fragments of, or alters the text
+  returned, and the judge never produces, selects or alters the text shown.**
+  Only `judge-apply` acts on a verdict, and it only chooses between two
+  outputs the program builds itself: for `ANSWERABLE`, `retrieve`'s output
+  unchanged plus one deciding-signal line; for `NOT_ANSWERABLE`, exactly
+  `no confident match` plus that line, and no passage. Any other reply is a
+  judge error: `judge-apply` prints `judge error`, exits 4 and shows nothing
+  as judged, and the product neither shows nor stores the reply's text. The
+  deciding-signal line names the prompt the judge step specifies; the program
+  cannot verify which prompt or model a session actually used.
   *(Enforced by `test_result_invariant_enforced`,
   `test_retrieved_text_is_verbatim_slice_of_file`,
   `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
   `test_reranked_hits_are_verbatim_passages`,
   `test_reranked_result_invariant_enforced` and
-  `test_reranker_returns_only_scores`.)*
+  `test_reranker_returns_only_scores`; for the judge step,
+  `test_judge_input_matches_retrieve_selection`,
+  `test_apply_answerable_is_retrieve_plus_signal`,
+  `test_apply_not_answerable_exact`, `test_apply_judge_error_shows_nothing`,
+  `test_apply_hash_mismatch`, `test_parse_verdict_table`,
+  `test_reason_never_leaves_parser` and
+  `test_unjudged_outputs_never_look_judged`.)*
```

**How the existing sentences are reconciled:**

- **"it does not abstain"** stays true and is pinned to `retrieve`. Retrieval still never abstains (spec 1.1: no change to `retrieve`, `eval` or `search.py`). The new abstention lives only in `judge-apply`, and only after a verdict. The words now say so ("Only `judge-apply` acts on a verdict").
- **"to decide confidence"** is kept word for word. It is an existing permission that ADR 0003's dense confidence relies on. Removing it would narrow a separate decision without a reason of its own (design question D5 asks whether you want that). The judge is added beside it as a third, narrower permission, rather than being folded into "decide confidence". That way it carries its own limits: returning only a verdict, and only in the step an operator runs.
- **"selects":** the intent's words, "never produces, selects or alters the text shown", are kept verbatim. The next sentence fixes their meaning. The verdict picks one of two outputs that the program builds. It cannot pick, drop or reorder a passage (spec 1.4). Without that sentence, "never selects" would be literally false, because a `NOT_ANSWERABLE` verdict does choose to show nothing.
- **"the program cannot verify which prompt or model"** is spec 8.8, stated in the invariant itself.

### 2.2 INV-5

**Current (lines 44-75, verbatim):**

```
- **INV-5** — The product's network egress is limited to two kinds of
  read-only HTTPS GET download, both made only by `ingest`:
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
  hash, never on the host. No credentials are sent. **No question, passage or
  user text ever leaves the machine.** `retrieve`, `eval` and the default test
  suite make no network calls.
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
  block.)*
```

**Proposed (replaces lines 44-75 exactly):**

```
- **INV-5** — The program's own network egress is limited to two kinds of
  read-only HTTPS GET download, both made only by `ingest`:
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
  hash, never on the host. No credentials are sent. **The program never sends a
  question, passage or user text off the machine: it makes no network call
  other than the two downloads above.** `retrieve`, `eval`, `judge-input`,
  `judge-apply` and the default test suite make no network calls; the four
  commands start no process and never call the judge. **When the operator runs
  the judge step (`/aveto-judge`), the operator's own Claude Code session sends
  the question and the full text of the shown passages to that session's model
  provider, and nowhere else; the program itself sends nothing.** The step runs
  only when the operator invokes it. The product stores no judge reply:
  `judge-apply` deletes its two transport files in `.aveto-judge/` on every
  path. The operator's session keeps its own transcript (the question, the
  passages and the reply) on the operator's machine, and the provider's
  retention follows its own terms; neither is under the product's control.
  "Nowhere else" is the judge step's contract, which the program cannot
  enforce: it cannot verify which prompt, model or destination a session used.
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
  `test_reranker_absent_fails_closed_without_download`,
  `test_program_offline_no_model`, `test_judge_modules_import_allow_list`,
  `test_apply_deletes_transport_files_every_path`,
  `test_judge_input_removes_stale_reply_only`,
  `test_reason_never_leaves_parser`, the autouse network block, and, for the
  shape of the session artefacts only (not what a session does),
  `test_agent_definition`, `test_command_definition` and
  `test_transport_dir_ignored`.)*
```

**Diff (lines 44-75 → proposed):**

```diff
-- **INV-5** — The product's network egress is limited to two kinds of
+- **INV-5** — The program's own network egress is limited to two kinds of
   read-only HTTPS GET download, both made only by `ingest`:
@@ (lines 46-55 unchanged) @@
   used**. On a mismatch the file is deleted and ingest fails. Trust rests on the
-  hash, never on the host. No credentials are sent. **No question, passage or
-  user text ever leaves the machine.** `retrieve`, `eval` and the default test
-  suite make no network calls.
+  hash, never on the host. No credentials are sent. **The program never sends a
+  question, passage or user text off the machine: it makes no network call
+  other than the two downloads above.** `retrieve`, `eval`, `judge-input`,
+  `judge-apply` and the default test suite make no network calls; the four
+  commands start no process and never call the judge. **When the operator runs
+  the judge step (`/aveto-judge`), the operator's own Claude Code session sends
+  the question and the full text of the shown passages to that session's model
+  provider, and nowhere else; the program itself sends nothing.** The step runs
+  only when the operator invokes it. The product stores no judge reply:
+  `judge-apply` deletes its two transport files in `.aveto-judge/` on every
+  path. The operator's session keeps its own transcript (the question, the
+  passages and the reply) on the operator's machine, and the provider's
+  retention follows its own terms; neither is under the product's control.
+  "Nowhere else" is the judge step's contract, which the program cannot
+  enforce: it cannot verify which prompt, model or destination a session used.
   *(Enforced by `test_redirect_to_other_host_refused`,
@@ (lines 61-73 unchanged) @@
-  `test_reranker_absent_fails_closed_without_download`, and the autouse network
-  block.)*
+  `test_reranker_absent_fails_closed_without_download`,
+  `test_program_offline_no_model`, `test_judge_modules_import_allow_list`,
+  `test_apply_deletes_transport_files_every_path`,
+  `test_judge_input_removes_stale_reply_only`,
+  `test_reason_never_leaves_parser`, the autouse network block, and, for the
+  shape of the session artefacts only (not what a session does),
+  `test_agent_definition`, `test_command_definition` and
+  `test_transport_dir_ignored`.)*
```

**What each change does, and why:**

- **"The product's network egress" → "The program's own network egress"** is one change beyond what the intent names, and I am making it on purpose. With the judge step, a product artefact (`/aveto-judge`) causes the session to send data. Left as "the product's", the first sentence would contradict the new judge-step sentence. The limit itself is unchanged: two GET downloads, made only by `ingest`.
- **"No question … leaves the machine"** becomes a claim about **the program**, which is true and tested (`test_program_offline_no_model`, `test_judge_modules_import_allow_list`, spec 6.3).
- **The judge-step sentence** says what is sent: the question and the **full** passage text, which is more than the excerpt the user sees (spec 1.3). It also says where it goes: the provider of the operator's session. That covers the main session's own model, which sees the payload in step 3, as well as the judge subagent. Both are the processor approved under rule 6 (`APPROVAL_RECORD-2.md`).
- **"Stored":** only the product's own storage is denied. The session's transcript (spec 8.18) and the provider's retention are named, not denied.
- **"Nowhere else"** is labelled as a contract. The program cannot enforce it (spec 1.2, 4.3 residual, T5). The tests listed for it check the artefacts' shape, not session behaviour. The seen-set audit (spec 5.3) and Security (spec 6.7) are what check behaviour.
- **"start no process":** `test_program_offline_no_model` (spec 6.3) runs all four commands with process creation patched to raise. "Call no model" is avoided on purpose: `retrieve` runs the local embedding model.

### 2.3 Enforcing tests, by spec name

| Invariant clause | Tests (spec section) | Part |
|---|---|---|
| INV-4: judge only chooses between program-built outputs | `test_apply_answerable_is_retrieve_plus_signal`, `test_apply_not_answerable_exact` (6.1) | 3a |
| INV-4: anything but one verdict → `judge error`, exit 4, nothing judged | `test_apply_judge_error_shows_nothing`, `test_parse_verdict_table`, `test_apply_hash_mismatch` (6.1) | 3a |
| INV-4: judge sees the same selection the user does | `test_judge_input_matches_retrieve_selection` (6.1) | 3a |
| INV-4: reply text never shown or stored by the product | `test_reason_never_leaves_parser` (6.1) | 3a |
| INV-4: `retrieve` still never abstains, unjudged output never looks judged | `test_unjudged_outputs_never_look_judged` (6.1), `test_eval_without_verdicts_unchanged` (6.2) | 3a |
| INV-5: program offline, no process, no network library | `test_program_offline_no_model`, `test_judge_modules_import_allow_list` (6.3) | 3a |
| INV-5: product stores no reply | `test_apply_deletes_transport_files_every_path`, `test_judge_input_removes_stale_reply_only`, `test_reason_never_leaves_parser` (6.1), `test_transport_dir_ignored` (6.4) | 3a / 3b |
| INV-5: artefacts name no other route (shape only) | `test_agent_definition`, `test_command_definition` (6.4) | 3b |
| INV-5: "nowhere else", which prompt or model a session used | **No test can enforce these.** Seen-set tool-use audit (5.3), Security adversarial (6.7) | — |

### 2.4 When the file is edited, and by whom (a proposal for the Orchestrator)

- These approved bytes go into `.agentic/SAFETY_INVARIANTS.md` **at the end of 3b**, in the same commit set as the last of their named tests, so the file never names a test that does not exist. The words are applied exactly as approved, with no other edit. The Orchestrator assigns the role; SAFETY_INVARIANTS' header names Architect + Security as owners. The Release Gate checks that every named test exists and passes.
- Any later change to these words, including restoring the old ones on rollback, is a new rule 4 request (spec 7.3 step 3).

### 2.5 Mirrored sentences: follow-on edits for the Tech Writer, after the verdict (not made here)

Found by grep for "never abstains", "does not abstain", "leave(s) the machine", "offline", "decide confidence" and "rank passages". **One of these is false once 3b exists**, namely README lines 70-71. So the branch must not merge to `main` before the Docs stage lands these edits. The Release Manager should check that.

| # | File:line | Current text (abridged) | Proposed follow-on |
|---|---|---|---|
| F1 | `README.md:70-71` | "`retrieve`, `eval` and the default tests make no network calls, and no question or passage text ever leaves your machine." | Scope to the program and add the judge step: the program sends nothing. If you run `/aveto-judge`, your Claude Code session sends the question and the full shown passages to your session's provider, and your session keeps its transcript. **This is false once 3b exists.** |
| F2 | `README.md:3-8` (status) | "It never abstains … Abstention is not built …" | State the scorer's recorded figure and the verdict, and nothing stronger (intent "Done means"). `retrieve` still never abstains; the judge step can print `no confident match`. |
| F3 | `README.md:54-57` | "`retrieve` … never abstains … never writes an answer." | Keep (still true of `retrieve`). Add one sentence pointing to `/aveto-judge` and `judge-apply`, and add exit code 4. |
| F4 | `README.md:81` | "It decides nothing: retrieval does not abstain." | Keep. Still true of the calibration list and of `retrieve`. |
| F5 | `docs/ARCHITECTURE.md:141-144` | "A model may **only** rank passages and decide confidence. It never produces…" | Mirror the approved INV-4 sentence, including the judge clause and "cannot verify which prompt". |
| F6 | `docs/ARCHITECTURE.md:147-148` | "Not silent when the docs do not answer … Abstention is not built." | Rewrite: abstention is the operator-run judge step. `retrieve` is unchanged. Give the verdict's figure. |
| F7 | `docs/ARCHITECTURE.md:149-159` | "Bounded network surface (INV-5 …) … **No question, passage or user text ever leaves the machine.**" | Mirror the approved INV-5: the program's egress, plus the judge-step sentence. Cite this slice's rule 4 record. |
| F8 | `docs/ARCHITECTURE.md:84-86` (diagram), `104-113` | "retrieve - offline … never abstains"; "`retrieve` is fully offline … never abstains"; "`eval` is fully offline" | Keep these (still true). Add the judge path to the diagram: `judge-input` → session → judge subagent → `judge-apply`. Mark the session hop as the only egress. Add `eval --verdicts`. |
| F9 | `docs/ARCHITECTURE.md:131-134` | "Retrieval never says the docs do not answer … abstention is not built." | Update to the judge step and its contract. Note that a future drafter can reuse it (intent). |
| F10 | `docs/ARCHITECTURE.md:190-195` (Decisions) | ADR list ends at 0007 (rejected) | Add ADR 0008 with its status at the time. |
| F11 | `.agentic/PROJECT_CONTEXT.md:79` | "(BAAI/bge-small-en-v1.5 …) only helps rank passages." | Keep (still true of the embedding model). Grep found no INV-4/INV-5 mirror in PROJECT_CONTEXT. The Tech Writer adds one line on the judge step only if the file describes features. |
| F12 | `.agentic/CURRENT_MVP_STATUS.md` | not read (outside my read list) | Per the intent, after the verdict: the scorer's figure and nothing stronger. |

`docs/ARCHITECTURE.md` is the Architect's living record. These edits are listed for the Tech Writer only because the brief for this pass forbids editing it before the verdict.

## 3. Rule 5 — an LLM judge in a previously deterministic path

### 3.1 What

Today, whether `retrieve`'s output is shown is decided by nothing: it is always shown (deterministic, no model). This request adds a **Claude Haiku-class subagent** that returns one verdict, `ANSWERABLE` or `NOT_ANSWERABLE`, for one question and its shown passages. It is invoked by the operator's own Claude Code session through `/aveto-judge`. The program applies the verdict deterministically. The program itself still calls no model (spec 1.1). The LLM sits in the **operator's session**, between `judge-input` and `judge-apply`.

### 3.2 Why

The default path never abstains (0 of 93 seen questions). No score rule reaches either bar (best 13/20 and 37/56). The local classifier tried under ADR 0007 reached 2/20. In five pilots in exactly this configuration, Haiku met both bars on the 93 seen questions (20/20 and 47/56; intent "Why this"). No deterministic alternative is left that has evidence behind it.

### 3.3 The artefacts, by exact identity

**(a) Prompt file:** `prompts/answerability-judge-v1.txt` (product-local, committed in 3a as an inert file).

- **Derivation (as spec 3.2 states it, verified in the spec):** "line 104 of that file at commit 00d491a, with its first character (`"`) and its last character (`"`) removed, followed by a single `\n`. UTF-8, no BOM, no other change." The file is `/Users/gopalpatwa/opt/agentic-sdlc-playbook/docs/pilots/2026-10-llm-answerability-pilot.md` at `00d491ac2de0418bd29bd17f9890d814b2260dcd`, section "The judge prompt (fixed; not edited after the first run)". The text is extracted from that line, not retyped.
- **sha256:** `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427`. The Orchestrator computed it from the extraction above and recorded it in `STATE.md`. I did not recompute it (this role has no shell). `test_prompt_file_hash` (spec 6.4) pins file hash == `judge.PROMPT_SHA256` == this literal. A different byte fails the test and the step closed.
- **Text (as quoted in spec 3.2, for reading only; the bytes are the extraction above, not this quote):**

  > You judge documentation search results. For each block you get a user's question and the passages a search returned. Decide whether the passages themselves contain the information needed to answer the question. Answer ANSWERABLE only if they do. Answer NOT_ANSWERABLE if the passages are on a related topic but do not state what the question asks, or are unrelated. Judge only from the passages shown; use no outside knowledge and no tools. Reply with one line per block, exactly: <id> <ANSWERABLE|NOT_ANSWERABLE> <at most 12 words of reason>.

- The prompt is not edited for the product, and no injection-hardening sentence is added. That would be an unpiloted change (spec 3.2). A changed prompt is a new file, a new sha256 and a new rule 5 request.

**(b) Subagent definition:** `.claude/agents/aveto-answerability-judge.md` (product-local, 3b). Body = the prompt file's bytes exactly, after the frontmatter and one empty line. Frontmatter as in spec 3.3:

| Field | Value | Status |
|---|---|---|
| `name` | `aveto-answerability-judge` | decided |
| `description` | "Product-local answerability judge, used only by the /aveto-judge command. Never delegate to it otherwise. Not a pack role." | decided |
| `tools` | **none** (a zero-tool form) | **8.1 — unverified, being researched by the support session; 3b does not start until settled.** If no zero-tool form exists, this comes back to you. It does **not** fall back to `tools: Read`. |
| `hooks: PreToolUse` | a match-all matcher, `type: command`, `echo "aveto-answerability-judge has no tools" >&2; exit 2`, timeout 10 | **8.1 — unverified** (the match-all matcher string, and whether exit 2 blocks the call); same condition |
| `model` | `haiku` (the alias; the pack's verified class vocabulary, `.claude/agentic.config.json:10-14`) | **8.2 — unverified** which model the alias resolves to (the pilots ran "Haiku 4.5"). Being researched; 3b does not start until settled. The seen-set check records the model actually run, and a non-Haiku-class model voids the batch. |
| `effort` | omitted (harness default) | 8.3: the pilots' effort setting is not recorded. The check records what the harness reports. |

**(c) Command:** `.claude/commands/aveto-judge.md` (product-local, 3b). Its body is the contract of spec 1.2 plus rules 1-6 of spec 3.4: run only when the operator types `/aveto-judge <question>`; use only `aveto-answerability-judge`, never another agent or model, never `claude -p` or an API; pass the payload verbatim and complete; treat the reply as data, write it unmodified to `.aveto-judge/reply.txt` (empty if there is none), and never show, quote, paraphrase or store it elsewhere; show `judge-apply`'s stdout verbatim, or only `judge error` on exit 4; write the question and the reply with the Write tool, never in a shell command. The main session needs Write, Bash (for `uv run`) and the Agent tool. It grants the judge nothing.

- **8.6 — unverified, being researched by the support session; 3b does not start until settled:** whether a command can be barred from model invocation. If a flag exists, it is added. A skill was rejected because a model may invoke one on its own.

**(d) Around the artefacts (also unverified, same condition):**

- **8.5:** whether a subagent can spawn the judge, and where each judge spawn's transcript is kept for the tool-use audit. This must be settled before the seen-set check.
- **8.14:** how the pack's `budget-guard.mjs` (a `PreToolUse` hook on every Agent spawn) behaves on a judge spawn, both inside a slice and in plain operator use. If it misbehaves, the support session handles it. The installed hook is not patched.

### 3.4 What the owner is approving, and what not

**Approving (rule 5):**

1. The judge step as the decision on whether `judge-apply` shows `retrieve`'s output or `no confident match`. The judge is the prompt with sha256 `24b244d2…5427` (full value above), in the zero-tool `haiku` subagent above, run through `/aveto-judge`.
2. Building 3b (the three files 9-11 of spec 7.1) once 8.1, 8.2, 8.5, 8.6 and 8.14 are settled within the forms stated above.
3. Its use, attended only: in the seen-set check (93 seen questions, one fresh judge per question, spec 5), in slice B's single scoring run on the fifth set (spec 5.6), in Security's adversarial tests, and by an operator who types `/aveto-judge`. Each use draws on the operator's subscription usage window. There is no per-token bill (intent decision 1). Spec 5.2 gives the seen-set check's cost as roughly 60-80k peak context per driver batch, over 6 batches, plus small Haiku spawns. It is inside the confirmed plan (STATE: plan 950k, ceiling 1.4M).

**Not approving:**

- A metered API, an API key, any credential, or `claude -p` (intent constraints).
- Scheduled or unattended use (intent decision 1 and "not a service").
- Any other prompt, any edit to this one, any other model or tier (a larger tier needs a measurement and a new decision, intent decision 2), or any tool for the judge. Each is a new rule 5 request.
- A change to `retrieve`, `eval`'s default output or exit code, retrieval or ranking.
- The INV-4 and INV-5 words. That is rule 4, approved separately in section 2.
- The data processor. That is rule 6, **already approved: `runs/docs-answerability/APPROVAL_RECORD-2.md`** (Anthropic, through the operator's own Claude Code session). It is cited here, not asked again. The payload in 1.3 of the spec (question + full shown passages) is what that processor receives.
- Release, merge or announcement. Those belong to the Release Gate and need both bars to pass.

### 3.5 Reversible if denied

No code and no data-sending artefact exists yet. Implementation is pending, and the spec's order puts both approvals before 3a (spec 8.15). If rule 5 is denied, nothing is built. The slice stops and is recorded "not releasable, judge not approved". There is nothing to revert. If the approval is given and later withdrawn, the rollback is spec 7.3: revert 3b, then 3a, and delete any local `.aveto-judge/`. Restoring the old INV words would itself be a rule 4 request.

### 3.6 The smallest request

One prompt (by sha256), one Haiku-class subagent with zero tools, one command that runs only when an operator types it, one question per spawn, attended only, on the processor already approved. The request asks for no tool for the judge, no new dependency (spec 6), no network call in the program, no stored replies and no change to the default path.

## 4. Owner design questions (not approvals; each has a default)

"Design questions: defaults" accepts every default below. To override one, reply with its line, for example `D1: confirm per question`.

| # | Question | Recommended default | Reply to override |
|---|---|---|---|
| D1 | **Payload inspectable, no per-question confirmation (spec 8.17).** `judge-input` prints the payload in the session before the spawn, and nothing stops to ask. | No per-question stop. You typed the command, and rule 6 is approved. | `D1: confirm per question` (the command adds a stop between steps 3 and 4) |
| D2 | **Shape of `no confident match` (spec 8.20).** | Two stdout lines: line 1 exactly `no confident match`, line 2 the `Deciding signal: …` line. | `D2: signal on stderr` (stdout becomes the single line) |
| D3 | **False premises (spec 8.13, owner decision 2).** | The labels decide (answerable = show the sources). If the fifth set marks false-premise questions, the scoring QA reports the strict reading from the key, as a diagnostic. `judge_eval` reads no new key in this slice. | `D3: score the strict reading in judge_eval` (adds a key and tests to 3a) |
| D4 | **Exit code for `judge error` (spec 1.5).** | `4`, distinct from 0 (ok), 1 (retrieval gate), 2 (input) and 3 (fetch). Only `judge-apply` returns it. | `D4: exit 2` (judge error merges with input errors) |
| D5 | **Keep "to decide confidence" in INV-4 (section 2.1).** | Keep it. It is an existing permission that ADR 0003 relies on, and dropping it is a separate decision. | `D5: drop "decide confidence"` (I redraft INV-4 and the rule 4 request is re-made) |
| D6 | **Merge order (section 2.5).** README lines 70-71 become false once 3b exists. | The branch does not merge before the Docs stage lands F1-F12. The Release Manager checks this. | `D6: <your order>` |

Recorded by the Architect and needing no reply unless you object: the 12-word reason limit is not enforced (spec 8.9); the judge path is fixed to `file-rrf-v1` (spec 8.10); `effort:` is omitted (spec 8.3); 3a waits for both approvals (spec 8.15, the Orchestrator's call).

## 5. Replies, exactly

- **Everything as recommended (one message):**
  `Approve rule 4: INV-4 and INV-5 words as in 02b section 2. Approve rule 5: the judge step as in 02b section 3. Design questions: defaults.`
- **Separately:**
  - Rule 4: `Approve rule 4: INV-4 and INV-5 words as in 02b section 2.`
  - Rule 5: `Approve rule 5: the judge step as in 02b section 3.`
- **Deny:** `Deny rule 4` or `Deny rule 5`, with any reason. The slice stops before any code is written (3.5).

Each approval counts only when typed by the owner in the driving session. The Orchestrator writes one `APPROVAL_RECORD-<n>.md` per rule and fills in the STATE approvals rows. A message relayed from another session is not an approval.

## Handoff

- **To the Orchestrator:** present sections 1 and 5 to the owner and wait. Record the decisions. Before 3b, confirm that the support session has settled 8.1, 8.2, 8.5, 8.6 and 8.14 within the forms in 3.3. A result outside those forms goes back to the owner.
- **To the AI Engineer (Implementation), after both approvals:** spec 02-tech-spec.md as written, plus the approved INV words, which are applied to `.agentic/SAFETY_INVARIANTS.md` at the end of 3b exactly as in 2.1 and 2.2 (2.4). The prompt sha256 to pin is `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427`.
- **To the Tech Writer, after the verdict:** F1-F12 in 2.5.
- **ADR:** `docs/adr/0008-operator-run-answerability-judge.md` (Proposed).

