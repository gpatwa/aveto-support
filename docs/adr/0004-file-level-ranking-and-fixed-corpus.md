# ADR 0004: Rank files, not passages, over a fixed allow-listed corpus of user documentation; retrieval no longer abstains

> Architecture Decision Record. Owned by the Architect. Never edited after it is
> accepted. A changed decision gets a new ADR that supersedes this one.

- **Status:** proposed (becomes accepted if slice B `docs-retrieval-2-proof` passes its gate)
- **Date:** 2026-09-29
- **Slice:** `runs/docs-retrieval-2/` (slice A, method to freeze). Full specification, with every parameter: `runs/docs-retrieval-2/02-tech-spec.md`.
- **Supersedes:** the **ranking** part of [ADR 0003](0003-hybrid-embedding-retrieval.md) (passage-level RRF with a per-file cap) and the **abstention** parts of [ADR 0002](0002-lexical-retrieval-calibrated-abstention.md) and ADR 0003 ("no confident match returns no passages"; dense confidence as a gate). The model, its pin, int8 embeddings, heading passages, BM25 parameters and RRF k = 60 stand.

## Context

Slice 1's method found a correct file in the top 5 for 8 of 17 held-out questions (close-out §2, aggregate only). Its close-out named two untested hypotheses: the corpus includes maintainer material, and the method ranks passages while users ask for, and the eval scores, files. The owner's intent (`docs-retrieval-2`) fixes three decisions: abstention moves to the future check step (Decision 1; rule 4, Approvals 1 and 2); the corpus is a named list of user documentation (Decision 2); the only model stays bge-small (Decision 3). Done means 2 and 3 require the corpus in config and file-level results with passages, headings and line ranges.

**Disclosure.** The corpus list and the ranking method were chosen on general grounds, before any run, and nothing was chosen by its score on any eval set. The decider (the owner's intent, and this Architect) has seen slice 1's failure in aggregate, and the intent discloses that `docs/BACKLOG.md` and `docs/ARCHITECTURE.md` appeared in slice 1's wrong answers. The exclusions are argued from audience (maintainer material vs user documentation). This Architect did not read any eval file, any eval-run output, or any per-question result.

## Decision

1. **Corpus as an allow-list in `docs-source.toml`** (`include`, required): `README.md`; eleven named files in `docs/`; everything under `agents/`, `templates/`, `project-packs/`, `prompts/`, `skills/`, `examples/`, `execution/`. A file matching no entry is not indexed. Ingest fails (exit 2) if an entry matches no file. The list changes only by a new decision, never after a run.
2. **File-level ranking `file-rrf-v1`:** a lexical file list (whole-file BM25) and a dense file list (each file's best passage similarity, MaxP) are fused by reciprocal rank fusion, k = 60. The top 5 files are returned, each with its 2 best passages (by the same fusion within the file), heading, line range and permalink. All parameters are pre-registered in the tech spec and recorded in the index params; there is no threshold, no word-, path- or question-specific rule, and no weight to tune.
3. **Retrieval never abstains.** `retrieve` always returns its top files and the top score (best passage similarity), with the ingest-time calibrated similarity printed as a reference only. The calibration and the frozen off-topic list are kept as that diagnostic. The eval gates only on answerable top-5 file recall (at least 80%); unanswerable questions and top scores are printed as diagnostics.

## Alternatives considered

- **Passage-first ranking grouped by file** (ADR 0003's shape): the wrong unit; it does not combine evidence from different sections of one file, and many-section files crowd the list.
- **Sum, count or top-k sum of passage scores per file:** grows with file length or adds a k with no principled value.
- **Mean-pooled file embeddings:** dilute a single relevant section; a whole file does not fit the model's 512 tokens.
- **Weighted blend of normalised BM25 and cosine** (incl. slice 1's `file_lambda`): a tuning weight over incomparable scales.
- **Deny-list corpus** (`exclude`): a new maintainer file would enter the index by default; rejected for an allow-list that fails closed.
- **Removing the calibration entirely:** would change the index schema, `test_index.py` and about eight calibration tests for no gain in this slice; kept as a labelled diagnostic instead.
- **A reranker or larger model:** out of scope (Decision 3); the next slice's question if this fails.

## Consequences

- Easier: results match the question users ask ("which doc") and the unit the eval scores; the corpus is auditable in one config key; an index built by slice 1's code is rejected at load.
- Harder: nothing in retrieval says "the docs don't answer this". **Carry-forward, not dropped:** the check-step slice (where a model reads the passages, README step 4) must carry the abstention requirement forward, with its own eval of unanswerable questions; slice B's close-out lists it as a follow-up. Until then, output states "These are sources, not an answer."
- MaxP mildly favours long, many-section files; accepted rather than adding a normalisation knob.
- Revisit if slice B's single held-out run fails the 80% gate (then a reranker is the next question, with a fresh held-out set and a new rule 4 approval), or when the check step lands.
