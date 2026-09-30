# Tech Spec — docs-retrieval-2 (slice A: method to freeze)

> Owner: Software Architect Agent (Stage 7, depth standard)
> Status: ready for implementation
> Source: short path, no PRD/UX. `runs/docs-retrieval-2/intent.md` (Decisions 1 to 3 fixed), `01-scope.md`, `APPROVAL_RECORD-1.md`, `APPROVAL_RECORD-2.md` (incl. Clarification).
> ADR: `docs/adr/0004-file-level-ranking-and-fixed-corpus.md`

**What I did not read.** No third held-out set (none exists). Not `evals/retrieval.toml`, `evals/retrieval-heldout.toml`, `evals/calibration-offtopic.toml`, any `runs/docs-retrieval/eval-run-*.txt`, or any per-question result from slice 1. From slice 1's close-out I read sections 1, 2 and 5 only (aggregate numbers and hypotheses). Nothing below is chosen by a score on any set; every parameter is fixed here, before any run.

## Summary

Two changes to the method, none to the machinery. (1) **Corpus:** `docs-source.toml` gains a required allow-list `include` holding exactly intent Decision 2; ingest reads only `.md` files matching it, and fails (exit 2) if any entry matches no file. (2) **Ranking:** `retrieve` ranks **files**, not passages: a lexical file list (whole-file BM25, already built in slice 1 as `_file_corpus`) and a dense file list (each file scored by its best passage, "MaxP") are fused by reciprocal rank fusion (k = 60). It returns the top 5 files, each with its 2 best passages (heading, line range, permalink), plus the top score. There is no confidence rule and no "no confident match" (Approvals 1 and 2); abstention moves to the future check step (ADR 0004). The eval gates on answerable top-5 file recall only. Same model, same embeddings, same index schema, `embed.py` untouched.

### Done-means trace

| Done means | Satisfied by |
|---|---|
| 2 Corpus fixed in config, exactly Decision 2 | `include` in `docs-source.toml`; §Data model; tests `test_committed_config_include_is_decision_2`, `test_read_markdown_admits_only_included_paths`, `test_include_entry_matching_no_file_fails` |
| 3 File-level ranking, passages with heading and line range | `search.retrieve` → `RetrievalResult.files`; §Ranking method; §Output |
| 4 (first half) freeze and recorded commit | §Freeze scope (method files listed) |
| 7 build side: deterministic ingest, provenance, no generative model, offline retrieve/eval, hashes | unchanged machinery; §Test plan keeps every INV-4/INV-5 test (one retirement, owner-approved) |
| C1 PROJECT_CONTEXT line | one-line task to product-manager (§Hand off) |
| C2 abstention carry-forward | ADR 0004 "Consequences"; §Risks |

## Data model deltas

| Type | Change | Rationale |
|------|--------|-----------|
| `docs-source.toml` `include` | **new, required** list | Decision 2 as an allow-list: a file in neither list is out by default |
| `docs-source.toml` `exclude`, `[embedding].offtopic_*` | unchanged (`exclude = []`) | `exclude` still applies after `include`; off-topic list kept for the diagnostic (below) |
| `ingest.SourceConfig` | new field `include: tuple[str, ...]` (no default) | carried from config |
| `index.RetrievalParams` | `ranking` `"ranking-v2"` → `"file-rrf-v1"`; `confidence` `"corroboration-v1"` → `"none"`; `file_lambda` **removed** | the index records the method truthfully; an index built by slice 1's code (126 files, ranking-v2) is rejected at load ("different retrieval parameters", exit 2) instead of being scored silently |
| `index.SCHEMA`, `Passage`, `Index`, `EmbeddingParams` | **unchanged** | file-level scoring is computed at query time from existing passage text, paths and int8 vectors; no new index data |
| `search.Hit`, `Analysis`, old `RetrievalResult` | removed / replaced | see below |
| `evaluate.EvalReport`, `QuestionOutcome` | modified | answerable-only gate |
| Eval file schema (`pinned_commit`, `[[question]]` with `id`, `question`, `answerable`, `sources`, `hard_negative`) | **UNCHANGED** | one loader rule added: at least one answerable question (else exit 2). The owner's third set needs no change. |

**Corpus allow-list** (committed in `docs-source.toml`, in this order):

```toml
# User documentation only (intent Decision 2). Allow-list: a file matching no
# entry is not indexed. "x.md" = exactly that file; "dir/" = every .md under it.
# Deliberately absent (maintainer material): docs/BACKLOG.md, docs/ARCHITECTURE.md,
# docs/PLATFORM_EVAL.md, runs/, site/.
include = [
  "README.md",
  "docs/GETTING_STARTED.md", "docs/AGENTIC_SDLC.md", "docs/AGENT_ROLES.md",
  "docs/HUMAN_APPROVAL_RULES.md", "docs/RELEASE_GATES.md", "docs/OPERATING_MODEL.md",
  "docs/DEPLOYMENT.md", "docs/STANDARDS_WATCH.md", "docs/VALIDATION_MATRIX.md",
  "docs/PIPELINE_ANALYTICS.md",
  "agents/", "templates/", "project-packs/", "prompts/", "skills/", "examples/", "execution/",
]
```

Validation (`load_source_config`, `ConfigError` → exit 2): key present; non-empty list of strings; no duplicates; each entry repo-relative (no leading `/`, no `..` segment); each entry ends in `.md` (exact file) or `/` (directory). Matching (`read_markdown`): `rel == entry` for file entries, `rel.startswith(entry)` for directory entries (the trailing `/` stops `agents/` matching `agents-old/`), case-sensitive; then the existing `.md` and `exclude` rules. After reading, `run_ingest` raises `ConfigError("include entry <e> matches no .md file at <commit>")` for any entry that matched nothing, so a typo cannot silently shrink the corpus. `commit` is unchanged (`3a83b669…`); intake counted 123 in-scope `.md` files there.

**Calibration and off-topic list: kept, as a diagnostic.** Ingest still computes the dense-null-v3 threshold (unchanged code, unchanged index fields `threshold`, `tau_salad`, `tau_offtopic`) and still hash-checks the frozen off-topic list. Nothing gates on it. It is printed as a *reference similarity* next to the top score, so the top score is interpretable and the future check step has a documented baseline. Removing it would bring `index.py` schema, `test_index.py` and eight calibration tests into scope for no gain in this slice. Byte-identical ingest still holds (same deterministic code path; only the file set and two param strings differ).

## Ranking method `file-rrf-v1` (pre-registered)

**Argument (general grounds only).** The user asks "which doc", and the eval scores files, so the ranked unit should be the file. A file's evidence is spread across its sections (the title in H1, the specific term in a subsection); ranking passages and deduplicating afterwards lets a file with many near-duplicate sections crowd the list and never adds up evidence that sits in different sections of one file. Classical document retrieval scores the document as the unit (BM25 over the whole document, length-normalised), and passage-based neural ranking aggregates to the document by its best passage (MaxP, Dai & Callan 2019), because a document is relevant if some part of it is. Lexical and dense scores live on incomparable scales, so they are combined by rank (RRF, Cormack et al. 2009, k = 60), which has one literature-standard constant and no weight to tune; RRF is already the approved fusion in ADR 0003.

**Steps** (all at query time, from the existing index):

1. Question with no words (`not question.strip()` or `embedder.token_count(question) == 0`) → `QuestionError` (exit 2). Index with no passages → `IndexFormatError` (exit 2). Otherwise always proceed.
2. `terms = sorted(set(tokenize(question)))` (tokenizer v2, NLTK-179 stopwords, Porter 1980: unchanged). `query = embedder.embed_query(question)` (bge-small, query prefix, CLS, int8: unchanged). `sim[p] = dot(query, p) / 127²` for every passage (one matrix product, existing `DenseMatrix`).
3. **Lexical file list LF:** files with whole-file BM25 > 0 (existing `_file_corpus`: every passage's full text plus path tokens × `path_weight` 1; k1 1.2, b 0.75), ordered by (−score, path).
4. **Dense file list DF:** every file, score = max `sim[p]` over its passages (MaxP), ordered by (−score, path).
5. **File score** = Σ over {LF, DF} (in that order) of `1 / (60 + rank)`, each list cut at `fusion_depth` 100 (unchanged; about 123 files, so it trims at most the tail). Order by (−score, path). Keep the top `top_k` = 5 (fewer only if the index has fewer files).
6. **Matched passages per file:** within the file, a lexical list (its passages with passage-BM25 > 0; existing passage bag: body + heading × 2 + path × 1; ordered −score, line_start) and a dense list (all its passages, ordered −sim, line_start), fused by the same RRF (k 60, depth 100); order (−score, line_start); keep `per_file_cap` = 2. Every file has at least one passage in its dense list, so every returned file carries 1 or 2 passages.
7. `top_score` = max `sim[p]` over the whole index (the same quantity slice 1 called `dense_top1`; model-scale, comparable to the reference similarity).

**Parameters, fixed here and recorded in the index params:** tokenizer v2, stopwords nltk-english-179, stemmer porter-1980, k1 1.2, b 0.75, heading_weight 2, path_weight 1, rrf_k 60, fusion_depth 100, top_k 5 (files), per_file_cap 2 (passages per file), dense aggregation MaxP, lists fused {lexical-file, dense-file}, ties by path then line_start, no threshold. Every value except the ranking label, MaxP and the file unit is carried unchanged from slice 1's frozen code; none is to be set after a run. There is no synonym table, no rule keyed to a word, file, path or question, and no per-file weight.

**Alternatives considered and rejected**

| Alternative | Why rejected |
|---|---|
| Passage-first ranking, then group by file (slice 1's embed-v3 shape) | Wrong unit: does not combine evidence across a file's sections; many-section files crowd the top 5 |
| Sum or count of passage scores per file | Grows with file length; needs a normalisation choice (a knob) |
| Mean of passage embeddings as a file vector | Dilutes one relevant section inside a long, multi-topic file; bge-small cannot embed a whole file (512 tokens) |
| Sum of top-k passages per file | Adds k, a knob with no principled value |
| Weighted linear blend of normalised BM25 and cosine (incl. slice 1's `file_lambda`) | Needs a weight and a normalisation; scales are incomparable |
| Dense only, or lexical only | Throws away one of the two approved signals; each fails on different question shapes (exact terms vs paraphrase) |
| Extra field boosts (titles, H1) beyond the existing heading × 2 / path × 1 | New weights = knobs; the existing weights stay |
| Reranker, larger model, query rewriting, synonyms | Out of scope (Decision 3, intent "Out of scope"); synonyms are rules keyed to words |

## Service surface

| Function | Signature | Invariant |
|----------|-----------|-----------|
| `ingest.py:load_source_config` | `(Path) -> SourceConfig` | `include` required and validated as above; unknown keys still rejected |
| `ingest.py:read_markdown` | unchanged signature | returns only `.md` files matching `include`, minus `exclude`, sorted by path |
| `ingest.py:run_ingest` | unchanged signature | `ConfigError` if any `include` entry matched no file; otherwise as today |
| `search.py:rrf` (new, module-level) | `(lists: Sequence[Sequence[K]], k: int, depth: int) -> dict[K, float]` | pure; sums in list order; caller orders |
| `search.py:Searcher.rank` | `(terms) -> list[tuple[Passage, float]]` | now pure passage BM25 (file blend removed); candidates > 0; ties path, line |
| `search.py:Searcher.file_lexical` (new) | `(terms) -> list[tuple[str, float]]` | whole-file BM25 > 0; order (−s, path) |
| `search.py:Searcher.file_dense` (new) | `(sims) -> list[tuple[str, float]]` | MaxP per file; every file; order (−s, path) |
| `search.py:retrieve` | `(Searcher, str) -> RetrievalResult` | never abstains; 1..5 files; raises `QuestionError` / `IndexFormatError` only for no words / empty index; `PlaceholderEmbedder` still raises |
| `search.py:permalink` | unchanged; plus `file_permalink(repo, commit, path) -> str` | `https://github.com/{repo}/blob/{commit}/{escaped path}` |
| `evaluate.py:load_eval_set` | unchanged signature | also `EvalFormatError` if no answerable question |
| `evaluate.py:score` | `(Searcher, EvalSet) -> EvalReport` | answerable hit ⇔ some returned file path ∈ `sources`; unanswerable never counts |
| `__main__.py:format_result` | `(RetrievalResult, Index) -> str` | never prints "no confident match"; ends "These are sources, not an answer." |
| `__main__.py:main` | unchanged | catches `QuestionError` → exit 2 |

Removed from `search.py`: `Hit`, `Analysis`, `analyse`, `decide`, `capped`, `Searcher.fused`, `Searcher.corroboration`, `Searcher._rank_ids`' file blend. Kept unchanged: tokenizer, stemmer, `_Corpus`, `DenseMatrix`, `dense_ranked`, `calibrate`, `eligible_passages_by_file`, `body_tokens`.

**Result types** (`search.py`, frozen dataclasses):

```python
class QuestionError(ValueError): ...           # empty question -> exit 2

@dataclass(frozen=True)
class PassageMatch:
    passage: Passage            # verbatim, unchanged from the index
    score: float                # within-file RRF
    url: str                    # permalink(...) with #Lstart-Lend

@dataclass(frozen=True)
class FileHit:
    rank: int
    path: str
    score: float                # file RRF
    url: str                    # file_permalink(...)
    passages: tuple[PassageMatch, ...]
    # __post_init__: 1 <= len(passages); every passage.path == path; no repeated line_start

@dataclass(frozen=True)
class RetrievalResult:
    question: str
    files: tuple[FileHit, ...]
    top_score: float
    reference: float            # index.threshold; diagnostic only
    ranking_mode: str           # f"file-rrf-v1:hybrid:{model}@{revision}"
    generation_mode: Literal["deterministic"] = "deterministic"
    # __post_init__: files non-empty; ranks == 1..n; paths distinct; else ValueError
```

## Output and exit codes

`retrieve` (always this shape for a question with words):

```
Sources for: <question>
Docs: <repo> @ <commit>
Ranking: file-rrf-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c…  no text generated
Top score: 0.734 (best passage similarity; ingest reference 0.702, reported only: retrieval does not decide whether the docs answer)

1. docs/RELEASE_GATES.md  (score 0.0325)
   https://github.com/<repo>/blob/<commit>/docs/RELEASE_GATES.md
   a. lines 12-30  Heading: Release Gates > Tier 2
      https://github.com/<repo>/blob/<commit>/docs/RELEASE_GATES.md?plain=1#L12-L30
      | <first three non-blank body lines, verbatim, as today's _excerpt>
   b. lines 40-52  Heading: ...
2. ...

These are sources, not an answer.
```

`ingest` prints its threshold line relabelled `reference similarity: 0.702 (dense-null-v3 …; diagnostic, retrieval does not abstain)` and adds nothing else. Ingest warning texts are unchanged (slice B's prose refresh may reword "abstention").

`eval` (one `--eval-file` per run, CLI unchanged; slice B's QA runs it three times, and only the held-out run's exit code is the gate; the two earlier sets are diagnostics by process):

```
eval: <file>  index: <repo> @ <commit8>…  ranking: file-rrf-v1  reference similarity: 0.702 (diagnostic)
a01  HIT   docs/X.md (rank 2)  top score 0.73
a02  MISS  expected A | B; got f1, f2, f3, f4, f5  top score 0.66
u01  DIAG  top file docs/Y.md  top score 0.64 [hard negative]
answerable:   12/15 (80.0%)  required >= 80%  PASS
unanswerable: 3 (diagnostic only, not gated)
eval: PASS
```

`EvalReport(outcomes, answerable_hits, answerable_total, unanswerable_total)`, `passed = answerable_total > 0 and answerable_hits * 5 >= answerable_total * 4`. `ungated_recall`, `unanswerable_hits`, `unanswerable_pass` are removed (the gated number is now the ungated one).

| Exit | Meaning |
|---|---|
| 0 | success; `retrieve` always lists its top files; `eval` answerable ≥ 80% |
| 1 | `eval`: answerable below 80% |
| 2 | input or usage: config (incl. bad `include`, entry matching no file), index (incl. built for other params, empty), eval file (incl. no answerable question), commit mismatch, question with no words, missing model cache |
| 3 | fetch error (`ingest` only), unchanged |

## Adapter boundaries

| Boundary | Default adapter | Placeholder behaviour |
|----------|-----------------|------------------------|
| Query/passage embedding (`embed.py`, **unchanged**) | `OnnxEmbedder` (pinned bge-small, sha256-checked) | `PlaceholderEmbedder` raises; `Searcher` defaults to it, so `retrieve` without an injected embedder raises (existing test kept) |
| Everything else in retrieval | deterministic Python/numpy | n/a |

The model only produces the query vector used to rank; it never produces, selects fragments of, or alters returned text (INV-4 second sentence). No generative model; no network in `retrieve`/`eval`.

## Audit / feedback / usage events

None added or changed. The product has no event log; the only state change is `ingest` writing the index file, whose sha256 is printed (unchanged). `retrieve` and `eval` are read-only. Recorded rather than skipped.

## Integration points

- `index.load_index` / `RetrievalParams` — the params check now rejects slice 1 indexes (exit 2, re-run ingest).
- `ingest.fetch_archive`, `ensure_model_files` — unchanged; the re-ingest uses the already-approved pinned GitHub archive and cached, hash-checked model files; no new host (INV-5).
- `search._Corpus` (passage and file BM25), `DenseMatrix`, `calibrate` — reused unchanged.

## Test plan

Synthetic text only (FakeEmbedder, `make_archive`); **no eval question, from any set, appears in any test**; no `eval` run against `evals/` during design or build (01-scope §6 constraint 4). `test_committed_eval_set_is_well_formed` stays as a format check only.

**INV-enforcing tests (Security in slice B checks this list):**

| Test | INV | Action |
|---|---|---|
| `test_not_confident_returns_no_hits` (test_search) | INV-4 clause 2 | **RETIRED** (owner-approved, APPROVAL_RECORD-2 Clarification). Replaced by `test_retrieve_never_abstains` |
| `test_result_invariant_enforced` (test_search) | INV-4 | **Name kept, body rewritten to the file-level equivalent, at least as strong:** `ValueError` for empty `files`; ranks not 1..n; repeated path; `FileHit` with no passages; `FileHit` holding a passage from another path |
| `test_hybrid_hits_are_verbatim_passages` (test_search) | INV-4 | **Name kept, body iterates `result.files[*].passages`**: every `passage.text` equals the exact line slice of its source; also asserts `passage.path == file.path` |
| `test_retrieved_text_is_verbatim_slice_of_file` (test_index) | INV-4 | unchanged |
| All INV-5 tests listed in SAFETY_INVARIANTS, autouse network block | INV-5 | unchanged |

**Other tests retired or rewritten (not INV-enforcing):**

| Test | Action, reason |
|---|---|
| `test_confident_iff_dense_top1_reaches_threshold` | retired: the confidence rule no longer exists (Approval 2) |
| `test_corroboration_is_evidence_beyond_the_strongest_word` | retired: corroboration removed (was a confidence input) |
| `test_file_level_evidence_lifts_passages_in_a_matching_file` | rewritten as `test_file_bm25_adds_evidence_across_sections` (file with each word in a different section outranks a file with one word, in `file_lexical`) |
| `test_rrf_fusion_math` | rewritten against `rrf` (exact 1/(k+rank) sums, depth cut) |
| `test_hybrid_candidates_union_of_lists` | rewritten as `test_file_fusion_uses_both_lists` |
| `test_per_file_cap_applies_after_fusion` | rewritten as `test_each_file_carries_at_most_two_passages` |
| `test_at_most_five_hits` | rewritten as `test_at_most_five_distinct_files` |
| `test_no_searchable_words` | rewritten: `""`, `"   "` raise `QuestionError` |
| `test_no_passage_matched_on_empty_index` | rewritten: raises `IndexFormatError` |
| `test_confident_returns_hits_with_provenance` | rewritten as `test_file_results_carry_provenance` (same path, heading_path, line range and URL assertions, plus file URL and `ranking_mode` prefix `file-rrf-v1:`) |
| `test_lexical_only_match_can_still_be_returned_by_dense_list` | rewritten as `test_question_with_no_lexical_match_still_returns_files` |
| `test_unanswerable_hit_on_no_match` (test_evaluate) | rewritten as `test_unanswerable_is_diagnostic_only` (adding unanswerable questions never changes `passed`) |
| `test_ungated_diagnostic_does_not_affect_exit` | retired: ungated recall is now the gate |
| `test_threshold_integer_boundaries` | kept, answerable-only (12/15 pass, 11/15 fail; 4/5 pass, 3/5 fail) |
| `test_format_report_summary_lines`, `test_answerable_hit_any_listed_source`, `test_answerable_no_match_is_miss` | adapted to the new report |
| `test_cli_retrieve_no_match_exit_0` | rewritten as `test_cli_retrieve_below_reference_exit_0_with_files` |
| `test_cli_retrieve_prints_no_confident_match_first_line` | retired, replaced by `test_cli_retrieve_output_shape` (never contains "no confident match"; files, headings, line ranges, permalinks, top score line, closing line) |
| `test_cli_retrieve_confident_output_names_sources` | folded into `test_cli_retrieve_output_shape` |
| `test_load_config_valid`, config-writing fixtures | `conftest.config_text` gains an `include` argument |

Tests whose expected order depended on the removed passage/file blend (`test_bm25_prefers_passage_with_rarer_term`, `test_heading_and_path_count`, `test_rank_tie_break_is_path_then_line`) are expected to pass unchanged against pure passage BM25; if one does not, the Implementer re-derives it from the rule above and names it in 03-implementation.md.

**New tests:** test_search: `test_retrieve_never_abstains` (reference 0.99, files still returned, `format_result` has no "no confident match"), `test_file_dense_is_maxp`, `test_file_ties_break_by_path`, `test_retrieve_is_deterministic`, `test_fewer_files_than_top_k_returns_all`. test_ingest: `test_include_required_and_validated`, `test_read_markdown_admits_only_included_paths` (archive with `README.md`, `nested/README.md`, `agents/a.md`, `agents-old/a.md`, `docs/BACKLOG.md`, `docs/NEW.md`, `runs/x.md`, `site/x.md`: exactly the included ones come back), `test_include_entry_matching_no_file_fails` (exit 2), `test_committed_config_include_is_decision_2` (literal 18-entry list in the test equals the committed `include`). Extend `test_live_ingest_byte_identical` (`-m network`): every indexed path matches `include`. test_evaluate: `test_eval_with_no_answerable_question_exit_2`.

**Implementation hand-checks (no eval):** real `ingest` twice → same sha256; `files indexed` equals intake's 123; the index contains no path starting `docs/BACKLOG.md`, `docs/ARCHITECTURE.md`, `docs/PLATFORM_EVAL.md`, `runs/`, `site/`; two or three `retrieve` runs on the Implementer's own questions (not from any eval file) show the output shape. Then the full regression after the last commit: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, and `uv run pytest -m model`.

## Proposed INV change (owner first) — APPROVED and APPLIED

> Approved by the owner 2026-09-29T17:49:13Z (`runs/docs-retrieval-2/APPROVAL_RECORD-3.md`) and applied exactly as below to `.agentic/SAFETY_INVARIANTS.md`; nothing else in that file changed.

INV-4's **text does not need to change**: it is a disjunction, and always returning verbatim passages with provenance satisfies its first branch; "a model may be used only to rank passages and to decide confidence" still permits what the model does. Only the **annotation** goes stale, because it names a retired test. Proposed exact edit to `.agentic/SAFETY_INVARIANTS.md` (not made; the Orchestrator asks the owner):

```
-  *(Enforced by `test_not_confident_returns_no_hits`,
-  `test_result_invariant_enforced`,
+  *(Enforced by `test_result_invariant_enforced`,
```

If the owner declines, the annotation keeps naming a test that no longer exists; Security in slice B should record that. No INV-5 change.

## Files against the EM cap (01-scope §4)

| Group | Files | Count | Cap |
|---|---|---|---|
| Product and config | `aveto_support/ingest.py`, `docs-source.toml`, `aveto_support/search.py`, `aveto_support/__main__.py`, `aveto_support/evaluate.py` | 5 | 5 |
| Conditional product | `aveto_support/index.py` (3 lines in `RetrievalParams`: `ranking`, `confidence`, remove `file_lambda`, and its `to_dict`). Justified: the index is the record of the method's parameters, and the load check is what stops a slice 1 index (old corpus, old method) being scored. No schema or format change. | 1 | 0 to 3 conditionals |
| Tests | `tests/test_search.py`, `tests/test_evaluate.py`, `tests/test_ingest.py`, `tests/conftest.py` (justified: `config_text` is shared by test_ingest and test_evaluate and must write `include`) | 4 | 4 |
| Context and docs | `.agentic/PROJECT_CONTEXT.md` (C1), `.agentic/LOCAL_COMMANDS.md` (exit-code line, retrieve/eval rows), `docs/adr/0004-file-level-ranking-and-fixed-corpus.md` | 3 | 3 |
| Conditional, owner first | `.agentic/SAFETY_INVARIANTS.md` (the one-line annotation edit above, only if the owner says yes) | 0 or 1 | within 0 to 3 |

**Not touched:** `embed.py`, `tests/test_index.py`, anything in `evals/`, `README.md`, `docs/ARCHITECTURE.md` (slice B). **Disclosed:** at the Orchestrator's instruction I also add one status line to ADR 0002 and ADR 0003 ("partly superseded by ADR 0004"); these are record-keeping lines on Architect-owned records, no product change, but they are two more files touched than the doc cap names. Total: 13 files (14 with the INV annotation), plus the two ADR status lines. Fits the cap; no re-split needed.

## Freeze scope (what "the method" is)

The Orchestrator records the frozen SHA after Implementation's last commit and green regression. From then until slice B's single scoring run, `git diff <frozen> HEAD -- <files>` must be empty for:

`docs-source.toml`, `aveto_support/search.py`, `aveto_support/ingest.py`, `aveto_support/index.py`, `aveto_support/embed.py`, `aveto_support/evaluate.py`, `aveto_support/__main__.py`, `aveto_support/__init__.py` (if present), `pyproject.toml`, `uv.lock`, and `evals/retrieval.toml`, `evals/retrieval-heldout.toml`, `evals/calibration-offtopic.toml` (the earlier sets and the frozen off-topic list). The index QA scores with is built from the frozen commit and its sha256 recorded before the run. Tests and docs may change after the freeze only if the method files above do not.

## Rollback plan

Nothing is deployed or pushed from slice A, so rollback is local and mechanical:

1. `git revert <implementation commits>` in reverse order (or reset the branch to `c80299a`, the last pre-architecture commit, if nothing after it is kept). This restores the `exclude`-only config, passage-level embed-v3 and the abstaining `retrieve`.
2. Re-run `uv run python -m aveto_support ingest`. The old code rejects the new index ("different retrieval parameters"), so a stale index cannot be used by mistake; re-ingest uses only the approved hosts and cached, hash-checked models.
3. Run the full regression. If Approvals 1 and 2 are then no longer used, note in `STATE.md` that INV-4's retired test is back and revert the annotation edit if it was made.

## Risks / open questions

- **The method may still miss the 80% bar.** Accepted: the intent's test is exactly this hypothesis; a failure goes to the failure loop, and a further method change needs a fresh held-out set and a new rule 4 question (Approvals are scoped to this work).
- **MaxP mildly favours long, many-section files** (more chances at a high passage). Accepted: whole-file BM25's length normalisation offsets it on the lexical side; any correction would be a knob.
- **Abstention is gone from retrieval.** Moved, not dropped: ADR 0004 obliges the check-step slice to carry "the docs don't answer this" forward; slice B's close-out lists it as a follow-up. Until then, retrieve's output says "sources, not an answer" and the top score is printed.
- **The reference similarity may be misread as a gate.** Mitigated by the label "reported only" in `retrieve` and `eval`.
- **Stale index from slice 1** — mitigated by the params change (exit 2).
- Questions for the owner: (1) the INV-4 annotation edit above; (2) none on the eval schema, which is unchanged.

## Hand off

Next agent: **backend-architect** (Implementation), all product and test files above; one focused change, targeted tests first, full regression before each commit and after the last. One-line C1 task to **product-manager**: replace the "retrieval only, no model" line in `.agentic/PROJECT_CONTEXT.md` (line 66) with a line saying retrieval uses the approved local embedding model to rank and never generates text. `LOCAL_COMMANDS.md` updated by whichever role the write-scope hook allows (Implementer by default): the exit-code line per §Output and "retrieve lists its top 5 files". No eval runs; no reading of `evals/` content.
