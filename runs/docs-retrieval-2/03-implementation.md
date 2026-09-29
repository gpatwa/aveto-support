# Implementation — docs-retrieval-2 (slice A)

> Owner: Backend Architect (Stage 8, depth standard). Changes are uncommitted; the Orchestrator commits.

## Files changed (11 against the spec's cap of 11)
Product: `aveto_support/ingest.py`, `docs-source.toml`, `aveto_support/search.py`, `aveto_support/__main__.py`, `aveto_support/evaluate.py` (5); `aveto_support/index.py` (conditional, 3 lines in `RetrievalParams`) (1). Tests: `tests/test_search.py`, `tests/test_evaluate.py`, `tests/test_ingest.py`, `tests/conftest.py` (4). Docs: `.agentic/LOCAL_COMMANDS.md` (1). Plus this file and the STATE.md row. Not touched: `embed.py`, `test_index.py`, SAFETY_INVARIANTS, PROJECT_CONTEXT, README, ARCHITECTURE, pyproject, `evals/`.

## Tests
Retired: `test_not_confident_returns_no_hits` (owner-approved), `test_confident_iff_dense_top1_reaches_threshold`, `test_corroboration_is_evidence_beyond_the_strongest_word`, `test_ungated_diagnostic_does_not_affect_exit`, `test_cli_retrieve_prints_no_confident_match_first_line`, `test_cli_retrieve_confident_output_names_sources` (folded).
Rewritten (spec names): `test_result_invariant_enforced` and `test_hybrid_hits_are_verbatim_passages` (names kept, at least as strong, file level), `test_file_bm25_adds_evidence_across_sections`, `test_rrf_fusion_math`, `test_file_fusion_uses_both_lists`, `test_each_file_carries_at_most_two_passages`, `test_at_most_five_distinct_files`, `test_question_with_no_words_raises` (was `test_no_searchable_words`), `test_empty_index_raises`, `test_file_results_carry_provenance`, `test_retrieve_never_abstains`, `test_unanswerable_is_diagnostic_only`, `test_threshold_integer_boundaries`, `test_format_report_summary_lines`, `test_answerable_hit_any_listed_source`, `test_answerable_no_match_is_miss`, `test_cli_retrieve_below_reference_exit_0_with_files`, `test_cli_retrieve_output_shape`, config fixtures (`config_text(include=...)`).
New: `test_file_dense_is_maxp`, `test_file_ties_break_by_path`, `test_retrieve_is_deterministic`, `test_fewer_files_than_top_k_returns_all`, `test_include_required_and_validated`, `test_read_markdown_admits_only_included_paths`, `test_include_entry_matching_no_file_fails`, `test_committed_config_include_is_decision_2`, `test_eval_with_no_answerable_question_exit_2`. `test_lexical_only_match_can_still_be_returned_by_dense_list` was replaced by the dense-only file case inside `test_file_fusion_uses_both_lists` (z.md) rather than a separate test. `test_retrieved_text_is_verbatim_slice_of_file` (test_index) unchanged. The three BM25 order tests passed unchanged.

## Regression (run after the last code change)
`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`: mypy "Success: no issues found in 13 source files"; ruff "All checks passed!"; pytest "122 passed, 5 deselected in 5.48s". `uv run pytest -m model`: "3 passed, 124 deselected". `uv run pytest -m network` (with `SSL_CERT_FILE=/etc/ssl/cert.pem`, needed on this macOS Python): "2 passed, 125 deselected in 144.46s".

## Ingest evidence (real, pinned commit 3a83b669)
Two runs, same sha256 `f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756` (cmp identical). `files indexed: 123`, `passages: 890`, skipped 0, empty sections dropped 32, truncated for embedding 19. Reference similarity 0.701717 (tau_salad 0.701717, tau_offtopic 0.696323). Index params: ranking `file-rrf-v1`, confidence `none`, no `file_lambda`. No indexed path starts with `docs/BACKLOG.md`, `docs/ARCHITECTURE.md`, `docs/PLATFORM_EVAL.md`, `runs/`, `site/`. Every include entry matched.

## Hand-check of retrieve (my own questions)
"how do I approve a deploy", "what does a QA agent hand off", "chocolate cake recipe": each printed the header (question, Docs, Ranking `file-rrf-v1:hybrid:...`, Top score with the reference "reported only"), 5 files with score and file URL, up to 2 passages each (letter, line range, heading trail, `?plain=1#L..` permalink, three excerpt lines), then "These are sources, not an answer." Exit 0; "no confident match" never appears (off-topic question still lists 5 files, top score 0.510).

## Deviations
1. `test_live_ingest_byte_identical` (network): the old assertion "every eval source path is indexed" read `evals/retrieval.toml` at runtime and could contradict the fixed corpus; replaced by the spec's "every indexed path matches `include`". The test no longer touches `evals/`.
2. `run_ingest` counts an include entry as matched if a file matching it was skipped for not being UTF-8 (so the error means "no file at all", not "unreadable file"); no test named, behaviour otherwise as spec.
3. Ingest warning text unchanged (still says "abstention"), per spec; `retrieve --help` text and the `__main__` docstring updated.
4. The `index/docs-index.json` (git-ignored) was refreshed with the new index for the hand-check.

## Evals
I did not open, read, print or grep any file under `evals/`, did not run `eval` against any file, and computed no recall or score on any real question. `evaluate.py` was exercised only with synthetic eval files written inside the tests. (`test_committed_eval_set_is_well_formed` still reads `evals/retrieval.toml` as a pre-existing format check; it prints nothing.)
