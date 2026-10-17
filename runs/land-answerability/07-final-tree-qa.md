# Stage 8: Final-tree QA (land-answerability)

- Role: QA Evidence (fresh spawn, wrote none of this code). Depth: standard.
- **HEAD:** `e2b228eaf01d9732be54e3268c0ca9265d77f0f9` (branch `claude/land-answerability`); `git status` clean before and after.
- Not done, by the brief: no judge or model spawn, no ingest, no network command, no gate re-run, no code change, no commit, no push.

## 1. Regression, run in order, each separately (output trimmed)

| # | Command | Result |
|---|---------|--------|
| 1 | `uv sync --locked` | `Resolved 18 packages in 18ms` / `Audited 16 packages in 5ms`, exit 0 |
| 2 | `uv run mypy` | `Success: no issues found in 24 source files`, exit 0 |
| 3 | `uv run ruff check` | `All checks passed!`, exit 0 |
| 4 | `uv run pytest` | `425 passed, 12 deselected in 12.12s`, exit 0 |

### Test-count delta (slice 7 baseline 375)
- `tests/test_judge_seen_skill.py` at `bca0e40`: 20 non-model tests (15 parametrized `test_refuses_bad_ids` + `test_ids_match_key`, `test_skill_frontmatter_and_body`, `test_refuses_id_not_in_key`, `test_refuses_wrong_argument_count`, `test_prepare_writes_question_only`).
- At HEAD: 70 non-model tests = `HOSTILE` (21 values) x 3 (`test_refuses_bad_ids`, `test_argv_is_refused_and_runs_nothing`, `test_shell_line_has_no_caller_text`) = 63, plus 7 single tests (`test_ids_match_key`, `test_skill_frontmatter_and_body`, `test_refuses_missing_symlink_and_binary_id_file`, `test_read_id_accepts_one_trailing_newline`, `test_refuses_id_not_in_key`, `test_refuses_wrong_argument_count`, `test_prepare_writes_question_only`).
- Delta +50 = 70 - 20; 375 + 50 = **425**, equal to the observed count. `git diff bca0e40 --stat -- tests` shows this one file only. (Stage 1's 428 had a 22nd hostile value `"r001\n"`, +3; security R1 removed it in `0379f59`, giving 425.) No unexplained count. 12 deselected unchanged (the `model`/`network` marks).

## 2. Checks (a) to (g)

| id | Check | Result |
|----|-------|--------|
| a | `git diff bca0e40 --stat -- aveto_support tools prompts .claude/agents/aveto-answerability-judge.md .claude/skills/aveto-judge` | **Empty.** Method files frozen. |
| b | `.agentic/SAFETY_INVARIANTS.md` vs `git show bca0e40:...` | `diff` rc 0, **identical** (INV-4, INV-5 and the rest unchanged). Only other `.agentic` change since `bca0e40` is `CURRENT_MVP_STATUS.md` (docs T7/T9, Tech Writer stage), not an invariant file. |
| c | Every backticked `test_` name in `SAFETY_INVARIANTS.md` exists in `tests/` | **PASS.** 49 unique names, each found as a `def` (including the four S5-related: `test_ids_match_key`, `test_refuses_bad_ids`, `test_refuses_id_not_in_key`, `test_refuses_wrong_argument_count`). None MISSING. |
| d | `git diff main -- .claude/settings.json` | **Empty.** |
| e | `git status` after the runs | **Clean** (only ignored caches and the gitignored `.claude/settings.local.json`). |
| f | S5 hostile list includes `r101' ; echo INJECTED ; '` | **Yes**, `tests/test_judge_seen_skill.py:113`; passes in all three tests: `test_refuses_bad_ids`, `test_argv_is_refused_and_runs_nothing`, `test_shell_line_has_no_caller_text` (PASSED, verbose run). |
| g | Repeatability and no tracked-file change | `uv run pytest` run three times (once in section 1, twice more): 425 passed, 12 deselected each time, exit 0; `git status --short` empty and `git diff --stat` empty afterwards; no `.aveto-judge/` left behind; HEAD unchanged. |

## 3. Safety invariants
INV-4 and INV-5: text byte-identical to `bca0e40` (b); the tests they cite exist (c) and pass (section 1). The S5 hostile-argument tests cover INV-5's seen-skill qualification. INV-1 and INV-3: no product code changed (a).

## 4. Not verifiable here
- Harness behaviour of the live skill (no harness run, by the brief); Security's A2 reliance stands as advisory.
- No UI in this slice; no preview needed.
- No new test was written, so no non-vacuity break was needed. R1's fix (`0379f59`) was not mutation-tested by this stage.

## 5. Verdict
**GO.** All four regression commands pass on `e2b228e`; the count 425 is explained by the diff; checks (a) to (g) pass; tree clean. Open items carried to the end review are Security's A1 to A4 (A5 addressed by `e2b228e`).
