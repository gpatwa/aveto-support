# Intent: Know when the docs don't answer, second attempt: a Sonnet-class judge, registered up front

> **Confirmed 2026-10-12.** Drafted by Claude in the playbook session from
> slice 6's close-out (`docs-answerability`, closed not releasable) and the
> pilots. The owner chose, in the support session, the Sonnet judge and the
> sample integration check as recommended ("let's go with Sonnet and your
> recommendation"), after asking whether to retry Haiku 5.5 (the answer: slice 6
> already was Haiku 5.5, and it is marginal). **This commit is not an approval
> of anything:** rule 4, rule 5 and rule 6 and the budget figures are taken from
> the owner in the Orchestrator's session, in the owner's own words. Start from
> a fresh worktree off `main`.

## What I want

The same product as the first attempt, with what slice 6 taught built in from
the start: a **judge step** the operator runs in their own Claude Code session
on their subscription. It takes what `retrieve` would show, asks a subagent
whether those passages answer the question, and if not the product prints
exactly `no confident match` and no passages. The program stays offline. No
cloud account, no API key, no `claude -p`, nothing unattended.

The one substantive change: **the judge is a Sonnet-class model**, not Haiku.
The other changes are method fixes that slice 6 had to re-register
mid-run and this slice registers before anything runs.

## Why, and the evidence

Slice 6 (`runs/docs-answerability/04-seen-set-check.md`, branch
`claude/aveto-docs-answerability-85eb6d`): the attended Haiku 5.5 judge scored
**Bar 1 20/20, Bar 2 44/56** against a threshold of 45 on the pooled seen sets,
with 5/5 hard negatives and 1 judge error. It did not fail by being wrong about
refusals; it over-abstained on answerable questions (11 misses) and fell to a
format error once. The pilots had Haiku at 47/56, Sonnet 5.5 at 51/56 and
Opus 5.5 at 49/56 on the same sets, and Sonnet matched Opus on the hard
negatives and false premises. The first attempt's intent said "a larger one
only on a measurement"; this is that measurement.

What slice 6 had to fix by re-registering after seeing failures, which this
slice registers up front (`docs/LESSONS.md` L36 to L39):
- The payload is **injected by the harness** (a forked skill with a `!` line),
  never retyped by a model. The harness adds a 150-character prefix; the
  registered layout is "harness prefix, then payload".
- The judge's deny list ends in `mcp__*`, so it is offered 7 tools, not 141
  (first request 11k tokens, not 73k).
- The verdict grammar accepts an optional colon after the token and reads the
  verdict from the **last non-empty line**. Earlier lines are never shown or
  stored.

## What this deliberately is not

- Not a service, not unattended, not scheduled. Attended only; a new intent
  would have to start from Anthropic's current terms.
- Not a replacement for the human: every reply still needs a person (INV-1).
- Not a change to the bars. The bars and the fifth gate set are the ones fixed
  before slice 6 ran. **The slice 6 result is evidence for choosing a model; it
  is not a reason to move a bar.**
- Not a rebuild. The program pieces, skills and tests exist on the slice 6
  branch.

## Owner decisions

For the owner to confirm (recommended answers given):
1. **The judge model: Sonnet 5.5, full model ID pinned** (rule 5: the full ID,
   as in slice 6). *Recommended.* Opus only on a further measurement.
2. **Seen-set integration check: a pre-registered sample, not all 93.** All 20
   unanswerable, plus every second answerable-with-right-file-in-top-5 question
   in key order (28 of 56), 48 spawns. Thresholds scaled before running:
   at least 16 of 20 and at least 23 of 28 (the 80% bar rounded up). The code
   path (injection, grammar, audit, parse) was proven end to end by slice 6's 93
   spawns; what is left to test is the model, which a sample tests.
   *Recommended; the alternative is all 93 at about 1.3M more.*
3. **Budget, typed by the owner at plan confirmation:** the plan, a ceiling,
   and (if the owner adopts the band design, `docs/SESSION_AND_BUDGET_DESIGN.md`)
   a hard cap. Figures in "Budget" below are suggestions in the pack's unit
   (peak context summed per spawn).
4. **Attended operation only** and **Anthropic as the data processor through the
   operator's own session** (rule 6). *Recommended: accept.*

## Done means

- [ ] Starts from `main` (pack v18 or later). Retrieval, ranking, corpus and the
      embedding model are unchanged. The judge code, skills and tests come over
      by cherry-picking slice 6's `37c21d2`; **INV-4/INV-5 words and run
      records do not** (they are re-approved here, below).
- [ ] **The program stays offline.** A test asserts `retrieve`, `eval`,
      `judge-input` and `judge-apply` make no network call and call no model.
- [ ] **Stage 1 measures before it builds:** two one-question Sonnet spawns in
      the real forked-skill configuration, reporting peak, in-equivalent
      tokens and the offered tool count, and a projection with a derived
      ceiling. The owner confirms the budget after reading it.
- [ ] **The judge agent is `claude-sonnet-5-5` (full ID), tools omitted, with
      the deny list ending in `mcp__*`, the match-all deny hook unchanged**, and
      a test that pins the file.
- [ ] **What the judge sees is reported.** Slice 6's probe 2 found the judge's
      context includes the session's `CLAUDE.md`, the user's email and recent
      git status. A read-only check says exactly what a forked judge receives,
      and whether it can be reduced without touching the safety text. Whatever
      leaves the machine is stated in INV-5.
- [ ] **Safety-control text, exact words approved by the owner (rule 4),
      before any code that sends data runs:** INV-4 (a model may judge whether
      shown passages answer the question by returning only a verdict; it never
      produces, selects or alters shown text) and INV-5 (the program makes no
      network call; when the operator runs the judge step, the question, the
      shown passages **and the session context the judge receives, as measured**
      go to the model provider of the operator's session and nowhere else).
- [ ] **Registered up front in the tech spec, not changed after a result:**
      payload layout (harness prefix, then payload), verdict grammar (optional
      colon, last non-empty line), pass thresholds, the sample rule, how a judge
      error is counted (a failure on both bars, reported as its own number).
- [ ] **Seen-set integration check** (sample above) on the product's own path.
      Failing it stops the slice before the fifth set is touched.
- [ ] **Freeze first, then the fifth set:** the method's commit is recorded,
      then the fifth gate set (24 answerable, 24 unanswerable of which 18 are
      hard negatives, plus reserves) is handed over by the support session,
      labels reviewed by a fresh QA spawn (unanswerable ones attacked hardest),
      and a different fresh QA spawn scores it once, one fresh judge spawn per
      question, under the pilots' tool-use audit (any tool use voids the
      batch; one rerun; both reported).
- [ ] **Two bars, fixed, never moved after a result:** abstain correctly on at
      least 80% of unanswerable (20 of 24); do not abstain on at least 80% of
      answerable whose right file retrieval put in the top five. Both must pass.
- [ ] **Reported in the same run:** never-abstain and the best score rule on the
      same set; the end-to-end figure; the over-abstention count; how often the
      judge said ANSWERABLE when the right file was not in the top five; the
      verdicts that differ from the key with the judge's reply held in the run
      record only; usage from `usage.mjs` plus transcript peak-sums for the
      forked judge spawns (`usage.mjs` does not list them).
- [ ] **Security Review at adversarial depth** (prompt injection through
      passages; the judge's tools and the hook as the only barrier for the 7
      remaining harness tools; the verdict parser; no free text in a shell
      command line; what the payload contains) and the **Release Gate**, tier
      2. "Internally releasable, not announced" only if both bars pass.
      A depth below adversarial needs the owner's recorded word.
- [ ] README and `.agentic/CURRENT_MVP_STATUS.md` state only the recorded
      figure and only after the verdict.
- [ ] Everything earlier slices guaranteed still holds.

## Must not break

- Nothing retrieved is presented as an answer; the user can see every
  passage's source; abstaining is never worse than showing a wrong file.
- **The program never sends the question or the docs anywhere.** Only the
  operator's own session does, when the operator runs the judge step, with
  the payload inspectable first.

## Constraints

- Python 3.12, uv, existing structure, no new runtime dependency.
- **No metered API, no API key, no `claude -p`.** The terminal `claude` here
  offers only an API login, so subscription work happens in the desktop app.
- Held-out rules (`project-packs/ai-agent-product.md`): the builder does not
  write the set; freeze, commit the set, run once; labels reviewed first.
- Agent files load when a session starts: any stage that changes `.claude/agents`
  or `.claude/skills` must say so in the plan and ask the owner to start a fresh
  session in the worktree (a session request, `docs/SESSION_AND_BUDGET_DESIGN.md`
  part A).
- One fresh agent per stage; review stages estimated with a tight read list.

## Out of scope

Drafting replies, the INV-3 draft checker, classification; any model beyond the
one judge; any change to retrieval; posting; unattended operation; any
credential; the `docs-retrieval-ci` workflow (any exit 134 fails the build, no
retry wrapper).

## Stakes

- [x] Touches real user data (the question is user text; it goes to the
      operator's model provider when the judge step runs)
- [ ] Moves money, or changes billing
- [ ] Irreversible
- [x] Changes auth, permissions, or a safety control (INV-4, INV-5)
- [ ] Adds a screen or UI
- [ ] None of the above

## Budget (suggestions; the owner types the real figures)

Slice 6 cost about 2.5M against a 950k plan, mostly a 93-spawn check, two
re-registrations and an unmeasured driver. This slice has no build stage and
fixes the method first. Rough plan, peak-sum, from slice 6's measured spawns
(about 14 to 16k each at 11k first request; Sonnet's peak context is similar,
its weight in the usage window is higher and is measured in stage 1):
- Stage 1 measurement, Scope, Architecture (INV words, spec, ADR): about 300k.
- Integration check (48 spawns, sample): about 0.7M.
- Label review, freeze, scoring (48 spawns), Security (adversarial), Release
  Gate (three spawns), docs, close-out: about 1.1M.
- **Plan about 2.1M; ceiling 2.7M; hard cap 3.1M.**
The owner may prefer a smaller slice, or all 93 for the check (add about 0.6M).

## Decisions (recommended; the owner can overturn any)

1. Sonnet 5.5 first; Opus only on a measurement.
2. A label, nothing else; fail closed on every error.
3. The sample integration check, registered before it runs.
4. The fifth set stays unspent until the method is frozen, and is used once.
5. If the owner later wants unattended operation, that is a new intent that
   starts with Anthropic's current terms.
