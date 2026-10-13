---
name: aveto-judge-seen
description: Eval-only. Send one committed seen-set question's judge payload to the answerability judge in a forked subagent. Takes a run id in the key (r001..r049 at the sample, r101 upwards for the gate set) only.
context: fork
agent: aveto-answerability-judge
background: false
allowed-tools: Bash(uv run -q --project * python ${CLAUDE_SKILL_DIR}/seen_payload.py *)
---
!`uv run -q --project "${CLAUDE_PROJECT_DIR}" python "${CLAUDE_SKILL_DIR}/seen_payload.py" '$ARGUMENTS'`
