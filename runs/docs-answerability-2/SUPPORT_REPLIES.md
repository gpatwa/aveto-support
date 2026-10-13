# Support replies — docs-answerability-2

> Writer: the support/playbook session ("Aveto AI SDLC"). One writer per file. Nothing here is an approval. Items marked "recommended default under SI-1" are design choices the Orchestrator may adopt and list in the next digest; items marked OWNER are not decided here.

## Reply 1 — read of `01-measurement.md` (stage 1)

Read in full on 2026-10-12. The measurement is clean: two spawns, `claude-sonnet-5-5` as logged, 7 offered tools, zero tool calls, one request each, 14.2k and 14.3k peak, second spawn a cache hit (in-equivalent 9.4k).

**D1 (recommended default under SI-1, but the agent-file diff goes to the OWNER first, as in slice 6).** Add the seven remaining harness tools (`DesignSync`, `ListPlugins`, `ListSkills`, `SearchPlugins`, `SearchSkills`, `SuggestPluginInstall`, `SuggestSkills`) to the judge's `disallowedTools`. Two reasons. Cost: the report puts them at about half the first request (~6.9k of 14.2k), about 0.33M per 48-spawn stage. Safety: slice 6's probe 2 found these seven were covered by the hook alone and never refused live; denying them makes layer (a) cover everything and leaves the hook as a true second layer. Verify in the stage 4 smoke test that the deny list is accepted (the offered tool count in `prefix.json` should be 0) and that a zero-tool subagent still returns its verdict. Needs a fresh-load session afterwards. Bring the exact diff to the owner before applying.

**D2.** The report's "harness prefix is 94 characters, not 150" compares the wrong thing: 94 is the system block's `cliPrefix`; slice 6's 150 was the `Base directory for this skill: <path>` line that opens the user prompt. The registered layout is that line followed by the payload. Stage 3 should state the line's length as measured in this worktree, and not use 94.

**D3.** INV-5's wording (stage 3b) should list what the judge receives, from the report's table: the question and passages; the project instruction files (`CLAUDE.md` / `AGENTS.md`, taken from the main checkout path, not the worktree); the user's email; git branch, user and five recent commit subjects; environment lines. Words are the OWNER's at rule 4.

**D4.** No budget change is needed from stage 1. With D1 the spawn stages fall below the plan's lines; without D1 the all-in ratio (about 1.5× bare) puts stages 5 and 7 about 0.45M over their 800k lines, still inside the 3.4M ceiling. The ceiling is the OWNER's.
