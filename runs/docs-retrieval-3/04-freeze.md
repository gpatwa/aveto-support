# Freeze — docs-retrieval-3 (slice A)

- **Method commit (frozen):** `8499c2a778b739b08cc41e7fa2ac24e46ce3422c` — `file-rerank-v1` over `file-rrf-v1`, the 123-file corpus, pack v12. Recorded 2026-10-01, before any fourth held-out set exists in the repo (the Orchestrator has seen none; `evals/` holds only the three earlier sets and the calibration list, all unchanged since `36c9cff`).
- **Method files** (must not change after this point; slice B's QA diffs them against HEAD): `aveto_support/` (all), `docs-source.toml`, `pyproject.toml`, `uv.lock`, `tests/`, `.agentic/SAFETY_INVARIANTS.md`, and the three earlier eval files.
- **Regression after the commit** (Orchestrator re-run, not only the Implementer's): mypy clean, ruff clean, `pytest` 157 passed, `pytest -m model` 7 passed. Two `ingest` runs gave the same index sha256 `f36ef5d4…a756`, equal to slice 2's (Implementer's report, `03-implementation.md`).
- **Pinned reranker:** `cross-encoder/ms-marco-MiniLM-L6-v2` @ `233902d25c440f23af6f7d6e94d2946bac0bee0a`; `onnx/model.onnx` sha256 `5d3e70fd…4d4a`, `vocab.txt` sha256 `07eced37…38a3` (A1, `APPROVAL_RECORD-1.md`).
- **Known cosmetic deviation, accepted:** `evaluate.py` hardcodes the label `file-rrf-v1` in its report header; `__main__` replaces it with the method that ran, and `eval` prints `Ranking:` first. Not fixed, because editing `evaluate.py` after the freeze would touch a method file. QA reads the `Ranking:` line.
- **Open for release, not for scoring:** the MS MARCO licence question (owner's condition, `APPROVAL_RECORD-1.md`).
- **Slice B:** `runs/docs-retrieval-3-proof/`, budget 240k (owner, this session).
