# Intent: Know when the docs don't answer — the check step's first half

> **Confirmed 2026-10-08.** Drafted by Claude in the playbook session from
> slice 4's close-out (`runs/docs-retrieval-4/07-close-out.md`) and the
> carry-forward in T22. The owner reviewed the draft and said "commit it"; the
> six recommended decisions below stand as written and the owner can still
> overturn any before the slice starts. This commit is not an approval of
> anything: rule 4 (INV-4 wording) and, if a model is proposed, rule 5 are
> taken from the owner in the Orchestrator's session. Start from a fresh
> worktree off `main` (slice 4 is merged).

## What I want

Retrieval that can say "the docs don't answer this". Today `retrieve` always
returns five files, even for a question the docs say nothing about. Slice 1
moved abstention out of retrieval; slices 2–4 made retrieval find the right
file about 70–87% of the time. This slice makes the *absence* case work, so
the pipeline can be measured as a whole: **of the questions asked, how often
does it return the right file, or correctly say there is none?** Nothing that
writes text for a user ships before this slice has passed its gate.

This is the first half of the check step. The second half (INV-3: a draft is
checked against its sources by a different model from the one that wrote it)
cannot be built or gated until a drafter exists, so it is deferred to the
drafting slice (Decision 1).

## Why the obvious way probably fails

Slice 4's fourth-set run printed a top score for every question. Answerable
hits scored 0.63–0.71. The four unanswerable questions scored 0.61, 0.74, 0.65
and 0.66. They overlap, so **a similarity threshold cannot separate them**, and
one unanswerable question (`fu02`, a deployment question) outscored every
answerable hit on that set. A model that reads the question *and* the passage together is
the likely need. That is a guess; the slice proves it by measuring the cheap
baseline first (below), not by assuming.

## Done means

- [ ] Starts from `main` (slice 4 merged: `file-rrf-v1` default, pack v14).
      Corpus, first-stage ranking and the embedding model are unchanged.
- [ ] **Baseline first, on seen sets only.** Before any model is proposed, the
      Architect reports what a score threshold and a score-margin rule do on
      the four seen sets' unanswerable and answerable questions (20 and 73
      questions; all seen, so diagnostic). If a simple rule meets both bars
      below on the seen sets with room to spare, no model is added. If not, the
      Architect argues one model, on general grounds, before any run.
- [ ] **If a model is proposed:** a local, non-generative **answerability
      judge** that reads the question with the top passages and returns a
      yes/no signal. It never produces text. Pinned to an exact revision,
      every file checked against a recorded sha256, ONNX Runtime + numpy, no
      PyTorch, no `trust_remote_code`, no new network use outside ingest. Needs
      rule 4 and 5 approval of the specific model before anything is installed
      or downloaded. Its licence and training data are recorded in an ADR
      before approval (the reranker's open MS MARCO question is the cautionary
      case).
- [ ] **Freeze first.** The method's commit is recorded; then a **fifth
      held-out set** is committed (Decision 2). Run once.
- [ ] **Two bars, both set here, both must pass, neither moved after a result:**
      1. **Abstains correctly on at least 80% of unanswerable questions** (16
         of 20).
      2. **Does not abstain on at least 80% of the answerable questions whose
         correct file retrieval put in the top 5.** Abstention is not asked to
         repair retrieval misses, and a system that always abstains must fail.
- [ ] **Reported in the same run, as diagnostics:** the end-to-end figure (right
      file, or correct abstention, over all questions); the baseline method
      and any earlier method on the same set; abstention on the four seen
      sets; the top-score distribution for abstained and answered questions.
- [ ] **`retrieve` and `eval` output:** an abstention prints exactly
      `no confident match` with no passages (as INV-4 already states), exits 0,
      and says which signal decided. Retrieved text stays verbatim; nothing is
      reworded.
- [ ] `.agentic/SAFETY_INVARIANTS.md`: INV-4 is extended by one sentence stating
      that a model may judge whether the passages answer the question, and
      nothing more (rule 4). If a model is added, INV-5 names its pin.
- [ ] **Security Review** (adversarial for any new download path and for
      INV-4) and the **Release Gate** run once, tier 2: no deploy, nothing
      posted. The Release Gate's verdict may be **"internally releasable, not
      announced"** only if both bars pass on the fifth set; if either fails the
      verdict is "not releasable" and the slice records why.
- [ ] The README's status line and `.agentic/CURRENT_MVP_STATUS.md` state the
      whole-pipeline figure and nothing stronger. No document claims
      production readiness, or that drafting is safe to build on, from this
      result alone.
- [ ] Everything earlier slices guaranteed still holds: deterministic ingest,
      provenance on every passage, no generative model, no network outside
      ingest and CI setup, every model file hash-checked, retrieve offline.

## Must not break

- Nothing retrieved is presented as an answer.
- The user can always see where every passage came from.
- The question and the docs never leave the machine.
- Abstaining is never worse than showing a wrong file: when unsure between the
  two, the default is to say "no confident match".

## Constraints

- Python 3.12, uv, the existing structure. At most one new model, and only if
  the baseline fails. No generative model, no hosted API.
- Nothing is chosen by its score on the gate set. The signal, the threshold and
  any model are argued before the run; seen sets may inform them, the gate set
  may not.
- **Held-out rules** (`project-packs/ai-agent-product.md`, "Held-out gates"):
  the builder does not write the set; freeze, then commit the set, then run
  once; labels reviewed by someone other than the drafter before the set is
  committed and sharpened before scoring, never after; the bars never move.
- One fresh agent per stage; no resumed agents. Review-archetype stages
  (Security, Release Manager) are budgeted at 50–60k, with a tight read list.
- **Baseline a claim on the unfixed code before arguing a cause** (slice 4's
  lesson): the Architect's account of why abstention fails must rest on the
  numbers in "Why the obvious way probably fails", re-measured, not on this
  paragraph.
- No Azure, no API key, no deploy. CI stays its own slice.

## Out of scope

- Any generative model, drafting, classification, or the INV-3 draft checker.
- Changing the corpus, the first-stage ranking or the embedding model.
- Re-opening the reranker.
- The `docs-retrieval-ci` workflow (precondition recorded: any exit 134 fails
  the build, no retry wrapper).
- Posting anywhere.

## Stakes

- [ ] Touches real user data
- [ ] Moves money, or changes billing
- [ ] Irreversible — deletes, sends, or deploys to live users
- [x] Changes auth, permissions, or a safety control — INV-4 gains a sentence
      (rule 4); a model, if added, is a rule 5 approval and extends INV-5
- [ ] Adds a screen or UI a user will see
- [ ] None of the above

## Decisions (recommended; the owner can overturn any)

1. **Abstention only; the INV-3 draft checker waits for a drafter.** A checker
   that compares a draft with its sources cannot be built honestly, or gated,
   with no draft to check. Abstention can, and it is the part retrieval owes.
   The drafting slice owns INV-3 and must pass its own gate before anything
   reaches a user; the playbook session will record
   this in T22 once the owner confirms this intent.
2. **The gate set is a new, fifth set, with at least 24 unanswerable and 24
   answerable questions, drafted by Claude in the playbook session and kept
   outside the repo until the freeze.** The four existing sets hold only 20
   unanswerable questions, all seen, and too few to bar on. Unanswerable
   questions are the hard part: the label is a claim that the docs do *not*
   answer it. So **a fresh QA spawn reviews every unanswerable label by trying
   to find a defensible answer in the docs**, and drops or reclassifies any
   question it finds one for, before the set is committed. The reviewer gets
   the questions and the docs, not the method or any result. A different fresh
   QA spawn scores it once. At least half the unanswerable questions are hard
   negatives that share vocabulary with the docs (as `fu02` does).
3. **Bar 2 uses retrieval hits as its denominator.** Otherwise a retrieval
   miss and a false abstention would be indistinguishable, and the abstention
   method would be blamed or credited for retrieval's work.
4. **The cheap baseline comes first, and a model has to earn its place.** If
   thresholds meet both bars on the seen sets with room to spare, the slice
   ships without a model, which also keeps INV-5 untouched. This is the
   lesson of slice 3: a component that meets a gate can still be worth
   nothing, and the comparison to the simple method is what shows it.
5. **Budget: 650k, split at the freeze.** Slice A (Scope, Architecture with the
   baseline, rule 4/5 approvals, Implementation, freeze) 330k; slice B (label
   review, scoring, Security, Release Gate, close-out) 320k. Slice 4 was
   planned at 400k and measured 581k; its review stages ran 3–4× their
   estimates, so those are set at 50–60k here. An overrun stops and asks with
   the numbers; the budget is never raised by an agent, and Security and the
   Release Gate are not compressed.
6. **What the Release Gate may say.** "Internally releasable, not announced"
   if both bars pass, with the whole-pipeline figure stated. A pass is still
   not a production claim: it removes a blocker for the drafting slice and no
   more.
