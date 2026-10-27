# Stage 13 Production verification (read-only; from the Orchestrator's records)

Service `ca-aveto-ask`, final revision 0000011, image `ffc2e2e5f39a`. Judged against tech spec 12.4 to 12.8 only. I ran nothing live; every line cites a record in `13-live/` or `12-deploy/`.

## Verdict: HEALTHY WITH WATCH ITEMS

Every pre-registered pass rule is met on the records. No behaviour failure, no C8.1 trigger. The watch items below are record-quality gaps and unmeasured areas. None is a failed rule.

## Pass rules

| Rule | Result | Signal |
|---|---|---|
| Behaviour, 7 questions (12.4) | PASS | `ask-result.json`: `behaviour_failure` false, `outcome_differs_from_expected` empty. Questions 1, 2, 3, 5 and 7 answered; 4 (gu18) and 6 (gu15) `no_confident_match`. All HTTP 200; the form path was 303 then result 200. No over-abstention and no R1 answered. |
| Byte equality | PASS | Index sha256 `f36ef5d4…a756` matches the ingest line in `acr-build.log` (line 130), so `byte_equality_established` is true. `byte_equal` is true on all 5 answered, including the form path (#7). It is null on the two refusals, which have no passages. |
| Log tables (12.5) | PASS, see W2 | `log-abuse.txt`: 7 rows, all `{"t","ip":"<16 hex>","o"}`, with 5 `answer` and 2 `no_confident_match`. This matches the 7 requests, so the arrival precondition holds. `log-search.txt`: no rows. |
| Rollback rehearsal (12.7) | PASS | `rehearsal-timing.json`: command to first of three polls 65.2 s (to confirmed 70.3 s), limit 600 s. `after-2.txt`: revision 0000010 at 100 Healthy, image `d067b9a95ac6`, env identical to `after-1.txt`. `check-old.json` ok: `/health` 200, no skip link, `/scorecard` 404. |
| Roll forward (12.8) | PASS | `rehearsal-timing.json`: 64.5 s (69.5 s confirmed). `after-3.txt`: revision 0000011 at 100 Healthy, image `ffc2e2e5f39a`, env identical. `check-new-after-forward.json` ok. |
| Headers | PASS on the final revision | `security_headers_on_root` and `security_headers_on_scorecard` are true in `check-new-after-forward.json` (revision 0000011). See W1 for revision 0000009. |
| Counts delta | As expected, reported only | +7 asked, +5 answered, +2 not answered, 0 visits, 0 clicks. |

The two "about 65 s" figures are the Charter definition (create command to first of three). The watcher's own clock gives 87.2 s and 86.5 s from watcher start. The README is consistent with `rehearsal-timing.json`.

## Measured, with no pass figure

- Warm (requests 2 to 7, live): median 1.36 s and slowest 1.59 s as recorded. Request 1: 1.56 s. Per question: 1.56, 1.36, 1.34, 1.32, 1.59, 1.13, 1.58 s. Method: spec 12.4, JSON and form, `perf_counter`, send to full body, 2026-10-26T23:28Z.
- Cold: 25.8 s to the first `/health` 200, then `GET /` 0.31 s. Date 2026-10-26T23:45:12Z. Method: one `GET /health` with a 180 s timeout after scale to zero, as in the 30.8 s record. The README says the replica was idle about 7 minutes with count 0. That is not in `cold.json` (see W3).
- Cost: $0.059978 for 7 questions, which is $0.008568 a question (28,464 input and 305 output tokens). The day's cap is $0.322580, with 0.059978 spent at the end of `ask`.

## Watch items (records that do not fully support a README claim, or gaps)

- **W1. `check-new.json` is not a revision 0000009 record.** The README cites it for the check on revision 0000009. Its timestamps are 23:37:49 to 23:37:50 and the content is identical to `check-new-after-forward.json`. The deploy-1 `check new` was overwritten by the post-forward run. Headers, skip link and suggestions are therefore evidenced only for revision 0000011. Revision 0000009 is evidenced by `after-1.txt` and `ask-result.json`. Ask the Orchestrator to correct the README row or restore the original output.
- **W2. Log evidence is weaker than the README wording.** `log-search.txt` is a zero-byte file. That cannot tell "no rows" from a query that returned nothing because it failed. The query time and the literal command are not recorded, so the 5-minute wait after request 7 (23:28:45) cannot be confirmed. The 7 arrived abuse rows show the ingestion lag was already past. The abuse table is clean. The absence of question text is supported, but not independently proven.
- **W3. Cold-start precondition not in the record.** `cold.json` does not hold the replica count or the idle time. The 7 minutes is consistent with the timestamps (last check 23:37:50, cold 23:45:12, about 7.4 min), but the "read as 0" claim rests on the README alone. A single measurement.
- **W4. Small record flaws.** (a) `check-old.json` has trailing fragment lines after the JSON object (lines 2 to 3), so it is not valid JSON as a file. The first line is intact and says ok. (b) The README and `ask-result.json` give a median of 1.36 s, but the median of the six recorded values (1.13, 1.32, 1.34, 1.36, 1.58, 1.59) is 1.35 s. (c) Rulings exist only for what-if 1 (`whatif-1-ruling.md`). `whatif-2.json` and `whatif-3.json` have the same shape (image, probe order, server-populated fields), but no written ruling is on file.
- **W5. TLS.** Python could not verify the platform chain, so the checks used `SSL_CERT_FILE=/etc/ssl/cert.pem` in a scratch wrapper. The README says verification stayed on. I cannot see the wrapper. Unconfirmed; places read: README, `live.py` listing only.

## Not checked live

- The kill switch (no toggle; C8.3 allows one only if C8.1 requires it). Offline tests only.
- Touch devices.
- A real-browser run against the live URL. Live checks were HTTP only.
- The waiting state (the in-progress card while a live answer is pending).
- Codex review: the owner's.
- Also not covered: the live drawer and links beyond `/scorecard` 200, Visits and click counts under real visitors, and any window beyond about 17 minutes after deploy 1. I saw no record beyond cold at 23:45Z.

## Rollback

Not triggered. The rehearsal already showed the previous image restores in 65.2 s. The plan stays tech spec section 13.

## Handoff

HEALTHY WITH WATCH ITEMS goes to SRE and into `END_REVIEW.md`. W1, W2 and W4 need correction by the Orchestrator, not a redeploy.
