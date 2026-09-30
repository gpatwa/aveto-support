from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import embed_all

from aveto_support.index import (
    EmbeddingParams,
    Index,
    IndexFormatError,
    Passage,
    RetrievalParams,
    load_index,
    serialize_index,
    split_passages,
    split_sections,
    write_index,
)


def test_split_atx_levels_and_trail() -> None:
    text = "# A\nintro\n## B\nb text\n### C\nc text\n## D\nd text\n"
    ps = split_passages("x.md", text)
    assert [p.heading for p in ps] == ["A", "B", "C", "D"]
    assert [p.heading_path for p in ps] == [("A",), ("A", "B"), ("A", "B", "C"), ("A", "D")]
    assert [(p.line_start, p.line_end) for p in ps] == [(1, 2), (3, 4), (5, 6), (7, 8)]


def test_heading_in_backtick_fence_ignored() -> None:
    ps = split_passages("x.md", "# A\n```\n# not a heading\n```\nafter\n")
    assert [p.heading for p in ps] == ["A"]
    assert ps[0].line_end == 5


def test_heading_in_tilde_fence_ignored() -> None:
    ps = split_passages("x.md", "# A\n~~~~\n# no\n~~~\n# still inside\n~~~~\n# B\nb\n")
    assert [p.heading for p in ps] == ["A", "B"]


def test_unclosed_fence_runs_to_eof() -> None:
    ps = split_passages("x.md", "# A\ntext\n```\n# hidden\nmore\n")
    assert [p.heading for p in ps] == ["A"]
    assert ps[0].line_end == 5


def test_front_matter_not_headings() -> None:
    ps = split_passages("x.md", "---\n# comment in yaml\ntitle: t\n---\n# Real\nbody\n")
    assert [p.heading for p in ps] == ["", "Real"]
    assert ps[0].line_start == 1 and ps[0].line_end == 4
    assert ps[1].line_start == 5


def test_hashtag_without_space_not_heading() -> None:
    assert split_passages("x.md", "#tag is text\nmore\n")[0].heading == ""


def test_closing_hashes_stripped() -> None:
    ps = split_passages("x.md", "## Title ##\nbody\n# Other #\nbody\n")
    assert [p.heading for p in ps] == ["Title", "Other"]


def test_up_to_three_leading_spaces() -> None:
    ps = split_passages("x.md", "   # Three\nbody\n    # Four (code)\nmore\n")
    assert [p.heading for p in ps] == ["Three"]


def test_setext_heading_not_recognised() -> None:
    ps = split_passages("x.md", "Title\n=====\nbody\n")
    assert len(ps) == 1 and ps[0].heading == ""


def test_preamble_passage() -> None:
    ps = split_passages("x.md", "intro line\n\n# H\nbody\n")
    assert ps[0].heading == "" and ps[0].heading_path == ()
    assert (ps[0].line_start, ps[0].line_end) == (1, 1)


def test_empty_sections_dropped() -> None:
    ps, dropped = split_sections("x.md", "# A\n\n## B\n\n## C\nc\n")
    assert dropped == 2
    assert [p.heading for p in ps] == ["C"]
    assert ps[0].heading_path == ("A", "C")


def test_line_end_trims_trailing_blanks() -> None:
    ps = split_passages("x.md", "# A\nbody\n\n\n# B\nb\n")
    assert (ps[0].line_start, ps[0].line_end) == (1, 2)


def test_retrieved_text_is_verbatim_slice_of_file() -> None:
    text = "pre\n\n# A\nline  with   spaces\n\n```\n# code\n```\n## B\n  indented\n\n\n"
    lines = text.split("\n")
    passages = split_passages("x.md", text)
    assert passages
    for p in passages:
        assert 1 <= p.line_start <= p.line_end <= len(lines)
        assert p.text == "\n".join(lines[p.line_start - 1 : p.line_end])


def _index(threshold: float = 0.5) -> Index:
    passages = tuple(
        embed_all(split_passages("a.md", "# Ünï\nbody text\n") + split_passages("b.md", "# B\nmore\n"))
    )
    return Index(
        "o/r", "a" * 40, 2, (("c.md", "not utf-8"),), passages, threshold, RetrievalParams(),
        3, 0.25, 0.5, 1,
    )


def test_serialize_canonical() -> None:
    data = serialize_index(_index())
    assert data.endswith(b"\n") and not data.endswith(b"\n\n")
    doc = json.loads(data)
    assert list(doc) == sorted(doc)
    assert "Ünï" in data.decode("utf-8")
    assert serialize_index(_index()) == data
    with pytest.raises(ValueError):
        serialize_index(_index(float("nan")))


def test_load_round_trip(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "i.json"
    original = _index(0.123457)
    digest = write_index(original, out)
    assert len(digest) == 64
    assert load_index(out) == original
    assert not [p for p in out.parent.iterdir() if p != out]


def test_load_rejects_wrong_schema(tmp_path: Path) -> None:
    out = tmp_path / "i.json"
    write_index(_index(), out)
    doc = json.loads(out.read_text())
    doc["schema"] = "other@2"
    out.write_text(json.dumps(doc))
    with pytest.raises(IndexFormatError, match="schema"):
        load_index(out)


def test_load_rejects_params_mismatch(tmp_path: Path) -> None:
    out = tmp_path / "i.json"
    write_index(_index(), out)
    doc = json.loads(out.read_text())
    doc["params"]["k1"] = 9.9
    out.write_text(json.dumps(doc))
    with pytest.raises(IndexFormatError, match="different retrieval parameters"):
        load_index(out)


def test_load_missing_file_and_bad_json(tmp_path: Path) -> None:
    with pytest.raises(IndexFormatError):
        load_index(tmp_path / "nope.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    with pytest.raises(IndexFormatError):
        load_index(bad)


def test_load_malformed_passages(tmp_path: Path) -> None:
    out = tmp_path / "i.json"
    write_index(_index(), out)
    doc = json.loads(out.read_text())
    doc["passages"][0]["line_start"] = "one"
    out.write_text(json.dumps(doc))
    with pytest.raises(IndexFormatError, match="malformed"):
        load_index(out)


def test_load_rejects_index_v2(tmp_path: Path) -> None:
    out = tmp_path / "i.json"
    write_index(_index(), out)
    doc = json.loads(out.read_text())
    doc["schema"] = "aveto-support/index@2"
    out.write_text(json.dumps(doc))
    with pytest.raises(IndexFormatError, match="schema"):
        load_index(out)


def test_embedding_params_mismatch_rejected(tmp_path: Path) -> None:
    out = tmp_path / "i.json"
    write_index(_index(), out)
    for key, value in (("dim", 128), ("rrf_k", 10), ("query_prefix", "x"), ("quantization", "int8-63")):
        doc = json.loads(out.read_text())
        doc["params"]["embedding"][key] = value
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps(doc))
        with pytest.raises(IndexFormatError, match="different retrieval parameters"):
            load_index(bad)


def test_embedding_identity_is_data_and_validated(tmp_path: Path) -> None:
    other = EmbeddingParams(model="acme/other", revision="d" * 40, onnx_sha256="e" * 64,
                            vocab_sha256="f" * 64, offtopic_sha256="1" * 64)
    idx = Index("o/r", "a" * 40, 0, (), (), 0.5, RetrievalParams(embedding=other))
    out = tmp_path / "i.json"
    write_index(idx, out)
    assert load_index(out).params.embedding == other
    doc = json.loads(out.read_text())
    doc["params"]["embedding"]["revision"] = "main"
    out.write_text(json.dumps(doc))
    with pytest.raises(IndexFormatError, match="malformed"):
        load_index(out)


def test_load_rejects_bad_embedding_bytes(tmp_path: Path) -> None:
    out = tmp_path / "i.json"
    write_index(_index(), out)
    for bad in ("not base64!!", "AAAA", 5):
        doc = json.loads(out.read_text())
        doc["passages"][0]["embedding"] = bad
        target = tmp_path / "bad.json"
        target.write_text(json.dumps(doc))
        with pytest.raises(IndexFormatError, match="malformed"):
            load_index(target)


def test_passage_is_frozen() -> None:
    p = Passage("a.md", "", (), 1, 1, "x")
    with pytest.raises(AttributeError):
        p.text = "y"  # type: ignore[misc]
