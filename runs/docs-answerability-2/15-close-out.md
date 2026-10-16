# 15 - Close-out: docs-answerability-2 (Post-Launch Learning, fresh spawn, depth standard)

> Role: Post-Launch Learning Agent. No shell (Read, Write, Edit, Grep, Glob only). Edits only this file. Commits nothing, approves nothing, does not touch `STATE.md`.
> Read: `intent.md`, `STATE.md`, `STANDING_INSTRUCTIONS.md`, `trace.json`, `05-seen-check.md`, `07-gate-scoring.md`, `12-tier3-dryrun-audit.md`, `13-release-checklist-tier3.md`, `02-tech-spec.md` section 1 (R1 to R4) and section 14, `09-release-qa.md` section 5, `08-security-review.md` (findings table), `05a-smoke.md` and `07a-driver-log.md` (grep only). Not opened, by the brief: the fifth-set files, `batch-2.txt`, `q/`, `06-label-review.md`, any `diffs.md`, `RELEASE_APPROVAL_PACKET.md`. I relied on `13` for the content of `11-monitoring-plan.md` and `11b-vendor-risk.md` (not re-read).
> "Released" here means: not released. The slice is a branch candidate (`landed: false` in `trace.json`). This review covers what the run measured, not production use, because there is none. There are no production signals to cite; every figure below is from a run record.

## 1. Outcome

### 1.1 What was built

The same judge step as slice 6, on a Sonnet-class judge, with the method fixed before anything was scored. An operator, in their own Claude Code session, runs `/aveto-judge`. The program builds a payload (the question plus the passages `retrieve` would show), a forked judge subagent (`claude-sonnet-5-5`, no tools, deny list ending in `mcp__*` plus the seven harness tools under D1, match-all deny hook) returns one verdict line, and `judge-apply` prints either `retrieve`'s output plus a signal line or exactly two lines (`no confident match` and the signal line). The program stays offline (a test asserts it; the tier 3 dry run re-ran the commands under an OS-level network deny, `12` part (a) A11). Eval-only pieces: `tools/judge_run.py` (record, diagnostics, transcript audit), `eval --verdicts`, a sample derivation, and the eval skill `/aveto-judge-seen`. INV-4 and INV-5 were rewritten in the owner's typed words (records 5, 8).

### 1.2 What was measured (figures exactly as recorded)

| Measure | Stage 5, seen-set sample (`05-seen-check.md`) | Stage 7, fifth set, scored once (`07-gate-scoring.md`) |
|---|---|---|
| Record valid | 48 spawns, 0 offered tools, 0 `tool_use`, model `claude-sonnet-5-5` | same: 48 spawns, 0, 0, no anomaly |
| Bar 1 (abstain on unanswerable) | **20/20**, registered at least 16: MET | **24/24**, registered at least 20: MET |
| Bar 2 (answerable, right file in top 5, not abstained) | **24/28**, registered at least 23: MET | **16/19 = 84.2%**, registered 80%: MET |
| Margin on Bar 2 | one question (22 would fail) | one question (15 would fail: 15*5=75 < 76) |
| Judge errors | **0** | **0** |
| Never abstain | not printed | Bar 1 0/24, Bar 2 19/19 |
| Best-score rule (`top1 < 0.67`) | Bar 1 13/20, Bar 2 17/28: **NOT MET** | Bar 1 10/24, Bar 2 13/19: **NOT MET** |
| Over-abstention | 4/28 | 3/19 (g09, g10, g24) |
| ANSWERABLE when right file not in top 5 | 0/0 | 1/5 (g19) |
| Hard negatives abstained (diagnostic) | n/a | 18/18 |
| End to end (right file shown after judging; diagnostic) | n/a | **16/24** |
| Retrieval gate on the fifth set | answerable 28/28 (sample), exit 0 | **19/24 = 79.2%, required 80%, exit 1.** Misses g05, g06, g18, g19, g22. Not a registered bar. R-A not accepted by the owner (record 9) |
| Usage (transcript peak-sum) | 378,696 (in-equivalent 439,564); smoke r049 adds 7,784 | 410,748 (in-equivalent 479,870) |

Reading it straight: the judge did what it was built for on refusals (24 of 24 and 20 of 20, including 18 of 18 hard negatives, 0 judge errors in 96 audited spawns). It beat the best-score rule on both bars at both stages. It over-abstains on a few answerable questions (4/28, 3/19), and Bar 2 is met by one question at both stages. Five answerable questions on the fifth set are lost before the judge sees them (retrieval), three more to over-abstention, so 16 of 24 end with the right file shown. By the intent's own standard (abstaining is never worse than showing a wrong file) that is lost coverage, not a wrong claim.

### 1.3 Verdict and what is not validated

- **Tier 3 verdict (`13-release-checklist-tier3.md`): GO WITH CONDITIONS. An internally releasable branch candidate, not announced, not cleared to land.** Six tier 3 items are NOT MET (release-action approval not requested, change request PENDING, DPA UNKNOWN, rollback never rehearsed, monitoring thresholds not adopted by the owner, no final-tree regression on the merge candidate). Dry run on a fixture MET (11 of 11); audit coverage MET WITH GAPS (G1 to G9); monitoring plan as a document MET WITH GAPS. Record 9: "Do not merge or push."
- **Not validated:**
  - **The operator path (`/aveto-judge`).** There the main session retypes the payload into the judge prompt (`02-tech-spec.md` 14.1). Stages 5 and 7 measured the eval path only (the harness injects the payload). The bars describe the eval path; any figure quoted from real use must say so. No accuracy on real operator questions is observable (`11-monitoring-plan.md`, via `13`).
  - **Open-ended questions on non-public text.** Everything sent so far was public documentation passages plus eval questions. The vendor risk file (`11b`) rates residual risk medium-unknown for such use until the DPA, retention and training fields are stated.
  - **Generalisation.** One set of 24 and one half-sample of 28, each scored once. The fifth set's sources overlap earlier sets' (21 of 24 answerable questions cite a file an earlier set cites, D4), which may flatter Bar 2.
  - **The load path of the stage 7 judge.** The driver session started in the main checkout and was moved to the worktree before any spawn. The audit proves model, offered tools, `tool_use`, base-dir line and payload attribution matched stage 5 on all 48 rows; no audited field records how the files loaded (`07-gate-scoring.md`).
  - **The hook.** It never fired (0 tools offered on all 96 spawns), so whether Claude Code runs it is untested.

### 1.4 Success criteria (intent "Done means"), rated

| Criterion | Rating | Evidence |
|---|---|---|
| Starts from `main`; retrieval unchanged | Met, one part unverified | `09-release-qa.md`; "pack v18 or later" was checked only as "started from main" (section 5 item 10) |
| Program stays offline, tested | Met | offline tests; `12` A11 under network deny with control |
| Stage 1 measures before building | Met | `01-measurement.md`; STATE: 2 spawns, 0 tool calls |
| Judge agent pinned, deny list, hook unchanged | Met, with D1 (record 7) adding seven tools | `09-release-qa.md`; `13` section 2 |
| What the judge sees reported, stated in INV-5 | Met with a stated limit | INV-5 list "as measured, not complete" (about 2.7k of 14.2k tokens not itemised, via `12` B1 row 5) |
| INV-4/INV-5 exact words approved before data-sending code | Met | records 5, 6, 8 |
| Method registered up front | Met | `02-tech-spec.md` R1 to R4; see 2.2 |
| Seen-set integration check | Met | 20/20, 24/28 |
| Freeze, then fifth set; labels reviewed; scored once | Met | freeze `bca0e40`, diff empty (Security, QA); label review changed data first (section 2.2) |
| Two bars never moved | Met | 24/24; 16/19 |
| Reported in the same run | Met | table 1.2 |
| Security at adversarial depth | Met | 0 blocking; S5, S6 required-fix, S1 to S4, S7, S8 advisory |
| Release Gate, tier 2 | Superseded: owner ruled tier 3 | record 9; GO WITH CONDITIONS, not landable |
| README and status state only the recorded figure, after the verdict | Met on figures (by `13` section 7 C6); tier and S6 lines were stale then, a later commit (`cfa3163`) says they now carry the tier 3 verdict (not re-read by me) | |
| Everything earlier slices guaranteed still holds | Met with one disclosed failure | 375 passed, 12 deselected; `-m model` 8 passed, 1 failed (`test_sample_derivation_reproducible`) |

## 2. What the method fixes bought, and what the sample limits

### 2.1 Against slice 6 (the intent's comparison)

- **Slice 6 (Haiku 5.5, from the intent; its records are not in this tree):** Bar 1 20/20, Bar 2 44/56 (78.6%) against a threshold of 45, 5/5 hard negatives, 1 judge error. Pilots: Haiku 47/56, Sonnet 51/56, Opus 49/56.
- **Here (Sonnet 5.5):** Bar 1 20/20 and Bar 2 24/28 (85.7%) on a 48-spawn sample of the same seen sets, then 24/24 and 16/19 on the fifth set. Judge errors 0 of 96 spawns, against 1 in slice 6.
- **What can be said:** the direction the pilots predicted held. Bar 1 was never the problem for either model; the Haiku shortfall was over-abstention on answerable questions, and Sonnet's over-abstention is lower in rate on the sample (4/28 = 14.3%, against Haiku's 12 of 56 Bar 2 failures = 21.4%, which is 56 minus 44; the intent says 11 were over-abstentions and one a format error).
- **What cannot be said:** this is not a paired comparison. The sample is positions 1, 3, ..., 55 of the same 56 answerable questions (R4), Haiku was scored on all 56 at 93 spawns, and slice 6's per-question results are not here. The two Bar 2 figures have different denominators (28 against 56) and different thresholds (23 against 45). A difference of one question flips Bar 2 at both stages here. The data do not show that Sonnet is reliably above the 80% line, only that it was above it on these two scorings.

### 2.2 The method fixes, and "zero re-registrations after a result", verified

Registered up front in `02-tech-spec.md` section 1: payload layout (R1: harness prefix line, then payload; 137 characters in this worktree, checked by form on every spawn), verdict grammar (R2: optional colon, last non-empty line, earlier lines never stored), thresholds (R3), the sample rule (R4), judge-error counting (R5: a failure on both bars, reported as its own number). The four slice 6 failure classes did not recur: payload retyping (the harness injects it; every transcript matched a key payload by hash), tool count (0 offered on 96 of 96), grammar misses (0 judge errors), first-request size (about 7.9k and 8.6k mean peak per spawn from the usage lines, against 14.2k and 14.3k at stage 1, which ran before D1 was applied; the comparison is indicative only).

Verified against the records:

- **No re-registration after any scored result.** `05-seen-check.md`: "No retune, re-derivation, rescore or re-registration was done." `07-gate-scoring.md`: "No retune, rescore, re-derivation or rerun." The freeze record names `ef9ad1e` (record 8) as the last method-file change, committed before r001 ran, and Security found the diff empty since `bca0e40`. No rerun allowance (A3) was used.
- **Method changes did happen before the first scored spawn, and they should be named, not hidden.** D1 (record 7, seven harness tools added to the deny list) and the INV-5 environment-list edit (record 8) both came after stage 1 and the spec. STATE says the smoke criteria were met "after APPROVAL_RECORD-8". The smoke row r049 was never scored. Both are owner-approved in typed words. They are not re-registrations of a result, but they were not in the original registered list either; the spec (section 14.1) priced leaving D1 out at about 0.45M over the stage 5 and 7 lines.
- **The fifth set was edited before scoring, by rule.** Label review (held-out rule: labels first) found gu09 AMBIGUOUS (replaced by reserve gr02 on the owner's typed word, D5b) and added sources to 10 answerable questions (D5, additions only, nothing dropped). Widening sources can only add retrieval hits. That is data, applied before the single scoring, and disclosed, but it bears on the 19/24 retrieval figure and on Bar 2's denominator of 19, and the reader should know it.
- **After the freeze one test broke by construction:** `test_sample_derivation_reproducible` compares the whole key file, and the gate rows were appended after the freeze. The test is frozen; it fails (`-m model` 8 passed, 1 failed). A later slice must change it to compare the sample prefix.

### 2.3 What the sample scale limits

- One scoring per set, by rule, so there is no variance estimate. Stage 5: 28 answerable (the registered 23-of-28 line left a margin of one). Stage 7: 19 answerable with a hit. With 19, each question is 5.3 percentage points; 84.2% against 80% is one question.
- The monitoring plan's own arithmetic (checked by the Release Manager, `13` section 2) shows how little a small tally proves: 4 of 10 at a true rate of 15% is about 5%; 5 of 10 about 1%.
- The sample is a subset of seen sets, so it tests the model on questions the method designers have looked at; the fifth set is the only held-out evidence, and it overlaps earlier sets' sources (D4).

## 3. Cost

Unit: **peak context summed per spawn** (the budget unit; self-reported telemetry, not billing). Plan 2,600k, ceiling 3,400k, no hard cap (record 1).

### 3.1 Total, computed from `trace.json`

Summing the 18 stage entries in `trace.json` (28,517 + 107,000 + 178,000 + 165,000 + 154,000 + 386,000 + 42,000 + 226,000 + 411,000 + 47,000 + 157,000 + 83,000 + 104,000 + 65,000 + 52,000 + 58,000 + 83,000 + 121,000) gives **2,467,517, about 2,468k**. `STATE.md` records 2469k; the 1k gap is rounding of stage 1 (28.5k or 29k). That is **95% of the plan and 73% of the ceiling**, and it stops at the tier 3 QA spawn.

**Not yet in `trace.json` or STATE:** the tier 3 Release Manager verdict spawn (`13`, est. 60k), the README and status update after it (est. 30k, commit `cfa3163`), and this close-out (est. 55k). The Orchestrator projected 2,614k including a final-tree run; on my sum it is 2,468k + 60k + 30k + 55k = about 2,613k, **over the 2,600k plan by about 13k and under the 3,400k ceiling**. This is a projection from estimates, not a measurement. The Orchestrator records the actuals; I do not invent them.

The STATE trace "Total" row shows **139 tool calls**, which equals Scope plus Architecture pass 1 only (61 + 78). Summing the subagent entries in `trace.json` gives **666 tool calls** (judge spawns 0). Flagged for the Orchestrator to correct.

### 3.2 By stage against the estimate (from STATE and `09-release-qa.md` section 5)

| Stage | Estimate | Actual (peak) | Over |
|---|---|---|---|
| Scope | 60k | 107k | +47k (78%) |
| Architecture pass 1 | 130k | 178k | +48k (37%) |
| Architecture pass 2 | 90k | 165k | +75k (83%) |
| Implementation | 130k | 154k | +24k (18%) |
| Stage 5 judge spawns (49) | 350k | 386k | +36k (10%) |
| Label review | 110k | 226k | +116k (105%) |
| Stage 7 judge spawns (48) | 400k | 411k | +11k (3%) |
| Security (adversarial) | 125k | 157k | +32k (26%) |
| Release Gate QA run | 60k | 83k | +23k (38%) |
| Release Gate verdict (tier 2) | 50k | 104k | +54k (108%) |
| Docs (Tech Writer) | 30k | 65k | +35k (117%) |
| Tier 3: monitoring plan (SRE) | 40k | 58k | +18k (45%) |
| Tier 3: vendor risk and change request | 50k | 83k | +33k (66%) |
| Tier 3: fixture dry run and audit | 60k | 121k | +61k (102%) |
| No estimate recorded: stage 1 (28.5k), stage 5 scoring (42k), stage 7 scoring (47k), Architect docs finish (52k) | | 169.5k | |

For the 14 stages with an estimate, the estimates sum to 1,685k and the actuals to 2,298k, **+613k (36%)**. The two judge-spawn drivers, the only stages built on a measured per-spawn cost, came in within 10%; every review or writing stage ran over, and four ran at about twice the estimate or more (label review, tier 2 Release Manager, Docs, tier 3 QA at 2.0x to 2.2x). The tier 3 additions (SRE, Compliance, QA) cost 262k against 150k estimated, before the Release Manager verdict.

Caveats: (1) peak context understates the work. Label review processed 13.31M tokens for a 226k peak; Architecture pass 1 4.90M for 178k (STATE trace). The unit is the pack's, but it is not billing. (2) The forked judge spawns (96) and the owner-started session spawns are not listed by `usage.mjs`; their figures are transcript peak-sums (7.9k and 8.6k per spawn on average), so those rows are a different kind of number from the subagent rows. (3) The Architect's docs-finish row (52k) is "peak across passes" after a session-limit interruption.

### 3.3 Pipeline analytics

I cannot run `node <playbook>/execution/analyze.mjs .` (no shell), so `runs/ANALYTICS.md` and `runs/dashboard.html` are **not regenerated by this stage**. The Orchestrator, or any session with a shell, runs it after recording the Release Manager and close-out spawns. `trace.json` exists and is complete through the tier 3 QA stage (18 stages, nine approvals, five gate catches, `leastPrivilegeEnforced: true` with a note); it lacks the three entries named above. I have not read `PIPELINE_SLOS.md`, so I do not state which stages the generator will flag. By my own estimate ratios (not the generator's density rule), the candidates are the four at about 2x or more listed above.

## 4. Surprises, and what we would do differently

Each has a record behind it; none is a feeling.

- **Zero judge errors in 96 spawns.** The spec (14.1) kept the strict `CONTROL` and `MULTI_TOKEN` rules and warned they might cost Sonnet format failures. `05-seen-check.md` and `07-gate-scoring.md`: judge errors 0 at both stages.
- **Retrieval, not the judge, caps the result.** Five answerable questions on the fifth set (g05, g06, g18, g19, g22) never reach the judge with the right file in the top 5; the retrieval gate exits 1 at 79.2%, and the dev set scores the same 19/24 (LOCAL_COMMANDS, via `07`). The judge cannot repair that; end to end is 16/24.
- **The best-score rule failed both bars at both stages** (13/20 and 17/28; 10/24 and 13/19), so the judge earns its cost against the cheap baseline.
- **The judge said ANSWERABLE on 1 of 5 questions whose right file was not shown** (g19), which is the one place a judge "yes" is not backed by the key. One case; no rate can be inferred.
- **Review and writing stages cost far more than estimated** (section 3.2), while the measured spawn stages did not.
- **The costly late discovery was governance, not accuracy.** The DPA is UNKNOWN, the release action was never asked, and rollback was never rehearsed, all found at tier 3 after the evidence work was done.

Do differently next time: rule the tier at intake; review any skill with a shell line before its first use; give review stages estimates from processed tokens as well as peak; put the DPA line into the rule 6 question.

## 5. Lessons

A lesson without an evidence line is dropped. "Pack defect" marks items for the support session to curate into the playbook's `docs/LESSONS.md`; I mark candidates, I do not assert the cause is in the pack beyond what the evidence shows.

| Lesson | Evidence | Cost | Enforce at |
|---|---|---|---|
| Review and writing stages overrun estimates by a large factor; measured spawn stages do not. Estimate review stages from processed tokens, not a guess. | Section 3.2: 14 estimated stages, +613k (36%); label review 226k peak for 13.31M processed (STATE trace) | 613k over estimates; plan exceeded by a projected 13k | Pack: estimating guidance in `RUN_ECONOMICS.md`. **Pack defect candidate** |
| Agent and skill files load at session start; an owner-started session must be started in the worktree, and the load path is not audited. | `05a-smoke.md`: "The earlier terminal attempt spawned nothing" (intent: the terminal offers only an API login); `07a-driver-log.md` and `09-release-qa.md` section 5 item 2: stage 7 driver began in the main checkout, was moved before any spawn; `07-gate-scoring.md`: no audited field records the load | One lost attempt; an unprovable load path at stage 7, carried as a disclosure | Session request template: a first-line check; `tools/judge_run` audit: a load-path field (project pack). Not yet enforced |
| A permission rule or skill written to make a helper run unprompted is a security surface; review it before first use, and keep the rule to the exact command. | Freeze record: `.claude/settings.local.json` rule `Bash(uv run -q --project * python * seen_payload.py *)` written by the stage 5 session; `08-security-review.md` S5 (`'$ARGUMENTS'` breakout) and S6 (rule too wide), both required-fix; first reviewed at stage 8, after 96 spawns | Two required-fix findings; `/aveto-judge-seen` unusable until fixed (T8); S6 disposition recorded only by the support session (T9a) | Project pack: Security looks at any `!` shell line and any helper permission rule before the first spawn that uses it |
| Do not commit evidence scripts into a linted tree. | `09-release-qa.md`: `ruff check` exit 1, 23 errors, all in `security-probes/*.py` committed in `69fd907`; D6 (`# ruff: noqa` on line 1) | One NO-GO as written, one fix commit; STATE failure budget shows 0 retries while STANDING says "retry 1" | Orchestrator brief (commit hygiene), or a ruff exclude for `runs/` in a later slice (`pyproject.toml` is frozen here). **Pack defect candidate** |
| Rule the tier at intake when a safety-control rewrite and a third-party data flow are both in scope. | `01-scope.md` section 3, `02-tech-spec.md` 14.1 and `09-release-qa.md` item 9 all raised it; ruled only on 2026-10-16 (record 9); tier 3 then added SRE, Compliance and QA spawns (262k) plus a second Release Manager verdict, and a re-edit of README and status | 262k for the three tier 3 spawns, the tier 2 verdict (104k) largely redone, the Release Manager tier 3 verdict (unrecorded, est. 60k) | Pack: intake step and intent template ask for the tier; `RELEASE_GATES.md` tier text. **Pack defect candidate** (scope allowed deferral to the gate) |
| Label review before scoring earns its cost, and the set request must not impose a constraint that cannot hold. | `trace.json` gateCatches: gu09 AMBIGUOUS replaced by gr02 (D5b); 13 source additions on 10 answerable questions (D5); Request 1 forbade any source reuse, Reply 2 showed it cannot hold (96 of 123 corpus files cited; 21 of 24 questions overlap), D4 allowed and disclosed it | 226k (2.05x estimate); a disclosed optimism risk on Bar 2 | Project pack held-out rule: check source overlap when the request is written |
| A DPA status must be surfaced when the rule 6 question is asked, not discovered at the release gate. | `13` section 3.1: records 3 and 6 stand, "given without a stated DPA position, and that has not been repaired"; `11b` DPA and eight further fields UNKNOWN; gate NOT MET | A tier 3 blocker no agent can clear; the owner's time | `HUMAN_APPROVAL_RULES.md` rule 6 ask template and the Architect's `02c` question. **Pack defect candidate** |
| Standing instructions (SI-1 to SI-3) kept the run moving without silent decisions, but two SI-1 defaults shaped the held-out evidence. | `STANDING_INSTRUCTIONS.md` digest: D1 to D6, A1 to A13, D4 (reuse) and D5 (source additions); SI-3 stop list; no stop was triggered by a spawn anomaly | None measured; risk is that a quoted figure omits D4 and D5 | Digest template: a column "affects held-out evidence", so reports quote it. Not yet enforced |
| The write-scope guard blocked the Tech Writer from Architect-owned files, so docs were partial and needed a resumed Architect after a session-limit interruption. | STATE Docs rows: Tech Writer 65k (two files refused), Architect finish 52k | 52k plus a resume | Stage plan: schedule the file owner for owned docs. **Pack defect candidate** (the Tech Writer brief assumes it can edit them) |
| The Release Manager has no shell, so the final-tree regression stayed open at both verdicts. | `09-release-checklist.md` and `13` section 2: ruff, mypy and pytest "not run by me"; T6 | T6 open; two verdicts rest on others' reports | Release gate ordering: a QA run on the final commit after docs, before the verdict |
| Create `trace.json` at intake and record identity and time in approval records. | `13` section 3.1: records 1 to 8 say "owner" only, no time of day, and at that time no `trace.json` (it now exists with `operator: Gopal Patwa`) | T11 time of day still open | `APPROVAL_PROTOCOL.md` record template; Orchestrator intake. **Pack defect candidate** |

## 6. Carry-forward (the records' items, with owners; nothing new proposed)

Open conditions from `13` section 8 (each closes only by an artefact):

| # | Item | Owner | Status I can see |
|---|---|---|---|
| T1 | Ask for and obtain approval of the release action (merge and push are two yeses; name the merge method) | Orchestrator raises on the owner's request; owner decides | Not requested |
| T2 | Change request decision recorded (`11c` PENDING) | Owner | Open |
| T3 | State the vendor-risk position (DPA, plan, retention, training use, terms, subprocessors, residency), adopt or decline "public-docs questions only until stated", RoPA line, or waive in the owner's words | Owner | Open (all UNKNOWN) |
| T4 | Rehearse rollback on a scratch branch, or accept the plan as written | A session with a shell; or owner | Not rehearsed |
| T5 | Adopt monitoring thresholds, cadence, operator, the standing mitigation; copy plan sections 2 and 5 to `docs/runbooks/` | Owner; Tech Writer | Open |
| T6 | Final-tree ruff, mypy, pytest on the merge candidate (expect clean, 375 passed, 12 deselected), plus empty diff of method files against `bca0e40` | Orchestrator | Open (close-out run is the Orchestrator's) |
| T7 | R-A: accept the retrieval gate exit 1 (19/24 = 79.2%) in words, or declare it relevant | Owner | Not accepted |
| T8 | S5: fix, retire or accept in words before `/aveto-judge-seen` reaches `main` | Owner | Held, not fixed |
| T9 | (a) Owner states the S6 disposition in the driving session (file absent here; support Reply 4 records the deletion); (b) README, status, `ARCHITECTURE.md` stop saying "tier 2 / tier open"; (c) STATE corrections | (a) Owner; (b), (c) Orchestrator | (b) a later commit says done (`cfa3163`), not re-read by me; (c) see section 8 |
| T10 | Rule which governance gates apply (Data Governance, AI Governance, threat model in template form) | Owner; named roles if enabled | Open |
| T11 | Approval trail: `trace.json` with `operator` now exists; time of day on the release approval still missing | Orchestrator; owner | Half done |

Also carried:
- **Advisories S1 to S4, S7, S8** (`08-security-review.md`): S1 judged ANSWERABLE echoes the normalised question; S2 a symlink `reply.txt` survives cleanup; S3 passage text can imitate payload structure and carry Cc/Cf characters; S4 any model can spawn the judge with a `model` override; S7 a crafted newline question can print a bare `no confident match`; S8 a docstring cites `APPROVAL_RECORD-10`, absent from this branch. Owner: a later slice (none filed).
- **Audit gaps G1 to G9** (`12` B5): G1 no program-side record of the send on the operator path (by design); G2 the printed result omits model, input hash, time and operator; G3 a refused tool call leaves only a hook message; G4 symlink cleanup skip (S2); **G5 a void `record` into a directory holding a valid run leaves the earlier `verdicts.toml`, `diffs.md`, `audit.json` in place** (confirmed by a probe, no test; the guard is described in `12`); G6 an `ApplyError` in `record` leaves no `audit.md`; G7 `diffs.md` stores uncapped replies and is committed (nobody has read it; read before any publication); G8 a non-domain exception ends in a traceback, exit 1; G9 context drift is invisible on the operator path. Owner: the QA or Engineer role of a later slice.
- **The failing model-marked test** `test_sample_derivation_reproducible`: compare the sample prefix, not the whole key file. It is frozen here; a later slice changes it.
- **The runbook copy** in `docs/runbooks/` (Tech Writer) and **the rollback rehearsal** (T4, a session with a shell).
- **The unmeasured operator path** (`/aveto-judge` retypes the payload; `02-tech-spec.md` 14.1). Owner and Security decide whether to measure it before any claim from real use.
- **QA's proposal** that a later slice either gates `ruff` over `runs/` or keeps probe scripts untracked.
- **R-B to R-F** stated, not accepted (Bar 2 margins; advisories; the failing test; hook never fired and the context list incomplete; self-reported telemetry and the overruns in section 3).
- **Hold:** no use of `/aveto-judge-seen`; no reuse of reserves (gr02 is now gu09); no rescore; any change to a method file voids the freeze.

## 7. Follow-up slices

None filed. No artefact asks for one. Candidates, for the owner only, each taken from a record:

1. Close G5 with a valid-then-void `record` test and fix (`12`).
2. Change `test_sample_derivation_reproducible` to compare the sample prefix (`09-release-qa.md`).
3. Fix, retire or accept S5, and decide S1 to S4, S7, S8 (`08`).
4. Measure the operator path before any claim from real use (`02-tech-spec.md` 14.1; `13` section 9).
5. Retrieval misses on the fifth set (g05, g06, g18, g19, g22): the record says the judge cannot repair them; whether to change retrieval is the owner's call and is outside this slice's scope (the intent excludes retrieval changes).

## 8. For the Orchestrator

- Record the actuals of the tier 3 Release Manager verdict, the docs update and this close-out in `STATE.md` and `trace.json`; do not use my estimates.
- `STATE.md` as I read it: "Current stage" still reads "Release Gate re-run at tier 3" and "Next action" still describes the tier 2 Release Gate; the trace "Total" tool calls reads 139 where the subagent entries sum to 666; the failure budget table shows 0 retries while STANDING calls D6 "retry 1". Yours to correct.
- Regenerate `runs/ANALYTICS.md` and `runs/dashboard.html` with `node /Users/gopalpatwa/opt/agentic-sdlc-playbook/execution/analyze.mjs .` after the actuals are in. I could not run it.
- Raise T1 only when the owner asks; nothing here is an approval, a push or a merge.

