# 05a-smoke — spawn ran and was audited; smoke NOT passed on one item (context). Stage 5 not started.

Session: 743bfcfe-0d5e-42db-86a8-92e094551951 (desktop app, this worktree). Subagents dir: `~/.claude/projects/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-docs-answerability-2/743bfcfe-0d5e-42db-86a8-92e094551951/subagents/`. One judge spawn (`/aveto-judge-seen r049`), no retry. The earlier terminal attempt spawned nothing, so 48 of the 49 allowed spawns remain.

Setup: owner-specified rule `Bash(uv run -q --project * python * seen_payload.py *)` written to `.claude/settings.local.json` (gitignored, not committed). Nothing else in settings.

## Part A step 1 (agent file)
`aveto-answerability-judge` is in the offered agent list; the agent file has `model: claude-sonnet-5-5` and the seven harness tools named in `disallowedTools` before `mcp__*` (checked in the earlier attempt; file unchanged since).

## Part A step 3 (`check-transcripts`)
| Item | Expected | Seen |
|---|---|---|
| agent type | aveto-answerability-judge | aveto-answerability-judge |
| model as logged | claude-sonnet-5-5 | claude-sonnet-5-5 |
| offered tools | 0 | **0** (`toolNames: []`) |
| `tool_use` count | 0 | **0** |
| base-dir line length | 137 (layout ok) | **137**, layout ok |
| reply present | yes | yes (107 chars) |
| reply parses | yes | parses (token not recorded here) |
| requests | | 1 |
| peak | | 7,784 |
| in-equivalent | | 9,716 |
| payload sha16 | | 01e660d80cf84cf4 |

## Part A step 4 (context the judge received besides the payload, from its first request)
First request outline: user message = system_reminder 6,268 chars + user_context 1,481 chars + payload 9,323 chars (base-dir line + payload); system block 2,176 chars (94-char harness cliPrefix + 1,844-char fixed judge prompt + small parts). Tool schemas: none offered.

| Item | ~Size | Named in INV-5? |
|---|---|---|
| Judge fixed system prompt | 1.8k chars | yes ("the judge's fixed system prompt") |
| Harness cliPrefix line ("You are Claude Code...") | 94 chars | harness's own text, not session context; INV-5 says what the harness sends for its own purposes is outside the invariant |
| `CLAUDE.md` | 300 chars | yes (path is the worktree's, not the main checkout's; INV-5 says a different checkout sends different text) |
| `AGENTS.md` | 5.3k chars | yes (same note) |
| User email | 267 chars | yes |
| Git status block: branch, main branch, git user, working-tree status (`?? runs/docs-answerability-2/judge-check/q/`), 5 commit subjects | 855 chars | yes (branch, user, status, five subjects); the "Main branch" line is part of that block |
| Environment: working directory, platform, shell, scratchpad path | ~0.5k chars | yes |
| Environment: **OS version (`Darwin 25.3.0`)** and `isWorktree` / `isGitRepo` flags | ~40 chars | **NO.** INV-5's environment list is "working directory, platform, shell, scratchpad path, model ID, date and organisation ID". OS version and the two flags are not in it |
| Model ID and name, knowledge cutoff | ~130 chars | yes (model ID) |
| Date | 38 chars | yes |
| Organisation ID | ~90 chars | yes |
| Base-dir line (skill path) | 137 chars | yes (INV-5 names the line) |

Of the roughly 2.7k tokens INV-5 already says it did not itemise, nothing further was found besides the row marked NO.

## Result
Smoke criteria 1 to 5 met (launched on claude-sonnet-5-5; offered tools 0; `tool_use` 0; base line 137; reply present). Criterion 6 (every context item named in INV-5) **not met**: OS version and the `isWorktree`/`isGitRepo` flags are sent and not named. Per SESSION_REQUEST-2 this goes to the owner and stage 5 does not start. No reply text or verdict is copied here.

## For the owner
Either approve a wording change to INV-5 (rule 4, owner's own words) that adds "OS version" to the environment list, or tell this session to proceed as-is. This session does neither and approves nothing. The allowance left is 48 spawns.
