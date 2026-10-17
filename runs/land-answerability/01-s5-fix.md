# Stage 1: S5 fix (aveto-judge-seen)

## What changed
- SKILL.md: the `!` line is now fixed (`uv run -q --project "${CLAUDE_PROJECT_DIR}" python "${CLAUDE_SKILL_DIR}/seen_payload.py"`): no `$ARGUMENTS`, no quote. `allowed-tools` lost its trailing ` *`, so it matches only that command.
- seen_payload.py: takes no argv (any argv is refused with a fixed line, exit 2). The run id comes from the fixed file `.aveto-judge/seen-id` (gitignored dir), written by the operator. `read_id` refuses a missing file, a symlink, non-ASCII, or over 64 bytes; `prepare` still checks `^r[0-9]{3}$` (fullmatch) and membership in key.toml before any question file is written.

## Why safe
No caller text reaches a shell: the only channel is a file read as data and validated before use. No harness substitution behaviour is relied on. No dependency added.

## Tests (tests/test_judge_seen_skill.py)
21 hostile values (r001+newline removed: the helper accepts one trailing newline by design, covered by test_read_id_accepts_one_trailing_newline) (the `'`, `"`, `$()`, backtick, newline, `;`, `&&`, `|`, empty, 5000-char, unknown ids, etc.) x 3: id-file refusal (no INJECTED, no q/ file); argv refusal via subprocess; rendered shell line unchanged by substitution, run under /bin/sh with a stub `uv`, exactly one fixed call logged. Plus missing/symlink/binary file, trailing-newline acceptance, frontmatter (no `$ARGUMENTS`, no quote, no `*)`).

## Regression
uv run mypy: Success, 24 files. uv run ruff check: All checks passed. uv run pytest: 428 passed, 12 deselected.

## Files changed
.claude/skills/aveto-judge-seen/SKILL.md, .claude/skills/aveto-judge-seen/seen_payload.py, tests/test_judge_seen_skill.py, runs/land-answerability/01-s5-fix.md, runs/land-answerability/STATE.md.
Note: operator usage changes: write the id to `.aveto-judge/seen-id`, then run `/aveto-judge-seen` with no argument.

Follow-up: added test_refuses_wrong_argument_count (any argv refused, fixed line, exit 2, no payload) because .agentic/SAFETY_INVARIANTS.md cites it; every other cited test name still exists in tests/.

Follow-up (R1): refusal tests that call main() now run on a tmp key/batch copy with judge-input's subprocess.run stubbed to fail; each asserts it is never reached. Suite no longer depends on index/ or models/.
