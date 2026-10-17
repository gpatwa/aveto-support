# APPROVAL_RECORD-7 — D1, seven harness tools added to the judge's disallowedTools (owner, typed, 2026-10-12)

Owner's words: "Approved: apply the D1 diff in runs/docs-answerability-2/03a-d1-proposed-diff.md exactly as written (the seven harness tool names added before mcp__* in the judge's disallowedTools, and the same change to DENY_LIST in tests/test_judge_artefacts.py). Nothing else in the agent file changes. If the smoke spawn shows the zero-tool agent does not launch or does not return its verdict, revert the diff and bring me the result; do not work around it."

Applied exactly (`git apply` of the fenced diff; no other edit). Registered consequence: the audit's `expect_tools` is **none** (0 offered tools) from the smoke onward. Standing condition: if the smoke shows the agent does not launch or returns no verdict, the Orchestrator reverts the diff (`git apply -R`), reports the transcript facts to the owner and works around nothing. Approves nothing else.
