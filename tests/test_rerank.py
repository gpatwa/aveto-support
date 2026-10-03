from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import COMMIT, REPO, FakeEmbedder, FakeReranker, embed_all

from aveto_support.__main__ import main
from aveto_support.embed import (
    INPUT_NAMES,
    ModelError,
    WordPiece,
    passage_input,
    sha256_file,
)
from aveto_support.index import Index, RetrievalParams, split_passages, write_index
from aveto_support.rerank import (
    OnnxReranker,
    PlaceholderReranker,
    RerankParams,
    encode_pair,
    reranker_dir,
)
from aveto_support.search import (
    FileHit,
    PassageMatch,
    RetrievalResult,
    Searcher,
    retrieve,
)

FAKE = FakeEmbedder()
GOLDEN = Path(__file__).parent / "fixtures" / "wordpiece_golden.json"

DOCS = {
    f"area/f{i:02d}.md": (
        f"# Topic{i}\nShared intro words alpha beta{i % 3}.\n## Part{i}\nDetail{i} gamma delta{i % 4} "
        f"alpha unique{i}.\n"
    )
    for i in range(30)
}
QUESTION = "alpha gamma detail3 unique3 intro"


def build(docs: dict[str, str] = DOCS, reranker: object | None = None) -> Searcher:
    passages = []
    for path, text in docs.items():
        passages.extend(split_passages(path, text))
    passages.sort(key=lambda p: (p.path, p.line_start))
    index = Index(REPO, COMMIT, len(docs), (), tuple(embed_all(passages)), 0.3, RetrievalParams())
    return Searcher(index, FAKE, reranker)  # type: ignore[arg-type]


def first_stage(question: str = QUESTION) -> RetrievalResult:
    return retrieve(build(), question)


class Constant:
    def score(self, question: str, passage_text: str) -> float:
        return 0.0


class Bad:
    def __init__(self, value: object) -> None:
        self.value = value

    def score(self, question: str, passage_text: str) -> float:
        return self.value  # type: ignore[return-value]


def vocab() -> WordPiece:
    tokens = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "a", "b", "c", "d"]
    return WordPiece(tokens)


# --- the pin and the pair encoding -------------------------------------------


def test_placeholder_reranker_raises() -> None:
    with pytest.raises(RuntimeError, match="not configured in this build"):
        PlaceholderReranker().score("q", "p")


def test_rerank_params_pin_is_well_formed() -> None:
    p = RerankParams()
    assert p.model == "cross-encoder/ms-marco-MiniLM-L6-v2"
    assert p.revision == "233902d25c440f23af6f7d6e94d2946bac0bee0a"
    assert p.onnx_sha256.startswith("5d3e70fd") and p.onnx_sha256.endswith("4d4a")
    assert p.vocab_sha256.startswith("07eced37") and p.vocab_sha256.endswith("38a3")
    assert p.candidates == 20 and p.max_tokens == 512 and p.max_question_tokens == 64


@pytest.mark.parametrize("bad", ["abc123", "A" * 40, "main", "a" * 39, "a" * 41])
def test_reranker_revision_must_be_40_hex(bad: str) -> None:
    with pytest.raises(ValueError, match="40-hex"):
        RerankParams(revision=bad)


def test_reranker_sha256_must_be_64_hex() -> None:
    with pytest.raises(ValueError, match="64"):
        RerankParams(onnx_sha256="a" * 63)
    with pytest.raises(ValueError, match="64"):
        RerankParams(vocab_sha256="A" * 64)
    with pytest.raises(ValueError, match="owner/name"):
        RerankParams(model="no-owner")


def test_reranker_dir_layout(tmp_path: Path) -> None:
    p = RerankParams()
    assert reranker_dir(tmp_path, p) == tmp_path / "cross-encoder--ms-marco-MiniLM-L6-v2" / p.revision


def test_pair_encoding_layout() -> None:
    ids, types = encode_pair(vocab(), "a b", "c d c")
    assert ids == [2, 4, 5, 3, 6, 7, 6, 3]
    assert types == [0, 0, 0, 0, 1, 1, 1, 1]


def test_pair_encoding_truncates_to_512() -> None:
    ids, types = encode_pair(vocab(), "a b", "c " * 1000)
    assert len(ids) == len(types) == 512
    assert ids[:4] == [2, 4, 5, 3] and ids[-1] == 3
    assert types[:4] == [0, 0, 0, 0] and set(types[4:]) == {1}


def test_pair_encoding_caps_question_at_64() -> None:
    ids, types = encode_pair(vocab(), "a " * 100, "c d")
    assert ids[1:65] == [4] * 64 and ids[65] == 3
    assert len(ids) == 64 + 2 + 2 + 1 and types[:66] == [0] * 66


# --- the reranked method, with a fake ----------------------------------------


def test_constant_reranker_is_identity() -> None:
    base = first_stage()
    reranked = retrieve(build(reranker=Constant()), QUESTION)
    assert [f.path for f in reranked.files] == [f.path for f in base.files]
    assert [f.passages for f in reranked.files] == [f.passages for f in base.files]
    assert [f.rank for f in reranked.files] == [1, 2, 3, 4, 5]


def test_rerank_only_reorders_top_n() -> None:
    searcher = build()
    order = _first_stage_order(searcher)
    outsider = order[20]

    class Loves:
        def __init__(self) -> None:
            self.seen: list[str] = []

        def score(self, question: str, passage_text: str) -> float:
            self.seen.append(passage_text)
            return 100.0 if passage_text == outsider_text else 0.0

    outsider_text = passage_input(searcher.passages_of(outsider)[0])
    fake = Loves()
    result = retrieve(build(reranker=fake), QUESTION)
    assert outsider not in [f.path for f in result.files]
    assert outsider_text not in fake.seen


def _first_stage_order(searcher: Searcher) -> list[str]:
    """The full first-stage order, via a result wide enough to show every file."""
    wide = Index(
        REPO, COMMIT, 0, (), searcher.index.passages, 0.3, RetrievalParams(top_k=len(DOCS))
    )
    return [f.path for f in retrieve(Searcher(wide, FAKE), QUESTION).files]


def test_reranker_sees_only_shown_passages() -> None:
    searcher = build()
    order = _first_stage_order(searcher)
    fake = FakeReranker()
    retrieve(build(reranker=fake), QUESTION)
    assert len(fake.calls) <= 40
    wide = Index(REPO, COMMIT, 0, (), searcher.index.passages, 0.3, RetrievalParams(top_k=len(DOCS)))
    shown = retrieve(Searcher(wide, FAKE), QUESTION)
    expected = [
        passage_input(m.passage) for f in shown.files[:20] for m in f.passages
    ]
    assert [text for _, text in fake.calls] == expected
    assert order[:20] == [f.path for f in shown.files[:20]]
    assert {q for q, _ in fake.calls} == {QUESTION}


def test_rerank_file_score_is_maxp() -> None:
    fake = FakeReranker()
    result = retrieve(build(reranker=fake), QUESTION)
    for hit in result.files:
        scores = [fake.score(QUESTION, passage_input(m.passage)) for m in hit.passages]
        assert hit.score == max(scores)
    assert [f.score for f in result.files] == sorted((f.score for f in result.files), reverse=True)


def test_rerank_ties_break_by_first_stage_rank() -> None:
    class Tiered:
        def score(self, question: str, passage_text: str) -> float:
            return 1.0 if "Topic3" in passage_text or "Topic4" in passage_text else 0.0

    base = first_stage()
    result = retrieve(build(reranker=Tiered()), QUESTION)
    boosted = [f.path for f in result.files if f.score == 1.0]
    rest = [f.path for f in result.files if f.score == 0.0]
    assert [f.path for f in result.files] == boosted + rest
    base_pos = {f.path: f.rank for f in base.files}
    for group in (boosted, rest):
        ranks = [base_pos.get(p, 99) for p in group]
        assert ranks == sorted(ranks)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_rerank_non_finite_score_fails_closed(bad: float, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(ModelError, match="non-finite"):
        retrieve(build(reranker=Bad(bad)), QUESTION)
    idx = tmp_path / "i.json"
    write_index(build().index, idx)
    assert main(["retrieve", "--index", str(idx), QUESTION], embedder=FAKE, reranker=Bad(bad)) == 2
    assert "non-finite" in capsys.readouterr().err


def test_rerank_is_deterministic() -> None:
    searcher = build(reranker=FakeReranker())
    assert retrieve(searcher, QUESTION) == retrieve(searcher, QUESTION)


# --- INV-4 -------------------------------------------------------------------


def test_reranked_hits_are_verbatim_passages() -> None:
    searcher = build(reranker=FakeReranker())
    index_passages = {(p.path, p.line_start): p for p in searcher.index.passages}
    result = retrieve(searcher, QUESTION)
    for hit in result.files:
        lines = DOCS[hit.path].split("\n")
        for m in hit.passages:
            p = m.passage
            assert m.passage is index_passages[(p.path, p.line_start)]
            assert p.text == "\n".join(lines[p.line_start - 1 : p.line_end])
            assert p.path == hit.path and p.heading_path
            assert f"#L{p.line_start}-L{p.line_end}" in m.url


def test_reranked_result_invariant_enforced() -> None:
    result = retrieve(build(reranker=FakeReranker()), QUESTION)
    first = result.files[0]
    other = result.files[1].passages
    with pytest.raises(ValueError, match="another file"):
        FileHit(1, first.path, 1.0, first.url, other)
    with pytest.raises(ValueError, match="1..n"):
        RetrievalResult("q", (result.files[1],), 0.0, 0.0, "m")
    with pytest.raises(ValueError, match="distinct"):
        RetrievalResult("q", (first, FileHit(2, first.path, 1.0, first.url, first.passages)), 0.0, 0.0, "m")
    candidates = {p.path for p in build().index.passages}
    assert {f.path for f in result.files} <= candidates
    assert all(isinstance(m, PassageMatch) for f in result.files for m in f.passages)


def test_reranker_returns_only_scores() -> None:
    for bad in ("an invented sentence", None, [1.0], True):
        with pytest.raises(ModelError, match="non-numeric"):
            retrieve(build(reranker=Bad(bad)), QUESTION)
    marker = "INVENTED-BY-RERANKER"
    result = retrieve(build(reranker=FakeReranker()), QUESTION)
    blob = json.dumps(
        [(f.path, f.url, [(m.passage.text, m.url) for m in f.passages]) for f in result.files]
    )
    assert marker not in blob


def test_ranking_mode_names_both_models() -> None:
    base = first_stage()
    assert base.ranking_mode == "file-rrf-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
    mode = retrieve(build(reranker=FakeReranker()), QUESTION).ranking_mode
    assert mode == (
        "file-rerank-v1:hybrid:BAAI/bge-small-en-v1.5@5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
        "+ce:cross-encoder/ms-marco-MiniLM-L6-v2@233902d25c440f23af6f7d6e94d2946bac0bee0a:n20"
    )


# --- the CLI -----------------------------------------------------------------


def _index(tmp_path: Path) -> Path:
    idx = tmp_path / "i.json"
    write_index(build().index, idx)
    return idx


def test_cli_retrieve_ranking_switch(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx = _index(tmp_path)
    assert main(["retrieve", "--index", str(idx), "--ranking", "file-rrf-v1", QUESTION], embedder=FAKE,
                reranker=Bad("must not be called")) == 0
    out = capsys.readouterr().out
    assert "Ranking: file-rrf-v1:hybrid:" in out and "file-rerank-v1" not in out
    assert main(["retrieve", "--index", str(idx), "--ranking", "file-rrf-v1", QUESTION], embedder=FAKE) == 0
    assert capsys.readouterr().out == out
    fake = FakeReranker()
    assert main(["retrieve", "--index", str(idx), QUESTION], embedder=FAKE, reranker=fake) == 0
    assert "Ranking: file-rerank-v1:hybrid:" in capsys.readouterr().out
    assert fake.calls


def test_cli_eval_ranking_switch_on_synthetic_set(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx = _index(tmp_path)
    ev = tmp_path / "e.toml"
    ev.write_text(
        f'pinned_commit = "{COMMIT}"\n[[question]]\nid = "a1"\nquestion = "{QUESTION}"\n'
        'sources = ["area/f03.md"]\n'
    )
    for ranking, codes in (("file-rrf-v1", {0, 1}), ("file-rerank-v1", {0, 1})):
        code = main(["eval", "--index", str(idx), "--eval-file", str(ev), "--ranking", ranking],
                    embedder=FAKE, reranker=FakeReranker())
        lines = capsys.readouterr().out.split("\n")
        assert code in codes
        assert lines[0].startswith(f"Ranking: {ranking}:hybrid:")
        assert f"ranking: {ranking}" in lines[1]
        assert lines[-2] in ("eval: PASS", "eval: FAIL") or lines[-1] in ("eval: PASS", "eval: FAIL")


def test_cli_default_mode_without_reranker_cache_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx = _index(tmp_path)
    assert main(["retrieve", "--index", str(idx), QUESTION], embedder=FAKE, models_dir=tmp_path / "none") == 2
    captured = capsys.readouterr()
    assert "run ingest" in captured.err and captured.out == ""


# --- the real model: needs the approved cached files (pytest -m model) -------

pytestmark_model = pytest.mark.model


def _load() -> OnnxReranker:
    return OnnxReranker.load(Path(__file__).parent.parent / "models")


@pytestmark_model
def test_reranker_tokenizer_matches_golden() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    base = reranker_dir(Path(__file__).parent.parent / "models", RerankParams())
    assert sha256_file(base / "vocab.txt") == golden["generated_by"]["vocab_sha256"]
    reranker = _load()
    for case in golden["cases"]:
        assert reranker.tokenizer.encode(case["text"]) == case["ids"], case["text"]


@pytestmark_model
def test_reranker_onnx_signature() -> None:
    sig = _load().signature()
    assert sig.inputs == INPUT_NAMES
    assert len(sig.output_shape) == 2 and sig.output_shape[-1] == 1


PAIRS = [
    ("How do I install the package?", "Installation\nRun the installer and follow the prompts to install."),
    ("How do I install the package?", "Release notes\nVersion 2 adds a new colour theme."),
    ("Where are logs stored?", "Logging\nLog files are written to the logs directory."),
]


@pytestmark_model
def test_reranker_scores_repeatable() -> None:
    first = [_load().score(q, p) for q, p in PAIRS]
    second = [_load().score(q, p) for q, p in PAIRS]
    assert first == second


@pytestmark_model
def test_reranker_known_answer() -> None:
    reranker = _load()
    relevant, unrelated = (reranker.score(q, p) for q, p in PAIRS[:2])
    assert relevant > unrelated
