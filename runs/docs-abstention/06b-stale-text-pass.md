# 06b Stale-text pass (Tech Writer)

Authority: APPROVAL_RECORD-8. Verified against code: `search.py` retrieve docstring "Never abstains"; `__main__.py` ingest prints the reference similarity as "diagnostic, retrieval does not abstain"; `evaluate.py` reports unanswerable as "diagnostic only, not gated".

## Applied

| File | Lines (before) | Before | After |
|---|---|---|---|
| README.md | 3-4 status | "...internally releasable, not announced" | "not released and not announced"; never abstains; abstention not built; no threshold/margin rule separated unanswerable from answerable on seen sets; tried judge model failed its seen-set check, not adopted; no end-to-end result (no figures) |
| README.md | 49-51 | "...or `no confident match`. It never writes an answer." | Top-five-files passages with path, heading, lines, permalink, top score; never abstains; never writes an answer |
| README.md | 71-74 (found by grep, same staleness) | Off-topic list "used to calibrate 'no confident match'"; ingest warns abstention is too permissive | List yields a reference similarity printed for information; decides nothing |

## BLOCKED by the write-scope guard (not applied)

The hook allows the Tech Writer only runs/, README.md, CHANGELOG.md, docs/ (and ARCHITECTURE.md is owned by the Architect); `.agentic/CURRENT_MVP_STATUS.md` is outside scope. Both need the owner path (Architect / Security A1 route). Proposed edits, ready to paste:

### docs/ARCHITECTURE.md (Architect)
- L22: "The model ranks passages and decides confidence, and it never writes text." -> "The model ranks passages, and it never writes text."
- L27: `RetrievalResult (≤5 passages | no confident match)` -> `RetrievalResult (top 5 files, passages, top score)`
- L39: "dense-confidence calibration" -> "reference-similarity calibration (diagnostic)"
- L85-87: node text "...· dense top-1 ≥ τ ?" -> "...· never abstains"; delete the `confident`/`not confident` branches and the `none[no confident match]` node; single edge `retrieve --> hits[top 5 files, best passages<br/>path · heading · lines · permalink · top score]`
- L109-112: replace "It is confident only if ... `no confident match` and **no** passages." with: "It returns verbatim passages from the top five files, each with path, heading, line range and permalink, plus the top score. It never abstains: a question the docs do not answer still returns files. The ingest-time τ is printed as a reference similarity and decides nothing."
- L132-134: "If there is no confident match, it escalates." -> "Retrieval never says the docs do not answer, so the drafter cannot rely on it for that; how a drafter decides not to draft is open work (abstention is not built)."
- L141-142: "Retrieval returns only verbatim passages, or "no confident match" with none." -> "Retrieval returns only verbatim passages and does not abstain." Keep "A model may **only** rank passages and decide confidence..." matching INV-4.
- L147-148 (extra, same staleness): "**Grounded or silent.** Below the calibrated threshold, nothing is shown..." -> "**Not silent when the docs do not answer.** Retrieval always returns the top files, even for a question the docs do not answer. Abstention is not built."
- L103, L79-80: ingest "calibrates τ" is still true of the code but should read "computes a reference similarity (diagnostic)". L186-191 ADR summaries mention calibrated abstention/dense confidence; ADRs are out of scope, leave as history.

### .agentic/CURRENT_MVP_STATUS.md lines 11-16 (owner path)
Replace the `retrieve` bullet with: "`retrieve`: returns verbatim passages from the top five files with path, heading trail, line range and a permalink at the pinned commit, plus the top score. It never abstains: a question the docs do not answer still returns files. Ranking is hybrid: BM25 (Porter stemming, passage plus file evidence) fused with dense similarity by reciprocal rank fusion. The ingest-time reference similarity is printed for information and decides nothing." Add bullet: "Abstention is not built. Slice `docs-abstention` measured that no score-threshold or margin rule separates unanswerable from answerable questions on the seen sets, and a tried local judge model failed its seen-set check, so the owner stopped that path. There is no end-to-end figure, and nothing here claims production readiness or that drafting is safe to build on." (Line 26 is true as is. Also line 35-36 "Not yet done" is fine.)

## Final grep
README.md: no remaining `no confident match`/abstain/confident staleness. docs/ (excl. adr/): remaining hits are the blocked ARCHITECTURE lines above. Not touched: INV text, LOCAL_COMMANDS.md, code, ADRs.
