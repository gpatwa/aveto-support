# Intent: Find the right Aveto doc for a question — add a reranker

> **Confirmed 2026-09-30.** Drafted by Claude in the playbook session from
> slice 2's close-out (`runs/docs-retrieval-2-proof/02-close-out.md`). The
> owner delegated the three open questions, verbatim: "make a decision for
> the three questions and commit". Claude decided them as recorded under
> **Decisions**; the owner can overturn any before the slice starts. The
> reranker itself still needs the owner's own rule 4 and 5 approval, of the
> specific model, in the Orchestrator's session.
> Pass to `/agentic-slice intents/docs-retrieval-3.md` from a fresh worktree
> off `main`.

## What I want

Retrieval that finds the right Aveto doc for at least 80% of questions it has
never seen. Slice 2's file-level ranking reached about 70%: the right file was
usually near the top, but five narrow, specialised files lost to broader
neighbours. A reranker — a small model that reads the question together with
each candidate and re-orders the top few — targets exactly that. This slice
adds one, and changes nothing else.

## Done means

- [ ] Starts from `main` (slice 2's method `file-rrf-v1`, the 123-file corpus
      and pack v12). Corpus, first-stage ranking and the embedding model are
      unchanged.
- [ ] A **local reranker** re-orders the first stage's top candidates (the
      Architect proposes how many, on general grounds). It reads text; it never
      produces text. Pinned to an exact revision, every file checked against a
      recorded sha256, run on ONNX Runtime + numpy, no PyTorch, no
      `trust_remote_code`. Needs rule 4 and 5 approval of the specific model
      before anything is installed or downloaded.
- [ ] **Freeze first.** The method's commit is recorded; then a **fourth
      held-out set** (at least 15 answerable questions) is committed, **its
      labels reviewed by a fresh QA spawn before the set is committed; a
      different fresh QA spawn scores it** (Decision 2) — every defensibly-answering file listed
      (`project-packs/ai-agent-product.md`, "Held-out gates"). Run once.
- [ ] On that set, a correct file in the top 5 for **at least 80%** of
      answerable questions. That is the whole gate; unanswerable questions, if
      any, are diagnostic.
- [ ] The three earlier sets are reported alongside as diagnostics, with
      slice 2's method on the same sets, so the reranker's own effect is
      visible.
- [ ] Everything earlier slices guaranteed still holds: deterministic ingest,
      provenance on every passage, no generative model, no network outside
      ingest and CI setup, every model file hash-checked.

## Must not break

- Nothing retrieved is presented as an answer.
- The user can always see where every passage came from.
- The question and the docs never leave the machine.

## Constraints

- Python 3.12, uv, the existing structure. Retrieve stays offline.
- Nothing is chosen by its score on any eval set: the reranker, how many
  candidates it sees, and how its score combines with the first stage are
  argued before the run.
- One fresh agent per stage; don't resume the same agent across passes (slice
  1 processed 30.9M tokens that way, slice 2 6.7M).
- No Azure, no API key, no deploy; CI stays its own slice.

## Out of scope

- Any generative model, including an LLM reranker or query rewriting.
- Hosted reranking or embeddings APIs.
- Abstention ("the docs don't answer this") — owned by the check-step slice
  (Decision 3).

## Stakes

- [ ] Changes auth, permissions, or a safety control
- [x] None of the above — the new download changes INV-5, which the rule 4
      approval of the specific model covers, as in slice 1

## Decisions (were open questions)

1. **Budget: 600k, split at the freeze.** Slice A (Architecture,
   Implementation, freeze) 330k; slice B (label review, scoring, Security,
   Release Gate, close-out) 270k. Slice 2 used about 380k across both halves,
   and this slice adds a model proposal and its approvals. An overrun stops
   and asks with the numbers; the budget is never raised to fit.
2. **Labels are reviewed by a fresh QA spawn, inside the slice, after the
   freeze and before the set is committed.** It gets only the draft set and
   the pinned docs — not the method, the spec or any results — and lists
   every file that defensibly answers each question. The owner commits the
   reviewed set. A **different** fresh QA spawn scores it once, so the agent
   that saw the questions never grades the method. Chosen over an owner
   review to keep the owner's time to the approvals.
3. **The check-step slice is scheduled right after this one, and nothing
   that writes text for a user ships before it.** Abstention ("the docs don't
   answer this") is a safety requirement that slice 2 moved to the check step,
   which doesn't exist yet. No drafting slice may reach its Release Gate until
   the check-step slice has passed its own gate, with an abstention bar set in
   its intent in advance.
