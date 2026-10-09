from __future__ import annotations

from pathlib import Path

import pytest
from conftest import (
    COMMIT,
    REPO,
    FakeEmbedder,
    FakeOpener,
    FakeReranker,
    as_opener,
    config_text,
    embed_all,
    make_archive,
)

from aveto_support.__main__ import main
from aveto_support.evaluate import (
    EvalFormatError,
    EvalQuestion,
    EvalSet,
    check_commit,
    format_report,
    load_eval_set,
    score,
)
from aveto_support.index import (
    Index,
    RetrievalParams,
    load_index,
    split_passages,
    write_index,
)
from aveto_support.ingest import run_ingest
from aveto_support.search import Searcher

DOCS = {
    "pets/cats.md": "# Cats\nCats purr and chase mice.\n",
    "pets/dogs.md": "# Dogs\nDogs bark and fetch sticks.\n",
    "farm/cows.md": "# Cows\nCows graze in meadows.\n",
    "farm/hens.md": "# Hens\nHens lay eggs daily.\n",
    "sea/whales.md": "# Whales\nWhales sing under water.\n",
    "sea/crabs.md": "# Crabs\nCrabs scuttle sideways.\n",
    "zzz/last.md": "# Last\nNothing about animals lives here.\n",
    **{f"misc/f{i:02d}.md": f"# Filler{i}\nunrelated{i} filler{i} words{i}\n" for i in range(14)},
}


FAKE = FakeEmbedder()


def searcher(threshold: float = 0.3, commit: str = COMMIT) -> Searcher:
    passages = []
    for path, text in DOCS.items():
        passages.extend(split_passages(path, text))
    passages.sort(key=lambda p: (p.path, p.line_start))
    index = Index(REPO, commit, len(DOCS), (), tuple(embed_all(passages)), threshold, RetrievalParams())
    return Searcher(index, FAKE)


def answerable(i: int, question: str, source: str) -> EvalQuestion:
    return EvalQuestion(f"a{i:02d}", question, True, (source,))


def unanswerable(i: int, question: str) -> EvalQuestion:
    return EvalQuestion(f"u{i:02d}", question, False)


def test_load_eval_set_parses_both_kinds(tmp_path: Path) -> None:
    f = tmp_path / "e.toml"
    f.write_text(
        'pinned_commit = "abc"\n'
        '[[question]]\nid = "a1"\nquestion = "q?"\nsources = ["x.md", "y.md"]\nwhere = "w"\n'
        '[[question]]\nid = "u1"\nquestion = "z?"\nanswerable = false\nhard_negative = true\n'
    )
    es = load_eval_set(f)
    assert es.pinned_commit == "abc"
    assert es.questions[0] == EvalQuestion("a1", "q?", True, ("x.md", "y.md"))
    assert es.questions[1] == EvalQuestion("u1", "z?", False, (), True)


def test_malformed_eval_file(tmp_path: Path) -> None:
    f = tmp_path / "e.toml"
    for body in (
        "not toml [",
        'pinned_commit = "a"\n',
        'pinned_commit = "a"\n[[question]]\nid = "a1"\nquestion = "q"\n',
        'pinned_commit = "a"\n[[question]]\nid = "a1"\nquestion = "q"\nanswerable = "no"\n',
    ):
        f.write_text(body)
        with pytest.raises(EvalFormatError):
            load_eval_set(f)
    with pytest.raises(EvalFormatError):
        load_eval_set(tmp_path / "missing.toml")


def test_answerable_hit_any_listed_source() -> None:
    q = EvalQuestion("a01", "cats purr", True, ("nothing.md", "pets/cats.md"))
    report = score(searcher(), EvalSet(COMMIT, (q,)))
    assert report.answerable_hits == 1
    assert report.outcomes[0].detail.startswith("pets/cats.md (rank 1)  top score ")


def test_answerable_no_match_is_miss() -> None:
    wrong = score(searcher(), EvalSet(COMMIT, (answerable(1, "cats purr", "zzz/last.md"),)))
    assert wrong.answerable_hits == 0
    assert "expected zzz/last.md; got pets/cats.md" in wrong.outcomes[0].detail


def test_unanswerable_is_diagnostic_only() -> None:
    base = _fake_questions(20, 24)
    extra = tuple(unanswerable(i, "quantum spaceship") for i in range(9))
    plain = score(searcher(), base)
    with_u = score(searcher(), EvalSet(COMMIT, base.questions + extra))
    assert with_u.unanswerable_total == 9 and with_u.passed == plain.passed
    assert (with_u.answerable_hits, with_u.answerable_total) == (20, 24)
    detail = with_u.outcomes[-1].detail
    assert detail.startswith("top file ") and "top score" in detail
    assert not with_u.outcomes[-1].answerable and not with_u.outcomes[-1].hit


def _fake_questions(hits: int, total: int) -> EvalSet:
    """Synthetic set: the first `hits` answerable questions hit, the rest miss."""
    qs = [answerable(i, "cats purr", "pets/cats.md") for i in range(hits)]
    qs += [answerable(i, "cats purr", "zzz/last.md") for i in range(hits, total)]
    return EvalSet(COMMIT, tuple(qs))


def test_threshold_integer_boundaries() -> None:
    assert score(searcher(), _fake_questions(12, 15)).passed
    assert not score(searcher(), _fake_questions(11, 15)).passed
    assert score(searcher(), _fake_questions(4, 5)).passed
    assert not score(searcher(), _fake_questions(3, 5)).passed


def test_format_report_summary_lines() -> None:
    s = searcher()
    es = _fake_questions(20, 24)
    report = score(s, EvalSet(COMMIT, es.questions + (unanswerable(1, "quantum spaceship"),)))
    lines = format_report(report, "e.toml", s.index).split("\n")
    assert "ranking: file-rrf-v1" in lines[0] and "(diagnostic)" in lines[0]
    assert lines[-4].startswith("u01  DIAG")
    assert lines[-3].startswith("answerable:   20/24 (83.3%)  required >= 80%  PASS")
    assert lines[-2] == "unanswerable: 1 (diagnostic only, not gated)"
    assert lines[-1] == "eval: PASS"


def test_eval_with_no_answerable_question_exit_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    idx, ev = _write(tmp_path, 0.3, '[[question]]\nid = "u1"\nquestion = "q"\nanswerable = false\n')
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)], embedder=FAKE, reranker=FakeReranker()) == 2
    assert "at least one answerable" in capsys.readouterr().err
    with pytest.raises(EvalFormatError):
        load_eval_set(ev)


def test_commit_mismatch_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx = tmp_path / "i.json"
    write_index(searcher().index, idx)
    ev = tmp_path / "e.toml"
    ev.write_text('pinned_commit = "other"\n[[question]]\nid = "a1"\nquestion = "q"\nsources = ["x.md"]\n')
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)], embedder=FAKE, reranker=FakeReranker()) == 2
    assert "re-run ingest" in capsys.readouterr().err
    with pytest.raises(EvalFormatError):
        check_commit(searcher().index, EvalSet("other", ()))


def test_missing_index_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["retrieve", "--index", str(tmp_path / "none.json"), "anything"], embedder=FAKE, reranker=FakeReranker()) == 2
    assert capsys.readouterr().err.startswith("error: ")


def _write(tmp_path: Path, threshold: float, eval_body: str) -> tuple[Path, Path]:
    idx, ev = tmp_path / "i.json", tmp_path / "e.toml"
    write_index(searcher(threshold).index, idx)
    ev.write_text(f'pinned_commit = "{COMMIT}"\n' + eval_body)
    return idx, ev


A_CATS = '[[question]]\nid = "a1"\nquestion = "cats purr"\nsources = ["pets/cats.md"]\n'


def test_cli_eval_exit_0_on_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, ev = _write(tmp_path, 0.3, A_CATS)
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)], embedder=FAKE, reranker=FakeReranker()) == 0
    assert capsys.readouterr().out.rstrip().endswith("eval: PASS")


def test_cli_eval_exit_1_on_miss(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, ev = _write(tmp_path, 0.3, A_CATS.replace("pets/cats.md", "zzz/last.md"))
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)], embedder=FAKE, reranker=FakeReranker()) == 1
    assert capsys.readouterr().out.rstrip().endswith("eval: FAIL")


def test_cli_retrieve_below_reference_exit_0_with_files(tmp_path: Path) -> None:
    idx, _ = _write(tmp_path, 0.99, "")
    assert main(["retrieve", "--index", str(idx), "quantum", "spaceship"], embedder=FAKE, reranker=FakeReranker()) == 0


def test_cli_retrieve_output_shape(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, _ = _write(tmp_path, 0.99, "")
    assert main(["retrieve", "--index", str(idx), "--ranking", "file-rrf-v1", "Do", "cats", "purr?"], embedder=FAKE) == 0
    out = capsys.readouterr().out
    assert "no confident match" not in out.lower()
    lines = out.split("\n")
    assert lines[0] == "Sources for: Do cats purr?"
    assert lines[1] == f"Docs: {REPO} @ {COMMIT}"
    assert lines[2].startswith("Ranking: file-rrf-v1:hybrid:BAAI/bge-small-en-v1.5@")
    assert lines[3].startswith("Top score: ") and "ingest reference 0.990" in lines[3]
    assert "1. pets/cats.md  (score " in out
    assert f"https://github.com/{REPO}/blob/{COMMIT}/pets/cats.md\n" in out
    assert "a. lines 1-2  Heading: Cats" in out
    assert "?plain=1#L1-L2" in out
    assert "      | Cats purr and chase mice." in out
    assert sum(1 for line in lines if line[:2] in ("1.", "2.", "3.", "4.", "5.")) == 5
    assert out.rstrip().endswith("These are sources, not an answer.")


def test_cli_ingest_fetch_error_exit_3(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                       capsys: pytest.CaptureFixture[str]) -> None:
    cfg = tmp_path / "s.toml"
    cfg.write_text(config_text())
    import aveto_support.ingest as ingest_mod

    def failing(*args: object, **kwargs: object) -> bytes:
        raise ingest_mod.FetchError("boom")

    monkeypatch.setattr(ingest_mod, "fetch_archive", failing)
    assert main(["ingest", "--config", str(cfg), "--out", str(tmp_path / "i.json")]) == 3
    assert capsys.readouterr().err == "error: boom\n"
    assert main(["ingest", "--config", str(tmp_path / "missing.toml")]) == 2


def test_cli_ingest_end_to_end_and_reload(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cfg = tmp_path / "s.toml"
    cfg.write_text(config_text(include='include = ["pets/", "farm/", "sea/", "zzz/", "misc/"]\n'))
    archive = make_archive({p: t.encode() for p, t in DOCS.items()})
    out = tmp_path / "i.json"
    report = run_ingest(
        cfg, out, opener=as_opener(FakeOpener(archive)), models_dir=tmp_path / "m", embedder=FAKE
    )
    assert load_index(out).files_indexed == report.files_indexed == len(DOCS)


def test_usage_error_exit_2() -> None:
    assert main(["retrieve"]) == 2
    assert main([]) == 2


def test_committed_eval_set_is_well_formed() -> None:
    root = Path(__file__).parent.parent
    es = load_eval_set(root / "evals" / "retrieval.toml")
    assert sum(q.answerable for q in es.questions) >= 20
    assert sum(not q.answerable for q in es.questions) >= 5
    from aveto_support.ingest import load_source_config

    assert es.pinned_commit == load_source_config(root / "docs-source.toml").commit


# --- default ranking and adapter ownership ----------------------------------


def _fail_reranker_load(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> object:
        raise AssertionError("the default ranking must not load the reranker")

    monkeypatch.setattr("aveto_support.rerank.OnnxReranker.load", fail)


def test_retrieve_default_ranking_is_rrf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, _ = _write(tmp_path, 0.3, "")
    assert main(["retrieve", "--index", str(idx), "cats", "purr"], embedder=FAKE) == 0
    out = capsys.readouterr().out
    assert "Ranking: file-rrf-v1" in out and "file-rerank-v1" not in out


def test_eval_default_ranking_is_rrf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, ev = _write(tmp_path, 0.3, A_CATS)
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)], embedder=FAKE) == 0
    lines = capsys.readouterr().out.split("\n")
    assert lines[0].startswith("Ranking: file-rrf-v1") and "ranking: file-rrf-v1" in lines[1]


def test_default_run_loads_no_reranker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fail_reranker_load(monkeypatch)
    idx, ev = _write(tmp_path, 0.3, A_CATS)
    assert main(["retrieve", "--index", str(idx), "cats"], embedder=FAKE) == 0
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)], embedder=FAKE) == 0


def test_rerank_ranking_still_selectable(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, _ = _write(tmp_path, 0.3, "")
    fake = FakeReranker()
    assert main(["retrieve", "--index", str(idx), "--ranking", "file-rerank-v1", "cats", "purr"],
                embedder=FAKE, reranker=fake) == 0
    assert "Ranking: file-rerank-v1" in capsys.readouterr().out and fake.calls


class _Tracked:
    def __init__(self, log: list[str], name: str, inner: object) -> None:
        self._log, self._name, self._inner = log, name, inner

    def close(self) -> None:
        self._log.append(self._name)

    def __getattr__(self, attr: str) -> object:
        return getattr(self._inner, attr)


def test_main_closes_loaded_adapters_in_reverse_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    log: list[str] = []
    monkeypatch.setattr(
        "aveto_support.embed.OnnxEmbedder.load", lambda *a, **k: _Tracked(log, "embedder", FAKE)
    )
    monkeypatch.setattr(
        "aveto_support.rerank.OnnxReranker.load", lambda *a, **k: _Tracked(log, "reranker", FakeReranker())
    )
    idx, ev = _write(tmp_path, 0.3, A_CATS)
    miss = tmp_path / "miss.toml"
    miss.write_text(ev.read_text().replace("pets/cats.md", "zzz/last.md"))
    base = ["eval", "--index", str(idx), "--ranking", "file-rerank-v1", "--eval-file"]
    for eval_file, expected in ((ev, 0), (miss, 1), (tmp_path / "absent.toml", 2)):
        log.clear()
        assert main([*base, str(eval_file)]) == expected
        assert log == ["reranker", "embedder"]
    log.clear()
    assert main(["retrieve", "--index", str(idx), "cats"]) == 0
    assert log == ["embedder"]  # default ranking: no reranker was loaded
    capsys.readouterr()
    # Injected adapters belong to the caller and are never closed.
    log.clear()
    injected = _Tracked(log, "injected", FAKE)
    assert main(["retrieve", "--index", str(idx), "cats"], embedder=injected) == 0  # type: ignore[arg-type]
    assert log == []
