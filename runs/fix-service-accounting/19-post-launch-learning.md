# Post-Launch Learning: fix-service-accounting

> Post-Launch Learning Agent, 2026-10-24. Read only the run artefacts named below; no live query, no production signal beyond `18-production-verification.md`. Stage 11 `trace.json` and analytics are the Orchestrator's (not run here).

## Did the slice meet its goal? Yes, with watch items

| Criterion (intent "Done means") | Rating | Evidence |
|---|---|---|
| #6 retry never settles above the cap, test fails first | Met | T6.1 22,466,000 vs cap 13,124,000 on 87178bd; mutation caught (`13-qa-evidence.md`). Caveat CR-1: T6.1 passes on head by refusal, T6.2 proves the retry case |
| #7 503 then 400 charges the first attempt; all-never-billed charges 0 | Met | T7.1 `0 == 13124000` on base; T7.2 guards; mutations 7a, 7b caught |
| #8 price 2000/10000 with source comment | Met in code. Pricing page not checked by QA, Security or me | T8.1, T8.2; live `spend_minus_token_cost_nano: 0` (`18-...` check 8) |
| Nothing else moves | Met | byte-identical protected paths; 14th path `tests/test_service_api.py` disclosed |
| Live smoke: 5 questions, cost within 15% of $0.0078, no question text in logs, kill switch on/off | Met, one measurement missing | $0.008544 per question (inside band, 9.5% above reference); log queries clean; D1 toggle time not watcher-measured (W1) |
| Docs state recorded figures only | Pending at stage 11 | `18-...` handoff: "not deployed yet" lines still to update before the PR |

Verdict from stage 10: HEALTHY WITH WATCH ITEMS, no rollback. Revision `ca-aveto-ask--0000008`.

## What worked

- Fail-first on the base commit, then independent re-run by QA with an identical 30-id list, then mutations per fix. Every claim in the intent had a test that moved.
- Fixing the post-deploy checks and the pass rule in the spec before the deploy (what-if rule, 15% band, 8.5 triggers). Stage 10 was a read-and-compare, not a judgement call.
- Security ran all 144 two-attempt sequences through the real adapter and found a case the spec table missed (connection error then success, A1).
- The Release Manager read the unreviewed `smoke.py` before it made billed calls (P4); the smoke then ran once, 5 judged, no duplicate sends.
- Dropping the Cloud Deployment spawn (the spec 7 sheet was already literal) saved a stage without losing a gate.

## What surprised us

1. **Stage 2 spent about 2.7x its estimate** (derived about 243k vs 90k; see table). Evidence: STATE.md Notes (394k after stage 3 minus 62k stage 1 minus 89k stage 3). The spec carried the deploy sheet, smoke design, three fixes and a cost model in one spawn.
2. **The smoke script was left out of the stage 3 brief.** The Architect assigned it to stage 3 (note d), but the Backend finished without it (STATE row 3: "smoke script not written"). The follow-up spawn cost 104k, more than the 89k stage it supported, and hit a usage limit (429) midway (Interruptions row). Cause: the spec's assignment did not reach the stage 3 brief.
3. **Event-log paths were worktree-relative.** The first event-log verification needed "worktree-prefixed allowed paths" (commit 506bcd7). The check passed only after the allowed paths were re-expressed with the worktree prefix. Cause not examined further here; see Lessons.
4. **Local TLS and PYTHONPATH broke the smoke tooling.** First `watch on` failed all 213 polls on a TLS error (fix `SSL_CERT_FILE=/etc/ssl/cert.pem`); the first `ask` failed on an import until `PYTHONPATH=.` (W1, W5). Cost: D1 toggle time is only an upper bound (69 to 73 s from deploy timestamps).
5. **What-if representation noise.** The Orchestrator wrote its own ruling (`7.2-whatif-ruling.md`) for the noise; I did not re-read the what-if JSON (W6, unconfirmed by me; looked: `18-production-verification.md` only).
6. **Pause point is about 33 a day (estimate), not the intent's 41.** CR-3. Live per-question cost ($0.008544) would give about 37 on cost alone, so 33 binds.

## Estimate accuracy per stage

Tokens in thousands. Stage 1 to 3 split is derived from totals in STATE Notes (394k after stage 3), so stage 1 and 2 are inferred, not recorded; telemetry is self-reported.

| Stage | Est. | Actual | Ratio |
|---|---|---|---|
| 1 Scope | 50 | about 62 (derived) | 1.2x |
| 2 Tech spec | 90 | about 243 (derived) | 2.7x |
| 3 Fixes | 110 | 89 (+104 smoke follow-up = 193) | 0.8x (1.8x with follow-up) |
| 4 Review | 50 | not a spawn (Orchestrator session) | n/a |
| 5 QA | 70 | about 67 (565 minus 394 minus 104) | 1.0x |
| 6 Security | 70 | 127 | 1.8x |
| 7 Docs | 50 | 83 | 1.7x |
| 8 Release Gate | 80 | 119 | 1.5x |
| 9 to 11 | 160 | not in spawn spend (Orchestrator session) | n/a |
| Total through stage 8 | 570 | 894 | 1.6x |

Plan 730k, ceiling 950k; spend through stage 8 was 122% of plan, 94% of ceiling. Pattern: every review and docs stage came in 1.5x to 1.8x; only mechanical work (3, 5) held. Next plan: weight review and docs stages up by about 1.6x and spec stages for deploy-bearing slices by about 2.5x.

## Carry forward

1. **Owner decision A1** (connection error then success charged usage only; a read-phase failure can be billed). Options in `14-security-review.md`: classify by the SDK error's `__cause__`, or charge `attempts - 1` on success.
2. **Owner decision A2** (that Anthropic does not bill a 429 is unconfirmed; looked: repo records, SDK source). Live `Δspend` was 0 gap, so no billed retry occurred; it did not test the question.
3. **Rollback rehearsal (R-1/W3).** `revision activate` is unrehearsed and revision 0006 is no longer active after D2. R2 (kill switch on via D1's command) is the proven fallback. A rehearsal needs a Charter line naming it.
4. **D1 counters survive a restart** (decision D1, A4): counters reset per revision; the two deploys reset them twice. Anthropic console limit is the backstop. Backlog slice.
5. **Backlog candidates:** A3 (midnight straddle), A5/CR-4 (unclamped settle), and a recheck of the $0.0078 reference against the live $0.008544 once more traffic exists.
6. **Stage 11 chores:** update "not deployed yet" docs lines to recorded figures; PR body `Closes #6`, `Closes #7`, `Closes #8`; END_REVIEW notes the model reconciliation and `smoke.py` reviewed only by one read.
7. **Smoke tooling fix for the support session** (see Lessons 2): the watcher and `ask` must set `SSL_CERT_FILE` and `PYTHONPATH` themselves or fail with a clear message.

## Follow-up slices to file

- Rollback rehearsal of `revision activate` on a non-incident run (needs owner approval).
- Persistent counters (D1).
- Midnight straddle and settle clamp (A3, A5).
- A1 classification by `__cause__`, if the owner chooses option (a).

## Lessons

| # | Lesson | Evidence | Cost | Enforce where |
|---|---|---|---|---|
| 1 | A deliverable the spec assigns to a stage must appear in that stage's brief; check the brief against the spec's assignment list | Spec note (d) vs STATE row 3 "smoke script not written" | 104k follow-up spawn plus a 429 interruption | Orchestrator brief checklist in the pack (not enforced yet). Pack defect candidate |
| 2 | Smoke tooling must not depend on the caller's shell environment (`SSL_CERT_FILE`, `PYTHONPATH`) | `18-...` W1, W5; watch-on-attempt1-tls-failed.json | D1 toggle time unmeasured; one wasted watcher run | Project-pack rule plus the `smoke.py` fix. Pack defect for the support session |
| 3 | Deploy-bearing tech specs run about 2.7x; estimate them by what they must contain (deploy sheet, smoke, cost model) | STATE Notes: 394k after stage 3 | about 153k over plan at stage 2 | Planning template estimate guidance. Nowhere yet |
| 4 | Event-log allowed paths must be derived from the worktree root when the slice runs in a worktree | commit 506bcd7 "verified with worktree-prefixed allowed paths" | one re-verification | `event-log` / charter-check in the pack. Pack defect for the support session (cause unconfirmed: looked at the commit subject and the release checklist only) |
| 5 | Run the what-if pass rule against a normalised diff so representation noise needs no ruling | `7.2-whatif-ruling.md`, W6 | one Orchestrator ruling per deploy | Deploy sheet tooling. Nowhere yet |
