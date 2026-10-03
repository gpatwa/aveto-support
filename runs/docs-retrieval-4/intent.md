# Intent: Ship the retrieval that earned its place — make the simple method the default

> **Confirmed 2026-10-01.** Drafted by Claude in the playbook session from
> slice 3's close-out (`runs/docs-retrieval-3-proof/03-close-out.md` on branch
> `claude/docs-retrieval-3`). The owner delegated the three open questions,
> verbatim: "decide them". Claude decided them as recorded under
> **Decisions**; the owner can overturn any before the slice starts. Decision
> 2 changes a safety control, so the Orchestrator should take the owner's own
> rule 4 yes in its session. Start from a fresh worktree off `main`, then merge
> `claude/docs-retrieval-3`.

## What I want

A retrieval step that is ready to release: the method that did as well as any
on every held-out set, without the parts that earned nothing. Slice 3 showed
the reranker met the gate by exactly the minimum while the simpler
`file-rrf-v1` scored 14/16 on the same set, and across four sets the reranker
was net negative at 2.3–3.8 s a question against 0.9 s. So the default
becomes `file-rrf-v1`, the reranker stays available but off, the intermittent
shutdown crash is fixed, and the result goes through Security Review and the
Release Gate once, as a smaller change than slice 3 would have been.

## Done means

- [ ] Starts from `main` with `claude/docs-retrieval-3` merged (slice 3's code,
      reranker included), keeping slice 3's `runs/` as the record.
- [ ] **`file-rrf-v1` is the default ranking** in `retrieve` and `eval`;
      `--ranking file-rerank-v1` still works and is off unless asked for.
      Default `retrieve` and `eval` load **no reranker files and make no
      reranker download**; the reranker's model files are fetched only if the
      owner opts in.
- [ ] **The shutdown crash is fixed or explained.** `eval` and `retrieve`
      exit 0 after a passing run, 20 consecutive runs of the gate command in
      a row, with both ranking modes. If the root cause is the ONNX runtime
      holding two sessions, the fix is argued in the tech spec on general
      grounds, not found by trial against the gate set.
- [ ] **No new gate set is written and none is re-scored for tuning.** The
      default method is the one that already scored on the fourth set
      (14/16), the third (11/16) and the second (12/17): this slice changes
      *which method is the default*, not the method. The Release Gate re-runs
      the default once on the fourth set as a regression check, reports the
      earlier sets as diagnostics, and **makes no release claim** (Decision 1).
- [ ] **Security Review** (adversarial depth for the download path and
      INV-4 / INV-5, standard elsewhere) and the **Release Gate** run once on
      the whole retrieval step, tier 2: no deploy, nothing posted. The Release
      Gate's verdict is "internally releasable, not announced" (Decision 1). The
      reranker's MS MARCO licence question is recorded as **not applicable to
      the default path** and explicitly open for anyone who opts in.
- [ ] `.agentic/SAFETY_INVARIANTS.md`: INV-5 keeps naming both models'
      pins (Decision 2), with a sentence stating that the default path
      fetches only the embedding model.
- [ ] The stale "plain code" wording in `.agentic/PROJECT_CONTEXT.md` and the
      README's status line are updated to match what shipped.
- [ ] Everything earlier slices guaranteed still holds: deterministic ingest,
      provenance on every passage, no generative model, no network outside
      ingest and CI setup, every model file hash-checked, retrieve offline.

## Must not break

- Nothing retrieved is presented as an answer.
- The user can always see where every passage came from.
- The question and the docs never leave the machine.

## Constraints

- Python 3.12, uv, the existing structure. No new dependency, no new model,
  no new download.
- One fresh agent per stage; do not resume agents across passes.
- Nothing is chosen by its score on any eval set. The default is changed on
  the evidence already recorded; this slice does not tune.
- No Azure, no API key, no deploy. CI stays its own slice, started only after
  this one releases.

## Out of scope

- Any generative model, and abstention ("the docs don't answer this"):
  owned by the check-step slice, which must exist before anything that writes
  text for a user ships.
- A new held-out set, a new reranker, or any ranking change.
- The `docs-retrieval-ci` workflow.

## Stakes

- [ ] Touches real user data
- [ ] Moves money, or changes billing
- [ ] Irreversible — deletes, sends, or deploys to live users
- [ ] Changes auth, permissions, or a safety control
- [ ] Adds a screen or UI a user will see
- [x] None of the above — INV-5's one-sentence clarification is a rule 4
      approval, as in slices 1–3

## Decisions (were open questions)

1. **Slice 4 is cleanup only, with no release claim.** No default method has
   passed the 80% bar twice (`file-rrf-v1`: 14/16, 11/16, 12/17), and nothing
   that writes text for a user may ship before the check-step slice exists. A
   retrieval-only release would add a claim without adding a user. The
   Release Gate verdict is therefore "internally releasable, not announced":
   the code is sound, secure and tidy, and the README keeps its honest status
   line. The release claim moves to the check-step slice, which will state
   what the whole pipeline achieves.
2. **INV-5 keeps naming both models' pins.** The code can still fetch the
   reranker on opt-in, so the safety control should still name it. One
   sentence is added: the default path fetches only the embedding model.
   This is a rule 4 approval, taken in the Orchestrator's session.
3. **Budget: 400k, no split.** A small slice: Scope Review, one Architecture
   note, one Implementation, Security, Release Gate, close-out. An overrun
   stops and asks with the numbers.
