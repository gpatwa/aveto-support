# Intent: Land the answerability judge on main, under one Charter

> **Draft, not confirmed.** Drafted 2026-10-16 by Claude in the playbook
> session. The first reference-app run under Aveto Process v2 (pack v20): the
> owner approves **one Charter** at the start and reviews the result at the end;
> nothing else is asked. Nothing in this file is an approval. The decisions
> below go into the Charter the Orchestrator drafts; the owner approves that
> Charter by its hash.

## What I want

Slice 7 (`docs-answerability-2`) built the attended judge step and passed its
held-out gate (24/24 and 16/19), but it closed as an internal candidate that is
**not cleared to land**: its tier 3 Release Gate left eleven items open (T1 to
T11 in `runs/docs-answerability-2/13-release-checklist-tier3.md` on branch
`claude/docs-answerability-2`). I want those items closed, the judge step on
`main` behind a pull request I merge myself, and the run to need me only for the
Charter and the end review.

## Who it's for

The operator who answers docs questions: today `main` has retrieval that never
abstains; after this, `main` has the judge step that says `no confident match`
when the shown passages do not answer the question.

## Done means

- [ ] Starts from branch `claude/docs-answerability-2` (slice 7 as closed), in a
      fresh worktree, with pack v20 installed on `main` first (setup phase).
- [ ] **S5 fixed:** `/aveto-judge-seen` takes no caller text in its `!` shell
      line (a fixed id validated against the committed key, passed so that no
      quote can break out). A hostile-argument test (`r101' ; echo INJECTED ; '`
      and similar) proves no second command runs. The operator-facing
      `/aveto-judge` is unchanged. No other method file changes; the gate results
      of slice 7 stand as recorded and are not re-run.
- [ ] **Rollback rehearsed (T4):** on a throwaway branch, the rollback plan in
      `11c-change-request.md` is executed (revert of the slice commits) and the
      full regression passes on the reverted tree; nothing from the throwaway
      branch is kept.
- [ ] **Monitoring adopted (T5):** the SRE's proposed thresholds, cadence and
      stop rules in `11-monitoring-plan.md` become the adopted ones (the
      Charter records that the owner adopted them as written), and sections 2
      and 5 are copied into `docs/runbooks/answerability-judge.md`.
- [ ] **Known limit stated (T7):** README and `CURRENT_MVP_STATUS.md` say
      plainly that retrieval put the right file in the top five for 19 of 24
      answerable questions on the fifth set (79.2%, under its 80% bar) and that
      16 of 24 ended with the right file shown after judging.
- [ ] **Governance (T10):** an AI Governance review at standard depth of the
      judge step; Data Governance waived with the reason recorded (the program
      stores no user data; the operator's session is covered by records 3 and 6).
- [ ] **Vendor risk (T3):** the Anthropic DPA, plan and retention status, as the
      owner states it in the Charter, recorded in `11b-vendor-risk.md`, with the
      operating rule "public-docs questions only until a DPA is in place" adopted
      or declined as the Charter says.
- [ ] **Records (T2, T9, T11):** the change request decision recorded from the
      Charter; README, `CURRENT_MVP_STATUS.md` and `ARCHITECTURE.md` updated to
      the tier 3 verdict and S6's removal; a `trace.json` with the operator
      handle.
- [ ] **Security re-check** at standard depth of the S5 fix and anything else
      changed since slice 7's review; **Release Gate at tier 3** with every T
      item MET; final-tree `ruff`, `mypy`, `pytest` recorded on the PR head.
- [ ] **End:** the landing branch is pushed and a pull request into `main` is
      opened, with the end review linked. The run never merges.

## Must not break

Every invariant in `.agentic/SAFETY_INVARIANTS.md` as approved in slice 7
(records 5 and 8); the program stays offline; nothing retrieved is presented as
an answer; the judge stays zero-tool on `claude-sonnet-5-5`.

## Constraints

Python 3.12, uv, no new runtime dependency. No metered API, no API key, no
`claude -p`, no terminal client. One session runs the slice (pack v20); no
session the owner must open. No Azure, no deploy, no drafting, no runtime model
client (the set-aside `RELEASE_APPROVAL_PACKET.md` stays out of scope).

## Out of scope

Drafting replies; INV-3; an autonomous product (a runtime model client, GitHub
issue intake, deploy); any change to retrieval or to the judge's method; re-running
any gate.

## Stakes

- [x] Touches real user data (the operator's question goes to Anthropic through
      their own session when they run the judge step; unchanged from slice 7)
- [ ] Moves money, or changes billing
- [ ] Irreversible (a PR is opened; the owner merges)
- [x] Changes auth, permissions, or a safety control (the eval skill's shell line)
- [ ] Adds a screen or UI a user will see
- [ ] None of the above

## For the Charter (recommended answers; the owner changes any before approving)

| Charter section | Recommended line |
|---|---|
| C2 budget | plan 450k; ceiling 600k; hard cap 750k |
| C3 models | `claude-sonnet-5-5` as the judge, the operator's session only (unchanged) |
| C4 processors | Anthropic through the operator's session, as records 3 and 6; **DPA/plan/retention: the owner fills this in** (the Charter cannot pass `charter-check` with it blank) |
| C5 safety controls | `.claude/skills/aveto-judge-seen/` may change only to remove caller text from its shell line; no invariant text changes |
| C6 prerequisites | pack v20 installed on `main` (`install.mjs . --teams`) and committed; a visible symlink to the worktree; each with a dry run |
| C7 depth | Security standard (the re-check); Release Gate tier 3 |
| C8.1 on a failed check | close as not releasable, write the close-out, stop |
| C8.2 at the end | push the landing branch and open a pull request into `main`; never merge, never deploy, never send |
| C8.3 irreversible | the branch push and the PR in C8.2 only |
| T5, T7 | adopt the monitoring proposals as written; accept the retrieval limit and state it |
