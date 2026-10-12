# 03d: seen-set driver skill (Reply 5 D1-D4, D8)

Role: AI Engineer. No judge was run, no Agent spawned.

## Built
- `.claude/skills/aveto-judge-seen/SKILL.md`: frontmatter `name`, `description`, `context: fork`, `agent: aveto-answerability-judge`, `background: false`, `allowed-tools: Bash(uv run -q --project * python ${CLAUDE_SKILL_DIR}/seen_payload.py *)`. No `model`, no `disable-model-invocation`. Body is one line: the `!` injection of `seen_payload.py '$ARGUMENTS'`.
- `.claude/skills/aveto-judge-seen/seen_payload.py`: validates `fullmatch ^r[0-9]{3}$` and membership in `key.toml` (table names only), takes the question from the `batch-<n>.txt` line (id stripped), writes `seen-check/q/<id>.txt`, runs `judge-input --question-file` with stderr discarded, prints stdout bytes unchanged. Any refusal prints one `refused: ...` line and exits 2.
- `runs/docs-answerability/seen-check/DRIVER.md`: the driver recipe, including the sha step `judge-input --question-file <q file> >/dev/null`.
- `tests/test_judge_seen_skill.py` (21 tests). `tests/test_judge_artefacts.py` unchanged (it pins only `/aveto-judge`).

## Docs relied on (fetched 2026-10-10 from code.claude.com/docs/en/skills.md and tools-reference.md)
- "Claude Code starts a new subagent of the type set in the `agent` field and gives it the skill content as its prompt."
- "`agent` ... Which subagent type to use when `context: fork` is set." "any custom subagent from `.claude/agents/`".
- "The `!`<command>` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder." Recognized only at line start or after whitespace.
- "with the default `bash` shell, Claude Code merges stderr into stdout" (hence stderr discarded in the helper; judge-input's sha line would otherwise enter the payload).
- "A failed command aborts the entire skill invocation ... Claude never sees the skill content" (hence refusals exit 2: no judge starts).
- Injected commands are permission-checked and abort unless allowed; "pre-approve it with `allowed-tools`".
- Ceiling: tools-reference "Output limits": valid result "Inline up to roughly 30,000 characters by default; past that, the path of a file ... plus a preview of up to the first 2,000 characters". Tests use 30000.

## Results
- Largest payload of the 93: r072, 20,674 characters (below 30,000). No truncation needed.
- Refusals tested: empty, short/long ids, case, trailing space/newline, `;`, `$()`, backticks, `&&`, `|`, `../`, free text, wrong arg count, id absent from key (no q file written).
- `uv run mypy`: clean. `uv run pytest`: 287 passed, 11 deselected. `uv run pytest -m model`: the new payload-size test passes; 4 failures, all `tests/test_rerank.py` (reranker files not cached; unrelated). `uv run ruff check`: my files clean; 3 errors remain, all in the untracked `seen-check/key/prepare.py` (pre-existing, not mine; `uv run ruff check` as a whole is therefore not green).
- The payload test is marked `model` (needs the embedding cache and the index), so the default run skips it.

## Not verified (cannot be without a spawn) and residuals
1. The live fork was not run: that the forked judge receives exactly the helper's stdout, that `allowed-tools` pattern matches the quoted command line (else the invocation aborts, which is fail closed), and whether Claude Code trims a trailing newline of the injected text (the sha is of judge-input's stdout). The first real use is the D8 test.
2. `$ARGUMENTS` is substituted textually into the command line. The docs describe no escaping. I single-quote it; the helper refuses anything but a bare id, but an argument containing a single quote could break out of the quoting before the helper runs. Mitigation is procedural (only the Orchestrator passes `rNNN`); worth Security's attention (D7).
3. The skill lets the Orchestrator send committed seen-set data to the judge (D3).
