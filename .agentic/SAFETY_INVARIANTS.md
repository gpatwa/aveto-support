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

- **INV-4** — Retrieval returns only verbatim passages from the configured source
  at its pinned commit, each with path, heading and line range, or "no confident
  match" with no passages. It never returns generated or reworded text.
  *(Architect, docs-retrieval-core, `runs/docs-retrieval/02-tech-spec.md`.
  Enforced by `tests/test_search.py::test_not_confident_returns_no_hits`,
  `test_result_invariant_enforced` and
  `tests/test_index.py::test_retrieved_text_is_verbatim_slice_of_file`.)*
- **INV-5** — The product's only network egress is the HTTPS archive fetch of the
  configured GitHub repo at a full 40-hex commit. Redirects go only to
  `github.com` / `codeload.github.com`, and no credentials are sent.
  *(Architect, docs-retrieval-core. Rule-5 approval:
  `runs/docs-retrieval/APPROVAL_RECORD-1.md`. Enforced by
  `tests/test_ingest.py::test_redirect_to_other_host_refused`,
  `test_short_sha_rejected`, `test_default_network_is_blocked` and the autouse
  network block in `tests/conftest.py`.)*
