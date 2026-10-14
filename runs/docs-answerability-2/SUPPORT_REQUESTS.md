# Support requests — docs-answerability-2

> Writer: the Orchestrator. One writer per file. Nothing here is an approval. Read by the support session; answers go in `SUPPORT_REPLIES.md`.

## Request 1 — placement of the fifth gate set (method frozen)

**Freeze:** method commit `bca0e403a69a5cda7826ea36897734bc63dc7b87` (recorded in `STATE.md`, "Freeze record"). The fifth set may now be placed. The Orchestrator does not ask for it, has not looked for it, and runs nothing on it. It must not be opened by the builder, the Orchestrator or any role that built retrieval or the judge; the first reader is the fresh label-review QA.

### Where
Worktree `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-answerability-2` (branch `claude/docs-answerability-2`), exactly two files:
1. `evals/retrieval-heldout-5.toml`: the scored set, **exactly 24 answerable and 24 unanswerable** questions (18 of the unanswerable carry `hard_negative = true`).
2. `evals/retrieval-heldout-5-reserves.toml`: the reserves, same format, ids `gr01`, `gr02`, ... Reserves are **never** run through `add-set` and never scored unless the label review replaces a question (the label-review protocol, not this file, says how). Keep them out of file 1.

Place them as **uncommitted files**. The writer does not `git add`, commit or run anything on them. Tell the owner they are in place; the owner then tells the Orchestrator, who commits the two files **unopened** (`git add` of those two paths, nothing else) as the first commit after the freeze, before any label review.

### Format (the product's own eval format; `aveto_support/evaluate.py` loads it, `tools/judge_run.py add-set` reads only `id` and `question`)
- TOML. First key: `pinned_commit = "3a83b669a8b53dfdff869a1bbe361bdb156e3a13"` (the seen sets' commit and the index's; any other value makes `eval` refuse).
- One `[[question]]` table per question, in this form:

```toml
[[question]]
id = "g01"
question = "One question, one line, as a user would ask it?"
sources = ["docs/RELEASE_GATES.md"]      # answerable ONLY: non-empty list of paths inside the corpus at the pinned commit
where = "optional free text naming the passage"   # answerable only; ignored by the loader

[[question]]
id = "gu01"
question = "A question the docs do not answer?"
answerable = false                        # unanswerable ONLY
hard_negative = true                      # the boolean true, NOT a string; only on the 18 hard negatives
```
- `answerable` is omitted (default true) on answerable questions and `false` on unanswerable ones. An answerable question without a non-empty `sources` list makes the file unloadable.
- `hard_negative` must be the TOML boolean `true`. (`evals/retrieval-heldout-4.toml` used a string; the loader only counts `true`, so a string would silently not count as a hard negative.) No `hard_negative` key on answerable questions, or on the 6 unanswerable ones that are not hard negatives.
- `id`: a unique string per question across both files, not reusing any seen-set id (use `g01`..`g24` for answerable, `gu01`..`gu24` for unanswerable, `gr01`.. for reserves).
- `question`: **one line**, non-empty, no leading or trailing space, no newline or carriage return, no control or format characters (zero-width, bidi), plain text only. It becomes the judge's input verbatim, so it must contain nothing you would not want sent to the model provider.
- Questions must not repeat a topic or a question of the four seen sets (`evals/retrieval.toml`, `-heldout`, `-heldout-3`, `-heldout-4`), and no `sources` path may be a source in any seen set (the earlier sets' rule).

### What to strip before placing
- Any run id (`rNNN`), judge verdict, score, model output, hit/miss or rank for any question, from comments or fields.
- Any mention of this slice's results (sample check numbers, which questions the judge got wrong) or of the seen-set per-question outcomes.
- Any reviewer notes, answer text, or quoted docs passages beyond the single `where` phrase.
- Any retrieval output: the set must not have been run through `retrieve`, the index or `eval` (state this in the provenance header).
- Everything not listed above: extra keys, extra tables, a `[meta]`-style table. The loader ignores unknown keys, but `add-set` reads the raw `[[question]]` tables, so keep to the form above.
- Header comments are allowed (the earlier sets have them) but only provenance: who drafted it, when, that it was kept outside the repo until the freeze, that it has not been run, and the bars (20 of 24 unanswerable; 80% of answerable whose right file is in the top 5). No results, no secrets.

### Not asked of the support session
Its contents are not requested here; no one is asked to describe, summarise or sample it. Label review is the fresh QA's job (unanswerable labels attacked hardest), and a different fresh QA scores it once.
