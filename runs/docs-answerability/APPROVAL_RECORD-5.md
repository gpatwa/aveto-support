# Approval record 5 — rule 5: the judge step, with two owner conditions

- **Decision:** approved as in `02b-approval-packet.md` section 3, **amended by the owner in two ways**
- **Approver:** the owner (Gopal Patwa), typed directly in the session driving this run
- **When (UTC):** 2026-10-10T05:13:28Z
- **Amendment 1 (supersedes the packet's `model: haiku` row, 3.3(b)):** the model is pinned to the full ID `claude-haiku-5-5`, **not** the alias `haiku`. The alias is not approved. If Claude Code does not accept the full ID in the agent's frontmatter, that is a stop-and-ask, not a fallback to the alias.
- **Amendment 2 (stop condition):** if no zero-tool form can be shown by a **test that a tool call is refused**, stop and ask the owner. No fallback to any tool (not `tools: Read`, not any other). "Shown by a test" means evidence that a tool call by the judge is refused, not only that the definition lists no tools.
- **Unchanged:** prompt `prompts/answerability-judge-v1.txt`, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427; the command `/aveto-judge`; attended use only; the not-approved list in packet 3.4. Rule 6: APPROVAL_RECORD-2.

**Owner's response, verbatim:** see APPROVAL_RECORD-4 (one message).
