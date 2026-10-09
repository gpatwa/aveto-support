# 03 Implementation log (A4, AI Engineer, standard depth)

## M1 code + tests with fakes: done
Files changed (10, spec 7.1): aveto_support/{judge(new),search,__main__,evaluate,ingest}.py; tests/{test_judge(new),test_search,test_evaluate,test_ingest,conftest}.py.
Full regression (mypy, ruff, pytest): green, 215 passed, 11 deselected (model/network).
Notes: conftest autouse fixture stubs OnnxJudge.load (always-answers) and ingest.ensure_judge_files (no 438 MB fetch in tests); marker `real_judge_load` (registered in conftest, pyproject untouched) opts out. `JUDGE_MAX_BYTES` = 500,000,000 in ingest (the existing 200 MB cap would reject the pinned 438 MB graph).

## M2 real model through `ingest`: done
Command: `SSL_CERT_FILE=/etc/ssl/cert.pem uv run python -m aveto_support ingest` (the documented macOS CA workaround; verification stays on; the first run without it failed on the GitHub fetch, before any model fetch). Output: `judge files: downloaded (sha256 verified before use)`; index sha256 unchanged (f36ef5d4...a756).
Files (`models/cross-encoder--qnli-electra-base/c7dea87c98b2269a935686c31336e97e837cbbeb/`): onnx/model.onnx 438,212,375 bytes sha256 595b3754...61d9; vocab.txt 231,508 bytes sha256 07eced37...38a3. Both match the approved values. ONNX inputs `['input_ids','attention_mask','token_type_ids']`, output `logits` shape `['batch_size', 1]` (load check in ingest and `pytest -m model`: 8 passed).

## M3 seen-set confirmation (spec 4.1): run; the pre-registered condition FAILED
Raw outputs: runs/docs-abstention/03-confirm-<set>.txt (+ .err). Method untouched, nothing tuned.
| set | Bar 1 | Bar 2 | end-to-end top5/top1 | exit |
|---|---|---|---|---|
| retrieval | 1/6 | 18/19 | 19/30, 12/30 | 1 (retrieval gate, by design) |
| heldout | 1/6 | 12/12 | 13/23, 6/23 | 1 |
| heldout-3 | 0/4 | 11/11 | 11/20, 8/20 | 134 after the full report printed (libc++abi recursive_mutex abort at teardown; recorded, no retry) |
| heldout-4 | 0/4 | 14/14 | 14/20, 13/20 | 0 |
| pooled | 2/20 | 55/56 | | |
4.1 requires pooled Bar 1 >= 16/20 and Bar 2 >= 45/56. Bar 2 holds; Bar 1 (2/20) fails by a wide margin. STOP: nothing adjusted. Observation only: judge p on answerable questions is mostly >= 0.9 (min 0.26); on unanswerable questions best-of-shown p is mostly >= 0.9 too (only 2 of 20 below 0.5).

## M4 regression: green (mypy, ruff, pytest 215 passed, 11 deselected). See git status in the final report.
