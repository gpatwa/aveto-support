# End review — fix-service-accounting

> Orchestrator, 2026-10-24. For the owner. Charter `CHARTER.md` sha256 `afc984d1…aefe4`, approved 2026-10-23T07:18Z (APPROVAL_RECORD-1).

## Result

Issues #6, #7 and #8 are fixed, deployed and smoke-checked live. The service now reserves both possible judge attempts and returns the unused part, charges each attempt on its own outcome, and prices `claude-sonnet-5-5` at $2 and $10 per million tokens. Revision `ca-aveto-ask--0000008` (image `aveto-ask:d067b9a95ac6`) serves 100% with the kill switch off. The pull request is open for you to merge; the run did not merge it.

- **Fail-first:** 30 tests fail on `87178bd` with the figures the spec named (for example #6: `22466000 <= 13124000`), and pass on the branch. QA reproduced the list independently, and reverting each fix alone makes a new test fail.
- **Regression:** mypy clean, ruff clean, 668 passed, 0 failed (3 runs). The baseline failure on `main` (`test_core_files_unchanged`, pack v28's `event-log.mjs`) is repaired test-only (C1.4).
- **Nothing else moves:** `aveto_support/`, `prompts/`, `.claude/`, `.agentic/SAFETY_INVARIANTS.md` and the judge prompt are byte-identical to `87178bd` (`09-deploy/p2-nothing-else-moves.txt`). INV-1 to INV-5 unchanged (C5.0).
- **Live smoke (2026-10-24, `10-smoke/smoke-result.json`):** g01, g03, g04 answered, byte-identical to local `retrieve` (index hash `f36ef5d4…a756` matches the build); gu15, gu18 `no confident match`. Cost per judged question **$0.008544** (n = 5), inside the 15% band around $0.0078 (9.5% above it). The counter's spend equals the token cost at $2/$10 **exactly** (gap 0). No question text in any log table (`10-smoke/log-search.txt`). Kill switch: with it on, a POST got 503 `service_off`; off took **71.4 s**; the on-toggle time was **not measured** (see Misses), upper bound about 73 s from the deploy timestamps.
- **Verdicts:** code review 5 findings, 0 Important (tier High, unscored); QA GO WITH CONDITIONS; Security PASS (standard); Release Gate tier 3 GO WITH CONDITIONS, all pre-deploy conditions met; Production Verification HEALTHY WITH WATCH ITEMS, no rollback needed.

## Blocked on you (decisions, none blocks the merge)

1. **The daily pause comes at about 33 questions, not the intent's 41** (estimate; CR-3). Reserving two attempts per question means the day closes when settled spend plus two attempts would pass the cap. Security found this no worse than before: the live revision paused at about 23 to 27.
2. **A1:** a connection error followed by a success is now charged usage only. "connection" also covers a connection dropped while the reply is read, so an attempt Anthropic may have billed can go uncounted, up to about $0.03 each time (estimate). It needs a network fault, and the day's cap still holds against the counter. Accept, or ask for a slice that charges such attempts.
3. **A2:** that Anthropic does not bill a 429 is **unconfirmed** (looked: the repo, which states it without a source, and the SDK; no network check of Anthropic's docs).
4. **Rollback is unrehearsed.** After D2, revision `0000006` is no longer active; rolling back means reactivating an inactive revision, never tried on this app. The proven fallback is the kill switch (on, about 70 s). A rehearsal needs a Charter line; the tier 3 rule says a High change's rollback is rehearsed before it is offered, so this is a gap.
   **Owner's decision on items 1 to 3 (2026-10-24, Gopal Patwa, directly in the driving session):** "I accept the 33-a-day pause, A1 and A2 as they are; record that in END_REVIEW.md." Items 1 to 3 are closed as accepted; no follow-up slice is opened for them. A2 stays unconfirmed (no source for 429 or 4xx not being billed). Items 4 and 5 remain open.
5. Carried, unchanged: D1 (counters reset on every restart and redeploy; this run's two deploys reset them twice), A3 (a question admitted before midnight UTC is charged to the next day), CR-4/A5 (settled cost is not clamped to the reservation; pre-existing).

## Human review (tier High)

Read the change itself: `git diff main...claude/fix-service-accounting -- aveto_service infra tests` (5 source files, 5 test files). The review findings are in `code-review.md`; Security's advisories in `14-security-review.md`.

## Found

- **Event log** (`EVENTS.jsonl`, `events-verify-output-final.txt`): chain intact, 777 lines, head **`bcd55d013d3d0c87`** when this file was written. Calls: main 104 (4 failed), architect 72, tech writer 45, security 33, release manager 33, backend 26, engineering manager 25, QA 21, production verification 21, post-launch 9; all roles 0 failed. Attempts with no outcome: 1 (a `cd` in the Orchestrator's session). No write outside the allowed paths. The first verifier run used paths without the worktree prefix and flagged every write; re-run with the prefix (Orchestrator error, corrected before release).
- **Questions asked of you after the Charter:** 0. (You switched the session model twice and ran `/agentic-resume` once after a pause; no decision was asked.)
- **Code review findings:** 5 (0 Important, 3 Nit, 1 Pre-existing, 1 behaviour note): 0 fixed, 4 intentional, 1 reported pre-existing. Reviewer not noisy on this run.
- **Spend against estimates** (peak context summed per spawn, from `usage.mjs`; the Orchestrator's own session is not counted):

| Stage | Est. | Actual | |
|---|---|---|---|
| 1 Scope | 50k | 64k | 1.3× |
| 2 Tech spec | 90k | 236k | 2.6× |
| 3 Build + smoke script | 110k | 103k | 0.9× |
| 4 Review | 50k | 0 (Orchestrator) | — |
| 5 QA | 70k | 65k | 0.9× |
| 6 Security | 70k | 125k | 1.8× |
| 7 Docs | 50k | 81k | 1.6× |
| 8 Release Gate | 80k | 117k | 1.5× |
| 9 Deploy | 60k | 0 (Orchestrator) | — |
| 10 Smoke verdict | 60k | 46k | 0.8× |
| 11 Addendum + post-launch | 40k | 82k | 2.1× |
| **Total** | **730k** | **919k** | **1.26×; under the 950k ceiling** |

  During the run I tallied the agents' own token reports and sent notices projecting about 1,015k above the ceiling; the harness figure is lower because the backend's two passes count once at their peak.

## Misses (Charter and process)

- **C6.P:** no permission prompt appeared, but the session ran in bypass-permissions mode for most of the run, so that proves little. Commands outside the listed rules ran: housekeeping in the Orchestrator's session (`sed`, `python3`, `cp`, `grep`, `shasum`, `tee`, `mkdir`, `date`), the smoke and watcher with an environment prefix (`SSL_CERT_FILE=/etc/ssl/cert.pem`, `PYTHONPATH=.` before `uv run`), and the log search inside a `sleep`. All read-only or local except the smoke's own five POSTs (C3.1, C8.5). The workspace id came from the what-if output, so the unlisted `workspace show` was not needed.
- **D1 toggle time not measured:** the first `watch on` failed TLS verification on every poll (python.org Python needs the system CA bundle, as `LOCAL_COMMANDS.md` notes). The smoke script should set this itself; sent as a lesson to the support session (`19-post-launch-learning.md`, lessons 2 and 4).
- **The smoke script** was assigned to stage 3 in the spec but left out of the stage 3 brief (Orchestrator's miss); its follow-up hit a usage limit and was resumed.
- **Stage 9** ran without a Cloud Deployment spawn (spec §7 was already the literal sheet the Release Manager checked); recorded in `STATE.md`.

## Where things are

Branch `claude/fix-service-accounting`; pull request https://github.com/gpatwa/aveto-support/pull/9. Live: `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`, revision `0000008`. Local `.claude/settings.local.json` (the C6.P rules) deleted after the pull request opened.
