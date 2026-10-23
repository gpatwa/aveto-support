# Post-launch learning: public-ask-the-docs (stage 19, SMOKE, Charter v2)

From the saved artefacts only. I called nothing live and have no shell. Anything I did not check is marked unconfirmed, with where I looked.

## Goal met?
Partial to yes. Bar 1 10/10 met. Bar 2 8/10 met, exactly at the bar, margin zero (`18-gate/RESULT.md`). Production verification: HEALTHY WITH WATCH ITEMS (`18-production-verification.md`). The monthly Azure cost, which the intent lists as "measured and reported", is not recorded.

## 1. What worked
- Fail-closed startup: the crash-looping first deploy served nothing and made no model call (`STATE.md`, Orchestrator note after stage 17).
- Stage order held. The method froze before the gate set was committed (sha256 7eb4f588…064f). The gate was scored once, and the scorer refuses a repeat post (`RESULT.md`).
- Different-model words check (15c) caught what the author could not (see 2e).
- M3 byte-identity: live passages equal local `retrieve` (`17-deploy/m3-byte-compare.txt`). The G5 canary found no question words in the logs (`17-deploy/g5-canary.txt`).
- Kill-switch rehearsal: about 65 s on and 66 s off (`17-deploy/e3-rollback.txt`).
- Security round 2 fixed many advisories inside the run (STATE note, security round 2).

## 2. What surprised us
a. **First deploy crash-looped on file modes.** `ingest` writes with mkstemp (0600) and the image files were root-owned, so uid 10001 could not read them. Logs showed `{"ops":"startup_failed","c":"index"}`. No offline test could show this, because tests run as one user and the image had never been built (no Docker daemon). Evidence: STATE note "stage 17 (kill switch ON)", F-LIVE-1. Cost: one new commit, P2 repeated, rebuild, redeploy, checklist reopened.
b. **Stray whitespace in the stored key gave a silent `judge error` (502).** The service by design cannot say why: the log contract holds abuse and ops lines only, with no cause code. A cause code needs a Charter amendment to C4.2/C5.2. Cause is "probable, not proven" (`17-deploy/README.md` S6; `18-production-verification.md` section 1). The owner re-stored the key and it worked.
c. **Roles without a shell forced the Orchestrator to run every live command and re-run every check.** This hit Cloud Deployment, Release Manager, Tech Writer and Architect (SR-1 in `SUPPORT_REQUESTS.md`; STATE notes after stages 11 and 15). The guard was correct and the pack gave no stage that could validate Bicep or deploy. I did not find a support reply in `SUPPORT_REPLIES.md`. I did not check whether one exists, so that is unconfirmed.
d. **The plan's own wording could not avoid two Charter stops** (`15c-words-check.md`, STATE note "stage 15 stop"). First, the SDK's own headers (user-agent, x-stainless-os/arch/runtime) go beyond C4.1's "exactly". Second, INV-5's "one exception" sentence had to change because the service is a second exception, and C5.2 says every other sentence stays. Both needed Charter v2 (APPROVAL_RECORD-2). Neither could be seen until the words were written and checked.
e. **The in-service daily cap is not a cap.** Spend and rate counters reset on every revision change and scale-to-zero (observed in `e3-rollback.txt` and `RESULT.md`: batch 2 started at 0). The $10 console limit is the only durable cap, and it rests on the owner's word (S9, D1, D7). The tech spec flagged this at stage 5, but the live run showed it concretely.
f. **Budget.** The plan estimate of 2.0M was reached at stage 15 (2004k) and the run finished near 2.5M, still under the 3.0M ceiling (`STATE.md` Budget and Trace). Spend at the time of reading: 2343k, and stages 18 and 19 are not in it. The biggest rows are Architect 215k and 203k, Security 226k, QA 145k, Backend 146k, and Release Gate 197k. The 15c check cost 180k plus a round 2. trace.json is absent (see 4).
g. **The IPv6 test was invalid.** The service has no AAAA record, so the IPv6 rate-limit key is unconfirmed (`17-deploy/s1-step2-result.txt`, `18-production-verification.md` section 5).
h. **Cost per question was 1.5 to 1.85 times the spec estimate.** Measured $0.0118 against an estimate of $0.008, at default prices that are unconfirmed for `claude-sonnet-5-5`. Daily capacity at those costs is about 27 questions (`RESULT.md`).
i. **Over-abstention.** 2 of 10 answerable questions got no answer (p06, p09). Earlier sets had 3 of 19 and 4 of 28, so it is consistent, not new.
j. **Unexplained waits.** After a revision change the URL took 3 min 50 s and 150 s to answer. Cause unconfirmed (`RESULT.md`, production verification section 5).

## 3. Carry-forward items for the next slice
1. Persistent counter store, so the daily cap survives restarts. Needs a Charter line, because C8.3 names no storage resource. Owner: Software Architect, then the human. (D1, CR-3)
2. A cause code for `judge_error` (for example auth, whitespace key, timeout) in the ops log. Needs C4.2/C5.2 wording. Owner: Software Architect, with Security checking the words.
3. A smoke test for file modes and the runtime uid in the image, run at build or as a startup self-test. Owner: Backend Architect. (F-LIVE-1)
4. Strip or validate the key on read, and fail startup with a named cause. Owner: Backend Architect. This may sit inside item 2.
5. Over-abstention (2 of 10) and a larger gate set. Ten questions cannot separate 80% from somewhat below. Needs a new held-out set and an owner decision on prompt or judge changes. Owner: AI Engineer, with the Data Analyst for the set.
6. Read the monthly Azure cost after a day or more, and close the "measured and reported" item. Owner: Cloud Deployment, with the Orchestrator running the command.
7. Confirm the `claude-sonnet-5-5` prices and correct the service defaults. Owner: AI Engineer.
8. IPv6: add an AAAA record or dual-stack and test the key. Also run a small concurrency burst. Owner: Cloud Deployment, then QA Evidence.
9. Re-search all five log tables for the 20 gate questions' words (none saved). Owner: Security & Privacy.
10. Rehearse previous-image rollback once a second healthy tag exists. Owner: Release Manager.
11. The aveto.dev link. It is a playbook-repo change and needs the owner's word. Decide D1 (counter reset) and D3 (public `/health`) first. Owner: the human, then Tech Writer.
12. Open advisories S-A3 (the "paused, not a fault" copy is false during an outage), S-A5 (invisible-character injection), S-A7, S-A9, S-A10 and S-A11 (no cap on Azure spend). Owners: UX, Security and Backend, as each is routed. Also the onnxruntime telemetry line, which is unconfirmed.
13. Investigate the 150 s to 3 min 50 s post-revision waits and the 30.8 s cold start (min replicas, startup probe). Owner: Cloud Deployment.

## 4. Pack and playbook suggestions (for the support session; not edited)
1. **Role tooling vs assignments.** `.claude/agents/cloud-deployment.md` and `.claude/hooks/write-scope-guard.mjs`. Either give the deploy role read-only `az` checks, or have the Architect brief say deploy and validation are Orchestrator-run. Also state a rule to avoid assigning outside the guard's scope. (SR-1; still unanswered as far as I could find.)
2. **Image smoke test as a pack default.** Release gates or the Backend brief (`RELEASE_GATES.md`, tier 3): "run the image as the runtime user and read every file it needs" before first deploy. Offline tests could not catch F-LIVE-1.
3. **Words check earlier.** Run the different-model check on a draft of the safety words before the Charter is approved, and add to the Charter template that any "exactly" or "one exception" wording must be checked against the SDK and library behaviour. Touches `templates/CHARTER_TEMPLATE.md` (name unconfirmed) and the stage 15 flow. It would have avoided Charter v2.
4. **Ops-log contract.** Add to the Charter/tech-spec template a line asking whether the log contract allows a failure cause, since a silent 5xx cannot be diagnosed live. Touches the project-pack C4 section.
5. **Budget re-estimate.** `RUN_ECONOMICS.md`: when a stage reaches 100% of plan before the live stages, require a re-estimate that includes the Orchestrator's own deploy and gate work, not only spawns. Opus 15a at 203k and 15c at 180k were not forecast.
6. **trace.json is missing.** `runs/public-ask-the-docs/trace.json` does not exist (Glob), so I could not confirm it complete or regenerate `runs/ANALYTICS.md` and `runs/dashboard.html`. I have no shell to run `analyze.mjs`. This is **handed back**: the Orchestrator must produce trace.json (`SLICE_STATE.md`) and run `node <playbook>/execution/analyze.mjs .`. Likely flags once run: 5 Tech spec (215k), 14 Security (226k) and 15a (203k) against the per-stage cap. Unconfirmed until it runs.
7. **Counter-reset check in the Charter.** A hard limit that lives in memory behind scale-to-zero is not a limit. Add to the intent/Charter template: "which limits are durable?"

## Lessons
| Lesson | Evidence | Cost | Enforce at |
|---|---|---|---|
| A built image must be run as its runtime user before the first deploy | F-LIVE-1, STATE note stage 17 | one commit, P2, rebuild, redeploy, checklist reopened | Backend brief or `RELEASE_GATES.md` (tier 3). Pack defect (suggestion 2) |
| Words that say "exactly" or "one exception" must be checked against the real SDK before the Charter is approved | `15c-words-check.md` S10, S11b | Charter v2, about 180k check plus 52k round 2 | Charter template, stage order. Pack defect (suggestion 3) |
| A silent failure the log contract cannot explain turns a 1-minute fix into a diagnosis by elimination | `17-deploy/README.md` S6; production verification section 1 | an extra live attempt, cause unproven | project pack, C4.2 wording. Nowhere yet |
| Roles without a shell push every live command onto the Orchestrator | SR-1; STATE notes after stages 11 and 15 | Orchestrator context and re-runs for 4 roles | Agent briefs and guard. Pack defect (suggestion 1) |
| In-memory limits behind scale-to-zero are not limits | `e3-rollback.txt`, `RESULT.md` | the daily cap is per replica life; the owner's console limit is the only cap | project pack and Charter template. Nowhere yet |

## .agentic/CURRENT_MVP_STATUS.md
Not edited. I checked it: the Tech Writer's pass already records the gate, figures, live checks, the "Not measured" list and D1 to D7. A carry-forward list would belong in `END_REVIEW.md`, not the status file.
