# Slice plan — docs-answerability-2

> Orchestrator, 2026-10-12. **Proposed; not confirmed.** Units: **peak context summed per spawn** (the pack's unit) unless a line says otherwise.

## Outcome (one line)
An operator-run Sonnet 5.5 judge step (full ID pinned) decides whether the shown passages answer the question; the program stays offline and prints exactly `no confident match` on NOT_ANSWERABLE. Method registered up front; measured first.

## Success criteria
`intent.md` "Done means", verbatim by reference (not restated). Bars fixed: 20/24 unanswerable abstained; at least 80% of answerable-with-right-file-in-top-5 not abstained. Sample check before the freeze: at least 16/20 and at least 23/28 (48 spawns).

## Stages (tier 2; Security binds at **adversarial** per the intent)

| # | Stage | Owner | Depth | Environment | Est. |
|---|-------|-------|-------|-------------|------|
| 1 | Measurement: two one-question Sonnet spawns via the forked skill; offered tool count, peak, in-equiv; read-only report of what a forked judge receives (CLAUDE.md, email, git status); projection | Orchestrator drives, fresh QA records | smoke | **fresh-load** (owner-started session in this worktree) | 100k |
| 2 | Scope Review (claims vs code, tight read list) | Engineering Manager | standard | default | 60k |
| 3 | Architecture pass 1: tech spec with the registered method (payload layout, grammar, thresholds, sample rule, judge-error counting, session-context finding) | Software Architect | standard | default | 130k |
| 3b | Architecture pass 2: INV-4/INV-5 exact words, ADR 0008 (rewritten), approval packet | Software Architect | standard | default | 90k |
| 4 | Implementation: pin Sonnet, sample key (48), fix the 3 tests that read slice 6's run key, context text, tests incl. offline test | AI Engineer | standard | default (**fresh-load** after, if agent/skill files change) | 130k |
| 5 | Integration check, 48 spawns (sample, registered) | QA Evidence, fresh | standard | **fresh-load**, driver is a fresh context | 800k |
| — | **Freeze:** method commit recorded; owner told; support session hands over the fifth set | Orchestrator | — | — | 0 |
| 6 | Label review of the fifth set (unanswerable attacked hardest) | QA Evidence, fresh | adversarial on unanswerable | default | 110k |
| 7 | Scoring once, 48 spawns, different fresh QA, tool-use audit | QA Evidence, fresh | standard | **fresh-load** | 800k |
| 8 | Security Review | Security & Privacy | **adversarial (binds)** | default | 125k |
| 9 | Release Gate (plan, QA run, Release Manager: three spawns) | QA / Release Manager | standard | default | 150k |
| 10 | README + `CURRENT_MVP_STATUS`, after the verdict only | Tech Writer | smoke | default | 30k |
| 11 | Close-out | Post-Launch Learning | standard | default | 55k |

**Plan total: about 2.58M** (stages 1-5: 1.31M; 6-11: 1.27M). Stage 5 failing stops the slice at about 1.3M with the numbers.
Not in the plan: one scoring rerun (the intent allows one; about +0.8M).

## Derived from slice 6's measured ratios (`07-close-out.md`, `05-lean-measurement.md`)
- Whole slice: **2.6×** plan (2.5M vs 950k), but almost all of it in one stage.
- Stages before the check: 717k against about 325k planned (**2.2×**); they included an unplanned addendum, two probes and an extra pass. Slice 4 ran 1.45×, slice 5 1.2-1.3×.
- Per spawn: projected 12.1-13.1k peak (1.17M for 93); actual all-in about 1.76M for the check session (**~19k per question** with drivers, QA passes and reruns), i.e. **1.5× the per-spawn projection**.
- Here the spawn stages are priced at 16k per spawn plus overhead (about 800k for 48), i.e. already above the slice 6 projection but at slice 6's actual all-in rate (19k × 48 = 0.91M) the two spawn stages would add about 0.2M. Stage 1 replaces this guess with a measurement.

## Proposed figures (you type the real ones)
| | Proposal | Basis |
|---|---|---|
| Plan | **2.6M** | sum above, rounded |
| Ceiling | **3.4M** (1.3×) | the pack says 1.5× for an adversarial Security Review; 1.3× here because the one stage that blew slice 6 (spawn cost) is now priced from slice 6's measured per-spawn figures and re-measured at stage 1. Spend between plan and ceiling needs no question. |
| Hard cap | **4.1M** | ceiling plus one scoring rerun (about 0.8M); never raised by me |
The intent's own suggestion was 2.1M / 2.7M / 3.1M; at slice 6's measured ratios I think that is too low (its stage lines assume ~12.5k per spawn). Stage 1 may move this; any change is yours to type.

## Approvals and asks (none taken; each needs your own words in this session)
1. **Plan, intent, figures** (above).
2. **Rule 5, the judge model:** change the judge agent from `claude-haiku-5-5` to `claude-sonnet-5-5` (full ID), prompt unchanged, tools omitted, `mcp__*` deny list and match-all hook unchanged. Needed **before** the fresh session, because stage 1 measures Sonnet.
3. **Rule 6, data processor:** Anthropic, through your own session, attended only.
4. **Stage 1 and the INV-5 words (needs your explicit decision).** The intent says the INV-4/INV-5 words are approved before any code that sends data runs; the INV-5 words must state the session context the judge receives "as measured", and stage 1 is what measures it. I propose Stage 1 sends one or two public eval-set questions with their passages (no user data) plus the session context that every spawn already carries, as the only exception, and the INV words follow in stage 3b. If you would rather approve the words first, stage 3b moves ahead of stage 1 and the words say "as measured in stage 1" is dropped until measured.
5. Rule 4 (INV-4/INV-5 exact words) comes at the end of stage 3b, as one packet.

## Sessions you must start
- **Session request 1 (after ask 2 is approved and committed):** a fresh session in `.claude/worktrees/docs-answerability-2` (agent and skill files load at session start). Stage 1 runs there. I will write `SESSION_REQUEST-1.md` with the exact line. Later fresh-load sessions: before stage 5 and stage 7 only if agent/skill files changed since.

## Open items for stage 4 (found at intake, not decided)
- The first commit (5eb2a8a) passes mypy and ruff and 313 tests; 3 tests in `tests/test_judge_seen_skill.py` fail because they read slice 6's run key (`runs/docs-answerability/seen-check/key/key.toml`), which was left behind on purpose. Stage 4 rebuilds the key for the 48-question sample.

## Non-goals
Drafting, INV-3 checker, classification; any change to retrieval/ranking/corpus/embedding model; any model beyond the one judge; posting; unattended operation; any credential; the `docs-retrieval-ci` workflow.

## Constraints
Python 3.12, uv, no new runtime dependency. No metered API, no key, no `claude -p`. INV-1..5 hold; INV-4/INV-5 change only by approved words. Held-out rules: builder does not write the set; freeze, commit, run once; bars never move; fifth set not asked for or looked for. One fresh agent per stage; bounded retries. Regression: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`.
