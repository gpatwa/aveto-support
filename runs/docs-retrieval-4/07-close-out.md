# Close-out: docs-retrieval-4

> Post-Launch Learning. Tier 2, standard depth. Sources: `06-release-checklist.md`, `STATE.md`, slice 3 close-out section 6. No production signals exist (nothing is deployed or announced), so every finding below cites the checklist or STATE.

## 1. Outcome

**Internally releasable, not announced.** The fourth held-out set, run once on the default ranking, scored 14/16 (87.5%), at the bar set before the run (misses f04 and f12, exit 0, `file-rrf-v1`, no reranker). Security: PASS with advisories after one retry (required-fix R1, an ADR sentence over-claiming a crash outcome, resolved at the re-check). Nothing is announced, pushed or merged. The owner pushes, opens the PR and merges. No retrieval-quality claim is made: no default method has passed the 80% bar twice on unseen data.

## 2. Against the intent's "Done means"

- **Met:** branch started from slice 3 merged (6591bf3); `file-rrf-v1` is the default and loads no reranker and downloads none; no new gate set written or re-scored; Security and the Release Gate run once; INV-5 sentence added with the owner's rule 4 approval; stale wording updated; earlier guarantees hold (168 tests green).
- **Not met as written: the crash fix.** The crash is **NOT REPRODUCED**. It is not fixed and not explained. Slice 3 saw 1 abort (exit 134) in 8 runs; slice 4 saw 0 in 660 runs (220 unfixed, 440 fixed) plus 0 in QA's 4 default-path eval runs. The Architect's mechanism (a session alive at finalisation) was observed false on the unfixed code: both adapters were already dead when `main()` returns. The close discipline added is hygiene with no demonstrated effect.
- The "20 consecutive runs" sub-requirement is met as 20 runs per mode with none at 134; dev-set eval exits 1 by design (79.2%).
- Diagnostics, not claims: dev 19/24, second set 12/17, third set 11/16.

## 3. What worked, what surprised, what to fold in

**Worked**
- The bar was committed (23d233c) before the QA run, and the result was judged against it without edits.
- Fresh spawns for plan, QA and verdict kept the Release Gate honest; the verdict stated the open crash item and the box that was not met instead of softening them.
- Security found a real over-claim (ADR 0006 crash wording) and the retry cost 20k + 36k.

**Surprised**
- The Architect's cause argument was wrong: its premise was not observed. A cheap pre-fix baseline (run the unfixed code first) would have shown that before the fix was designed. The 200-run unfixed loop that did so was suggested by another session and adopted by the owner.
- The README said "internally releasable" before any gate ran; it was corrected (3b95a64).
- Budget was raised three times by the owner (400k to 520k to 560k to 585k) because stages overran their estimates: Security 129k vs 70k est.; Release Manager step 1 59k vs 15k est. Architecture and Implementation came in on estimate.

**Fold into the next slice**
- Measure first: reproduce or baseline a defect on the unfixed code before a spec argues a cause.
- Do not write status claims ahead of the gate that earns them.

## 4. Carry-forward

Advisories (none blocking):
- **A1.** INV-5's named offline tests cover only the opt-in ranking with injected adapters; name a default-path offline test at the next rule 4 touch of INV-5 (needs approval).
- **A2.** `test_ingest_with_reranker_fetches_and_rehashes` overstates what it proves; strengthen with real cached fixtures, do not rename (the name is in INV-5).
- **A3.** The reranker hash-mismatch message gives mixed guidance ("run ingest" no longer refetches the reranker). Cosmetic, fails closed.
- **A5.** The crash-evidence scripts hard-code absolute local paths; parameterise if reused.

Other:
- **`docs-retrieval-ci` preconditions:** any exit 134 fails the build and is filed as an occurrence of the open crash item; no retry wrapper. The crash stays open (not reproduced) and is stated as a precondition in that plan. CI must not describe a passing checklist as a quality claim.
- **Check-step slice** owns abstention and the release claim; it must exist before anything that writes text for a user ships.
- **MS MARCO licence question** is open for anyone who opts in (`ingest --with-reranker`, `--ranking file-rerank-v1`); not applicable to the default path.
- **Estimate guidance:** review-archetype stages that read many artefacts ran 3-4x over a 15k-35k estimate (Security 129k vs 70k; Release Manager step 1 59k vs 15k). Budget them at 50-60k, or give them a tight read list.

## 5. Metrics

Final spend per `usage.mjs` after this stage (Orchestrator-corrected; the figure the stage was written with, 555k, excluded Close-out itself): 581k of 585k peak context (99.3%), 9.68M processed. Close-out came in at 26k against its 25k estimate. The Orchestrator regenerates `runs/ANALYTICS.md` and `runs/dashboard.html` with `analyze.mjs` after this artefact (this role has no shell); flagged stages (Security 129k, Release Manager step 1 59k) are carried above.
