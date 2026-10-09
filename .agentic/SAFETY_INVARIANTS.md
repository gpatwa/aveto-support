# Safety Invariants

> **PARTIAL — seeded by hand from the owner's own statements in `README.md`,
> nothing inferred.** The Architect + Security stages still own this file and
> must extend it from the PRD/UX before any delivery stage runs. A missing
> invariant is not a permission.
>
> Each invariant: one line, testable, stated as what MUST hold across releases.

## Posting

- **INV-1** — Nothing is written to GitHub (issue comment, Discussion reply,
  or any other write) unless a person approved that specific reply first, and
  the approval is recorded. There is no code path that posts without one.
  *(README: "It never posts on its own: every reply is approved by a person
  first.")*

## Grounding

- **INV-2** — Every answer is drawn from Aveto's own documentation, and every
  drafted reply names the passages it came from.
  *(README: answers "from Aveto's own documentation"; step 3 drafts "a grounded
  reply".)*
- **INV-3** — A draft is checked against its sources by a different model from
  the one that wrote it; a claim the sources do not support is removed or the
  question is escalated — never posted as-is.
  *(README, step 4. Applies once drafting exists.)*

## Retrieval and network

- **INV-4** — Retrieval returns only verbatim passages from the configured
  source at its pinned commit, each with path, heading and line range; it does
  not abstain (a question the docs do not answer still returns its top files,
  and `eval` reports unanswerable questions as a diagnostic). It never returns
  generated or reworded text. **A model may be used only to rank passages and to decide confidence. It
  never produces, selects fragments of, or alters the text returned.**
  *(Enforced by `test_result_invariant_enforced`,
  `test_retrieved_text_is_verbatim_slice_of_file`,
  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
  `test_reranked_hits_are_verbatim_passages`,
  `test_reranked_result_invariant_enforced` and
  `test_reranker_returns_only_scores`.)*

- **INV-5** — The product's network egress is limited to two kinds of
  read-only HTTPS GET download, both made only by `ingest`:
  (a) the archive of the configured GitHub repo at a full 40-hex commit, with
  redirects only to `github.com` / `codeload.github.com`; and
  (b) the pinned files of exactly two local models — the configured embedding
  model (`docs-source.toml`) and the reranker model pinned in
  `aveto_support/rerank.py` — each requested from `huggingface.co` at its own
  full 40-hex revision, with redirects only to hosts under `hf.co` (for example
  `us.aws.cdn.hf.co`).
  Of the two models, the default path fetches only the embedding model's files:
  **`ingest`** fetches the reranker's files only when run with **`--with-reranker`**.
  Every model file is checked against its committed sha256 **before it is
  used**. On a mismatch the file is deleted and ingest fails. Trust rests on the
  hash, never on the host. No credentials are sent. **No question, passage or
  user text ever leaves the machine.** `retrieve`, `eval` and the default test
  suite make no network calls.
  *(Enforced by `test_redirect_to_other_host_refused`,
  `test_hf_redirect_outside_hf_co_refused`, `test_short_sha_rejected`,
  `test_model_revision_must_be_40_hex`,
  `test_model_hash_mismatch_rejected_and_deleted`,
  `test_cached_file_rehashed_before_use`,
  `test_retrieve_is_offline_with_cached_model`,
  `test_reranker_revision_must_be_40_hex`,
  `test_reranker_hash_mismatch_rejected_and_deleted`,
  `test_reranker_cached_file_rehashed_before_use`,
  `test_reranker_redirect_outside_hf_co_refused`,
  `test_retrieve_is_offline_with_cached_reranker`,
  `test_default_ingest_fetches_no_reranker`,
  `test_default_ingest_makes_no_reranker_request`,
  `test_ingest_with_reranker_fetches_and_rehashes`,
  `test_reranker_absent_fails_closed_without_download`, and the autouse network
  block.)*
