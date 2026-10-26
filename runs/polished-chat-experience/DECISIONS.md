# Orchestrator decisions inside the Charter

## D1 (2026-10-26, after stage 1): refusal card shows no passages
Stage 1 (`01-scope.md` S1) found that intent item 2 ("the nearest passages") contradicts INV-4(b): on `NOT_ANSWERABLE` the service returns "no passage, path or reason", a test pins it, and Charter C1.3 and C5.0 forbid changing `SAFETY_INVARIANTS.md`. Showing passages needs a safety-text change, which the intent and Charter section 9.1 make a stop.
**Taken path (Option A, inside the Charter):** the refusal card carries the refusal message, a rephrasing hint, the issue link, the docs link and the suggested questions. No passages. This is a reduction of intent item 2, not a safety change. **For the owner:** if you want nearest passages on the refusal screen, that is Option B (amend INV-4(b); a new Charter hash and a rule-4 approval) and a later change.
## D2: receipts drawer
Shows the outcome, the docs commit and the file and line list this request already held. Not the `signal` line (INV-4: no deciding-signal line on the page; same stop as D1 if wanted).
## D3: "docs search"
The service has no docs search. Read as: the docs link stays visible in the resting state. Recorded as a reading of the intent.
## D4: size
Stage 1 rates the slice oversized (about 18 to 22 files). Run as one slice (splitting changes the Charter hash). Stage 4 ends at a checkpoint: backend tests green and committed before stage 5.
## D5: unconfirmed claim
"First load about 26 seconds": no record found in README, runbook or status file (they record 30.8 s). Not repeated anywhere; the scorecard shows only measured figures.
