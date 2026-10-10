# 02d — Claude Code facts read from the official docs by the Orchestrator (2026-10-10)

Advice-grade facts, not approvals. Sources: https://code.claude.com/docs/en/tools-reference and https://code.claude.com/docs/en/skills, fetched via WebFetch (the answers are produced by a small model summarising the page; quotes below are from the saved page text for the tools reference; the skills page was read through its first 100,000 of 106,609 characters). They settle the Architect's 'from memory' deny list and add two findings the addendum missed.

## Built-in tool names (tools reference table, exact strings)
Agent Artifact AskUserQuestion Bash CronCreate CronDelete CronList Edit EndConversation EnterPlanMode EnterWorktree ExitPlanMode ExitWorktree Glob Grep LSP ListAgents ListMcpResourcesTool Monitor NotebookEdit PowerShell PushNotification Read ReadMcpResourceTool RemoteTrigger ReportFindings ScheduleWakeup SendFeedback SendMessage SendUserFile ShareOnboardingGuide Skill SubagentHandback TaskCreate TaskGet TaskList TaskOutput TaskStop TaskUpdate TodoWrite ToolSearch WaitForMcpServers WebFetch WebSearch Workflow Write 

Plus MCP tools, named `mcp__<server>__<tool>`; whether `disallowedTools` accepts an `mcp__*` wildcard in frontmatter is NOT stated in what was read (unverified). The tools reference says deny rules in *permission rules* can use `"*"` to remove every tool, but whether `disallowedTools: ["*"]` is accepted in subagent frontmatter was not found (unverified).

## Two tools a deny list cannot remove (new; the addendum did not account for them)
1. **`EndConversation`**: "PreToolUse hooks don't run for it ... neither --disallowedTools nor a --tools list can remove it" (it does nothing but end the conversation). Harmless to the judge's job but it is a tool the judge keeps unless every other tool is removed by a matching `"*"` rule.
2. **`SubagentHandback`**: "Delivers a subagent's final report to whichever conversation receives that subagent's result. Provided only in auto mode ..." and "Claude Code also gives the subagent that tool, even if you leave it out of tools or list it in disallowedTools." So in auto mode the judge still has the tool that returns its verdict. A match-all exit-2 PreToolUse hook might block it, which would stop the verdict ever arriving (a fail-closed `judge error`, but an unusable judge). **The refusal probe must show what happens**: the judge's normal reply must still reach the session, and a probe record must say whether SubagentHandback appeared and whether the hook fired on it.

## Skills (owner change, record 7)
- Project skill location: `.claude/skills/<name>/SKILL.md`. Arguments via `$ARGUMENTS` (appended as `ARGUMENTS: <value>` if no placeholder).
- `disable-model-invocation: true`: "prevent[s] Claude from automatically loading this skill ... trigger manually with /name"; the user can still invoke it; it also stops preloading into subagents and, from v2.1.196, a scheduled task firing with it as the prompt.
- Custom commands are merged into skills; if a skill and a `.claude/commands/` file share a name the skill wins.
- Subagent tool inheritance: neither field set inherits every available tool; `tools` only = those; `disallowedTools` only = all but those; both = disallowed wins. If every `tools` entry fails to match, the Agent tool "usually returns an error naming the entries instead of launching the subagent".
