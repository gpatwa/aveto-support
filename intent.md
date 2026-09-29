# Intent: Answer "where in Aveto's docs is this?" — retrieval only, no generative model

> **Confirmed by the owner, 2026-09-26.** Drafted by Claude from the
> 2026-09-26 conversation; every line Claude inferred was reviewed and
> confirmed as written. Pass this file to `/agentic-slice intent.md` from a
> session started in this repo.
>
> **Amended and confirmed by the owner, 2026-09-29** (one open question below
> is still open). Eval run 1
> (`runs/docs-retrieval/eval-run-1.txt`) showed keyword retrieval puts a correct
> source in the top 5 for 14 of 24 questions phrased the way users ask; the bar
> is 80%. Two changes follow. One small **local embedding model** is allowed —
> it matches meaning, never generates text, and runs on this machine. And
> because the original 30 questions have now been seen, a **fresh held-out
> set** written after the method is frozen becomes the gate. Everything else
> is unchanged. Drafted by Claude; the owner confirmed it as written.

## What I want

The first working piece of the Aveto support agent: given a question about
Aveto, find the passages in Aveto's own documentation that answer it, and say
exactly where each one came from. No model writes anything — this is the
retrieval step (step 2 of the design in the README) on its own, done well
enough that everything built on top of it later can trust it. A small local
embedding model may help *find* passages by meaning; it never produces text.

## Who it's for

For now, the owner — checking that the agent will look in the right place
before it is ever allowed to write a word. Later, the drafting and checking
steps, which depend entirely on this one returning the right sources.

## Done means

- [ ] A clean checkout installs, type-checks and passes its tests with the
      commands recorded in `.agentic/LOCAL_COMMANDS.md`.
- [ ] An ingest command reads the markdown of `gpatwa/agentic-sdlc-playbook`
      **pinned to commit `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`**, splits it
      into passages by heading, and reports how many files and passages it
      indexed.
- [ ] Running ingest twice on the same commit produces byte-identical output.
- [ ] A retrieve command takes a question and returns up to 5 passages, each
      with its **source file path, heading, and line range** in that commit.
- [ ] A question the docs do not answer returns **"no confident match"**
      rather than the least-bad passages.
- [ ] A committed evaluation set of **at least 20 real questions about Aveto**,
      each labelled with the file(s) that answer it, plus **at least 5 questions
      the docs do not answer**.
- [ ] **The evaluation set is written and labelled by the owner or by QA — not
      by the engineer who builds retrieval — and committed before retrieval is
      tuned.** The git history shows it landing first. An implementer who writes
      its own test questions is grading its own homework: the verifier-wrote-it
      failure this product exists to prevent.
- [ ] **The retrieval method is frozen before the gate is written.** Its
      commit SHA is recorded; only then does the owner write and commit a
      **fresh held-out set** (at least 15 answerable and 5 unanswerable
      questions, labelled like the first set). No role that designs or builds
      retrieval sees it before the run, and the method does not change between
      that commit and the run. It is run once.
- [ ] On the **held-out set**, a correct source appears in the top 5 for **at
      least 80%** of answerable questions, and at least 80% of the unanswerable
      ones return "no confident match". The original set is kept as a
      development set: its score is printed alongside, and does not gate. Both
      scores are printed by a command, and the held-out score is checked in CI.
- [ ] The repo's **first CI workflow** (GitHub Actions) runs install,
      type-check, tests and the evaluation score on every push and pull
      request. A score below the thresholds fails the build, so it gates the
      merge the same way a failing test does.
- [ ] No generative model and no model API is called anywhere. At most **one
      local embedding model** is used, pinned to an exact revision, with every
      file it loads checked against a recorded sha256 before use. It needs
      approval under `HUMAN_APPROVAL_RULES.md` rules 4 and 5 before anything is
      installed or downloaded; without that approval, retrieval stays
      keyword-only.
- [ ] Network access happens only in ingest and CI setup: the pinned docs
      fetch, and — if approved — the pinned model download from Hugging Face
      (`huggingface.co` and its download CDN). Retrieve and eval make no
      network calls at all.
- [ ] The Architect records the stack decision as `docs/adr/0001` and starts
      `docs/ARCHITECTURE.md`; the README explains how to run ingest and
      retrieve against your own docs.

## Must not break

The pack's floor for AI agent products (`project-packs/ai-agent-product.md`)
applies from the first slice, even though no model runs yet:

- Nothing retrieved is ever presented as an answer — this slice returns
  sources, not replies.
- The user can always see where every passage came from.
- The question and the docs never leave the machine: no embeddings API.

## Constraints

- **Python + FastAPI, calling Anthropic's SDK directly — no agent framework**
  (decided by the owner, 2026-09-26). This slice calls no generative model,
  so only the language, structure and test setup are exercised. pytest for tests.
- As few dependencies as possible. If the embedding model is approved, it runs
  on ONNX Runtime and numpy — no PyTorch, no `sentence-transformers`, and no
  model that needs `trust_remote_code`.
- **uv** manages the Python environment, with its lockfile committed, so a
  clean checkout installs the same versions every time. Python 3.12.
- The retrieval source is **configurable** — a repo and a pinned commit —
  with Aveto's docs as the first configured source, since this is a template
  others will point at their own docs.
- The index for this slice is a generated file, not a database. The real
  database arrives with the slice that needs it.
- No Azure, no API key, and no deploy in this slice. Both credentials are
  supplied by the owner in later slices and never handled by an agent.

## Out of scope

- Any generative model call — classification by model, drafting, checking.
- Any hosted embeddings API.
- Fine-tuning, or choosing the model by its score on either eval set.
- **RAGAS or any model-judged evaluation.** Nothing is generated yet, so there
  is nothing for faithfulness scoring to measure. Revisit at the drafting
  slice, deliberately. RAGAS is Python, like this app, so the language is no
  longer an objection; what remains is that every model-judged score is a
  metered call, and that a model judging the checker model needs its own
  answer to "who checks the checker".
- A web UI, sign-in, a database, GitHub integration, Azure.

## Stakes

- [ ] Touches real user data
- [ ] Moves money, or changes billing
- [ ] Irreversible — deletes, sends, or deploys to live users
- [ ] Changes auth, permissions, or a safety control
- [ ] Adds a screen or UI a user will see
- [x] None of the above

With no stakes ticked, this is eligible for the **short path**: no Market
Research, Discovery or UX Research. QA, Security and the Release Gate still run.

## Open questions

- **Does changing INV-5 (network egress) tick "Changes a safety control"?**
  Claude's view: no — the invariant was created in this slice, no user
  depends on it yet, and the change still needs rule 4 approval. Ticking it
  would take the slice off the short path. The owner decides before
  confirming this amendment.

Previously: none. The one question this intent had — who writes
`.agentic/PROJECT_CONTEXT.md` on a greenfield short path — was resolved by the
owner writing it directly and committing it alongside this file.
