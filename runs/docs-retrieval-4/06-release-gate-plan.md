# Release Gate plan and regression bar: docs-retrieval-4

Release Manager, Release Gate step 1 of 3. Written **before any QA run**; no eval and no test was run to write it. Depth: standard. Inputs read: `intent.md`, `00-slice-plan.md`, `01-scope.md` (section 4, risks 2 and 4, plus section 3), `STATE.md`, `04-security-review.md` (verdict and re-check), `runs/docs-retrieval-3-proof/03-close-out.md` (section 2), `docs/RELEASE_GATES.md`, `docs/HUMAN_APPROVAL_RULES.md`, `.agentic/LOCAL_COMMANDS.md` (command and exit codes only). This artefact fixes the plan and the bar. **It gives no verdict**; a different, fresh Release Manager spawn gives it after the QA run.

## 1. Tier and gate checklist

**Tier 2 confirmed (proposed by the plan, confirmed here).** Behavioural change (default ranking, an opt-in on `ingest`, adapter close discipline) with no external effect: no deploy, no send or post, no user-facing screen, no real user data, nothing announced, no change to auth or permissions. Tier 3 is not triggered: nothing in rules 1, 2, 3, 5 or 6 of `HUMAN_APPROVAL_RULES.md` fires (scope review section 3). Rule 4 fired once (the INV-5 sentence) and is recorded in `APPROVAL_RECORD-1.md`. Push, merge and PR are the owner's actions, not the agents'.

Marks: **E** = already evidenced (the later Release Manager reads the cited artefact and confirms, not re-runs); **Q** = to be run by the QA spawn; **n/a** = not applicable, with the reason. Tier 2 requires all implementation, QA and security gates, a release checklist and a rollback plan.

| Stage | Gate | Mark | Evidence or reason |
|-------|------|------|--------------------|
| Scope | Slice fits in one implementation pass | E | `01-scope.md` sections 1 and 2 (file caps, exception for six wording files recorded); `03-implementation.md` for the actual diff against the cap |
| Scope | Non-goals are explicit | E | `00-slice-plan.md` "Non-goals"; `01-scope.md` section 2 "Not to be touched" |
| Discovery | Success criteria are observable | E | `intent.md` "Done means" and `00-slice-plan.md` "Success criteria". The PM stage was skipped by the compressed plan (`01-scope.md` section 5); the intent's checklist stands in |
| Architecture | Adapter boundaries identified | E | `02-tech-spec.md` (the later RM confirms the section exists); Security re-checked the boundary (`04-security-review.md` section 5, "Adapter boundary integrity") |
| Architecture | Audit / feedback / usage events listed | E | `02-tech-spec.md`; Security section 5 "Audit events" (no event store exists; the `ingest` report lines are the record, none weakened) |
| Implementation | Typecheck passes (`uv run mypy`) | E and Q | `03-implementation.md` (regression green); QA re-runs once, offline and cheap, in the full regression below |
| Implementation | Targeted tests pass | E | `03-implementation.md`; Security ran the 27 INV-4 / INV-5 named tests by name |
| Implementation | Full test suite passes | E and Q | Security: 168 passed, 10 deselected, at 4419650 and again at the re-check head; QA re-runs once at the release head |
| Implementation | Build passes | n/a | Python project, no build step. The pack equivalent is `uv sync --locked`, which QA runs as the first step of the full regression |
| Implementation | One commit per task | E | `git log` review by the later RM (the log from 6591bf3 to the release head) |
| Implementation | No new lint warnings (`uv run ruff check`, `git diff --check`) | E and Q | `03-implementation.md`; QA runs `uv run ruff check` once. The later RM runs no command (no Bash); it reads QA's output |
| QA | UI verified in preview | n/a | No UI. Intent Stakes: no screen |
| QA | Local regression command passes | Q | `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest` (`.agentic/LOCAL_COMMANDS.md`). QA reports each step's exit code and the pytest tail line |
| QA | Safety invariants verified | Q and E | Q: QA walks `.agentic/SAFETY_INVARIANTS.md` INV-1 to INV-5 and confirms every name in the enforced-by lists exists and passes (`uv run pytest -q <names>` or `-k`). E: Security's adversarial runtime checks A to E (`04-security-review.md` sections 2 to 4) |
| Security | No secrets / credentials in diff | E | `04-security-review.md` section 1 |
| Security | No PII / sensitive data logged | E | Section 3 (question never leaves stdout; error messages carry paths, never the question) |
| Security | Audit events cover state changes | E | Section 5 "Audit events" |
| Security | Adapter boundary placeholder still throws | E | Section 5 "Adapter boundary integrity" (`PlaceholderReranker.score` still raises) |
| Release | Human approval points satisfied | E | `APPROVAL_RECORD-1.md` (rule 4, INV-5 sentence; Gopal Patwa, 2026-10-03T06:42:53Z; STATE.md Approvals table). Security section 3.1 confirmed the text applied equals the approved words. No other approval point exists at tier 2. The later RM confirms no later `.agentic/` edit; the Security re-check found none since 4419650 |
| Release | Rollback plan exists | E | Tech spec rollback section (the later RM confirms it exists and checks it against the actual diff). Expected shape: nothing is deployed and nothing is pushed or merged, so rollback is dropping or reverting the branch commits since 6591bf3; the reranker remains selectable. The later RM states it in the checklist |
| Release | Release checklist filled | E (later RM) | `templates/RELEASE_CHECKLIST_TEMPLATE.md`, written by the later RM; proposed path `runs/docs-retrieval-4/06-release-checklist.md` |
| Enterprise | All overlay gates (data classification, RoPA, migration, threat model, compliance, subprocessor, AI risk tier, FinOps, SRE, CAB) | n/a | Overlay roles not enabled (project pack `ai-agent-product`, tier 2); no new data, flow, subprocessor or migration; no deploy. The Tech Writer "docs match shipped behaviour" gate: role skipped, wording done in Implementation; the later RM checks the six wording files against the diff |
| Tier 3 only | Dry-run on fixture, audit coverage verified manually, post-launch monitoring plan | n/a | Tier 2. Nothing goes live, so there is nothing to monitor |
| Task-specific | Regression check on the fourth set | Q | Section 2 below |

A gate with missing evidence returns the slice to its owning stage. A skipped gate without a rationale is a blocker; every n/a above carries one.

## 2. The regression bar (fixed now, before the run)

**What is being checked.** That making `file-rrf-v1` the default did not change what that method does. The method and the corpus are unchanged by this slice (`search.py`, `evaluate.py`, every `evals/*.toml`, the index inputs are off-limits and Security confirmed their diffs are empty). The same method on the same set and index should therefore give the same numbers.

**The run.** The QA spawn runs the **default ranking** (`file-rrf-v1`, no `--ranking` flag) on `evals/retrieval-heldout-4.toml` **exactly once**. Prior score of this method on this set: **14/16 (87.5%)**, recorded in `runs/docs-retrieval-3-proof/03-close-out.md` section 2.

**Expected misses (derived from the same table, stated so they can be checked).** The close-out records `file-rerank-v1` at 13/16 with misses f01, f12, f13, and records that the reranker moved f04 in and f01 and f13 out relative to `file-rrf-v1`. So `file-rrf-v1`'s two misses are **f04 and f12**. This is a derivation from the close-out, not a quoted line; QA checks it against `runs/docs-retrieval-3-proof/` raw output if that file exists, without re-running anything. If the derivation proves wrong because of how the close-out was written, the 14/16 count is still the bar and the listed ids are reported as a discrepancy of the record, not a regression.

**No regression (the only outcome that passes the check).** All of:

1. **14 of 16 answerable questions hit (87.5%).**
2. **The two misses are f04 and f12.**
3. **Exit code 0.**
4. The printed `Ranking:` line names `file-rrf-v1`, and the run loaded no reranker (the report line says so or the reranker files line is absent; QA records what it printed).
5. Unchanged inputs, recorded by QA: git HEAD sha; sha256 of `evals/retrieval-heldout-4.toml` (the close-out records `180cfc0b…8aee`); sha256 of `index/docs-index.json`. A different eval-file hash is a stop: the run is not valid and the QA reports without scoring.

**Regression, to be investigated as a DEFECT.** Any other outcome, including:

- fewer than 14 hits, **even if the exit code is 0** (13/16 = 81.2% clears the 80% gate and is still a regression from 14/16);
- 14 hits with different misses, or more than 14 hits (the method is deterministic; a different number means something changed and is not good news);
- exit 1 (below 80%, that is 12 or fewer of 16);
- a changed `Ranking:` line, or any sign the reranker was loaded.

A regression is investigated as a defect in the default path or the ranking code: a changed default, a changed fusion or scoring function, a changed index or a corrupted cache. **It is not resolved by changing the method, by choosing another ranking, by editing a threshold or an eval file, or by writing a new set.** The investigation is a separate defect task for the owning agent; this gate does not carry it out.

**If the result differs from the bar, the QA spawn must:** report the numbers, the misses, the exit code and the file hashes as they are; **not retry, not re-run, not tune, not run the other ranking to explain the difference, not edit anything**; and stop. One run, one result. A re-run is itself a tuning step.

**Exit codes.** For an at-bar result the exit code is **0**. Below 80% the exit code is **1**. Exit 2 or 3 is an input, model-cache or fetch error and the run is invalid: report it, do not retry. **Any exit 134, or any death by signal, is recorded as it is, not retried.** If the full report printed and the score was read from it, the score still stands, and the abort is recorded separately as an occurrence of the open crash item (it would be the first in any default-mode run recorded in slice 4; the Security review and `03-implementation.md` record zero in 660 runs). A run that died before printing its report has no score; QA reports that and the later Release Manager treats the regression check as not completed (the gate fails closed), not as a pass.

**What the bar is not.** It is a regression check, **not a release claim**. This set has now been seen twice; no default method has passed the 80% bar twice on unseen data (Decision 1). The pass or fail of this run does not, by itself, change the "no release claim" decision: a pass does not create a claim, and a fail is a defect to investigate, not a retraction of a claim never made.

## 3. Commands and what QA reports

Run in the repo root, in this order. Output goes to files; QA reads back exit codes, the printed summary lines and the miss ids, and keeps context small (`01-scope.md` risk 2). Proposed result path: `runs/docs-retrieval-4/06-qa-result.md`, raw output in `runs/docs-retrieval-4/06-eval-run-heldout4.txt`.

1. **Record inputs** (no run): `git rev-parse HEAD`; `shasum -a 256 evals/retrieval-heldout-4.toml index/docs-index.json`.
2. **The regression check, once:**
   `uv run python -m aveto_support eval --eval-file evals/retrieval-heldout-4.toml > runs/docs-retrieval-4/06-eval-run-heldout4.txt 2>&1; echo "exit $?" >> runs/docs-retrieval-4/06-eval-run-heldout4.txt`
   (default ranking: no `--ranking`, and no `--index` unless the default path does not resolve, in which case report it and stop.) Compare to section 2 and report: hits of answerable (n of 16), percentage, miss ids, the unanswerable diagnostic as printed, the `Ranking:` line, the exit code, and the three hashes.
3. **Full local regression, once:** `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest -q`. Report each exit code and the pytest summary line (Security recorded 168 passed, 10 deselected). Then the INV-4 and INV-5 enforced-by names from `.agentic/SAFETY_INVARIANTS.md`, run by name once, passed count reported.
4. **Diagnostics, optional and cheap, only after step 2 is written to disk.** QA **may** run the three earlier sets once each with the default ranking: `evals/retrieval.toml` (dev), the second held-out set and the third held-out set (QA finds the second and third file names with Glob in `evals/`; it does not read them for content beyond running them). Command shape as in step 2 with the file changed; one run each, raw output to files. Recorded scores to compare against, from the close-out: dev 19/24 (79.2%; exit 1 by design), second 12/17 (70.6%), third 11/16 (68.8%; below 80%, so exit 1). Report the numbers next to the recorded ones and note any difference. **These are diagnostics only.** Nothing is chosen, tuned or concluded from them; no ranking is switched on their account; a difference is reported, not investigated here. If any of the three would need more than one run, a retry, or anything beyond the command above, QA skips it and says so.
5. **Not to be run by QA:** `--ranking file-rerank-v1` on any set, any new set, `ingest`, any network command, the 20-run crash loops (Implementation already ran them: unfixed 220, fixed 440, zero exit-134, `03-implementation.md`), `pytest -m network`, `pytest -m model`.

QA reports, in one artefact: the inputs (step 1), the step-2 result against the bar in section 2 with the outcome word "at bar" or "differs" and no verdict beyond that, the step-3 results, the step-4 diagnostics (or "not run, reason"), and every anomaly seen, with its exit code.

## 4. Verdict wording rules for the later Release Manager

1. **The only permitted release verdicts are:**
   - **"internally releasable, not announced"**, if every gate in section 1 holds and the section 2 check is at bar (or is a regression that was investigated as a defect, fixed through its owning stage, and re-checked under a fresh plan; this plan does not authorise that path in advance); or
   - **"not releasable"**, with the failing gates and reasons listed and the slice handed back to the owning stage (EM for the list).
   No other wording: not "released", "shipped", "ready for users", "passes the retrieval gate", "meets the 80% bar", "go" with a condition, or any phrase that reads as a release claim. No conditional sign-off: a condition is resolved before the verdict, or the verdict is "not releasable".
2. **README line.** README.md line 3 currently reads "Status: retrieval only; Security Review and Release Gate pending; not announced." It is flipped **only** on the verdict "internally releasable, not announced", and only to reflect that Security Review and the Release Gate have run and what the verdict is, with "not announced" kept and no release claim. README line 7 ("Nothing here is released.") and the figures stated as recorded scores must stay true. On "not releasable", or if the section 2 run did not complete, the line is left unchanged. The later RM edits the line itself only if its tool boundary allows; otherwise it states the exact new line for the Orchestrator. This plan, the QA spawn and the Orchestrator do not flip it.
3. **The crash is NOT REPRODUCED.** It is never written as "fixed", "explained", "resolved" or "no longer occurs". Plain statement with counts: slice 3 saw one abort in eight runs with two sessions loaded (`03-close-out.md` section 4); slice 4 recorded 0 exit-134 in 660 runs (unfixed 220, fixed 440, both modes, on `evals/retrieval.toml` and `retrieve`), and the spec's premise (a session alive at finalisation) was observed false. If the QA run in section 3 shows an exit 134, that is reported next to those counts.
4. **How the open crash item bears on the verdict is the later Release Manager's call**, stated with reasons, not decided here. It must weigh at least: the abort is intermittent and was seen once, on a path (two sessions, reranker) that is no longer the default; it occurs after all output has been written and cannot leak data (Security section 9, risk 1); the close discipline is hygiene with no demonstrated effect; the carry-forward says CI must not start until it is settled ("blocked on the exit-134 fix and a passing release", slice 3 close-out); and the verdict is internal-only with no CI and no announcement. The later RM states whether the open item changes "internally releasable" and why, and records what stays open for `docs-retrieval-ci`.
5. **The intent's criterion "fixed or explained"** (`intent.md`, Done means, third box) is reported plainly as **not met as written**, and met **only** in this sense: "not reproduced, with counts" (the numbers in rule 3). It is not ticked as fixed or as explained. The later RM also reports the other "Done means" items with their evidence and the 20-consecutive-run item as what it is: 20 runs per mode that all exited 0 or 1 (eval exit 1 is the dev set's score, not an abort), none exited 134.
6. **No release claim.** The verdict sentence carries the scope: the code is sound, secure (PASS with advisories A1, A2, A3, A5 carried) and tidy; no claim of retrieval quality is made, because no default method has passed the 80% bar twice on unseen data (Decision 1). The MS MARCO question is recorded as "not applicable to the default path, still open for anyone who opts in".
7. **Approvals.** The later RM records the rule 4 approval by identity and time (Gopal Patwa, 2026-10-03T06:42:53Z) and states that no approval is requested or implied for push, merge, PR, deploy or any announcement: those remain the owner's own actions, taken directly in the session driving the run.
8. **Separation.** The later RM is a fresh spawn that did not write this plan or run the QA step. It confirms the bar in section 2 was unchanged since this file's commit (compare to the committed text) before reading the result; a bar changed after the run voids the check.
