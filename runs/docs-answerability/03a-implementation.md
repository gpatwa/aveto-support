# Implementation 3a — docs-answerability (AI Engineer, standard depth)

Scope: spec 7.1 files 1-8 only. Files 9-11 (agent definition, command, artefact test) not created. No SAFETY_INVARIANTS, README, ARCHITECTURE, CURRENT_MVP_STATUS or ADR edits. Not committed; changes are in the working tree. No judge call of any kind, no credentials, no `claude -p`, no `-m model` / `-m network` run. No eval file and no fifth set read (synthetic fixtures only).

## 1. What was built, per file

| # | File | Change |
|---|------|--------|
| 1 | `aveto_support/__main__.py` | M. Docstring now lists the exit codes incl. 4. New subcommands `judge-input`, `judge-apply`; `eval --verdicts`. New helpers `_with_searcher`, `_raw_question`, `_judge_input`, `_apply_verdict`, `_judge_apply`. `--verdicts` with a non-`file-rrf-v1` ranking raises before any output (exit 2). The verdicts section is built before anything is printed, then appended after the unchanged report; exit code stays `0 if report_eval.passed else 1`. New error types mapped to exit 2. Existing code untouched apart from the argparse additions and these insertions. |
| 2 | `aveto_support/judge.py` | A. `BLOCK_ID`, `PROMPT_ID`, `PROMPT_SHA256`, `TRANSPORT_DIR`; `normalise_question`, `read_question_file`, `retrieve_for_judge`, `format_judge_input` (marker check, full passage text), `input_sha256`, `parse_verdict` (grammar 4.1), `render_applied`, `signal_line`, `transport_file` / `read_reply` / `delete_transport_files` / `remove_stale_reply`; errors `QuestionFormatError`, `PayloadMarkerError`, `TransportError`, `JudgeError(category)`; `Verdict(token)` carries the token only. |
| 3 | `aveto_support/judge_eval.py` | A. `load_verdicts` (exact keys, exact format and prompt hash, one entry per eval id, hash recomputed), `score_verdicts`, `right_file_rank`, `bar_met`, `format_judge_section`, `judge_section`. Reads no `false_premise` key. |
| 4 | `prompts/answerability-judge-v1.txt` | A. Extracted, not retyped: `sed -n 104p` of the pilot doc @ 00d491a, first and last `"` stripped, one `\n`. `shasum -a 256` = `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427`, equal to the Orchestrator's value and to `judge.PROMPT_SHA256`. One line plus one newline. |
| 5 | `tests/test_judge.py` | A. 72 tests (parametrised). |
| 6 | `tests/test_judge_eval.py` | A. 19 tests (parametrised). Imports shared helpers from `test_judge`. |
| 7 | `.gitignore` | M. `.aveto-judge/`. |
| 8 | `.agentic/LOCAL_COMMANDS.md` | M. Three rows (judge-input, judge-apply, eval --verdicts), exit code 4 and the new exit-2 causes. |

Design notes: the program neither networks nor starts a process (no `subprocess`, no SDK). Judge-apply order is: validate the verdict path, read the reply (4,096-byte cap, strict UTF-8, `O_NOFOLLOW`), normalise and retrieve, check the hash, parse, render, then delete the transport files, then print. Deletion runs on every path once arguments have parsed (including the exit-2 paths, which re-raise after deletion). A deletion failure prints `judge error` / `judge error: transport file not deleted`, exit 4, and prints no judged result.

## 2. Tests and what each proves

`tests/test_judge.py`
- `test_judge_input_layout_exact`: golden bytes of the payload for a two-file index (markers, blank lines, `(top of file)`, final `\n`).
- `test_judge_input_full_text_not_excerpt`: a passage with more than 3 lines and a 200-character line appears whole; no excerpt prefix, no `…`.
- `test_judge_input_matches_retrieve_selection`: same files, passages, line ranges, order as `retrieve`.
- `test_judge_input_has_no_scores_urls_labels`: no score, URL, commit, repo, ranking, `Sources for`, `Docs:`, closing sentence, verdict word.
- `test_judge_input_deterministic_and_hash_on_stderr`: identical bytes twice; stderr is exactly `input sha256: <sha256 of stdout>`.
- `test_question_normalised`, `test_question_controls_rejected` (RLO, ZWSP, NUL, ESC, empty, whitespace only), `test_question_file_limits` (over 4,096 bytes, not UTF-8, missing), `test_question_sources_exclusive`.
- `test_passage_marker_collision_refused` (3 marker forms): exit 2, message has path and line range, not the passage text.
- `test_judge_input_removes_stale_reply_only`: only `.aveto-judge/reply.txt` removed; neighbours, an outside `reply.txt` and a symlink target untouched.
- `test_parse_verdict_table`: 26 reply shapes to token or exact category.
- `test_verdict_carries_only_the_token`, `test_reason_never_leaves_parser`: a sentinel in the reason is absent from stdout, stderr and every file under the test directory.
- `test_apply_answerable_is_retrieve_plus_signal`: stdout is `retrieve`'s stdout plus the exact signal line. `test_apply_not_answerable_exact`: the two exact lines, no path, URL or question. `test_apply_positional_question_works`.
- `test_apply_judge_error_shows_nothing` (9 cases), `test_apply_exactly_4096_bytes_is_not_too_long`, `test_apply_missing_verdict_file`: stdout exactly `judge error\n`, stderr exactly `judge error: <category>\n`, exit 4, transport files gone.
- `test_apply_hash_mismatch` (other question, zero hash, upper-case hash), `test_apply_after_reingest_is_refused`.
- `test_apply_outside_transport_dir_untouched`: a path outside, a symlink inside pointing outside, a sibling directory: not read, not deleted; an outside question file is read but never deleted.
- `test_apply_deletes_transport_files_every_path`: success, judge error, bad question (exit 2), missing index (exit 2). `test_apply_deletion_failure_is_judge_error` (row 14).
- `test_apply_requires_verdict_and_hash`: either flag missing is exit 2 and deletes nothing.
- `test_unjudged_outputs_never_look_judged`: `retrieve` and plain `eval` contain none of `deciding signal`, `judge`, `no confident match`.
- `test_program_offline_no_model`: with the autouse network block plus `subprocess.Popen`, `os.system`, `os.posix_spawn(p)`, `os.execv/execve/execvp`, `os.fork` patched to raise, runs `retrieve`, `eval`, `eval --verdicts`, `judge-input`, `judge-apply` (both verdicts and a judge error).
- `test_judge_modules_import_allow_list` (3 modules): AST walk finds only the spec's allow-list and `aveto_support.*`.
- `test_prompt_file_hash_pinned`: file sha256 == `judge.PROMPT_SHA256` == the approved literal; one line, no BOM, starts as expected.

`tests/test_judge_eval.py`
- `test_eval_without_verdicts_unchanged`: stdout and exit code equal what the frozen `format_report` / `score` produce; no judge text. Also checked once outside the suite (section 3).
- `test_eval_verdicts_exit_code_is_retrieval_gate`: gate fails with both bars met gives exit 1; gate passes with both bars not met gives exit 0.
- `test_eval_verdicts_appends_after_unchanged_report`: the plain report is a prefix of the verdicts run; same exit code.
- `test_verdicts_loader_rejects` (9 cases): wrong format, wrong prompt hash, missing id (names the id), duplicate id, id not in set, a `reason` key, token outside the three, input hash mismatch (names the id), extra top-level key. Each is exit 2 with empty stdout.
- `test_verdicts_file_unreadable_or_not_toml`, `test_verdicts_requires_default_ranking`, `test_load_verdicts_direct_error_type`.
- `test_bars_arithmetic` (4/5 met, 3/4 not, 0 total not, 16/20 and 45/56 met, 44/56 not; JUDGE_ERROR fails both bars), `test_missing_right_file_is_not_scored_on_bar_2`.
- `test_hit_matches_evaluate_score`: per question, `right_file_rank is not None` equals `evaluate.score`'s HIT, including a rank-3 source.
- `test_bars_line_fixed_format`: the `bars:` line parses with one regex; the per-question and bar lines are pinned literally.

## 3. Regression output (real)

```
$ uv sync --locked && uv run mypy && uv run ruff check && uv run pytest
Resolved 18 packages in 10ms
Audited 16 packages in 0.44ms
Success: no issues found in 19 source files
All checks passed!
...
tests/test_judge.py .................................................... [ 59%]
....................                                                     [ 67%]
tests/test_judge_eval.py ...................                             [ 74%]
tests/test_rerank.py .............................                       [ 85%]
tests/test_search.py .....................................               [100%]

====================== 259 passed, 10 deselected in 7.81s ======================
```
(`uv sync` output abbreviated to its last lines.) 91 of the 259 are new. `git status` shows `search.py`, `evaluate.py`, `index.py`, `embed.py`, `ingest.py`, `rerank.py` and `conftest.py` unmodified.

Output equivalence checked once by script (not a committed test): `git show HEAD:aveto_support/__main__.py` run against the new `__main__` on the same synthetic index: `eval` (stdout and exit code 1) and `retrieve` (stdout, exit 0) are byte-identical.

Prompt hash verified by me: `shasum -a 256 prompts/answerability-judge-v1.txt` = `24b244d2...a159427`, equal to the required literal.

## 4. Non-vacuity (break, confirm fail, restore)

All restored; no `.bak` files left. Each mutation failed the test(s) named:
1. Control/format characters no longer detected: question and parser tests fail.
2. Two-token check removed: parse table fails.
3. Passage text cut in the payload: layout and full-text tests fail.
4. Marker check disabled: collision test fails.
5. Symlink check removed in `transport_file`: outside/symlink test fails.
6. `delete_transport_files` without the safe-path check: outside-untouched test fails.
7. Hash check removed in judge-apply: hash mismatch test fails.
8. Re-raising a pending exit-2 error before deletion: every-path deletion test fails.
9. Stale-reply removal removed from judge-input: stale-reply test fails.
10. ANSWERABLE output without the signal line: fails. `PROMPT_SHA256` altered: pinned-hash test fails.
11. Raw verdict-file path echoed in the judge-error stderr: error-shape tests fail.
12. Question file no longer deleted: fails.
13. `os.system(...)` and `import subprocess` added to the judge-input path: offline test and the import allow-list both fail.
14. JUDGE_ERROR scored as a correct answer: bars test fails. Bar threshold `>=` changed to `>`: fails. Hash check removed in the verdicts loader: loader test fails. Extra-key rejection loosened: loader test fails. `eval` exit code made constant 0: exit-code test fails. Ranking guard disabled: ranking test fails. Extra text appended to plain `eval`: unchanged-eval test fails. A `Deciding signal` string added to `retrieve`'s output: `test_unjudged_outputs_never_look_judged` fails.
15. Hit rule restricted to rank 1: survived at first (all fixtures hit at rank 1); I added a rank-3 question (`test_hit_matches_evaluate_score`) and the mutation is now killed.

Not mutation-checked: the `bars:` line format test (it pins literals, so any change fails by construction); the per-case wording of every 4.2 row; the 4,096-byte reply boundary beyond the two tests that bracket it.

## 5. Deviations from the spec

1. **Spec 4.2 row 11 vs grammar 4.1.** Row 11 lists `**Q1 ANSWERABLE**` and `` `Q1 ANSWERABLE` `` as `wrong block id`. The ordered grammar (step 4 before step 5) classifies them as `malformed verdict line` (the markdown is glued to the id or the token). I followed the grammar; both are judge error, exit 4. Tests pin the grammar's category. `Q2 ANSWERABLE` and `q1 NOT_ANSWERABLE` are `wrong block id`.
2. **Payload end.** The spec's layout sketch is ambiguous about the blank line before `=== end Q1 ===`. I put one blank line after every passage's end marker, including the last (consistent with the stated rule). Pinned by the golden test. The seen-set check validates the layout anyway (spec 8.11).
3. **Passage order inside a file is retrieval's** (in the golden fixture the top-of-file passage ranks before the headed one). The payload follows `retrieve` exactly, as the spec requires.
4. **Small duplication in `__main__.py`.** `_with_searcher` repeats about eight lines of the existing index/embedder load-and-close logic instead of refactoring `_dispatch` (scope: no refactor mixed in). It builds only the default-ranking `Searcher`, never a reranker.
5. **`except Exception` in `_judge_apply`** carries `# noqa: BLE001`: it exists to delete the transport files before re-raising the original exception.
6. **Extra strictness:** `load_verdicts` rejects unknown top-level keys (spec lists only the per-entry rule). `QuestionError` from `retrieve` (for example a question with no searchable words) is mapped to `QuestionFormatError`, exit 2, in the judge commands only.
7. **`judge-input` exclusivity error** is raised after argument parsing (message `give exactly one of --question-file or the question words`, exit 2) rather than by argparse itself; same exit code. For `judge-apply` that check runs inside the cleanup scope, so transport files are still deleted.
8. **Normalised question in the ANSWERABLE output.** `render_applied` prints `retrieve`'s format for the normalised question, so for a question with irregular whitespace the `Sources for:` line differs from plain `retrieve` (which joins argv without normalising). Identical for ordinary questions (tested).
9. **`test_prompt_file_hash_pinned` is in `tests/test_judge.py`**, per the brief, although spec 6.4 assigns the hash test to 3b's file. 3b's `test_prompt_file_hash` can duplicate or drop it.
10. Ruff's autofix once rewrote `‮` escapes in the tests into literal characters; I replaced them with `\N{RIGHT-TO-LEFT OVERRIDE}` (the sources now contain no hidden characters, checked with a non-ASCII grep: only `…` remains).

## 6. Unverified or left open

- No real run: the payload layout has not been seen against the real corpus (index not built here; no `ingest`, no `retrieve` on real docs). `PayloadMarkerError` on the real corpus is a seen-set-check finding.
- `.aveto-judge/` resolves against the working directory (spec 8.21); the tests `chdir` into a temp dir.
- Symlink/race handling in `transport_file` is checked-then-used (an `O_NOFOLLOW` open for the read, but deletion re-checks then unlinks); a concurrent swap between the check and `unlink` is not defended. For Security.
- Whether a session can be made to skip the judge, paste drift, the zero-tool definition, the model pin: 3b and the seen-set check, as the spec says. Nothing in 3a assumes the `haiku` alias or any model ID.
- `.agentic/LOCAL_COMMANDS.md` says "Only commands that have been run are listed": the three new rows are exercised by the tests, not run against real docs.
- The `judge: verdicts <path>` header prints the path as given on the command line.
