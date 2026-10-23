# 15b docs note: README, status file, runbook (Tech Writer, depth standard)

HEAD b860183. Files written: `README.md` (edited), `.agentic/CURRENT_MVP_STATUS.md` (edited), `docs/runbooks/public-ask.md` (new). Not touched: `SAFETY_INVARIANTS.md`, `docs/ARCHITECTURE.md`, code, STATE.md. Nothing committed.

## What I wrote

- **README.md:** a banner line, and a new section "Public service (Ask the Docs)": what it is (verbatim passages or `no confident match`, the model decides only whether they answer, no generated text), how it differs from the attended `/aveto-judge` path (both exist; attended path still attended and internal), routes, limits (10 an hour, 500 characters, $10/31 a day with UTC reset, kill switch, owner's console limit; counters restart with the replica), what is sent to whom, how to run locally, and a "not yet measured (stage 18)" list. The existing Status section and every recorded figure from earlier slices are unchanged.
- **CURRENT_MVP_STATUS.md:** a "What exists" entry for the service; "Not yet done" entry with open owner decisions D1 to D7 and the stage 17 and 18 items still to run; "Out of scope" corrected (the program still makes no model call; the HTTP surface now exists on the branch; database, accounts, chat, custom domain stay out). Earlier figures untouched.
- **docs/runbooks/public-ask.md:** deploy commands 1 to 5 and rollback copied from tech spec section 7 (also identical in `11-infra-note.md`); kill switch (on/off by command 5, new revision, counters restart); `/health` fields; UTC reset and per-replica-lifetime caveat; 7-day read-back (spec section 5 command, run for both tables); "Paused for today", `judge error` and outage handling; the Anthropic console limit as an owner action; removal of resources; S-C1 to S-C3 as a pre-switch-on checklist.

## Sources

`intent.md` (Done means last line, Out of scope), `05-tech-spec.md` sections 3, 4, 5, 7, `11-infra-note.md`, `11c-infra-checks.md`, `14-security-review.md` (D1 to D7, S-C1 to S-C3, S-A3, S-A10), `13-qa-evidence.md` (606 passed), the code (`aveto_service/settings.py`, `main.py`, `limits.py`, `pipeline.py` health fields, `render.py` copy), `docs/runbooks/answerability-judge.md` for style. I did not re-read `08/09/10-*` notes or CHARTER C8.3/C8.5 in full (C8.5 line read: gate batches of at most 10, an hour apart).

## Left out because unmeasured

Cost per question, response time (median, slowest), cold-start time, monthly Azure cost, the gate result, deploy-step durations, image size. The spec's estimates ($0.008 a question, about 35 questions a day, $5 to $10 a month Azure, 10 to 30 s cold start) are not repeated anywhere; they are estimates marked (U) in the spec, not recorded figures. The only numbers stated are limits set in code (10, 500, 30 retrievals an hour in the runbook, $10/31) and 606 tests passed from the QA run (labelled as that run).

## Could not confirm from the repo

1. **Removal commands in runbook section 10** (`az containerapp delete`, `env delete`, `workspace delete`, `acr delete`, `identity delete`) are not in the spec or any note; I wrote them from the resource names in `infra/main.bicep`. Marked "not run" in the runbook. Whether the vault is inside `rg-aveto-ask` is not known, so the runbook says not to delete the group as a shortcut. The role-assignment removal is described, not given as an exact command.
2. **`az containerapp show ... runningStatus`** in the outage section is from memory, marked "not run".
3. **No committed command starts a local server with a fake judge.** The README says so and points to the fake-judge tests. It mentions `aveto_service.main:app` (from the Dockerfile CMD and `main.py`) without giving a `uvicorn` line.
4. **Latest test count.** 606 is QA's figure at stage 13; the security rounds (S-R1, S-R2, S-A2, S-A4, S-A6, S-A8) may have changed it. I did not run anything.
5. **Whether the security required fixes S-R1 and S-R2 were re-checked.** The code has a 30-a-hour retrieval limiter (`limits.py:20`), which I documented as a fact of the code; I did not read a re-check record.
6. **Whether table retention below 30 days works, ingress behaviour, console limit hardness, effort field acceptance:** all still unconfirmed upstream; the docs say so or point to the stage 17 check.
7. The runbook states `Paused for today` copy is inaccurate during transient shortfalls and outages (S-A3). If later rounds changed the copy, that line is stale.

## Corrections after the coordinator's message (Charter v2, final safety words)

- Runbook section 10: the vault is inside `rg-aveto-ask` (owner created it there, per the coordinator); "do not delete the resource group" is now stated outright and the "not confirmed" wording is removed. Item 1 above is superseded on the vault location only; the delete commands are still not run.
- README "What is sent to whom" now names the SDK's own headers and links INV-5 for the two exceptions; the status file and runbook link INV-4/INV-5 instead of restating them. Checked against the final `SAFETY_INVARIANTS.md`; I did not read 15a or 15c.

## Release-gate conditions P3 and P4 (smoke)

- **P3:** runbook section 11 "Processors and data": the 07 section 9 record (Anthropic, Azure), what each receives (07 section 2), terms status and UNKNOWNs (07 section 3), abuse-line retention 7 days for the two named tables, what the visitor is told (07 section 6 as built in `render.py`, per 16 checklist 8.1 row 7; I did not re-read `render.py`). DPA worded "in place by reference per the owner's statement; text unread". Links `07-compliance-data.md` and `CHARTER-v2.md` C4.1/C4.2. Nothing invented; UNKNOWNs kept.
- **P4:** runbook section 12 "Monitoring": one table restating 06 section 7 thresholds, actions, cadence, owner, gaps M1 to M3; no new threshold. Grep targets "text unread", "5%", "M1" are present.
- Not checked: `render.py` wording against my paraphrase of the page copy; no shell.

## Final pass: recorded figures (stage 18 and 17 live checks)

Source: `18-gate/RESULT.md`, `17-deploy/README.md`, intent last Done-means line. Edited README.md (banner, service status, retention sentence, recorded-figures table with caveats, attended-path "not deployed" wording scoped to the attended path), CURRENT_MVP_STATUS.md (service moved from built to deployed and gate scored once; figures, live checks, D1 to D7, unmeasured list; earlier slices' figures untouched), runbook (status, measured kill-switch and cold-start times, counters reset note, first-live-call whitespace lesson, F-LIVE-1, build notes, token baseline). Address named in the runbook and status only; not linked from aveto.dev.
Left unmeasured and said so: monthly Azure cost, IPv6 clients, screen reader, real visitors, previous-image rollback, price confirmation. The runbook's `answer` share baseline row still says "not yet recorded" (RESULT.md gives no admitted-call answer share). Unconfirmed by me: I did not check the served page or the live address; the "S-C1 passed" and "effort accepted" lines rest on `17-deploy/README.md`.

## Cost figure and Azure budget alert (2026-10-23, smoke, facts given by the Orchestrator)

- Price confirmed by the Orchestrator from Anthropic's pricing page and models overview ($2 / $10 per million; pinned id; retirement not before 2027-09-28; `effort` default `high`). I did not check the page myself. The recorded "$0.0118 per question at default prices, unconfirmed" is replaced by "$0.0079 per question at Anthropic's published prices; the service's counter, at $3/$15, reads 50% high" in README, CURRENT_MVP_STATUS and the runbook (status line, `/health` table, new section 8 subsections "Cost and capacity", "Pricing", "Budget alert"). Capacity: about 1,270 questions a month in the $10 limit; the daily pause at about 27 a day by the counter (about 41 real). The env change to 2000 and 10000 is NOT done; stated as the owner's call and as an open item in the status file.
- Budget alert `bud-aveto-ask` ($20/month, notifies only, not in `infra/main.bicep`, removal command) written into the runbook and summarised in README and the status file. D5 now reads: alert yes, cap no.
- Not changed: the earlier lines in this note and `18-gate/RESULT.md` still show $0.0118 as the figure recorded at the time. Other runbook lines (section 12 thresholds, token baseline) were not re-derived. No commit.

## For other roles

The README Status banner of the attended judge ("merged to main by PR #4") is unchanged and still true on `main`; this branch is not merged. The Release Manager should check the new README section against the final tree. Safety-text (INV-4, INV-5) and the ARCHITECTURE record are the Architect's parallel work and may need cross-checking against the "what is sent to whom" paragraph.
