# 01-measurement — stage 1, two Sonnet judge spawns

> Written by the owner-started session (desktop app, folder = this worktree), 2026-10-12, per `SESSION_REQUEST-1.md`. Data, not an approval. Token sizes marked "~" are characters / 4 and approximate. Reply text is not copied here; hashes only.

## Facts

**Agent check (step 1).** The offered agent list at session start included `aveto-answerability-judge`. `.claude/agents/aveto-answerability-judge.md` pins `model: claude-sonnet-5-5`.

**Spawns.** Exactly two, via `/aveto-judge-seen r001` and `/aveto-judge-seen r002` (forked skill, `requestShape: foreground`, `spawnDepth: 1`). Both completed; no retries and no failures.

| | spawn 1 (r001) | spawn 2 (r002) |
|---|---|---|
| Agent id | `a4e4f19350199713a` | `ad0079ab35b738cbb` |
| Model as logged | `claude-sonnet-5-5` | `claude-sonnet-5-5` |
| Offered tools | 7 (see below) | 7 (same) |
| Tool calls | 0 | 0 |
| API requests | 1 | 1 |
| Input uncached | 2 | 2 |
| Cache write | 14,171 | 6,866 |
| Cache read | 0 | 7,384 |
| First-request tokens | 14,173 | 14,252 |
| Output tokens | 45 | 47 |
| Peak context (input + output) | 14,218 | 14,299 |
| In-equivalent (write 1.25x, read 0.1x, output as counted) | 17,760 | 9,370 |
| Verdict line sha256 (first 16 hex) | `4ac32c3d733fc1ec` | `eeeb7206885f4725` |

In-equivalent arithmetic: spawn 1 = 2 + 14,171×1.25 + 45 = 17,760. Spawn 2 = 2 + 6,866×1.25 + 7,384×0.1 + 47 = 9,370. Spawn 2 got a cache hit on spawn 1's prefix (7,384 tokens, the 5-minute cache), so the second spawn is cheaper in in-equivalent terms and not in peak terms.

**Offered tools (7, not more than 7):** `DesignSync`, `ListPlugins`, `ListSkills`, `SearchPlugins`, `SearchSkills`, `SuggestPluginInstall`, `SuggestSkills`. None was used. The agent's `disallowedTools` list removes the rest, but not these seven. The `PreToolUse` hook (`exit 2`) would have blocked any call. The stop rule (more than 7 offered, or a tool used) was not triggered.

**Harness prefix.** The `cliPrefix` is "You are Claude Code, Anthropic's official CLI for Claude, running within the Claude Agent SDK." — **94 characters, not 150** (the logged first system block length is 94; the second block, the judge's own prompt, is 1,829 characters).

**Tool-use evidence.** Each transcript has one assistant message with a `text` block only (no `tool_use` blocks) and `stop_reason: end_turn`.

**Output.** One line per block, as the prompt asks. The block id is `Q1` (the payload's own label), not the run id.

Sources: `~/.claude/projects/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-docs-answerability-2/f8149669-f933-46b0-b033-db99ac5636ba/subagents/agent-<id>.jsonl` and the matching `.prefix.json` / `.meta.json`.

## Read-only context report (step 4)

What the judge received in its first request besides the question and passages (spawn 1 sizes; spawn 2 within 1–3%):

| Item | Chars | ~Tokens | Notes |
|---|---|---|---|
| Tool schemas (the 7 offered tools) | 27,632 | ~6,900 | Largest block by far. |
| `CLAUDE.md` + `AGENTS.md` text | 5,972 | ~1,500 | Taken from the **main checkout** path (`/Users/gopalpatwa/opt/aveto-support/`), not the worktree. Appears in a 6,190-char system-reminder block. |
| User email + git status | 1,418 | ~350 | Email, current branch, git user, clean status, five recent commit subjects. |
| Environment, model line, date, org uuid | ~1,000 | ~250 | Working directory, platform, shell, scratchpad path, model id, date. |
| Judge's own system prompt (incl. 94-char prefix) | 1,923 | ~480 | The safety text. |
| Skill payload (base-dir line + question + passages) | 7,967 | ~2,000 | r001; r002 is 8,202 chars. This is the part that must be there. |

The listed items add up to about 11.5k of the 14.2k first-request tokens. About 2.7k are not itemized in the transcript (the wire framing, the tool-definition envelope and the like), and I did not guess at them.

**Could it be reduced without touching the safety text?** Probably, yes, but I did not edit anything:
- The seven offered tools are about half of the context and are never usable (the hook blocks them). Adding them to `disallowedTools` in the agent file would drop most of that block. That is an agent-file edit and needs a fresh-load session afterwards.
- `CLAUDE.md`/`AGENTS.md`, the email and the git status are session context the harness adds to every fork. I found no setting in the files read here that removes them. Whether one exists is an open question, not a finding.
- The judge's system prompt (the safety text) is not touched by any of these.

## Projection (peak context summed per spawn, the budget unit)

Mean measured peak per spawn: (14,218 + 14,299) / 2 = **14,259**.

| Stage | Spawns | Peak sum | In-equivalent, warm cache (first spawn cold) | In-equivalent, every spawn cold |
|---|---|---|---|---|
| 5 Sample integration check | 48 | ~684k | ~458k | ~852k |
| 7 Scoring | 48 | ~684k | ~458k | ~852k |

The warm figure assumes 47 spawns at spawn 2's 9,370 plus one at 17,760. Whether the cache stays warm over a long run is not shown by two spawns.

**Effect on the 3.4M ceiling** (figures from `00-slice-plan.md`, unit peak per spawn):
- The plan prices stages 5 and 7 at 800k each (16k per spawn plus overhead), 1.6M together. Measured bare spawns come to ~684k each, ~1.37M together, so the spawn cost alone is about 0.23M under the plan's guess.
- The slice 6 all-in rate was 1.5× the bare per-spawn figure (drivers, QA passes, reruns). Applied here: ~1.03M per stage, ~2.05M together, which is above the plan's 1.6M by ~0.45M. If the stage 5 and 7 lines move, that is a budget question for the owner; this file does not change any figure.
- The measured 14.3k per spawn is 1.1–1.2× slice 6's projected 12.1–13.1k, mostly from the seven offered tools.
- Closing the tool block (above) would cut roughly 6.9k tokens per spawn (about half of peak), and would cut the 48-spawn peak sum by about 0.33M per stage.

## Not done

No files other than this one were written. No judge spawn beyond the two. No approval requested, given or relayed. Nothing pushed.
