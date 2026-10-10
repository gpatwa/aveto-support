# 03b Implementation: the judge artefacts (AI Engineer, standard depth)

Built from spec 3.3/3.4/6.4 as replaced by addendum 7.1-7.3 and amended by APPROVAL_RECORD-7. Nothing committed; the judge was not run or spawned, no probe, no credentials.

## Files
- `.claude/agents/aveto-answerability-judge.md`: frontmatter keys `name, description, disallowedTools, model, hooks`, no `tools`. `model: claude-haiku-5-5` (full ID). Hook text exactly as addendum 7.1 (match-all `"*"`, exit 2, timeout 10). Body = `prompts/answerability-judge-v1.txt` bytes after one empty line. The description keeps addendum 7.1's text ("the /aveto-judge command") verbatim, though it is now a skill.
- `.claude/skills/aveto-judge/SKILL.md`: `name`, `description`, `disable-model-invocation: true`; no `allowed-tools`, no `model`. Body: the 1.2 steps with `$ARGUMENTS`, rules 1-7 (7 includes "do not pass a `model` parameter"), the addendum-6 budget-guard sentence verbatim, trust and model-pin notes. No `.claude/commands/aveto-judge.md`.
- `tests/test_judge_artefacts.py` (8 tests).

## Deny list (47 names)
Agent, Task, Bash, Read, Write, Edit, WebFetch, WebSearch first, then every other name from the tools reference in 02d-doc-facts.md in its order (not the Architect's from-memory list). `Task` is added as the old spawn name (addendum 2.1); `EndConversation` and `SubagentHandback` are listed for completeness.
- `EndConversation` and `SubagentHandback` cannot be removed by a deny list (02d-doc-facts.md), so listing them withholds nothing. The first is harmless; the second is how the verdict is returned in auto mode, and the probe must show what the hook does to it.
- Unverified, not claimed: that `mcp__*` or `"*"` forms are accepted in `disallowedTools`. Neither is used. MCP tools are covered only by the hook (and the audit).

## Tests and deviations from addendum 7.3
- Agent test pins: frontmatter literal byte for byte (final list written in the test), exact key set without `tools`, body == prompt bytes, `Agent` and `Task` in list, no duplicates, `model: claude-haiku-5-5`, no `model: haiku`, path under `.claude/agents/`.
- Hook test: the command extracted-by-equality from the agent file is run via `/bin/sh` on PreToolUse JSON for all 47 names plus `mcp__probe__fetch`, `Write`, `FutureTool` and an empty name, each with and without `agent_type`, plus malformed JSON, empty stdin and binary junk. All give exit 2, stderr exactly the reason, empty stdout.
- Skill test replaces the command test. Deviation: addendum 7.3 says the body contains none of `claude -p` / `general-purpose`, but rule 2 (which the addendum requires) contains both as prohibitions. The test requires that any line mentioning them says "Never"; `API_KEY` and `--ranking` are banned outright. It also asserts the command file does not exist.
- Prompt hash/shape tests are included (cheap; they are the 6.4 rows), `test_transport_dir_ignored` unchanged.
- **This pytest hook test does NOT satisfy APPROVAL_RECORD-5 Amendment 2 on its own.** It shows the hook command refuses, not that Claude Code runs it for the judge. The live probe (a later QA stage, at most two spawns, must try an `mcp__` tool, and the Release Gate must say whether a live hook refusal was seen) is what satisfies it.

## Verification (offline default)
`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`:
```
Success: no issues found in 20 source files
(ruff check: clean)
tests/test_judge_artefacts.py ........
====================== 267 passed, 10 deselected in 8.32s ======================
```
Non-vacuity (break, confirm fail, restore; restored run: 8 passed):
1. alias `model: haiku` -> test_agent_definition fails
2. hook `exit 0` -> test_agent_definition and test_deny_hook_refuses_every_input fail
3. a `tools:` key added -> test_agent_definition fails
4. a byte appended to the body -> test_agent_definition fails
5. skill gains `allowed-tools` -> test_skill_definition fails
6. rule 7 wording changed -> test_skill_definition fails
7. `.claude/commands/aveto-judge.md` created -> test_skill_definition fails
8. `.gitignore` entry removed -> test_transport_dir_ignored fails
9. `Agent` dropped from deny list -> test_agent_definition fails

## Unverified
- That Claude Code accepts the full model ID and this deny list in frontmatter, that the frontmatter hook fires for the judge, that `disable-model-invocation` works for this skill: all only for the live probe or operator use to show.
- The skill text is for Security review (rule 7, operator notes).
- Not edited: SAFETY_INVARIANTS, README, ARCHITECTURE, ADRs, CURRENT_MVP_STATUS.
