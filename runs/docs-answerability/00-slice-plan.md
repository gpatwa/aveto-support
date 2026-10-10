# Slice plan — docs-answerability

> Orchestrator, 2026-10-10. **Proposed; not confirmed.** Nothing past Scope Review starts, and nothing is spawned, until the owner confirms in the driving session.

## Outcome (one line)
An operator-run judge step (a Haiku-class subagent in their own Claude Code session) decides whether the shown passages answer the question; the program stays offline and gains a judge-input mode, a verdict-applying command that prints exactly `no confident match`, and `eval` scoring two bars from a verdicts file.

## Success criteria
Taken verbatim from `intent.md` "Done means" (the intent is the source of truth; not restated here to avoid drift). The two bars are fixed: 20/24 unanswerable abstained; at least 80% of answerable-with-right-file-in-top-five not abstained. Pre-registered continue-or-stop: seen sets, pooled at least 16/20 and 45/56, before the freeze.

## Stages (tier 2; adversarial Security binds, per the intent; Release Gate not compressed)
Estimates are peak-context units from `RUN_ECONOMICS.md` (review 50–60k, 100–130k adversarial; build ~130k; Release Gate three spawns ~150k; Architecture ending in an approval request is two passes). The intent's own figure (about 700k) is lower than these measured ratios; see "Findings".

| # | Stage | Owner | Depth | Est. | Slice |
|---|-------|-------|-------|------|-------|
| 1 | Scope Review (claims vs code; read list tight) | Engineering Manager | standard | 55k | A |
| 2 | Architecture, pass 1 (spec: modes, contract, verdict grammar, where the judge lives, tool list verified against generated agent files and the pilots' prompt) | Software Architect | standard | 80k | A |
| 2b | Architecture, pass 2 (INV-4/INV-5 exact words, ADR 0008, approval packet) | Software Architect | standard | 60k | A |
| 3 | Implementation (three offline pieces + tests + judge artefacts; after rule 4/5/6 approvals) | AI Engineer | standard | 130k | A |
| 4 | Seen-set integration check, pre-registered (93 questions through the product's own block output, fresh judge subagents per batch under the tool-use audit) | QA Evidence | standard | 100k | A |
| — | **Freeze:** method commit SHA recorded in STATE.md; owner told; owner hands over the fifth set | Orchestrator | — | 0 | — |
| 5 | Label review of the fifth set (attacks the unanswerable labels) | QA Evidence, fresh | adversarial on unanswerable | 60k | B |
| 6 | Score once, different fresh spawn, tool-use audit | QA Evidence, fresh | standard | 100k | B |
| 7 | Security Review | Security & Privacy | **adversarial** | 115k | B |
| 8 | Release Gate (plan, QA run, Release Manager verdict: three spawns) | QA / Release Manager | standard | 150k | B |
| 9 | README + `CURRENT_MVP_STATUS` + stale lines, after the verdict only | Tech Writer | smoke | 30k | B |
| 10 | Close-out | Post-Launch Learning | standard | 55k | B |

Plan total: **A 425k + B 510k = 935k**, rounded to **950k**. Seen-set check failing stops the slice at stage 4 (about 365k spent) and goes to the owner with the numbers.

**Proposed ceiling: 1.4M** (about 1.5× the plan: the plan has an adversarial Security Review and an approval-bearing Architecture). The owner types the ceiling once; I never raise it.

Skipped on purpose (short path, per the intent): Market Research, PRD, UX, UI, Cloud Deployment, SRE, Production Verification. The intent is the PRD.

## Approvals (all the owner's, typed in this session)
- **At plan confirmation (one packet):** plan and intent; owner decisions 3 and 4; the ceiling; rule 6 (data processor).
- **End of Architecture (one packet):** rule 4 exact INV-4 and INV-5 words; rule 5 (the judge artefacts: prompt with sha256, agent definition, tier, tools). No safety-control text is edited before the exact words are approved, and none is applied before the code or artefact it describes.
- **End of Security (one packet):** anything outstanding.

## Non-goals
Drafting, the INV-3 draft checker, classification; any change to retrieval, ranking, corpus or embedding model; any model other than the one judge; posting; unattended or scheduled operation; any credential; the `docs-retrieval-ci` workflow; the Azure runner.

## Constraints (from `.agentic/` and the intent)
Python 3.12, uv, no new runtime dependency. No metered API, no key, no `claude -p`. INV-1..5 hold; INV-4 and INV-5 change only by approved words. Held-out rules: the builder does not write the set; freeze, then commit the set, then run once; bars never move. One fresh agent per stage, never resumed across passes. Full regression: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`.

## Findings: intent claims and status lines checked against the code
1. **Judge input is not the displayed text.** The pilots' judge read the full text of at most two passages per file; `retrieve` prints only 3 non-empty lines of at most 160 characters per passage (`aveto_support/__main__.py:26-37`). The judge-input mode must be its own formatter, and the contract must say the judge reads more than the user sees. The intent's wording (full text of shown passages) already implies this; the Architect must not reuse `_excerpt`.
2. **The pilots' prompt is not a standalone committed file.** It is the section "The judge prompt (fixed...)" of the playbook's pilot doc (line 103). The product needs it as a file with a sha256, copied verbatim and verified by the Architect.
3. **Budget:** the intent's 700k is below what the measured ratios give (about 935k). Both are shown so the owner can choose; the intent's own split A/B is kept, each half under 600k.
4. **Stale in `.agentic/CURRENT_MVP_STATUS.md`:** "Not yet done" says `tests/fixtures/wordpiece_golden.json` is missing; the file exists. Lines 8-10 and 17-18 carry the older stale items from `runs/docs-abstention/06b`. Corrected only after the verdict (Tech Writer, stage 9).
5. **Stale in `docs/ARCHITECTURE.md`:** line 193 lists ADR 0007 (local judge) as the abstention decision; ADR 0007 is rejected. A superseding ADR 0008 is needed; older stale lines (header, L106-109, eval exit rule, L21, L79-80, L103) are carried from the slice 5 close-out.
6. **Counts verified:** the four seen eval files hold 23 + 20 + 20 + 30 = 93 questions, matching the intent's 93.
7. **Generated agents:** `.claude/agents/` holds 28 installer-generated roles and no judge. The installer rewrites that directory, so a product-local judge cannot live there unprotected; the Architect decides placement after reading the installer, not from memory.
8. **README and INV-5 wording** are consistent with the intent: `retrieve`/`eval` offline, "never abstains" today. INV-5's "No question, passage or user text ever leaves the machine" is the sentence rule 4 rescopes.

## Open questions
None in the intent. Owner decisions 3 (data processor: Anthropic, via the operator's own Claude Code session) and 4 (attended only) are the recommended answers awaiting the owner's own words.
