# Docs note - result-page-clarity (Tech Writer, stage 7)

Applied under Charter C1.3: README.md, docs/runbooks/public-ask.md, and .agentic/CURRENT_MVP_STATUS.md only. No visitor-facing string, code, ARCHITECTURE.md or ADR touched. No live figure, revision or date written; the deploy has not happened.

| File | Edit | Record behind it |
|---|---|---|
| README.md | New paragraph "Result first" after "The page": order on a result page, home unchanged, scroll and focus, no wording change, answering unchanged. Marked built and tested locally, not deployed or merged. | 08-browser-checks.md "Order" and focus; 13-qa-evidence.md sections 2 and 3 |
| docs/runbooks/public-ask.md | New section "Result-first page": what changed, post-deploy check table (local 16.1 px at 1280x800, 15.6 px at 375x667, focus `#result`; live column NOT YET MEASURED), rollback per section 2, not rehearsed. | 08-browser-checks.md item 1 table; bar from the same file |
| .agentic/CURRENT_MVP_STATUS.md | Slice entry with before/after heading tops (-2,820.9 to 16.1; 292.1 to 16.1; -4,182.9 to 15.6; -2.9 to 15.6), axe 4.10.2 zero serious or critical on five local views, 738 passed, QA GO. "Not yet done": live measurements, deploy, rollback rehearsal, Codex review, release verdict, aveto.dev screenshots. | 08-browser-checks.md; 13-qa-evidence.md section 1 and verdict |

## Not written, on purpose
- No live heading position, revision, deploy date or rollback timing (no record).
- No release or readiness claim (Release Gate's verdict).
- The no-JavaScript heading offset, the dark colour scheme, a screen reader: not measured (08-browser-checks.md), so not claimed.
- The short-answer live figure of 616 of 800 px from the intent is not quoted; it is the intent's, not a record in 08.

## Flags
- QA P3-3: docs/ARCHITECTURE.md is in the diff (Architect's page row); no contradiction found with these docs.
