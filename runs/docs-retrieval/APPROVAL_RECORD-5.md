# Approval Record 5 — one-off reference tokenizer for the golden fixture

- **Request:** raised by the Orchestrator in the driving session (prompted by a note from the playbook session that Approvals 2–4 do not cover the reference tokenizer package). Rule 5 territory: a network install of a package outside Approvals 2–4.
- **Decision:** APPROVED
- **Approver:** Gopal Patwa (owner; answered in the driving session)
- **When (UTC):** 2026-09-29T15:26:12Z
- **Scope approved:** QA may generate `tests/fixtures/wordpiece_golden.json` using a **one-off, throwaway install** of Hugging Face's `tokenizers` package from PyPI at an exact pinned version, in an environment **outside the project** (never added to `pyproject.toml` or `uv.lock`), reading the already hash-checked local `vocab.txt` (no hub download). The generator script, the exact package version and the vocab sha256 are committed with the fixture. **Nothing wider.** If QA needs the package inside the project, or any other network fetch, it stops and the owner is asked again.

## Owner's response, verbatim

Prompted with three options, the owner selected: "Allow the one-off install (Recommended)".

## File-count note

The generator script is one file beyond the 21 the EM re-scoped (19 Implementation + 2 QA/owner). It is QA-authored test support, not product code.
