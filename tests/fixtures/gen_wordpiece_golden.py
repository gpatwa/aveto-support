"""One-off dev tool: generates tests/fixtures/wordpiece_golden.json.

NOT a project dependency and NOT run by the test suite. It needs Hugging Face's
`tokenizers` package, which is deliberately absent from pyproject.toml and
uv.lock (Approval Record 5, docs-retrieval slice). It was run once, in a
throwaway environment outside the project, and the fixture it wrote is the
answer key that `test_wordpiece_matches_golden` checks the project's own
WordPiece against.

  tokenizers version : 0.22.2 (exact pin)
  vocab.txt sha256   : 07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3
                       (BAAI/bge-small-en-v1.5 @ 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a;
                        checked below, the script refuses any other file)
  Run by             : qa-evidence (role), 2026-09-29 UTC
  Command (run from a temp directory outside the repo; no hub download):
    uv run --no-project --with tokenizers==0.22.2 python \\
      <repo>/tests/fixtures/gen_wordpiece_golden.py \\
      <repo>/models/BAAI--bge-small-en-v1.5/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/vocab.txt \\
      <repo>/tests/fixtures/wordpiece_golden.json

Reference settings (BertTokenizer semantics, from the spec, embed-v3 section 1):
lowercase=True, strip_accents=None (accents are stripped when lowercasing),
handle_chinese_chars=True, clean_text=True, [CLS]/[SEP] added, truncation to 512
including both. Cases 1 to 11 are the pre-registered strings from the spec;
12 and 13 are QA additions (mixed case, over-long single word). None comes from
any eval set.
"""
import hashlib
import json
import sys
from pathlib import Path

import tokenizers
from tokenizers import BertWordPieceTokenizer

EXPECTED_TOKENIZERS = "0.22.2"
EXPECTED_VOCAB_SHA256 = "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

TEXTS = [
    "",
    "Hello, world!",
    "Café naïve résumé Ångström",
    "日本語のテキストと中文",
    "don't stop-believing: e.g. 3.14 (v2) [x] {y} <z>",
    "tab\there\nnewline\u0007bell​zero-width",
    "unaffable electroencephalography antidisestablishmentarianism",
    "🙂 ☃ ∑ emoji and symbols",
    "## Install `install.mjs` → run /agentic-slice --help",
    "word " * 600,
    QUERY_PREFIX + "How do I resume a run?",
    "The QUICK Brown fOx jumps over ThE lazy DOG, iPhone OS X",
    "a" * 150 + " short",
]


def main(vocab_path: str, out_path: str) -> None:
    if tokenizers.__version__ != EXPECTED_TOKENIZERS:
        sys.exit(f"tokenizers {tokenizers.__version__} != pinned {EXPECTED_TOKENIZERS}")
    vocab = Path(vocab_path)
    digest = hashlib.sha256(vocab.read_bytes()).hexdigest()
    if digest != EXPECTED_VOCAB_SHA256:
        sys.exit(f"vocab sha256 {digest} != pinned {EXPECTED_VOCAB_SHA256}")
    tok = BertWordPieceTokenizer(
        str(vocab), lowercase=True, strip_accents=None, handle_chinese_chars=True, clean_text=True
    )
    tok.enable_truncation(max_length=512)
    cases = []
    for text in TEXTS:
        enc = tok.encode(text, add_special_tokens=True)
        cases.append({"text": text, "ids": enc.ids, "tokens": enc.tokens})
    assert len(cases[9]["ids"]) == 512, "truncation case must hit exactly 512"
    fixture = {
        "generated_by": {
            "role": "qa-evidence",
            "date_utc": "2026-09-29",
            "tokenizers_version": tokenizers.__version__,
            "vocab_sha256": digest,
            "command": (
                "uv run --no-project --with tokenizers==0.22.2 python "
                "tests/fixtures/gen_wordpiece_golden.py <vocab.txt> tests/fixtures/wordpiece_golden.json"
            ),
            "snippet": Path(__file__).read_text(encoding="utf-8"),
        },
        "cases": cases,
    }
    Path(out_path).write_text(json.dumps(fixture, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out_path}: {len(cases)} cases")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
