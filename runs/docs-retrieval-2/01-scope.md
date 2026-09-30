# Agent Handoff — engineering-manager → software-architect

> Slice: docs-retrieval-2 (retrieval, second attempt)
> From: engineering-manager (Stage 3, Scope Review, depth standard)
> To: software-architect (Stage 7, Architecture, depth standard)
> Date: 2026-09-29
> Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (the relative path does not resolve from this worktree)

## 1. Scope decision: SPLIT into two slices at the freeze

**Why the plan is over.** 7 stages, 760k (890k with headroom) trips RUN_ECONOMICS §2 ("more than 6 stages or ~600k is a signal the slice is too big"). My scope rules also say to reject a non-refactor change that touches more than 10 files. Counting from the intent and the file names (section 4), the full slice touches about 14 to 17 files, so it fails that rule as one slice. The owner confirming the plan does not change either rule; the owner asked for this review.

**Why split at the freeze, and only there.** The freeze is a seam that already exists in the intent ("Freeze first, again") and is also the isolation boundary for the held-out set. Everything before it is design and build with no held-out set in sight. Everything after it is one scoring run plus review. Splitting here brings each half under 6 stages and 600k, gives the owner one clean, recorded freeze point, and puts the "nobody who builds retrieval reads the set" rule on a slice boundary instead of a promise.

**Why not split further (recorded exception to the 10-file rule).** Corpus scope (`ingest.py`, config) and file-level ranking (`search.py`, output) could be separate slices, but neither has an observable gate alone: the intent gates only the combined method on the held-out set, and it forbids choosing either part by score. A third slice would cost another Architect + Implementation + review chain (about 300k) to save about 3 files. Instead, slice A gets a hard cap (section 4): 5 product files, 4 test files, 2 to 3 context or doc files; README and `ARCHITECTURE.md` prose are moved to slice B, after the outcome is known. If the Architect needs more than the cap, stop and hand back to me for a re-split; do not just widen.

| Slice | Stages | Ends at | Est. |
|-------|--------|---------|------|
| **A: `docs-retrieval-2`** (method to freeze) | 3 Scope Review (this) -> 7 Architecture -> 8 Implementation -> (freeze) | Frozen commit recorded by the Orchestrator; full regression green | 100 + 100 + 130 = 330k, plus 130k headroom (Implementation) = **460k** |
| **B: `docs-retrieval-2-proof`** (proof and release) | owner commits held-out set -> 9 QA Evidence -> 10 Security Review -> 11 Release Gate -> 12 Post-Launch (smoke) | Gate result; release go/no-go; close-out | 130 + 100 + 100 + 100 = 430k, **no separate headroom** |

Both slices sit inside the existing 890k (460k + 430k = 890k). Nothing here raises a budget line. Slice B has no headroom of its own: if QA overruns, that is a stop-and-ask with the numbers (rule 6), not a quiet raise. Security and the Release Gate run only if the gate passes (as in the plan); if it fails, slice B saves about 200k and goes to the failure loop and close-out. The Orchestrator sets each slice's `STATE.md` Budget block; I have not edited it.

Slice B is created by the Orchestrator after the freeze is recorded. Its `intent.md` is a byte-identical copy of this slice's intent; it owns Done-means 4 (second half), 5, 6 and 7 (the verification half).

### Every "Done means" item has exactly one owner

| # | Done means (short) | Owner | Note |
|---|--------------------|-------|------|
| 1 | Starts from slice 1's code, `main` merged | A | **Met at intake** (`fba5233`, merge `b20b583`, lint fix `e308551`) |
| 2 | Corpus scope fixed in config, exactly Decision 2's list, never tuned | A | Built and frozen in A |
| 3 | Ranking is file-level, passages with heading and line range | A | Built and frozen in A |
| 4 | Freeze first: method frozen and commit recorded; then owner commits third set (>= 15 answerable), run once | **Split, no overlap:** the freeze and its recorded commit are A's exit; the owner's commit of the set and the single run are B's entry and QA stage | Two halves of one sentence, each held by one slice. A's exit is not complete without the recorded commit; B does not start without it |
| 5 | Held-out top-5 recall >= 80% of answerable (12 of 15 if 15) | B | The whole gate |
| 6 | The two earlier sets reported as diagnostics, neither gates | B | Produced only by B's QA, in the same post-freeze run (section 6, constraint 4) |
| 7 | Slice 1's guarantees still hold (deterministic ingest, provenance, no generative model, no network outside ingest and CI setup, hashes checked) | A builds and keeps regression green; B's QA and Security verify | Verification evidence in B; a regression failure in A blocks the freeze |
| C1 | Fix the stale "retrieval only, no model" line in `.agentic/PROJECT_CONTEXT.md` (constraint) | A | One-line task to `product-manager` (the write-scope hook gives that role the file); line 66 today |
| C2 | Decision 1's carry-forward: the check-step slice must carry abstention forward | A records it in ADR 0004 and the tech spec; B's close-out lists it as a follow-up | Moved, not dropped |

No item is dropped; each is owned by A or B, and item 4 is deliberately split into two named halves.

## 2. Lifecycle stages and compression

Short path taken. Rationale: the intent has checkable "Done means", no open questions, and its Stakes line is "None of the above" (owner confirmed 2026-09-29T16:54:46Z: don't tick, stay on the short path). Market Research, Discovery, UX Research and UI Design are skipped (AGENTIC_SDLC "When to compress stages"). The Architect writes the tech spec directly from the intent. **Gates never compress.**

Stage sequence and depth are as in the table above, all `standard` except Post-Launch (`smoke`). No Analytics Engineer or Data Analyst stage.

## 3. Release tier and gates

**Tier 2** (Behavioural change with no external effect: RELEASE_GATES.md). Confirmed as the working tier; the Release Manager makes the go/no-go. Reasons: nothing is sent, posted, pushed or deployed; no new model, dependency or download; no auth or permission change; Stakes ticks are "none". Not Tier 3.

Tier 2 requires: all implementation, QA and security gates; a release checklist; a rollback plan. How they apply across the split:

- **Slice A:** the implementation gates (tests, `mypy`, `ruff check`, the full documented regression with `-m model`, reported after the last commit). A is **not releasable** by itself: no push, no PR, nothing shipped from A.
- **Slice B:** the QA, security and release gates, over the frozen code. The release checklist and rollback plan (revert to `fba5233` plus the merge; nothing is deployed, so rollback is a `git revert`) are B's Release Gate items.
- Fail closed: a failed gate in B sends the work back through the failure loop (cap 2 retries), never forward. A fresh third held-out set is needed for any further method change.

## 4. Files slice A is expected to touch

Inferred from the intent and the file names in `aveto_support/` and `tests/` (sizes by line count: `search.py` 489, `ingest.py` 440, `index.py` 401, `embed.py` 284, `evaluate.py` 201, `__main__.py` 161; `test_ingest.py` 512, `test_search.py` 481, `test_evaluate.py` 261, `test_index.py` 222, `conftest.py` 154, `docs-source.toml` 19). I have not read the code, so the Architect confirms or corrects this list.

| Group | Files | Count |
|-------|-------|-------|
| Product and config | `aveto_support/ingest.py` (corpus allow-list), `docs-source.toml` (list in config), `aveto_support/search.py` (file-level ranking, no abstention), `aveto_support/__main__.py` (output shape, exit codes), `aveto_support/evaluate.py` (gate on answerable only; diagnostics) | 5 |
| Tests | `tests/test_ingest.py`, `tests/test_search.py`, `tests/test_evaluate.py`, and `tests/conftest.py` only if shared fixtures change | 3 to 4 |
| Context and docs | `.agentic/PROJECT_CONTEXT.md` (C1), `.agentic/LOCAL_COMMANDS.md` (exit codes and retrieve output change), `docs/adr/0004-*.md` (new ADR, Architect) | 3 |
| Conditional only | `aveto_support/index.py` and `tests/test_index.py` (only if file-level scoring needs new index data); `.agentic/SAFETY_INVARIANTS.md` (see section 6, contradiction 1; owner first) | 0 to 3 |

Baseline **11 to 12**, up to 15 with the conditionals. That is over my 10-file rule, so the cap and the exception in section 1 apply: the Architect designs to the baseline and must justify each conditional file in the tech spec. `embed.py` must not change (the model is unchanged). README, `docs/ARCHITECTURE.md` and the prose refresh are deferred to slice B. `runs/` artefacts do not count.

The Architect's context to read is 7 files or fewer (section 5), inside the ~10-file guardrail.

## 5. Minimal context bundle for the Architect (paths only)

- `runs/docs-retrieval-2/intent.md` (source of truth; Decisions 1 to 3 are fixed)
- `runs/docs-retrieval-2/01-scope.md` (this file)
- `runs/docs-retrieval-2/APPROVAL_RECORD-1.md`, `APPROVAL_RECORD-2.md`
- `.agentic/SAFETY_INVARIANTS.md` (INV-4 and INV-5 with their enforcing tests), `.agentic/LOCAL_COMMANDS.md`
- `docs-source.toml`; `aveto_support/search.py`, `aveto_support/ingest.py`, `aveto_support/evaluate.py`, `aveto_support/__main__.py` (targeted reads with `grep -n`, not a tour)
- `runs/docs-retrieval/08-close-out.md` sections 1, 2 and 5 only (context on the failed first attempt)
- Tests: names only via `grep -n "def test_" tests/`. Read a test body only when deciding whether to change or retire it.
- **Do not read:** `evals/retrieval-heldout-*.toml` or any third set (it does not exist yet and must not be seen); do not read any other file in `evals/` for the purpose of choosing a method. Do not read `runs/docs-retrieval/` beyond section 5's close-out lines above.
- Commands: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, then `uv run pytest -m model` (`.agentic/LOCAL_COMMANDS.md`). Targeted tests first, full suite before each commit.

## 6. Approval points and constraints

**Approvals already given (both rule 4, both APPROVED 2026-09-29T16:54:46Z by Gopal Patwa):**

- **Approval 1** (`APPROVAL_RECORD-1.md`) authorises only: dropping the unanswerable half of the eval gate for this work. The gate is a correct file in the top 5 for at least 80% of answerable held-out questions. Unanswerable questions become a printed diagnostic. Abstention moves to the future check step. Nothing else in INV-1 to INV-5 changes.
- **Approval 2** (`APPROVAL_RECORD-2.md`) authorises only: `retrieve` always returns its top 5 files with the top score, and never prints "no confident match". INV-4's first clause still holds. It is not approval for anything generative, a new model, or wider network access.

**Nothing wider is authorised.** Both approvals are scoped to this work (the two slices together, one gate). If slice B fails and a further attempt is needed, or the gate is reopened, that is a new rule 4 question for the owner.

**New model, download or network access: none planned, none found.** The only model is the approved `BAAI/bge-small-en-v1.5` @ `5c38ec7c…`. Re-running `ingest` for the new corpus uses the already-approved pinned GitHub fetch and cached, hash-checked model files (INV-5), with no new host. If the Architect proposes anything else (larger model, reranker, new dependency, new host), stop and raise it as its own approval (rule 5); do not proceed.

**Still human-approval points:** pushing the branch or opening a PR (owner only, after B's Release Gate); the owner's own commit of the third held-out set; and any change to INV text beyond what Approvals 1 and 2 cover (contradiction 1 below).

### Constraints (inherited, and two added by me)

1. Nothing is chosen by score on any eval set (corpus list, ranking method, model). Argued on general grounds in the tech spec.
2. The three eval files `evals/retrieval.toml`, `evals/retrieval-heldout.toml`, `evals/calibration-offtopic.toml` are **read-only to every role**.
3. The third held-out set is isolated: no role that designs or builds retrieval reads it before the single scoring run. It is committed only after the freeze is recorded, and nothing in the method files changes between its commit and the run (B's QA verifies with `git diff <frozen> HEAD` over the method files, as slice 1 did).
4. **Added by me: no eval run during design or build.** The Architect and the Implementer must not run `eval` against either earlier set (they are seen sets, and running them invites tuning by score, which the intent forbids). Hand-check `retrieve` on their own non-eval questions. The two earlier sets are scored only once, by B's QA, after the freeze, alongside the third set, as diagnostics. This does not weaken any approval; it applies the intent's own "nothing is chosen by its score".
5. Every code-changing stage re-runs the full documented regression after its last commit and reports the result (the Orchestrator's process constraint from slice 1).
6. Decisions 1 to 3, the fixed corpus list (Decision 2), file-level ranking, and the frozen off-topic list stay as written.

### Consistency check: contradictions and gaps found (flagged, not resolved silently)

1. **INV-4's enforcing tests vs Approval 2.** INV-4 lists `test_not_confident_returns_no_hits` (and related) as enforcing "or 'no confident match' with no passages". Approval 2 says retrieval never prints that. INV-4 is a disjunction, so always returning verbatim top-5 satisfies it as written; the text need not change. But the test that asserts abstention must be changed or retired, and editing a test that enforces a safety invariant is not something Approval 2 states in so many words. **Ruling for the Architect:** keep `test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file` and `test_hybrid_hits_are_verbatim_passages` (or their file-level equivalents) at full strength; list every retired or rewritten INV-enforcing test by name in the tech spec, with the reason, so Security (slice B) can check it. Do not edit `.agentic/SAFETY_INVARIANTS.md` without a request to the owner; if the Architect thinks the INV-4 text must change, that is a **rule 4 question for the owner**, not a design detail.
2. **The eval gate still hard-codes the unanswerable half.** `evaluate.py` and `LOCAL_COMMANDS.md` describe exit 1 for "either threshold" and retrieve's "no confident match" as exit 0. Approval 1 covers dropping this; the change is in scope for slice A, but the eval's diagnostic output must still print the unanswerable result (Decision 1 says reported, not gated) and the top score.
3. **The frozen off-topic list and the calibration in `docs-source.toml`** become unused by retrieval. Consistent with the frozen `evals/calibration-offtopic.toml` (read-only either way). The Architect chooses between keeping the values as a printed diagnostic and removing them, and records why. Removing config keys while the frozen list stays is not a contradiction.
4. **Isolation vs a runnable eval.** The third set does not exist yet, so slice A can only test `evaluate.py` on synthetic fixtures in `tests/`. That is enough; the held-out file's schema is taken from the `evals/` format that `evaluate.py` already loads. If the Architect changes the eval file schema, the owner must be told **before** writing the set (a schema change would otherwise leak into the set).
5. **Corpus list is an allow-list.** The plan's "123 of 126 in scope, 3 excluded" was checked by the Orchestrator at intake. The config must hold the Decision 2 allow-list (not a deny-list), so a future file that is in neither list is out by default, not in.
6. **Approvals are for the pair.** Approvals 1 and 2 name "docs-retrieval-2"; slice B is a continuation of the same gate. The Orchestrator should say so in slice B's `STATE.md` and reference both records, rather than re-asking, because the scope authorised is unchanged (this is my reading; if the Orchestrator disagrees it is a one-line ask to the owner).

## 7. Acceptance criteria (from the intent's "Done means")

**Slice A exit (this handoff's stages):**

- [ ] Done-means 1: met at intake (no work).
- [ ] Done-means 2: config holds exactly the Decision 2 list; a test asserts the ingested file set equals it; the list is committed before any run.
- [ ] Done-means 3: `retrieve` returns files (max 5), each with its matched passages, heading and line range, and the top score; `retrieve` never prints "no confident match".
- [ ] Constraint C1: `.agentic/PROJECT_CONTEXT.md` no longer says "retrieval only, no model".
- [ ] Done-means 7 (build side): deterministic ingest twice gives byte-identical output; provenance on every passage; no generative model; `retrieve` and `eval` make no network calls; every model file hash-checked; INV-4 and INV-5 enforcing tests pass (retired ones named per contradiction 1).
- [ ] Full regression green after the last commit: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, plus `uv run pytest -m model`.
- [ ] Done-means 4, first half: the Orchestrator records the frozen commit SHA in `STATE.md` and the slice B intake; only then may the owner commit the third set.

**Slice B (for its own Scope, not this handoff):** Done-means 4 (second half), 5, 6, 7 (verification).

## 8. Realistic estimates to the Release Gate

| Stage | Slice | Est. |
|-------|-------|------|
| 3 Scope Review | A | 100k |
| 7 Architecture (thin spec, one fresh spawn, no repeated resumes) | A | 100k |
| 8 Implementation | A | 130k |
| 9 QA Evidence | B | 130k |
| 10 Security Review | B | 100k |
| 11 Release Gate | B | 100k |
| **To and including the Release Gate** | | **660k** |
| 12 Post-Launch (smoke) | B | 100k |
| **Total** | | **760k of 890k** (130k headroom, held in A) |

I keep the plan's per-stage numbers and add none; the doc-fix one-liner is inside A's headroom as the plan says. Risk: slice 1's Architect was resumed repeatedly and consumed 19.5M processed tokens; one thin spawn per stage is the control. If Implementation needs a retry, A's 130k headroom is spent and B's 430k has no spare; the next overrun is a stop-and-ask, not a raise.

## What "done" looks like for the next stage (Architecture)

- A short tech spec (`runs/docs-retrieval-2/02-tech-spec.md`) and ADR 0004 covering: the corpus allow-list and how it is expressed in `docs-source.toml`; the file-level ranking method, argued on general grounds only; the always-return-top-5 output shape; which tests are retired or rewritten (by name); what happens to the unused calibration; the exact file list against the section 4 cap.
- A statement of what the freeze will cover (which files are "the method").
- No eval runs on any set; no reading of any third set.

## Constraints inherited from prior stages

- Section 6, constraints 1 to 6 and contradictions 1 to 6.
- Intent Decisions 1 to 3 are fixed. Playbook path: `/Users/gopalpatwa/opt/agentic-sdlc-playbook`.

## Open questions for the next agent

- [ ] Does file-level scoring need new index data (so `index.py` and `test_index.py` enter scope)? Justify in the spec; if so it uses part of the "0 to 3 conditional" file allowance. Resolver: Architect.
- [ ] Keep the unused calibration as a diagnostic, or remove it? Resolver: Architect.
- [ ] Does INV-4's text need to change? Default: no. If yes, stop and ask the owner (rule 4), through the Orchestrator. Resolver: owner.
- [ ] Does the eval file schema need to change? Default: no. If yes, the owner is told before writing the set. Resolver: Architect, then owner.

## Out of scope reminder

- Any generative model call (drafting, checking, query rewriting, LLM reranking); hosted embeddings or reranking APIs; a larger model or a reranker (Decision 3); a new dependency.
- The CI workflow `docs-retrieval-ci` (its own slice, started only after slice B's gate passes); a web UI; a database.
- Anything in `evals/`: read-only. README and `ARCHITECTURE.md` prose (slice B).

## Escalation path

- Needs more than the section 4 cap, or reads more than about 10 files: hand back to the Engineering Manager for a re-split.
- Wants anything in section 6's "new model, download or network access" or an INV text change: stop, write an approval request, and wait for the owner's own yes through the Orchestrator (`APPROVAL_PROTOCOL.md`). Never proceed on assumed approval.
- Failed gate or repeated failure: `FAILURE_LOOP.md` (2 retries, then the human).
