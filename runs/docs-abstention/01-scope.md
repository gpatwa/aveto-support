# Scope Review: docs-abstention

> Engineering Manager, standard depth. Read: `intent.md`, `00-slice-plan.md`, `STATE.md`, `.agentic/SAFETY_INVARIANTS.md`,
> `.agentic/CURRENT_MVP_STATUS.md`, `runs/docs-retrieval-4/07-close-out.md`. No code read, no other runs read.
> I produce scope decisions and flags only. Nothing here is a spec, and no open question below is resolved by me.

## 1. Verdict

**Scope: ACCEPT, with six required clarifications (section 4) fixed before A2 is spawned, and two owner decisions (section 6).**

- One behaviour change (abstention in `retrieve`/`eval`), one safety-control wording change (INV-4), at most one conditional model. It does not mix a user-facing change with an internal refactor. It is small enough for one implementation pass, provided the Architect lists the files A4 will touch and it stays at 10 or fewer (OPERATING_MODEL scope rule). If the model path is taken and the list exceeds 10, A4 splits.
- The A/B split at the freeze is the right shape. The freeze is the one point after which the method may not change, so it is the natural budget and responsibility boundary. I do not recommend splitting into two slices: the bars, the method and the gate set only mean something together.
- **No compression.** The short path is unavailable: the intent ticks "changes auth, permissions, or a safety control" (INV-4), and stakes override completeness. Discovery, UX and UI Design are already absent, correctly, because there is no UI and the intent carries the "why". Security and the Release Gate always run and are not compressed.
- **Gate tier: 2** (no deploy, nothing posted). Agree with the plan; the Release Manager confirms.
- **Stages: no additions.** The plan's stage list stands, with one reorder recommended as an owner decision (section 6, Q1).

## 2. Stages as scoped

| Stage | Run? | Depth | Note |
|-------|------|-------|------|
| A1 Scope | run (this) | standard | |
| A2 Baseline (qa-evidence) | run | standard | Measure only, argue no cause. Must also emit a sweep table over a pre-fixed grid (section 4, C2), because A3 has no shell. |
| A3 Architecture | run | standard | Decides threshold/margin vs one model. On the model path, the model-path total must be computed and sent to the owner before A4 (section 5). |
| Approvals | run | n/a | Rule 4 (INV-4 sentence); rule 5 + rule 4 on INV-5 only if a model. Typed by the owner in the driving session. |
| A4 Implementation | run | standard | No README or MVP-status claim written here (section 4, C6). |
| Freeze | run | n/a | Method commit in STATE.md. |
| B1 Label review | run | standard | Fresh. |
| B2 Scoring | run | standard | Fresh, different from B1. See Q1 for its order relative to B3. |
| B3 Security | run | **adversarial** (earned: INV-4 is a safety control, plus any download path) | |
| B4 Release Gate | run | standard | One verdict spawn. |
| B5 Close-out | run | standard | |

Skipped, with reason: Market Research, Discovery, UX Research, UI Design, Post-Launch beyond close-out. The intent carries the why and there is no UI.
Not compressed: Security, Release Gate, QA.

## 3. What is sound in the plan

- Baseline-first on the unchanged code, by a spawn that argues no cause, applies slice 4's lesson directly.
- The model has to earn its place against the simple rule on the same data.
- Review-stage estimates (50-60k, tight read lists) respond to slice 4's 3-4x overruns.
- The bars are committed in the intent before any run, so no separate bar-commit step is needed. Agree.
- Retries capped at 2, a failed bar is a result, nothing is tuned afterwards.

## 4. Ambiguities and gaps (clarify before A2; none needs the owner unless marked)

**C1. "pack v14" in the intent's first Done line.** The repo is on v15 (0dfd433). The line's substance holds (slice 4 merged, `file-rrf-v1` default). The intent is a byte-identical copy and must not be edited. Record in STATE.md that "pack v14" is read as "slice 4's state", and have A2 verify `file-rrf-v1` is the default and the corpus pin is unchanged as its first act. Not a blocker.

**C2. The baseline needs a fixed signal, grid and selection rule, set now.** Otherwise the "sweep" is a search over the seen sets with the stopping point chosen by its result.
- Signal: the **dense cosine similarity of the best passage among the returned top-5**, the same quantity the existing confidence uses and the one the intent's 0.61-0.74 figures are. Raw RRF scores are not comparable across questions and are not a candidate.
- Margin: top-1 minus top-2 of that same score, per question.
- A2 emits (a) one row per seen question: id, set, label, top-1 score, top-2 score, margin, rank of the correct file (or none), and (b) a sweep table over a fixed grid (threshold in 0.01 steps across the observed range; margin in 0.005 steps; plus the combined "threshold AND margin" rule), giving Bar 1 and Bar 2 counts at each point. A2 selects nothing. The Architect picks from the table and states the pick and the reason before any gate-set run.
- Why A2 and not A3: the Architect has no shell, and a 93-row sweep by hand is the kind of unverified arithmetic slice 4 paid for.

**C3. The existing "no confident match" threshold.** `CURRENT_MVP_STATUS.md` says retrieve already returns `no confident match` when the best passage's dense similarity falls below a threshold calibrated at ingest, and INV-4 already allows "a model ... to decide confidence". The intent says retrieve "always returns five files". Both cannot describe the same path. Required before A2 ends:
- State whether, on the default `file-rrf-v1` path, the calibrated threshold is applied today, and what it does on the 20 unanswerable and 73 answerable seen questions. This is the **first baseline row**. If it already meets both bars on the seen sets, the plan's premise is wrong and the Architect says so.
- State how a new rule composes with it: replace, or run in addition (abstain if either fires). Recommendation: in addition, with the calibrated threshold unchanged, so a new rule can only abstain more, never less, consistent with "when unsure, say no confident match". The Architect decides; the choice is made before the sweep and the sweep is run on the composed rule.
- Every abstention counts, whichever signal fired, in both bars. The output names the deciding signal.

**C4. "Right file in the top 5" for Bar 2.** Define it exactly, before the fifth set is delivered:
- A question is in the Bar 2 denominator if one of the files its label accepts appears in the five files returned by `file-rrf-v1` **before any abstention rule is applied**, at the frozen commit. If a label lists more than one acceptable file, any one counts. This is computed from retrieval's own output, so a false abstention can never remove a question from its own denominator.
- Bar 2 numerator: those questions where the system does not abstain. (It need not return the right file; Bar 2 measures abstention, not ranking.)
- Counts are fixed as ceilings: Bar 1 passes at `ceil(0.8 * n_unanswerable)` (20 of 24; 16 of 20 on the seen sets as the intent states); Bar 2 at `ceil(0.8 * n_hits)`. The denominator is known only at scoring, so the scorer states it from the pre-abstention output before applying any rule.
- Note for the owner, not a change: with 24 questions per group a bar is a coarse test (one question is 4 points), and the denominator of Bar 2 will be around 20. The bars stand; the Release Gate must not read a narrow pass as more than it is.

**C5. "With room to spare" must be a number fixed now.** Recommendation: a rule counts as meeting the seen-set bars with room to spare only if **both** bars are **at least 90%** on the seen sets (Bar 1: 18 of 20 or better; Bar 2: 90% of the seen-set hits) **and** the single chosen setting still clears 80% on both when the four seen sets are scored leave-one-set-out. Rationale: the setting is chosen on those same sets, so it is optimistically biased, and a 10-point margin plus the leave-one-out check is the cheapest guard before the one unseen run. This is a recommendation for the owner (Q2): it is a bar-adjacent number and the intent leaves it open. It must be committed before A2's sweep table is read by the Architect. The intent's own numbers (answerable 0.63-0.71, unanswerable 0.61-0.74) suggest a threshold will not clear it, so plan for the model path (section 5).

**C6. Status claims and who writes them.** The plan does not say who edits the README status line and `CURRENT_MVP_STATUS.md`. Slice 4's close-out records a README claim written before its gate. Rule: **A4 writes no whole-pipeline figure**. Those two edits happen after the Release Gate verdict, by the Orchestrator or Backend (not the Close-out role, which has no code-side write scope), and state only the figure the scorer recorded. INV-4/INV-5 text is written in A4 only in the exact words the owner approved.

**C7. What "run once" means.** Slice 3 saw one exit 134 in 8 runs (open, not reproduced). Define now: the scoring run is one invocation at the frozen commit with raw output captured. A process abort with no result (exit 134 or similar) is not a result; it may be re-run identically and both attempts are recorded and reported. Any run that produces a result is final. No re-run for any other reason. The owner confirms (Q3).

**C8. The INV-4 sentence must earn its place.** INV-4 already says a model "may be used only to rank passages and to decide confidence". The new sentence (rule 4) must say something that is not already true, otherwise it is a safety-control edit with no effect. If the baseline path ships with no model, the Architect should say whether the sentence is still needed (the owner may decide none is). If a model ships, the sentence should state what it may read (question plus passages), what it returns (a yes/no signal only), and the fail-closed behaviour: judge missing, hash mismatch or error means an error exit or `no confident match`, never a pass-through of unjudged passages. I am not drafting the sentence.

**C9. Gate-set definition gaps (intent Decision 2).**
- "At least 24 unanswerable and 24 answerable" and "at least half hard negatives" must hold **after** the label review drops or reclassifies questions. The review can only remove, so the delivering session must supply a surplus, or the slice stops short of its minimum. Specify "after review" in the handback to the other session. Owner confirms (Q4).
- "Hard negative that shares vocabulary with the docs" is not testable as worded. Require the drafter to tag each hard negative with the file(s) it overlaps and the shared terms, and B1 to confirm each tag. Overlap is checked, not asserted.
- Keep the set unreachable to A2-A4: it lives outside the repo and outside every spawn's read list, and the brief for each says not to look. The Orchestrator already has not read it.
- The label reviewer must record, per unanswerable question, what it searched and what it found, so a "no answer found" is auditable.

**C10. The "end-to-end" diagnostic.** "Right file, or correct abstention" does not say whether "right file" means top-1 or in the top 5. Report both, with top-5 as the headline (it matches Bar 2). Diagnostic only.

## 5. Freeze order, and what the plan quietly assumes

**Freeze order, as scoped (testable):**
1. A3 fixes the rule (signal, composition with the calibrated threshold, threshold or margin value, or model + pin) in `02-tech-spec.md` before any gate-set file exists in the repo.
2. Owner approvals recorded. A4 implements. Tests green.
3. Orchestrator records the **method commit SHA** in STATE.md. Checkable: `git diff <sha> HEAD` touches no abstention decision code after this point.
4. The fifth set is delivered; B1 reviews; the Orchestrator commits the set in a commit that touches only the set files and the review record.
5. B2 scores once at the recorded SHA (C7).
Add one rule the intent does not state: **after step 3, any change to code that affects the abstention decision voids the fifth set** (it becomes a seen set), and the slice would need a new one. Doc and wording changes (README, INV text) do not.

**Assumptions in the plan that I flag:**
- **Model-path cost is understated.** The plan notes slice B overshoots (340k vs 320k). Slice A also overshoots on the model path: A1 50 + A2 60 + A3 70 (an ADR on licence and training data will push this up) + A4 178 = 358k vs 330k. Whole slice on the model path is roughly 698k against 650k (50+60+70+178+80+50+130+55+25), not "slightly tight". The stop-and-ask must happen **at A3's exit, before A4 is spawned**, with the model-path total, and not after A4 has run. EM position: the budget decision is the owner's; Security and the Release Gate are not shrunk to fit.
- **A3 sweeps without a shell.** Handled by C2.
- **Security after scoring (B3 after B2).** A required fix that touches the decision code after scoring (slice 4 had one, R1, though on an ADR sentence) either voids the fifth set or leaves a known defect in a safety control. See Q1.
- **A model implies INV-5 changes.** INV-5(b) says "exactly two local models". A third rewrites that wording (rule 4) as well as adding rule 5 approval for the model itself. The plan covers this, but the approvals are two separate typed approvals, plus any ADR on licence and training data before the rule 5 request, not after.
- **Slice 4 advisory A1** (name a default-path offline test in INV-5) falls due at "the next rule 4 touch of INV-5". If the model path is taken, INV-5 is touched anyway, so the Architect should offer it as an optional line in the same approval request; it must not be added without the owner approving that exact text. If no model, INV-5 stays untouched and A1 stays carried forward.
- **Fail-closed behaviour of any judge** is not in the intent or plan; see C8.
- **Out of scope, checked:** the plan's non-goals match the intent's "Out of scope". No item is quietly assumed outside it. One thing sits close to the line: changing the `eval` exit rule (non-zero below 80% on either group). The intent asks only for new output and diagnostics; leave the existing exit rule alone unless the Architect shows it must change, and then take it back to the owner as scope.

## 6. Open questions for the owner (not resolved here)

- **Q1. Order of Security (B3) and Scoring (B2).** Recommendation: run B3 on the frozen method **before** B2 scores, so a required fix lands before the one unseen run rather than after it. It adds no stage, only changes order, and B3 does not need the fifth set's results. Alternative: keep the intent's order and accept that a decision-code fix after scoring voids the set. The intent does not fix the order, so this is the owner's call.
- **Q2. "Room to spare" number.** Recommended: both bars at least 90% on the seen sets, and 80% or better leave-one-set-out (C5). Committed before the sweep table is read.
- **Q3. "Run once" with an abort.** Confirm the C7 rule (an abort with no result may be repeated identically and both recorded; nothing else).
- **Q4. Gate-set counts after review.** Confirm that 24/24 and "half hard negatives" are measured after the label review, and that the other session supplies a surplus.
- **Q5. Whether a sentence is added to INV-4 on the no-model path.** INV-4 already allows a model to decide confidence. The intent assumes a sentence is added; the Architect will argue whether it is needed; the owner decides at the rule 4 approval.

## 7. Context bundles (thin)

- **A2:** `runs/docs-abstention/intent.md` (the "Why the obvious way..." and "Done means" sections), the section 4 clarifications above, the repo's `retrieve`/`eval` entry points and the four seen eval files (paths to be listed by A2 itself from `.agentic/LOCAL_COMMANDS.md`), no spec, no cause arguments.
- **A3:** `02-baseline.md` and raw tables, this scope file, `.agentic/SAFETY_INVARIANTS.md`, `intent.md`. Not the gate set.
- **A4:** `02-tech-spec.md`, the approved INV text, the files the spec names (the Architect lists them; more than 10 means split), the existing tests named in INV-4/INV-5.
- **B1/B2:** each gets the questions and docs (B1) or the frozen SHA and bar definitions (B2). B1 gets no method or result; B2 gets no review reasoning beyond the committed labels.
- **B3/B4:** tight read lists at 50-60k (100k adversarial for B3, 130k with a model); the Orchestrator names the files.
- Everyone: targeted `grep -n` and range reads, targeted tests first, full suite before the freeze commit.

## 8. Acceptance for this scope stage

- [x] Scope judged against the 10-file, mixed-change, dependency, two-suite and observable-criteria rules: passes, subject to the A4 file list.
- [x] Lifecycle: no compression, no added stage; one optional reorder (Q1).
- [x] Tier 2; no human approval has been assumed. Pending approvals: rule 4 (INV-4), and if a model, rule 5 and rule 4 on INV-5; each typed in the driving session.
- [ ] C1 to C10 recorded in STATE.md or the A2 brief before A2 is spawned (Orchestrator).
- [ ] Owner answers Q1-Q5 (Q2 and Q1 before A2/A3; Q3-Q5 before B1).

**Handoff:** to the Orchestrator, for A2 (QA Evidence, baseline). Gates fail closed; none were relaxed.

