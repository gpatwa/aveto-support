# 05a-smoke — STOPPED, smoke did not run

Result: **smoke not passed. No judge spawn happened. Stage 5 not started.**

## Part A step 1 (confirmed)
- `aveto-answerability-judge` is in the offered agent list of this session.
- Its agent file (`.claude/agents/aveto-answerability-judge.md`) has `model: claude-sonnet-5-5`, and `disallowedTools` names `DesignSync, ListPlugins, ListSkills, SearchPlugins, SearchSkills, SuggestPluginInstall, SuggestSkills` before `mcp__*`. (The agent list shows tools, not the model; the model is from the file.)

## Part A step 2 (what happened)
- `/aveto-judge-seen r049` was invoked once through the Skill tool.
- It failed before any spawn with: `Shell command permission check failed for pattern "!`uv run -q --project <worktree> python <worktree>/.claude/skills/aveto-judge-seen/seen_payload.py 'r049'`": This command requires approval`.
- The skill's `!`-injection of the helper command was not auto-allowed in this session's permission settings. That is a skill error / unpredicted permission requirement (R6 point 1). Not retried.

## Steps 3 and 4
- Not done: there is no judge transcript to check, and no first request to measure context from. Offered tools, `tool_use` count, base-dir length, reply, parse, requests, peak, in-equivalent and the INV-5 context comparison are all unmeasured.

## For the owner
- Needs a permission rule (or an approval) that lets the helper command run, e.g. an allow entry for `uv run -q --project <worktree> python <worktree>/.claude/skills/aveto-judge-seen/seen_payload.py *`. I did not edit settings (outside this request's file list).
- Then a new fresh session is needed; this one has used its smoke allowance on a failed attempt (no spawn affected, so R6 point 4 continuation may apply).
