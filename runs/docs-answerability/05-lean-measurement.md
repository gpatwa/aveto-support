# Lean measurement (measurement only; nothing approved; no ceiling change)

One spawn of the untracked scratch agent `aveto-judge-scratch` (deleted after), prompt "Reply with exactly the word: ok", model claude-haiku-5-5. Copies in `probe-transcripts/scratch-measure-ad6c3a04.*`.

## disallowedTools accepts MCP names (all three forms)
Offered tools 141 (probe) -> **110**. Removed exactly 31: 5 exact `mcp__terminal__*` names, wildcard `mcp__Claude_Browser__*` (19), server-only `mcp__ccd_host` (7). The agent launched; no entry was rejected. Untested: bare `mcp__*`.

## Cost
- First (only) request: 57,783 tokens, all cache-write (probe judge: 72,686). Drop 14,903 for 31 tools = about 481 tokens per tool.
- usage.mjs does not list this spawn (not a registered slice stage); figures are from the transcript: peak 57.8k; in-equiv about 72k (cache write at 1.25x, 4 output tokens).
- Probe judge for comparison (usage.mjs): peak 76k, in-equiv 113k.

## Derived (not measured)
- Lean (all 103 remaining MCP tools denied, 7 harness tools kept): first request about 7k; with a 1-2k payload about 8-9k peak, about 11k in-equiv per spawn.
- 93 spawns: lean about 0.8M peak-sum (range 0.65-0.95M), about 1.0M in-equiv. As built today (110 tools): about 5.4M peak-sum, about 6.7M in-equiv. Unchanged agent (141 tools): about 7.1M peak-sum.

## Bare `mcp__*` (one spawn, agent ab5e0b72; scratch agent since deleted)
Copies in `probe-transcripts/scratch-bare-mcp-ab5e0b72.*`. Same prompt, same model.
- prefix.json `toolNames`: **7** offered (DesignSync, ListPlugins, ListSkills, SearchPlugins, SearchSkills, SuggestPluginInstall, SuggestSkills). The bare wildcard is accepted and removes every MCP tool (110 -> 7). Agent launched; reply "ok".
- First (only) request: **11,081 tokens** (11,079 cache-write + 2 input), 4 output. In-equiv about **13.9k** (cache write 1.25x). Measured, not derived: the 7k lean figure above was low by about 4k (system prompt plus 7 deferred-tool schemas).

## Projection, 93 one-question spawns (lean agent; payload 1-2k assumed, not measured)
- Peak per spawn 12.1-13.1k; peak-sum **about 1.17M** (1.13-1.22M). In-equiv about 15.3-16.5k per spawn, about **1.48M** (1.42-1.53M). No cross-spawn cache reads counted (unmeasured; identical prefix may be read at 0.1x inside the 5-minute TTL, which would lower in-equiv only).
- Ledger basis (peak-sum): spent about 759k + stage 4 about 1.17M + stages 5-10 per plan 510k = **about 2.44M**.
