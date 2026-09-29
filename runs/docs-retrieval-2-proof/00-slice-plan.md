# Slice Plan — docs-retrieval-2-proof (slice B)

- **Continues:** `runs/docs-retrieval-2/` (slice A, closed at the freeze). **Intent:** `runs/docs-retrieval-2-proof/intent.md`, byte-identical to slice A's and to `intents/docs-retrieval-2.md` on `main` at `4b4ca1c`.
- **Scope owned here (01-scope.md of slice A):** Done-means 4 (second half: the third held-out set is committed after the freeze; run once), 5 (the gate), 6 (earlier sets as diagnostics), and 7's verification half.
- **Playbook:** `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (resolved from the main checkout). **Release tier (proposed):** 2; the Release Manager confirms.
- **Frozen method:** commit `b3f3fc41f2382283678e638b55ff44b32876034c` (`file-rrf-v1` + the 123-file corpus). Verified unchanged through `HEAD` (b2794a9) at 2026-09-29T20:58:53Z: `git diff b3f3fc41f2382283678e638b55ff44b32876034c HEAD` over `aveto_support tests docs-source.toml pyproject.toml uv.lock` and the three earlier eval files is empty.

## The gate (intent Decision 1, owner-approved rule 4, Approvals 1 to 3 of slice A)

A correct file in the top 5 for **at least 13 of the 16 answerable** questions in `evals/retrieval-heldout-3.toml` (80%: 13*5=65 >= 16*4=64; 12 misses the bar). Unanswerable (4) is a printed diagnostic only. The two earlier sets (`evals/retrieval.toml`, `evals/retrieval-heldout.toml`) are reported alongside as diagnostics; **neither gates**. Run **once**.

## The held-out set (provenance, carried into the record)

`evals/retrieval-heldout-3.toml`, owner commit `74c5a2d` (2026-09-29 11:02 -0700, after the freeze commit `b3f3fc4` at 10:18). Its header states: drafted by Claude in the playbook session, kept outside the repo until the freeze, reviewed and committed by the owner; the drafter drafted both earlier sets and had read both runs' results **and slice 2's tech spec (so it knew the method)**, but did not run retrieval on these questions; no role that designed or built retrieval has seen them. **Orchestrator's checks:** 16 answerable + 4 unanswerable; every labelled source is inside the 123-file corpus; no source is shared with either earlier set; the highest question-text overlap with any earlier question or the calibration list is 0.25 (Jaccard); the file equals the committed `74c5a2d`.

## Approvals

Approvals 1 and 2 (rule 4) and 3 (INV-4 note edit) were given for slice A and name `docs-retrieval-2`; this slice is the same gate's second half (Scope Review's reading, 01-scope.md §6.6). The owner directed this slice's creation, so the Orchestrator treats them as covering the pair and says so here; the scope authorised is unchanged. See `runs/docs-retrieval-2/APPROVAL_RECORD-1.md`, `-2.md`, `-3.md`. Nothing wider is authorised. Any further attempt or reopening of the gate is a new rule 4 question.

## Stages

| Stage | Role | Est. | Notes |
|-------|------|------|-------|
| 9 QA Evidence | qa-evidence | 130k | Scores the third set once; the two earlier sets once each as diagnostics; regression after; writes the result |
| 10 Security Review | security-privacy | 100k | **Only if the gate passes** |
| 11 Release Gate | release-manager | 100k | **Only if the gate passes** |
| 12 Post-Launch | post-launch-learning | 100k | smoke; close-out either way |

Budget **430k**, no separate headroom (Scope Review). If QA overruns, that is a stop-and-ask. **README and ARCHITECTURE prose refresh** (deferred here by Scope Review) is not budgeted in the 430k; decide after the result (skip on a fail).

## If the gate fails

Failure loop (retry cap 2); nothing ships; a further method change needs a fresh fourth held-out set from the owner and a new rule 4 look, since this set will have been seen. The next question, per Decision 3, is a reranker.

## Constraints

Every constraint from slice A stands: no eval run other than the single scoring runs named above, no change to any method file, the three eval files (and the third set) read-only to every role, no generative model, no new dependency or network access, nothing presented as an answer. QA re-runs the full documented regression (`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, plus `-m model`) at the end, static checks last.
