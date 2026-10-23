# Intent: make the public service's spend accounting correct (issues #6, #7 and #8)

> **Confirmed by the owner 2026-10-23 ("intent confirmed").** Drafted the same day by Claude in the playbook
> session from the owner's instruction ("plan the fix slice"). Confirming the intent is not approving the
> Charter: the Charter is approved by its hash when the run drafts it. A run under Process v2: the owner
> approves one Charter at the start and reviews the result at the end. **The service code lives on the
> branch of pull request 5, not on `main`: this slice starts only after the owner has merged that
> pull request.**

## What I want

The public ask-the-docs service charges and reserves spend wrongly in three small ways. All three are in
the same few lines and are found by outside review, not by visitors. Fix them together, once, and redeploy.

1. **#6 (P2): retries are not reserved.** Admission reserves the cost of one judge attempt, but the adapter
   can make two. Settlement then charges both, so a retried question can settle above what was reserved
   and the day's cap can be overshot. (`aveto_service/pipeline.py` about line 254; `anthropic_judge.py`
   `MAX_ATTEMPTS = 2`.)
2. **#7 (P3): the last error erases earlier cost.** If the final error's category is "never billed"
   (`status_4xx`, `connection`), `_judged` zeroes the whole charge, including an earlier attempt that may have
   been billed (a 503 followed by a 400 settles at zero). (`pipeline.py` about lines 275 to 291.)
3. **#8 (P3): wrong price.** The counter assumes $3 and $15 per million tokens for `claude-sonnet-5-5`;
   Anthropic's published price and the owner's console bill say **$2 and $10**. The default is in
   `aveto_service/settings.py` lines 15 and 16 and in `infra/main.bicep` lines 31 and 34; the live service
   takes it from the Bicep parameters.

## Why this is a slice and not three edits

It changes code after the tier 3 release gate, in a service that is live and spends real money, and it must be
redeployed. That is a deploy (rule 3), so it needs a Charter. The three fixes share lines, tests and the
redeploy, so one run is cheaper than three.

## Who it's for

The owner, who relies on the service's day limit and on its cost figures, and on the Anthropic console limit
staying the backstop. Visitors notice nothing, except that the service pauses for the day a little later than
before (at the corrected price, about 41 questions a day, not 27).

## Done means

- [ ] Starts from `main` **after pull request 5 is merged**, with pack v28 installed (the Charter line C3.R and
      the event log need it).
- [ ] **#6 fixed, with a test that fails first** (run on the base commit): with a cap equal to one reservation
      and a fake client that returns a retryable error and then succeeds, the service never settles spend above the
      cap because of the retry. Either both possible attempts are reserved up front and the unused part is refunded
      on settlement, or the budget is checked again before a retry is sent; the Architect chooses, and says which
      and why. The test uses the reviewer's figures as a starting point ($0.030000 cap settled $0.039342).
- [ ] **#7 fixed, with a test that fails first:** a 503 followed by a 400 charges the first attempt as a 5xx would
      be charged; a sequence in which every attempt is never-billed still charges zero. The Architect states the rule
      in one sentence.
- [ ] **#8 fixed:** the defaults are 2000 and 10000 nano-dollars per token in `settings.py` and `infra/main.bicep`;
      the `ASK_PRICE_*` override stays; a comment names the source and the date it was read. The tests,
      `docs/runbooks/public-ask.md` and any other place that quotes $0.0118 per question or 27 questions a day are
      updated to the corrected figures, and any figure that is only an estimate says so.
- [ ] **Nothing else moves.** `git diff main -- aveto_support prompts .claude .agentic` is empty; the retrieval,
      the judge prompt, the corpus and every safety invariant are byte-identical. If a safety-text change turns out to
      be needed, the run stops and says so (Charter C5.0 is "none").
- [ ] **A live smoke after the deploy, not a gate:** five fixed questions (three the docs answer, two they do not,
      chosen from the repository's earlier, already-spent evaluation sets and listed in the run's record) are asked
      once through the live service. The service answers or refuses as `retrieve` would; the cost per judged question
      read from `/health` counters is within 15% of **$0.0078**; no question text appears in any log table; the
      kill switch still works (on, then off, timed). Reported as measured, including any miss.
- [ ] **Code review layer, `code-review.md`** (tier High: the files hold spend limits) and a **Security Review at
      standard depth** limited to the accounting code and the new tests (no new input surface). **Release Gate at
      tier 3** because the run deploys. Landing: a pull request the owner merges; the deploy is covered by the
      Charter's C8.3.
- [ ] README, `.agentic/CURRENT_MVP_STATUS.md` and the runbook state only recorded figures; issues #6, #7 and #8 are
      closed by the pull request.

## Must not break

INV-1 to INV-5 as approved; nothing is posted to GitHub; the service never shows generated text; no question is
stored or logged; the kill switch; the 500-character and ten-an-hour limits; the retrieval and judge behaviour.

## Constraints

Python 3.12, uv, no new runtime dependency. No new data processor: Anthropic and Azure only, as in the
approved Charter v2 of the previous run. The live smoke sends five documentation questions, no personal data.

## Out of scope

Decision D1 (making the spend and visitor counters survive a restart; it needs a Charter change and probably a
resource the previous Charter did not name); changing the daily or monthly caps; the page's privacy wording; the
retrieval, the judge, or the corpus; any new feature. **Open for the owner, not included:** the Article 50 and
privacy page tweak (operator name, contact, visitor rights). Say so and it becomes one more bullet here (it is
visible copy and touches the page tests).

## Stakes

- [x] Touches real user data (visitors' questions go to Anthropic and through Azure, unchanged)
- [x] Moves money, or changes billing (it changes how spend is counted and capped)
- [x] Irreversible (a redeploy of a public service; rollback is the previous revision or the kill switch)
- [ ] Changes auth, permissions, or a safety control
- [ ] Adds a screen or UI
- [ ] None of the above

## Setup the owner does once (credentials; an agent never does these)

1. `az login` in the session that runs the slice, if the sign-in has expired.
2. Nothing else: the API key already sits in the Key Vault and the console limit is set (the owner's statement).

## For the Charter (recommended answers; the owner changes any before approving)

| Charter section | Recommended line |
|---|---|
| C2 budget | plan 700k; ceiling 900k; hard cap 1.2M (a short spec, a small fix, fail-first tests, a standard security pass, a deploy and a smoke; the previous run used 2,496k for a whole service) |
| C3 models | the service's judge unchanged: `claude-sonnet-5-5`, effort high, the app at runtime via the Anthropic API; build agents as the pack routes them, each with an effort level |
| C3.R | no review rescore since 2026-10-17: `unscored` for this run, or rescore first |
| C4 processors | Anthropic (Commercial Terms, DPA by reference) receives only the five smoke questions and the passages shown; Microsoft Azure hosts the service; nothing else |
| C5 safety controls | C5.0 none |
| C6 prerequisites | C6.P permission rules in the local settings file; pack v28 installed; `az account show` succeeds; the key secret exists (checked by name, never read) |
| C7 depth | Security standard; Release Gate tier 3 |
| C8.1 | on a failed check: keep the previous revision serving, do not deploy, report, stop |
| C8.2 | push the branch and open a pull request; never merge |
| C8.3 | in `rg-aveto-ask` only: build and push one new image with `az acr build`; deploy the repository's Bicep with `az deployment group create` (new revision only); set the kill switch on or off; rollback: activate the previous revision |
| C8.4 | review |
