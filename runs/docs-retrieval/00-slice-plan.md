# Slice Plan — docs-retrieval

- **Intent:** `runs/docs-retrieval/intent.md`, a byte-identical copy of `intent.md` on `main` at `a3803ca` (owner-confirmed in `dcca4c1`)
- **Eval set:** `evals/retrieval.toml`, owner-committed in `a4e5275` before any retrieval code existed. 24 answerable, 6 unanswerable.
- **Project pack:** `project-packs/ai-agent-product.md`
- **Release tier (proposed):** 2 — a new service with no external effect. No
  deploy, no post, no push by an agent. The Release Manager confirms the tier.
- **Playbook:** `/Users/gopalpatwa/opt/agentic-sdlc-playbook` at `70c095d`. This
  run is driven from a git worktree, where the configured relative path
  `../agentic-sdlc-playbook` does not resolve, so every stage is given the
  absolute path.

## Outcome (one line)

Given a question about Aveto, return up to 5 passages from Aveto's docs at a
pinned commit, each with its file, heading and line range, or "no confident
match". No model is called, and the owner's eval set in CI proves the ≥80% bar.

## Stages

Short path: the intent has checkable "Done means", no open questions, and no
Stakes ticked. Market Research, Discovery (PM), UX Research and UI Design are
skipped (AGENTIC_SDLC "When to compress stages"). The Architect reads the
intent directly. Gates never compress.

| # | Stage | Role | Archetype | Est. | Depth |
|---|-------|------|-----------|------|-------|
| 3 | Scope Review | engineering-manager | review | 100k | standard |
| 7 | Architecture | software-architect | review | 100k | standard |
| 8 | Implementation | backend-architect | build | 130k | standard |
| 9 | QA Evidence (runs the eval set) | qa-evidence | build | 130k | standard |
| 10 | Security Review | security-privacy | review | 100k | standard |
| 11 | Release Gate | release-manager | review | 100k | standard |
| 12 | Post-Launch | post-launch-learning | review | 100k | smoke |

- **The eval set is not authored in this slice.** It is already owner-written
  and committed (`a4e5275`). The engineer **may read `evals/retrieval.toml`
  and must not edit it**. QA runs it at stage 9 and verifies in git history
  that it was not modified after `a4e5275` except by the owner.
- **No Analytics Engineer / Data Analyst.** The slice adds no new measurement
  beyond the eval score, which QA owns.
- **Post-Launch runs at `smoke`.** Nothing launches to users. It records what
  the next slice (drafting) inherits.

## Budget

Σ estimates = 760k, plus 130k headroom (one build stage) = **890k**.

**This is still over the ~600k "slice too big" signal in RUN_ECONOMICS §2.**
The first job of Scope Review is to decide whether to split. The obvious split
is **(a)** ingest, retrieve and the eval score, then **(b)** the CI workflow and
the ADR/ARCHITECTURE/README docs. The EM decides; if it splits, this plan and
the budget are revised and shown to the owner again.

## Success criteria (from intent "Done means")

1. A clean checkout installs, type-checks and passes its tests with the
   commands recorded in `.agentic/LOCAL_COMMANDS.md`.
2. Ingest reads the markdown of `gpatwa/agentic-sdlc-playbook` at
   `3a83b669a8b53dfdff869a1bbe361bdb156e3a13`, splits it into passages by
   heading, and reports file and passage counts.
3. Running ingest twice on the same commit gives byte-identical output.
4. Retrieve returns up to 5 passages, each with source path, heading and line
   range in that commit.
5. An unanswerable question returns "no confident match".
6. The eval set has ≥20 answerable questions labelled with the files that
   answer them, and ≥5 unanswerable ones, committed. **Met at intake:**
   `evals/retrieval.toml` has 24 + 6.
7. The eval set is written by the owner or QA (not the implementer) and lands
   in git history before any retrieval code. **Met at intake:** `a4e5275`,
   owner-authored. QA re-verifies that it is unchanged by the implementer.
8. On that set: a correct source is in the top 5 for ≥80% of answerable
   questions (≥20 of 24), and ≥80% of unanswerable questions return "no
   confident match" (≥5 of 6). A command prints the score and CI checks it.
9. The first GitHub Actions workflow runs install, type-check, tests and the
   eval score on every push and PR. A score below threshold fails the build.
10. No model call anywhere. The only network access is fetching the pinned
    docs.
11. `docs/adr/0001` records the stack. `docs/ARCHITECTURE.md` is started. The
    README explains how to run ingest and retrieve against your own docs.

## Non-goals (from intent "Out of scope")

Any model call, RAGAS or any model-judged eval, a web UI, sign-in, a database,
GitHub integration, Azure, and deploy.

## Constraints (from intent + `.agentic/`)

- Python 3.12, FastAPI, uv with a committed lockfile, pytest, as few
  dependencies as possible. No agent framework.
- The source is configurable (repo + pinned commit), with Aveto's docs first.
- The index is a generated file, not a database.
- No API key, no Azure, no deploy. Credentials are never handled by an agent.
- SAFETY_INVARIANTS INV-1 and INV-2 apply. Retrieval returns sources, never
  answers, and provenance is always visible.
- `evals/retrieval.toml` is read-only to every role except QA, and QA does not
  change questions or labels.

## Gated actions (HUMAN_APPROVAL_RULES scan)

| Action | Rule | Status |
|--------|------|--------|
| Ingest fetches the pinned docs over the network, and CI runs ingest plus the eval score on every push, which adds a network call to the build/test path | 5 ("Adding a network call to the build / test / commit path") | **PENDING — must be approved before Implementation** |
| Pushing the branch or opening a PR so the CI workflow runs | Outward-facing; not done by any agent in this slice | Owner does it, after Release Gate |

Not fired: 1 (nothing is sent or posted), 2 (nothing destroyed), 3 (no
deploy), 4 (the slice adds a CI gate and removes none), 6 (a public docs repo
is not a data processor, and no user data flows anywhere).

## Notes for the owner

- The `evals/retrieval.toml` header now states the 80% unanswerable threshold
  (`17a6ae6`, a comment-only change by the owner; no question, source or label
  changed). It matches criterion 8.
- The installed budget guard (from `677c1e1`) checks only spent ≥ budget. The
  spent + estimate check (pack v8) is not installed mid-slice, so the
  Orchestrator applies rule 6 by hand before every spawn and keeps the
  "Next stage … est." line in STATE.md current.
