# End review — land-answerability

Tier 3. Verdict (Release Manager, `08-release-checklist-tier3.md`): **GO WITH CONDITIONS to open the PR; not a landing sign-off.** The PR opens against `main`; **you merge it, if you choose**. Nothing is announced or deployed.

## What changed (Risk tier High: skill, invariant-adjacent, permissions)
- **S5 fixed** (`1a8f5f8`, `501ec3a`, `0379f59`): `/aveto-judge-seen` has a fixed shell line with no caller text. The run id is now read from `.aveto-judge/seen-id` (write it, then run the skill with no argument). 21 hostile values × 3 tests, including `r101' ; echo INJECTED ; '`. `/aveto-judge` and every method file are unchanged from `bca0e40`; INV-4/INV-5 text is byte-identical.
- **T4** rollback rehearsed on a scratch branch: clean `git revert -m 1`, reverted tree equals `main`, regression 168 passed. Covers a *merge commit* only.
- **T5** monitoring adopted as written + `docs/runbooks/answerability-judge.md`. **T7** known limit stated (19/24 = 79.2%; 16/24 end to end; operator path unmeasured). **T9** tier 3 / S6 removed in README, status, ARCHITECTURE, ADR 0008 note. **T2** change request decision recorded. **T3** vendor risk recorded. **T10** AI Governance (standard) MET WITH GAPS; Data Governance waived. **T11** `trace.json`, operator Gopal Patwa.
- Final-tree: `mypy`, `ruff` clean; `pytest` **425 passed, 12 deselected** (375 + 50 new) at `e2b228e`; later commits touch only `runs/` (checked at push, below).

## Read these yourself
1. `.claude/skills/aveto-judge-seen/` (SKILL.md, seen_payload.py): the one safety-control change (C5.3).
2. `runs/land-answerability/06-security-recheck.md`: PASS, no blocker; R1 fixed; advisories A1 (wildcard inside allowed-tools, pre-existing, narrowed), A2 (relies on the harness's own escaping of arguments), A3 (symlinks followed when writing `q/<id>.txt`; needs a local writer) carry to a later slice.
3. `runs/land-answerability/code-review.md`: 1 finding (F1), fixed.

## Deviations and things not hidden
- **F1 / Charter C6.P file name:** the run's permission rules were written to `.claude/settings.json` per the Charter, then moved to the gitignored `.claude/settings.local.json` because they would otherwise have shipped to `main`. Same rules, narrower scope. That file was **deleted after the PR was opened** (A4); see the final line of this file.
- **T3 is WAIVED, not MET:** personal subscription, no DPA; retention/training per public plan terms, not verified. The operating rule "public-docs questions only until a DPA is in place" is adopted (policy only, no technical enforcement). Your Charter does not contain a sentence accepting residual risk; the Compliance and change-request approver boxes in `11b`/`11c` remain yours to tick.
- **Spend:** 651k peak-context sum vs plan 450k, ceiling 600k (**exceeded; notice, run continued**), hard cap 750k not reached. Overruns: Security (94k vs 60k est.), Tech Writer, Release Manager (187k vs 60k est.). Two spawns (Architect, Security) were logged as Opus; the Trace models come from `usage.mjs`.
- **No time of day** on the Charter approval (not invented).
- A permission prompt: none observed in the stages.
- Carried unaccepted from slice 7: R-B (Bar 2 by one question), R-C advisories, R-D (the model-marked `test_sample_derivation_reproducible` fails), R-E, R-F. Art. 50 question flagged for you or legal.

## What is yours to decide
- Whether to merge, and **how** (a merge commit keeps the rehearsed rollback valid; squash or fast-forward would need a different revert).
- Accepting (or not) the DPA residual risk; the Compliance/Release Manager rows.
- Whether the operator path should be measured before any use beyond public docs.

## Pre-push check (condition C-1), run on the head before the push
`git status --short` empty; `git diff --name-only e2b228e HEAD` lists only `runs/` paths; `git diff bca0e40 HEAD` over the method files empty; `git diff main -- .claude/settings.json` empty; `SAFETY_INVARIANTS.md` identical to `bca0e40`; `git diff --check`: only trailing-blank-line notes in run records (slice 7's and this slice's), no code. The pushed head is the commit this file is in; later commits, if any, touch only `runs/`.
