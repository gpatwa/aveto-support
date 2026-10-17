# REVIEW.md

> Read by every code review in this repo (see `.claude/protocols/CODE_REVIEW.md`).
> Keep it short: it is loaded every time.

## What failure looks like here
- **Caller text reaching a shell, a path or a prompt unvalidated.** A skill's `!`
  line, a `--verdict-file`, a question echoed to stdout. Slice 7's S5 was a `'`
  breaking out of quotes before the script's own checks ran.
- **A permission rule or deny list that allows more than it names.** A wildcard
  before or inside a command; a deny list that stops at built-ins and leaves
  `mcp__*` or the harness tools reachable. Slice 7's S6.
- **The program making a network call or calling a model.** `retrieve`, `eval`,
  `judge-input` and `judge-apply` stay offline (INV-5); only `ingest` fetches.
- **Retrieved text altered, reworded or chosen by a model** (INV-4): the verdict
  only decides whether `retrieve`'s whole output is printed.
- **A test that passes without asserting what its name says,** or an eval key
  that drifts from its loader (a string where the loader counts only `true`).

## Report only
- A bug with a file and line, what triggers it, and the fix.
- At most 3 nits per review. Style-only and cleanup-only findings are dropped.
- Nothing already reported in an earlier round.

## Skip
- `index/`, `models/`, `uv.lock`, and `runs/*/judge-check/` (generated or data).
- `evals/*.toml` content: held-out sets are labelled by their own review, not here.

## Always read closely
- `.agentic/SAFETY_INVARIANTS.md`, `.claude/agents/aveto-answerability-judge.md`
  (the deny list and the hook), `.claude/skills/`, `.claude/settings*.json`,
  `aveto_support/judge.py`, and anything under `.github/workflows/`.

## Summary
Start with the count of findings. If there is nothing to fix, say so plainly.
