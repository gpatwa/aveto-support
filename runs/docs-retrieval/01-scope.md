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
  **meeting the ≥80% eval bar (Done-means item 8)**, the stack ADR, and the
  usage README. This is the retrieval engine: one coherent unit of
  behaviour, verified against the owner's eval set.
- **`docs-retrieval-ci`** — the GitHub Actions workflow that runs install,
  type-check, tests and the eval score on every push/PR, and **enforces**
  the item 8 bar as a required check. This depends on
  `docs-retrieval-core` existing (there is nothing to wire into CI
  otherwise) and is a distinct kind of risk: it is the piece that touches
  the build/test/commit path and is what actually fires
  `HUMAN_APPROVAL_RULES` rule 5.

Splitting this way also separates two different verification concerns
cleanly, which is its own justification independent of the token count:
core retrieval logic (QA runs the score command and verifies the ≥80% bar
is met on the owner's eval set) vs. CI plumbing (QA verifies the workflow
gates correctly on a red score). Bundling both into one Implementation → QA → Security →
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

Stage 3 (QA Evidence) runs the eval score command on
`evals/retrieval.toml` and records the result: a correct source in the top
5 for ≥80% of answerable questions (≥20 of 24) and ≥80% of unanswerable
ones returning "no confident match" (≥5 of 6). Stage 5's Release Gate
fails if the score is below either threshold.

Σ = 560k, 5 stages. Under both RUN_ECONOMICS §2 signals. Budget with one
build stage of headroom = **690k**.

**Owns these Done-means items** (numbering per `00-slice-plan.md` §"Success
criteria"): **1, 2, 3, 4, 5, 6 (verify only — met at intake), 7 (verify
only — met at intake), 8 (meeting the bar; `ci` owns enforcing it), 10,
11.**

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

**Owns these Done-means items:** **8 (enforcement only), 9.** Item 8 is
split plainly: `core` owns *meeting* the ≥80% bar (builds the score
command and passes both thresholds at its own QA/Release Gate);
`docs-retrieval-ci` owns *enforcing* it (makes the same command a required
check on every push/PR so a score below threshold fails the build). The
bar is already met by `core`; `ci` only gates it.

**No Done-means item is owned by both slices (item 8's two parts are
divided as above), and none is dropped.** Item
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

**Approval-1 (rule 5: "adding a network call to the build/test/commit
path") is APPROVED** — see `runs/docs-retrieval/APPROVAL_RECORD-1.md`
(Gopal Patwa, 2026-09-29T00:02:48Z). The owner also accepted the split and
its combined budget, with the ≥80% eval bar moved into `core`.

- **Live fetch is allowed in `ingest` and in CI.** `ingest` fetches
  `gpatwa/agentic-sdlc-playbook` at `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`
  live from GitHub, in local runs and in `docs-retrieval-ci`'s workflow.
  `docs-retrieval-core`'s tests may exercise this fetch directly or via a
  recorded-fixture test double (Architect's call, recorded in the tech
  spec). The approval covers only the read-only fetch of that pinned repo;
  any other network access still needs a new approval.
- **The vendored-snapshot fallback is no longer needed.** Do not vendor a
  snapshot. `ingest` still takes a configurable repo + pinned commit (the
  intent's "source is configurable" constraint).
- **No slice is blocked on approval.** `docs-retrieval-core` Architecture
  may proceed now, and Implementation is unblocked for both slices (ci
  remains sequenced after core's Release Gate).

**Needs the owner:** nothing outstanding. The split and its combined
1,220k budget are accepted.

## What `docs-retrieval-core`'s Architecture stage must also decide

Beyond the normal tech-spec content:

- How the eval score command reports the two thresholds (answerable
  top-5 hits out of 24, unanswerable "no confident match" out of 6) and
  its exit code, so QA can run it at stage 3 and the Release Gate can fail
  on a miss in `core`, and so `ci` can later gate on it unchanged.
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

`docs-retrieval-core` (items 1, 2, 3, 4, 5, 10, 11 to build; 8 to meet;
6, 7 to verify unchanged since intake):

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
8. **Met here.** On `evals/retrieval.toml`, a correct source is in the
   top 5 for ≥80% of answerable questions (≥20 of 24) and ≥80% of
   unanswerable questions return "no confident match" (≥5 of 6). The
   score is printed by a command built in `core`; QA runs it at stage 3
   and `core`'s Release Gate fails if either threshold is missed.
10. No model is called anywhere; the only network access is the approved
    read-only fetch of the pinned docs (Approval-1, APPROVED).
11. `docs/adr/0001` records the stack decision; `docs/ARCHITECTURE.md` is
    started; the README explains how to run `ingest` and `retrieve`
    against your own docs.

`docs-retrieval-ci` (item 8 enforcement, item 9):

8. **Enforcement only.** The bar in item 8 is already met by `core`; here
   the same score command becomes a required check on every push and pull
   request, so a score below either threshold fails the build.
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

None outstanding. Approval-1 is approved (live fetch) and the split with
its combined 1,220k budget is accepted (APPROVAL_RECORD-1.md).

## Amendment 2026-09-29 — file-count ruling for docs-retrieval-core

Rule: EM scope-discipline, "touches more than 10 files for a non-refactor
change." The Architect's tech spec (`02-tech-spec.md`, "Files touched")
lists 18 files and flags the overrun.

**Ruling: ACCEPTED at 18 files. Not waived silently; the rule is applied
by its purpose.** The rule exists so one implementation pass stays
verifiable in one head. Here that holds:
- Only 5 files carry logic (`__main__`, `ingest`, `index`, `search`,
  `evaluate`; ~600–800 lines total), each one concern with one matching
  test file. `__init__.py` is a one-line marker.
- The rest is not reviewed as logic: 1 generated lockfile, 3 greenfield
  scaffolding files any first Python slice needs, 3 docs required by
  Done-means 1 and 11.
- A further split would separate code from its tests, or ingest from the
  retrieve/eval it feeds, leaving neither half checkable against item 8.
  The 10-file rule and the ≤6-stage rule are both already satisfied by the
  split into core and ci; splitting again would add another QA/Security/
  Release pass (~300k+) for no verification benefit.
- Merging `index.py` into `ingest.py` (17 files) is rejected as the
  Architect argued: a worse module boundary to save one file.

**Implementation must change nothing** in the file list, and must not add
files beyond the 18 (plus `runs/docs-retrieval/eval-run-*.txt` artefacts).
Any 19th file is a re-scope back to the EM, not an Implementation call.

**QA should check because of the overrun:** (1) the diff touches exactly
the 18 listed files and nothing else in the product tree; (2) each logic
module has its own test file and the targeted-tests-first run passes per
module before the full suite; (3) `uv.lock` is regenerated from
`pyproject.toml`, not hand-edited, and no dependency exists beyond what the
spec allows; (4) the README, LOCAL_COMMANDS and CURRENT_MVP_STATUS edits
match the commands actually run (no drift between docs and CLI).

## Escalation path

If the Architect hits a blocker (e.g. the eval set's format under-specifies something `retrieve`'s output
contract needs), record it in the Architecture stage's own artefact and
escalate to the EM for a possible re-scope, per the EM brief's
"Escalation" responsibility — do not silently expand this slice's file or
token count past what is recorded here.
