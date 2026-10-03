# Scope addendum 1: docs-retrieval-4 (2026-10-03T06:45:00Z)

Owner decision, given in the Orchestrator's session (verbatim): "Yes to both extras: add the 200-run retrieve loop per ranking mode to the crash evidence (exit codes and count of 134s only), and allow the docs/ARCHITECTURE.md update as a documented exception to the file cap. Nothing wider."

Not a rule 4 approval (no safety control changes). It amends `01-scope.md`:

1. **Crash evidence gains a 200-run `retrieve` loop per ranking mode** on one throwaway question, in addition to the 20 `eval` runs per mode on `evals/retrieval.toml`. The reranker-mode loop runs against files fetched with `ingest --with-reranker` (or already cached). Record only exit codes and the count of 134s. No eval set is used. Suggested by the Aveto AI SDLC session; adopted on the owner's decision, not theirs.
2. **File cap exception: `docs/ARCHITECTURE.md`** may be updated (reranker, opt-in, default ranking, per spec section 7). Files: 7 code/test + 6 wording + 1 documented exception = 14. The not-to-touch list is otherwise unchanged.
3. Budget unchanged (400k). Both extras cost shell time, and one file edit; if either pushes Implementation past its estimate, the Orchestrator stops and asks with the numbers.

## Addendum 2 (2026-10-03T06:49:02Z): crash criterion clarified by the owner

Owner (verbatim): "Clarification to the crash criterion: it is "no exit 134 and no signal exit across the runs". An eval exit of 1 on evals/retrieval.toml is expected, because that set misses its bar in both modes, and is not a failure. The 200-run retrieve loop must still exit 0 every time. Record the count of exit 0, exit 1 and exit 134 for each loop. Nothing wider."

Supersedes the intent's "exit 0" reading for the eval loops only. Eval loops: pass = no 134 and no signal exit (any status >128); exit 1 is expected. Retrieve loops: every run exits 0. Per loop, record counts of exit 0, exit 1, exit 134 (and any other code separately).

## Addendum 3 (2026-10-03T07:39:04Z): unfixed 200-run retrieve loop added by the owner

Owner (verbatim): "Yes, add the unfixed 200-run loop". Suggested by the Aveto AI SDLC session; adopted on the owner's decision. Crash evidence gains 200 consecutive `retrieve --ranking file-rerank-v1` runs on the UNFIXED code (commit before 07bc11d, e.g. 6591bf3 or a worktree of it), same throwaway question as the fixed loops, reranker files cached or fetched with the opt-in, exit codes and counts of 0 / 1 / 134 only. If no 134 appears, the report says that nothing here can discriminate the fix; claims stay at "implemented, closed in reverse order, proven by the close-order test; abort not reproduced in N unfixed and M fixed runs". Shell time only; budget unchanged.
