# Slice Plan — docs-retrieval-3

- **Intent:** `runs/docs-retrieval-3/intent.md` (byte-identical to `intents/docs-retrieval-3.md` at 2534f13; confirmed by the owner 2026-09-30). No open questions: Decisions 1–3 are settled.
- **One-line outcome:** add a local cross-encoder reranker over slice 2's `file-rrf-v1` top candidates, then score it once on a fourth held-out set (gate: ≥80% of answerable questions, a correct file in the top 5).
- **Playbook:** `/Users/gopalpatwa/opt/agentic-sdlc-playbook` @ 383058a (resolved against the main checkout; held-out rules in `project-packs/ai-agent-product.md` "Held-out gates"). **Pack:** v12. **Project pack:** ai-agent-product. **Release tier (proposed):** 2; the Release Manager confirms.
- **Base:** branch `claude/docs-retrieval-3` at 36c9cff (main, pack v12). Suite green at start (122 passed, mypy, ruff).
- **Depth:** standard. Adversarial is not earned: nothing here changes auth or a safety control; the new download is covered by the rule 4/5 approval of the specific model.

## Success criteria (intent "Done means")

1. Starts from main: `file-rrf-v1`, the 123-file corpus, pack v12; corpus, first stage and embedding model unchanged.
2. Local reranker over the first stage's top-N (Architect proposes N on general grounds). Reads text, never produces it. Exact revision, per-file sha256, ONNX Runtime + numpy only, no PyTorch, no `trust_remote_code`. **Needs the owner's own rule 4 and 5 approval of the specific model (revision, file hashes, source) before anything is installed or downloaded.**
3. Freeze first: method commit recorded; then a fourth held-out set (≥15 answerable) with labels reviewed by a fresh QA spawn before the owner commits it; a **different** fresh QA spawn scores it once.
4. Gate: ≥80% of answerable, a correct file in the top 5. Unanswerable is diagnostic.
5. Three earlier sets reported as diagnostics, with `file-rrf-v1` on the same sets, so the reranker's effect is visible.
6. Earlier guarantees hold: deterministic ingest, provenance on every passage, no generative model, no network outside ingest/CI setup, every model file hash-checked.

## Non-goals

Any generative model (incl. LLM reranking, query rewriting); hosted reranking/embedding APIs; abstention (check-step slice, Decision 3); CI; Azure/API keys/deploy.

## Constraints (from `.agentic/`, the intent and SAFETY_INVARIANTS)

INV-4 (a model may only rank; never produces, selects fragments of, or alters returned text) and INV-5 (egress limited to the two pinned downloads, made only by `ingest`; every model file sha256-checked before use; no question or passage text leaves the machine; INV-5 must be extended for the reranker's files, which is a rule 4 edit). Nothing is chosen by its score on any eval set: the reranker, N, and how its score combines with the first stage are argued before the run. One fresh spawn per stage; no resumes across passes. Retrieve stays offline.

## Budget (intent Decision 1): 600k total, split at the freeze

Units are peak context per spawn (RUN_ECONOMICS). **Slice A (this run, `docs-retrieval-3`): 330k.** **Slice B (`docs-retrieval-3-proof`, opened at the freeze): 270k.** Overrun stops and asks with the numbers; the budget is never raised to fit.

## Stages

| # | Stage | Role | Est. | Notes |
|---|-------|------|------|-------|
| 1 | Scope Review | engineering-manager | 40k | Confirms compression, the A/B split, stage estimates; flags approval triggers |
| 2 | Architecture | software-architect | 110k | One fresh spawn. Proposes the specific reranker (revision, file list, source, size, licence), N, score combination, INV-4/INV-5 deltas. **Writes the approval request; nothing is downloaded.** |
| — | **STOP: owner approval** | human | — | Rules 4 and 5, of the specific model; plus the INV-5 wording. Owner's own words in this session only |
| 3 | Implementation | backend-architect | 130k | Pins hashes, fetch in `ingest` only, ONNX rerank, tests (offline default), full regression. Never runs eval against any set |
| 4 | Freeze | Orchestrator | — | Record the method commit; open slice B; owner hands over the draft fourth set |
| B1 | Label review | qa-evidence (fresh) | ~60k | Gets only the draft set and the pinned docs |
| B2 | Scoring | qa-evidence (a different fresh spawn) | ~90k | Scores once; earlier sets and `file-rrf-v1` as diagnostics |
| B3 | Security, Release Gate, Post-Launch | security-privacy, release-manager, post-launch-learning | ~120k | Security and Release only if the gate passes |

Product Manager, UX, UI and the Tech Writer are skipped (no user-facing surface; docs prose refresh deferred as in slice 2). Gates never compress.

## If the gate fails

Failure loop (cap 2); nothing ships; the next move is a new intent and a new fifth set.

## Budget amendment (owner, 2026-10-01)

Owner moved 30k from slice B to slice A: **A 360k, B 240k**, total 600k unchanged (his words are in STATE.md Budget). Slice B stage estimates (60k + 90k + 120k = 270k) now exceed 240k by 30k: if B runs short, stop and ask the owner with the numbers.
