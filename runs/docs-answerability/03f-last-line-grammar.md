# 03f - last-line verdict grammar (APPROVAL_RECORD-10)

Changed only `judge.parse_verdict` (aveto_support/judge.py). No prompt, agent, hook, skill or safety text touched.

- Verdict line = last non-empty line (split on \n, \r\n, \r; blank/whitespace-only lines ignored; stripped). Regex (optional colon), wrong block id and ANSWERABLE-count==1 apply to that line only. Earlier lines are discarded, never returned/logged/printed/stored.
- Empty / all-blank reply: `empty reply` (checked first).
- Control/format check, strictest choice: any Cc or Cf character anywhere in the WHOLE reply is `control or format character`, except the line terminators \n and \r. Tab (and \x0b, \x0c) in any line, including an earlier or blank one, is rejected. Consequence: a trailing tab on a line, previously stripped, is now rejected.
- `more than one line`: the `MULTI_LINE` constant and its raise were removed (nothing else used it; only tests did). Spec 4.2 row 8 is left as history and marked superseded by a dated note under 4.1.
- Tests (tests/test_judge.py): table cases for last-line-wins both ways, r010 / r012 shapes, blank lines and \r\n / trailing newline, invalid last line after a valid earlier line (malformed, wrong id, multi-token), control char in an earlier or last line, old one-line cases unchanged. The two pinned `more than one line` rows were rewritten.
- Regression: pytest 316 passed (11 deselected); mypy clean; ruff reports only untracked runs/.../seen-check/key/prepare.py (ignored per instruction).
- Not done: the offline re-application to r001-r012 and the r013-r093 run (separate steps).
