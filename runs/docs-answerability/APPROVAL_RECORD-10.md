# Approval record 10 — re-registration: verdict read from the last non-empty line

- **Approver:** the owner (Gopal Patwa), typed directly in the session driving this run
- **Decision:** approved
- **Scope:** the verdict grammar (spec 4.1) reads the verdict from the last non-empty line, which must match the existing line grammar (optional colon kept); earlier lines ignored, never shown or stored outside the ledger; if the last line fails the grammar it is still a judge error; tests of SUPPORT_REPLIES.md Reply 7 item 1; nothing else loosened. The 12 stored raw replies (r001-r012) are re-applied offline to the new parser and disclosed as produced under the previous grammar. r013-r093 run as one run. Bars unchanged (16/20, 45/56). Stop at the first anomaly other than a judge error.
- **Ceiling:** the owner's message left the ceiling as the unfilled placeholder "[type your number]". No new number was given, so the ceiling stays **2.6M** (APPROVAL_RECORD-8); the Orchestrator does not raise it. Stop and ask above it.
- **Note (Reply 7 item 3):** this rule was chosen after seeing two failures on the seen sets; the protection is the fifth set, untouched until freeze.

**Owner's response, verbatim:**

> Decision on the seen-set method: read SUPPORT_REPLIES.md Reply 7. I approve re-registering the verdict grammar to read the verdict from the last non-empty line, which must match the existing grammar (colon tolerance kept), with the tests Reply 7 lists and nothing else loosened. Re-apply the new parser offline to the 12 stored raw replies, disclose that r001 to r012 came from the previous grammar, then run r013 to r093 as one run. Bars unchanged. Stop at the first anomaly other than a judge error. Ceiling: [type your number], stop and ask above it.
