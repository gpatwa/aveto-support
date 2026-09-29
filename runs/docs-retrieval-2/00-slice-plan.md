# Slice Plan — docs-retrieval-2

- **Intent:** `runs/docs-retrieval-2/intent.md`, a byte-identical copy of `intents/docs-retrieval-2.md` on `main` at `4b4ca1c`
- **Project pack:** `project-packs/ai-agent-product.md`
- **Release tier (proposed):** 2. There is no deploy, no post, and no new model, dependency or download. A change to a gate (Decision 1) is handled by approval rule 4, not by the tier. The Release Manager confirms.
- **Playbook:** `/Users/gopalpatwa/opt/agentic-sdlc-playbook` at `6be205c`, resolved from the main checkout (the relative path does not resolve from a worktree). Every stage is given the absolute path.
- **Starting point (Done-means 1) is already met:** slice 1's code is on this branch (`fba5233`), `main` is merged in (`b20b583`), and `main`'s pack v10 files were taken on the only `.claude/` conflict (`.claude/hooks/budget-guard.mjs`); `.gitignore` kept slice 1's entries. One extra commit, `e308551`, fixed two lint findings in QA's one-off tokenizer-fixture generator (introduced in slice 1 and missed because the static checks were not re-run after that commit). Suite at start: 118 tests pass, 3 model tests pass, mypy and `ruff check` clean.

## Needs your decision (before anything past Scope Review runs)

1. **Confirm the intent and this plan.** The intent's header says the three open questions were decided by Claude (in the playbook session) under your "make a decission for 1 - 3 and execute it", and that you can overturn any of them before the slice starts. Do you accept Decisions 1 to 3 as written?
2. **Approval Request 1 (rule 4):** drop the unanswerable half of the gate for this slice. `APPROVAL_REQUEST-1.md`.
3. **Approval Request 2 (rule 4), only if my reading in "Interpretations" is right:** retrieval stops abstaining and always returns its top 5 files. `APPROVAL_REQUEST-2.md`.
4. **Stakes:** the intent ticks "None of the above". Decision 1 removes half of a gate and Request 2 turns off a behaviour the safety invariants mention. Does that tick "Changes auth, permissions, or a safety control"? Ticking it takes the slice off the short path. In slice 1 you answered "don't tick" for a different change (INV-5). This one is yours to decide; I have not decided it.

## Interpretations (inferred — not in the intent; a line still marked inferred after your confirmation is dropped)

- **(inferred) Retrieval no longer abstains.** Decision 1 says the check step decides "the docs don't answer this", and the gate is "a correct file in the top 5". A withheld result can never satisfy that, so I read it as: `retrieve` always returns its top 5 files with the top score printed, and the confidence cutoff no longer decides anything. That is Request 2. If you meant retrieval keeps abstaining, say so and Request 2 falls away, but then a withheld result would count as a miss or the gate would have to be scored ungated, which is a different gate.
- **(inferred) The third held-out set is isolated the same way slice 1's was:** no role that designs or builds retrieval reads it before the run, it is committed only after the method's frozen commit, and nothing changes between its commit and the single scoring run. This intent says "written by the owner or drafted outside the slice"; it does not repeat slice 1's isolation sentence.
- **(inferred) The frozen off-topic list and the calibration in `docs-source.toml`** become unused by retrieval under Request 2. The Architect decides whether to keep them as a diagnostic or remove them; `evals/calibration-offtopic.toml` stays frozen either way.

## Outcome (one line)

Given a question about Aveto, return the top 5 **files** from Aveto's user documentation (a scoped, fixed corpus), each with the passages that matched, their headings and line ranges, and the top score, and prove a correct file is in the top 5 for at least 80% of a fresh owner-committed held-out set. No generative model, no new model.

## Stages

Short path: the intent has checkable "Done means" and no open questions, and it ticks no Stakes (subject to item 4 above). Market Research, Discovery (PM), UX Research and UI Design are skipped (AGENTIC_SDLC "When to compress stages"). The Architect reads the intent directly. **Gates never compress.**

| # | Stage | Role | Archetype | Est. | Depth |
|---|-------|------|-----------|------|-------|
| 3 | Scope Review | engineering-manager | review | 100k | standard |
| 7 | Architecture | software-architect | review | 100k | standard |
| 8 | Implementation | backend-architect | build | 130k | standard |
| — | Freeze, then the owner commits the held-out set | Orchestrator / owner | — | — | — |
| 9 | QA Evidence (scores once; regression; diagnostics) | qa-evidence | build | 130k | standard |
| 10 | Security Review | security-privacy | review | 100k | standard |
| 11 | Release Gate | release-manager | review | 100k | standard |
| 12 | Post-Launch | post-launch-learning | review | 100k | smoke |

- **Doc fix:** the stale "retrieval only, no model" line in `.agentic/PROJECT_CONTEXT.md` (Done-means constraints) goes to the `product-manager` role as a one-line task, because the write-scope hook gives that role that file. It is counted in the headroom.
- **Security and the Release Gate run only if the gate passes.** If it fails, the failure loop applies (slice 1's pattern); they do not run.
- **No Analytics Engineer / Data Analyst.** The slice adds no new measurement beyond the eval score.

## Budget

Σ estimates = 760k, plus 130k headroom (one build stage) = **890k**. This is **over the ~600k "slice too big" signal** in RUN_ECONOMICS §2. Scope Review decides first whether to split. Note the intent already separates the CI workflow (`docs-retrieval-ci`), so this slice is the method change plus its proof.

Budget is in peak-context units. Slice 1 processed 19.5M tokens (most of it the Architect's repeated resumes) against 854k of budget. To keep consumption in check this time: one thin, fresh spawn per stage, no repeated resumes of the Architect, and the tech spec kept short.

## Success criteria (from intent "Done means")

1. Starts from slice 1's code with `main` merged and `main`'s pack files taken on conflict. **Met at intake** (see above).
2. **Corpus scope is fixed before any run, on principle:** the index covers exactly the user-documentation list in Decision 2, recorded in config, and is never tuned after a run. (At the pinned commit: 126 markdown files, 123 in scope, 3 excluded: `docs/ARCHITECTURE.md`, `docs/BACKLOG.md`, `docs/PLATFORM_EVAL.md`. I checked that every labelled source in both earlier eval sets is inside the new corpus, so the intent's claim holds; no scoring was run.)
3. **Ranking is file-level:** results are files, each carrying the passages that matched with heading and line range.
4. **Freeze first, again:** the method is frozen and its commit recorded; then the owner commits a **third, fresh held-out set** (at least 15 answerable; unanswerable optional and diagnostic only), written by the owner or drafted outside the slice and reviewed and committed by the owner. Run once.
5. On that held-out set, a correct file appears in the top 5 for **at least 80%** of answerable questions (with 15 answerable, at least 12). That is the whole gate.
6. The two earlier sets (`evals/retrieval.toml`, `evals/retrieval-heldout.toml`) are reported alongside as diagnostics; neither gates.
7. Everything slice 1's "Done means" guaranteed still holds: deterministic ingest, provenance on every passage, no generative model, no network outside ingest and CI setup, every model file hash-checked.

## Non-goals (from intent "Out of scope")

Any generative model call (drafting, checking, query rewriting, LLM reranking), hosted embeddings or reranking APIs, the CI workflow (`docs-retrieval-ci`, a separate slice started only after this gate passes), a web UI, a database.

## Constraints (from intent + `.agentic/`)

- Python 3.12, uv, the existing structure. The approved model (`BAAI/bge-small-en-v1.5` @ `5c38ec7c…`, ONNX Runtime + numpy) stays the only model: no larger model, no reranker (Decision 3).
- Nothing is chosen by its score on any eval set: corpus list, ranking method and model are argued on general grounds before the run.
- No Azure, no API key, no deploy. Credentials are never handled by an agent.
- `.agentic/SAFETY_INVARIANTS.md` INV-1 to INV-5 apply as written unless an approved request changes them. Nothing retrieved is presented as an answer, provenance is always shown, and the question and the docs never leave the machine.
- **Process constraint from the Orchestrator (not from the intent), learned from slice 1:** every stage that changes code re-runs the full documented regression (`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, plus `-m model`) after its last commit and reports the result, so a check that goes red after a late commit is caught at once.

## Gated actions (HUMAN_APPROVAL_RULES scan)

| Action | Rule | Status |
|--------|------|--------|
| Drop the unanswerable half of the gate for this slice (Decision 1) | 4 | **PENDING** — `APPROVAL_REQUEST-1.md`; must be answered before Implementation |
| Retrieval stops abstaining and always returns its top 5 files (inferred reading of Decision 1) | 4 | **PENDING** — `APPROVAL_REQUEST-2.md`; only if the reading is right; before Implementation |
| Pushing the branch or opening a PR | outward-facing | Not done by any agent in this slice. The owner does it, after the Release Gate |

Not fired: 1 (nothing sent or posted), 2 (nothing destroyed), 3 (no deploy), 5 (no new model, no new download, no new network call: the approved pinned fetch and model files are unchanged), 6 (no new data processor).

## Risk to state plainly (from slice 1's own artefacts, not a new run)

Slice 1's held-out result put a correct file in the top 5 for only 8 of 17 questions ignoring abstention (47%). Corpus scope removes 3 of 126 files, and only 2 of the 17 held-out answers were confidently wrong (both included broad docs). So corpus scope alone is unlikely to close a gap from about 47% to 80%; the outcome depends mostly on file-level ranking. The intent argues both changes on general grounds and forbids choosing by score, and the plan follows it. If the gate is missed, the failure loop applies and the next question is the reranker (Decision 3 says so). This is a risk note, not a prediction.
