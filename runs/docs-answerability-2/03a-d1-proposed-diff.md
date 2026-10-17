# D1 proposed diff (NOT APPLIED) — docs-answerability-2

Owner decision needed (deny list of a safety control; rule 4). Nothing below has been applied: `.claude/agents/aveto-answerability-judge.md` and `tests/test_judge_artefacts.py` are unchanged in the working tree. Source: tech spec section 10 (D1), stage 1 measurement (the judge is offered exactly these seven harness tools, `tool_use` 0, hook unchanged).

The diff is a standard unified diff (paths `a/` and `b/` from the repo root). To apply after approval: save the fenced block to a file and run `git apply <file>`; to revert, `git apply -R <file>`. A fresh-load session is needed after the agent file changes.

```diff
--- a/.claude/agents/aveto-answerability-judge.md
+++ b/.claude/agents/aveto-answerability-judge.md
@@ -1,7 +1,7 @@
 ---
 name: aveto-answerability-judge
 description: Product-local answerability judge, used only by the /aveto-judge command. Never delegate to it otherwise. Not a pack role.
-disallowedTools: Agent, Task, Bash, Read, Write, Edit, WebFetch, WebSearch, Artifact, AskUserQuestion, CronCreate, CronDelete, CronList, EndConversation, EnterPlanMode, EnterWorktree, ExitPlanMode, ExitWorktree, Glob, Grep, LSP, ListAgents, ListMcpResourcesTool, Monitor, NotebookEdit, PowerShell, PushNotification, ReadMcpResourceTool, RemoteTrigger, ReportFindings, ScheduleWakeup, SendFeedback, SendMessage, SendUserFile, ShareOnboardingGuide, Skill, SubagentHandback, TaskCreate, TaskGet, TaskList, TaskOutput, TaskStop, TaskUpdate, TodoWrite, ToolSearch, WaitForMcpServers, Workflow, mcp__*
+disallowedTools: Agent, Task, Bash, Read, Write, Edit, WebFetch, WebSearch, Artifact, AskUserQuestion, CronCreate, CronDelete, CronList, EndConversation, EnterPlanMode, EnterWorktree, ExitPlanMode, ExitWorktree, Glob, Grep, LSP, ListAgents, ListMcpResourcesTool, Monitor, NotebookEdit, PowerShell, PushNotification, ReadMcpResourceTool, RemoteTrigger, ReportFindings, ScheduleWakeup, SendFeedback, SendMessage, SendUserFile, ShareOnboardingGuide, Skill, SubagentHandback, TaskCreate, TaskGet, TaskList, TaskOutput, TaskStop, TaskUpdate, TodoWrite, ToolSearch, WaitForMcpServers, Workflow, DesignSync, ListPlugins, ListSkills, SearchPlugins, SearchSkills, SuggestPluginInstall, SuggestSkills, mcp__*
 model: claude-sonnet-5-5
 hooks:
   PreToolUse:
--- a/tests/test_judge_artefacts.py
+++ b/tests/test_judge_artefacts.py
@@ -34,7 +34,9 @@
     "NotebookEdit, PowerShell, PushNotification, ReadMcpResourceTool, RemoteTrigger, "
     "ReportFindings, ScheduleWakeup, SendFeedback, SendMessage, SendUserFile, "
     "ShareOnboardingGuide, Skill, SubagentHandback, TaskCreate, TaskGet, TaskList, "
-    "TaskOutput, TaskStop, TaskUpdate, TodoWrite, ToolSearch, WaitForMcpServers, Workflow, mcp__*"
+    "TaskOutput, TaskStop, TaskUpdate, TodoWrite, ToolSearch, WaitForMcpServers, Workflow, "
+    "DesignSync, ListPlugins, ListSkills, SearchPlugins, SearchSkills, SuggestPluginInstall, "
+    "SuggestSkills, mcp__*"
 )
 HOOK_COMMAND = 'echo "aveto-answerability-judge has no tools" >&2; exit 2'
 FRONTMATTER = f"""---
```

## What each part does and what each test asserts

Agent file: the seven names go into `disallowedTools` immediately before `mcp__*`, so the list still ends in `mcp__*`; no `tools:` key is added, `model: claude-sonnet-5-5`, the match-all deny hook and the prompt are unchanged. Effect: layer (a) (the deny list) then covers every tool the harness offered the judge, so the hook becomes a true second layer; the measured cost is about 6.9k fewer tokens per spawn (chars/4 estimate). `DENY_LIST` in `tests/test_judge_artefacts.py` is the byte-for-byte pin: `test_agent_definition` rebuilds the whole frontmatter from `DENY_LIST` and requires the agent file to equal it (plus the prompt body, no `tools:` key, the pinned model, `Agent` and `Task` named, names unique), and `test_deny_hook_refuses_every_input` runs the hook on every name in `DENY_LIST` (now seven more) and must still refuse each with exit 2. Both tests fail if only one of the two hunks is applied, which is intended. Change in the audit's expected tool count: without D1 the registered `expect_tools` is the seven names exactly as measured (offered 7, `record` voids a batch whose spawns show anything else); with D1 applied it is `()` (offered 0, `--expect-tools none`), and a spawn that still shows 7 offered tools then voids the batch. The smoke spawn (`r049`) is what confirms the offered count after the owner's decision and a fresh-load session; if the zero-tool agent returns no reply or the harness rejects the list, the run stops and goes back to the owner.
