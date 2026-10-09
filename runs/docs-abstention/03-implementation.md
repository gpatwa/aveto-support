# 03 Implementation log (A4, AI Engineer, standard depth)

## M1 code + tests with fakes: done
Files changed (10, spec 7.1): aveto_support/{judge(new),search,__main__,evaluate,ingest}.py; tests/{test_judge(new),test_search,test_evaluate,test_ingest,conftest}.py.
Full regression (mypy, ruff, pytest): green, 215 passed, 11 deselected (model/network).
Notes: conftest autouse fixture stubs OnnxJudge.load (always-answers) and ingest.ensure_judge_files (no 438 MB fetch in tests); marker `real_judge_load` (registered in conftest, pyproject untouched) opts out. `JUDGE_MAX_BYTES` = 500,000,000 in ingest (the existing 200 MB cap would reject the pinned 438 MB graph).
