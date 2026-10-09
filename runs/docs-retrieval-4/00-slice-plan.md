# Slice Plan — docs-retrieval-4

- **Intent:** `runs/docs-retrieval-4/intent.md` (byte-identical to `intents/docs-retrieval-4.md` at dd896c9; confirmed 2026-10-01). No open questions: Decisions 1–3 are settled.
- **One-line outcome:** make `file-rrf-v1` the default ranking (reranker opt-in only, no reranker files loaded or fetched by default), fix the intermittent shutdown crash (exit 134), run Security Review and the Release Gate once; verdict "internally releasable, not announced".
- **Playbook:** `/Users/gopalpatwa/opt/agentic-sdlc-playbook` @ 931650b (resolved against the main checkout; the relative path does not resolve from a worktree). **Pack:** v14. **Project pack:** ai-agent-product. **Release tier (proposed):** 2; the Release Manager confirms.
- **Base:** branch `claude/docs-retrieval-4` = main (5e35082, pack v14) + merge of `claude/docs-retrieval-3` (2f42a20), merge commit 6591bf3, no conflicts; `.claude/` and `AGENTS.md` untouched. Not behind main. Suite green at start (mypy, ruff, 157 passed, 10 deselected).
- **Depth:** standard overall; **adversarial for Security Review of the model download path and INV-4 / INV-5**, standard elsewhere (owner's instruction).

## Success criteria (intent "Done means")

1. Starts from main with `claude/docs-retrieval-3` merged; slice 3's `runs/` kept as the record. (Done at intake.)
2. `file-rrf-v1` is the default in `retrieve` and `eval`; `--ranking file-rerank-v1` still works and is off unless asked. Default runs load no reranker files and make no reranker download; reranker files are fetched only on opt-in.
3. Shutdown crash fixed or explained: 20 consecutive runs exiting 0 in **each** ranking mode, run on `evals/retrieval.toml` (the oldest set), never the fourth. The Architect argues the cause from how ONNX Runtime holds two sessions, not by trial against a gate set.
4. No new gate set, no tuning. The Release Gate runs the default once on the fourth set as a regression check; the other sets are diagnostics only. **No release claim** (Decision 1).
5. Security Review and Release Gate run once, tier 2, no deploy, nothing posted. Verdict: "internally releasable, not announced". MS MARCO licence: recorded as "not applicable to the default path, still open for anyone who opts in".
6. `.agentic/SAFETY_INVARIANTS.md` INV-5 keeps naming both models' pins plus one sentence: the default path fetches only the embedding model. **Rule 4 approval, owner's own words in this session.**
7. Stale "plain code" wording in `.agentic/PROJECT_CONTEXT.md` and the README status line updated to match what shipped; `LOCAL_COMMANDS.md` / `CURRENT_MVP_STATUS.md` default-ranking statements brought in line.
8. Earlier guarantees hold: deterministic ingest, provenance on every passage, no generative model, no network outside ingest/CI setup, every model file hash-checked, retrieve offline.

## Non-goals

New method, new gate set, any tuning, new dependency/model/download, generative model, abstention (check-step slice), CI (`docs-retrieval-ci`), Azure/API key/deploy, push/PR/merge (owner only).

## Constraints (from `.agentic/`)

INV-4 (a model only ranks), INV-5 (egress limited to the two pinned downloads, ingest only, sha256-checked before use, nothing user-side leaves the machine). Must not break: nothing retrieved presented as an answer; provenance visible; question and docs stay on the machine. One fresh agent per stage; none resumed across passes. Nothing is chosen by its score on any eval set.

## Budget (intent Decision 3): 400k, no split

Units are peak context per spawn (RUN_ECONOMICS). Overrun stops and asks with the numbers; the budget is never raised to fit. Proposed estimates below total 390k with 10k headroom, which is thin; the Engineering Manager must confirm or compress them at Scope Review.

## Stages

| # | Stage | Role | Est. | Notes |
|---|-------|------|------|-------|
| 1 | Scope Review | engineering-manager | 50k | Confirms compression and estimates; flags approval triggers; file cap |
| 2 | Architecture | software-architect | 70k | One short tech spec: default switch, opt-in-only reranker load, crash cause argued from two ORT sessions on general grounds, INV-5 sentence. **Writes the rule 4 approval request with exact wording; nothing is edited in `.agentic/SAFETY_INVARIANTS.md` yet** |
| — | **STOP: owner approval** | human | — | Rule 4: INV-5 sentence. Owner's own words in this session only |
| 3 | Implementation | backend-architect | 100k | Default switch, lazy reranker load, crash fix, tests, wording fixes, INV-5 sentence after approval. Crash reproduction on `evals/retrieval.toml` only; 20 consecutive exit-0 runs per mode. Full regression |
| 4 | Security Review | security-privacy | 70k | Adversarial: model download path, INV-4, INV-5. Standard: the rest. Records MS MARCO position |
| 5 | Release Gate | qa-evidence (one regression run on the fourth set) then release-manager | 70k | Fourth set once as regression check; other sets diagnostic; verdict "internally releasable, not announced" |
| 6 | Close-out | post-launch-learning | 30k | Records the lesson and carry-forward to the check-step slice |

Product Manager, UX, UI, Market Research and Tech Writer are skipped (no user-facing surface; the wording fixes are inside Implementation). Gates never compress.

## If a gate fails

Failure loop (cap 2 per stage); then blocked-on-failure and escalate to the owner with the numbers.
