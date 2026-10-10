# Approval record 7 — 3b design (addendum 02c section 8 items 1-4) and the skill change

- **Decision:** items 1, 2 and 3 approved with the conditions below; item 4 denied; one additional owner change.
- **Approver:** the owner (Gopal Patwa), typed directly in the session driving this run
- **When (UTC):** 2026-10-10T05:42:01Z
- **Item 1 (frontmatter realised as `tools` omitted + `disallowedTools` + hook + `model: claude-haiku-5-5`):** approved.
- **Item 2 (live refusal probe):** approved, **at most two judge spawns for the probe** (this caps the addendum's "at most 2 spawns plus 1 re-probe"; any need beyond two comes back to the owner).
- **Item 3 (what counts as refused):** outcome A (tool never offered) counts, **as long as the probe also tries an `mcp__` tool and the Release Gate says plainly whether a live hook refusal was seen.**
- **Item 4 (temporary probe agent with a real tool):** no.
- **Additional change:** `/aveto-judge` is a **skill** with `disable-model-invocation: true`, same name — not a command file. This supersedes packet 3.3(c) and addendum section 5 (command file). The skill lives at `.claude/skills/aveto-judge/SKILL.md`.
- **Unchanged:** APPROVAL_RECORD-5's two conditions (full model ID; stop and ask unless a test shows a tool call refused).

**Owner's response, verbatim:**

> Item 1: approved. Item 2: approved, at most two judge spawns for the probe. Item 3: outcome A counts, as long as the probe also tries an mcp__ tool and the Release Gate says plainly whether a live hook refusal was seen. Item 4: no. Also: make /aveto-judge a skill with disable-model-invocation: true, same name.
