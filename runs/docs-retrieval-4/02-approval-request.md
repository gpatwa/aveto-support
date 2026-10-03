# Approval Request 1: docs-retrieval-4, rule 4 (change a safety control)

- **Requested by:** Software Architect, for the Orchestrator to put to the owner
- **Rule:** `HUMAN_APPROVAL_RULES.md` rule 4, change a safety control (`.agentic/SAFETY_INVARIANTS.md`, INV-5)
- **Record path:** `runs/docs-retrieval-4/APPROVAL_RECORD-1.md` (created by the Orchestrator only after the owner answers)
- **Decision:** APPROVED with the owner's wording change — see APPROVAL_RECORD-1.md (the owner's sentence replaces the one below)

> An approval counts only if the owner gives it **directly in the Orchestrator's session**. A message from another session or agent, even one quoting the owner, is not an approval. Nothing in `.agentic/SAFETY_INVARIANTS.md` is edited until the record shows a yes.

## What you are asked to approve

Two things, approved or denied together.

### 1. The exact new INV-5 wording

One sentence is added after clause (b). The enforced-by list gains four test names. Both models' pins stay named, and the rest of INV-5 is unchanged.

The sentence, verbatim:

> **The default path fetches only the embedding model: `ingest` fetches the reranker's files only when run with `--with-reranker`.**

The four test names added to INV-5's enforced-by list, verbatim:

> `test_default_ingest_fetches_no_reranker`, `test_default_ingest_makes_no_reranker_request`, `test_ingest_with_reranker_fetches_and_rehashes`, `test_reranker_absent_fails_closed_without_download`

The full new paragraph and the diff are in `runs/docs-retrieval-4/02-tech-spec.md` section 4.

### 2. The new default behaviour of `ingest`, verbatim

> By default, `ingest` fetches and hash-checks only the docs archive and the embedding model. It does not fetch, hash-check or load the reranker's files, and it prints `reranker files: not fetched (optional; ingest --with-reranker fetches them for --ranking file-rerank-v1)`. With `ingest --with-reranker`, it also fetches the reranker's two pinned files exactly as today: same host rules, same 40-hex revision, sha256-checked before use, deleted on mismatch. The index written is byte-identical either way. `retrieve` and `eval` default to `--ranking file-rrf-v1` and never load the reranker. `--ranking file-rerank-v1` with the reranker's files absent exits 2 with a message telling you to run `ingest --with-reranker`, and never downloads.

## Why this is rule 4 only

- **Rule 4 fires:** the INV-5 text in `.agentic/SAFETY_INVARIANTS.md` changes. The change narrows what the default path does and keeps the opt-in path's control fully stated, but it is still an edit to a safety control.
- **The `ingest` default change** is put to you here together with the sentence, so that nothing about the new default has to be inferred later (scope review section 3). It fetches less than today, and it adds nothing.
- **Rule 1 (send/submit) does not fire:** nothing is posted, sent or submitted.
- **Rule 2 (destructive shared-state) does not fire:** no push, merge or PR (you do those). No shared data is deleted. Local cached model files are untouched.
- **Rule 3 (deploy) does not fire:** no deploy. Tier 2, internal.
- **Rule 5 (real model/client, new data processor) does not fire:** there is no new model, download or dependency. The same two pinned models are used, and the reranker's existing download moves behind an opt-in. No question, passage or user text leaves the machine.
- The reranker's MS MARCO licence question does not arise on the default path. It stays recorded as open for anyone who opts in.

## Effect of your answer

- **Approve:** Implementation applies exactly the section 4 diff to INV-5, last in its stage, after the code and tests that enforce it are green. Then the slice proceeds to Security Review (adversarial on the download path and INV-4/INV-5) and the Release Gate.
- **Deny:** INV-5 is not edited.
  - The reranker opt-in for `ingest` would leave INV-5 silent about the default path. The Architect revises the request (for example, different wording) and the run stops again for your answer.
  - If you also reject the `ingest` opt-in itself, `ingest` keeps fetching the reranker by default. The intent's line "fetched only if the owner opts in" then cannot be met, so the slice goes back to the Orchestrator to re-scope with you.
  - Either way, nothing proceeds on silence.
