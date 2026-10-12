# 03e Verdict grammar change (APPROVAL_RECORD-9, SUPPORT_REPLIES Reply 6 item 1)

- Code: `aveto_support/judge.py` line 46, regex only: `(?P<token>ANSWERABLE|NOT_ANSWERABLE):?(?: (?P<reason>\S.*))?`. Nothing else changed (id, case, single-line, control/format, wrong-id, count==1, reason discarded).
- Accepted: `Q1 T`, `Q1 T:`, `Q1 T reason`, `Q1 T: reason`.
- Tests added to the `test_parse_verdict_table` parametrisation in `tests/test_judge.py`: colon+reason (both tokens), trailing colon (both), `T::`, `T;`, `T:reason`, `T:  reason` (malformed); `Q1: T` (wrong block id, since `Q1:` parses as the id); second token after a colon (multi token); bold/lowercase with colon (malformed). Existing `ANSWERABLE.`/bold/lowercase rows unchanged.
- Spec: dated note added below 02-tech-spec.md 4.1 step 4; original text kept.
- No test pinned the old regex string. No prompt, agent, hook, skill or safety text touched.
- Results: mypy clean; pytest 304 passed, 11 deselected; ruff only the known untracked-file errors (see reply).
