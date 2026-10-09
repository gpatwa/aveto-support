# Approval Record 1: docs-retrieval-4, rule 4 (change a safety control)

- **Request:** `runs/docs-retrieval-4/02-approval-request.md`
- **Rule:** `HUMAN_APPROVAL_RULES.md` rule 4
- **Decision:** APPROVED, with one wording change by the owner
- **Approver:** Gopal Patwa (the owner), in the Orchestrator's own session
- **When (UTC):** 2026-10-03T06:42:53Z
- **Recorded by:** Orchestrator

## The owner's words, verbatim

> Approved under rule 4, with one wording change to the INV-5 sentence. It reads: "Of the two models, the default path fetches only the embedding model's files: ingest fetches the reranker's files only when run with --with-reranker." The four test names added to INV-5's enforced-by list, and the new default behaviour of ingest in part 2, exactly as written. Nothing wider.

## What is approved

1. **The INV-5 sentence, as the owner worded it** (this REPLACES the sentence quoted in the request and in `02-tech-spec.md` section 4; apply the owner's text, in the same position, after clause (b)):

   > Of the two models, the default path fetches only the embedding model's files: ingest fetches the reranker's files only when run with --with-reranker.

   Typography (bold, backticks around `ingest` and `--with-reranker`) follows the file's existing style; the words are the owner's, unchanged.
2. **The four test names**, added to INV-5's enforced-by list exactly as written in the request: `test_default_ingest_fetches_no_reranker`, `test_default_ingest_makes_no_reranker_request`, `test_ingest_with_reranker_fetches_and_rehashes`, `test_reranker_absent_fails_closed_without_download`.
3. **The new default behaviour of `ingest` (part 2 of the request), exactly as written** there.

## Not approved ("Nothing wider")

Anything beyond the above. In particular the owner did not, in this answer, grant the optional extras raised alongside the request (a cap exception for `docs/ARCHITECTURE.md`; an extra 200-run `retrieve` loop per mode). They are not part of this slice's scope unless the owner says so.

An earlier message from the "Aveto AI SDLC" session suggested the 200-run loop; it was advice, not an approval of anything.
