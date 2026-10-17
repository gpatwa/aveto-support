# 12 - Tier 3 gate items: dry run on a fixture, and audit event coverage (docs-answerability-2)

- **Stage / role:** QA Evidence (fresh spawn), depth standard. Edits only this file. Approves nothing.
- **Worktree:** `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-answerability-2`, branch `claude/docs-answerability-2`, HEAD `9d25a97`.
- **Why:** the owner ruled the release tier 3 (`APPROVAL_RECORD-9.md`). Tier 3 adds (a) a dry run on a fixture before live and (b) audit event coverage verified manually (playbook `docs/RELEASE_GATES.md`, "Tier 3"). The "external effect" here is the operator-run judge step sending data to the operator's model provider (INV-5) and printing `no confident match`.
- **Not opened / not run (by the brief):** `evals/retrieval-heldout-5*.toml`, `judge-check/batch-2.txt`, `judge-check/q/`, `06-label-review.md`, diffs. No judge spawn, no `claude -p`, no network, no metered API, nothing pushed. Nothing was run on the fifth set.
- **Scratch dir (outside the repo):** `/private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/4e1555a5-07b3-40cd-a817-c0720ebbe723/scratchpad/qa-dryrun/` (called `$S` below). The only repo path the commands touch is the gitignored `.aveto-judge/` transport directory (`.gitignore:17`), which `judge-apply` requires and empties.
- **Index used:** `index/docs-index.json`, sha256 `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756`; models from `models/` (cached, no fetch).

## Part (a) - Dry run on a fixture (offline, no model)

### Pass criteria, stated before running

| # | Criterion |
|---|---|
| A1 | `judge-input` on each of 3 questions exits 0; stdout is a payload that starts `=== Q1 ===` and ends `=== end Q1 ===`; stderr is exactly one line `input sha256: <64 hex>`; a second run gives the same hash; it writes nothing (the repo's tracked/untracked set is unchanged, `.aveto-judge/` stays empty). |
| A2 | Valid ANSWERABLE reply: exit 0; stdout equals `retrieve`'s own stdout for the same question (default ranking) followed by exactly one line, the `Deciding signal:` line naming ANSWERABLE; stderr empty. Compared mechanically (`diff` of `judge-apply` stdout minus its last line against `retrieve` stdout). |
| A3 | Valid NOT_ANSWERABLE reply: exit 0; stdout is exactly two lines, `no confident match` then the `Deciding signal:` line naming NOT_ANSWERABLE; no passage, path or question text; stderr empty. |
| A4 | Empty reply: exit 4; stdout exactly `judge error`; stderr exactly `judge error: empty reply`. |
| A5 | Malformed reply: exit 4; stdout `judge error`; stderr one fixed category line (`malformed verdict line`). |
| A6 | Colon after the token: the grammar in `judge.py:44-46` allows `:?` directly after the token, so `Q1 ANSWERABLE:` and `Q1 NOT_ANSWERABLE: <reason>` are accepted (exit 0, reason never shown); a colon elsewhere (`Q1: ANSWERABLE`, `Q1 ANSWERABLE:reason`) is a judge error. Predicted from the code, then checked. |
| A7 | Multi-line reply with the verdict on the last line: exit 0, earlier lines neither shown nor stored. |
| A8 | Reply with a non-matching `--input-sha256`: exit 4, stdout `judge error`, stderr `judge error: verdict is for a different input`; no passage printed. |
| A9 | On every `judge-apply` path above, `.aveto-judge/` is empty afterwards (question and reply deleted), and no reply text appears on stdout or stderr. |
| A10 | `eval --eval-file <3-question synthetic file> --verdicts <synthetic verdicts>` prints the usual report, then the judge section with both bars, the judge-error count and the diagnostics, with figures equal to hand-computed expectations (written down before the run); exit code is the retrieval gate on the synthetic file. A tampered `input_sha256` and `--ranking file-rerank-v1` with `--verdicts` are refused with exit 2 and no report. |
| A11 | Nothing in the run uses the network, starts a model, or leaves a file in the repo (tracked/untracked set unchanged apart from other agents' own run files). |

### Results

**Fixture questions.** Answerable: `a01` of `evals/retrieval.toml` ("How do I add Aveto to a project I already have?"). Unanswerable (hard negative): `u02` of the same file ("Does Aveto run on Windows?"). Made-up: "Which agent writes the rollback plan for a slice?". Each was written to a temp file in `$S`. No file under `evals/retrieval-heldout-5*` was opened. **Replies are hand-written fixtures; no model ran.** Runner: `$S/run-apply.sh` (copies the question and reply into `.aveto-judge/` as the skill does, runs `judge-apply`, records exit code, line count, what is left in `.aveto-judge/`, stderr). A first attempt failed on my own runner (relative paths after a `cd`); it was fixed and everything below is from the second run.

#### A1. `judge-input` (command: `uv run python -m aveto_support judge-input --question-file $S/q-<name>.txt`)

| Question | Exit | stdout | stderr (the whole of it) | Second run, same hash |
|---|---|---|---|---|
| a01 (answerable) | 0 | 207 lines, 9,561 bytes; first line `=== Q1 ===`, last `=== end Q1 ===` | `input sha256: b48a7e93c476db5e9469d5b1bf4ac6a905084c1a2d5995a7b3398d500d903978` | yes |
| u02 (unanswerable) | 0 | 169 lines, 7,304 bytes; same first/last | `input sha256: fc211a043cedee499516fa9ebd549f6ee3989179df8798e7f6490af86661eae7` | yes |
| made-up | 0 | 129 lines, 5,299 bytes; same first/last | `input sha256: 4c577283d3af0850a3fe5b3e5089ebd32554942257500c1e602b9f43c6f604c8` | yes |

`.aveto-judge/` held 0 entries afterwards; `git status --short` outside `runs/` was empty. A fourth payload (a02's question, used below for the scorer) was printed by mistake to the terminal while I fetched its hash: it is the full verbatim text of nine passages from five files with headings and line ranges (about 9 KB), which is what INV-5 says the operator's session sends the provider. Nothing else is in it (no score, URL or label).

#### A2 to A9. `judge-apply` with hand-written replies (`--verdict-file .aveto-judge/reply.txt`, question file `.aveto-judge/question.txt`, `--input-sha256` from the matching `judge-input`)

`SENTINEL-ZETA` is a marker I put in the reply text of the malformed, colon-reason and multi-line fixtures to prove reply text never comes back out.

| Case | Fixture reply (bytes) | Exit | stdout shape (fixed lines quoted) | stderr | `.aveto-judge/` after | Marker seen in any output |
|---|---|---|---|---|---|---|
| ANSWERABLE, a01 | `Q1 ANSWERABLE\n` | 0 | 57 lines = `retrieve`'s stdout (56 lines) + one line `Deciding signal: answerability judge verdict ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d2...)` | empty | empty | 0 |
| NOT_ANSWERABLE, u02 | `Q1 NOT_ANSWERABLE\n` | 0 | exactly 2 lines: `no confident match` / `Deciding signal: answerability judge verdict NOT_ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427)` | empty | empty | 0 |
| Empty reply | 0 bytes | 4 | `judge error` | `judge error: empty reply` | empty | 0 |
| Malformed | `I think the passages answer it. SENTINEL-ZETA\n` | 4 | `judge error` | `judge error: malformed verdict line` | empty | 0 |
| Colon after token, bare | `Q1 ANSWERABLE:\n` | 0 | as ANSWERABLE (57 lines, last line names ANSWERABLE) | empty | empty | 0 |
| Colon after token, with reason | `Q1 NOT_ANSWERABLE: SENTINEL-ZETA the docs never mention the operating system\n` | 0 | the same 2 lines as NOT_ANSWERABLE (byte-identical output, sha256 prefix `e35ab806b4d07ddf0fca` for all three NOT_ANSWERABLE runs); the reason is not shown | empty | empty | 0 |
| Colon after the id | `Q1: ANSWERABLE\n` | 4 | `judge error` | `judge error: wrong block id` | empty | 0 |
| Colon, no space before reason | `Q1 ANSWERABLE:SENTINEL-ZETA\n` | 4 | `judge error` | `judge error: malformed verdict line` | empty | 0 |
| Multi-line, verdict last | `Let me think. SENTINEL-ZETA\nThe passages cover install.\nQ1 ANSWERABLE\n` | 0 | as ANSWERABLE (57 lines); earlier lines not shown | empty | empty | 0 |
| Hash mismatch | `Q1 ANSWERABLE\n` for a01, `--input-sha256` of the made-up question's payload | 4 | `judge error` | `judge error: verdict is for a different input` | empty | 0 |
| Made-up question, ANSWERABLE | `Q1 ANSWERABLE\n` | 0 | 68 lines = `retrieve` stdout + signal line | empty | empty | 0 |
| Made-up question, NOT_ANSWERABLE | `Q1 NOT_ANSWERABLE\n` | 0 | the same 2 fixed lines | empty | empty | 0 |

Extra exit paths run to feed part (b): reply over 4096 bytes: exit 4, `judge error: reply too long`; a BEL character in the reply: exit 4, `judge error: control or format character`; two verdict tokens on the last line: exit 4, `judge error: more than one verdict token`; `Q2 ANSWERABLE`: exit 4, `judge error: wrong block id`; verdict file outside `.aveto-judge/`: exit 4, `judge error: verdict file outside .aveto-judge/` (the outside file and the outside question file were left untouched); verdict file missing: exit 4, `judge error: verdict file unreadable`; empty question file: **exit 2**, stdout empty, stderr `error: the question is empty` (the transport files were still deleted; `.aveto-judge/` empty). For every case `.aveto-judge/` was empty afterwards.

**How the ANSWERABLE output was compared with `retrieve`.** `uv run python -m aveto_support retrieve "$(cat q-<name>.txt)" > retrieve-<name>.txt` (default ranking, exit 0, 56 lines for a01). Then, for each ANSWERABLE-producing case: `head -n $((N-1)) out-<case>.txt | diff -q - retrieve-<name>.txt` where N is the line count of the `judge-apply` stdout. Result: IDENTICAL for a01 (three cases: plain, colon, multi-line) and for the made-up question. Control: `head -n 55` of the same output against the same file is reported as different, so the comparison does detect a one-line change. `retrieve`'s stdout contains neither `no confident match` nor `Deciding signal` for a01, u02 or the made-up question (grep count 0 each).

#### A10. `eval --verdicts` on a synthetic 3-question file

Files in `$S`: `synth-eval-A.toml`, `synth-eval-B.toml`, `synth-verdicts.toml` (header comment says synthetic; the labels are made up for this test, not the owner's). Questions: `s1` = a02's text, answerable, source `docs/GETTING_STARTED.md`; `s2` = a01's text, answerable, source `docs/DEPLOYMENT.md` (file A) or `docs/RELEASE_GATES.md` (file B, a deliberate miss); `s3` = u02's text, unanswerable, hard negative. Verdicts (hashes from `judge-input`): `s1` ANSWERABLE, `s2` JUDGE_ERROR, `s3` NOT_ANSWERABLE.

Expected in advance (file A): retrieval 2/2 hits, exit 0; rows `s1 ... AGREE`, `s2 JUDGE_ERROR ... DIFF`, `s3 ... AGREE`; bar 1 = 1/1 MET; bar 2 = 1/2 NOT MET; judge errors 1; hard negatives 1/1; end to end 1/2. File B: retrieval 1/2 = 50%, exit 1; `s2 ... n/a`; bar 2 = 1/1 MET (no hit, so not in its denominator).

Observed:
- File A: exit 0 (`eval: PASS`). Rows `s1  ANSWERABLE  show (right file rank 1)  AGREE`, `s2  JUDGE_ERROR  show (right file rank 1)  DIFF`, `s3  NOT_ANSWERABLE  abstain  AGREE`. Lines `bar 1 ... 1/1 (100.0%) ... MET`, `bar 2 ... 1/2 (50.0%) ... NOT MET`, `judge errors: 1 (counted as failures on both bars)`, `hard negatives abstained: 1/1 (diagnostic)`, `end to end: ... 1/2 (diagnostic)`, `bars: unanswerable_abstained=1/1 answerable_hit_not_abstained=1/2 judge_errors=1`, and the closing `judge: bars reported, not gated here; eval exit code is the retrieval gate`. Every figure equals the expectation.
- File B: exit 1 (`eval: FAIL`, the retrieval gate), judge section: `s2  JUDGE_ERROR  show (right file not in top 5)  n/a`, bar 2 `1/1 (100.0%) ... MET`. Equals the expectation. (A judge error on a question with no hit is not in either bar; the `diagnostics` command reports it separately, `test_diagnostics_judge_error_on_a_question_without_a_hit`.)
- Refusals, each exit 2 with empty stdout (no report printed): a tampered `input_sha256` (`error: s1: input_sha256 is not the hash of this product's payload for the question`); `--ranking file-rerank-v1` with `--verdicts` (`error: --verdicts needs --ranking file-rrf-v1: the judge was measured on that ranking only`); a `reason = "SENTINEL-ZETA"` key in a verdict entry (`error: each [[verdict]] needs exactly id, verdict, input_sha256`; the marker appears nowhere in the output).

#### A11. Offline

Beyond the offline tests (`test_program_offline_no_model`, `test_judge_modules_import_allow_list`), I re-ran `judge-apply` (NOT_ANSWERABLE), `judge-input` and `eval --verdicts` under `sandbox-exec -p '(version 1)(allow default)(deny network*)' uv run --offline ...`. A control `socket.connect(('1.1.1.1',443))` under the same profile failed with `PermissionError: Operation not permitted`, so the profile does block. All three commands gave the same results as above (exit 0, same output). `git status --short` outside `runs/` was empty at the end, and `.aveto-judge/` was empty. The commands start no model.

### Part (a) criteria check

| # | Result |
|---|---|
| A1 | PASS (3 questions; one stderr line; deterministic; nothing written) |
| A2 | PASS (stdout minus the signal line identical to `retrieve`; compared with `diff`, with a negative control) |
| A3 | PASS (exactly two lines, no passage or question text) |
| A4 | PASS |
| A5 | PASS |
| A6 | PASS (prediction from the code held on all four colon forms) |
| A7 | PASS |
| A8 | PASS |
| A9 | PASS (12 cases plus 7 extra exit paths; the marker was never echoed; `.aveto-judge/` empty every time) |
| A10 | PASS (figures equal the pre-written expectations, both exit codes, three refusals) |
| A11 | PASS (including an OS-level network deny, with a control that proves the deny) |

**Part (a) verdict: PASS.** One observation, not a defect: a harness error on my side (missing file) is reported by the product as `verdict file unreadable` with exit 4, indistinguishable from a bad reply; the category names are the fixed ones in the spec, so this is as designed.

## Part (b) - Audit event coverage, checked by hand

Method: read the code paths (`judge.py`, `__main__.py` lines 137-210, `judge_eval.py`, `tools/judge_run.py` `apply_reply`/`record`, the skill and agent files), ran the exit paths in part (a), read the committed stage records (`judge-check/stage5/audit.md`, `audit.json`, `verdicts.toml`; I did not open any `diffs.md`, `batch-2.txt` or `q/` file), and ran the judge test files (`uv run pytest tests/test_judge.py tests/test_judge_run.py tests/test_judge_eval.py tests/test_judge_artefacts.py tests/test_judge_seen_skill.py`: **207 passed, 2 deselected**). The product has no event store (spec section 7): its audit trail is what it prints, plus the run records. "Record" below means that.

Column "Check": **T** = exercised by the named test; **R** = verified by reading only; **D** = exercised by me in part (a).

### B1. The operator path (`/aveto-judge`), step by step

| # | Action | Record that exists (where, content) | Deliberately not in it | Check |
|---|---|---|---|---|
| 1 | `judge-input` removes a stale `.aveto-judge/reply.txt` | none (state change on a temp file; spec says no event needed). Failure: `error: cannot remove the stale reply file in .aveto-judge/`, exit 2, stderr | - | T `test_judge_input_removes_stale_reply_only`; D (dir empty after) |
| 2 | Question read, normalised, validated | refusal only: `error: <fixed text>`, exit 2, stderr (empty, control char, over 4096 bytes, not UTF-8, both/neither source) | the question is not logged | T `test_question_normalised`, `test_question_controls_rejected`, `test_question_file_limits`, `test_question_sources_exclusive` |
| 3 | Payload build (`retrieve_for_judge`, `format_judge_input`) | stdout is the payload itself (the data that will leave the machine, inspectable first). Marker forgery refused: `error: ...a passage line starts like a payload marker`, exit 2 | no score, URL, label, index path (INV-5 list) | T `test_judge_input_layout_exact`, `test_judge_input_has_no_scores_urls_labels`, `test_passage_marker_collision_refused`; D (3 payloads) |
| 4 | Payload hash | stderr `input sha256: <64 hex>` (only record of payload identity on this path; terminal only, not persisted by the program) | - | T `test_judge_input_deterministic_and_hash_on_stderr`; D (stable across two runs) |
| 5 | **The spawn: the INV-5 egress** (operator's session sends question, payload, fixed prompt, session context to its provider) | **No program record.** The program starts no process (T `test_program_offline_no_model`, `test_judge_modules_import_allow_list`; D under a network-deny sandbox). The only record is the harness's own session transcript (outside the repo, operator's). What is sent is documented in INV-5 and measured in `01-measurement.md` (as measured 2026-10-12, "not complete": about 2.7k of 14.2k tokens not itemised) and approved in `APPROVAL_RECORD-3.md` (processor) and `-8.md` (environment list) | the program cannot log what the harness attaches | T for the pinned definition: `test_agent_definition`, `test_command_definition`, `test_deny_hook_refuses_every_input`; R for "what was sent" |
| 6 | Judge tool call attempted | refused by the agent's `PreToolUse` hook (`echo "aveto-answerability-judge has no tools" >&2; exit 2`); the refusal is visible only in the harness transcript. Not audited on this path (the eval path audits it, see B2) | - | T `test_deny_hook_refuses_every_input` (hook); no test for an operator-path audit because none exists |
| 7 | Reply written to `.aveto-judge/reply.txt` by the Write tool | none; the reply (up to 4096 bytes, else `reply too long`) exists only in that file until step 8 and in the session transcript | skill rule 4: not shown, quoted or stored elsewhere | T `test_command_definition` pins the wording; R for the behaviour of the session |
| 8 | `judge-apply`, exit 0 ANSWERABLE | stdout: `retrieve`'s output + `Deciding signal: answerability judge verdict ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d2...)` (verdict, prompt id, prompt hash) | the reply text and reason; the model; the input hash; time; operator | T `test_apply_answerable_is_retrieve_plus_signal`; D |
| 9 | `judge-apply`, exit 0 NOT_ANSWERABLE | stdout exactly `no confident match` + the `Deciding signal:` line | no passage, path, question, reason | T `test_apply_not_answerable_exact`; D |
| 10 | `judge-apply`, exit 4 (11 fixed categories) | stdout `judge error`; stderr `judge error: <category>` | the reply text is never echoed (marker test in D) | T every category: `test_parse_verdict_table` (empty reply, malformed verdict line, wrong block id, more than one verdict token, control or format character), `test_apply_judge_error_shows_nothing` and the table at `test_judge.py:415-423` (reply too long, reply not UTF-8), `test_apply_missing_verdict_file` (verdict file unreadable), `test_apply_hash_mismatch` and `test_apply_after_reingest_is_refused` (different input), `test_apply_outside_transport_dir_untouched` (outside), `test_apply_deletion_failure_is_judge_error` (not deleted). D ran 9 of the 11 (not "reply not UTF-8", not "transport file not deleted") |
| 11 | `judge-apply`, exit 2 (bad question file, missing index) | stderr `error: <text>`, stdout empty; transport files deleted first | - | T `test_apply_deletes_transport_files_every_path`; D (empty question) |
| 12 | `judge-apply`, unexpected non-domain exception | deletion runs, then the exception is re-raised: a Python traceback, exit 1. No fixed category line | - | R (`__main__.py:192-207`); no test |
| 13 | Hash binding (payload rebuilt, compared with `--input-sha256`) | the `verdict is for a different input` category | - | T as in row 10; D |
| 14 | Transport deletion (question and reply, every path) | none on success (absence); failure becomes `judge error: transport file not deleted`, exit 4, and happens before any result is printed | a symlink or a file outside `.aveto-judge/` is skipped silently (S2) | T `test_apply_deletes_transport_files_every_path`, `test_apply_deletion_failure_is_judge_error`, `test_apply_outside_transport_dir_untouched`; D (empty after 19 runs; outside files untouched) |
| 15 | Files stored under `.aveto-judge/` | `question.txt`, `reply.txt` only, transient; the directory is gitignored (`.gitignore:17`) | nothing is retained after `judge-apply` | T `test_transport_dir_ignored`; D |
| 16 | `retrieve` / `eval` without `--verdicts` never look judged | n/a (negative property) | - | T `test_unjudged_outputs_never_look_judged` (see S7 below for the crafted-question exception) |

### B2. The eval path and the run records

| # | Action | Record that exists | Deliberately not in it | Check |
|---|---|---|---|---|
| 17 | `derive-sample` / `add-set` | `judge-check/key/key.toml` header comment (generating command, index sha256, counts, parity; add-set: "no label read"), `batch-1.txt`, `sample-eval.toml`; refuses to overwrite an existing key | no label in the key (membership only) | T `test_derive_order_parity_and_smoke`, `test_derive_refuses_when_counts_are_off`, `test_write_check_dir_refuses_existing_key`, `test_key_has_membership_only_and_no_label`, `test_add_set` |
| 18 | `seen_payload.py` prepares a run id | writes `judge-check/q/<id>.txt` (question only); a refusal prints one `refused:` line, exit 2 | judge-input's stderr (the hash) is discarded here, so the hash is recomputed later by `record` | T `test_prepare_writes_question_only`, `test_refuses_bad_ids`, `test_refuses_id_not_in_key`, `test_refuses_wrong_argument_count`. (S5 and S6 touch this path's permission model, not its record.) |
| 19 | Spawns by the forked skill | the harness transcripts (outside the repo); committed driver logs `05b-driver-log.md`, `07a-driver-log.md` (session id, subagents dir, ids invoked in order, first anomaly, "no reply text copied") | reply text | R (files exist and read as described; I read the head of `05b` only) |
| 20 | `check-transcripts` | stdout per spawn: model, offered tools, `tool_use` count, base-dir line length, payload, peak; no reply text, no token | reply, token | T `test_judge_run.py:548` (7 lines per the fixture) |
| 21 | `record`: attribution, void checks (tool_use, model, offered tools, base-dir line, unknown payload, duplicate, missing) | `audit.md` is written even when the batch is void, with `Batch decision: VOID` and one `void reason:` per cause | - | T `test_record_voids_the_whole_batch` (8 parametrised causes: verdicts.toml and diffs.md absent), `test_record_expect_tools_must_match` |
| 22 | `record`: each reply through the product's `judge-apply` in-process | `audit.md` row per spawn: run id, eval id, agent id, model, offered-tool count, `tool_use`, line length, payload sha16, **reply sha16**, token or `JUDGE_ERROR (<category>)`, peak, in-equivalent; batch totals; other agents. Checked on the committed `stage5/audit.md`: 49 spawn rows (48 plus the smoke), columns as listed | **no reply text** (a test plants `Q1 ANSWERABLE` and "shows it" and asserts neither appears) | T `test_record_valid_batch_scores_through_the_product`, `test_apply_reply_matches_the_product_grammar`, `test_apply_reply_not_utf8_and_different_input` |
| 23 | `record`: `verdicts.toml` | `format`, `prompt_sha256`, per question `id`, `verdict`, full `input_sha256`; input to `eval --verdicts` (D: the same file shape scored end to end) | no reason, no reply | T `test_record_valid_batch_scores_through_the_product`, `test_verdicts_loader_rejects` |
| 24 | `record`: `audit.json` | run id, eval id, token, category, peak, in-equivalent, in_batch; feeds `diagnostics` | no hash, no reply | T `test_record_differing_rows_and_error_split` (reads it) |
| 25 | `record`: `diffs.md` | for each differing or errored row: run id, eval id, expected, verdict, category and the **full reply text** (or `(no reply)`) | this is the one place a reply is stored, by design ("run record only") | T `test_record_differing_rows_and_error_split` (reply present in diffs, absent from audit) |
| 26 | `record`: `apply_reply` anomaly (exit other than 0/4, unexpected stdout shape) | `ApplyError` -> `error: ...` on stderr, exit 2. `audit.md` is written **after** the replies are applied, so an anomaly leaves no `audit.md` for that call | - | T `test_apply_reply_unexpected_exit_or_stdout_is_an_anomaly` (raises); R for "no audit.md" |
| 27 | `eval --verdicts` | stdout: per-question rows (id, token, expectation, AGREE/DIFF/n/a), both bars, judge errors, hard-negative diagnostic, `bars:` machine line, closing "not gated" line. Malformed or foreign verdicts: `error: ...`, exit 2, no report | reply text and reasons are rejected at load (extra key refused, D) | T `test_eval_verdicts_appends_after_unchanged_report`, `test_verdicts_loader_rejects`, `test_bars_line_fixed_format`, `test_eval_verdicts_exit_code_is_retrieval_gate`; D |
| 28 | `diagnostics` (incl. `--self-check`) | stdout figures; self-check exit 1 if not 13/20 and 37/56 | - | T `test_best_score_rule_counts`, `test_diagnostics_judge_error_on_a_question_without_a_hit`; the `--self-check` on the real index is the `-m model` test run (not run here) |
| 29 | Approvals and review | `APPROVAL_RECORD-1..9.md`, `08-security-review.md`, `07-gate-scoring.md` (committed) | - | R (files present; I read the S-findings section of 08) |

### B3. The INV-5 data flow, audit view

1. What leaves the machine on the operator path: question, payload (about 5 to 9.6 KB of verbatim passages in my three fixtures), fixed judge prompt, session context. Program-side record: the payload is printable beforehand and its sha256 is printed. Provider-side record: none visible to the program.
2. Who is accountable: the operator typed the command (the skill is `disable-model-invocation: true`; pinned by `test_command_definition`) and the owner approved the processor and the environment list (APPROVAL_RECORD-3, -8).
3. No local log says "this question was sent at this time"; the harness transcript is the only trace. That is the design (section 7: no event store) and the INV-5 text says the list is "as measured and is not complete".

### B4. Advisories touching audit (08-security-review.md)

| Id | Touches audit how | Status here |
|---|---|---|
| S1 | A judged ANSWERABLE output echoes the **normalised** question (whitespace collapsed), so the echoed header can differ from what the operator typed or what `retrieve` echoes. In D every fixture question was single-spaced, which is why `retrieve` matched byte for byte | advisory, unchanged; matters for comparing outputs |
| S2 | A symlink named `reply.txt` is skipped by the cleanup with no error and no record | advisory; not exercised by me; T partly: `test_judge_input_removes_stale_reply_only` shows the symlink is neither followed nor deleted |
| S3 | Passage text can imitate payload structure and carry control characters to the judge; the payload hash would still match | advisory; no audit record of it beyond the payload itself |
| S4 | Any model in the session can spawn the judge, with a `model` override; the operator path records neither which model answered nor any tool use; only the eval path does (rows 21, 22) | advisory; real asymmetry between the two paths |
| S7 | `retrieve` echoes the raw question, so a question with a newline can print a bare `no confident match` or `Deciding signal:` line; the signal line is plain text, not tamper-evident | advisory; I did not re-run the probe |
| S8 | `parse_verdict`'s docstring cites `APPROVAL_RECORD-10`, which is not on this branch | advisory; traceability only |

### B5. Gaps, stated plainly

| Id | Action with no record, or a weak record | Severity (QA view) |
|---|---|---|
| G1 | The spawn (INV-5 egress) on the operator path has no program-side record; only the harness transcript | by design (spec section 7); disclose, not a defect |
| G2 | The printed result carries verdict, prompt id and prompt hash but not the model, the input hash, a time or an operator; on the operator path nothing checks the model or tool use (S4) | low; the eval path does check |
| G3 | A refused judge tool call leaves only a hook message in the transcript on the operator path | low |
| G4 | Cleanup silently skips a symlink `reply.txt` (S2) | low |
| G5 | **A void `record` into a stage directory that already holds a valid run leaves the earlier `verdicts.toml`, `diffs.md` and `audit.json` in place** while the new `audit.md` says VOID. I confirmed this with a scratch probe outside the repo (`$S/test_probe_stale.py`, reusing the tests' `world` fixture): files before and after were the same four names, `audit.md` contained `VOID`, `verdicts.toml` still present. No test covers it (`test_record_voids_the_whole_batch` starts from an empty directory). Mitigation in practice: the spec reruns into a fresh batch and `eval --verdicts` binds each verdict to its payload hash; the two committed stage directories are valid runs | low to medium; a stale file could be scored by mistake. Not blocking for this slice (no further `record` is planned) |
| G6 | An `ApplyError` inside `record` leaves no `audit.md` for that attempt (stderr `error:` only) | low (R only) |
| G7 | `diffs.md` stores the full, uncapped model reply for differing and errored rows and is committed. I did not open the stage `diffs.md` files (brief), so I cannot say what they hold | low; deliberate, but a reviewer should read it before any publication |
| G8 | A non-domain exception in `judge-apply` ends in a traceback with exit 1, no fixed category (R only) | low |
| G9 | Context drift (what the harness attaches) is visible on the eval path (peak per spawn via `check-transcripts`/`audit.md`) and not at all on the operator path | low; INV-5 already says the list is incomplete and may change |

### Part (b) verdict: **PASS WITH GAPS**

Every automated action of the judge step has either a record (printed line, stderr category, run file) or a stated reason it has none, and all eleven judge-error categories, the transport cleanup on every exit path, the hash binding, the deciding-signal lines and the audit/void rules in `record` are exercised by named tests that pass (207 passed). The gaps are G1 to G9 above. None breaks INV-1, INV-4 or INV-5, and none is a missing record for an action that sends data. G5 is the one defect-like item: a stale-file hazard in an eval-only tool, confirmed by a probe, untested. G1 and G2 are design choices that should be disclosed to the owner as the reason there is no operator-path log.

## Summary

| Item | Verdict |
|---|---|
| (a) Dry run on a fixture | **PASS** (11 of 11 criteria; 19 `judge-apply` runs and 3 `eval --verdicts` variants; offline, under an OS-level network deny; no model) |
| (b) Audit event coverage | **PASS WITH GAPS** (G1 to G9; S1 to S4, S7, S8 noted) |

- Commands that could not be run: `uv run pytest -m model` (the `--self-check` and sample-derivation tests; about 50 s, not needed for these two items), `judge_run record` against real transcripts (none are available offline and it is outside the brief), the stage `diffs.md` files (not opened, per brief).
- Left behind by me: nothing in the repo except this file. Scratch files are in `$S`, outside the repo. `.aveto-judge/` is empty. A probe test for G5 was not added to `tests/` (QA does not edit code); if the owner wants G5 closed, the guard is: run `record` valid then void into one directory and assert `verdicts.toml`, `diffs.md` and `audit.json` are gone (or the void run refuses), and prove it fails without the fix.
- Nothing was approved, pushed or committed by this stage; `STATE.md` was not edited.
