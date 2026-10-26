# Release Gate preconditions P1 to P5 (Orchestrator, 2026-10-26T23:23:02Z)

## P1 regression at the gated tree (product files unchanged since scorecard commit a318d7c; only run records and docs after)
```
$ uv run pytest -q
731 passed, 12 deselected in 16.16s
$ uv run mypy
Success: no issues found in 53 source files
$ uv run ruff check
All checks passed!
$ git diff --stat main -- aveto_support prompts .claude .agentic/SAFETY_INVARIANTS.md .agentic/PROJECT_CONTEXT.md .agentic/LOCAL_COMMANDS.md infra Dockerfile pyproject.toml uv.lock (lines of output)
       0
$ git diff --stat main -- .claude/settings.json (lines)
       0
```

## P2 clean tree
`git status --porcelain` shows one unrelated modified file, `runs/fix-service-accounting/STATE.md` (the support session's one-line status fix, told to us in its message; not ours, not staged). `.dockerignore` excludes `runs/`, so it cannot reach the image; the image tag names the commit. Stated, not hidden.

## P3 Enter on a source link by keyboard
Local server, answer for the first suggestion; Tab from the result region reached the first source link; Enter navigated the pane to `https://github.com/gpatwa/agentic-sdlc-playbook/blob/3a83b669…/APPROVAL_PROTOCOL.md?plain=1#L50-L58` (the docs repository's permalink at the listed lines). PASS.

## P4 `live.py` dry run against the local dev server (stand-in judge, same index), through a scratch wrapper that only overrides `SERVICE_URL` and the output directory (live.py itself not edited)
- `check new`: ok, all nine checks true (headers on `/` and `/scorecard` equal the literal set).
- `check old` (negative control, run against the new code): ok false (`root_has_no_skip_link` false, `scorecard_404` false), as it must.
- `ask --index ... --models ...`: 7 questions, outcomes as expected, `byte_equal` true for all answered ones (including the form path and the 303 target), index sha256 `f36ef5d4…a756`, behaviour_failure false, counts delta +7 asked; no question or passage text written.
Not exercised locally: `watch`, `cold`, TLS/HTTPS.
