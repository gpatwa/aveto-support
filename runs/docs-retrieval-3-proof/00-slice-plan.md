# Slice Plan — docs-retrieval-3-proof (slice B)

- **Continues:** `runs/docs-retrieval-3/` (slice A, closed at the freeze; `04-freeze.md`). **Intent:** `runs/docs-retrieval-3-proof/intent.md`, byte-identical to `intents/docs-retrieval-3.md`. Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook`.
- **Frozen method:** `8499c2a778b739b08cc41e7fa2ac24e46ce3422c` (`file-rerank-v1`).
- **Gate:** a correct file in the top 5 for ≥ 13 of the 16 answerable questions of the fourth set, once. Unanswerable is diagnostic. The three earlier sets, with `file-rrf-v1` on the same sets, are diagnostics only.
- **Budget (owner):** 240k (slice A got 360k). Stage estimates below total 270k; if B runs short, stop and ask the owner with the numbers.
- **Draft set:** from the owner's "Aveto AI SDLC" session, outside the repo until reviewed; sha256 of the draft as received `0b29e2c7557ea594ad65e46d29dbf620b749a1fe06771497123942e3187f9855`.

| Stage | Role | Est. | Notes |
|-------|------|------|-------|
| B1 Label review | qa-evidence (fresh spawn #1) | 60k | Sees only the draft set and the pinned docs (123 files); no method, spec, results, earlier sets; no retrieve or eval |
| — | **Owner commits the reviewed set** | — | Owner's own act |
| B2 Scoring | qa-evidence (a DIFFERENT fresh spawn) | 90k | Scores once; earlier sets and `file-rrf-v1` as diagnostics; verifies no method file changed since 8499c2a |
| B3 Security / Release Gate | security-privacy, release-manager | 60k | Only if the gate passes; Release blocks on the MS MARCO licence question |
| B4 Post-Launch | post-launch-learning | 60k | Smoke depth, either outcome |

## The committed set (Orchestrator's note, 2026-10-01)

The owner committed `evals/retrieval-heldout-4.toml` at `431486e` (main), after the freeze (`8499c2a`). It is NOT byte-identical to the reviewer's `retrieval-heldout-4.reviewed.toml`: the owner's version drops `docs/AGENTIC_SDLC.md` from every question's sources (the reviewer had added it to 12) and trims some other additions (for example `project-packs/enterprise-saas-future.md`, `docs/AGENT_ROLES.md`, `docs/GETTING_STARTED.md`, `execution/README.md`, `execution/pack/AGENTS.md`), keeping the rest. That is the owner's call before commit and before any result; the committed file is the gate, labels fixed. 16 answerable + 4 unanswerable; sha256 `180cfc0b5505935b02e92a3f96dba2f0bf5799af71ed36ea9d855cdfdcc48aee`. Merged into this branch at `0be91a4`; `git diff 8499c2a HEAD` over method files and the earlier eval files is empty.
