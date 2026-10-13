# Standing instructions (owner, typed in the driving session, 2026-10-12)

- **SI-1:** for a design question with a recommended default (not rules 1 to 6, a budget change, a credential, or push/merge/deploy), proceed on the default and list it in the next digest; the owner vetoes by exception.
- **SI-2:** any Reply N in `runs/docs-answerability-2/SUPPORT_REPLIES.md` that marks its decisions as recommended defaults under SI-1 is adopted under SI-1, with each decision listed in the next digest. This never covers budget or ceiling changes, rules 1 to 6, credentials, safety-control wording, lowering a depth the intent names, or push, merge and deploy.

## Other owner instructions at start (same message)
- Fresh worktree off main (done: `.claude/worktrees/docs-answerability-2`, branch `claude/docs-answerability-2`).
- First commit brings slice 6's judge code, skills, tests, `mcp__*` deny list; NOT a8c9604 (INV words), NOT slice 6 run records.
- After that commit, the owner starts a fresh session in the worktree before any judge spawn (agent and skill files load at session start).
- Plan confirmation shows stages with Environment, the estimate, and a ceiling and hard cap derived from slice 6's measured ratios; the owner types the figures.
- Stage 1 is a two-spawn Sonnet measurement in the real forked-skill configuration, before anything is built; bring measured numbers and a projection.
- Never approve, relay or infer an approval. Stop and ask for rules 1 to 6, a ceiling or hard-cap change, lowering a depth the intent names, credentials, push/merge/deploy. No `claude -p`, no metered API. Do not ask for or look for the fifth gate set.

## Digest: decisions taken under SI-1
| # | Decision | Default taken |
|---|----------|---------------|
| D1 | The first commit cannot be a plain `git cherry-pick 37c21d2` (it is a delta on slice 6's 3a/3b commits, main lacks the base files: modify/delete conflicts). | Take the files 37c21d2 touches, plus the files they need to run (`judge_eval.py`, `__main__.py`, prompt, `/aveto-judge` skill, tests, `.gitignore`), at their 37c21d2 state, in one commit (5eb2a8a). Left out: a8c9604, ADR 0008, `.agentic/LOCAL_COMMANDS.md`, all `runs/`. |
| D2 | Stage 1 needs a seen-check directory for the forked skill (its path is hardcoded). | Created `runs/docs-answerability/seen-check/` with only two rows (r001, r002; public eval-set questions) and a key with membership only, no answers. Not slice 6's records; stage 4 rebuilds it for the 48 sample. |
| D3 | The worktree had no `index/` or `models/` (gitignored). | Copied both from the main checkout (local copy, no network). |
