# Approval record 8 — `mcp__*` on the judge's deny list, ceiling 2.6M, probe respawn, seen-set check

- **Approver:** the owner (Gopal Patwa), typed directly in the session driving this run
- **Decision:** approved
- **Scope:** (1) append `mcp__*` to `disallowedTools` in `.claude/agents/aveto-answerability-judge.md`, the one-token diff proposed in 05-lean-measurement.md, hook unchanged; (2) run the refusal probe once more on the changed agent (judge spawn 2 of 2, APPROVAL_RECORD-7 item 2) and record it; (3) ceiling for this slice **2.6M peak-sum**, stop and ask above it; (4) then run the 93-spawn seen-set check as pre-registered.
- **Consequence handled by the Orchestrator, not separately approved:** `tests/test_judge_artefacts.py` pins the agent's exact deny list, so the same one token was added to its `DENY_LIST` constant to keep the regression green. No safety text, hook or model changed.
- **Unchanged:** APPROVAL_RECORD-5's two conditions (full model ID; stop-and-ask unless a test shows a tool call refused).
- **Replaces:** the 1.4M ceiling of APPROVAL_RECORD-1, by the owner's own typed word.

**Owner's response, verbatim:**

> Approved: append mcp__* to disallowedTools in .claude/agents/aveto-answerability-judge.md, exactly the one-token diff you proposed, hook unchanged. Then run the refusal probe once more (judge spawn 2 of 2) on the changed agent and record it. Ceiling for this slice: 2.6M peak-sum; stop and ask above it. Then run the 93-spawn seen-set check as pre-registered.
