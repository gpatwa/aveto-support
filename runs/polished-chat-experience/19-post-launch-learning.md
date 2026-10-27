# Post-Launch Review: polished-chat-experience

> Owner: Post-Launch Learning Agent (stage 14, standard). Tier: 3. Date: 2026-10-26.
> Released: image `ffc2e2e5f39a`, revision `ca-aveto-ask--0000011` (final, after the rollback rehearsal and roll forward). Source: `intent.md` Done means 1 to 9 (no PRD; the intent is the source).
> Verdicts quoted, not made here: Release Manager, GO WITH CONDITIONS (`16-release-checklist-tier3.md`). Production Verification, HEALTHY WITH WATCH ITEMS (`18-production-verification.md`).
> Signals: records in `13-live/` and `12-deploy/` read through `18-production-verification.md`; I ran nothing live (tools: Read, Write, Edit, Grep, Glob). No user feedback exists yet: the service has had only the run's 7 questions.

## Success criteria: did we hit them?

| Criterion (intent Done means) | Met? | Evidence |
|---|---|---|
| 1 Starts from `main`, pack v29 | yes | QA row 1: merge-base 32e54a6, packVersion 29, charter-check complete |
| 2 Bars fixed, not moved: timings as measured; axe zero serious; 375 px and keyboard; no open P0/P1; answering byte-identical | partial | Byte-identical, no P0/P1: yes (39-case golden re-derived, 731 passed). Timings measured live: warm median 1.36 s (README, script) vs 1.35 s from rounded values, cold 25.8 s, one sample each. Axe, 375 px, keyboard: local, stand-in judge; one clause (activate a source link by keyboard) was a precondition P3, not seen executed in the records I read |
| 3 Nothing about answering moves | yes | `git diff` of `aveto_support prompts .claude .agentic` empty; `pipeline.py` hunk add-only; live passages byte-equal on 5 of 5 answered (`ask-result.json`) |
| 4 Embedding: option (a), header unchanged | yes | `frame-ancestors 'none'` on every route; live headers true on revision 0000011 only (W1) |
| 5 Four tests fail first | yes | QA section 6: 4 of 4 fail on base and under mutation; 57 of 62 new items fail first, 5 are guards |
| 6 Code review, Security standard, Release Gate tier 3, Codex review | partial | Review 2 rounds, 0 open; Security PASS WITH CONDITIONS; Gate GO WITH CONDITIONS. Codex trial review is the owner's, not done |
| 7 Deploy plus rollback gate | yes | Rollback 65.2 s and roll forward 64.5 s (limit 600 s), `rehearsal-timing.json`; revisions 0000010 and 0000011 Healthy |
| 8 The build is shown (links on the scorecard) | partial | D13: Charter and run record linked; PR, end review, event-log summary, cost/time and owner-decisions not shipped. Links point at a commit that was local until the push (C8.2); not confirmed live here |
| 9 Docs state only recorded figures | partial | Stage 10 done; the README row for `check-new.json` is wrong (W1, correction is the Orchestrator's); 731 vs 730 tests resolved by the Gate |

## What worked

- Scope review read the safety text against the intent before any design (S1) and the Charter turned that into a decision, not a surprise at the gate.
- The frozen golden was written at a tree equal to base, then re-derived independently by QA from `git archive main`: byte-identical, sha256 `56e4b77b...e281c`. The strongest piece of evidence in the run.
- Fail-first plus mutation: each of the four intent tests was shown to fail on base and under 2 or 3 mutations, so none is vacuous.
- A pre-registered live sheet (tech spec 12.4 to 12.8) with pass rules fixed before the deploy; Production Verification could judge the records without discretion.
- Rollback rehearsal made a gate: measured 65 s against a 600 s limit, and the previous image restored with env identical (`after-2.txt`).
- 7 live questions cost $0.059978 (about $0.0086 each), under the day's cap of $0.3226.

## Which gates caught what (gateCatches)

| Gate | Catch | Disposition |
|---|---|---|
| Scope review (1) | S1: refusal card "nearest passages" contradicts INV-4(b) | D1: Option A, no passages; Option B left to the owner |
| Scope review (1) | Oversize (18 to 22 files); unconfirmed "about 26 seconds" (record says 30.8 s); baseline axe `aria-prohibited-attr` | D4 checkpoint; D5 not repeated; bar C1.4.3 binds |
| Code review (6) | F2 Important: `warm()` cached a failed warm-up for the process life | fixed `f5c139c`, re-reviewed |
| QA (7) | Q1: script dropped the client-side empty/over-500 guard, so the "Nothing was sent." card became untrue with script on | fixed `6c32de1`, Security confirmed |
| QA (7) | Q2: "It can take up to a minute" had no record; Q3: "sent one after another" unconfirmed | reworded or labelled; Q5 (suggestion labels) open until live |
| Security (9) | S1: result-store bound in code-review F1 does not hold for zero-spend `JUDGE_ERROR` (same on `main`) | to END_REVIEW, no fix |
| Security (9) | S2: counts unauthenticated, inflatable (70 posts, 60 counted) | scorecard wording, no fix |
| Release Gate (11) | Unrun `live.py` ("WRITTEN, NOT RUN"), uncommitted file from another slice, unsaved diff outputs | preconditions P1 to P5 before the build |
| Production verification (13) | W1 overwritten `check-new.json`; W2 empty log search, no time or command; W3 cold precondition only in README; W4 stray lines, median 1.36 vs 1.35, no ruling for what-ifs 2 and 3; W5 TLS wrapper | Orchestrator wrote corrections into `13-live/README.md` |

## Surprises

| Surprise | Signal | Severity |
|---|---|---|
| The tech spec spent 352k peak context against an estimate of 90k (3.9x) and set the overrun for the rest | per-spawn peak context: tech spec 352k, backend 220k vs 110k, frontend 150k vs 140k; notices in DECISIONS.md (notice 1 at 547k) | high |
| Total about 1,510k against plan 1,000k, ceiling 1,300k, hard cap 2,000k; the ceiling was passed after stage 10 | Budget notice 5; STATE still prints `Spent: 1,350k` (stale, Budget lines not mine to change) | high |
| The intent itself conflicted with a safety invariant | `01-scope.md` S1; D1 | medium |
| Evidence records were overwritten by a re-run into the same file, so the first revision's check exists only as the Orchestrator's statement | W1; `13-live/README.md` correction note | medium |
| A claimed README figure and its record disagreed (median 1.36 s vs 1.35 s; "26 s" vs 30.8 s) | W4b; D5 | low |
| Cold start 25.8 s, below the earlier 30.8 s, but after about 7 minutes idle, not over an hour | `cold.json`; W3 | low (one sample, different condition) |
| Python could not verify the platform TLS chain; run needed a scratch wrapper | `13-live/README.md`; W5 (wrapper unseen by Verification) | low |

## What we'd do differently

- Cap the tech spec: it is a document, yet it cost four times its estimate. Give the Architect a section-by-section budget and a read-list, or split it (contract vs deploy sheet) before it starts.
- Write every live output to a new, timestamped file name; never reuse a name. W1 would not exist.
- Record the literal command, start time and exit code beside each empty output (W2), and the replica count inside `cold.json` (W3).
- Dry-run `live.py` before the Release Gate, not as a precondition at the gate.
- Run the byte-equality golden, fail-first and mutation steps at stage 4, not only at QA: they were cheap to read and caught nothing late.

## Carry-forward to next PRD

- Refusal card shows no passages (D1). If the owner wants them, it needs an INV-4(b) amendment, new Charter hash and approval.
- Scorecard links shipped in part (D13); the PR, end review, event-log summary, cost/time and owner-decisions links need a later change after the PR exists. Live timings reach the scorecard only by a later change (D7).
- Counts are raw and inflatable since last restart (S2); one global 60 an hour beacon budget; `/scorecard` publishes asking activity and process start (A2).
- Result store bound for zero-spend `JUDGE_ERROR` (S1, also on `main`); `/warm` has no rate limit while the search fails (A1).
- Not checked live: kill switch, touch devices, a real browser against the live URL (CSP console errors, beacon end to end, DOMParser swap), the waiting state, Q5 suggestion labels beyond the run's questions 4 and 6 (gu18, gu15 returned `no_confident_match`), Codex review.
- Runbook sections 5, 7, 8 still describe the earlier release (`15-docs-note.md`).
- Open watch items W1 to W5 and the unrecorded kill-switch test go into `END_REVIEW.md`.

## Follow-up slices to file (proposals for the owner)

- [ ] Real-browser live check: open the live URL in a browser, record console errors, beacon, swap and waiting state, keyboard activation of a source link.
- [ ] Scorecard completion: after the PR exists, add its links and live warm/cold figures with method and date; use one median method.
- [ ] Harden counts and store: store only `ANSWER`/`NO_CONFIDENT_MATCH` results or cap per client; remember a failed warm for a few seconds; per-client beacon limit.
- [ ] Owner decision slice on Option B (refusal card shows nearest passages): only if wanted; it is a safety-text change.
- [ ] Docs debt: runbook sections 5, 7, 8; README row for `check-new.json`.

## Lessons

| Lesson | Evidence | Cost | Enforce where | Pack defect? |
|---|---|---|---|---|
| Reusing an output file name destroys the earlier run's evidence | W1: `check-new.json` equals the post-forward run, 23:37:49 vs first run 23:28:26 | one revision's header/skip-link evidence lost; Orchestrator correction | proposal: `13-live` rule or a `live.py` flag that refuses to overwrite | yes, proposal |
| Estimate for a spec stage was off 3.9x and nothing stopped it | tech spec 352k vs 90k; notice 1 at 547k | about 260k over estimate, ceiling passed | proposal: a per-stage cap that stops a spawn mid-stage (`PIPELINE_SLOS.md`), not only a notice | yes, proposal |
| An intent can contradict the safety text; catch it at scope, before design | S1 found at stage 1, D1 | none beyond one decision; a late find would cost the UX and tech spec | already enforced: scope reads `SAFETY_INVARIANTS.md` | no |
| Dropping a client-side guard in a rewrite makes existing copy untrue | QA Q1, fix `6c32de1` | one fix commit, one test | proposal: UX/QA brief lists "claims the copy makes" against behaviour | maybe |
| Evidence empty output needs the command and time beside it | W2, W3 | live claims rest on README text | proposal: live-sheet template field | yes, proposal |
| STATE `Spent` was not updated past stage 10 | STATE shows 1,350k; the run total is about 1,510k | misleading budget view | Orchestrator hook already parses it; nothing changed by me | unconfirmed |

## Pipeline analytics

Not done: `runs/polished-chat-experience/trace.json` does not exist (searched that path), and I have no tool to run `node execution/analyze.mjs`. The Orchestrator must write the trace, then run the generator for `runs/ANALYTICS.md` and `dashboard.html`. Stages to expect flagged: tech spec 352k and backend 220k (over estimate); the stage 13 spawn used 42k, under its 70k.

## Hand off

Next agent: Orchestrator. Surface follow-ups and W1 to W5 in `END_REVIEW.md`. No release verdict is made here.
