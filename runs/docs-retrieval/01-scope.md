# Agent Handoff — Scope Review → Software Architect

> Slice: docs-retrieval (split into docs-retrieval-core and docs-retrieval-ci — see Decision)
> From: engineering-manager (Scope Review)
> To: software-architect (Architecture, first stage of docs-retrieval-core)
> Date: 2026-09-27

## Decision: split, not keep as one slice

The confirmed plan (`runs/docs-retrieval/00-slice-plan.md`) totals **7 stages
and Σ760k tokens (890k with headroom)**. Both numbers are over the
RUN_ECONOMICS §2 signal: *"A slice that needs more than **6 stages** or
**~600k** is a signal the slice is too big — send it back to the EM before
spending, not after."* Per the EM brief's scope-discipline rules, that
signal is grounds to split (it is the direct token-budget analogue of the
">10 files for a non-refactor change" rule — both exist to keep one
implementation pass verifiable in one head).

The plan itself proposed the seam, and it is the right one: the
Done-means items split cleanly along a real dependency edge, not an
arbitrary token cut.

- **`docs-retrieval-core`** — ingest, retrieve, the eval score command,
  the stack ADR, and the usage README. This is the retrieval engine: one
  coherent unit of behaviour, testable entirely offline once a docs
  snapshot exists.
- **`docs-retrieval-ci`** — the GitHub Actions workflow that runs install,
  type-check, tests and the eval score on every push/PR. This depends on
  `docs-retrieval-core` existing (there is nothing to wire into CI
  otherwise) and is a distinct kind of risk: it is the piece that touches
  the build/test/commit path and is what actually fires
  `HUMAN_APPROVAL_RULES` rule 5.

Splitting this way also separates two different verification concerns
cleanly, which is its own justification independent of the token count:
core retrieval logic (QA verifies precision/recall against the owner's
eval set) vs. CI plumbing (QA verifies the workflow gates correctly on a
red score). Bundling both into one Implementation → QA → Security →
Release pass would have made a QA finding in one hard to disentangle from
the other.

**Sequence:** `docs-retrieval-core` → `docs-retrieval-ci`. Strict
dependency: `docs-retrieval-ci` cannot start Implementation until
`docs-retrieval-core`'s Release Gate has passed (it wires and tests
against the real `ingest`/`retrieve`/score commands, not stubs).

This Scope Review stage (already spent) is shared — it is not repeated for
`docs-retrieval-ci`; that slice's own handoff (written when `core` reaches
its Release Gate) inherits this decision rather than re-litigating it.

## Per-slice stages, tier, budget

### `docs-retrieval-core`

| # | Stage | Role | Archetype | Est. | Depth |
|---|-------|------|-----------|------|-------|
| 1 | Architecture | software-architect | review | 100k | standard |
| 2 | Implementation | backend-architect | build | 130k | standard |
| 3 | QA Evidence | qa-evidence | build | 130k | standard |
| 4 | Security Review | security-privacy | review | 100k | standard |
| 5 | Release Gate | release-manager | review | 100k | standard |

Σ = 560k, 5 stages. Under both RUN_ECONOMICS §2 signals. Budget with one
build stage of headroom = **690k**.

**Owns these Done-means items** (numbering per `00-slice-plan.md` §"Success
criteria"): **1, 2, 3, 4, 5, 6 (verify only — met at intake), 7 (verify
only — met at intake), 10, 11.**

### `docs-retrieval-ci`

| # | Stage | Role | Archetype | Est. | Depth |
|---|-------|------|-----------|------|-------|
| 1 | Implementation | backend-architect | build | 130k | standard |
| 2 | QA Evidence | qa-evidence | build | 130k | standard |
| 3 | Security Review | security-privacy | review | 100k | standard |
| 4 | Release Gate | release-manager | review | 100k | standard |
| 5 | Post-Launch | post-launch-learning | review | 100k | smoke |

Σ = 560k, 5 stages. Under both signals. Budget with headroom = **690k**.

No separate Architecture stage: `docs-retrieval-core`'s Architect writes
the tech spec for the whole feature area, including how CI will invoke
`ingest`/`retrieve`/the score command (this is stated as a requirement
below, in "What `docs-retrieval-core`'s Architecture stage must also
decide"). Wiring an existing, specified command into a GitHub Actions
workflow is implementation, not a fresh architecture decision — consistent
with the EM brief's "internal refactor" compression pattern (Architect
stub only; here the stub is folded into `core`'s tech spec rather than
repeated).

**Owns these Done-means items:** **8, 9.** (`core` builds and locally
verifies the score command that item 8 needs; `docs-retrieval-ci` is what
actually closes item 8, by making the score a required CI check — the
same command, gated instead of just printed.)

**No Done-means item is owned by both slices, and none is dropped.** Item
1 ("clean checkout installs, type-checks, passes tests") is built by
`core` and re-checked (not re-owned) by `ci`'s QA stage as a regression
guard — adding the workflow must not break the local commands it wraps.

Combined total across both slices: **1,120k**, plus this Scope Review's
already-spent 100k = **1,220k** — higher than the original single-slice
890k estimate. That is the expected cost of splitting (duplicated
QA/Security/Release Gate passes) and is the correct trade for keeping each
implementation pass independently verifiable and within the per-slice
budget signal. Flagging this now rather than after both slices spend: if
the owner would rather accept the single-slice overrun than pay the
split's overhead, that is a call for the owner, not one the EM makes
silently — noted under "Needs the owner" below.

## Release tier and gates

**Tier 2 confirmed for both slices** (Release Manager still gives the
final confirmation at each slice's Release Gate, per
`docs/RELEASE_GATES.md`): a new service and, for `ci`, a CI workflow, with
no external effect — no deploy, no post, no push by an agent, and (per
`docs/RELEASE_GATES.md` Tier 3 examples) a read-only fetch of one public
repo at a pinned commit is not "an integration with a third party" in the
credentialed-vendor sense that trips Tier 3. Gates that apply to both, per
the Tier 2 row of `RELEASE_GATES.md`: all Implementation gates
(typecheck, targeted + full tests, build, one commit per task, no new lint
warnings), all QA gates (safety invariants checklist — INV-1/INV-2 apply
even though no model runs yet, since retrieval-returns-sources-not-answers
is exactly what INV-2 requires), all Security gates (no secrets/PII in
diff, no new network surface beyond the approved fetch, adapter boundary
placeholder still throws — n/a here, no model adapter exists yet, mark
n/a with that reason), Release checklist and rollback plan.
`docs-retrieval-ci` additionally exercises the "eval-gated merge" pattern
named in `RELEASE_GATES.md` ("Enforcing gates in CI") — that pattern is
the entire point of that slice.

## Approval points

`APPROVAL_REQUEST-1.md` (rule 5: "adding a network call to the
build/test/commit path") is **PENDING**. Per the confirmed plan and
`STATE.md`, it gates **Implementation**, not Scope Review or Architecture.
Concretely, that means:

- **`docs-retrieval-core` Architecture may proceed now** (this handoff)
  regardless of the answer — but the tech spec must design for both
  outcomes, because the answer changes the ingest module's default I/O
  path, not just a downstream wiring choice.
- **`docs-retrieval-core` Implementation is blocked until Approval-1 is
  answered.** The approval request explicitly names "the ingest command,
  run locally" as one of the two triggering points, alongside CI — so
  writing `ingest`'s network-fetch path counts, not just wiring it into
  CI. Do not start Implementation on the strength of this handoff alone.
- **`docs-retrieval-ci` Implementation is blocked on the same approval**
  (it is the workflow itself that runs ingest automatically on every
  push).

**How each answer changes scope:**

- **Approved (live fetch allowed):** `ingest` fetches
  `gpatwa/agentic-sdlc-playbook` at `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`
  live from GitHub, in both local runs and in `docs-retrieval-ci`'s
  workflow. `docs-retrieval-core`'s own test suite may exercise this fetch
  directly (or via a recorded-fixture/VCR-style test double — Architect's
  call, recorded in the tech spec) since network access is the approved,
  intended behaviour. Simpler design; CI availability is coupled to
  GitHub's.
- **Denied:** per APPROVAL_REQUEST-1's own "what is reversible if
  denied" — vendor a snapshot of the pinned commit's markdown into the
  repo as fixture data. `docs-retrieval-core`'s tests and
  `docs-retrieval-ci`'s workflow both run offline against that snapshot.
  `ingest` still supports fetching a live repo+commit (the intent's
  "source is configurable" constraint requires this as a capability), but
  it is exercised as a manual, human-run command outside the automated
  test/CI path, not invoked by anything that runs on every push. This adds
  one committed fixture file to `docs-retrieval-core`'s file count and one
  "keep the snapshot in sync with the pin" note to
  `docs/ARCHITECTURE.md`; it does not change any Done-means item's
  wording (item 10, "the only network access is fetching the pinned
  docs," stays true either way — the manual command is still that fetch).

**Needs the owner, before `docs-retrieval-core` Implementation can start:**
1. Answer APPROVAL_REQUEST-1 (fetch vs. vendored snapshot).
2. Confirm accepting the split's higher combined budget (1,220k across
   both slices, vs. the original single-slice 890k) — or say if the
   single-slice overrun is preferred instead. Recorded here as a decision
   the EM surfaces per RUN_ECONOMICS §2 ("stop and ask the human with the
   numbers"), not one the EM makes silently.

## What `docs-retrieval-core`'s Architecture stage must also decide

Beyond the normal tech-spec content:

- Which of the two Approval-1 outcomes the design supports as default,
  and how the other is still reachable (config flag, not a second code
  path) — write this so Implementation does not block a second time once
  the owner answers.
- How `docs-retrieval-ci` will later invoke `ingest`/`retrieve`/the score
  command (CLI entry points, exit codes, where the score is printed so CI
  can parse/threshold it) — record this in `docs/ARCHITECTURE.md` even
  though building the workflow itself is `docs-retrieval-ci`'s job.
- `docs/adr/0001` records the stack decision already made by the owner
  (Python + FastAPI, calling Anthropic's SDK directly — no agent
  framework; recorded in `.agentic/PROJECT_CONTEXT.md` "Decisions already
  made"), not a new decision to deliberate.

## Minimal context bundle (for the Architect)

Files to read — not the whole repo:

- `runs/docs-retrieval/intent.md` — source of truth for "Done means."
- `runs/docs-retrieval/00-slice-plan.md` — confirmed plan, constraints,
  gated-actions scan.
- `runs/docs-retrieval/01-scope.md` — this file (the split, tier,
  approval status, and what the Architecture stage must decide).
- `runs/docs-retrieval/APPROVAL_REQUEST-1.md` — the pending approval and
  its two named outcomes.
- `.agentic/PROJECT_CONTEXT.md` — stack decision, stance ("grounded or
  silent"), stage.
- `.agentic/SAFETY_INVARIANTS.md` — INV-1, INV-2 apply.
- `.agentic/LOCAL_COMMANDS.md` — where the Architect records the install /
  type-check / test / ingest / retrieve / score commands.
- `evals/retrieval.toml` — **read-only**, do not edit. Read to learn the
  eval set's shape (question/label format) so `retrieve`'s output
  contract matches what QA will score against.
- `/Users/gopalpatwa/opt/agentic-sdlc-playbook/project-packs/ai-agent-product.md`
  (absolute path — this worktree's relative playbook path does not
  resolve) — deterministic-first, no model in this slice.

No commands exist yet (greenfield); the Architect defines them in
`.agentic/LOCAL_COMMANDS.md`.

## Acceptance criteria (from intent "Done means", split by slice)

`docs-retrieval-core` (items 1, 2, 3, 4, 5, 10, 11 to build; 6, 7 to
verify unchanged since intake):

1. A clean checkout installs, type-checks and passes tests via
   `.agentic/LOCAL_COMMANDS.md`.
2. `ingest` reads the markdown of `gpatwa/agentic-sdlc-playbook` pinned to
   `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`, splits it into passages by
   heading, and reports file and passage counts.
3. Running `ingest` twice on the same commit produces byte-identical
   output.
4. `retrieve` takes a question and returns up to 5 passages, each with
   source file path, heading, and line range.
5. A question the docs do not answer returns "no confident match."
6. **Met at intake** — `evals/retrieval.toml` has 24 answerable + 6
   unanswerable questions, owner-labelled. QA re-verifies it is unchanged
   from `a4e5275` except by the owner.
7. **Met at intake** — the eval set landed (`a4e5275`) before any
   retrieval code. QA re-verifies via git history.
10. No model is called anywhere; the only network access is fetching the
    pinned docs (see "Approval points" for how this is satisfied under
    either Approval-1 outcome).
11. `docs/adr/0001` records the stack decision; `docs/ARCHITECTURE.md` is
    started; the README explains how to run `ingest` and `retrieve`
    against your own docs.

`docs-retrieval-ci` (items 8, 9):

8. On the owner's eval set, a correct source is in the top 5 for ≥80% of
   answerable questions (≥20 of 24) and ≥80% of unanswerable questions
   return "no confident match" (≥5 of 6). The score is printed by a
   command (built in `core`) **and checked in CI** (built here) — a score
   below threshold fails the build.
9. The repo's first GitHub Actions workflow runs install, type-check,
   tests and the eval score on every push and pull request.

## Constraints inherited from prior stages

- Python 3.12, FastAPI, uv with a committed lockfile, pytest, as few
  dependencies as possible, no agent framework.
- The retrieval source is configurable (repo + pinned commit); Aveto's
  docs are the first configured source.
- The index is a generated file, not a database.
- No Azure, no API key, no deploy in this slice; credentials are never
  handled by an agent.
- `evals/retrieval.toml` is read-only to every role except QA; QA does
  not change questions or labels, only verifies them unchanged.
- SAFETY_INVARIANTS INV-1 and INV-2 apply: retrieval returns sources, not
  answers, and provenance is always visible.

## Out of scope reminder

Neither slice includes: any model call (classification, drafting,
checking), RAGAS or any model-judged evaluation, a web UI, sign-in, a
database, GitHub integration beyond the read-only pinned fetch, Azure, or
deploy. `docs-retrieval-ci` specifically does not include a deploy step or
a post-deploy smoke check — there is nothing running that a smoke check
would target.

## Open questions for the next agent

- [ ] Fetch vs. vendored snapshot (APPROVAL_REQUEST-1) — owner, before
      Implementation starts on either slice.
- [ ] Accept the split's combined 1,220k budget vs. the original
      single-slice 890k estimate — owner, alongside the approval answer.

## Escalation path

If the Architect hits a blocker other than the two open questions above
(e.g. the eval set's format under-specifies something `retrieve`'s output
contract needs), record it in the Architecture stage's own artefact and
escalate to the EM for a possible re-scope, per the EM brief's
"Escalation" responsibility — do not silently expand this slice's file or
token count past what is recorded here.
