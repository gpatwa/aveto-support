# Intent: after a visitor asks, the result is the first thing they see

> **DRAFT 2026-10-27, not confirmed.** Drafted by Claude in the playbook session from the owner's note that the
> live app is not clear and easy to understand, then checked in a real browser (below). Confirming the intent is not
> approving the Charter: the Charter is approved by its hash when the run drafts it. Process v2, the first run under
> **pack v30** (installed on main, `a0af0f8`). The owner asked for as few questions as possible: every open choice
> below has a default, so one "intent confirmed" starts the slice.

## What is wrong, measured

Checked on the live app (revision 0000011) in a 1280 by 800 window, after asking a question: the page scrolls to
`#result` and focuses it, but the result's heading lands at **616 px of 800**, the bottom fifth of the screen, so
none of the quoted passage is visible without scrolling. Above the result sit the six-bullet "What to expect"
list, the four suggested questions and the question box (about 1,150 px). A visitor who has just pressed Ask sees
the page they left, not the answer.

## What I want

1. **The result starts at the top of the screen after Ask**, on desktop and at phone width, and keeps keyboard
   focus (so a screen reader and keyboard user land on it too). No motion that cannot be turned off.
2. **On a result page, the result comes first.** The order becomes: title and the one-line statement that nothing is
   written by a model, the question box (so a second question is easy), the result, then the "What to expect" block
   and the suggestions. **The home page, which every visitor sees before their first question, does not change.**
3. **No wording changes.** "What to expect", the privacy and limits lines and the page's other strings stay
   byte-identical; only their position on a result page moves. If the Architect thinks a string must change, the
   run stops and says so (the owner approves public wording).
4. **Phone width (375 px):** the result heading is within the top quarter of the screen after Ask.

## Who it's for

The five internal customers and the one or two prospects, and anyone who opens the live app from aveto.dev.

## Done means

- [ ] Starts from `main` with pack v30 installed. **First run under v30:** the guard follows this worktree and
      the hard cap below; the end review counts every guard prompt the owner answered (target 0 questions after the
      Charter) and lists any permission prompt that actually appeared.
- [ ] **Measured, not asserted:** in the browser pane at 1280 by 800 and 375 by 667, after asking one answered and one
      refused question on the local build, the result heading's top is within the top 25% of the viewport; before
      and after figures are recorded next to the 616 px above.
- [ ] **Nothing about answering moves.** `git diff main -- aveto_support prompts .claude .agentic` is empty except
      the pack install; the 39-case `/ask` golden file is byte-equal; the response headers (including
      `frame-ancestors 'none'`) and the privacy and limits strings are byte-identical; INV-1 to INV-5 unchanged.
- [ ] Tests that fail first: on a result page the question box precedes the result and the expectations follow it; on
      the home page the order is unchanged; every previously tested string still appears; keyboard focus lands on the
      result.
- [ ] Accessibility: axe-core, zero serious or critical on the home and result views (answer, refusal, resting);
      keyboard-only flow; reading order matches the visual order.
- [ ] **Code review layer** (tier standard; the change is presentation only) and a **Security Review at smoke depth**
      (no new route, no new input, no header change; confirm that). **Release Gate tier 3** because the run deploys,
      with the **rollback rehearsal as a release gate** as in the last slice. Landing: a pull request the owner
      merges; the owner runs the Codex review. The aveto.dev screenshots are retaken after the deploy (a separate
      playbook commit with wording the owner approves).
- [ ] README, runbook and `.agentic/CURRENT_MVP_STATUS.md` state only recorded figures; the slice's `STATE.md` is set
      to `done` when the pull request opens.

## Must not break

INV-1 to INV-5; the service never shows generated text; no question is stored or logged; the kill switch; the 500
character and ten-an-hour limits; the daily cap; the privacy and limits wording; the answer and refusal behaviour.

## Constraints

Python 3.12, uv, no new runtime dependency, no third-party script, font or analytics (the CSP stays `'self'`). No
new data processor: Anthropic and Azure only. Public wording is approved by the owner.

## Out of scope

Any wording change, multi-turn answers, an embedded panel (framing stays off), D1 (counters surviving a restart),
the cap, new routes, and the deferred `/warm` retry bound.

## Stakes

- [x] Touches real user data (visitors' questions still go to Anthropic and through Azure, unchanged)
- [ ] Moves money, or changes billing
- [x] Irreversible (a redeploy of a public service; rollback is the previous revision or the kill switch)
- [ ] Changes auth, permissions, or a safety control
- [x] Adds a screen or UI
- [ ] None of the above

## Setup the owner does once (credentials; an agent never does these)

1. `az login` in the session that runs the slice, if the sign-in has expired.
2. Nothing else.

## For the Charter (defaults; the owner changes any before approving)

| Charter section | Recommended line |
|---|---|
| C2 budget | **one number: hard cap 800k** (C2.3); ceiling 720k (about 90%); plan 400k (a presentation change, fail-first tests, two reviews, a deploy with the rollback gate; the last UI slice's backend and frontend stages took about 440k together and this one touches only ordering and scrolling). One notice when the projection passes the ceiling; the hard cap is copied into STATE.md. |
| C3 models | the service's judge unchanged; build agents as the pack routes them, each with an effort level |
| C4 processors | Anthropic and Microsoft Azure only, as before |
| C5 safety controls | C5.0 none |
| C6 prerequisites | C6.P an `Agent(<role>)` rule for every role the plan spawns (v29); `az account show` succeeds |
| C7 depth | Security smoke; Release Gate tier 3 |
| C8.1 | on a failed check, including the rollback rehearsal: keep the previous revision serving, do not deploy, report, stop |
| C8.2 | push the branch and open a pull request; never merge |
| C8.3 | in `rg-aveto-ask` only: one image build and push; deploy the Bicep (new revision only); kill switch on or off; rollback: activate the previous revision, rehearsed once after the deploy as a release gate |
| C8.4 | review |
