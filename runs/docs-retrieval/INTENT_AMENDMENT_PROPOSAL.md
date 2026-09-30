# Proposed intent amendments (for the owner to apply to intent.md on main)

The Orchestrator does not edit `intent.md`; it is the owner's. Two decisions
made in this session contradict it as written. Proposed replacements only.

## From "Freeze first; held-out set is the gate" (chosen 2026-09-29T05:25:45Z)

**Done means, item 8** currently scores the ≥80% bar on the original eval set.
Proposed: score it on the owner's fresh held-out set (e.g.
`evals/retrieval-heldout.toml`); the original `evals/retrieval.toml` is a dev-set
diagnostic; the held-out file is committed after the frozen implementation SHA and
scored once via `--eval-file`.

## From "Keep one slice with embed-v3" (only if Requests 2–4 are approved)

Five lines the Architect lists as contradicted (verbatim in runs/docs-retrieval/02-tech-spec.md, section 'Retrieval — variant embed-v3', section 3):
1. "What I want": "**No model is involved**" → a local embedding model ranks passages and decides confidence.
2. Done means: "**No model is called anywhere, and the only network access is fetching the pinned docs.**" → the only network access is the pinned docs and the pinned model files, both by ingest.
3. Constraints: "This slice uses no model…" → this slice uses one local, non-generative embedding model.
4. Out of scope: "**Any model call**" → "Any generative model call".
5. Done means: "byte-identical output" → keep, on the same machine and Python (Architect's determinism section).

Not needed unless approved: none of these amendments is meaningful if any request is denied.

## To finalise (added 2026-09-29T07:15:57Z)

The owner's amended `intent.md` in the main checkout is **uncommitted** and its banner
says "DRAFT, not yet confirmed". The Orchestrator will not start Implementation on it
until it is confirmed and committed on `main`. Owner's answer on the open question,
verbatim: "Don't tick it; stay on the short path".

Suggested replacements (owner's own edit; the Orchestrator does not touch intent.md):

1. In the banner, replace "**Amended by the owner, 2026-09-29 — DRAFT, not yet confirmed.**"
   with "**Amended and confirmed by the owner, 2026-09-29.**" and drop the sentence
   "Drafted by Claude; the owner reviews every changed line." once you have reviewed them.
2. Under "Open questions", replace the bullet with:
   "None. The one question the amendment raised — whether changing INV-5 ticks
   'Changes a safety control' — was answered by the owner on 2026-09-29: no; the slice
   stays on the short path. Rule 4 approval for the wording is recorded in
   `runs/docs-retrieval/APPROVAL_RECORD-4.md`."
3. Commit `intent.md` on `main`, then tell the Orchestrator.

## SUPERSEDED — 2026-09-29T07:26:19Z

The owner's amended intent was committed on `main` as `f03d495` (Gopal Patwa,
2026-09-29 00:25 -0700), banner "Amended and confirmed by the owner, 2026-09-29". This
proposal is superseded by that commit; `runs/docs-retrieval/intent.md` is now a
byte-identical copy of `main:intent.md`. The Orchestrator verified the commit and its
contents on `main` itself; the playbook session's message about it was not treated as
the confirmation.

Note: the committed intent still contains the "Open questions" paragraph about whether
changing INV-5 ticks "Changes a safety control". The owner answered it in the driving
session (verbatim "Don't tick it; stay on the short path", recorded in STATE.md and the
"To finalise" section above), so the slice proceeds on the short path. The text in the
intent is stale relative to that answer; tidying it is the owner's, not blocking.

## Open question closed on main — 2026-09-29T07:27:51Z

`04ba5fb` (Gopal Patwa, 2026-09-29 00:27 -0700) replaced the intent's open-question
paragraph with the owner's verbatim answer ("Don't tick it; stay on the short path") and
a pointer to `APPROVAL_RECORD-4.md`, and dropped "one open question is still open" from
the banner. Only the header line and the Open questions section changed. Verified on
`main` by the Orchestrator; merged; `runs/docs-retrieval/intent.md` re-copied unchanged.
The intent now has no open question, so the "stale text" note above no longer applies.
