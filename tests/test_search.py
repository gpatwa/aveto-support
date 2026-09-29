from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import FakeEmbedder, embed_all

from aveto_support.embed import (
    DIM,
    INPUT_NAMES,
    ModelError,
    OnnxEmbedder,
    PlaceholderEmbedder,
    WordPiece,
    dequantise,
    model_dir,
    passage_input,
    quantise,
    verify_file,
)
from aveto_support.index import (
    EmbeddingParams,
    Index,
    Passage,
    RetrievalParams,
    split_passages,
)
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
FAKE = FakeEmbedder()


def passages_of(docs: dict[str, str]) -> list[Passage]:
    found: list[Passage] = []
    for path, text in docs.items():
        found.extend(split_passages(path, text))
    found.sort(key=lambda p: (p.path, p.line_start))
    return embed_all(found)


def build(docs: dict[str, str], threshold: float = 0.0) -> Searcher:
    ps = passages_of(docs)
    index = Index("acme/docs", "c" * 40, len(docs), (), tuple(ps), threshold, PARAMS)
    return Searcher(index, FAKE)


# --- tokenizer and stemmer -------------------------------------------------


def test_tokenize_casefold_split_stopwords() -> None:
    assert tokenize("The Quick-Brown_fox, and 42 dogs!") == ["quick", "brown", "fox", "42", "dog"]


def test_stopwords_removed_before_stemming() -> None:
    assert tokenize("does") == []
    assert tokenize("this is was") == []


def test_porter_1980_published_examples() -> None:
    cases = {
        "caresses": "caress", "ponies": "poni", "ties": "ti", "caress": "caress", "cats": "cat",
        "feed": "feed", "agreed": "agre", "plastered": "plaster", "bled": "bled",
        "motoring": "motor", "sing": "sing", "conflated": "conflat", "troubled": "troubl",
        "sized": "size", "hopping": "hop", "tanned": "tan", "falling": "fall", "hissing": "hiss",
        "fizzed": "fizz", "failing": "fail", "filing": "file", "happy": "happi", "sky": "sky",
        "relational": "relat", "conditional": "condit", "rational": "ration", "valenci": "valenc",
        "digitizer": "digit", "operator": "oper", "feudalism": "feudal", "decisiveness": "decis",
        "hopefulness": "hope", "callousness": "callous", "formaliti": "formal",
        "sensitiviti": "sensit", "sensibiliti": "sensibl", "triplicate": "triplic",
        "formative": "form", "formalize": "formal", "electriciti": "electr", "electrical": "electr",
        "hopeful": "hope", "goodness": "good", "revival": "reviv", "allowance": "allow",
        "inference": "infer", "airliner": "airlin", "gyroscopic": "gyroscop", "adjustable": "adjust",
        "defensible": "defens", "irritant": "irrit", "replacement": "replac", "adjustment": "adjust",
        "dependent": "depend", "adoption": "adopt", "homologou": "homolog", "communism": "commun",
        "activate": "activ", "angulariti": "angular", "homologous": "homolog",
        "effective": "effect", "bowdlerize": "bowdler", "probate": "probat", "rate": "rate",
        "cease": "ceas", "controlling": "control", "roll": "roll",
    }
    for word, expected in cases.items():
        assert stem(word) == expected, word


def test_porter_short_tokens_unchanged() -> None:
    assert stem("is") == "is" and stem("a") == "a" and stem("42") == "42"


# --- quantisation and adapters ---------------------------------------------


def test_int8_quantise_roundtrip() -> None:
    data = quantise([1.0, -1.0, 0.5, 2.0, -2.0, 0.0])
    assert list(memoryview(data).cast("b")) == [127, -127, 64, 127, -127, 0]
    assert list(dequantise(data)) == [1.0, -1.0, 64 / 127, 1.0, -1.0, 0.0]


def test_placeholder_embedder_raises() -> None:
    for call in (
        lambda: PlaceholderEmbedder().embed_passage("x"),
        lambda: PlaceholderEmbedder().embed_query("x"),
        lambda: PlaceholderEmbedder().token_count("x"),
    ):
        with pytest.raises(RuntimeError, match="embedding model is not configured in this build."):
            call()


def test_searcher_defaults_to_placeholder_and_retrieve_raises() -> None:
    s = Searcher(build({"a.md": "# A\nsome text\n"}).index)
    with pytest.raises(RuntimeError, match="not configured"):
        retrieve(s, "text")


def test_fake_embedder_deterministic() -> None:
    a, b = FakeEmbedder().embed_query("alpha beta"), FakeEmbedder().embed_query("alpha beta")
    assert a == b and len(a) == DIM
    assert FakeEmbedder().embed_query("alpha beta") != FakeEmbedder().embed_query("gamma")


def test_passage_input_is_heading_trail_then_body() -> None:
    p = split_passages("x.md", "# A\n## B\nbody one\nbody two\n")[0]
    assert passage_input(p) == "A > B\nbody one\nbody two"
    pre = split_passages("x.md", "intro\n# A\nx\n")[0]
    assert passage_input(pre) == "\nintro"


# --- WordPiece on a tiny synthetic vocab -----------------------------------

VOCAB = [
    "[PAD]", "[UNK]", "[CLS]", "[SEP]", "hello", "world", "cafe", "naive", "un", "##aff",
    "##able", "##s", ",", "!", "日", "本", "don", "'", "t", "word", "a", "b",
]


def _ids(text: str) -> list[str]:
    wp = WordPiece(VOCAB)
    return [VOCAB[i] for i in wp.encode(text)]


def test_wordpiece_basic_rules() -> None:
    assert _ids("") == ["[CLS]", "[SEP]"]
    assert _ids("Hello, WORLD!") == ["[CLS]", "hello", ",", "world", "!", "[SEP]"]
    assert _ids("Café naïve") == ["[CLS]", "cafe", "naive", "[SEP]"]
    assert _ids("Café") == ["[CLS]", "cafe", "[SEP]"]
    assert _ids("unaffable unaffables") == ["[CLS]", "un", "##aff", "##able", "un", "##aff", "##able", "##s", "[SEP]"]
    assert _ids("日本日") == ["[CLS]", "日", "本", "日", "[SEP]"]
    assert _ids("zzz hello") == ["[CLS]", "[UNK]", "hello", "[SEP]"]
    assert _ids("hel\u0007lo \u200bworld") == ["[CLS]", "hello", "world", "[SEP]"]
    assert _ids("hel\u0007lo\u200bworld") == ["[CLS]", "[UNK]", "[SEP]"]  # removed, not split
    assert _ids("don't") == ["[CLS]", "don", "'", "t", "[SEP]"]


def test_wordpiece_truncates_to_512_with_special_tokens() -> None:
    ids = WordPiece(VOCAB).encode("word " * 600)
    assert len(ids) == 512
    assert ids[0] == VOCAB.index("[CLS]") and ids[-1] == VOCAB.index("[SEP]")
    assert WordPiece(VOCAB).content_ids("word " * 600).__len__() == 600


def test_wordpiece_requires_special_tokens() -> None:
    with pytest.raises(ModelError):
        WordPiece(["a", "b"])


# --- ranking ---------------------------------------------------------------


def test_bm25_prefers_passage_with_rarer_term() -> None:
    s = build(
        {
            "a.md": "# One\ncommon common zebra\n",
            "b.md": "# Two\ncommon common common\n",
            "c.md": "# Three\ncommon words here\n",
        }
    )
    assert s.rank(["common", "zebra"])[0][0].path == "a.md"


def test_heading_and_path_count() -> None:
    s = build(
        {
            "billing/invoices.md": "# Invoices\nnothing relevant here\n",
            "other.md": "# Misc\nbody body body\n",
            "third.md": "# Third\nfiller text\n",
        }
    )
    assert s.rank(tokenize("invoice"))[0][0].path == "billing/invoices.md"
    assert s.rank(tokenize("billing"))[0][0].path == "billing/invoices.md"


def test_file_level_evidence_lifts_passages_in_a_matching_file() -> None:
    s = build(
        {
            "deploy.md": "# Deploy\nship release\n# Rollback\nrelease notes\n# Tips\nrelease\n",
            "misc.md": "# Notes\nrelease ship deploy\n",
            "other.md": "# Other\nnothing here\n",
        }
    )
    ranked = s.rank(tokenize("deploy ship release"))
    assert ranked[0][0].path == "deploy.md"
    assert all(0 < score <= 1.0 + 1e-9 for _, score in ranked)


def test_passage_without_question_words_is_never_a_lexical_candidate() -> None:
    s = build({"a.md": "# A\nalpha\n# B\nbeta\n", "b.md": "# C\ngamma\n"})
    assert {p.heading for p, _ in s.rank(["alpha"])} == {"A"}


def test_rank_tie_break_is_path_then_line() -> None:
    s = build({"b.md": "# T\nshared words\n", "a.md": "# T\nshared words\n", "c.md": "# X\nother\n"})
    assert [p.path for p, _ in s.rank(tokenize("shared"))] == ["a.md", "b.md"]
    s2 = build({"a.md": "# T\nshared words\n# T\nshared words\n", "z.md": "# X\nother\n"})
    assert [p.line_start for p, _ in s2.rank(tokenize("shared"))] == [1, 3]


def test_corroboration_is_evidence_beyond_the_strongest_word() -> None:
    s = build({"a.md": "# A\nalpha beta gamma\n", "b.md": "# B\nother stuff\n", "c.md": "# C\nmore stuff\n"})
    p = s.rank(["alpha"])[0][0]
    assert s.corroboration(["alpha"], p) == 0.0
    assert s.corroboration(["nowhereword"], p) == 0.0
    two = s.corroboration(["alpha", "beta"], p)
    assert two == pytest.approx(min(s.idf("alpha"), s.idf("beta")))
    assert s.corroboration(["alpha", "beta", "gamma"], p) > two


def _vec(**parts: int) -> bytes:
    values = [0] * DIM
    for key, amount in parts.items():
        values[int(key[1:])] = amount
    return bytes(v & 0xFF for v in values)


def _crafted() -> tuple[Searcher, bytes]:
    docs = {
        "x.md": "# X\nzeta filler words here more\n",
        "y.md": "# Y\nzeta zeta zeta zeta\n",
        "z.md": "# Z\nunrelated content only\n",
    }
    ps = passages_of(docs)
    vectors = {"x.md": _vec(e0=127), "y.md": _vec(e0=60, e1=100), "z.md": _vec(e1=127)}
    import dataclasses

    crafted = [dataclasses.replace(p, embedding=vectors[p.path]) for p in ps]
    index = Index("acme/docs", "c" * 40, 3, (), tuple(crafted), 0.0, PARAMS)
    return Searcher(index, FAKE), _vec(e0=127)


def test_rrf_fusion_math() -> None:
    s, query = _crafted()
    assert [s.passage(i).path for i, _ in s.dense_ranked(query)] == ["x.md", "y.md", "z.md"]
    assert [p.path for p, _ in s.rank(["zeta"])] == ["y.md", "x.md"]
    fused = s.fused(["zeta"], query)
    scores = {s.passage(i).path: score for i, score in fused}
    assert scores["x.md"] == pytest.approx(1 / 61 + 1 / 62)
    assert scores["y.md"] == pytest.approx(1 / 61 + 1 / 62)
    assert scores["z.md"] == pytest.approx(1 / 63)
    assert [s.passage(i).path for i, _ in fused] == ["x.md", "y.md", "z.md"]


def test_hybrid_candidates_union_of_lists() -> None:
    s, query = _crafted()
    paths = {s.passage(i).path for i, _ in s.fused(["zeta"], query)}
    assert paths == {"x.md", "y.md", "z.md"}  # z.md is dense-only
    lexical_only = {s.passage(i).path for i, _ in s.fused(["zeta"], _vec(e5=127))}
    assert {"x.md", "y.md"} <= lexical_only


def _many_docs() -> dict[str, str]:
    docs = {f"f{i}.md": "".join(f"# S{j}\nshared token {i}{j}\n" for j in range(4)) for i in range(4)}
    docs["other.md"] = "# O\nunrelated\n"
    return docs


def test_per_file_cap_applies_after_fusion() -> None:
    result = retrieve(build(_many_docs()), "shared")
    per_file: dict[str, int] = {}
    for h in result.hits:
        per_file[h.passage.path] = per_file.get(h.passage.path, 0) + 1
    assert result.hits and max(per_file.values()) == 2


def test_at_most_five_hits() -> None:
    result = retrieve(build(_many_docs()), "shared token")
    assert len(result.hits) == 5
    assert [h.rank for h in result.hits] == [1, 2, 3, 4, 5]


# --- the confidence rule ---------------------------------------------------


def test_no_searchable_words() -> None:
    s = build({"a.md": "# A\nsome text\n"})
    for q in ("", "   "):
        r = retrieve(s, q)
        assert (r.confident, r.hits, r.reason) == (False, (), "no-searchable-words")


def test_no_passage_matched_on_empty_index() -> None:
    s = Searcher(Index("acme/docs", "c" * 40, 0, (), (), 0.5, PARAMS), FAKE)
    r = retrieve(s, "anything at all")
    assert (r.confident, r.hits, r.reason) == (False, (), "no-passage-matched")


def test_not_confident_returns_no_hits() -> None:
    s = build({"a.md": "# A\nalpha beta\n", "b.md": "# B\ngamma delta\n"}, threshold=0.99)
    r = retrieve(s, "alpha gamma")
    assert r.reason == "below-threshold" and r.hits == () and not r.confident
    assert 0 < r.confidence < 0.99


def test_confident_iff_dense_top1_reaches_threshold() -> None:
    docs = {"a.md": "# A\nalpha beta\n", "b.md": "# B\ngamma delta\n"}
    sim = retrieve(build(docs), "alpha beta").confidence
    assert retrieve(build(docs, threshold=sim), "alpha beta").confident
    assert not retrieve(build(docs, threshold=sim + 1e-6), "alpha beta").confident


def test_confident_returns_hits_with_provenance() -> None:
    s = build({"docs/a b.md": "# Top\n## Install\nrun the installer\nmore\n", "z.md": "# Z\nzzz\n"}, 0.1)
    r = retrieve(s, "installer")
    assert r.confident and r.reason == "ok" and r.generation_mode == "deterministic"
    assert r.ranking_mode.startswith("hybrid:BAAI/bge-small-en-v1.5@")
    hit = r.hits[0]
    assert hit.passage.path == "docs/a b.md"
    assert hit.passage.heading_path == ("Top", "Install")
    assert (hit.passage.line_start, hit.passage.line_end) == (2, 4)
    assert hit.url == f"https://github.com/acme/docs/blob/{'c' * 40}/docs/a%20b.md?plain=1#L2-L4"


def test_hybrid_hits_are_verbatim_passages() -> None:
    docs = {"a.md": "# A\nline  one\n\n  indented\n```\n# code\n```\n## B\nbody\n", "b.md": "# C\nother text\n"}
    lines = {path: text.split("\n") for path, text in docs.items()}
    result = retrieve(build(docs), "line one indented body other text")
    assert result.confident and result.hits
    for hit in result.hits:
        p = hit.passage
        assert p.text == "\n".join(lines[p.path][p.line_start - 1 : p.line_end])


def test_lexical_only_match_can_still_be_returned_by_dense_list() -> None:
    docs = {"a.md": "# A\nalpha beta\n", "b.md": "# B\ngamma delta\n"}
    r = retrieve(build(docs), "xyzzy plugh")  # no lexical candidate at all
    assert r.confident and r.hits and r.corroboration == 0.0


def test_result_invariant_enforced() -> None:
    p = Passage("a.md", "A", ("A",), 1, 2, "# A\nx")
    hit = Hit(1, p, 1.0, "u")
    with pytest.raises(ValueError):
        RetrievalResult("q", False, (hit,), 0.0, 0.5, "below-threshold")
    with pytest.raises(ValueError):
        RetrievalResult("q", True, (), 1.0, 0.5, "ok")
    with pytest.raises(ValueError):
        RetrievalResult("q", True, (hit,), 1.0, 0.5, "below-threshold")


# --- calibration -----------------------------------------------------------


def _corpus(n_files: int) -> list[Passage]:
    docs = {
        f"f{i}.md": f"# H{i}\nword{i} common{i % 3} extra{i}\n## Sub\nmore{i} text{i}\n"
        for i in range(n_files)
    }
    return passages_of(docs)


def test_dense_calibration_deterministic() -> None:
    passages = _corpus(12)
    first = calibrate(passages, FAKE)
    assert first == calibrate(passages, FAKE)
    assert first == calibrate(list(reversed(passages)), FAKE)


def test_calibrate_in_unit_interval() -> None:
    c = calibrate(_corpus(12), FAKE)
    assert 0.0 <= c.tau_salad <= 1.0 and c.tau_offtopic is None and c.threshold == c.tau_salad


def test_calibrate_small_corpus_returns_sentinel() -> None:
    c = calibrate(_corpus(4), FAKE)
    assert c.tau_salad == 1_000_000.0 and c.threshold == 1_000_000.0


def test_tau_is_max_of_salad_and_offtopic() -> None:
    passages = _corpus(12)
    salad = calibrate(passages, FAKE).tau_salad
    near = ["word3 common0 extra3 more3 text3", "word5 common2 extra5", "word7 common1 extra7 more7"] * 2
    far = ["quantum spaceship", "airspeed velocity swallow", "zebra crossing", "lunar module", "opera"]
    high = calibrate(passages, FAKE, near)
    assert high.tau_offtopic is not None and high.tau_offtopic > salad
    assert high.threshold == high.tau_offtopic and high.tau_salad == salad
    low = calibrate(passages, FAKE, far)
    assert low.tau_offtopic is not None and low.tau_offtopic < salad and low.threshold == salad


# --- model-marked tests (need the cached, hash-verified files; never skip) ---

ROOT = Path(__file__).parent.parent
GOLDEN = Path(__file__).parent / "fixtures" / "wordpiece_golden.json"


def _pinned() -> tuple[Path, EmbeddingParams]:
    import tomllib

    with (ROOT / "docs-source.toml").open("rb") as handle:
        table = tomllib.load(handle)["embedding"]
    params = EmbeddingParams(
        model=table["model"],
        revision=table["revision"],
        onnx_sha256=table["onnx_sha256"],
        vocab_sha256=table["vocab_sha256"],
    )
    return ROOT / "models", params


def _load_onnx() -> OnnxEmbedder:
    models, params = _pinned()
    try:
        return OnnxEmbedder.load(models, params)
    except ModelError as exc:
        pytest.fail(f"model files are not cached or fail their pinned sha256 ({exc}); run ingest first")


@pytest.mark.model
def test_wordpiece_matches_golden() -> None:
    if not GOLDEN.is_file():
        pytest.fail(
            "tests/fixtures/wordpiece_golden.json is missing. QA generates it from the reference "
            "tokenizer (spec, embed-v3 section 1); this test cannot pass until it lands."
        )
    fixture = json.loads(GOLDEN.read_text(encoding="utf-8"))
    cases = fixture["cases"]
    assert len(cases) >= 11, "golden fixture must cover the 11 pre-registered strings"
    tokenizer = _load_onnx().tokenizer
    for case in cases:
        assert tokenizer.encode(case["text"]) == case["ids"], case["text"][:40]


@pytest.mark.model
def test_onnx_graph_signature() -> None:
    signature = _load_onnx().signature()
    assert signature.inputs == INPUT_NAMES
    assert len(signature.output_shape) == 3 and signature.output_shape[2] == DIM


@pytest.mark.model
def test_onnx_embedding_is_repeatable() -> None:
    first = _load_onnx()
    second = _load_onnx()
    for text in ("Getting started\nInstall the tool.", "How do I resume a run?", "x"):
        a = first.embed_passage(text)
        assert len(a) == DIM
        assert a == first.embed_passage(text) == second.embed_passage(text)
    assert first.embed_query("hello") == second.embed_query("hello")


def test_verify_file_rehashes_and_deletes_on_mismatch(tmp_path: Path) -> None:
    import hashlib

    good = tmp_path / "f.bin"
    good.write_bytes(b"abc")
    verify_file(good, hashlib.sha256(b"abc").hexdigest())
    with pytest.raises(ModelError, match="does not match"):
        verify_file(good, "0" * 64)
    assert not good.exists()
    with pytest.raises(ModelError, match="missing"):
        verify_file(good, "0" * 64)


def test_model_dir_layout() -> None:
    p = EmbeddingParams()
    assert model_dir(Path("m"), p) == Path("m") / "BAAI--bge-small-en-v1.5" / p.revision
