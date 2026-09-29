from __future__ import annotations

import pytest

from aveto_support.index import Index, Passage, RetrievalParams, split_passages
from aveto_support.search import (
    Hit,
    RetrievalResult,
    Searcher,
    calibrate,
    retrieve,
    stem,
    tokenize,
)

PARAMS = RetrievalParams()


def build(docs: dict[str, str], threshold: float = 0.5) -> Searcher:
    passages: list[Passage] = []
    for path, text in docs.items():
        passages.extend(split_passages(path, text))
    passages.sort(key=lambda p: (p.path, p.line_start))
    return Searcher(Index("acme/docs", "c" * 40, len(docs), (), tuple(passages), threshold, PARAMS))


def test_tokenize_casefold_split_stopwords() -> None:
    assert tokenize("The Quick-Brown_fox, and 42 dogs!") == ["quick", "brown", "fox", "42", "dog"]


def test_s_stemmer_rules() -> None:
    assert stem("queries") == "query"
    assert stem("windows") == "window"
    assert stem("aliases") == "aliase"
    assert stem("glass") == "glass"
    assert stem("status") == "status"
    assert stem("bus") == "bus"


def test_stopwords_removed_before_stemming() -> None:
    assert tokenize("does") == []
    assert tokenize("this is was") == []


def test_bm25_prefers_passage_with_rarer_term() -> None:
    s = build(
        {
            "a.md": "# One\ncommon common zebra\n",
            "b.md": "# Two\ncommon common common\n",
            "c.md": "# Three\ncommon words here\n",
        }
    )
    ranked = s.rank(["common", "zebra"])
    assert ranked[0][0].path == "a.md"


def test_heading_and_path_count() -> None:
    s = build(
        {
            "billing/invoices.md": "# Invoices\nnothing relevant here\n",
            "other.md": "# Misc\nbody body body\n",
            "third.md": "# Third\nfiller text\n",
        }
    )
    assert s.rank(["invoice"])[0][0].path == "billing/invoices.md"
    assert s.rank(["billing"])[0][0].path == "billing/invoices.md"


def test_rank_tie_break_is_path_then_line() -> None:
    s = build({"b.md": "# T\nshared words\n", "a.md": "# T\nshared words\n", "c.md": "# X\nother\n"})
    assert [p.path for p, _ in s.rank(["shared"])] == ["a.md", "b.md"]
    s2 = build({"a.md": "# T\nshared words\n# T\nshared words\n", "z.md": "# X\nother\n"})
    assert [p.line_start for p, _ in s2.rank(["shared"])] == [1, 3]


def _many_docs() -> dict[str, str]:
    docs = {f"f{i}.md": "".join(f"# S{j}\nshared token {i}{j}\n" for j in range(4)) for i in range(4)}
    docs["other.md"] = "# O\nunrelated\n"
    return docs


def test_per_file_cap_two() -> None:
    result = retrieve(build(_many_docs(), threshold=0.0), "shared")
    per_file: dict[str, int] = {}
    for h in result.hits:
        per_file[h.passage.path] = per_file.get(h.passage.path, 0) + 1
    assert result.hits and max(per_file.values()) == 2


def test_at_most_five_hits() -> None:
    result = retrieve(build(_many_docs(), threshold=0.0), "shared token")
    assert len(result.hits) == 5
    assert [h.rank for h in result.hits] == [1, 2, 3, 4, 5]


def test_no_searchable_words() -> None:
    s = build({"a.md": "# A\nsome text\n"})
    for q in ("", "the is of"):
        r = retrieve(s, q)
        assert (r.confident, r.hits, r.reason) == (False, (), "no-searchable-words")


def test_no_passage_matched() -> None:
    r = retrieve(build({"a.md": "# A\nsome text\n"}), "xyzzy plugh")
    assert (r.confident, r.hits, r.reason, r.coverage) == (False, (), "no-passage-matched", 0.0)


def test_not_confident_returns_no_hits() -> None:
    s = build({"a.md": "# A\nalpha beta\n", "b.md": "# B\ngamma delta\n"}, threshold=0.9)
    r = retrieve(s, "alpha gamma")
    assert r.reason == "below-threshold" and r.hits == () and not r.confident
    assert 0 < r.coverage < 0.9


def test_confident_returns_hits_with_provenance() -> None:
    s = build({"docs/a b.md": "# Top\n## Install\nrun the installer\nmore\n", "z.md": "# Z\nzzz\n"}, 0.5)
    r = retrieve(s, "installer")
    assert r.confident and r.reason == "ok" and r.generation_mode == "deterministic"
    hit = r.hits[0]
    assert hit.passage.path == "docs/a b.md"
    assert hit.passage.heading_path == ("Top", "Install")
    assert (hit.passage.line_start, hit.passage.line_end) == (2, 4)
    assert hit.url == f"https://github.com/acme/docs/blob/{'c' * 40}/docs/a%20b.md?plain=1#L2-L4"


def test_result_invariant_enforced() -> None:
    p = Passage("a.md", "A", ("A",), 1, 2, "# A\nx")
    hit = Hit(1, p, 1.0, "u")
    with pytest.raises(ValueError):
        RetrievalResult("q", False, (hit,), 0.0, 0.5, "below-threshold")
    with pytest.raises(ValueError):
        RetrievalResult("q", True, (), 1.0, 0.5, "ok")
    with pytest.raises(ValueError):
        RetrievalResult("q", True, (hit,), 1.0, 0.5, "below-threshold")


def test_oov_term_lowers_coverage() -> None:
    s = build({"a.md": "# A\nalpha beta\n", "b.md": "# B\nother\n"})
    top = s.rank(["alpha", "beta"])[0][0]
    full = s.coverage(["alpha", "beta"], top)
    with_oov = s.coverage(["alpha", "beta", "nowhereword"], top)
    assert full == pytest.approx(1.0)
    assert with_oov < full


def _corpus(n_files: int) -> list[Passage]:
    out: list[Passage] = []
    for i in range(n_files):
        out.extend(split_passages(f"f{i}.md", f"# H{i}\nword{i} common{i % 3} extra{i}\n## Sub\nmore{i} text{i}\n"))
    return out


def test_calibrate_deterministic() -> None:
    passages = _corpus(12)
    assert calibrate(passages, PARAMS) == calibrate(list(reversed(passages)), PARAMS)


def test_calibrate_in_unit_interval() -> None:
    assert 0.0 <= calibrate(_corpus(12), PARAMS) <= 1.0


def test_calibrate_small_corpus_returns_one() -> None:
    assert calibrate(_corpus(4), PARAMS) == 1.0
