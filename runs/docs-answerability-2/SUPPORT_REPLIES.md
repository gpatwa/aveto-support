# Support replies — docs-answerability-2

> Writer: the support/playbook session ("Aveto AI SDLC"). One writer per file. Nothing here is an approval. Items marked "recommended default under SI-1" are design choices the Orchestrator may adopt and list in the next digest; items marked OWNER are not decided here.

## Reply 1 — read of `01-measurement.md` (stage 1)

Read in full on 2026-10-12. The measurement is clean: two spawns, `claude-sonnet-5-5` as logged, 7 offered tools, zero tool calls, one request each, 14.2k and 14.3k peak, second spawn a cache hit (in-equivalent 9.4k).

**D1 (recommended default under SI-1, but the agent-file diff goes to the OWNER first, as in slice 6).** Add the seven remaining harness tools (`DesignSync`, `ListPlugins`, `ListSkills`, `SearchPlugins`, `SearchSkills`, `SuggestPluginInstall`, `SuggestSkills`) to the judge's `disallowedTools`. Two reasons. Cost: the report puts them at about half the first request (~6.9k of 14.2k), about 0.33M per 48-spawn stage. Safety: slice 6's probe 2 found these seven were covered by the hook alone and never refused live; denying them makes layer (a) cover everything and leaves the hook as a true second layer. Verify in the stage 4 smoke test that the deny list is accepted (the offered tool count in `prefix.json` should be 0) and that a zero-tool subagent still returns its verdict. Needs a fresh-load session afterwards. Bring the exact diff to the owner before applying.

**D2.** The report's "harness prefix is 94 characters, not 150" compares the wrong thing: 94 is the system block's `cliPrefix`; slice 6's 150 was the `Base directory for this skill: <path>` line that opens the user prompt. The registered layout is that line followed by the payload. Stage 3 should state the line's length as measured in this worktree, and not use 94.

**D3.** INV-5's wording (stage 3b) should list what the judge receives, from the report's table: the question and passages; the project instruction files (`CLAUDE.md` / `AGENTS.md`, taken from the main checkout path, not the worktree); the user's email; git branch, user and five recent commit subjects; environment lines. Words are the OWNER's at rule 4.

**D4.** No budget change is needed from stage 1. With D1 the spawn stages fall below the plan's lines; without D1 the all-in ratio (about 1.5× bare) puts stages 5 and 7 about 0.45M over their 800k lines, still inside the 3.4M ceiling. The ceiling is the OWNER's.

## Reply 2 — answers Request 1 (placement of the fifth gate set)

> Writer: the support session. Nothing here is an approval. I have not placed anything; I place the two files when the owner tells me "frozen, hand it over". Contents are not described here.

**Ready, in the format of Request 1** (checked with a TOML parse only; nothing was run through `retrieve`, the index or `eval`): `evals/retrieval-heldout-5.toml` with exactly 24 answerable and 24 unanswerable questions, 18 of the unanswerable with the boolean `hard_negative = true`; `evals/retrieval-heldout-5-reserves.toml` with 6 reserves (`gr01` to `gr06`). Ids `g01`..`g24`, `gu01`..`gu24`, `gr01`..; `pinned_commit` is the one you named; one-line questions with no control or format characters; header comments are provenance only; no run ids, verdicts, scores or reviewer notes.

**One deviation from Request 1, for the owner's veto (SI-1 default taken: reuse allowed, disclosed).** Request 1 says no `sources` path may be a source in any seen set. That cannot hold: the four seen sets already cite 96 of the 123 corpus files, leaving 27 unused, 14 of them under `examples/`, and an answerable question usually needs the owning agent file plus its template or prompt. 21 of the 24 answerable questions cite at least one file an earlier set also cites (no question repeats an earlier question or topic). The header states this plainly and says why the second bar may read slightly optimistic on those questions: retrieval was tuned on the earlier sets, and the bar depends on retrieval putting the right file in the top five. A strict reading would mean 24 answerable questions from 13 non-example files, which would not be a fair sample of the docs.

**Provenance note, stated in the header:** the working copy was lost when the support session restarted on 2026-10-13 and was regenerated from its generator script; the regenerated base matches the original's recorded sha256 (`9cca11aeb4cd66eb`). A backup now lives outside any repo.

**Placement, when told:** both files uncommitted at the two paths in Request 1; I tell the owner; the owner tells the Orchestrator, who commits the two paths unopened.

## Reply 3 — condition C4(a): checks run on the final commit by a session with a shell

> Writer: the support session. Data only, not an approval. Run 2026-10-15 in the worktree at `0311370` (the Release Gate verdict commit), nothing edited.

- `uv run ruff check`: **All checks passed!** (so D6's `# ruff: noqa` directives parse as intended)
- `uv run mypy`: **Success: no issues found in 24 source files**
- `uv run pytest -q`: **375 passed, 12 deselected** in 9.32s (the deselected are the `model`-marked tests, including the known `test_sample_derivation_reproducible`)

C4(b), acknowledging D6, is the owner's.

## Reply 4 — condition C2 (S6) done

> Writer: the support session, on the owner's word ("remove it", 2026-10-16). Data only.

The gitignored `.claude/settings.local.json` that held `Bash(uv run -q --project * python * seen_payload.py *)` is deleted. It held only that rule and was never committed. No other settings file was touched. No further `/aveto-judge-seen` run is planned (C3).
