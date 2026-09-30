# Intent: Find the right Aveto doc for a question — retrieval, second attempt

> **Confirmed 2026-09-29.** Drafted by Claude in the playbook session from the
> first slice's close-out (`runs/docs-retrieval/08-close-out.md` on branch
> `claude/repo-review-b01795`). The owner delegated the three open questions,
> verbatim: "make a decission for 1 - 3 and execute it". Claude decided them
> as recorded under **Decisions**; the owner can overturn any of them before
> the slice starts. Decision 1 changes a gate from the first intent, so the
> Orchestrator should still take the owner's own rule 4 yes in its session.
> Pass this file to `/agentic-slice intents/docs-retrieval-2.md`.

## What I want

The retrieval step of the Aveto support agent, working well enough to trust:
given a question about Aveto, return the files in Aveto's user documentation
that answer it, with exact provenance. The first slice built the machinery —
ingest, provenance, a deterministic index, a local embedding model fused with
keyword search — and proved, with a held-out set, that its method finds the
right file for only 8 of 17 new questions. This slice changes the method, not
the machinery, and proves the change the same way.

## Who it's for

The owner now; the drafting and checking steps next, which can only be as good
as the sources this step hands them.

## Done means

- [ ] Starts from the first slice's code (branch `claude/repo-review-b01795` at
      `fba5233`), with `main` merged in and `main`'s pack files taken on
      conflict.
- [ ] **Corpus scope is fixed before any run, on principle:** the index
      covers exactly the user-documentation list in Decision 2, recorded in
      config, and is never tuned after a run.
- [ ] **Ranking is file-level:** results are files, each carrying the passages
      that matched with their heading and line range, because the question a
      user asks is "which doc", and the eval scores files.
- [ ] **Freeze first, again.** The method is frozen and its commit recorded;
      only then does the owner commit a **third, fresh held-out set** (at least
      15 answerable questions; unanswerable questions are optional and diagnostic
      only, per Decision 1), written by the owner or drafted outside the slice and reviewed and
      committed by the owner. Run once.
- [ ] On that held-out set, a correct file appears in the top 5 for **at least
      80%** of answerable questions. That is the whole gate (Decision 1).
- [ ] The two earlier sets are reported alongside as diagnostics; neither
      gates.
- [ ] Everything the first slice's "Done means" guaranteed still holds:
      deterministic ingest, provenance on every passage, no generative model,
      no network outside ingest and CI setup, every model file hash-checked.

## Must not break

- Nothing retrieved is presented as an answer.
- The user can always see where every passage came from.
- The question and the docs never leave the machine.

## Constraints

- Python 3.12, uv, the existing structure; the approved model
  (`BAAI/bge-small-en-v1.5` @ `5c38ec7c…`, ONNX Runtime + numpy) stays
  the only model. No larger model and no reranker (Decision 3).
- Nothing is chosen by its score on any eval set: corpus list, ranking method
  and model are argued on general grounds before the run.
- No Azure, no API key, no deploy. The CI workflow (`docs-retrieval-ci`) stays
  a separate slice, started only after this gate passes.
- Fix the stale "retrieval only, no model" line in
  `.agentic/PROJECT_CONTEXT.md` (close-out §7).

## Out of scope

- Any generative model call: drafting, checking, query rewriting, LLM
  reranking.
- Hosted embeddings or reranking APIs.
- The CI workflow; a web UI; a database.

## Stakes

- [ ] Touches real user data
- [ ] Moves money, or changes billing
- [ ] Irreversible — deletes, sends, or deploys to live users
- [ ] Changes auth, permissions, or a safety control
- [ ] Adds a screen or UI a user will see
- [x] None of the above (no new model or download: Decision 3)

## Decisions (were open questions)

1. **"The docs don't answer this" moves to the check step.** Two methods
   failed to decide it from a similarity score — answerable and unanswerable
   questions score in the same band — and the README design already has a
   check step where a model reads the passages. Retrieval is gated on
   "correct file in the top 5" for ≥80% of answerable held-out questions.
   Retrieve still prints its top score, and unanswerable questions, if the
   held-out set includes any, are reported as a diagnostic. This removes the
   unanswerable half of the first intent's gate: a rule 4 change, made here in
   advance, not in reaction to a result. The check-step slice must carry the
   abstention requirement forward; it is moved, not dropped.
2. **User documentation is:** `README.md`; `docs/GETTING_STARTED.md`,
   `docs/AGENTIC_SDLC.md`, `docs/AGENT_ROLES.md`, `docs/HUMAN_APPROVAL_RULES.md`,
   `docs/RELEASE_GATES.md`, `docs/OPERATING_MODEL.md`, `docs/DEPLOYMENT.md`,
   `docs/STANDARDS_WATCH.md`, `docs/VALIDATION_MATRIX.md`,
   `docs/PIPELINE_ANALYTICS.md`; and everything under `agents/`, `templates/`,
   `project-packs/`, `prompts/`, `skills/`, `examples/` and `execution/`.
   **Excluded as maintainer material:** `docs/BACKLOG.md` (the planning
   backlog), `docs/ARCHITECTURE.md` (the playbook's own internals),
   `docs/PLATFORM_EVAL.md` (research notes), and anything under `runs/` or
   `site/`. Disclosed: the decider has seen that BACKLOG and ARCHITECTURE
   appeared in slice 1's wrong answers. The exclusions are argued from
   audience, and none of the excluded files is a labelled source in either
   earlier eval set.
3. **No stronger model in this slice.** Only the approved bge-small model.
   This keeps the slice cheap, needs no new approvals, and is a clean test of
   the close-out's two hypotheses: corpus scope and file-level ranking. If it
   fails, a reranker is the next slice's question.
