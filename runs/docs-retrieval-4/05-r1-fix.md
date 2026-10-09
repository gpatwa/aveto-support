# 05 R1 fix (ADR 0006 wording, doc-only)

Changed only `docs/adr/0006-default-rrf-reranker-opt-in.md`:
- Consequences "no longer at the mercy of teardown order" -> property of the code (adapters closed in reverse order before shutdown; test_main_closes_loaded_adapters_in_reverse_order).
- Added status "exit-134 abort: NOT REPRODUCED" with counts (unfixed eval 20 / retrieve 200; fixed eval 20 and retrieve 200 per mode; 0 exit-134, no signal exit); loops cannot discriminate; spec mechanism not observed; ORT-internal lock is a reading, not a finding.
- "Slice 4 then reports it as explained, not fixed" replaced; "hides the lifetime defect" reworded (no defect asserted).
- A4: MS MARCO licence question does not apply to the default path, stays open for --with-reranker.
Grep (README.md, .agentic, docs, runs/docs-retrieval-4/*.md except 04): no remaining claim of "crash fixed"/"explained" outcome in docs/ or README.md. Hits left in runs/ (not edited): 00-slice-plan.md:13, 02-tech-spec.md:84,243, 03-implementation.md:7,60 (these negate or are spec history), intent.md:32 (owner's original criterion).
