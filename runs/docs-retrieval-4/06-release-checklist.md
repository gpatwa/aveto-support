# Release Checklist: docs-retrieval-4

> Owner: Release Manager Agent, Release Gate step 3 of 3 (the verdict). A fresh spawn: it did not write the plan (step 1) or run QA (step 2).
> Tier: **2**
> Source artefacts: `intent.md`, `00-slice-plan.md`, `01-scope.md`, `02-tech-spec.md`, `03-implementation.md`, `04-security-review.md` (with "Re-check (retry 1)"), `06-release-gate-plan.md`, `06-qa-result.md`, `APPROVAL_RECORD-1.md`, `STATE.md`. No PRD, feature spec or UX spec exists (compressed plan, `01-scope.md` section 5; no UI).
> Depth: standard. This spawn ran no command and read no code or raw crash evidence; it reads the artefacts above.

## Verdict (stated first)

**Internally releasable, not announced.**

The code is sound, secure (Security: PASS with advisories A1, A2, A3, A5 carried) and tidy. **No claim of retrieval quality is made**: no default method has passed the 80% bar twice on unseen data (intent Decision 1). The exit-134 crash item is open and **not reproduced**, not fixed or explained (section 3). Nothing is released, shipped or announced. Reasons are in sections 2 to 5. This is not a conditional sign-off: every open item below is carried forward by name, none is a condition on this verdict.

## 1. Tier classification and the bar

**Tier 2 confirmed.** Behavioural change (default ranking, an opt-in flag on `ingest`, adapter close discipline) with no external effect: no deploy, no send or post, no screen, no real user data, no auth or permission change, nothing announced. `HUMAN_APPROVAL_RULES.md` rules 1, 2, 3, 5 and 6 do not fire. Rule 4 fired once (the INV-5 sentence) and was approved (section 6).

**Bar unchanged check (plan section 4, rule 8).** I have no shell and cannot run `git diff 23d233c HEAD -- runs/docs-retrieval-4/06-release-gate-plan.md`. Substitute evidence, with its limit stated:
- `.git/logs/HEAD` shows the plan committed in `23d233c` ("committed before the run"), followed by only two commits before the QA run: `c6776c0` and `090f30c`, both titled "STATE: ..." (budget notes). QA's HEAD was `090f30c` with a clean working tree at start. The next commits are `70c9ece` (QA result) and `a4dd121` (STATE).
- `06-qa-result.md` section 2 quotes the five bar items in terms identical to plan section 2 (14/16 and 87.5%; misses f04 and f12; exit 0; `Ranking:` naming `file-rrf-v1` with no reranker; hashes, eval file `180cfc0b...8aee`).
- Limit: this is not a byte comparison. A change to the plan inside a commit titled "STATE" cannot be excluded by the log alone. I found no sign of one, and the bar text I read matches what QA tested against. The Orchestrator may run the git diff to close the limit; I do not treat the limit as a reason to void the check.

## 2. Gates (tier 2: all implementation, QA and security gates; release checklist; rollback plan)

### Scope and design

- [x] Slice fits one implementation pass. `01-scope.md` sections 1 and 2; `03-implementation.md`.
- [x] Non-goals explicit. `00-slice-plan.md` "Non-goals"; `01-scope.md` section 2.
- [x] Success criteria observable. `intent.md` "Done means" (stands in for the skipped PM stage). See section 3.
- [x] Adapter boundaries identified. `02-tech-spec.md`; Security section 5 "Adapter boundary integrity".
- [x] Audit / feedback / usage events listed. `02-tech-spec.md`; Security section 5 "Audit events": no event store exists, the `ingest` report lines are the record, none weakened.

### Implementation

- [x] Typecheck passed. QA: `uv run mypy` exit 0, "Success: no issues found in 15 source files" (`06-regress-mypy.txt`).
- [x] Targeted tests passed. Security: 27 INV-4 / INV-5 named tests; QA: all 22 enforced-by names collected, `27 passed, 151 deselected`, exit 0 (`06-regress-inv45.txt`).
- [x] Full test suite passed. QA: `uv run pytest -q` exit 0, `168 passed, 10 deselected` (`06-regress-pytest.txt`), the same count Security recorded at 4419650 and at the re-check head.
- [x] Build passed. n/a for a Python project; the equivalent `uv sync --locked` exit 0, "Audited 16 packages" (`06-regress-sync.txt`).
- [x] One commit per task. `.git/logs/HEAD` shows separate commits for the checkpoint, wording, README, "Implementation complete", Security Review, ADR 0006, the re-check and each Release Gate step. I did not inspect the diff of each commit. Limit noted; the log shape matches the stage plan.
- [x] No new lint warnings. QA: `uv run ruff check` exit 0, "All checks passed!" (`06-regress-ruff.txt`). `git diff --check` was recorded in `03-implementation.md`; I did not re-run it.

### QA

- [x] UI verified in preview: n/a (no UI; intent Stakes). Rationale recorded in plan section 1.
- [x] Local regression command passed. QA ran each step separately: sync, mypy, ruff, pytest all exit 0 (`06-qa-result.md` section 3).
- [x] Safety invariants verified. QA: INV-4 and INV-5 enforced-by names pass. Security: adversarial runtime checks A to E and 6 mutation checks, all caught (`04-security-review.md` sections 2 to 4 and 8). QA did not run the INV-1 to INV-3 names (plan scoped it that way; Security covered them).
- [x] **Regression check on the fourth set: at bar.** See the table below.

### Security

- [x] No secrets / credentials in diff. Security section 1.
- [x] No PII / sensitive data logged. Security section 3 (the question never leaves stdout).
- [x] Audit events cover state changes. Security section 5.
- [x] Adapter boundary placeholder still throws. Security section 5 (`PlaceholderReranker.score` still raises).
- [x] Security verdict: **PASS with advisories** after the retry-1 re-check (R1, the ADR 0006 crash wording, resolved; A4 resolved). 0 blockers, 0 required-fixes. Carried: A1, A2, A3, A5 (section 5 below).

### Release

- [x] Human approval points satisfied (section 6).
- [x] Rollback plan exists (section 7).
- [x] Release checklist filled (this file).

### Tier 3 only: not applicable (tier 2)

Human approval for an external effect, dry-run, manual audit coverage and a post-launch monitoring plan are tier 3 gates. Nothing goes live, so there is nothing to monitor.

### Skipped or n/a gates, with reasons

| Gate | Reason | Approved by |
|------|--------|-------------|
| UI verified in preview | No UI | Plan section 1 (Release Manager, step 1) |
| Build | No build step in this Python project; `uv sync --locked` ran instead | Plan section 1 |
| Enterprise overlay gates (data classification, RoPA, migration, threat model, compliance, subprocessor, AI risk tier, FinOps, SRE, CAB) | Overlay roles not enabled (pack `ai-agent-product`, tier 2); no new data, flow, subprocessor or migration; no deploy | Plan section 1 |
| Tech Writer "docs match shipped behaviour" | Role skipped; wording done in Implementation; Security section 6 checked README, `.agentic/CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md` and the ADRs against the diff, and the retry-1 re-check re-grepped them. I did not re-read the six wording files | Plan section 1; Security section 6 |
| Tier 3 gates | Tier 2 | n/a |
| PM stage (PRD, feature spec) | Compressed plan | `01-scope.md` section 5 |

### Regression check (plan section 2): result against the stated bar

QA ran the default ranking (no `--ranking`) on `evals/retrieval-heldout-4.toml` exactly once. Source: `06-qa-result.md` section 2, raw `06-eval-run-heldout4.txt`.

| Bar item | Required | Observed | Met |
|---|---|---|---|
| 1 | 14 of 16 answerable (87.5%) | 14/16 (87.5%) | yes |
| 2 | Misses are f04 and f12 | MISS f04, f12 only | yes |
| 3 | Exit code 0 | exit 0, `eval: PASS` | yes |
| 4 | `Ranking:` names `file-rrf-v1`, no reranker loaded | `Ranking: file-rrf-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c...`; no reranker line in the 26-line report | yes |
| 5 | Inputs recorded; eval hash matches | eval sha256 `180cfc0b...8aee` matches; index sha256 `f36ef5d4...a756`; HEAD `090f30c` | yes |

**Result: at bar (no regression).** The derivation of the expected misses was checked by QA against the slice-3 raw output (same 14/16, same misses). One run, no retry, nothing edited. Unanswerable diagnostic as printed: 4, not gated.

Diagnostics (one run each, default ranking, nothing chosen from them): dev 19/24 (79.2%, exit 1 by design), second held-out 12/17 (70.6%, exit 1), third held-out 11/16 (68.8%, exit 1). All three equal the recorded scores. These are not a release claim; two of the three are below 80%.

This is a regression check, not a quality claim. At bar means "the default change did not alter what the method does", nothing more.

## 3. Intent "Done means", box by box

1. **Starts from `main` with `claude/docs-retrieval-3` merged.** Met. Merge at 6591bf3 (`02-tech-spec.md` section 9; plan references the log from 6591bf3). Slice 3's `runs/` kept as the record.
2. **`file-rrf-v1` is the default in `retrieve` and `eval`; rerank selectable and off; default loads no reranker and downloads none.** Met. Evidence: QA run 2 printed `Ranking: file-rrf-v1` with no reranker line; Security runtime audit (zero reranker-file opens and zero network events on the default path; `file-rerank-v1` without files fails closed and never downloads; mutants M2 and M6 caught); tests `test_retrieve_default_ranking_is_rrf`, `test_eval_default_ranking_is_rrf`, `test_default_run_loads_no_reranker`.
3. **The shutdown crash is fixed or explained.** **NOT MET as written.** It is met only in this sense: **not reproduced, with counts.**
   - Slice 3 saw one abort (exit 134) in eight runs with two ONNX sessions loaded (`runs/docs-retrieval-3-proof/03-close-out.md` section 4).
   - Slice 4 recorded **0 exit-134 in 660 runs** (unfixed 220, fixed 440, both ranking modes, `evals/retrieval.toml` and `retrieve`; `03-implementation.md`, tallied independently by Security section 9 risk 1).
   - QA added 4 more default-path eval runs and the regression steps: 0 aborts, no signal exit.
   - The Architect's mechanism (a session alive at finalisation) was **observed false** on the unfixed code, both adapters being already dead when `main()` returns. So the crash is not explained, and since it was not reproduced, a fix cannot be shown to work. The close discipline is hygiene with no demonstrated effect.
   - Nothing in this checklist says fixed, explained, resolved or "no longer occurs".
   - The sub-requirement "20 consecutive runs in a row with both ranking modes" is met as what it is: 20 runs per mode, all of which exited 0 or 1 (eval exit 1 is the dev set scoring 79.2%, by design, not an abort), none 134. It is not "exit 0 after a passing run" for the dev-set eval, because that set does not pass.
   - The sub-requirement "argued on general grounds, not found by trial" was satisfied in the sense that the spec argued the fix before any run (`02-tech-spec.md` section 3); the argument's premise then failed observation.
4. **No new gate set written; none re-scored for tuning; the default re-run once on the fourth set; earlier sets as diagnostics; no release claim.** Met. Fourth set run once (section 2); diagnostics reported only; no set written, no threshold or eval file touched (Security confirmed the diffs of `search.py`, `evaluate.py`, `evals/*.toml` are empty). No release claim is made.
5. **Security Review and Release Gate run once, tier 2; verdict "internally releasable, not announced"; MS MARCO recorded as not applicable to the default path and open for opt-in.** Met. Security PASS with advisories (R1 retry used once of a cap of 2); this file is the Release Gate verdict; Security section 3.2, section 9 risk 5 and the ADR 0006 sentence (A4 resolved) record the MS MARCO question as not applicable to the default path and still open for anyone who opts in.
6. **INV-5 keeps naming both models' pins, plus a sentence that the default path fetches only the embedding model.** Met. Rule 4 approved (section 6); Security section 3.1 confirmed the applied text equals the approved words plus the four approved test names, and no `.agentic/` edit since 4419650.
7. **Stale "plain code" wording in `.agentic/PROJECT_CONTEXT.md` and the README status line updated.** Met for the wording done in Implementation (Security section 6 checked it; no release claim found). The README status line still reads "Security Review and Release Gate pending" and is updated by the Orchestrator on this verdict (end of this file).
8. **Everything earlier slices guaranteed still holds** (deterministic ingest, provenance on every passage, no generative model, no network outside ingest and CI setup, every model file hash-checked, retrieve offline). Met. Security sections 2 to 5 (adversarial network and tamper checks, INV-4 verbatim text, placeholder still throws); QA's 168 tests.
9. **Must not break** (nothing retrieved presented as an answer; provenance visible; question and docs never leave the machine). Met on the same evidence. Security found zero network events.

## 4. How the open, not-reproduced crash item bears on the verdict

It is my call, and my call is that **it does not change "internally releasable"**, for these reasons.

- **What the verdict covers.** Internal only: no CI, no deploy, no user, no announcement. The abort can only affect a developer running `eval` or `retrieve` locally.
- **No data or safety effect.** The abort, where it was seen, occurs after all output has been written; it cannot leak data, change a score, or alter an index (Security section 9 risk 1). No safety invariant depends on the exit code.
- **Rate and path.** One abort ever seen, in eight runs, on the slice-3 path (two sessions, reranker on) that is no longer the default. On the new default path (one session, no reranker) there are 0 in the runs recorded for it: the 660 are split across both modes, and QA's 4 default-path eval runs add 4 more. I do not claim the default path is proven clean. I claim it has not been seen to fail.
- **The slice-3 carry-forward** ("CI must not start until the crash is fixed and a release passes") is about CI. This verdict does not start CI. It is handed on as an explicit constraint (section 5), not waved away.
- **What it does change.** The intent box 3 is not met as written, and that is reported plainly above. The owner can decide that the box is a blocker and overrule me; the correct wording for that outcome would be "not releasable". I judge that a not-reproduced intermittent abort after output, with no effect on correctness or safety and no consumer that can be harmed by it, does not make an internal-only cleanup slice unreleasable, whereas claiming it fixed would be untrue and I do not.
- **Not conditional.** The verdict does not depend on the item being later fixed.

## 5. Carry-forward

Open advisories (Security, none blocking; for the EM to fold into a later slice):
- **A1.** INV-5's named offline tests cover only the opt-in ranking with injected adapters; default-path offline behaviour is enforced by unnamed tests. Name a default-path offline test at the next rule 4 touch of INV-5 (needs approval).
- **A2.** `test_ingest_with_reranker_fetches_and_rehashes` overstates what it proves (patches both the fetch and the load). Strengthen it with real cached fixture files; do not rename it (the name is in INV-5).
- **A3.** The reranker hash-mismatch message gives mixed guidance ("run ingest" no longer refetches the reranker). Cosmetic, fails closed.
- **A5.** The crash-evidence scripts hard-code absolute local paths. Parameterise them if reused.
- (A4 resolved by the ADR sentence at the re-check.)

For `docs-retrieval-ci`:
- **Any exit 134 fails the build and is filed as an occurrence of the open crash item. No retry wrapper.** A retry would hide the signal and turn an unexplained abort into a flaky pass.
- The crash stays open (not reproduced) as a precondition to be stated in that slice's plan; this verdict does not clear it.
- CI must not describe a pass of this checklist as a retrieval-quality claim.

For the check-step slice:
- It owns **abstention** ("the docs don't answer this") and the **release claim**. It must exist before anything that writes text for a user ships; it will state what the whole pipeline achieves. No default method has passed the 80% bar twice on unseen data (`file-rrf-v1`: 14/16, 11/16, 12/17).

Other: the MS MARCO licence question is open for anyone who opts in (`ingest --with-reranker`, `--ranking file-rerank-v1`).

## 6. Human approvals

| Action | Rule | Approver | When (UTC) | Record |
|--------|------|----------|-----------|--------|
| INV-5 one-sentence clarification (the default path fetches only the embedding model) | 4 (safety control) | Gopal Patwa, in his own wording | 2026-10-03T06:42:53Z | `runs/docs-retrieval-4/APPROVAL_RECORD-1.md`; request `02-approval-request.md`; STATE.md Approvals |

Security section 3.1 confirmed the text applied equals the approved words; the retry-1 re-check found no `.agentic/` change since 4419650.

**No approval exists, is requested, or is implied for push, merge, PR, deploy or any announcement.** Those are the owner's own actions, taken directly in the session driving the run. A revert of the INV-5 edit (rollback step 3) would itself need a rule 4 yes first.

## 7. Rollback plan

Lifted from `02-tech-spec.md` section 8; checked against what the artefacts say the diff is (no pushes, merges or deploys exist; Security confirmed the index, `search.py`, `evaluate.py` and eval-file diffs are empty). I did not read the code diff.

1. `git revert` the Implementation commit(s) on `claude/docs-retrieval-4` (from 6591bf3). Nothing has been pushed or merged, so dropping the branch is equally valid.
2. No index rebuild: the index bytes do not change (sha256 `f36ef5d4...` stable across the slice's inputs). Cached reranker files in `models/` stay in place; they are hash-checked before every use.
3. After a revert, the old `ingest` fetches the reranker unconditionally again, so INV-5's added sentence would be false. **Revert the INV-5 edit with the code.** That is a safety-control edit, so the reverting session takes a rule 4 yes from the owner first. Check: `pytest` green and `retrieve` prints `Ranking: file-rerank-v1` by default again.
4. Partial rollback without code: pass `--ranking file-rerank-v1` after `ingest --with-reranker`.

## 8. Post-launch monitoring

Tier 2, nothing goes live: not applicable.

## 9. Decision

- Verdict: **internally releasable, not announced.**
- The template's "Go: slice lands now" box is not ticked, because "landing" (push, merge, PR) is the owner's act and is not approved. No-go box: not ticked.
- No gate is failed and none is returned to an owning stage.
- Limits of this verdict, stated once: bar-unchanged checked from the git log and QA's quotes rather than a git diff; the per-commit and wording-file contents were taken from Security's review, not re-read; the crash item is open.

## Hand off

To the Orchestrator for Close-out (Post-Launch Learning Agent, 25k), after the budget re-check in STATE.md. The Orchestrator commits this file and STATE.md with the trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## README line for the Orchestrator to apply

README.md line 3 currently reads:

`> **Status: retrieval only; Security Review and Release Gate pending; not announced.** It lists`

Replace it with exactly (the trailing "It lists" continues to line 4 as before):

`> **Status: retrieval only; Security Review and Release Gate run, internally releasable, not announced.** It lists`

Check after applying: line 7's "Nothing here is released." stays; the 14/16, 11/16 and 12/17 figures stay stated as recorded scores; no word such as released, shipped, ready or passes is added; the line rewrapping, if any, must keep "not announced".
