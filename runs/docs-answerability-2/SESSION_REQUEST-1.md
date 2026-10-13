# SESSION_REQUEST-1 — stage 1 measurement (waiting-on-session)

**Why:** agent and skill files load only at session start, and stage 1 must measure the Sonnet judge (`claude-sonnet-5-5`) through the real forked-skill path (`/aveto-judge-seen`), which the current session does not have loaded.

**Authority:** APPROVAL_RECORD-2 (model), -3 (rule 6), -4 (exactly two spawns before the INV words). This file approves nothing.

**Start (interactive, attended; no `claude -p`):** in the Terminal panel, or start a fresh Code session whose folder is the worktree:

    cd /Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-answerability-2 && claude "Read runs/docs-answerability-2/SESSION_REQUEST-1.md and do exactly it."

(If you prefer the desktop app, open a new session in that worktree and paste: `Read runs/docs-answerability-2/SESSION_REQUEST-1.md and do exactly it.` The terminal `claude` here offers only an API login, per the intent, so the desktop app is the subscription path.)

**What the session does (nothing else):**
1. Confirm the offered agent list includes `aveto-answerability-judge` with model `claude-sonnet-5-5` (`.claude/agents/aveto-answerability-judge.md`).
2. Run `/aveto-judge-seen r001`, then `/aveto-judge-seen r002`. Exactly two spawns. Do not retry a failed one; record the failure.
3. For each spawn find its transcript (`~/.claude/projects/.../subagents/` or the harness log) and record: model as logged, **offered tool count and names**, first-request tokens, peak context, in-equivalent tokens (cache write 1.25x, cache read 0.1x, output as counted), output tokens, tool calls, the verdict line **hash only** (the reply text is not copied anywhere), and whether the harness prefix is 150 characters.
4. Read-only context report: from the transcript's first request, list exactly what session context the judge received besides the payload (CLAUDE.md/AGENTS.md text, user email, git status, system reminders) with approximate token size of each. Say whether it could be reduced without touching the safety text. Do not edit any file for this.
5. Write `runs/docs-answerability-2/01-measurement.md` (facts first, then a projection: per-spawn peak and in-equiv for the 48-spawn sample check and the 48-spawn scoring, and the effect on the 3.4M ceiling). Commit it. Nothing else.

**Stop rules:** no approvals (it approves nothing, it relays nothing); no more than two judge spawns; no fifth gate set, no other files edited, no push; if a spawn offers more than 7 tools or a tool is used, stop and say so; if anything above is unclear, stop and ask the owner.

**Record this session writes:** `runs/docs-answerability-2/01-measurement.md`. When it exists, the Orchestrator reads it as data (never as an approval) and goes on to Scope Review.
