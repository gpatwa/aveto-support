# 03c — INV-4 / INV-5 applied (Software Architect)

Authority: `APPROVAL_RECORD-4.md` (rule 4, approved as written), packet `02b-approval-packet.md` 2.1, 2.2, 2.4. Not committed.

## What changed

Only `.agentic/SAFETY_INVARIANTS.md`:

- INV-4 (was lines 31-42) replaced by the 2.1 "Proposed" block (packet lines 44-72); now lines 31-59.
- INV-5 (was lines 44-75) replaced by the 2.2 "Proposed" block (packet lines 163-212); now lines 61-110.
- Header, INV-1..INV-3, section headings and the blank line between INV-4 and INV-5 untouched (edits were bounded `Edit` replacements inside the two entries only).
- 2.5 mirrored-sentence edits (README, ARCHITECTURE, PROJECT_CONTEXT, status) NOT made; they remain for the Tech Writer.

## How verbatim was checked

Text copied from the packet's fenced blocks. After the edit the file was re-read and compared line by line against packet 2.1 Proposed and 2.2 Proposed: same line breaks, two-space continuation indent, bold/backtick/italic markers and punctuation. INV-5's unchanged middle (packet "lines 46-55" and "61-73") was left in place, and matches the packet's Proposed block. No shell, so no byte-level diff was run; the Release Gate or the Orchestrator can confirm with `git diff .agentic/SAFETY_INVARIANTS.md` against the packet's diff blocks.

## Test-name existence (grep `def <name>` in `tests/`)

All cited names exist except one:

- **MISSING: `test_command_definition`** (cited in INV-5). `tests/test_judge_artefacts.py` has `test_skill_definition` (line 144) instead; 3b built `/aveto-judge` as a skill (`.claude/skills/aveto-judge/SKILL.md`), and no `.claude/commands/aveto-judge*` exists.
- The autouse network block exists (`tests/conftest.py:22`).
- Present: the six INV-4 retrieval tests (test_search, test_index, test_rerank), the eight INV-4 judge-step tests (`tests/test_judge.py`), the sixteen INV-5 ingest/rerank tests (test_ingest, test_rerank), the five INV-5 judge tests (`tests/test_judge.py`), and `test_agent_definition` and `test_transport_dir_ignored` (`tests/test_judge_artefacts.py`).

Words NOT changed. Consequence: the file now names a test that does not exist, which packet 2.4 says must not happen, and the Release Gate check "every named test exists and passes" fails. To fix it, the Orchestrator must choose: either add a test named `test_command_definition` (AI Engineer; it must check the artefact's shape), or make a new rule 4 request to cite `test_skill_definition`. Related, but not a test-name issue: the approved packet (3.3c) put `/aveto-judge` in a command and rejected a skill, and the as-built artefact is a skill. INV-5's words do not say "command" for it, but the Orchestrator should confirm the skill form is covered by the rule 5 approval.

## Orchestrator addendum
Verbatim check redone by the Orchestrator: the 46 added lines in `git diff` equal the 46 `+` lines of packet 2.1/2.2, no others. Missing test name resolved on default (SI-1 #3), wording untouched: `test_skill_definition` renamed to `test_command_definition` (the /aveto-judge command ships as a skill, APPROVAL_RECORD-7). All 37 cited test names now exist; ruff, mypy clean, 267 passed.
