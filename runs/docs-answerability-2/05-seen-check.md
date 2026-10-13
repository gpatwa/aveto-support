# 05-seen-check — stage 5 scoring (fresh QA Evidence, depth standard)

Commands run from the worktree root. Flag spellings matched LOCAL_COMMANDS.md; no difference.

## Step 1: record
`uv run python -m tools.judge_run record --subagents-dir ~/.claude/projects/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-docs-answerability-2/743bfcfe-0d5e-42db-86a8-92e094551951/subagents --eval-file runs/docs-answerability-2/judge-check/sample-eval.toml --stage-dir runs/docs-answerability-2/judge-check/stage5 --expect-tools none`

Output: `batch valid; 48 batch spawns` (exit 0). Not void. r049 (smoke) reported apart, not counted.
Written by the tool: `judge-check/stage5/{verdicts.toml,audit.md,diffs.md,audit.json}`.

## Audit (audit.md, deterministic)
- 48 batch spawns r001-r048, one transcript each, none missing, none duplicated. All: agent `aveto-answerability-judge`, model `claude-sonnet-5-5`, offered tools 0, `tool_use` 0, base-dir line 137 with layout ok, payload matched exactly one key question.
- No other agents in the dir. No anomaly found by `record`.
- r049 (smoke, a04), reported apart, not counted: same checks pass (0 offered, 0 tool_use, 137), the tool printed ANSWERABLE, peak 7,784, in-equivalent 9,716.

## Step 2: eval with verdicts
`uv run python -m aveto_support eval --eval-file runs/docs-answerability-2/judge-check/sample-eval.toml --verdicts runs/docs-answerability-2/judge-check/stage5/verdicts.toml`

- Exit code 0. This is the retrieval gate (answerable 28/28, 100.0%, PASS), not the judge result.
- Judge lines as printed: `bar 1 20/20 (100.0%) MET`; `bar 2 24/28 (85.7%) MET`; `judge errors: 0`.

## Step 3: diagnostics
`uv run python -m tools.judge_run diagnostics --eval-file ... --verdicts ... --audit runs/docs-answerability-2/judge-check/stage5/audit.json` (exit 0)

```
best score rule (top1 < 0.67): bar 1 13/20 NOT MET; bar 2 17/28 NOT MET
over-abstention: 4/28 answerable questions with a hit were called NOT_ANSWERABLE (judge errors excluded)
ANSWERABLE without a hit: 0/0
judge errors: 0; bar 1 0 / bar 2 0 / neither 0
judge error categories: none
usage: 48 spawns; peak sum 378,696; in-equivalent sum 439,564
```

## Result against the registered thresholds (R3, stage 5)

| Check | Registered | Seen | Verdict |
|---|---|---|---|
| Bar 1: unanswerable abstained | at least 16 of 20 | 20 of 20 | MET |
| Bar 2: answerable with hit, not abstained | at least 23 of 28 | 24 of 28 | MET |
| Judge errors (own number) | reported | 0 (bar 1 0 / bar 2 0 / neither 0) | n/a |
| **Overall (both MET)** | | | **MET** |

Bar 2 passes with one question of margin (22 would fail). No retune, re-derivation, rescore or re-registration was done.

## Other registered reports (R7)
- Best score rule on the same sample: bar 1 13/20 NOT MET, bar 2 17/28 NOT MET (reproduces the self-check's 13/20 on U; the rule fails both bars).
- Over-abstention: 4/28 (judge errors excluded; none).
- ANSWERABLE without a hit: 0/0 (the sample has no such question, as R5 says).
- Verdicts differing from the key: 4, all answerable-with-hit called NOT_ANSWERABLE: r003 (a07), r006 (a15), r008 (a20), r021 (h12). Reply text stays in `runs/docs-answerability-2/judge-check/stage5/diffs.md` only (not copied here, per A1). No unanswerable question differed.
- Usage, from the tool's transcript read: 48 counted spawns, peak sum 378,696, in-equivalent sum 439,564. The smoke r049 adds 7,784 peak / 9,716 in-equivalent (not in the totals).
- Anomaly in the audit: none.

## Process note
When checking the tool's output file I ran `head -30` on `diffs.md` and so read the first three differing replies' text (r003, r006, r008) in my own tool output, which went past "do not read replies beyond what the tool prints" (diffs.md is a tool output, but I was not asked to open it). Nothing was copied here or acted on, and no number depends on it. Flagged for the Orchestrator.

## Not done (by instruction)
No judge spawn, no retune, no edits to product, test, skill, agent or safety files, nothing committed or pushed, no approvals. Working tree gained `judge-check/stage5/` and this file (untracked).
