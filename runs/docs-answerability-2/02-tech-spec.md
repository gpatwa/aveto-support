# Tech Spec — docs-answerability-2 (Architecture pass 1)

> Owner: Software Architect Agent. Pass 1 of 2, depth standard, 2026-10-12.
> Status: **draft, ready for pass 2** (pass 2 adds the INV-4/INV-5 draft words, ADR 0008 and the `docs/ARCHITECTURE.md` update; it does not change section 1).
> Source of requirements: `intent.md` (confirmed, APPROVAL_RECORD-1). No feature or UX spec (short path, see `01-scope.md` section 6).
> Inputs read: intent, `00-slice-plan.md`, `01-measurement.md`, `01-scope.md`, STATE, STANDING_INSTRUCTIONS, APPROVAL_RECORD-1..4, SUPPORT_REPLIES Reply 1 (data), `.agentic/*`, `aveto_support/judge.py`, `judge_eval.py`, the judge wiring in `__main__.py`, the judge agent file, both judge skills and `seen_payload.py`, `tests/test_judge*.py` (skimmed; the seen-skill test in full), `tests/conftest.py`, `evals/*.toml` (ids and counts only), `runs/docs-abstention/02-baseline.md` and `02-baseline-sweep.py` (the best-score rule's definition only), playbook `project-packs/ai-agent-product.md` (held-out rules) and `TECH_SPEC_TEMPLATE.md`. Read from the stage 1 transcripts (`~/.claude/projects/...docs-answerability-2/f8149669-.../subagents/`) by `Grep` only: the harness's base-dir line, the payload's start and end, the record types, `toolNames` and `model` in `prefix.json`, `meta.json`. **I deliberately did not read either stage 1 reply** (section 1 must be registered before any reply is read). I ran nothing (no Bash). I approved nothing and edited no product, test or safety file.

**Tags used throughout.**
- **[REG]** registered method text. Fixed now; never changed after any result of this slice. Frozen again, by commit, at the Freeze step.
- **[SI-1]** a design choice with a recommended default. Adopted by default under SI-1 and listed in section 14 for the owner's veto.
- **[OWNER]** not mine and not the Orchestrator's: rules 1 to 6, budget and ceiling, safety-control words, lowering a depth the intent names, credentials, push, merge and deploy. Each needs the owner's own words in the driving session.

## Summary

The product pieces exist (commit `5eb2a8a`): `judge-input` builds the payload, `judge-apply` applies a one-token verdict, `eval --verdicts` scores the two bars, the judge agent is pinned to `claude-sonnet-5-5` with a deny list ending in `mcp__*` and a match-all deny hook. This slice adds **no product behaviour**. It registers the method (section 1), rebuilds the eval-only seen-check data for the 48-question sample, and adds one eval-only tool, `tools/judge_run.py`, that (a) derives the sample deterministically from retrieval, (b) reads the forked judge transcripts after a batch, audits them (model, offered tools, tool use, payload binding), (c) turns each reply into a token **through the product's own `judge-apply`**, in-process, and writes the verdicts file that the product's `eval --verdicts` scores, and (d) computes the diagnostics the intent asks for that the product does not print. Everything the model sees is injected by the harness; no model retypes a payload or a reply. The INV-4/INV-5 words are pass 2's and the owner's; the D1 deny-list change is the owner's, at stage 4, on an exact diff.

## 1. Registered method [REG]

Registered here, before any reply of this slice is read and before any further spawn. Not changed after a result. The Freeze step (after stage 5) records the commit that holds this file together with the code and data in R8.

### R1. Payload layout

1. The judge's prompt (the first and only user message of each forked judge spawn) is exactly
   `Base directory for this skill: <D>` + `\n\n` + `<P>`, where
   - `<P>` is the stdout of `judge-input --question-file <judge-check>/q/<id>.txt`, byte for byte, as `seen_payload.py` passes it on (it starts `=== Q1 ===` and ends `=== end Q1 ===\n`), and
   - `<D>` is the absolute path of the `aveto-judge-seen` skill directory **as the harness writes it** for the session.
2. **Measured for this worktree** (both stage 1 transcripts, read by `Grep`): `<D>` = `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/docs-answerability-2/.claude/skills/aveto-judge-seen`, the **worktree** path, not the main-checkout path that `CLAUDE.md` comes from. That is 106 characters, so **the line is 31 + 106 = 137 characters** (without its terminator), and 139 characters precede the payload's `=== Q1 ===` (the line plus `\n\n`). This is my count from the transcript text, not a run. The tool in section 4 measures it on every spawn, and stage 4 checks the tool against the two stage 1 transcripts (expected 137 for both). 94 is the system block's `cliPrefix` and unrelated. 150 was slice 6's figure, with a longer path.
3. **The length depends on the path.** The line is `31 + len(<D>)` characters, so it differs per checkout. It is handled like this:
   - (a) The payload hash (`input_sha256`) covers `<P>` only, never the line. A different path cannot change a verdict's binding or a bar.
   - (b) For every spawn the audit records the line's length and checks its form: the exact text `Base directory for this skill: `, then an absolute path ending in `/.claude/skills/aveto-judge-seen` with no newline, then `\n\n`, then `<P>`.
   - (c) Stages 5 and 7 run from this worktree, so **the expected length is 137 on every spawn**. Any other length or form is an anomaly (R6): the batch is not scored.
   - (d) Moving the seen-check data (section 3) does not move the skill directory, so 137 still holds.
4. `<P>` must hash to the product's `input_sha256` of exactly one key question. That hash is what attributes a transcript to a run id. The constant block id `Q1` plays no part in attribution (`01-scope.md` 2.2).

### R2. Verdict grammar

This is the grammar `judge.parse_verdict` already implements, and the tests pin it. It is registered as is; no code changes. The product applies it in `judge-apply`, and the eval path reaches it only through `judge-apply` (section 4).

1. **Reply limits.** The reply must be at most 4096 bytes (`TOO_LONG`) and valid UTF-8 (`NOT_UTF8`).
2. **Lines.** The reply is split at `\r\n`, `\n` or `\r`. Each line has its surrounding whitespace stripped, and empty lines are dropped. If nothing is left, the category is `EMPTY`.
3. **Control or format characters anywhere fail** (`CONTROL`). Any Unicode Cc or Cf character in the whole reply, other than `\n` and `\r`, fails, **including in an earlier line that is otherwise skipped**. That covers a tab, a zero-width space, a soft hyphen and a bidi override. **Kept.** Reason: it is the parser's fail-closed defence against hidden text. Slice 6 approved it, and loosening it would weaken a safety parser after the fact. Cost: a think-aloud line containing a tab fails. Stage 5 measures how often that happens.
4. **The verdict comes from the last non-empty line only.** That line must fullmatch `<id> <TOKEN>[:][ <reason>]`. Breaking that down:
   - `<id>` is exactly `Q1`, otherwise `WRONG_ID`. `Q1:` counts as a wrong id.
   - `<TOKEN>` is `ANSWERABLE` or `NOT_ANSWERABLE`.
   - **An optional colon may follow the token directly.**
   - `<reason>`, if present, follows a single space and starts with a non-space character.
   - Anything else is `MALFORMED`. That includes `ANSWERABLE.`, `ANSWERABLE:reason`, `ANSWERABLE::`, two spaces after the colon, and bold or backtick wrapping.
5. **A reason containing the word `ANSWERABLE` fails** (`MULTI_TOKEN`). The last line must contain the case-sensitive substring `ANSWERABLE` exactly once, and `NOT_ANSWERABLE` contains it. A lower-case "answerable" in the reason passes. **Kept.** Reason: a line that names both tokens is ambiguous, and fail-closed is the declared stance (intent decision 2).
6. Checks run in this order, which decides which category a bad reply reports: `EMPTY`, `CONTROL`, `MALFORMED`, `WRONG_ID`, `MULTI_TOKEN`.
7. **The product never shows or stores earlier lines or the reason text.** Only the token leaves the parser (`Verdict.token`).
   - The eval record is a run artefact, not the product. It keeps a reply's full text **only** for rows whose verdict differs from the key or is a judge error, and only in `runs/docs-answerability-2/`. This is the intent's "the judge's reply held in the run record only". [SI-1: this reading of the intent. The alternative is to keep no reply text at all and lose the diagnosis of format failures.]
8. The prompt's "at most 12 words of reason" is not enforced, and is not registered as a check.

### R3. Pass thresholds

All of these use the product's `bar_met(count, total)`, which is `count * 5 >= total * 4` with integers, so 80% rounds up to the next whole question.

| Check | Bar 1: unanswerable abstained | Bar 2: answerable, right file in top 5, not abstained | Pass |
|---|---|---|---|
| Stage 5, seen sample (48) | **at least 16 of 20** (15 fails) | **at least 23 of 28** (22 fails) | both |
| Stage 7, fifth set | **at least 20 of 24** (19 fails) | **at least 80% of the answerable questions whose right file retrieval put in the top 5** (`bar_met` on that count, which is known only after retrieval on the fifth set) | both |

- Stage 7 scores exactly 24 unanswerable questions. If the label review leaves fewer than 24 after the reserves are used, the slice stops (pack held-out rule 9). How reserves are used is the label-review stage's protocol and is not registered here.
- **Failing stage 5 stops the slice before the fifth set is handed over.**
- The bars are the intent's and were fixed before slice 6. They are not this spec's to move.

### R4. The sample rule (48 spawns)

1. **The seen sets and their order (the "key order"):**
   - `evals/retrieval.toml`
   - `evals/retrieval-heldout.toml`
   - `evals/retrieval-heldout-3.toml`
   - `evals/retrieval-heldout-4.toml`

   That is the order the sets were made in, not alphabetical. Within each file, questions keep the order in which `load_eval_set` returns them, which is file order. `evals/calibration-offtopic.toml` is not a seen set for this check and is excluded.
2. **Unanswerable questions (U):** every question with `answerable = false`. **Expected 20**, with 6, 6, 4 and 4 per set.
3. **Answerable with a hit (H):** every answerable question for which `judge_eval.right_file_rank(judge.retrieve_for_judge(searcher, q.question), q.sources)` is not None, kept in key order.
   - Retrieval runs at the default ranking `file-rrf-v1`, over the index `index/docs-index.json` and the cached models in `models/` that are in this worktree (copied from the main checkout, digest D3). The tool records the index's sha256.
   - **Expected 56, with 19, 12, 11 and 14 per set.** These are the per-set counts in `runs/docs-abstention/02-baseline.md` (its pooled 56 and 17 misses), which slice 6 also reported.
   - **If U is not exactly 20, H is not exactly 56, or any per-set count differs, the tool writes nothing and exits non-zero. Stage 4 stops and reports.** The sample is not redrawn and no count is adjusted: retrieval is claimed unchanged, and a different count would disprove that.
4. **Parity: positions 1, 3, 5, ... 55 of H** (1-based; the first, then every second after it). That gives 28 questions: 10, 6, 5 and 7 per set, taking global positions 1-19, 20-31, 32-42 and 43-56.
5. **The sample S** is U plus the selected H, **in key order**, given run ids **`r001` to `r048`** in that order. Expected per set: 16, 12, 9 and 11.
6. **A smoke row `r049`** is the question at position 2 of H, the first hit **not** in S. It is in the key so the helper accepts it. It is used only for the stage 4 smoke spawn (section 10). It is **never scored** and the tool reports it separately. [SI-1]
7. **Stage 1's ids are restated.** In stage 1, `r001` was `tu01` (`evals/retrieval-heldout-3.toml`, unanswerable) and `r002` was `h15` (`evals/retrieval-heldout.toml`, answerable), as typed in `batch-1.txt` at commit `2eb98ec`. Under this rule both ids take new meanings, and the old rows survive only in git history and in APPROVAL_RECORD-4. **Stage 1's two replies are not counted in stage 5**: stage 5 spawns all 48 fresh.
8. **Total: 48 counted spawns in stage 5.** One smoke spawn goes before them. No reserves are used. Reruns follow R6.

### R5. How a judge error is counted

Every judge error **counts as a failure on the bar of the question it belongs to, and is also reported as its own number**. This matches `judge_eval.score_verdicts` line for line:

| Question | `JUDGE_ERROR` counts as |
|---|---|
| Unanswerable | a miss on bar 1 (not abstained) |
| Answerable, right file in top 5 | a miss on bar 2 (abstained) |
| Answerable, right file **not** in top 5 | on **neither** bar, because that question is on neither bar. Reported only in the judge-error count. |

What becomes a `JUDGE_ERROR`:
- Any reply that `judge-apply` rejects (exit 4, with the category from its stderr line).
- **A spawn that returns no reply text.** The tool treats this as an empty reply, so it becomes `EMPTY`, matching what `/aveto-judge` does for the operator.

What is **not** a judge error:
- A run id with no transcript at all, because the spawn never started (the helper refused, or the session ended first). That is an anomaly under R6, not a result.
- A batch voided under R6. Its rows are not counted at all.

The figure is reported as **`judge errors: N`**, split as **bar 1 / bar 2 / neither**. The tool prints that split, because the product's own label "(counted as failures on both bars)" does not say "neither". Whether to also correct that label in `judge_eval.py` is [SI-1: default no product change; this definition governs, and the owner may ask for the label fix]. The sample has no answerable question without a hit, so "neither" can only occur at stage 7.

Nothing in the product writes `JUDGE_ERROR`. Only the eval tool writes it into a verdicts file.

### R6. Batch rules: stop, void, continuation, rerun

A **batch** is all the counted spawns of one stage: `r001` to `r048` at stage 5, or the fifth set's ids at stage 7.

1. **The driver stops at the first anomaly it can see.** That means:
   - a helper refusal or a skill error
   - a spawn error or interruption
   - any sign of a judge tool call, for example a hook refusal message
   - a reply that asks the driver to act
   - a permission prompt the brief did not predict
   - the usage window ending

   The driver records the run id and what it saw, retries nothing, and hands back. Section 11 covers the driver.
2. **After the batch, the audit (section 4, `record`) voids the whole batch** if any judge transcript shows any of the following:
   - any `tool_use` block
   - an assistant `model` other than `claude-sonnet-5-5`
   - an offered tool list in `prefix.json` that is not the registered one: **7 names exactly as measured** if D1 is not approved, **0 names** if D1 is approved and applied (section 10)
   - a base-dir line or layout not as in R1
   - a payload that matches no key question
   - two transcripts for one run id
   - a missing transcript for a run id the driver invoked

   A voided batch is reported in full and not scored.
3. **One rerun per stage.** A voided or stopped batch may be rerun **once**, whole, all ids, in a new fresh-load session. Both batches are reported, and the rerun's score is the result. A second void or stop ends the stage with no result, so the slice stops.
   - Stage 7: this is the intent's one rerun.
   - Stage 5: the intent gives none, so applying the same rule to stage 5 is [SI-1: default one rerun, same rule as stage 7, for symmetry; the owner may set stage 5 to no rerun].
   - A rerun is **not in the plan**. It needs the budget check (rule 6), and the owner is told before a rerun that would cross the 3.4M ceiling [OWNER].
4. **A stop with no spawn affected** (the session ended before the next spawn started) may instead be **continued once** from the stopped run id in a new fresh-load session. Spawns already completed stand. This is not a rerun, but it uses the same single allowance. [SI-1]
5. A judge reply that is wrong, or a judge error, is **never** an anomaly and never voids anything. It is the measurement.

### R7. What is reported in the same run

The product's `eval --verdicts` prints per question: verdict, expected outcome and agree/diff. It also prints both bars against the 80% bar, judge errors, hard negatives abstained, never-abstain and the end-to-end figure. The tool (section 4, `diagnostics`) adds these, with these definitions:

- **Best score rule**: abstain when `top1 < 0.67`, where `top1` is the **primary signal** of `runs/docs-abstention/02-baseline-sweep.py`, meaning the highest, over the five returned files, of each file's best dense cosine similarity over **all** passages of that file. The bars are scored as for the judge.
  - The tool must reproduce **13/20 and 37/56** on the four seen sets (the recorded figures, `02-baseline.md` line 61) before stage 5 runs. If it does not, the rule's fifth-set figure is reported as "not reproduced", and the definition is not changed.
- **Over-abstention count**: answerable questions with a hit that the judge called `NOT_ANSWERABLE`. Judge errors are excluded and reported apart.
- **ANSWERABLE without a hit**: how often the judge said `ANSWERABLE` when the right file was not in the top five, out of how many such questions.
- **Judge errors** split as in R5, with their categories.
- **Rows that differ from the key**, with the full reply, in the run record only (R2 point 7).
- **Usage**: each judge spawn's peak (the largest `input + cache_creation + cache_read + output` over its requests), summed over the batch, plus in-equivalent tokens by the `01-measurement.md` formula, read from the transcripts. `usage.mjs` does not list forked spawns.

### R8. What the Freeze commit holds

Stage 4's output, plus stage 5's records:
- the judge agent file (after D1, if approved), `prompts/answerability-judge-v1.txt`, both judge skills and `seen_payload.py`
- `aveto_support/judge.py`, `judge_eval.py`, `__main__.py`
- `tools/judge_run.py`
- `judge-check/key/key.toml` (rows `r001` to `r049`), `judge-check/batch-1.txt`, `judge-check/sample-eval.toml`
- this section of this spec

After the freeze, only **data** is added: the fifth set's eval file (handed over by the support session), `batch-2.txt` and its key rows, verdicts, audit outputs and run records. Any change to a file in the first list after the freeze voids the freeze.

## 2. Trace: "Done means" to design

| Done-means line (intent) | Satisfied by | State |
|---|---|---|
| Starts from main; retrieval, ranking, corpus, embedding unchanged; judge code by `37c21d2` | Commit `5eb2a8a` (by files, digest D1). Stage 4 touches no retrieval file. The R4 count check (20 / 56 / 19-12-11-14) is the **observed** evidence that retrieval is unchanged. | done; checked at stage 4 |
| The program stays offline (a test) | `test_program_offline_no_model` plus the socket block, plus one named addition (section 12, T6) | stage 4 |
| Stage 1 measures before it builds | `01-measurement.md` | done |
| Judge is `claude-sonnet-5-5`, tools omitted, deny list ends `mcp__*`, hook unchanged, pinned by a test | Agent file plus `test_agent_definition` (byte-for-byte pin). **Already true; no new pin test.** D1 would change the pin string (section 10). | done; D1 [OWNER] |
| What the judge sees is reported; can it be reduced; stated in INV-5 | `01-measurement.md` context report; the reduction is D1 (tool schemas); the INV-5 content list is section 9; the stage 4 smoke re-measures after D1 | pass 2 / stage 4 |
| INV-4 / INV-5 exact words approved before any code that sends data runs | Pass 2 drafts them; the owner approves at the end of 3b [OWNER, rule 4]. Before that approval, no spawn beyond stage 1's two (section 11). | pass 2 |
| Registered up front: layout, grammar, thresholds, sample rule, judge-error counting | Section 1, R1 to R5 | **this file** |
| Seen-set integration check on the product's own path; failing stops the slice | Stage 5 (section 11). Verdicts go through the product's own `judge-apply` and are scored by the product's own `eval --verdicts` (section 4). R3 is the stop. | stage 5 |
| Freeze first, then the fifth set; label review; a different fresh QA scores once under the tool-use audit; one rerun | R8, section 11 (stages 6 and 7), R6 | stages 6-7 |
| Two bars, fixed | R3 | registered |
| Reported in the same run (never-abstain, best score rule, end to end, over-abstention, ANSWERABLE without a hit, diff rows with reply, usage plus transcript peak-sums) | Product `eval --verdicts` plus `judge_run diagnostics` (R7) | stage 7 |
| Security at adversarial; Release Gate tier 2 | Section 13 lists the inputs Security must attack; the depth binds [OWNER to lower] | stages 8-9 |
| README and status only after the verdict | Stage 10; section 12 names the stale lines from `01-scope.md` section 3 | stage 10 |
| Everything earlier still holds | Full regression (`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`); no product behaviour change | every stage |

## 3. Data model deltas

No product data model changes: no index, eval-schema or verdicts-format change. All deltas are **run data**, eval-only.

| Item | Change | Rationale |
|---|---|---|
| `runs/docs-answerability/seen-check/` (`key/key.toml`, `batch-1.txt`, `q/r001.txt`, `q/r002.txt`) | **removed** (`git rm -r`) at stage 4 | It is stage 1's two-row scaffold (digest D2), held under slice 6's directory name. Its content stays in git history at `2eb98ec`. |
| `runs/docs-answerability-2/judge-check/` | **new** directory; `seen_payload.py`'s `SEEN` constant points here [SI-1] | It keeps this slice's records under its own run directory, avoids a path collision with slice 6's 93-row `runs/docs-answerability/seen-check/` on its branch, and is named for both uses (the seen sample, then the gate set). Alternative for the owner's veto: keep the old path and rewrite its files in place, which needs no skill-helper edit. |
| `judge-check/key/key.toml` | **new**: one table per run id; fields `set` (eval file path) and `id` (eval question id); **no label, no answer**; header comments only (no top-level keys) | The helper reads table names only (membership control, unchanged). `set` and `id` let the tool map a run id to its eval question. Top-level keys would become "ids" to the helper, so metadata stays in comments: index sha256, the counts, the parity, the generating command. |
| `judge-check/batch-1.txt` | **new**: `r001` to `r049`, one line each, `<id> <question text>`, the eval question verbatim | The helper's question source (format unchanged). |
| `judge-check/sample-eval.toml` | **new**: a derived eval file. `pinned_commit` is the four sets' common commit (`3a83b669…`); the 48 sample questions are copied **verbatim** (all keys) in key order; `r049` is excluded. | It lets the product's own `eval --eval-file ... --verdicts ...` score the subset unchanged (`load_verdicts` requires a verdict for every question in the file). The eval ids are unique across the four sets, so no renaming is needed. |
| `judge-check/batch-2.txt` and key tables `r101` upwards | **added after the freeze** (stage 7), by `judge_run add-set` from the fifth set's file | So the frozen helper can serve the gate set without a code change (R8). `ID_RE` (`^r[0-9]{3}$`) is unchanged. |
| `judge-check/q/<id>.txt` | written by the helper per spawn (unchanged behaviour) | Committed with the stage's records as evidence. Deterministic. |
| `judge-check/<stage>/verdicts.toml` | **new per stage** (`stage5/`, `stage7/`, plus `-rerun` suffixes); format `aveto-judge-verdicts-v1` (unchanged): `id` (eval id), `verdict`, `input_sha256` | The product's scorer input. Written only by the tool. |
| `judge-check/<stage>/audit.md` | **new per stage**. For each spawn: run id, eval id, agent id, model, offered-tool count, `tool_use` count, base-dir line length, payload sha (first 16), reply sha (first 16), token or judge-error category, peak, in-equivalent. Then batch totals and the void decision. **No reply text.** | It is the tool-use audit and usage record. |
| `judge-check/<stage>/diffs.md` | **new per stage**: the full reply text for rows that differ from the key or are judge errors, **and nothing else** (R2 point 7) | The intent's "held in the run record only". |

**Key file sketch** (stage 4 generates it; nobody writes it by hand):

```toml
# docs-answerability-2 judge-check key. Membership only (the helper reads table names).
# Generated by: uv run python -m tools.judge_run derive-sample --out runs/docs-answerability-2/judge-check
# index sha256 <64 hex>; ranking file-rrf-v1; U=20 (6,6,4,4); H=56 (19,12,11,14); parity odd 1-based; r049 = smoke (H position 2), never scored
[r001]
set = "evals/retrieval.toml"
id = "a01"   # illustrative only; the real first row comes from the derivation
```

## 4. Service surface

### 4.1 Product (`aveto_support/`): no change

`judge.py`, `judge_eval.py` and `__main__.py` are used exactly as they stand at `5eb2a8a`. That keeps "the code path proven by slice 6" true and keeps Security's surface the one slice 6 reviewed. The only product decision this slice needs is the `judge-apply` output on `NOT_ANSWERABLE` (section 5), and the default there is no change either.

### 4.2 Skill helper (`.claude/skills/aveto-judge-seen/`)

| Function or line | Change | Invariant (unchanged) |
|---|---|---|
| `seen_payload.py`: `SEEN` | from `runs/docs-answerability/seen-check` to `runs/docs-answerability-2/judge-check` [SI-1, section 3] | Accepts one id matching `^r[0-9]{3}$` that is a table in `key/key.toml` and has a batch line. Otherwise it prints one `refused:` line and exits 2, so no judge starts. Fixed argv, no shell. It discards judge-input's stderr. |
| `seen_payload.py`: docstring `r001..r093` | becomes "a run id in the key (r001..r049 at the sample, r101 upwards for the gate set)" | text only |
| `SKILL.md`: `description` `(r001..r093)` | the same wording change | `context: fork`, `agent: aveto-answerability-judge`, one `!` injection line, `'$ARGUMENTS'` quoted, no `model` key (pinned by `test_skill_frontmatter_and_body`) |

Editing `SKILL.md` means **a fresh-load session is needed before any spawn** (intent constraint). One is needed anyway (section 11).

### 4.3 Eval-only tool: `tools/judge_run.py` (new file)

**Why a new file is justified.** Four "Done means" lines need something nothing in the tree does:
- deriving the sample from retrieval (R4)
- the tool-use audit over 48 forked transcripts (R6)
- the transcript peak-sums (R7), because `usage.mjs` does not list forked spawns
- the best-score and "ANSWERABLE without a hit" diagnostics (R7)

A model reading 48 transcripts of about 14k tokens each would cost about as much as the spawns themselves, and it would retype what it read. Slice 6's driver was left behind on purpose.

**Why it is not in `aveto_support/`.** It reads the harness's transcripts in `~/.claude/projects/`, which is not product behaviour. Keeping it outside the package keeps the product's import allow-list and its surface unchanged.

It is a module under a new top-level `tools/` directory, run as `uv run python -m tools.judge_run <command>`. mypy checks it through the tests' import. If stage 4 finds mypy does not follow that import, it adds `"tools"` to `[tool.mypy] files` in `pyproject.toml`, a one-line change that adds no dependency.

Imports are limited to the standard library (`argparse`, `contextlib`, `dataclasses`, `hashlib`, `io`, `json`, `os`, `pathlib`, `re`, `sys`, `tomllib`, `typing`) and `aveto_support.*`. That means **no `subprocess`, `socket`, `urllib` or `http`**, and a test pins it (section 12, T5).

| Function | Signature | Invariant |
|---|---|---|
| `derive_sample` | `(searcher: Searcher, root: Path) -> list[Row]` | Implements R4 exactly: the order, U, H, the parity, `r049`. Raises `SampleError` (exit 2, nothing written) unless U is 20 (6, 6, 4, 4) and H is 56 (19, 12, 11, 14). `Row` holds `run_id`, `set_path`, `eval_id`, `question` and a `role` of `sample`, `smoke` or `gate`. |
| `write_check_dir` | `(rows: list[Row], out: Path, index_sha256: str) -> None` | Writes `key/key.toml`, `batch-1.txt` and `sample-eval.toml`. **It refuses (exit 2) if `out/key/key.toml` already exists**, so the sample cannot be silently redrawn. The questions are copied verbatim from the eval files. All TOML strings go through one escaping function, and a round-trip test covers it. |
| `add_set` | `(eval_file: Path, out: Path, first: int = 101) -> list[Row]` | Stage 7 only, after the freeze. It appends the key tables and `batch-2.txt` for **every** question in the file, in file order, as `r101` upwards. It refuses if `batch-2.txt` exists or if the ids would pass `r999`. It reads no label. |
| `read_spawn` | `(jsonl: Path) -> Spawn` | Reads `<agent>.jsonl`, `<agent>.meta.json` and `<agent>.prefix.json`, and returns these fields: `agent_id`, `agent_type`, `models`, `offered_tools` (from `prefix.json` `toolNames`), `tool_uses` (the count of `tool_use` blocks in assistant content), `base_line_len`, `payload` (`<P>` per R1, else None), `reply`, `requests`, `peak` and `in_equiv`. `reply` is the concatenated `text` blocks of the last assistant message, or None if there are none. **It fails closed** (`TranscriptFormatError`) on any record shape it does not know. It never guesses. |
| `apply_reply` | `(question: str, payload_sha: str, reply: str \| None, *, embedder: Embedder, index: Path) -> Applied` | Writes `.aveto-judge/question.txt`, and writes `.aveto-judge/reply.txt` as `reply` or as an empty file when there is none. It then calls **`aveto_support.__main__.main(["judge-apply", "--index", ..., "--question-file", ..., "--input-sha256", payload_sha, "--verdict-file", ".aveto-judge/reply.txt"], embedder=embedder)` in-process**, with stdout and stderr captured. Results map as follows:<br>- **exit 0**: the token is read from the **last** stdout line, which must fullmatch the product's `Deciding signal: answerability judge verdict (ANSWERABLE\|NOT_ANSWERABLE) (prompt answerability-judge-v1, sha256 <PROMPT_SHA256>)`. For `NOT_ANSWERABLE`, stdout must equal exactly `no confident match\n` + that line + `\n`.<br>- **exit 4**: `JUDGE_ERROR`, with the category taken from the stderr line `judge error: <category>`.<br>- **any other exit, or any other stdout shape**: an anomaly (`ApplyError`). The batch is not scored.<br>It returns the token and category only. stdout (passages) is never stored. |
| `record` | `(subagents_dir: Path, check_dir: Path, eval_file: Path, stage_dir: Path, expect_tools: tuple[str, ...], *, embedder: Embedder, index: Path) -> RecordResult` | Takes every `agent-*.jsonl` in `subagents_dir`. Judge spawns are the ones whose `meta.json` `agentType` is `aveto-answerability-judge`; others are listed as "other agents" and not counted.<br>Attribution: it computes each key question's expected payload in-process (`format_judge_input(retrieve_for_judge(...))`) and maps transcripts to run ids by `sha256(<P>)`. `r049` is reported apart.<br>It applies every R6 void check. **If the batch is void, it writes `audit.md` only.** Otherwise it calls `apply_reply` per spawn and writes `verdicts.toml` (one entry per question in `eval_file`, which must be exactly the batch), `audit.md` and `diffs.md`. The diff rows are computed from the eval file's labels and the hit rule. |
| `diagnostics` | `(searcher: Searcher, eval_file: Path, verdicts: Path, audit: RecordResult \| None) -> str` | Prints R7's extra figures: the best score rule (both bars), over-abstention, ANSWERABLE without a hit, judge errors split three ways, and usage totals. `--self-check` reproduces 13/20 and 37/56 on the four seen sets (R7). |
| `check_transcripts` | `(subagents_dir: Path) -> str` | Read-only. It prints `read_spawn`'s fields per transcript, with no reply text and no token. Stage 4 uses it on stage 1's two transcripts (section 12, T4). |

**Scoring path (gap 5).** The tool turns replies into tokens through the product's `judge-apply`, the operator's own command, so the parse is the product's `parse_verdict` behind the product's transport checks and hash binding. The product scores:

```
uv run python -m aveto_support eval --eval-file runs/docs-answerability-2/judge-check/sample-eval.toml \
    --verdicts runs/docs-answerability-2/judge-check/stage5/verdicts.toml
```

That command prints both bars with `bar_met`, so MET at 80% means at least 16/20 and at least 23/28 (R3). Stage 7 uses the same command with the fifth set's eval file. The `eval` exit code is the retrieval gate on that file and is not the judge's result. That is the product's existing behaviour.

**Offline.** `tools/judge_run.py` makes no network call, starts no process and calls no model. It reads local files and calls product functions. The tests prove it under the same process and socket blocks as the product (section 12, T5 and T6).

## 5. `judge-apply` on NOT_ANSWERABLE versus "exactly `no confident match`"

**Observed (code and test):** `render_applied` prints two lines:
1. `no confident match`
2. `Deciding signal: answerability judge verdict NOT_ANSWERABLE (prompt answerability-judge-v1, sha256 24b244d2…)`

It prints no passage, path or reason, and `test_apply_not_answerable_exact` asserts exactly this. The intent says "prints exactly `no confident match` and no passages".

| Option | Effect |
|---|---|
| **A. Keep the code. The intent's "exactly" is read as: the only answer-bearing line is exactly `no confident match`, and one fixed deciding-signal line follows it. That line names the token, the prompt id and the prompt hash, and carries no question or passage text.** | No product, test or Security change. The operator can tell a judge abstention from a retrieval failure or a judge error, and the prompt version is on screen (the audit trail the product has). ADR 0007, slice 5's approved design, also printed "exactly `no confident match`, no passages, and the deciding signal". |
| B. Drop the signal line on `NOT_ANSWERABLE` (stdout is exactly `no confident match\n`) | Changes `judge.py`, its test and (for symmetry) the ANSWERABLE path. It loses the provenance line, and it is a product change after slice 6's review. |
| C. Move the signal to stderr | `/aveto-judge` shows only stdout, so the operator would never see it. |

**Recommended: A** [SI-1]. Two consequences:
- The pass 2 INV-4 content (section 9) **states the two-line output in full**, so the owner approves the exact behaviour with the words at rule 4. If the owner reads "exactly" strictly, that is the moment to veto, and B becomes a stage 4 change of about two files.
- The intent's wording is the owner's text. I record the reading and do not edit it.

## 6. Adapter boundaries

| Boundary | Deterministic side | Model side | Default / placeholder behaviour |
|---|---|---|---|
| Answerability judge (operator path) | `judge-input` (payload, sha256 on stderr), `judge-apply` (transport checks, hash binding, `parse_verdict`, render) | The `aveto-answerability-judge` subagent in the **operator's own** Claude Code session, spawned by `/aveto-judge` | The program has no model client at all; nothing can call a model. A missing or empty reply gives `EMPTY`, then exit 4 and `judge error`, never passages and never a pass-through. Tests feed reply bytes directly (`apply(...)` in `tests/test_judge.py`); no key, no network. |
| Answerability judge (eval path) | `seen_payload.py` (id check, then `judge-input`), `tools/judge_run.py` (audit, `judge-apply` in-process, scoring through `eval --verdicts`) | The same subagent, spawned by the forked skill `/aveto-judge-seen <id>` with the payload **injected by the harness** (R1) | A missing transcript is an anomaly (R6). A transcript with no reply is `EMPTY`, so a judge error. An unknown transcript shape raises `TranscriptFormatError` and nothing is scored. Tests use synthetic transcripts (section 12). |
| Embedding model (unchanged) | `Searcher` | the local ONNX model | `FakeEmbedder` in tests (existing) |

The model never produces, selects or alters shown text. On `ANSWERABLE`, `judge-apply` prints `retrieve`'s output unchanged plus the signal line (`test_apply_answerable_is_retrieve_plus_signal`). On `NOT_ANSWERABLE`, it prints section 5's two lines.

## 7. Audit, feedback and usage events

The product has no event store. Its audit trail is what it prints, plus the run records. Every state-changing function is listed here.

| Event | Emitted from | Fields | Kind |
|---|---|---|---|
| Deciding signal (judged result) | `judge.render_applied`, last stdout line of `judge-apply` exit 0 | verdict token, prompt id, prompt sha256 | audit, operator-visible, existing |
| Judge error | `__main__._judge_apply`, stdout `judge error`, stderr `judge error: <category>`, exit 4 | one of 11 fixed categories (`judge.py` lines 31-41) | audit, existing |
| Payload identity | `__main__._judge_input`, stderr `input sha256: <hex>` | sha256 of the payload | audit, existing |
| Transport cleanup | `judge.remove_stale_reply` (`judge-input`) and `judge.delete_transport_files` (`judge-apply`, every path) | none; a failure is the `NOT_DELETED` judge error | state change on local temp files, existing; no new event needed |
| Seen-question file written | `seen_payload.prepare` | `<judge-check>/q/<id>.txt` | state change, eval-only, existing |
| Sample derived / gate set added | `judge_run.write_check_dir`, `judge_run.add_set` | key header comment: generating command, index sha256, counts, parity | audit, new; the files are committed |
| Batch recorded | `judge_run.record` → `audit.md` | per spawn: run id, eval id, agent id, model, offered-tool count, `tool_use` count, base-line length, payload sha16, reply sha16, token or category, peak, in-equivalent; per batch: void decision and reason, anomalies, other agents, totals | audit and usage, new |
| Differing replies | `judge_run.record` → `diffs.md` | run id, eval id, expected, verdict, full reply text | feedback (run record only), new |
| Verdicts | `judge_run.record` → `verdicts.toml` | `id`, `verdict`, `input_sha256` (existing format) | input to the product's scorer |

## 8. Integration points

- `aveto_support.search.Searcher`, `judge.retrieve_for_judge`, `judge.format_judge_input`, `judge.input_sha256` are used by `judge_run` to derive the sample and attribute transcripts. They are not modified.
- `aveto_support.__main__.main(["judge-apply", ...], embedder=...)` is used by `judge_run.apply_reply`, so the product's own path turns each reply into a token. Not modified.
- `aveto_support.evaluate.load_eval_set` and `judge_eval.right_file_rank` are used for the R4 order and the hit rule, the same rule `eval` uses. Not modified.
- `aveto_support.embed.OnnxEmbedder` is loaded once by the tool and passed to `main` for every call.
- `aveto_support.__main__ eval --verdicts` is the scorer. Not modified.
- The harness's transcripts are read-only, in `~/.claude/projects/<slug>/<session>/subagents/`. **This is the one external format the slice depends on.** It is harness-internal and may change between app versions. `read_spawn` fails closed on an unknown shape. Stage 4 checks the reader against the two stage 1 transcripts.
- `runs/docs-abstention/02-baseline-sweep.py` is the **definition** of the best-score signal (R7). The tool reimplements the per-file top-1 in a few lines and proves equality by the self-check. It does not import a run script.

## 9. INV-4 and INV-5: what pass 2 must draft (content only, no words here)

The exact words are pass 2's draft and the owner's approval at the end of stage 3b [OWNER, rule 4]. SI-1 and SI-2 do not cover them. Until they are approved, **no judge spawn beyond stage 1's two may run**, including the stage 4 smoke. Below is what the words must cover, not the words themselves.

**INV-4 must say:**
1. `retrieve` is unchanged. It still never abstains, and it returns only verbatim passages with path, heading and line range. The existing retrieval enforcing tests stay listed.
2. A model, namely the judge pinned by full id in the agent file and run only in the operator's attended session, may judge whether the shown passages answer the question, **by returning only a verdict**. The product keeps the token from the last non-empty line (R2). The reason and earlier lines are never shown or stored by the product. The model never produces, selects or alters shown text. This replaces "a model may be used only to rank passages and to decide confidence" with a sentence that also allows the verdict.
3. `judge-apply`'s output, in full:
   - On `NOT_ANSWERABLE`: `no confident match` plus the one deciding-signal line (section 5), and no passage, path or reason.
   - On `ANSWERABLE`: `retrieve`'s output unchanged plus the signal line.
   - On any judge error: exit 4 and `judge error`. Never passages, never a pass-through.
4. Enforcing tests to name: `test_parse_verdict_table`, `test_verdict_carries_only_the_token`, `test_reason_never_leaves_parser`, `test_apply_not_answerable_exact`, `test_apply_answerable_is_retrieve_plus_signal`, `test_apply_judge_error_shows_nothing`, `test_unjudged_outputs_never_look_judged`, `test_agent_definition`, `test_deny_hook_refuses_every_input`, `test_prompt_file_hash_pinned`.

**INV-5 must say:**
1. **The program**: `ingest`'s two GET kinds are unchanged. `retrieve`, `eval` (with or without `--verdicts`), `judge-input` and `judge-apply` make no network call, start no process and call no model. The enforcing tests are `test_program_offline_no_model` (plus T6, section 12), the autouse socket block and `test_judge_modules_import_allow_list`. "No question, passage or user text ever leaves the machine" becomes true **of the program**.
2. **The operator's session**: when the operator runs the judge step (attended, by typing it), the session sends data to the model provider of that session (Anthropic, APPROVAL_RECORD-3) **and nowhere else**. What it sends:
   - the question and the shown passages, with their paths, headings and line ranges; the payload is inspectable first, via `judge-input`
   - the judge's system prompt
   - **the session context the harness attaches to the judge, as measured on 2026-10-12** (`01-measurement.md`; Reply 1 D3, adopted as content):
     - (a) the project instruction files `CLAUDE.md` and `AGENTS.md`, **as read from the main checkout path**, so a different checkout sends different text
     - (b) the user's email address
     - (c) git state: the current branch, the git user name, the working-tree status and the five most recent commit subjects. These will include this slice's own commit subjects.
     - (d) environment lines: working directory, platform, shell, OS version, scratchpad path, model id, date and organisation id
     - (e) on the eval path only, the harness's base-dir line (R1), which carries the local path
3. **Tool schemas are excluded from the list.** They are harness content, not session data, and D1 would remove them. The words must not depend on them.
4. **The list is not claimed complete.** About 2.7k of the 14.2k first-request tokens were not itemised (wire framing, the tool-definition envelope and the like). The words must say the list is "as measured", that the session may carry more, and that it is "whatever the operator's session carries". No setting that removes the session context was found, and the words should say that too.
5. **Stage 4 re-measures** items (a) to (e) and the unitemised remainder after D1 (or with D1 declined), from the smoke spawn's transcript (section 10). If the re-measure finds an item not in the approved words, the Orchestrator stops and brings it to the owner before stage 5. The approved words are not edited by anyone else.

**Also in the 3b packet, as the owner's questions:**
- Rule 6 scope (`01-scope.md` approval C): is the session context, including email and git subjects, within "Anthropic as data processor through my own session"? [OWNER]
- Section 5's reading of "exactly". [SI-1 default A; the owner may veto here]

## 10. D1: seven harness tools added to `disallowedTools` [OWNER]

**Not applied and not assumed approved.** APPROVAL_RECORD-2 does not cover it (`01-scope.md` 2.3), and the owner asked for the exact diff first (STANDING_INSTRUCTIONS).

**Where it fits:** stage 4, before any other stage 4 edit is committed and after the baseline run (section 12, step 1). The sequence:
1. The AI Engineer writes the exact diff to `runs/docs-answerability-2/D1-diff.md` without applying it. The diff has two hunks:
   - `.claude/agents/aveto-answerability-judge.md`, `disallowedTools` line: insert `DesignSync, ListPlugins, ListSkills, SearchPlugins, SearchSkills, SuggestPluginInstall, SuggestSkills, ` **immediately before `mcp__*`**, so the list still ends in `mcp__*`. No `tools:` key, `model:` unchanged, hook unchanged, prompt unchanged.
   - `tests/test_judge_artefacts.py`, `DENY_LIST`: the same seven names, in the same place, so the byte-for-byte pin follows.
2. The Orchestrator puts the diff in front of the owner, with the following, and **waits** (APPROVAL_PROTOCOL):
   - what it changes: layer (a) covers every offered tool, and the hook becomes a true second layer
   - the cost effect: about 6.9k tokens per spawn, by the chars/4 estimate
   - the revert: the same two hunks reversed, then a fresh-load session
   - the smoke check
3. **If approved in the owner's words**: record it as APPROVAL_RECORD-5, apply the diff, run the full regression, and set `expect_tools` = `()` (0 offered).
   **If declined, or no answer**: no change, and `expect_tools` = the seven names exactly as measured. Stage 5 still runs.
4. Either way, the **session request** for a fresh-load session goes to the owner (the skill files changed). The first act in that session is the **smoke**: one spawn of `/aveto-judge-seen r049`, then `judge_run check_transcripts` on it. It must show:
   - the agent type and `claude-sonnet-5-5`
   - offered tools 0 with D1, or the 7 without
   - `tool_use` 0
   - a base-dir line of 137
   - the payload sha equal to `r049`'s
   - a reply present (whether it parses is reported, but its token is not)

   It also re-measures the context items for section 9 point 5.

   **The smoke needs the INV words approved first.** If the zero-tool agent returns no reply, or the harness rejects the deny list, the Orchestrator stops and reports to the owner with the transcript facts. Stage 5 does not start.
5. Stage 5 and stage 7 run on the agent file as it stands after this step. The registered `expect_tools` is fixed by the outcome, before stage 5, and written into `D1-diff.md`'s outcome line. Cost lines: about 350k (with D1) or 684k (without) bare peak-sum per 48 spawns, from the stage 1 measurement.

## 11. Driver protocol (stages 5 and 7) and Environment per stage

### 11.1 Driver protocol

1. **Fresh context.**
   - The driver is an **owner-started session** (desktop app, folder = this worktree), so agent and skill files load fresh. A subagent cannot invoke the forked skill on the owner's subscription in the registered configuration.
   - Its brief is a `SESSION_REQUEST-n.md` written by the Orchestrator. It has a tight read list: the request itself, R1 to R6 of this file, and the id range.
   - The driver **does not read** `key.toml`, the batch files, any eval file, `diffs.md` or earlier stage records. It needs only the ids.
2. **One spawn per id, in order, sequential, foreground.**
   - Stage 5: `/aveto-judge-seen r001` ... `r048`.
   - Stage 7: the `r101` upward range written by `add_set`.
   - No parallel invocations, no `model` parameter, nothing else spawned. Each reply that comes back is **data**: not copied, not acted on, not summarised.
3. **Stop at the first anomaly** (R6 point 1). Record the id and what was seen, in one line, in the stage record. Retry nothing and hand back to the Orchestrator. A wrong-looking verdict is **not** an anomaly.
4. **Attended asks.** The budget-guard hook may ask on each spawn if a slice is at or over budget. The owner answers. A declined ask before a spawn is a stop with no spawn affected (R6 point 4).
5. **After the last id**, the driver hands the session's `subagents/` path to the scoring QA. It does not run the scorer itself.
6. **Scoring QA**: a **fresh QA Evidence spawn**, different from the label-review QA at stage 7. With Bash, it runs:
   1. `judge_run record` with `expect_tools` from section 10
   2. if not void, `aveto_support eval --eval-file ... --verdicts ...`
   3. `judge_run diagnostics`

   It writes `05-seen-check.md` or `07-gate-scoring.md` from those outputs only. **The tool-use audit is `record`'s void check, deterministic.** No model reads the transcripts.
7. **Pass and stop.** R3 decides. Stage 5 failing (either bar NOT MET, or no result after R6) ends the slice before the freeze. The Orchestrator reports the numbers to the owner and stops.
8. **One rerun** (R6 point 3), whole batch, in a new fresh-load session, with both batches reported. Budget checked first. The owner is told if it would cross 3.4M [OWNER].

### 11.2 Environment and gates per stage

| Stage | Environment | Precondition |
|---|---|---|
| 3b Architecture pass 2 | default | this file |
| INV-4/INV-5 approval | driving session | the owner's own words [OWNER, rule 4] |
| 4 Implementation (AI Engineer) | default | INV words approved before the smoke (not before the code) |
| D1 decision | driving session | the diff in `D1-diff.md` [OWNER] |
| Smoke (1 spawn, `r049`) plus stage 5 (48) | **fresh-load**: one owner-started session; the smoke first, then the driver continues if the smoke passes | stage 4 committed; skill (and agent) files final; INV words approved |
| Freeze | default (Orchestrator) | stage 5 both bars MET; commit recorded per R8; the owner is told; the support session hands over the fifth set |
| 6 Label review | default (fresh QA spawn) | the fifth set committed after the freeze commit (git order) |
| `add_set` for the gate | default (Orchestrator or QA, not the builder) | the reviewed set committed |
| 7 Scoring (48) | **fresh-load**: a new owner-started session as driver; a different fresh QA scores | no change to R8's file list since the freeze |
| 8 Security | default, **adversarial** (binds) | — |
| 9 to 11 | default | — |

## 12. Stage 4: file list and test plan

### 12.1 Order of work

1. **Baseline first, on the unchanged tree.** Run the full regression, `uv run pytest tests/test_judge_seen_skill.py -v` and `uv run pytest -m model tests/test_judge_seen_skill.py -v`, and record in `04-implementation.md` which tests fail and why. `01-scope.md` 2.8 *reads*, without running, that `test_ids_match_key` (default) and `test_largest_payload_is_below_inline_ceiling` (`model`) fail, and that `test_prepare_writes_question_only` passes. The plan's "3 failing" predates stage 1. **The run decides, not either reading.**
2. Write `D1-diff.md` and hand to the Orchestrator (section 10). Continue with the rest meanwhile; do not apply D1.
3. Build `tools/judge_run.py` and its tests. Run `check_transcripts` on stage 1's two transcripts (T4).
4. Run `derive-sample` (real index and models). This either writes `judge-check/` or stops on a count mismatch (R4).
5. Run `diagnostics --self-check` (13/20, 37/56).
6. Move the helper's path, remove the old directory, rebuild the seen-skill tests, add T6.
7. Run the full regression plus `-m model`. Make one commit (two if D1 is applied separately after approval).

### 12.2 Files (stage 4)

| # | File | Change |
|---|---|---|
| 1 | `tools/judge_run.py` | new (section 4.3) |
| 2 | `tests/test_judge_run.py` | new (T1 to T5) |
| 3 | `.claude/skills/aveto-judge-seen/seen_payload.py` | `SEEN` path, docstring |
| 4 | `.claude/skills/aveto-judge-seen/SKILL.md` | description id range |
| 5 | `tests/test_judge_seen_skill.py` | `SEEN` path, three tests rebuilt, one added (S1 to S4) |
| 6 | `tests/test_judge.py` | T6 (offline test addition) |
| 7 | `runs/docs-answerability-2/judge-check/key/key.toml`, `batch-1.txt`, `sample-eval.toml` | generated by the tool, never hand-written |
| 8 | `runs/docs-answerability/seen-check/**` | removed |
| 9 | `.agentic/LOCAL_COMMANDS.md` | add `judge-input`, `judge-apply`, `eval --verdicts`, exit code 4 and the `tools.judge_run` commands, each only once run [SI-1: stage 4, since it runs them; fallback stage 10] |
| 10 (conditional) | `pyproject.toml` | `"tools"` in mypy `files`, only if needed |
| D1 (conditional, [OWNER]) | `.claude/agents/aveto-answerability-judge.md`, `tests/test_judge_artefacts.py` | only after approval |

Code files: 6, plus up to 3 conditional. The rest are generated data and records. That is within the 10-file line in `01-scope.md` section 1. **No `aveto_support/` file changes.**

### 12.3 Tests

**`tests/test_judge_seen_skill.py`** (gap 3):
- **S1** `test_ids_match_key` (rebuilt):
  - batch ids equal key tables, unique, all `^r[0-9]{3}$`
  - `batch-1.txt` holds exactly `r001` to `r049`, contiguous
  - every key table has exactly `set` and `id`, and that pair exists in the named eval file
  - `batch-2.txt`, once it exists, holds only `r101` upwards
- **S2** `test_prepare_writes_question_only` (rebuilt): `prepare("r001")` writes exactly the `question` of the eval entry that `[r001]` names (cross-checked against the eval file, not hard-coded).
- **S3** `test_largest_payload_is_below_inline_ceiling` (`model`, rebuilt): `len(sizes)` equals the number of key ids, not 93.
- **S4** `test_sample_derivation_reproducible` (`model`, new): `derive_sample` on the real index reproduces the committed key, batch and `sample-eval.toml` byte for byte.
- `test_refuses_id_not_in_key`, `test_refuses_bad_ids`, `test_skill_frontmatter_and_body` and `test_refuses_wrong_argument_count` are unchanged. `r094` stays absent from the key.

**`tests/test_judge_run.py`** (new; `work`-style fixtures, `FakeEmbedder`, synthetic transcripts in `tmp_path`, no network, no process):
- **T1, derivation:**
  - order, parity and `r049` on a synthetic four-set fixture
  - refusal (nothing written) when U, H or a per-set count is off
  - refusal when the key already exists
  - TOML round-trip of `sample-eval.toml` equals the source entries
  - `add_set` numbering, refusals, and that it reads no label
- **T2, `read_spawn`:**
  - a well-formed synthetic transcript gives every field, including peak and in-equivalent by the `01-measurement.md` formula
  - each unknown shape raises `TranscriptFormatError`
  - a transcript with a `tool_use` block is counted
  - the base-dir line is parsed per R1, and a wrong form is caught
- **T3, `record` void rules:** one test per R6 point 2 condition (tool use, wrong model, offered tools differing from `expect_tools`, bad layout, unknown payload, duplicate, missing id). Each must void the batch and write no `verdicts.toml`. Non-judge agents are listed and not counted. `r049` is reported apart.
- **T4, `apply_reply` and scoring:**
  - replies from `test_parse_verdict_table`'s cases give the product's tokens and categories
  - no reply gives `JUDGE_ERROR` / `EMPTY`
  - a payload sha that does not match gives `JUDGE_ERROR` / `different input`
  - an unexpected stdout shape raises `ApplyError`
  - the end-to-end synthetic batch's `verdicts.toml` is accepted by `eval --verdicts` and gives the expected bars
  - `diffs.md` holds only differing and error rows
  - the R5 three-way split
  - (manual step, not a test) `check_transcripts` on stage 1's real transcripts reports 7 tools, 0 `tool_use`, line 137, peaks 14,218 and 14,299, model `claude-sonnet-5-5`. Any difference is a reader bug to fix before stage 5.
- **T5, `test_judge_run_offline_and_imports`:**
  - an AST import allow-list for `tools/judge_run.py` (section 4.3; no `subprocess`, `socket`, `urllib`, `http`)
  - the T4 end-to-end batch run under the same `subprocess.Popen` / `os.*` spawn blocks as `test_program_offline_no_model`, with the socket block active

**`tests/test_judge.py`:**
- **T6** (gap 9). `test_program_offline_no_model` plus the autouse socket block **does** satisfy the Done line in substance: it runs `retrieve`, `eval`, `eval --verdicts`, `judge-input` and `judge-apply` with process spawning blocked, under the socket block, with no model client in the code. The cached-model case is covered by `test_retrieve_is_offline_with_cached_model`. One gap is that the test does not show the network half in its own body, so removing the conftest fixture would not fail it. **Add** at the top of that test an assertion that `socket.create_connection(("192.0.2.1", 80))` raises (the guard is active), so the test fails if the guard is ever removed. [SI-1: the default is this one-assertion addition; the alternative is to accept the existing test as is.]

**Not added:** a new agent pin test (`test_agent_definition` already pins the file). No eval cases change: the seen sets are read, never edited.

**Live checks** (not pytest): the smoke (section 10), stage 5, stage 7.

## 13. Rollback plan

Nothing reaches `main` until the owner merges [OWNER]. Before a merge, rollback means not merging, or `git revert` of the slice commits on the branch in reverse order.

After a merge:
1. **Disable the operator path, no code revert needed.** `git rm -r .claude/skills/aveto-judge/` and commit. The operator can no longer start the judge. `judge-input` and `judge-apply` remain offline and inert without a reply, and `retrieve` is untouched.
2. **Full revert.**
   - `git revert -m 1 <merge-commit>`, then run the full regression.
   - Then **INV-4/INV-5** return to their pre-slice text. That is a safety-control text change, so it needs the owner's words (rule 4) before the revert lands; the revert must not be applied on an assumed approval.
   - README and `CURRENT_MVP_STATUS.md` return with the revert.
3. **D1 only:**
   - Reverse the two hunks in `D1-diff.md` (agent file and `DENY_LIST`), with the owner's approval (deny list).
   - Run `uv run pytest tests/test_judge_artefacts.py`.
   - Start a fresh-load session before any spawn.
4. **Eval data only:** `git rm -r runs/docs-answerability-2/judge-check/`. No product effect.
5. There is nothing to undo outside git. The program writes nothing persistent but `.aveto-judge/` (gitignored, deleted on every `judge-apply`). Transcripts in `~/.claude/projects/` are the owner's session data and are not touched by any rollback.

## 14. Risks, open questions, and the decisions register

### 14.1 Risks and open questions

- **The operator path retypes the payload.** `/aveto-judge` step 3 has the main session pass `judge-input`'s stdout to the judge as the Agent prompt. That is a model copying text, the thing L36 says the eval path must avoid. `judge-apply`'s hash binds the verdict to the payload the *program* built, not to what the judge *saw*. The forked-skill route avoids this only for fixed run ids, because free question text cannot go into a `!` shell line safely. This was **not** measured by stage 5 or 7 (they use the eval path). **For Security (adversarial) and the owner.** Not changed in this slice.
- **The transcript format is harness-internal.** `read_spawn` fails closed, and T4's manual check against stage 1 catches drift before stage 5. An app update between stages 5 and 7 could break `record`. A fix to the reader after the freeze changes an R8 file, so it would need the owner's word. Mitigation: run stage 7 promptly, and check `check_transcripts` on stage 7's first spawn.
- **The `CONTROL` and `MULTI_TOKEN` rules versus Sonnet's style** (R2 points 3 and 5). Kept. Stage 5 shows the cost, and the result does not change the rule.
- **The stage 1 replies' parse status is unknown.** It is reported by T4's manual check as parse OK or category only, and is not counted.
- **Budget.**
  - A rerun is not in the plan (`01-scope.md` section 1).
  - Without D1, stages 5 and 7 run about 0.45M over their lines at slice 6's 1.5x all-in ratio, still inside 3.4M.
  - The smoke adds one spawn (about 7 to 14k).
  - The tool replaces model-read audits, which lowers driver and QA cost.
- **Tier.** Tier 2 versus the tier-3 trigger (a safety control and user data via a session) is the Release Manager's to justify at the gate (`01-scope.md` section 3).
- **Stale lines** for stage 10 are listed in `01-scope.md` section 3, including the stale `wordpiece_golden.json` line in `CURRENT_MVP_STATUS.md`.
- **Model proposal rule.** Not triggered. No new model: Sonnet is approved (APPROVAL_RECORD-2), hosted through the operator's session (no weights, revision or licence file to pin), and piloted (51/56 in slice 6's pilots). Stage 5 is the pre-registered seen-set check.

### 14.2 Defaults adopted under SI-1 (for the next digest; the owner vetoes by exception)

| # | Decision | Default | Section |
|---|---|---|---|
| A1 | The eval record keeps full reply text only for rows that differ from the key or are judge errors | yes | R2 point 7 |
| A2 | Smoke row `r049` (H position 2), never scored | yes | R4 point 6, 10 |
| A3 | Stage 5 gets the same one-rerun rule as stage 7 | yes | R6 point 3 |
| A4 | A stop with no spawn affected may be continued once (shares the allowance) | yes | R6 point 4 |
| A5 | The product's "judge errors (counted as failures on both bars)" label is not changed; R5 governs and the tool prints the split | no product change | R5 |
| A6 | Seen-check data moves to `runs/docs-answerability-2/judge-check/` (helper `SEEN` and `SKILL.md` description change) | move | 3, 4.2 |
| A7 | Gate set served by the same helper as `r101` upwards in `batch-2.txt` | yes | 3 |
| A8 | Eval-only tool `tools/judge_run.py`; replies become tokens through in-process `judge-apply` | yes | 4.3 |
| A9 | `judge-apply` `NOT_ANSWERABLE` output kept as two lines; the intent's "exactly" read as the answer-bearing line | option A | 5 |
| A10 | Best score rule = `top1 < 0.67` on the docs-abstention primary signal, with a self-check | yes | R7 |
| A11 | The offline test gets one in-body socket assertion (T6) | yes | 12.3 |
| A12 | `.agentic/LOCAL_COMMANDS.md` updated at stage 4 | yes | 12.2 |
| A13 | The scoring QA runs the tool; no model reads transcripts | yes | 11.1 |

### 14.3 The owner's (not adoptable)

- **INV-4 and INV-5 exact words** (rule 4), end of 3b. The smoke and every spawn wait for them.
- **D1 diff** (deny list of a safety control), stage 4.
- **Rule 6 scope**: does the session context (email, git subjects, project files) fall within APPROVAL_RECORD-3?
- **Budget**: any rerun or spend that would cross the 3.4M ceiling.
- **Security depth**: lowering it below adversarial.
- **Tier**: stated by the Release Manager. It is the intent's call.
- **Push, merge and deploy**, and any post-merge revert of INV text.
- **The intent's own wording** ("exactly"; "cherry-picking `37c21d2`"; "11k"): recorded, not edited.

## 15. Hand off

- **Next:** Software Architect pass 2 (stage 3b), standard, est. 90k. It drafts the INV-4/INV-5 words from section 9, ADR 0008 (a new file, Proposed), the `docs/ARCHITECTURE.md` update (judge commands, the operator and eval paths, the adapter boundary, the diagram), and the rule 4 approval packet (including section 9's two owner questions).
- **Then:** AI Engineer (stage 4), owning every file in 12.2. The Orchestrator owns the D1 packet and the session request.
- No Frontend or Backend work.

