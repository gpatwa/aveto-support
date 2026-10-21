# PRD: public-ask-the-docs (stage 2, Product Manager, depth standard)

Sources: `intent.md` (source of truth; cited below as "Done N" = the Nth "Done means" line, counting from 1), `CHARTER.md` (C1.3 non-goals), `01-scope.md` section 7, INV-4 and INV-5. Lines marked **(inferred)** are mine, not the intent's. Where the intent and the Charter differ, the Charter governs (01-scope.md section 4).

## 1. Problem

Someone deciding whether to use Aveto has a question the site does not answer at a glance. Today the only way to get a sourced answer is to open a GitHub issue and wait for the owner, or to search the docs by hand. The retrieve-then-judge product already passed a held-out gate, but it runs only in the operator's own session, so no visitor can use it.

## 2. User and moment

A visitor to Aveto's public site, mid-evaluation, who would rather read the source passage than a summary (intent, "Who it's for"). The moment: they have typed a specific question about Aveto and want to know within a few seconds whether the docs answer it, and where. "A few seconds" is the intent's phrase, not a measured bar (see O3).

## 3. The one job

Given one question, show either the verbatim documentation passages that answer it, each with its file and line range, or say "The docs don't answer this" with a link to open a GitHub issue. A model decides only whether the passages answer the question; every word the visitor reads is copied from the docs (INV-4).

## 4. Requirements

Each is checkable by a test, a measured figure, or an audit-data check.

- **R1 Unchanged core.** Retrieval, ranking, the judge prompt `answerability-judge-v1` and the corpus at its pinned commit are unchanged; the service starts from `main` at pack v26. (Done 1)
- **R2 Answerable.** For a question the judge calls ANSWERABLE, the response contains the passages verbatim, each with path, heading and line range, and the page shows each with a link to the file and lines. A test shows the passages are byte-identical to what `retrieve` returns. (Done 2; intent "What I want")
- **R3 Not answerable.** For NOT_ANSWERABLE, the response carries `no confident match` only, no passage. The page shows "The docs don't answer this" and a link to open a GitHub issue. (Done 2; "What I want")
- **R4 Judge error.** For any other judge outcome (error, malformed or unparseable reply), the response carries `judge error` only, no passage. The page shows a visitor-readable failure, never a passage. (Done 2)
- **R5 Judge call bounds.** The judge runs through the Anthropic API with `claude-sonnet-5-5`, no tools in the request, the same prompt and the same verdict-only parser. Only the question and the shown passages are sent; the reason line never leaves the parser and is never shown. (Done 3; Charter C3.1, C4.1)
- **R6 Visitor rate limit.** A visitor (hashed IP, in memory only) can ask 10 questions per hour; the 11th within the hour is refused with no retrieval-to-judge model call. (Done 4)
- **R7 Daily spend pause.** The service keeps a daily spend counter from measured cost per question; when the day's share of $10 a month is reached it answers "Paused for today" and calls no model. (Done 4)
- **R8 Length limit.** A question over 500 characters is refused before any model call. (Done 4)
- **R9 Kill switch.** One setting turns the service off without a redeploy; when off, the service answers nothing and calls no model. (Done 4; Charter C8.1)
- **R10 Fail closed.** If a limit cannot be evaluated (counter unavailable, setting unreadable), the service refuses and calls no model. (Done 4, "fail closed")
- **R11 Backstop.** The owner-set Anthropic console limit of $10 a month remains the outer backstop; the service does not rely on it as its only control. (Done 4; Charter C6.6)
- **R12 No visitor data kept.** Questions are not stored or logged. Abuse logs hold a hashed IP, a time and an outcome code only, kept 7 days. A test shows a question never reaches a log line. (Done 5)
- **R13 Public page.** A plain, accessible page served by the service says what it is ("verbatim passages from Aveto's docs; a model decides only whether they answer"), its limits, and that questions are not stored. (Done 7)
- **R14 Deployed.** The service runs on Azure Container Apps (scale to zero) from an image built from this repo; infrastructure as code is in the repo; rollback is the previous revision or the kill switch. (Done 6; Charter C8.3)
- **R15 Pre-registered gate.** The 20-question gate (10 answerable, 6 not, 4 hostile), committed only after the method freezes with its sha256 matching `7eb4f588567d5b6fccea6dc59e2874f0d124777c9bde040c4e3a6de94786064f`, is scored once through the deployed service under the real limits. Bars: all 10 non-answerable and hostile questions get `no confident match` or a refusal with no passage shown; at least 8 of the 10 answerable get the right passages. A missed bar is reported as a miss. (Done 8; Charter C8.1, C8.5)
- **R16 Measured and reported.** The run reports cost per question, response time (median and slowest), cold-start time, a monthly Azure cost estimate and the gate result, each as a measured or labelled-estimate figure. (Done 9)
- **R17 Docs state only recorded figures.** README, `.agentic/CURRENT_MVP_STATUS.md` and `docs/ARCHITECTURE.md` state only recorded figures and stop saying "attended, internal" for this service only. (Done 11)
- **R18 Safety and review depth.** Security Review at adversarial depth, code review at tier High, Release Gate tier 3, and Production Verification of the live service after the deploy. INV-1, INV-2 and INV-4 hold; the attended `/aveto-judge` path keeps working. (Done 10; "Must not break")

Process-only lines (R1, R14, R17, R18) belong to the Architect, Cloud Deployment, Tech Writer and Release roles; they are here so QA can trace every "Done means" line.

## 5. Visitor-visible states

Stage 3 owns the journeys; stage 4 owns the copy. This PRD fixes only what each state must do and must not do. None shows a passage unless noted.

| State | Trigger | Must | Must not | Req |
|---|---|---|---|---|
| Answer shown | judge says ANSWERABLE | show passages verbatim, each with its file and line link | add, reword or summarise any text | R2 |
| No confident match | judge says NOT_ANSWERABLE | say the docs don't answer this; link to open a GitHub issue | show any passage; guess | R3 |
| Judge error | any other judge outcome | say it could not be decided, no passage | show a passage; expose the reason line or a stack trace | R4 |
| Rate limited | 11th question in an hour from one hashed IP | say the limit (10 an hour) and that trying later works | call the model | R6 |
| Paused for today | day's spend share used | say "Paused for today" | call the model; promise a reset time unless the design fixes one (O4) | R7 |
| Question too long | over 500 characters | say the limit (500 characters) | call the model; keep or log the text | R8 |
| Service off | kill switch on | say the service is off | call the model; show the kill-switch reason (inferred) | R9 |
| Cold start / slow | scaled-to-zero container starting, or a slow response | show that it is working (inferred) | look like a failure or double-submit the question (inferred) | O3 |
| Empty question (inferred) | blank input | stay on the page and ask for a question | call the model | (inferred) |

The "service unavailable" case where Azure itself is down is outside the service's control; the page, being served by the service, cannot show it.

## 6. Success metrics (only the intent's fixed figures)

| Metric | Bar (fixed in the intent) | Observed in |
|---|---|---|
| Non-answerable and hostile questions that show no passage | 10 of 10 (6 not answerable + 4 hostile) | gate result, R15 |
| Answerable questions that get the right passages | at least 8 of 10 | gate result, R15 |
| Questions per visitor per hour accepted | 10; the 11th refused | test and abuse-log outcome codes |
| Question length accepted | 500 characters | test |
| Monthly spend ceiling | $10 a month | service counter and console limit |
| Abuse-log retention | 7 days | infra config and test |
| Question text in any log line | none | test |

Measured and reported with no pass/fail bar, because the intent sets none: cost per question, response time (median and slowest), cold-start time, monthly Azure cost estimate. This PRD invents no threshold for them; if one is wanted it is O3 or O2 for the Architect and the owner at the end review.

If a bar is missed: reported as a miss; the kill switch is set on; the service stays on only on the owner's word at the end review (Done 8; Charter C8.1).

## 7. Non-goals (Charter C1.3)

- Generated answers, in any form. Writing replies in the model's own words is the separate drafting step.
- Multi-turn chat: each question is independent; there is no history.
- GitHub intake or posting: the issue link only opens a page; nothing is posted (INV-1).
- Visitor accounts or sign-in.
- A custom domain such as support.aveto.dev.
- Changing retrieval, ranking, the judge prompt or the corpus.
- The link from aveto.dev (a playbook-repo change after the run, on the owner's word) and the drafting step.

## 8. Open questions

Blocking implementation (answered by the Architect in the tech spec, stage 5; none needs the owner unless noted):

- **O1 Kill switch mechanism.** Which one setting turns the service off without a redeploy, runnable by an agent in the C8.1 failure path, using only actions Charter C8.3 lists? If it needs an unlisted action (an extension install, writing a Key Vault value), that is a Charter stop (9.1) found at stage 5, not something to assume. Also: does the page show "off" or does the service answer nothing at all (R9, "Service off")?
- **O2 Cost per question and daily capacity.** There is no price or measurement in the repo. The daily share of $10 a month is about a third of a dollar (inferred arithmetic, not a bar); how many questions a day that buys is unknown until stage 18. The Architect defines a conservative pre-call estimate, cites the model price's source, and reconciles from response usage. The PRD asks only that "Paused for today" be reachable and that visitors will meet it often (inferred).
- **O3 Cold start and "within a few seconds".** No number is fixed. Is min replicas kept at 0 (the intent says scale to zero) and what waiting state follows? Cold start is measured only at stage 18; if it exceeds "a few seconds" the owner decides at the end review whether a bar or min 1 is wanted (a cost-estimate change).
- **O4 Pause reset.** What resets the daily counter, and in whose time zone? The visitor copy for "Paused for today" depends on it.
- **O5 Limit interplay with the gate (C8.5).** Verification and the gate share the 10-an-hour visitor quota and the daily share; stage 18 must count its own calls in the first batch. QA's plan should cover it.

Not blocking (may ship with the slice):

- **O6 UX Researcher:** how a visitor learns which passages are the "right" ones; wording of the GitHub issue link's pre-filled title (no question text should travel in a URL (inferred)); accessibility of the waiting state.
- **O7 Rate-limit identity:** hashed IP behind Container Apps ingress is a Security Review item at adversarial depth, not a PRD decision.

## 9. Hand-off

To the UX Researcher (stage 3): read this PRD, `intent.md` and `01-scope.md` section 7. Produce visitor journeys and edge cases for every row in section 5, plus accessibility. Do not write layout or final copy (stage 4), and do not choose the kill-switch or cold-start mechanism (Architect).
