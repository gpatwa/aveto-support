# T4 Rollback rehearsal — land-answerability

QA Evidence, 2026-10-17. Plan rehearsed: `11c-change-request.md` "Rollback plan" step 3 (and `02-tech-spec.md` section 13 item 2, `13-release-checklist-tier3.md` section 10 item 3): `git revert -m 1 <merge-commit>` and the full regression. Nothing is merged, so the merge was simulated on a throwaway branch in a separate worktree outside the repo. Nothing from it is kept or pushed.

Landing HEAD before: `1a8f5f81d7fb0ef63ed9c41ae1baccb450e516a8`. `main`: `132b548`. merge-base(main, landing) = `132b548` (landing is main plus the slice 7 and landing commits).

## Commands and output (trimmed)

| # | Command (in order) | Result |
|---|---|---|
| 1 | `git worktree add -b scratch/rollback-rehearsal /private/tmp/claude-501/rollback-wt main` | `HEAD is now at 132b548` |
| 2 | `git merge --no-ff claude/land-answerability -m "scratch: simulate merge ..."` (in the scratch worktree) | clean, no conflicts; merge commit `157764090974f83837453c8e908aed30aacded56` (first parent 132b548, second 1a8f5f8). `git diff --stat main HEAD`: 193 files changed, 12014 insertions, 88 deletions |
| 3 | `git revert -m 1 --no-edit 157764090974f83837453c8e908aed30aacded56` | clean, no conflicts, no manual resolution; new commit `24076b3 Revert "scratch: simulate merge of claude/land-answerability"` (deleted `tests/test_judge*.py`, `tools/`, etc.) |
| 4 | `git rev-parse HEAD^{tree} main^{tree}`; `git diff --quiet main HEAD` | both trees `ac20066039c43be60999f1651d6da4a915f00c36`; `IDENTICAL_TO_MAIN`. The revert restores `main` exactly (incl. INV-4/INV-5 pre-slice text, README, `CURRENT_MVP_STATUS.md`; `.claude/skills/` absent; no "judge" in `aveto_support/`) |
| 5 | `uv sync --locked` | exit 0 |
| 6 | `uv run mypy` | `Success: no issues found in 15 source files`, rc 0 |
| 7 | `uv run ruff check` | `All checks passed!`, rc 0 |
| 8 | `uv run pytest` | `168 passed, 10 deselected in 7.43s`, rc 0 |

Each regression command was run separately (no `&&` chain) with its own exit code. (Step 3's printed `revert-exit` was the exit of a piped `tail`; success is established by the commit created and the identical-tree check in step 4, not by that echo.) 168 passed is the pre-slice suite count on `main`; the landing branch has 428 passed, 12 deselected (`01-s5-fix.md`). The difference is the judge tests removed by the revert, as expected.

## Cleanup proof

- `git worktree remove --force /private/tmp/claude-501/rollback-wt` rc 0; `git branch -D scratch/rollback-rehearsal` `Deleted branch ... (was 24076b3)`.
- `git branch --list 'scratch/*'`: empty. `git worktree list | grep -c rollback`: 0. Directory `/private/tmp/claude-501/rollback-wt`: gone.
- Landing branch untouched: `git status --short` empty; HEAD still `1a8f5f81d7fb0ef63ed9c41ae1baccb450e516a8`; `main` still `132b548`; reflog shows no new entry. Nothing pushed (no push command run).

## Deviations from the written plan and limits

1. `--no-edit` added to `git revert` (non-interactive). `git revert -m 1` worked cleanly.
2. The merge commit was simulated (`--no-ff` onto `main`), because nothing is merged. The real merge method is the owner's; the plan itself says the full-revert command assumes a merge commit. With a squash or fast-forward the revert target differs and this rehearsal does not cover it.
3. The simulated merge covers the whole landing branch (slice 7 plus the landing commits), so the revert rehearsed is the full back-out to `main`, which is the broadest case.
4. Only step 3 was rehearsed (the one T4 and the Done-means line name). Steps 1, 2, 4, 5 and 6 of the plan were not run. Step 6 (transcripts, the gitignored settings rule, Anthropic retention) is outside git and unreachable by any revert, as the plan says.
5. The INV-4/INV-5 text reverted on the scratch branch only. The plan's requirement of the owner's own words before a real revert lands (rule 4) is unchanged by this rehearsal; nothing was applied to a real branch.
6. Validity is against `main` at `132b548`. If `main` moves before the merge, the revert is on the owner to re-check; this rehearsal does not cover later main commits.
7. `git worktree add`, `git merge` and `git worktree remove` are not in the C6.P allow list; they ran only on the throwaway worktree/branch as the task asked, touched nothing shared, and needed no approval under the Charter (section 9 stops are not hit).

## Verdict

**T4 MET.** The rollback plan's step 3 was executed on a throwaway branch: `git revert -m 1` applied cleanly, restored a tree identical to `main`, and the full regression (`uv sync --locked`, `mypy`, `ruff check`, `pytest`) passed on the reverted tree (168 passed). Nothing from the throwaway branch was kept; the landing branch is unchanged.
