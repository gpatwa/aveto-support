# Release Checklist — docs-abstention

> Owner: Release Manager Agent (standard depth, single spawn)
> Tier: 2 (confirmed, see rationale)
> Source artefacts: `intent.md`, `STATE.md`, `02-baseline.md`, `03-implementation.md`, `04-security-review.md`, `APPROVAL_RECORD-5.md`, `-6.md`, `-7.md`. The Architect's `02-tech-spec.md` and ADR 0007 were not re-read (not on this stage's read list). Range under review: `0dfd433` (main) .. `fe5cf10` (HEAD), from the worktree reflog: intake, scope, baseline, spec, approvals, candidate code 479f82a, its revert f1a96ad, the option-1 record, the INV-4 correction 34c23d7, the security review fe5cf10.

## Verdict

**NOT RELEASABLE.** Neither "internally releasable, not announced" nor any abstention capability. Intent Decision 6 allows the first verdict only if both bars pass on the fifth set. The fifth set was never frozen, reviewed or scored, so the bars were never evaluated; there is no pass. The slice does not land as it stands either (see "Landing", below).

Reason, in one line: the only method the baseline left standing (one local answerability judge) failed its own pre-registered seen-set condition (spec 4.1: pooled Bar 1 >= 16/20 and Bar 2 >= 45/56) at Bar 1 = 2/20, Bar 2 = 55/56, and the owner stopped the model path (APPROVAL_RECORD-6). With the model path closed, nothing in the slice produces abstention, so there is nothing to gate.

## Tier classification rationale

Tier 2 is retained (STATE proposed it). Net product change at HEAD is empty: `git diff --stat 0dfd433 HEAD` over `aveto_support tests pyproject.toml uv.lock docs-source.toml .gitignore .claude` is empty, and `git diff 479f82a^ f1a96ad` is empty (04-security-review sections 1 and 3; I have no shell and did not re-run these, I rely on that evidence). The only non-record change is one edit to a safety control's text (INV-4, `.agentic/SAFETY_INVARIANTS.md`), which touched rule 4 and was approved (record 7). Nothing sends, posts, deploys or alters auth or permissions, so Tier 3 extras (dry-run on fixture, post-launch monitoring) do not apply. Tier 1 would understate it because a safety-control edit is involved and the intent's Done-means asked for a Tier 2 walk.

## Done-means, line by line (intent.md)

| # | Done-means line | Status | Reason |
|---|---|---|---|
| 1 | Starts from `main`; corpus, first-stage ranking, embedding model unchanged | **Met** | Worktree of main 0dfd433; product diff empty (Security 1, 3); baseline C1 confirms `docs-source.toml` identical and default `file-rrf-v1` (02-baseline 1). The intent says "pack v14"; STATE says playbook pack v15. I did not reconcile this. |
| 2 | Baseline first, seen sets only; model argued only if a simple rule fails | **Met** | 02-baseline section 5: no cell of the threshold, margin or combined family reaches both bars >= 90% pooled nor >= 80% pooled (best pooled min-bar 0.650 at t=0.67: Bar 1 13/20, Bar 2 37/56). Seen sets only; no gate set read. The Architect then argued one model. |
| 3 | If a model is proposed: local non-generative judge, pinned, hashed, ADR with licence and training data, rule 4 and 5 approval before download | **Not applicable at HEAD (conditions honoured before the stop)** | Licence decision (record 4), rule 5 and rule 4 (record 5) precede the download. The model is not shipped: record 6 lapses record 5 unused, ADR 0007 is marked rejected, no code references the judge (Security 3, 6). Cached files remain, gitignored (Security A2). |
| 4 | Freeze first; fifth held-out set committed; run once | **Not met** | No method commit exists (STATE "Failed condition"). Fifth set not committed, not read, not scored (Security 5). |
| 5 | Two bars on the fifth set, both must pass | **Not met (never evaluated)** | No pass or fail on the fifth set exists. The only figures are seen-set pre-checks of the candidate: 2/20 and 55/56, diagnostic, not the bars. Do not cite them as a bar failure. |
| 6 | Diagnostics in the same run: end-to-end figure, baseline vs earlier methods, abstention on seen sets, score distributions | **Not met** | No scoring run. Partial: the baseline reports the default path's behaviour on the four seen sets (0 abstentions in 93; top-1 distributions, 02-baseline sections 2, 4, 6). No end-to-end figure is reported or claimed by this slice. |
| 7 | `retrieve`/`eval` abstention prints exactly `no confident match`, exit 0, names the signal | **Not applicable** | No abstention built. Nothing in `aveto_support/` can print it (Security 2). |
| 8 | INV-4 extended by one sentence permitting a model to judge answerability; INV-5 names the pin | **Not met as written; superseded** | The extension (record 5 items 4-i/4-ii) lapsed. The owner instead approved a different change (record 7): INV-4's first sentence now says retrieval does not abstain. Verbatim match to the approved text, rest of INV-4 identical, INV-5 untouched (Security 2, 3). |
| 9 | Security Review (adversarial for new download path and INV-4) and Release Gate once, tier 2 | **Security met at a reduced depth; Release Gate = this document** | Security ran standard, PASS with advisories (0 blockers). The downgrade from adversarial is recorded only in STATE's option-1 plan, not in an approval record; its premise (no new code or download path) is verified by Security 1 and 3. No Tier 2 gate requires an approval for depth, so I record it as a deviation, not a blocker. |
| 10 | README status line and `CURRENT_MVP_STATUS` state the whole-pipeline figure and nothing stronger; no production or "safe to build on" claim | **Not met** | No whole-pipeline figure exists. Both documents still describe `no confident match` as a retrieval output (Security A1). Instructions below. |
| 11 | Earlier guarantees still hold (deterministic ingest, provenance, no generative model, no network outside ingest, hashes, offline retrieve) | **Met, with one open item** | Empty product diff and Security 3 (network code is main's two kinds only). Open: one exit 134 recorded on the `heldout-3` eval with the judge loaded; the code that produced it is gone, the item stays filed against slice 4's open crash item (see carry-forward). |
| - | "Must not break": abstaining is never worse than showing a wrong file; default is to say `no confident match` | **Not met, as on main** | Unmet before and after this slice (baseline section 2). Record it as the reason abstention is still owed, not as a regression. |

## Gates (RELEASE_GATES.md, Tier 2)

### Implementation

- [x] Typecheck, targeted tests, full suite, build: **n/a by identity, not re-run.** The product tree equals main's (empty diff). I have no shell and ran nothing. The one regression figure in the artefacts, 215 passed (03-implementation M1, M4), was recorded at the candidate commit 479f82a, which was then reverted; it is evidence about the candidate, not about HEAD. Main's own suite is the product here, and a green check on the merge commit is the artefact that would prove it. None is on file. This is not a claim that HEAD's suite passes.
- [x] One commit per task: **met.** Reflog shows one commit per stage or decision, the candidate and its exact revert as separate commits.
- [ ] No new lint warnings (`git diff --check`): **not run** (no shell). Changes at HEAD are Markdown and records; low risk, but unverified.

### QA

- [x] UI verified in preview: **n/a**, no UI.
- [x] Local regression command: **n/a by identity** (see above); not re-run.
- [x] Safety invariants verified: **met.** Security 2 and 3 compare INV-4 character for character with the approved text and show INV-5 byte-unchanged and the code consistent with INV-4's new sentence. INV-4 is now true of the code.

### Security (04-security-review, PASS with advisories)

- [x] No secrets or credentials in diff: met (Security 4).
- [x] No PII or sensitive data logged: met (Security 4; the questions CSV carries ids and scores only).
- [x] Audit events cover state changes: **n/a**, no product code changed, no audit path touched (Security 6).
- [x] Adapter boundary placeholder still throws: **n/a**, no adapter changed, no generative model added (Security 6).

### Release

- [x] Human approval points satisfied: **met** (next section).
- [x] Rollback plan: see below.
- [x] Release checklist filled: this document.

### Tier 3 only: n/a. Nothing external; no dry-run, audit coverage or monitoring plan is needed.

### Skipped gates

| Gate | Reason for skip | Approved by |
|------|-----------------|-------------|
| Freeze, label review, scoring (intent stages) | No method to freeze after spec 4.1 failed; the fifth set stays unspent and unread | Owner, APPROVAL_RECORD-6 (option 1), Gopal Patwa, 2026-10-09T17:49:16Z |
| Security at adversarial depth | Net diff empty apart from one text edit; no new download path | Orchestrator plan in STATE; no approval record (noted above) |
| Full suite / typecheck / build re-run | No product code differs from main; no shell in this role | Release Manager (this document); not owner-approved |

## Approvals verified

Checked against the records, not against messages. STATE's table and the records agree on approver, rule and time (Security 4 reached the same result).

| Record | Action | Rule | Approver | When (UTC) | Status at HEAD |
|---|---|---|---|---|---|
| 1 | Plan confirmation | plan | Gopal Patwa | 2026-10-09T06:32:12Z | Used |
| 2 | Scope Q1-Q5 | owner decision | Gopal Patwa | 2026-10-09T06:45:47Z | Used |
| 3 | Budget 650k to 780k | owner only | Gopal Patwa | 2026-10-09T16:45:05Z | Used |
| 4 | Licence decision, qnli-electra-base | owner decision | Gopal Patwa | 2026-10-09T16:55:27Z | Moot (model rejected) |
| 5 | Rule 5 model download; rule 4 INV-4 items 4-i/4-ii; rule 4 INV-5 and A1 line | 5, 4 | Gopal Patwa | 2026-10-09T17:05:20Z | **Lapsed by record 6, unapplied.** The download ran inside the window (M2); nothing from record 5 appears in `.agentic/`, README or `docs/` (Security 4). |
| 6 | Stop the model path; drop candidate code | owner decision | Gopal Patwa | 2026-10-09T17:49:16Z | Used; candidate reverted in f1a96ad |
| 7 | Rule 4: INV-4 correction (spec 8.3) | 4 | Gopal Patwa | 2026-10-09T17:50:52Z | Applied verbatim in 34c23d7 |

Record 5 was one reply to four separately surfaced requests (it lists each), which meets the "not batchable unless each was individually surfaced" test on its face; I did not see the surfacing message. Not approved anywhere: push, merge, PR, deploy, any other model or download. Advice from the other session (STATE "Advice received") is not an approval and is not relied on. Reflog shows no push-related operation, but the worktree reflog cannot prove none happened on a remote; I note no record of one.

## Rollback plan

Nothing was deployed and nothing is pushed, so rollback means undoing local commits. Confirmed against the actual diff:

1. The candidate code is already undone: `git diff 479f82a^ f1a96ad` is empty (Security 1).
2. The only live change is INV-4's first sentence (34c23d7). To revert, `git revert 34c23d7` (or drop the branch); this restores the old wording, which is false of the code, so revert only if the owner wants it.
3. Optional: delete the gitignored 438 MB judge cache at `models/cross-encoder--qnli-electra-base/` (Security A2).

## Landing: no-go as it stands

Verdict above covers the capability. For the branch itself, I also hold it: INV-4 now says retrieval does not abstain while `README.md`, `.agentic/CURRENT_MVP_STATUS.md` and `docs/ARCHITECTURE.md` still say it does. Landing INV-4 alone would leave the repo contradicting itself on a safety control, and Done-means line 10 is unmet. The fix is the tech-writer pass below, then a fresh owner decision on merge. Nothing is conditional: the held items are listed, and none is "ship if X".

## What the slice delivered, and what it did not

**Delivered**
- A measured baseline on the four seen sets (93 questions: 20 unanswerable, 73 answerable): the default path never abstains (0 of 93), and no threshold, margin or combined rule gets close to the owner's room-to-spare definition (best pooled min-bar 0.650; Bar 1 reaches 16/20 only with Bar 2 at 21/56 or lower). Seen-set, diagnostic.
- The INV-4 correction (record 7): the safety invariant no longer requires a behaviour the code never had.
- A recorded negative result about one model: `cross-encoder/qnli-electra-base` at revision c7dea87c, rule fixed at p >= 0.5, nothing tuned, scored Bar 1 2/20 and Bar 2 55/56 on the seen sets (03-implementation M3; on unanswerable questions the best-of-shown p was mostly >= 0.9 and below 0.5 for only 2 of 20). That is one model and one decision rule on seen data. It is not a result about answerability judges in general.

**Not delivered**
- Abstention in any form; `retrieve` still lists five files for every question.
- Any end-to-end figure (right file or correct abstention) on held-out data, and any fifth-set result. I report none.
- The INV-3 checker (out of scope by Decision 1) and a drafter.

**No production claim follows.** Nothing here supports "production ready", "internally releasable", or "drafting is safe to build on". The intent states that nothing that writes text for a user ships before this slice passes its gate; it did not pass, so the drafting slice stays blocked on abstention (or on an owner decision that revises that precondition).

## Pack and process catches

1. **Baseline on the unfixed code caught stale safety text and a mis-scoped premise.** Measuring the default path showed it never abstains while INV-4, README and CURRENT_MVP_STATUS said it did; and the intent's "0.63 to 0.71" overlap figures were set-4 only (pooled answerable-hit range 0.619 to 0.800, unanswerable 0.548 to 0.808).
2. **The pre-registered seen-set condition (spec 4.1) stopped a failing method before the one-shot set was spent.** The general-grounds argument for one model was falsified at the cost of an implementation pass, with the fifth set unread and no freeze to unwind.
3. **Approval hygiene held.** Model approvals were recorded as lapsed in their own record rather than dropped silently; the INV-4 correction was split into its own record 7 after record 6 left it pending; Security verified no lapsed text reached `.agentic/` or `docs/`.

Process gaps to note (not blockers): the Security depth reduction has no approval record; the Release Manager has no shell, so regression and `git diff --check` could not be re-run here and the artefacts hold no CI check on a merge commit; advisory labels collide (Security A1-A4, slice 4's A1-A5, and record 5's "A1 line"), so refer to them by source.

## Stale text: instructions for a tech-writer pass (not edited here)

Each item contradicts the corrected INV-4. Rewrite so it says what the code does: `retrieve` lists the top five files with their best verbatim passages and the top score, never abstains, and a question the docs do not answer still returns files. Do not touch INV-4 or INV-5 text. Route `.agentic/` edits through the usual owner path (Security A1).

1. **`README.md` lines 49-51** ("...a permalink, or `no confident match`. It never writes an answer."). Replace with: `retrieve` prints verbatim passages from the top five files, each with path, heading, line range and permalink, plus the top score. It never abstains (a question the docs do not answer still returns files) and never writes an answer. Also check the README status line: it must say abstention is not built, give no whole-pipeline figure (none exists), and make no production or "safe to build on" claim.
2. **`.agentic/CURRENT_MVP_STATUS.md` lines 11-16.** Delete "or `no confident match` with no passages". Replace the sentence "Confidence is the dense similarity ... calibrated at ingest" with: the ingest-time reference similarity is printed for information and decides nothing. Add a short line: abstention is not built; slice docs-abstention measured that no score-threshold or margin rule separates unanswerable from answerable questions on the seen sets, and one candidate model failed its seen-set pre-check (Bar 1 2/20, Bar 2 55/56), so the owner stopped that path; there is no end-to-end figure; no claim of production readiness or of drafting being safe to build on follows. Line 26 ("The models ... only rank") is true as is.
3. **`docs/ARCHITECTURE.md`**:
   - Line 27: change `RetrievalResult (≤5 passages | no confident match)` to the top-five-files result with no abstention branch.
   - Lines 85-87 (diagram): remove the `dense top-1 ≥ τ ?` test and the `not confident` / `no confident match` node; the only output is the hits node.
   - Lines 109-112: delete "It is confident only if the best dense similarity ... at least τ" and "Otherwise it returns exactly `no confident match` and **no** passages." State that the ingest-time τ is printed and decides nothing.
   - Lines 132-134: "If there is no confident match, it escalates" cannot stand. Say the drafter cannot rely on retrieval to say the docs do not answer; how it decides not to draft is open work (abstention is unbuilt).
   - Lines 141-144: remove "or 'no confident match' with none". The sentence "A model may only rank passages and decide confidence" mirrors INV-4's unchanged bold sentence; leave it matching INV-4 and do not edit the invariant.
4. Search `docs/` and `README.md` once more for `no confident match`, "abstain" and "confident" before closing; I grepped only the files above plus `LOCAL_COMMANDS.md` and `PROJECT_CONTEXT.md` (the former is already correct: "never abstains").

## What carries forward

- **Slice 4's A1-A5**: all remain open and unaffected by this slice; see `runs/docs-retrieval-4/07-close-out.md` (not re-read for this stage). Exit 134 is the one that moved.
- **Abstention is still owed.** Open question for the owner: a different method, or revising the intent's precondition that nothing that writes text ships before abstention passes. The baseline and the 4.1 result are the starting evidence; a new method needs its own rule 4/5 approvals and, if a model, a fresh hash check (Security A2).
- **The fifth set** stays unspent and unread, kept outside the repo; use it once, for a future frozen method.
- **Exit 134 (new occurrence)**: `eval` on `retrieval-heldout-3` aborted with libc++abi `recursive_mutex lock failed` after its full report printed, with the judge loaded (a third ONNX session). Filed against slice 4's open crash item; the code is gone so it cannot be reproduced from HEAD. The precondition stands: any exit 134 fails the build, no retry wrapper.
- **Cached judge files**: ~438 MB under lapsed approval; owner may delete (Security A2).
- **Stale-text pass** above, then an owner decision on merge.
- **Local absolute paths** in four record lines (Security A3): use repo-relative paths going forward.
- **The intent's "Must not break" abstaining default** remains unmet, as on main.

## Decision

- [ ] Go
- [x] **No-go.** Capability: not releasable (bars never evaluated; model path stopped by the owner). Branch: held for the stale-text pass; no push, merge, PR or deploy is approved or requested.

## Hand off

To the Engineering Manager (Orchestrator) with the failing items: Done-means lines 4, 5, 6, 7, 8 (as written), 10; then a tech-writer pass for the stale text; then Post-Launch Learning for close-out. The owner decides the next step on abstention.
