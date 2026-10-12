# Seen-set driver recipe (skill `aveto-judge-seen`)

Per question id `rNNN` (the driver never reads `key/key.toml`):

1. Invoke the skill with the id only: `/aveto-judge-seen rNNN` (or the Skill tool with `args: "rNNN"`). Claude Code runs the `!` command, which writes `seen-check/q/rNNN.txt` and injects `judge-input`'s stdout as the forked judge's whole prompt. No model retypes it. A refusal (bad id, id not in the key, judge-input failure) exits 2 and aborts the invocation: no judge starts.
2. Get the input sha256 (stderr), payload discarded:
   `uv run python -m aveto_support judge-input --question-file runs/docs-answerability/seen-check/q/rNNN.txt >/dev/null`
   (do this before `judge-apply`, which deletes the question file; the next skill call rewrites it).
3. Write the judge's returned text, unmodified, to `.aveto-judge/reply.txt` (Write tool); an empty file if there was none.
4. `uv run python -m aveto_support judge-apply --question-file runs/docs-answerability/seen-check/q/rNNN.txt --input-sha256 <hex> --verdict-file .aveto-judge/reply.txt`
5. Record outcome and raw reply per spec 5.2.

Note: step 2 runs `judge-input`, which deletes a stale `.aveto-judge/reply.txt`; run it before step 3.
