# Close-out: docs-answerability

> Post-Launch Learning. Tier 2, adversarial depth for Security only (never ran). Sources: `STATE.md` (Updates 1-4), `04-seen-set-check.md`, `03b-refusal-probe-2.md`, `03d`/`03e`/`03f` records, `APPROVAL_RECORD-1..10`, `05-lean-measurement.md`, `SUPPORT_REPLIES.md`, `intents/docs-answerability.md`. No production signals exist (nothing deployed), so every finding cites an artefact; no metric is invented. Owner decision (typed): accept the seen-set result as registered, no retuning, no rerun, close as not releasable, do not start Freeze, Security, Release Gate, label review or scoring, do not touch the fifth set.

## 1. Outcome

**NOT RELEASABLE. Do not merge this branch as a release.**

The pre-registered seen-set check (spec 5.4) failed on one bar, by one question:

| Bar | Result | Threshold | Verdict |
|---|---|---|---|
| Pooled Bar 1 (unanswerable questions abstained) | 20/20 | >= 16/20 | MET |
| Pooled Bar 2 (answerable, right file in top 5, judged ANSWERABLE) | **44/56** | >= 45/56 | **NOT MET** |

Denominators are exactly 20 and 56, so the check is valid (04-seen-set-check section 1). JUDGE_ERROR counts as a failure on both bars; there is one under the final grammar (r093). Per-set Bar 2: retrieval 13/19, heldout 11/12, heldout-3 9/11, heldout-4 11/14. Verdict mix over 93: 52 ANSWERABLE, 40 NOT_ANSWERABLE, 1 JUDGE_ERROR. Eleven of the twelve Bar 2 misses are NOT_ANSWERABLE verdicts on answerable questions.

Per spec 5.4 the run stopped before the fifth set. It was never read, requested or looked for. The intent's two-bar gate on the fifth set was never evaluated, so the slice's headline goal (the judge decides, on a held-out set, whether passages answer the question) is **not demonstrated**.

## 2. What was built and what is on this branch

Branch `claude/aveto-docs-answerability-85eb6d` (worktree off main at 56b4723; pack v17 moved to v18 by cherry-pick of main 77e6462). Working tree is uncommitted in part (see git status at close). Contents:

- **Judge agent** `.claude/agents/aveto-answerability-judge.md`: `model: claude-haiku-5-5` (full ID, APPROVAL_RECORD-5), `tools` omitted with a `disallowedTools` deny list that now ends in bare `mcp__*` (APPROVAL_RECORD-8), plus a hook. Prompt `prompts/answerability-judge-v1.txt`, sha256 24b244d2...f159427.
- **Skills**: `/aveto-judge` as a skill with `disable-model-invocation: true` (APPROVAL_RECORD-7); `.claude/skills/aveto-judge-seen/`, the forked driver for the seen-set check (03d).
- **Program pieces** in `aveto_support/judge.py`: `judge-input`, `judge-apply`, `parse_verdict`, and the `eval --verdicts` path. Grammar went through two re-registrations: optional colon (APPROVAL_RECORD-9, 03e) and last non-empty line (APPROVAL_RECORD-10, 03f).
- **Tests**: `tests/test_judge.py`, `tests/test_judge_artefacts.py`, `tests/test_judge_seen_skill.py`. Final regression at close-out (re-run by the Orchestrator): 316 passed, 11 deselected.
- **Run artefacts**: `runs/docs-answerability/` including `seen-check/` (ledger, 93 audited transcript copies, verdict TOMLs, discarded attempts) and `probe-transcripts/`.
- ADR `docs/adr/0008-operator-run-answerability-judge.md` **stays Proposed**.
- INV-4 / INV-5 words were approved (APPROVAL_RECORD-4) and, per STATE, applied verbatim (a8c9604). They describe a judge that did not pass its gate. The owner should decide whether they stay; this stage changed nothing.

## 3. What is NOT validated

- Bar 2 on any data. Seen-set result is a miss; the fifth-set result does not exist.
- The method as a clean pre-registered measurement: the grammar was tuned twice after failures seen on these same sets (disclosed below). Bars were unchanged.
- Freeze, label review, scoring: not started.
- Security (adversarial), Release Gate, Docs: never ran. No security verdict exists for the judge path, the deny list, the hook, or the new egress words.
- The live hook: the one live refusal was on the older agent definition (probe 1). After `mcp__*` was denied the 7 harness tools were offered and not exercised, so the hook was not seen to fire on the final definition (03b-refusal-probe-2).
- Operator-session behaviour (attended use, the `/aveto-judge` flow as a user would run it). Only the seen-set driver path was exercised.
- Cost figures beyond the transcript sums below.

## 4. Learnings (carry-forward as learnings only; no proposals, no fixes to the failed bar)

Format findings (judge Haiku, 93 spawns, 150-char prefix, zero tool calls):
- **Colon:** the judge wrote `Q1 NOT_ANSWERABLE:` in 20 rows of the registered run; the first grammar rejected them as JUDGE_ERROR (r001, 03e).
- **Thinking aloud:** some replies reasoned across several lines and self-corrected (r046, r051; r010, r012 observed). The line-per-verdict grammar failed on multi-line replies (03f). Five rows depend on the last-line rule.
- **Trailing note:** r093 added a "Note:" paragraph after an ANSWERABLE first line and is the one residual JUDGE_ERROR. One question decided the bar (44 vs 45); stated as fact, not as a rescoring.
- **Verdict behaviour:** the judge is conservative. All 12 bar-relevant misses are NOT_ANSWERABLE or an error; zero unanswerable questions differed. Pilots on the same 93 questions in a different configuration read 20/20 and 47/56 (04 section 6).

Driver and harness:
- **Retyping failure:** a model asked to retype each ~4-5k-token payload verbatim into the Agent call truncated r003 and voided batch 1 (STATE Update, probe-2 section). The forked-skill driver fixed it (payload byte-identical in all 93, hashes match).
- **Harness prefix:** the forked skill adds a 150-char `Base directory for this skill: <path>` line before the payload. Spec 5.2/5.4 said "verbatim" and a frozen layout; it was re-registered (APPROVAL_RECORD-9). The pilots did not record whether they had one.
- **Driver was not a fresh context** (the Orchestrator's top-level session), against spec 5.2. It should have stopped at r010 (first judge error) and did not; ledger discloses this and other deviations. Scorer noted ledger discarded-attempt counts (4 and 2) disagree with the directory (3 and 1) and its batch-complete labels disagree with the batch files.
- **`usage.mjs` does not count forked judge spawns** (also not registered scratch spawns). Spend has to be taken from transcripts.

Safety and coverage (for the owner; nothing changed here):
- **The judge can see more than the payload.** Judge spawns receive the session's CLAUDE.md, user email and git status as injected context. **INV-5 wording (approved in APPROVAL_RECORD-4) may be incomplete for this**; reporting to the owner, no edit made.
- **Hook-only coverage of the 7 harness tools** (DesignSync, ListPlugins, ListSkills, SearchPlugins, SearchSkills, SuggestPluginInstall, SuggestSkills): they cannot be denied by `disallowedTools`; only the hook covers them, and the hook is unexercised live on the final definition (section 3).
- **Cost of tool listing:** the harness listed 141 deferred tools (76k peak for one judge); `disallowedTools` accepts MCP names, exact, wildcard and server-only, and bare `mcp__*` takes the judge to 7 tools at about 11k per request (05-lean-measurement).

Process:
- **Both re-registrations came after seeing failures on these same sets** (APPROVAL_RECORD-9 and -10). APPROVAL_RECORD-10 names the fifth set as the protection; it remains unspent.
- **Spec 5.4 stop worked:** it stopped the method before the fifth set; same lesson as the previous slice.

## 5. Cost

- Plan 950k; intent figure about 700k; owner ceiling raised to 2.6M peak-sum (APPROVAL_RECORD-8, replacing 1.4M).
- Before the seen-set check: 717k (usage.mjs, the STATE Trace table). Last session: about 1.76M by transcript peak-sum (forked judge spawns, QA passes and drivers; **not in usage.mjs**). Total about **2.5M peak-sum**, about 2.6x the plan and about 3.6x the intent's figure; under the 2.6M ceiling by roughly 100k.
- The 93 judge spawns were the bulk; the estimate for the stage was 100k and was off by more than 10x at the time of the stop-and-ask (spec 5.2 was written without the harness tool list in mind).
- Stages over cap or at 2x density baseline: to come from `runs/ANALYTICS.md`, which the Orchestrator regenerates after this artefact.

## 6. Open items

- Release Gate, Security (adversarial), Docs, Freeze, Label review, Scoring: never ran, by owner decision.
- Fifth set untouched, unread, held outside this repo.
- ADR-0008 stays Proposed.
- Uncommitted work on the branch: judge/test changes, new skill, seen-check, probe-transcripts, approval records 8-10. Owner decides whether to commit as a record.
- INV-5 completeness question (section 4).
- `test_judge_artefacts.py` pins the deny list exactly (it was edited by the Orchestrator for `mcp__*`, not separately approved, per APPROVAL_RECORD-8); future deny-list changes touch it.
- Ledger vs directory count mismatches (section 4); judge-apply wrapper trimmed output.
- Whether to continue, change method, or retire the judge is the owner's decision; none is proposed here.

## 7. Follow-up slices

None filed. No follow-up was asked for.

## Lessons

| Lesson | Evidence | Cost | Enforce at |
|---|---|---|---|
| A budget estimate for per-spawn work must include the harness's per-spawn context (tool list, injected files), not just the payload | Plan estimated 100k for the seen-set stage; probe judge peaked at 76k per spawn, 93 spawns about 7M as built (STATE Open stop; 05-lean-measurement) | Stop-and-ask, ceiling raised 1.4M to 2.6M, two lean measurement spawns | Pack: Architect/Scope brief or RUN_ECONOMICS (not enforced yet) |
| `usage.mjs` must count forked skill spawns or the ledger undercounts | Last session about 1.76M by transcript not listed by usage.mjs (STATE Update 4) | Spend taken from transcripts by hand | **Pack defect** for the support session; a hook or analyzer fix |
| A "verbatim payload" contract fails if a model has to retype it; use a mechanical hand-off | r003 truncated, batch 1 voided (Update, 03d) | One rerun allowance and a new skill | Project pack: spec template for any model-in-the-loop driver |
| A frozen output grammar for an LLM judge must tolerate colons, reasoning lines and trailing notes, or be tested on the pilot before pre-registration | 20 colon rescues, 5 last-line rescues, r093 residual error decided the bar 44 vs 45 (04 section 2) | Two re-registrations, a clouded measurement | Project-pack rule: run a format probe on data not in the bar before freezing |
| Pre-registering a re-registration after seeing failures weakens the measurement; keep a never-seen set as the safeguard | APPROVAL_RECORD-9, -10; fifth set untouched | Seen-set result not clean | Already practised; keep |
| A driver for a pre-registered run should be a fresh context that stops at the first anomaly | Ledger: driver should have stopped at r010; not fresh (04 section 10) | Disclosed deviations, extra scoring work | Pack: driver protocol in spec template |
| Injected session context (CLAUDE.md, email, git status) reaches a "zero-tool" judge | Reported to this stage by the Orchestrator; not re-verified here | Possible gap in INV-5 words | Project-pack SAFETY_INVARIANTS (owner decision; nowhere yet) |


Close-out note: the Post-Launch Learning spawn used about 57k against the owner's 50k close-out cap (over by about 7k); the whole slice is at about 2.5M peak-sum, under the 2.6M ceiling.
