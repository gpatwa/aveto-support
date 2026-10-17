# Charter: land-answerability

> The only human approval in this run. Approve it once, in your own words, naming this file and its sha256. After that the run proceeds to a finished result and asks nothing; it stops only for section 9.

## 1. Scope
- **C1.1 Intent:** `runs/land-answerability/intent.md`, sha256 `2c631987dc1da7575502112e751602e8a51e01bec51eda50627fed27861ffdc0`
- **C1.2 Plan:** `runs/land-answerability/00-slice-plan.md`, sha256 `f53f7167547f4168512996500995902b84bae227d210a9237012cde181da95af`
- **C1.3 Non-goals:** drafting replies; INV-3; a runtime model client, GitHub issue intake or deploy; any change to retrieval or to the judge's method; re-running any gate; the set-aside `RELEASE_APPROVAL_PACKET.md`.

## 2. Budget (unit: peak context summed per spawn)
- **C2.1 Plan total:** 450k
- **C2.2 Ceiling:** 600k. Above it the run continues and sends a notice.
- **C2.3 Hard cap:** 750k. Above it the run stops. The run never raises it.

## 3. Models (rule 5)
- **C3.1** Answerability judge: `claude-sonnet-5-5`, the operator's session only, zero tools (unchanged from slice 7; this run does not call it).

## 4. Data processors (rule 6)
- **C4.1** Anthropic, through the operator's own Claude Code session, receives: the question, the shown public-docs passages and the fixed prompt, plus the harness-attached session context as named in approval records 3, 6 and 8 of slice 7 (unchanged). Terms status as stated by the owner: personal subscription, no DPA in place; retention and training use per that plan's public terms, not verified by an agent. Recorded in `11b-vendor-risk.md`. Operating rule **adopted**: public-docs questions only until a DPA is in place.

## 5. Safety controls (rule 4)
- **C5.1** `.agentic/SAFETY_INVARIANTS.md` INV-4: unchanged by this run; no word of it changes.
- **C5.2** `.agentic/SAFETY_INVARIANTS.md` INV-5: unchanged by this run; no word of it changes.
- **C5.0** INV-3 (drafting check) is out of scope: this run changes no word of it and builds nothing under it.
- **C5.3** `.claude/skills/aveto-judge-seen/` (`SKILL.md`, `seen_payload.py`): may change only to remove caller text from the `!` shell line (a fixed id validated against the committed key, passed so that no quote can break out) and to add the hostile-argument tests. `/aveto-judge` and every other method file stay byte-identical to `bca0e40`.

## 6. Prerequisites (set once in the setup phase, each with its dry run)
| id | What | Why | Dry run that proves it |
|---|---|---|---|
| C6.P | Allow rules written to `.claude/settings.json` after approval, exactly: `Bash(uv sync --locked)`, `Bash(uv run mypy)`, `Bash(uv run ruff check)`, `Bash(uv run pytest *)`, `Bash(git status *)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git add *)`, `Bash(git commit *)`, `Bash(git switch *)`, `Bash(git revert *)`, `Bash(git branch *)`, `Bash(git push -u origin claude/land-answerability)`, `Bash(gh pr create *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/charter-check.mjs *)`, `Bash(node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/usage.mjs *)` | every stage | each allowed command run once in setup (the push and PR rules are not run in setup; they are exercised once, at the end, under C8.2) |
| C6.1 | Pack v23 on `main`, merged into the landing branch | every stage | `grep packVersion .claude/agentic.config.json` prints 23 in the worktree |
| C6.2 | Agent teams on (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | stages 1 to 9 | `env` shows it |
| C6.3 | `uv sync --locked` in the worktree | stages 1, 2, 8 | `uv run pytest tests/test_judge_seen_skill.py` passes |
| C6.4 | Visible symlink to the worktree | owner's reading | `ls -l` resolves |

## 7. Depth (may not be lowered)
- **C7.1** Security Review: standard
- **C7.2** Release Gate tier: 3

## 8. Outcomes decided now
- **C8.1 If a pre-registered check fails:** close as not releasable, write the close-out, stop.
- **C8.2 At the end of a passing run:** push `claude/land-answerability` to origin and open a pull request into `main` with the end review linked; never merge, never deploy, never send.
- **C8.3 Irreversible actions allowed (rules 1 to 3):** the branch push and the pull request in C8.2 only. Rollback: close the PR and delete the remote branch.
- **C8.4 Human review of a Low-risk change at the end:** review
- **C8.5 Owner positions recorded by this Charter (T-items):** change request decision (T2): approve landing by pull request, merge is the owner's own act; monitoring thresholds, cadence and stop rules in `11-monitoring-plan.md` adopted as written (T5), with the standing mitigation "stop typing `/aveto-judge`, use `retrieve` alone"; retrieval gate limit (79.2% on the fifth set, 16 of 24 end to end) accepted and stated plainly in README and status (T7); S5 fixed, not retired (T8); S6 rule deleted, as the owner said on 2026-10-16 (T9a); Data Governance waived, AI Governance at standard (T10); operator handle for `trace.json`: Gopal Patwa (T11).

## 9. Stops (the only reasons the run asks)
1. An action not covered by a line above (a new model, processor, data, file, invariant, or irreversible action).
2. Spend above the hard cap (C2.3).
3. A credential is needed (agents never handle credentials).
4. Lowering a depth in section 7.
5. A change to this Charter (an amendment is a new approval of a new hash).

## 10. Notices (sent, never asked)
A push notification at each stage boundary with two lines: the stage, its result and the spend. The full record stays in `runs/land-answerability/`.
