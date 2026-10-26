# Figures recorded for the scorecard (stage 9b input)

The Backend Architect writes these rows into `aveto_service/scorecard.toml` and nothing else. Each row's record is a file in this repository. Values are copied from the cited files; none is estimated.

| section | label | value | basis (must start "Measured" or "Recorded") | record |
|---|---|---|---|---|
| checks | Tests | 731 passed, 0 failed (668 before this build) | Measured 2026-10-26 with `uv run pytest` on the tree before the release; the 668 is the count on the starting point. | runs/polished-chat-experience/13-qa-evidence.md |
| checks | Accessibility checks | No serious or critical issues on 5 views | Measured 2026-10-26 with axe-core 4.10.2 (WCAG 2.0 to 2.2, levels A and AA) on a local run of this release: the ask page, an answer, a refusal, the resting state and this scorecard. Colour contrast was also measured by hand where the tool could not decide. | runs/polished-chat-experience/08-browser-checks.md |
| checks | Mobile checks (375 px) | No sideways scrolling; the whole flow works from the keyboard | Measured 2026-10-26 in a browser set to 375 px wide on a local run of this release; keyboard flow tried with real key presses. Touch gestures and real devices were not tested. | runs/polished-chat-experience/08-browser-checks.md |
| checks | Open findings | None at P0 or P1; two at P2 | Recorded 2026-10-26 by the independent Security Review (no P0 or P1; two P2 findings, described in its report) and by the QA review (no P0 or P1). | runs/polished-chat-experience/14-security-review.md |

No row for the Codex review (it has not been recorded), for live cold or warm times on this release (measured after the release; the rows already in the file are labelled as an earlier release), or for local timings (measured with a stand-in for the model, so not a response time).

Links: `source_base` = `https://github.com/gpatwa/aveto-support/blob/<SHA>/` and `links.charter` = `https://github.com/gpatwa/aveto-support/blob/<SHA>/runs/polished-chat-experience/CHARTER.md`, `links.run_record` = `https://github.com/gpatwa/aveto-support/tree/<SHA>/runs/polished-chat-experience`, where `<SHA>` is the full commit id the Orchestrator gives in the spawn message (the commit that holds this file). `source_base` must end with a slash.
Also fix the basis of the existing "Warm response time" row: remove the words "sent one after another" (QA Q3: no record for that phrasing); say only "20 questions from one client".
