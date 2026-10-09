# Close-out: docs-abstention

> Post-Launch Learning. Tier 2, standard depth. Sources: `intent.md`, `STATE.md`, `06-release-checklist.md`, `04-security-review.md`, `06b-stale-text-pass.md`, `02-baseline.md`, `03-implementation.md`, slice 4's close-out. No production signals exist (nothing deployed), so every finding cites an artefact; no metric is invented.

## 1. Outcome

**Not releasable.** The two bars were never evaluated: no method was frozen, and the fifth set was never committed, reviewed or scored (06-release-checklist, Verdict).

Delivered:
- A measured baseline on the four seen sets (93 questions): the default path abstains on 0 of 93, and no threshold, margin or combined rule meets the owner's Q2 definition (02-baseline section 5; best pooled min-bar 0.650).
- The INV-4 correction (APPROVAL_RECORD-7): the invariant no longer requires abstention the code never had.
- README, ARCHITECTURE.md and CURRENT_MVP_STATUS.md stale text fixed for the approved lines (06b).
- A recorded negative result for one model: `qnli-electra-base` @ c7dea87c, rule p >= 0.5, nothing tuned, seen-set Bar 1 2/20, Bar 2 55/56 (03-implementation M3). One model, one rule, seen data; not a claim about judges in general.

Not delivered: abstention in any form, and any end-to-end figure. Nothing is pushed, merged or announced. The owner does the push, PR and merge.

## 2. Against "Done means"

| Line | Status | Reason |
|---|---|---|
| Starts from main, corpus/ranking/embedding unchanged | Met | Product diff empty (04-security-review 1, 3) |
| Baseline first, seen sets only | Met | 02-baseline section 5 |
| Model: pinned, hashed, ADR, rule 4/5 | n/a at HEAD | Approvals preceded download; record 5 lapsed unused (record 6); ADR 0007 rejected |
| Freeze, fifth set, run once | Not met | No method commit |
| Two bars on the fifth set | Not met | Never evaluated; seen-set 2/20 and 55/56 are pre-checks, not bar results |
| Diagnostics in the same run | Not met | No scoring run; only the baseline's default-path behaviour |
| `no confident match` output | n/a | Nothing built |
| INV-4 sentence, INV-5 pin | Not met as written; superseded | Record 7 changed INV-4 to say retrieval does not abstain; INV-5 untouched |
| Security and Release Gate once | Met at reduced depth | Security ran standard, PASS with advisories; the Release Gate's own text: "NOT RELEASABLE ... The fifth set was never frozen, reviewed or scored, so the bars were never evaluated" |
| README/status state figure, nothing stronger | Met after the stale-text pass | No whole-pipeline figure exists and none is claimed; 06b applied the status wording |
| Earlier guarantees hold | Met, one open item | Exit 134 occurrence (section 4) |

## 3. What worked, what surprised, what to fold in

**Worked**
- The pre-registered seen-set condition (spec 4.1) stopped the method before the one-shot fifth set was spent (03-implementation M3; Release Gate "Pack and process catches" 2).
- Baseline-first caught stale safety text (INV-4, README, status said retrieval abstains; it never does) and a set-4-only overlap premise: pooled answerable-hit range 0.619-0.800, unanswerable 0.548-0.808, against the intent's 0.63-0.71 (06-release-checklist, catches 1).
- Approvals were recorded as lapsed, not dropped silently (records 5, 6).

**Surprised**
- The seen sets could not support fitting: 4-6 unanswerable questions per set (STATE, Failed condition).
- The Architect's seen-set expectation for the judge did not hold: measured pooled Bar 1 2/20 against the >= 16/20 condition (03-implementation M3). Stated as measured; no cause is claimed.
- Estimates were exceeded (STATE Trace, peak context vs estimate): Baseline 82k vs 60k; Architecture 124k vs 70k, with an infra interruption (HTTP 429); completion pass 63k vs 25k; Implementation 131k vs 130k; Release Gate 63k vs 55k. The owner raised the budget once, 650k to 780k (APPROVAL_RECORD-3).
- Security ran at standard, not the intent's adversarial depth, after the model path stopped. This was an Orchestrator decision recorded in STATE with no approval record (STATE, Process note; Release Gate line 9). The owner can overturn it; the review found the net product diff empty.
- Pack defect: no role owned `.agentic/CURRENT_MVP_STATUS.md`; it cost a stage (06b: write-scope guard blocked it). Fixed in pack v17. A pack upgrade commit (ebd6c6e) landed mid-slice on this branch.

**Fold in**
- A pre-registered seen-set condition is cheap insurance for any one-shot gate; keep it.
- Seen sets this small cannot size a method. Say so before choosing one.

## 4. Carry-forward

- **Slice 4's A1-A5** remain open and unaffected (`runs/docs-retrieval-4/07-close-out.md`).
- **Exit 134, new occurrence:** `eval` on retrieval-heldout-3 aborted after its full report, with a third ONNX session loaded (STATE, Open crash item). Filed against the open crash item; not reproducible from HEAD, code removed. Precondition stands: any 134 fails CI, no retry wrapper.
- **Abstention is still owed.** Open question for the owner: a different method in a new slice, or revising the intent's precondition that nothing that writes text ships before abstention passes. Any new method needs its own rule 4/5 approvals.
- **Fifth set:** unspent and unread, kept outside the repo; use once, for a future frozen method.
- **Judge cache:** 438 MB in gitignored `models/`; reuse needs a new rule 5 approval and hash check, or the owner can delete it (Security A2).
- **Stale lines still left, each needing a new approval (06b):**
  - ARCHITECTURE.md: header L7-11; L106-109; L90 and L113-114 (eval exit rule); L21 (one model); L79-80 and L103 (calibrate tau).
  - CURRENT_MVP_STATUS.md: lines 8-10 (two pinned model files); lines 17-18 (eval exit rule).
- **Four record lines with local absolute paths** (Security A3): use repo-relative paths.
- **Process notes:** Security depth downgrade has no approval record; advisory labels collide (A1-A5 across slices and records), so cite by source; review stages continue to run over estimate, so keep tight read lists.

## 5. Metrics

Spend per STATE Trace: 631k peak-context sum of the 780k budget (80.9%), 8.28M processed, 229 tool calls, excluding this stage. Orchestrator regenerates analytics after this artefact (`runs/ANALYTICS.md`, `runs/dashboard.html`); stages over estimate are listed in section 3.

## Lessons

| Lesson | Evidence | Cost | Enforce at |
|---|---|---|---|
| A pre-registered seen-set pass condition stops a failing method before a one-shot set is spent | 03-implementation M3; spec 4.1 | Implementation pass 131k; fifth set saved | Project-pack held-out rule (nowhere yet as a required step) |
| Baseline on unfixed code catches stale safety text and a mis-scoped premise | 02-baseline; Release Gate catches 1 | Baseline stage 82k | Already in pack (slice 4 lesson); reinforced |
| Unowned status file blocks a stage | 06b (guard blocked `CURRENT_MVP_STATUS.md`) | One stage plus an upgrade commit | Pack defect, fixed in v17; for support session to curate in `docs/LESSONS.md` |
| Depth downgrade mid-slice needs a record | STATE Process note; Release Gate line 9 | None measured; audit gap | Pack defect candidate: no rule requires an approval record for a depth change; for support session |
