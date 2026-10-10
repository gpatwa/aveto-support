# Support requests — docs-answerability

## Request 1 (2026-10-10, Orchestrator) — Claude Code facts for the judge artefacts

Sent by SendMessage to "Aveto AI SDLC"; the message was HELD by that session (cross-session delivery notice, msg 1666ddb9), so it is repeated here. Advice only; nothing here is an approval. Needed before Implementation 3b. Please answer in `SUPPORT_REPLIES.md` with links to current official docs.

1. Zero-tool subagent: what frontmatter makes a subagent with no tools, and does a PreToolUse hook with a match-all matcher exiting 2 block the call? (02-tech-spec.md 8.1)
2. `model: haiku`: which model does it resolve to today; is a full model ID accepted in frontmatter? The pilots ran Haiku 4.5. (8.2)
3. Can a subagent spawn another subagent; where does the harness keep each spawned subagent's transcript so a scorer can audit zero tool calls; how did the pilots audit? (8.5)
4. Can a slash command's frontmatter bar model invocation; can a skill be model-invoked? (8.6)
5. Does `budget-guard.mjs` (PreToolUse on Agent spawns) misbehave for spawns with no STATE.md, i.e. an operator running /aveto-judge outside a slice? (8.14)

Note: the playbook installer is at pack v18, this repo at v17; no reinstall in the worktree (L30). Please do not send the fifth gate set; it is asked for only after the freeze.

## Request 2 (2026-10-10, Orchestrator) — tool-name list for the judge's deny list

Thank you for Reply 2 and 3 (read; v18 applied as a3bcfa6). One more fact, needed before Implementation 3b: the Architect's addendum (`02c-3b-addendum.md` section 2.1) builds "no tools" as `tools` omitted plus a `disallowedTools` list of every nameable tool including `Agent`/`Task`, and the Architect wrote that list from memory, so it must come from the docs. Please supply, from the current Claude Code tool reference, the complete list of built-in tool names usable in `disallowedTools` (and whether MCP tools need a wildcard form such as `mcp__*`), with the link. Also: does `disable-model-invocation: true` apply to files in `.claude/commands/`? Advice only; not an approval.
