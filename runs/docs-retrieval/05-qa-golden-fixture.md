# QA: WordPiece golden fixture (docs-retrieval, embed-v3)

Depth standard. Authorised by APPROVAL_RECORD-5 (one-off throwaway `tokenizers` install, outside the project, no hub download).

- **Package:** `tokenizers==0.22.2`, run with `uv run --no-project --with tokenizers==0.22.2 python tests/fixtures/gen_wordpiece_golden.py <vocab.txt> tests/fixtures/wordpiece_golden.json` from a temp directory outside the repo. Nothing else was fetched.
- **Vocab check:** `models/BAAI--bge-small-en-v1.5/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/vocab.txt` sha256 = `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`, equal to the pin. The generator re-checks it and the package version and refuses otherwise.
- **Reference settings:** `BertWordPieceTokenizer`, lowercase true, strip_accents None, handle_chinese_chars true, clean_text true, [CLS]/[SEP] added, truncation 512.
- **Cases (13):** the 11 pre-registered strings from the spec (empty; punctuation; accents; CJK; punctuation and digits; control and zero-width characters; `##` continuations; `[UNK]` symbols and emoji; markdown and arrow; `"word " * 600` = exactly 512 ids; query prefix plus the question), plus 2 QA additions (mixed case; a 150-character word, which the reference maps to `[UNK]`). No text from any evals/ file; `evals/calibration-offtopic.toml` was not opened. The fixture also records `tokens` per case and a `generated_by` header (role, date, version, vocab hash, command, full script); the test reads only `cases[].text` and `cases[].ids`.
- **Result:** `uv run --offline pytest -m model -q` gives `3 passed, 120 deselected`. `test_wordpiece_matches_golden` passes, so the implementation's tokenizer agrees with the reference on all 13 cases. The project environment has no `tokenizers` (`uv pip list` confirms).
- **Unchanged:** `git diff pyproject.toml uv.lock` is empty. Nothing under `aveto_support/`, `tests/*.py` or `docs-source.toml` was touched. New files only: `tests/fixtures/wordpiece_golden.json`, `tests/fixtures/gen_wordpiece_golden.py` (the 22nd file, as noted in Approval 5).
- **Not done:** no deliberate-break check of the test (that would need a code edit, out of scope); no eval was run.
