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
