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
