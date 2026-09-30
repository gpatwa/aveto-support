# Approval Record 2 (docs-retrieval-2)

- **Request:** runs/docs-retrieval-2/APPROVAL_REQUEST-2.md (rule 4)
- **Decision:** APPROVED
- **Approver:** Gopal Patwa (owner; answered in the driving session)
- **When (UTC):** 2026-09-29T16:54:46Z
- **Scope approved:** retrieval stops abstaining: `retrieve` always returns its top 5 files with the top score and never prints 'no confident match'. INV-4's first clause still holds. Not approval for anything generative, a new model, or wider network access.

## Owner's response, verbatim

Prompted with this request separately (Approve / Deny or its alternative), the owner selected: "Approve: always return the top 5 files".

## Clarification added by the Orchestrator (after the Engineering Manager flagged a gap)

The question the owner answered said, verbatim: "INV-4's first clause (only verbatim passages with provenance, nothing presented as an answer) still holds; the second clause's test would be retired." So the owner was told, before answering, that the test for INV-4's second clause would be retired. That is `test_not_confident_returns_no_hits` only. **Not covered:** retiring or weakening any other INV-enforcing test (the verbatim and provenance tests stay at full strength), and any change to the text of INV-4 or INV-5 in `.agentic/SAFETY_INVARIANTS.md`. Removing the retired test's name from INV-4's "Enforced by" annotation is an edit to that file and is put to the owner before it is made.
