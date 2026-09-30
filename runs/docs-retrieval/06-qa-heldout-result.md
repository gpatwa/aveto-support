# QA: held-out score of the frozen method (docs-retrieval, embed-v3)

Depth standard. Each eval run exactly once, no code, config, threshold or eval file changed.

**Verdict: FAILED GATE (answerable bar).** Held-out answerable 5/17 (29.4%) against a bar of 14/17. Unanswerable 5/6 passes. Per instruction, nothing else was tried.

## Provenance and pre-run checks
- HEAD `b923aaddfb72036230ffbdb15804cec793f5fd58`; method frozen at `c9b64e7`. `git status --short` was empty before running. `git diff c9b64e7 HEAD` over `aveto_support`, `pyproject.toml`, `uv.lock`, `docs-source.toml`, `tests/test_*.py`, `tests/conftest.py`, `evals/retrieval.toml` and `evals/calibration-offtopic.toml` is empty. The only difference under `tests/` is QA's `tests/fixtures/gen_wordpiece_golden.py` (fixture generator; it matches the `tests/*.py` pathspec glob).
- Index `index/docs-index.json` sha256 = `1f6b2194db040446aa09ba6021d30a80df4361bcbc1e9c2958292c97d0cbe5c9`, equal to the expected value. The existing file was used; no ingest was re-run, no network used.
- Commands: `uv run --offline python -m aveto_support eval --eval-file evals/retrieval-heldout.toml` and `... --eval-file evals/retrieval.toml`. Raw output, with exit code (both 1) on the last line: `eval-run-2-heldout.txt`, `eval-run-3-dev-diagnostic.txt`. Threshold printed: 0.702.

## Held-out set (the gate): `evals/retrieval-heldout.toml`
| Group | Score | Bar | Result |
|-------|-------|-----|--------|
| answerable | 5/17 (29.4%) | >= 14/17 | **FAIL** |
| unanswerable | 5/6 (83.3%) | >= 5/6 | PASS |

- Answerable HIT: h04 (rank 1), h07 (rank 1), h10 (rank 3), h15 (rank 3), h16 (rank 1).
- Answerable MISS (12): 10 abstained as "no confident match, below-threshold" (h03 0.66, h05 0.68, h06 0.65, h08 0.65, h09 0.69, h11 0.66, h12 0.64, h13 0.68, h14 0.67, h17 0.62). 2 returned confident wrong passages (h01, h02).
- Unanswerable HIT: hu02 (0.60), hu03, hu04, hu05, hu06. MISS: hu01 (returned 5 passages, top `execution/pack/AGENTS.md`, similarity 0.70).
- Ungated diagnostic printed: `ungated recall@5 8/17 (not a gate)`.

## Dev set (diagnostic only): `evals/retrieval.toml`
Not the gate; it has been seen before and gates nothing. Answerable 10/24 (41.7%), unanswerable 4/6 (66.7%, misses u02 Windows and u06 Slack), `ungated recall@5 17/24`. Same pattern: 10 of 14 answerable misses are abstentions, 4 are confident wrong passages.

## Reading (not a fix)
Both sets show the same shape: correct passages usually score just under the 0.702 threshold (0.62 to 0.70), so abstention, not ranking, costs most answerable questions. Held-out recall@5 is 8/17 against 5/17 scored. Even ungated, that is well under 14/17. This is for the Orchestrator and owner; QA changed nothing.

## Caveats (owner-approved provenance, must stay in the record)
a. The held-out set was drafted by Claude in the playbook session and reviewed and committed by the owner. The drafter had read eval run 1 and the embed-v3 spec but reports it never ran retrieval on these questions.
b. Held-out unanswerable hu02 (Jira tickets) shares its subject with calibration question o01, so the abstention result on hu02 is not fully independent of calibration.
c. hu01 (Raspberry Pi) shares its subject with dev-set u02 (Windows).

## Not done
No re-run, no threshold or method change, nothing committed. `evals/calibration-offtopic.toml` was not opened.
