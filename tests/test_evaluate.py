from __future__ import annotations

from pathlib import Path

import pytest
from conftest import COMMIT, REPO, FakeOpener, as_opener, make_archive

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
}


def searcher(threshold: float = 0.5, commit: str = COMMIT) -> Searcher:
    passages = []
    for path, text in DOCS.items():
        passages.extend(split_passages(path, text))
    passages.sort(key=lambda p: (p.path, p.line_start))
    return Searcher(Index(REPO, commit, len(DOCS), (), tuple(passages), threshold, RetrievalParams()))


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
    assert report.answerable_hits == 1 and report.outcomes[0].detail == "pets/cats.md (rank 1)"


def test_answerable_no_match_is_miss() -> None:
    report = score(searcher(), EvalSet(COMMIT, (answerable(1, "quantum spaceship", "pets/cats.md"),)))
    assert report.answerable_hits == 0
    assert "no confident match" in report.outcomes[0].detail
    wrong = score(searcher(), EvalSet(COMMIT, (answerable(1, "cats purr", "farm/cows.md"),)))
    assert wrong.answerable_hits == 0 and "got pets/cats.md" in wrong.outcomes[0].detail


def test_unanswerable_hit_on_no_match() -> None:
    es = EvalSet(COMMIT, (unanswerable(1, "quantum spaceship"), unanswerable(2, "cats purr")))
    report = score(searcher(), es)
    assert [o.hit for o in report.outcomes] == [True, False]
    assert "returned 1 passages" in report.outcomes[1].detail


def _fake_questions(hits: int, total: int) -> EvalSet:
    """Synthetic set: the first `hits` answerable questions hit, the rest miss."""
    qs = [answerable(i, "cats purr", "pets/cats.md") for i in range(hits)]
    qs += [answerable(i, "cats purr", "farm/cows.md") for i in range(hits, total)]
    return EvalSet(COMMIT, tuple(qs))


def test_threshold_integer_boundaries() -> None:
    assert score(searcher(), _fake_questions(20, 24)).answerable_pass
    assert not score(searcher(), _fake_questions(19, 24)).answerable_pass

    def unans(hits: int) -> EvalSet:
        qs = [unanswerable(i, "quantum spaceship") for i in range(hits)]
        qs += [unanswerable(i, "cats purr") for i in range(hits, 6)]
        return EvalSet(COMMIT, tuple(qs))

    assert score(searcher(), unans(5)).unanswerable_pass
    assert not score(searcher(), unans(4)).unanswerable_pass


def test_ungated_diagnostic_does_not_affect_exit() -> None:
    hi = searcher(threshold=1.0)  # withholds everything with < full coverage
    q = EvalQuestion("a01", "cats purr", True, ("pets/cats.md",))
    report = score(hi, EvalSet(COMMIT, (q,)))
    assert report.ungated_recall == 1 and report.answerable_hits in (0, 1)
    strict = score(searcher(threshold=1.01), EvalSet(COMMIT, (q,)))
    assert strict.ungated_recall == 1 and strict.answerable_hits == 0 and not strict.passed


def test_format_report_summary_lines() -> None:
    s = searcher()
    report = score(s, _fake_questions(20, 24))
    lines = format_report(report, "e.toml", s.index).split("\n")
    assert lines[-4].startswith("answerable:   20/24 (83.3%)  required >= 80%  PASS")
    assert lines[-3].startswith("unanswerable: 0/0")
    assert lines[-2].startswith("diagnostic:")
    assert lines[-1] in ("eval: PASS", "eval: FAIL")


def test_commit_mismatch_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx = tmp_path / "i.json"
    write_index(searcher().index, idx)
    ev = tmp_path / "e.toml"
    ev.write_text('pinned_commit = "other"\n[[question]]\nid = "u1"\nquestion = "q"\nanswerable = false\n')
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)]) == 2
    assert "re-run ingest" in capsys.readouterr().err
    with pytest.raises(EvalFormatError):
        check_commit(searcher().index, EvalSet("other", ()))


def test_missing_index_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["retrieve", "--index", str(tmp_path / "none.json"), "anything"]) == 2
    assert capsys.readouterr().err.startswith("error: ")


def _write(tmp_path: Path, threshold: float, eval_body: str) -> tuple[Path, Path]:
    idx, ev = tmp_path / "i.json", tmp_path / "e.toml"
    write_index(searcher(threshold).index, idx)
    ev.write_text(f'pinned_commit = "{COMMIT}"\n' + eval_body)
    return idx, ev


A_CATS = '[[question]]\nid = "a1"\nquestion = "cats purr"\nsources = ["pets/cats.md"]\n'


def test_cli_eval_exit_0_on_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, ev = _write(tmp_path, 0.5, A_CATS)
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)]) == 0
    assert capsys.readouterr().out.rstrip().endswith("eval: PASS")


def test_cli_eval_exit_1_on_miss(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx, ev = _write(tmp_path, 0.5, A_CATS.replace("pets/cats.md", "farm/cows.md"))
    assert main(["eval", "--index", str(idx), "--eval-file", str(ev)]) == 1
    assert capsys.readouterr().out.rstrip().endswith("eval: FAIL")


def test_cli_retrieve_no_match_exit_0(tmp_path: Path) -> None:
    idx, _ = _write(tmp_path, 0.5, "")
    assert main(["retrieve", "--index", str(idx), "quantum", "spaceship"]) == 0


def test_cli_retrieve_prints_no_confident_match_first_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    idx, _ = _write(tmp_path, 0.5, "")
    main(["retrieve", "--index", str(idx), "quantum spaceship"])
    out = capsys.readouterr().out.split("\n")
    assert out[0] == "no confident match"
    assert "pets" not in "\n".join(out)


def test_cli_retrieve_confident_output_names_sources(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    idx, _ = _write(tmp_path, 0.5, "")
    assert main(["retrieve", "--index", str(idx), "Do", "cats", "purr?"]) == 0
    out = capsys.readouterr().out
    assert "1. pets/cats.md  lines 1-2" in out
    assert "Heading: Cats" in out
    assert "?plain=1#L1-L2" in out
    assert "   | Cats purr and chase mice." in out
    assert out.rstrip().endswith("These are sources, not an answer.")


def test_cli_ingest_fetch_error_exit_3(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                       capsys: pytest.CaptureFixture[str]) -> None:
    cfg = tmp_path / "s.toml"
    cfg.write_text(f'repo = "{REPO}"\ncommit = "{COMMIT}"\n')
    import aveto_support.ingest as ingest_mod

    def failing(*args: object, **kwargs: object) -> bytes:
        raise ingest_mod.FetchError("boom")

    monkeypatch.setattr(ingest_mod, "fetch_archive", failing)
    assert main(["ingest", "--config", str(cfg), "--out", str(tmp_path / "i.json")]) == 3
    assert capsys.readouterr().err == "error: boom\n"
    assert main(["ingest", "--config", str(tmp_path / "missing.toml")]) == 2


def test_cli_ingest_end_to_end_and_reload(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cfg = tmp_path / "s.toml"
    cfg.write_text(f'repo = "{REPO}"\ncommit = "{COMMIT}"\n')
    archive = make_archive({p: t.encode() for p, t in DOCS.items()})
    out = tmp_path / "i.json"
    report = run_ingest(cfg, out, opener=as_opener(FakeOpener(archive)))
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
