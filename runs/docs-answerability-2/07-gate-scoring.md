# 07-gate-scoring — stage 7 scoring of the fifth gate set (fresh QA Evidence, depth standard)

Scored once, from the repo root of the worktree. Flag spellings matched LOCAL_COMMANDS.md; no difference. No retune, rescore, re-derivation or rerun. The programs read the set; this file holds only their printed output (ids, counts, file paths, scores). No question text, label or reply text is copied here. I did not open `evals/retrieval-heldout-5*.toml`, `batch-2.txt`, `q/`, `diffs.md` or `06-label-review.md`.

## Step 1: record

`uv run python -m tools.judge_run record --subagents-dir ~/.claude/projects/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-docs-answerability-2/e19c6533-e4b1-4427-b9c2-012790dffb1f/subagents --eval-file evals/retrieval-heldout-5.toml --stage-dir runs/docs-answerability-2/judge-check/stage7 --expect-tools none`

Output: `batch valid; 48 batch spawns`. Not void. The subagents dir held exactly 48 `.jsonl` transcripts (counted before the run). Written by the tool: `judge-check/stage7/{verdicts.toml,audit.md,diffs.md,audit.json}`.

### Audit (audit.md, deterministic)
- 48 spawns, r101 to r148, one transcript each, none missing, none duplicated; each matched one key question (g01-g24, gu01-gu24).
- Every row: agent `aveto-answerability-judge`, model `claude-sonnet-5-5`, offered tools 0, `tool_use` 0, base-dir line 137, layout ok. No smoke spawn in the dir. Other agents: none.
- Anomalies in the audit: none.
- Session-load deviation (07a): it shows in no audited field. Model, offered-tool count, tool_use, base-dir line length (137) and payload attribution are identical in form to stage 5 on all 48 rows. The audit has no field that records how or when the agent and skill files were loaded, so this proves the observable behaviour matched, not the load path itself. The deviation stays disclosed for the Orchestrator and owner.

## Step 2: eval with verdicts

`uv run python -m aveto_support eval --eval-file evals/retrieval-heldout-5.toml --verdicts runs/docs-answerability-2/judge-check/stage7/verdicts.toml`

- **Exit code 1.** This is the retrieval gate on this set, not the judge result: `answerable: 19/24 (79.2%) required >= 80% FAIL`, `eval: FAIL`. The right file is in the top 5 for 19 of 24 answerable questions; 20 would have been needed (`bar_met`: 19*5=95 < 24*4=96). Misses (retrieval): g05, g06, g18, g19, g22. The registered stage 7 bars (R3) are the two judge bars below; the retrieval-gate failure is a separate printed fact and is reported to the Orchestrator as such. It is not a judge bar.
- Judge lines as printed:
  - `bar 1 (unanswerable abstained): 24/24 (100.0%) required >= 80% MET`
  - `bar 2 (answerable, right file in top 5, not abstained): 16/19 (84.2%) required >= 80% MET`
  - `judge errors: 0 (counted as failures on both bars)`
  - `hard negatives abstained: 18/18 (diagnostic)`
  - `never abstain (today): bar 1 0/24, bar 2 19/19`
  - `end to end: answerable questions whose right file is shown after judging: 16/24 (diagnostic)`

## Step 3: diagnostics

`uv run python -m tools.judge_run diagnostics --eval-file evals/retrieval-heldout-5.toml --verdicts runs/docs-answerability-2/judge-check/stage7/verdicts.toml --audit runs/docs-answerability-2/judge-check/stage7/audit.json` (exit 0)

```
best score rule (top1 < 0.67): bar 1 10/24 NOT MET; bar 2 13/19 NOT MET
over-abstention: 3/19 answerable questions with a hit were called NOT_ANSWERABLE (judge errors excluded)
ANSWERABLE without a hit: 1/5
judge errors: 0; bar 1 0 / bar 2 0 / neither 0
judge error categories: none
usage: 48 spawns; peak sum 410,748; in-equivalent sum 479,870
```

## Result against the registered bars (R3, stage 7)

| Check | Registered | Seen | Verdict |
|---|---|---|---|
| Bar 1: unanswerable abstained | at least 20 of 24 (19 fails) | 24 of 24 | **MET** |
| Bar 2: answerable with right file in top 5, not abstained | at least 80% of the denominator the tool prints (`bar_met`) | 16 of 19 (84.2%); 15 would have failed (15*5=75 < 76) | **MET** |
| Judge errors (own number, R5) | reported | 0 (bar 1 0 / bar 2 0 / neither 0) | n/a |
| **Overall (both MET)** | | | **MET** |

Bar 2 passes with one question of margin.

## Other registered reports (R7)

- **Answerable with the right file in the top 5:** 19 of 24 (79.2%). Not in top 5: g05, g06, g18, g19, g22.
- **Never abstain (today):** bar 1 0/24, bar 2 19/19.
- **Best score rule (top1 < 0.67), same set:** bar 1 10/24 NOT MET (needs 20); bar 2 13/19 NOT MET (needs 16). Both bars fail; the judge beats it on both.
- **End to end:** the tool prints 16/24 (answerable questions whose right file is shown after judging, diagnostic). Arithmetic from printed numbers: 19 with the right file in the top 5, minus 3 abstained by the judge, equals 16, over 24 answerable.
- **Over-abstention:** 3/19 answerable questions with a hit were called NOT_ANSWERABLE (judge errors excluded): g09, g10, g24.
- **ANSWERABLE when the right file was not in the top 5:** 1/5, all in the answerable-without-a-hit group (that one is g19; g05, g06, g18, g22 were NOT_ANSWERABLE). In the unanswerable group, the judge said ANSWERABLE on 0 of 24 (bar 1 24/24); an unanswerable question has no right file, so the tool's 1/5 does not count that group.
- **Verdicts that differ from the key:** 3, ids g09, g10, g24 (the `eval` printout marks them DIFF). All three are answerable-with-hit called NOT_ANSWERABLE. No unanswerable question differed. The five answerable questions without a hit print `n/a` (no key comparison). I did not open diffs.md.
- **Usage (tool's transcript read):** 48 counted spawns, peak sum 410,748, in-equivalent sum 479,870. No smoke spawn in this batch.
- **Anomalies in the audit:** none.

## Notes for the Orchestrator

- **Retrieval gate exit 1 (19/24 = 79.2%, one question short of 80%).** It is not one of the registered stage 7 bars and I did not weigh it. The dev set also scores 19/24 = 79.2% on this ranking and exits 1 by design (LOCAL_COMMANDS.md), so the product's retrieval result is unchanged in kind. Whether the owner reads it as relevant to the release gate is the Orchestrator's and owner's call.
- **Held-out rule:** the set was scored once. Whether any method file changed since the freeze `bca0e40` was not re-verified by me beyond the audit; the Orchestrator's freeze record covers it.
- **Deviation disclosed in 07a** (session moved from the main checkout to the worktree before any spawn) shows in no audited field, as above.
- No command above wrote a file outside `judge-check/stage7/` and this file. `SUPPORT_REPLIES.md` was already modified before this stage and was not touched.

## Not done (by instruction)

No judge spawn, no retune, no rescore, no edits to product, test, skill, agent, safety or eval files, nothing committed or pushed, no approvals. Working tree gained `runs/docs-answerability-2/judge-check/stage7/` and this file (untracked).
