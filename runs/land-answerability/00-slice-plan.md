# Slice plan — land-answerability

> Orchestrator, 2026-10-17. **Proposed; not confirmed.** Units: peak context summed per spawn.
> Worktree `.claude/worktrees/land-answerability`, branch `claude/land-answerability`, cut from `claude/docs-answerability-2` (c150673, slice 7 as closed), with `main` (pack v23, `REVIEW.md`) merged in cleanly. Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (absolute; the relative path does not resolve from a worktree).

## Outcome (one line)
The attended judge step from slice 7 is on a branch with its eleven tier 3 items (T1 to T11) closed, `/aveto-judge-seen` no longer takes caller text in its shell line, and a pull request into `main` is open for the owner to merge; the run never merges.

## Success criteria
`intent.md` "Done means", by reference, not restated. Tier 3 Release Gate with every T item MET (T1 is met by the Charter's C8.2 for the push and PR; the merge is the owner's own act and is not a gate item the run can close). No gate result of slice 7 is re-run.

## Non-goals
Drafting replies; INV-3; any runtime model client, GitHub issue intake or deploy; any change to retrieval or to the judge's method; re-running any gate; the set-aside `RELEASE_APPROVAL_PACKET.md`.

## Constraints from `.agentic/`
Safety invariants as approved in slice 7 (INV-4, INV-5 text unchanged by this slice); the program stays offline; judge stays zero-tool on `claude-sonnet-5-5`; Python 3.12, uv, no new runtime dependency; no metered API, key or `claude -p`.

## Stages (tier 3; Security standard per the Charter)

| # | Stage | Owner | Depth | Environment | Est. |
|---|-------|-------|-------|-------------|------|
| 1 | S5 fix: `/aveto-judge-seen` shell line takes no caller text; fixed id validated against the committed key; hostile-argument tests (`r101' ; echo INJECTED ; '` and similar). `/aveto-judge` unchanged; no other method file changes | AI Engineer | standard | default | 80k |
| 2 | Rollback rehearsal (T4): throwaway branch, revert of the slice commits per `11c-change-request.md`, full regression on the reverted tree, branch deleted | QA Evidence | standard | default | 40k |
| 3 | Vendor risk (T3): record the owner's DPA/plan/retention statement in `11b-vendor-risk.md`, operating rule adopted | Compliance Reviewer | standard | default | 30k |
| 4 | AI Governance review of the judge step (T10); Data Governance waived, reason recorded in the plan and release checklist | AI Governance | standard | default | 50k |
| 5 | Records and docs: monitoring adopted as written, runbook `docs/runbooks/answerability-judge.md` (sections 2 and 5), known limit in README and `CURRENT_MVP_STATUS.md`, tier 3 verdict and S6 removal in README, status and `ARCHITECTURE.md`, `11c` decision from the Charter, STATE fixes | Tech Writer | standard | default | 50k |
| 6 | Review layer: `/code-review` at `high` on the diff against `main`, `REVIEW.md` as rules, `code-review.md` (Orchestrator runs; up to three fix rounds go to the author role) | Orchestrator | high | default | 30k |
| 7 | Security re-check of the S5 fix and everything changed since slice 7's review | Security & Privacy | standard | default | 60k |
| 8 | Final-tree `uv sync --locked`, `mypy`, `ruff check`, `pytest` on the PR head, plus an empty diff of every method file against `bca0e40` | QA Evidence | standard | default | 40k |
| 9 | Release Gate at tier 3 (walk T1 to T11) | Release Manager | standard | default | 60k |
| 10 | `trace.json` (operator handle), `END_REVIEW.md`, push of `claude/land-answerability`, PR into `main` (Orchestrator; Charter C8.2) | Orchestrator | — | default | 0 |

Estimated sum 440k; **plan total 450k** (10k margin). Review fix rounds, if any, draw on the margin and then the ceiling.
Skipped on purpose: Market Research, PM, UX, UI, Architect (no new design; the fix is bounded by the intent), Engineering Manager scope review (scope is fixed by T1 to T11). Gates do not compress; none is dropped.

## Data Governance (T10): waived
The program stores no user data; the operator's question goes to Anthropic through their own session, covered by approval records 3 and 6 of slice 7. Recorded here and in the release checklist.

## Prerequisites (setup phase; every row has a dry run before the first stage)

| id | What | Why | Dry run |
|---|---|---|---|
| P1 | Pack v23 installed and committed on `main` (already true: `agentic.config.json` packVersion 23); merged into the landing branch | every stage | `grep packVersion .claude/agentic.config.json` shows 23 in the worktree. Done in setup. |
| P2 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.json` env) so each stage is a named teammate | stages 1 to 9 | `env` shows it; teammate spawn in setup |
| P3 | Permission rules of Charter C6.P in `.claude/settings.json`, written only after approval | no prompt in a stage | each allowed command run once |
| P4 | `uv sync --locked` environment in the worktree | stages 1, 2, 8 | `uv run pytest tests/test_judge_seen_skill.py` runs |
| P5 | Local `/code-review` skill available | stage 6 | skill listed in the session |
| P6 | Visible symlink to the worktree for the owner | owner's reading | `ls -l` of the link resolves |
