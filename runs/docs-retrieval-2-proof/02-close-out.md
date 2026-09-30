# Close-out: docs-retrieval-2 (slice A) and docs-retrieval-2-proof (slice B)

> Post-Launch Learning, depth smoke. Nothing shipped, so there is no production signal; the evidence is the eval outputs and the run artefacts. The gate FAILED. Owner resolved the escalation as option A (verbatim "A.", 2026-09-30T01:32:07Z, `ESCALATION-1.md`). Security Review and the Release Gate did not run. No retry spent (0 of 2).

## 1. Did it meet its success criteria? No.

| "Done means" (`docs-retrieval-2/intent.md`) | Result | Evidence |
|---|---|---|
| Starts from slice 1's code, main merged | Met | `docs-retrieval-2/01-scope.md` (`fba5233`, merge `b20b583`, lint fix `e308551`) |
| Corpus fixed before any run, in config | Met | 123 files, Decision 2 allow-list; `03-implementation.md` (ingest twice, same sha256 `f36ef5d4...`); `01-qa-result.md` (index hash matches) |
| File-level ranking | Met | `file-rrf-v1`, `docs/adr/0004-*.md`, `03-implementation.md` |
| Freeze first; third set committed after | Met | method `b3f3fc41`; set committed at `74c5a2d`; `01-qa-result.md` diff of method files vs HEAD empty |
| Earlier sets reported as diagnostics | Met | `01-qa-result.md`, `eval-run-2-*`, `eval-run-3-*` |
| Slice 1 guarantees still hold | Met, as far as the artefacts show | full regression green after the last commit (pytest 122 passed, `-m model` 3 passed, mypy and ruff clean: `01-qa-result.md`); ingest deterministic; no method file changed. Slice B added no network, model or dependency. |
| **Correct file in top 5 for >= 80% of answerable, third set** | **Not met** | **11 of 16 (68.8%), bar 13** |

## 2. Results

| Set | Answerable | Role |
|---|---|---|
| Third held-out (`evals/retrieval-heldout-3.toml`) | **11/16** | the gate, FAIL (exit 1) |
| Second held-out (seen) | 12/17 (70.6%) | diagnostic |
| Dev (seen) | 19/24 (79.2%) | diagnostic |
| Third set, unanswerable (4) | top scores 0.70, 0.59, 0.81, 0.67 | diagnostic only; retrieve never abstains |

Against slice 1 on the same sets (ungated recall, `ESCALATION-1.md`): second held-out 8/17 to 12/17; dev 17/24 to 19/24. This is an indication, not proof: both sets are seen. The fair test is the third set, 11/16.

## 3. What we learned (hypotheses, not findings)

- The five misses (t04, t06, t12, t13, t15) all expected a narrow, specialised file (vendor risk template, UX researcher role, AI governance role or AI risk template, change request template, `execution/SECURITY.md`). The top 5 held broader or neighbouring role and template files. Five items is a pattern to test, not a result. A reranker is what would target it.
- Small sample: 16 questions; one question is 6.25 points; the shortfall is two questions.
- Provenance: the set was drafted by Claude in the playbook session, which had read both earlier runs and slice 2's spec (it reports never running retrieval on the questions), then reviewed and committed by the owner.

## 4. Carry-forward (options and open items, not decisions)

- (a) **Reranker.** The intent's Decision 3 names it as the next question. It would be its own slice: a new model, dependency and download (approval rule 5, possibly 4) and a **fourth fresh held-out set**. None of it is approved or started.
- (b) **ABSTENTION HAS NO OWNER SLICE.** Decision 1 moved "the docs don't answer this" to the check step; it did not drop it. **The check-step slice must carry it forward.** It is a safety requirement (INV-4 territory) that currently rests on no planned slice. On the third set's unanswerable diagnostic, retrieval returns five files with scores in the same band as answerable ones.
- (c) `docs-retrieval-ci` stays blocked on a passing gate.
- (d) Stale wording: `.agentic/PROJECT_CONTEXT.md` lines 47 and 55 and `README.md` still say retrieval is "plain code". The `README.md` and `docs/ARCHITECTURE.md` prose refresh (deferred to slice B by Scope Review) was not done because the gate failed. Also open, per `APPROVAL_RECORD-3.md`: the owner's wish to record "abstention moved to the check step" was not written into the INV-4 annotation; that would be a new rule 4 edit with exact wording.

## 5. Process

Worked:
- Freeze-first ordering held again; the method commit precedes the set commit and QA verified no method file changed.
- One thin fresh spawn per stage. Slice A's Architect ran as one fresh spawn (peak 122,905, plus 5,233 for one resume; `docs-retrieval-2/STATE.md`). Slice 1's Architect was resumed many times, which the same STATE file names as what inflated slice 1's processed total; section 6 gives the measured figures.
- The Engineering Manager's split at the freeze kept each half small (slice A 460k, slice B 430k, `01-scope.md`).
- The approval flow held: Approvals 1 to 3 recorded with verbatim answers. One restated approval is noted in `APPROVAL_RECORD-3.md`; the edit was already applied and matched scope.

Did not work:
- The merge into slice 1's branch exposed a mypy and ruff failure that predated it (static checks were not re-run after slice 1's tokenizer-fixture commit); fixed in `e308551` (`01-scope.md`). The plan then required the full regression after each last commit, and it stayed green.
- A pasted instruction assumed a different worktree than the one in use (this worktree is slice 1's branch); handled by mapping "take this branch's version" to pack v10. (Reported by the driving session; not recorded in a slice artefact.)
- Trace Model column: comes from the harness log (`usage.mjs`). One row was briefly "(declared)" when the log could not be read (reported by the driving session; both current STATE tables show model names).
- The write-scope hook falsely denied this role's writes in the worktree. The Orchestrator reproduced the root cause with CLAUDE_PROJECT_DIR set to the main checkout; the budget guard shared the root cause and would have been blind. It was reported upstream, the owner chose to wait, and pack v11 fixed both hooks (main commit 0188c76). Source: `runs/docs-retrieval-2-proof/STATE.md`, Interruptions.

## 6. Cost

Budget units are peak context per spawn, not consumed tokens. Slice A: 311,729 spent of 460k (`docs-retrieval-2/STATE.md`, trace.json). Slice B: 66,635 spent of 430k, which includes the paused close-out attempt of 39,756 (per the coordinator; QA alone was 26,879 in `STATE.md` and trace.json).

Processed tokens, measured with `node <playbook>/execution/usage.mjs . --slice <id>` on 2026-09-30 (harness-logged, figures supplied by the coordinator, not from a slice artefact):

| Slice | Processed | Peak context | By role |
|---|---|---|---|
| `docs-retrieval-2` (A) | 6.24M | 310k | software-architect 3.21M (opus-5-5), backend-architect 2.71M, engineering-manager 256k, product-manager 67k |
| `docs-retrieval-2-proof` (B) | 421k | 66k | qa-evidence 202k, post-launch-learning 219k |
| Slice 1 (first attempt, for comparison) | 19.5M | not stated here | its Architect alone 15.6M |

Consumption is far larger than the budget's units. Caveat: the budget is in peak-context units, and the usage tool may not count every resumed pass.

## 7. Follow-up slices to file (one line each, no commitment)

1. Reranker retrieval: re-order the top candidates with a cross-encoder, on a fresh fourth held-out set.
2. Check step: a model reads the passages and decides "the docs don't answer this"; carries abstention forward.
3. `docs-retrieval-ci`: CI workflow, blocked until a gate passes.
4. Docs wording: fix the "plain code" lines (`PROJECT_CONTEXT.md` 47 and 55, `README.md`) and refresh `README.md` and `docs/ARCHITECTURE.md` prose to match the method.
