# Approval Request 1 — drop the unanswerable half of the eval gate for this slice (rule 4)

- **Slice:** docs-retrieval-2
- **Rule:** HUMAN_APPROVAL_RULES §4 — changes to safety controls (the plan must call it out and the owner must approve before implementation begins)
- **Requested:** 2026-09-29T16:52:18Z, at Intake, before any implementation. The intent's own header asks the Orchestrator to take the owner's yes in its session.

## What

For **this slice only**, gate retrieval on one thing: a correct file in the top 5 for at least 80% of the *answerable* questions in a fresh, owner-committed held-out set (at least 15 answerable). The first intent's second half — at least 80% of *unanswerable* questions returning "no confident match" — stops being a gate here. Unanswerable questions, if the held-out set includes any, are printed as a diagnostic. This is intent Decision 1.

Abstention (the docs don't answer this) is **moved, not dropped**: the intent says the check step, where a model reads the passages, must carry the requirement forward. That check step does not exist yet.

## Why

Two methods (lexical v1; embed-v3) failed to decide "answerable vs not" from a similarity score: answerable and unanswerable questions score in the same band (slice 1: 5/17 answerable withheld or wrong, unanswerable 5/6 only by withholding almost everything). The design already has a check step for it.

## What is reversible if denied

Everything: nothing is built yet. The slice would keep both halves of the gate, so it would need a held-out set with at least 5 unanswerable questions and would have to keep retrieval's own confidence cutoff working (and calibrated) alongside the new ranking, which slice 1 showed is hard.

## The smallest request

This slice's gate only. It does not change INV-1 to INV-5 as written, and it does not relax the product's "grounded or silent" stance: that stays a requirement of the next slice's check step. It is not approval for retrieval to stop abstaining (that is Request 2).
