# APPROVAL_RECORD-1 — Charter approved (owner, typed, 2026-10-21)

Approver: **Gopal Patwa** (owner, in the driving session). Owner's words: "Approve runs/public-ask-the-docs/CHARTER.md, sha256 d0acc5346a80e199e3f95ac57e23a2c01fec43e56d93dbda3b4a03e6a99fa74c"

Recorded at: 2026-10-21T06:42:08Z (`date -u` when recorded; the owner's message carries no timestamp).
Hash re-computed before recording: matches.
An earlier message, "charter approved and gate review at stage 18", did not name the file's hash and was not recorded as the approval; its second half is taken as the owner's instruction that the C6.7 gate-set check happens before stage 18.

Effect: the run proceeds under Charter C1 to C10 (plan 2000k, ceiling 3000k, hard cap 3600k). Covered gated actions: C3.1 runtime judge via the Anthropic API; C4.1 Anthropic, C4.2 Azure; C5.1 INV-4 and C5.2 INV-5 words within bounds (adversarial check by Security); C8.3 the named resources in `rg-aveto-ask` and the deploy; C8.2 push of `claude/public-ask-the-docs` and a pull request into `main`. Merge is not covered.
