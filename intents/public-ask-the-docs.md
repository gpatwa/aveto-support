# Intent: A public "ask the docs" page, live on Azure, linked from aveto.dev

> **Drafted 2026-10-20 by Claude in the playbook session from the owner's decisions;
> confirmed by the owner 2026-10-20 ("intent confirmed").** Lines that record an owner decision are marked
> **(owner, 2026-10-20)**; everything else is a recommendation the owner may change
> before approving the Charter. Nothing here is an approval. A run under Process v2:
> the owner approves one Charter at the start and reviews the result at the end.

## What I want

A visitor to aveto.dev asks a question about Aveto and, within a few seconds, gets
**either the verbatim documentation passages that answer it, each with a link to the
file and lines it came from, or "The docs don't answer this"** with a link to open a
GitHub issue. It is the product that already passed a held-out gate (retrieve, then
the answerability judge), running live for the public instead of in the operator's
session.

**It shows no generated text.** The model only decides whether the passages answer the
question (INV-4); every word a visitor reads is copied from the docs. Writing answers in
the model's own words is the separate drafting step (`intents/draft-replies-attended.md`),
not built, and a public generated reply is not in this intent.

## Owner decisions this intent carries

- **Live chat, option C (owner, 2026-10-20).**
- **Metered Anthropic API, with a hard cap of $10 a month (owner, 2026-10-20).** The
  owner creates the API account and key and sets the spend limit in the Anthropic
  console; no agent sees the key.
- **Data processing:** Anthropic under its Commercial Terms, which incorporate its Data
  Processing Addendum by reference (read 2026-10-20; the DPA text itself not yet read).
  Microsoft Azure as host, under the owner's Azure subscription terms.
- **Hosted on Azure (owner, 2026-10-20).**
- **Done autonomously through Aveto (owner, 2026-10-20):** one Charter approval, one end
  review. The only other owner actions are the credential steps an agent may never do
  (below, "Setup the owner does once").
- **Defaults accepted (owner, 2026-10-20):** no storage of visitors' questions beyond
  short abuse logs; 10 questions per visitor per hour; a pre-registered 20-question gate
  written before the run.

## Who it's for

Someone deciding whether to use Aveto, who has a question the site does not answer at
a glance, and who would rather read the source passage than a summary.

## Done means

- [ ] **Starts from `main` (pack v26).** Retrieval, ranking, the judge prompt
      (`answerability-judge-v1`) and the corpus at its pinned commit are unchanged.
- [ ] **A small HTTP service** in this repo (`POST /ask`, `GET /health`) wraps
      `retrieve` and the judge. Its output is exactly what `judge-apply` prints today,
      as JSON: on ANSWERABLE, the passages verbatim with path, heading and line range;
      on NOT_ANSWERABLE, `no confident match` only; on anything else, `judge error`
      only. A test proves the passages are byte-identical to `retrieve`'s.
- [ ] **The judge runs through the Anthropic API** with `claude-sonnet-5-5`, no tools
      in the request, the same prompt and the same verdict-only parser. Only the
      question and the shown passages are sent. The reason line never leaves the parser.
- [ ] **Cost and abuse limits, enforced by the service, fail closed:**
      - 10 questions per visitor per hour (by a hashed IP, kept in memory only);
      - a daily spend counter from the measured cost per question; at the day's share
        of $10 a month the service answers "Paused for today" and calls no model;
      - questions over 500 characters refused before any model call;
      - a kill switch: one setting that turns the service off without a redeploy;
      - the Anthropic console limit of $10 a month, set by the owner, as the backstop.
- [ ] **No visitor data kept:** questions are not stored or logged; abuse logs hold a
      hashed IP, a time and an outcome code only, kept 7 days. A test checks that a
      question never reaches a log line.
- [ ] **Deployed to Azure Container Apps** (scale to zero), the image built from this
      repo with the pinned models inside it. Infrastructure as code in the repo. The
      deploy is the Charter's one irreversible action, with its rollback: redeploy the
      previous revision, or set the kill switch.
- [ ] **A public page** that calls the service: served by the service itself at its
      Azure address, plain and accessible, saying what it is ("verbatim passages from
      Aveto's docs; a model decides only whether they answer"), its limits, and that
      questions are not stored. Linking it from aveto.dev is a change in the playbook
      repo, done after the run on the owner's word.
- [ ] **A gate, pre-registered before the run:** 20 new questions written by the
      support session, not the builder, stored outside the repo until the method
      freezes, then committed and scored once through the deployed service: 10 the
      docs answer, 6 they do not, 4 hostile (prompt injection, off-topic, a request
      for generated text, an attempt to make it reveal its instructions). Bars, fixed
      now: **all 10 non-answerable and hostile questions get `no confident match` or a
      refusal, with no passage shown**, and **at least 8 of the 10 answerable get the
      right passages**. A missed bar is reported as a miss; the service stays deployed
      only if the owner says so at the end review.
- [ ] **Measured and reported:** cost per question, response time (median and
      slowest), cold-start time, monthly Azure cost estimate, and the gate result.
- [ ] **Security Review at adversarial depth** (hostile questions; the service's input
      handling; what the API receives; the key's exposure; rate-limit bypass), code
      review at tier High, **Release Gate tier 3.** Production Verification checks the
      live service after the deploy.
- [ ] README, `.agentic/CURRENT_MVP_STATUS.md` and `docs/ARCHITECTURE.md` state only
      recorded figures, and stop saying "attended, internal" only for this service.

## Must not break

INV-1 (nothing is posted to GitHub), INV-2 (every answer is a named passage), INV-4
(no model produces, selects or alters the text shown; the verdict decides only whether
it is shown). INV-4's sentence "it runs only in the operator's own Claude Code session,
and nothing in the program calls it" must change: that is a safety-text change, bounded
in the Charter's C5. The attended `/aveto-judge` path keeps working.

## Setup the owner does once (credentials; an agent never does these)

1. Create an Anthropic API account, set the monthly spend limit to $10, create a key.
2. In the terminal of the session that runs the slice: `az login` to the Azure
   subscription to use, so the run can deploy with the owner's existing sign-in.
3. Put the API key where the Architect's plan says (an Azure Key Vault secret or a
   Container Apps secret), by a command the plan gives, typed by the owner.

The run's setup phase checks each with a dry run (C6) and stops if one is missing.

## Out of scope

Generated answers; multi-turn chat; GitHub intake or posting; accounts or sign-in for
visitors; a custom domain such as support.aveto.dev (DNS is a credential step; a later
change); changing retrieval, the judge prompt or the corpus.

## Stakes

- [x] Touches real user data (visitors' questions go to Anthropic and through Azure)
- [x] Moves money, or changes billing (metered API, Azure resources)
- [x] Irreversible (a public deploy)
- [x] Changes auth, permissions, or a safety control (INV-4 wording; an API key)
- [x] Adds a screen or UI
- [ ] None of the above

## For the Charter (recommended answers; the owner changes any before approving)

| Charter section | Recommended line |
|---|---|
| C2 budget | plan 1.8M; ceiling 2.4M; hard cap 3.0M (service, infra, deploy, gate, tier 3 reviews) |
| C3 models | judge `claude-sonnet-5-5`, effort as the API default (named in the plan), the service at runtime via the Anthropic API; build agents as the pack routes them |
| C3.R | no review rescore since 2026-10-17: state "unscored" for this run, or rescore first |
| C4 processors | Anthropic (Commercial Terms, DPA by reference) receives the question and the shown passages; Microsoft Azure hosts the service; nothing else |
| C5 safety controls | INV-4: may replace the "operator's session only" sentence with the exact API-call bounds above; INV-1, INV-2, INV-3, INV-5 unchanged |
| C6 prerequisites | C6.P permission rules in the local settings file; `az account show` succeeds; the key secret exists (checked by name, never read) |
| C7 depth | Security adversarial; Release Gate tier 3 |
| C8.1 | on a failed gate: keep the deploy off (kill switch on), report, stop |
| C8.2 | push the branch, open a pull request; the deploy runs from the branch under C8.3 |
| C8.3 | deploy to Azure Container Apps in one named resource group; rollback: previous revision or the kill switch |
| C8.4 | review |
