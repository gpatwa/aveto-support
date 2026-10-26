# Intent: one polished reference product, the ask-the-docs chat, built, released and shown in public

> **Confirmed by the owner 2026-10-26 ("intent confirmed"), with option (a) for embedding and a hard cap of 2M.**
> Drafted the same day by Claude in the playbook session from the owner's direction
> ("we build one polished reference", "show how this was build, release and deployed"). Confirming the intent is
> not approving the Charter: the Charter is approved by its hash when the run drafts it. Process v2. Pack v29 is
> installed at the start of this slice, so the Charter check covers the roles the run spawns.

## What I want

The live ask-the-docs service becomes a product a person would choose to use, and the way it was built becomes
visible. Today it is a plain form on a developer-styled page. The answering does not change: verbatim passages
with file and line numbers, or "no confident match". Only the experience around it changes.

1. **Answer card.** The quoted passage, a source chip linking to the file in the repository at that line, a copy-link
   control. Nothing on the card is written by a model.
2. **Refusal card.** "The docs do not answer this", the nearest passages (shown as passages, not as an answer), and a
   short hint on rephrasing. This is the screen that carries the position.
3. **Suggested questions**, chosen from the repository's spent evaluation sets: three the docs answer, one they do not.
   A visitor sees an answer and a refusal in the first minute.
4. **Honest waiting.** The service is warmed when the page loads, and the wait shows what is really happening. No
   fake progress bar and no streaming that is not streaming. The first load today takes about 26 seconds.
5. **Resting state.** When the day's allowance is used, a plain "back after midnight UTC" message with the docs
   search still visible. It must not look like an error.
6. **Receipts drawer** ("How this answer was made"): the retrieval and the judge's verdict for this question, and
   links to the Charter and the run record. Shows only what the service already has for this request; stores nothing new.
7. **Quality scorecard** page, built from recorded figures only: cold and warm response time, accessibility and mobile
   checks, test count, open findings, the independent Codex review (including what it found), cost per question,
   and who decided what. A line with no record behind it is not shown.
8. **Counts without content** for the customer evidence: visits, questions asked, answered versus refused, clicks to
   the docs. No question text, no identifiers beyond what the service already keeps.

## Who it's for

About five internal customers and one or two prospects, and the people who read aveto.dev to decide whether
Aveto's way of building is credible. The $10 console limit stays (the owner: it is for internal customers; raise it
only if the budget is exceeded).

## Done means

- [ ] Starts from `main` with pack v29 installed (first use of v29 in a run; the Charter check passes for every role
      in the plan).
- [ ] **Quality bars, fixed before the build and not moved** (the Architect proposes the figures; the owner confirms them
      in the Charter): warm response time and cold-start time reported as measured; the page passes an automated
      accessibility check with no serious issue and works at 375 px wide and by keyboard alone; no open P0 or P1
      finding; the answering behaviour is byte-identical.
- [ ] **Nothing about answering moves.** `git diff main -- aveto_support prompts .claude .agentic` is empty except the
      pack install; retrieval, the judge prompt, the corpus, the verbatim-only rule, INV-1 to INV-5 and the kill switch
      are unchanged. A test proves the answer card contains only text that appears in a listed source. If a safety-text
      change is needed, the run stops and says so.
- [ ] **Embedding decision, stated by the Architect with the reason.** The page is served with
      `frame-ancestors 'none'` today (`aveto_service/pages.py`). Options: (a) keep the service on its own address and show
      it on aveto.dev as a recording plus a button; (b) allow framing by `https://aveto.dev` only. (b) changes a security
      header, so it is a Charter C5 safety-control item, needs the Security Review to cover it, and must name that one
      origin and no wildcard. **Decided by the owner: (a).** The `frame-ancestors 'none'` header does not change in this slice; an embedded panel (b) is a separate later intent if ever wanted.
- [ ] **Tests that fail first** for: the refusal card shows no model-written text; the resting state at the cap; the
      counts record no question text; the receipts drawer shows nothing the service did not already hold.
- [ ] **Code review layer** (tier High: the service handles spend limits and a public page) and a **Security Review at
      standard depth**. **Release Gate at tier 3** because the run deploys. The Codex review (manual, blind, new chat) is
      run by the owner on the pull request and recorded as a trial review.
- [ ] **Deployed** by the run under the Charter's C8.3 (new revision only). **Rollback is a gate, decided by the owner
      2026-10-26 (option 3):** after the deploy the run rolls back to the previous revision, checks that the previous page
      serves and `/health` answers, times it, then rolls forward again and checks the new revision. If the rehearsal fails,
      the release fails: the run keeps the previous revision serving, reports, and stops. The timing is reported as measured.
- [ ] **The build is shown.** The pull request, the Charter, the event-log summary, the end review, cost and time, and
      what the owner decided are linked from the scorecard page. The aveto.dev change (a short section and the link) is
      a separate playbook commit with wording the owner approves first, and the site deploy approved in GitHub's
      production environment.
- [ ] README, `docs/runbooks/public-ask.md` and `.agentic/CURRENT_MVP_STATUS.md` state only recorded figures.

## Must not break

INV-1 to INV-5; the service never shows generated text; no question is stored or logged; the kill switch; the 500
character and ten-an-hour limits; the daily cap; the privacy wording as approved (any change to it goes to the owner).

## Constraints

Python 3.12, uv, no new runtime dependency unless the Architect shows a need and the owner approves it. No new data
processor: Anthropic and Azure only. No third-party scripts, fonts or analytics on the service page (the CSP stays
`'self'`). Counts are computed in the service, not by an outside tool. Public wording is approved by the owner.

## Out of scope

Multi-turn conversation, answers written by a model, accounts or login, a second product, changing the cap, and
decision D1 (making the counters survive a restart). The service stays single-turn.

## Stakes

- [x] Touches real user data (visitors' questions still go to Anthropic and through Azure, unchanged)
- [ ] Moves money, or changes billing
- [x] Irreversible (a redeploy of a public service; rollback is the previous revision or the kill switch)
- [ ] Changes auth, permissions, or a safety control (option (a) chosen: the framing header does not change)
- [x] Adds a screen or UI
- [ ] None of the above

## Setup the owner does once (credentials; an agent never does these)

1. `az login` in the session that runs the slice, if the sign-in has expired.
2. Nothing else: the API key already sits in the Key Vault and the console limit is set (the owner's statement).

## For the Charter (recommended answers; the owner changes any before approving)

| Charter section | Recommended line |
|---|---|
| C2 budget | plan 1.0M; ceiling 1.3M; hard cap 2.0M, set by the owner (a UI slice with design, tests, two reviews, a deploy and a scorecard; the service-accounting fix used 919k) |
| C3 models | the service's judge unchanged (`claude-sonnet-5-5`); build agents as the pack routes them, each with an effort level |
| C4 processors | Anthropic and Microsoft Azure only, as before |
| C5 safety controls | C5.0 none (option (a); the framing header is unchanged) |
| C6 prerequisites | C6.P includes an `Agent(<role>)` allow rule for every role the plan spawns (pack v29); `az account show` succeeds |
| C7 depth | Security standard; Release Gate tier 3 |
| C8.1 | on a failed check: keep the previous revision serving, do not deploy, report, stop |
| C8.2 | push the branch and open a pull request; never merge |
| C8.3 | in `rg-aveto-ask` only: build and push one new image; deploy the Bicep (new revision only); kill switch on or off; rollback: activate the previous revision, rehearsed once after the deploy as a release gate (C8.1 applies if it fails) |
| C8.4 | review |
