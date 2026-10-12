from __future__ import annotations

import re
from pathlib import Path

import pytest
from conftest import COMMIT
from test_judge import (
    APPROVED_PROMPT_SHA256,
    DOCS,
    FAKE,
    Out,
    make_index,
    run,
    verdicts_file,
    write_idx,
)

from aveto_support.evaluate import format_report, load_eval_set, score
from aveto_support.index import load_index
from aveto_support.judge_eval import (
    VerdictsFormatError,
    bar_met,
    build_results,
    load_verdicts,
    right_file_rank,
    score_verdicts,
)
from aveto_support.search import Searcher


@pytest.fixture
def work(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".aveto-judge").mkdir()
    write_idx(tmp_path)
    return tmp_path


A_HIT = '[[question]]\nid = "a1"\nquestion = "cats purr"\nsources = ["pets/cats.md"]\n'
A_MISS = '[[question]]\nid = "a2"\nquestion = "cats purr"\nsources = ["zzz/last.md"]\n'
U1 = '[[question]]\nid = "u1"\nquestion = "quantum spaceship"\nanswerable = false\nhard_negative = true\n'
U2 = '[[question]]\nid = "u2"\nquestion = "rocket fuel"\nanswerable = false\n'


def eval_file(work: Path, body: str) -> Path:
    path = work / "e.toml"
    path.write_text(f'pinned_commit = "{COMMIT}"\n' + body)
    return path


def run_eval(capsys: pytest.CaptureFixture[str], ev: Path, *extra: str) -> Out:
    return run(capsys, ["eval", "--eval-file", str(ev), *extra])


def test_eval_without_verdicts_unchanged(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ev = eval_file(work, A_HIT + A_MISS + U1)
    searcher = Searcher(load_index(work / "i.json"), FAKE)
    report = score(searcher, load_eval_set(ev))
    text = format_report(report, str(ev), searcher.index).replace("ranking: file-rrf-v1", "ranking: file-rrf-v1", 1)
    r = run_eval(capsys, ev)
    from aveto_support.search import ranking_mode

    assert r.out == f"Ranking: {ranking_mode(searcher)}\n{text}\n"
    assert r.code == (0 if report.passed else 1) == 1 and r.err == ""
    assert "judge" not in r.out.replace(str(ev), "")


def test_eval_verdicts_exit_code_is_retrieval_gate(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Gate fails (1 of 2 answerable questions hit) while both bars are met.
    ev = eval_file(work, A_HIT + A_MISS + U1)
    vf = verdicts_file(work, ev, {"a1": "ANSWERABLE", "a2": "ANSWERABLE", "u1": "NOT_ANSWERABLE"})
    r = run_eval(capsys, ev, "--verdicts", str(vf))
    assert r.code == 1
    assert r.out.count("MET") == 2 and "NOT MET" not in r.out
    assert r.out.rstrip().endswith("judge: bars reported, not gated here; eval exit code is the retrieval gate")
    # Gate passes while both bars fail.
    ev = eval_file(work, A_HIT + U1)
    vf = verdicts_file(work, ev, {"a1": "NOT_ANSWERABLE", "u1": "ANSWERABLE"})
    r = run_eval(capsys, ev, "--verdicts", str(vf))
    assert r.code == 0
    assert r.out.count("NOT MET") == 2


def test_eval_verdicts_appends_after_unchanged_report(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ev = eval_file(work, A_HIT + U1)
    plain = run_eval(capsys, ev)
    vf = verdicts_file(work, ev, {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE"})
    withv = run_eval(capsys, ev, "--verdicts", str(vf))
    assert withv.out.startswith(plain.out)
    assert withv.code == plain.code


def _bad_cases() -> list[tuple[str, dict[str, object]]]:
    return [
        ("format", {"fmt": "other-v1"}),
        ("prompt_sha256", {"prompt_sha": "0" * 64}),
        ("no verdict for", {"drop": "u1"}),
        ("appears more than once", {"dup": "a1"}),
        ("not a question in the eval set", {"add": "zz9"}),
        ("exactly id, verdict, input_sha256", {"reason": True}),
        ("verdict must be one of", {"token": "MAYBE"}),
        ("input_sha256 is not the hash", {"badhash": "a1"}),
        ("other than format", {"extra": 'note = "x"\n'}),
    ]


@pytest.mark.parametrize(("needle", "case"), _bad_cases(), ids=[n for n, _ in _bad_cases()])
def test_verdicts_loader_rejects(work: Path, capsys: pytest.CaptureFixture[str],
                                 needle: str, case: dict[str, object]) -> None:
    ev = eval_file(work, A_HIT + U1)
    verdicts = {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE"}
    if "drop" in case:
        del verdicts[str(case["drop"])]
    if "token" in case:
        verdicts["a1"] = str(case["token"])
    if "add" in case:
        verdicts[str(case["add"])] = "ANSWERABLE"
    kwargs: dict[str, object] = {}
    if "fmt" in case:
        kwargs["fmt"] = case["fmt"]
    if "prompt_sha" in case:
        kwargs["prompt_sha"] = case["prompt_sha"]
    if "extra" in case:
        kwargs["extra"] = case["extra"]
    if "badhash" in case:
        kwargs["hashes"] = {str(case["badhash"]): "f" * 64}
    if "add" in case:
        kwargs["hashes"] = {str(case["add"]): "f" * 64}
    vf = verdicts_file(work, ev, verdicts, **kwargs)  # type: ignore[arg-type]
    if "dup" in case:
        text = vf.read_text()
        vf.write_text(text + "[[verdict]]" + text.rsplit("[[verdict]]", 1)[1])
    if "reason" in case:
        vf.write_text(vf.read_text().replace('verdict = "ANSWERABLE"', 'verdict = "ANSWERABLE"\nreason = "because"', 1))
    r = run_eval(capsys, ev, "--verdicts", str(vf))
    assert r.code == 2 and r.out == ""
    assert needle in r.err
    if needle in ("input_sha256 is not the hash", "no verdict for"):
        assert re.search(r"error: (a1|u1):", r.err)


def test_verdicts_file_unreadable_or_not_toml(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ev = eval_file(work, A_HIT + U1)
    assert run_eval(capsys, ev, "--verdicts", str(work / "none.toml")).code == 2
    bad = work / "bad.toml"
    bad.write_text("not toml [")
    r = run_eval(capsys, ev, "--verdicts", str(bad))
    assert (r.code, r.out) == (2, "") and "not valid TOML" in r.err


def test_verdicts_requires_default_ranking(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ev = eval_file(work, A_HIT + U1)
    vf = verdicts_file(work, ev, {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE"})
    r = run_eval(capsys, ev, "--ranking", "file-rerank-v1", "--verdicts", str(vf))
    assert (r.code, r.out) == (2, "") and "file-rrf-v1" in r.err


def test_bars_arithmetic(work: Path) -> None:
    assert bar_met(4, 5) and bar_met(16, 20) and bar_met(45, 56)
    assert not bar_met(3, 4) and not bar_met(44, 56) and not bar_met(0, 0) and not bar_met(0, 5)
    ev = eval_file(work, A_HIT + U1 + U2)
    eval_set = load_eval_set(ev)
    results = build_results(Searcher(make_index(DOCS), FAKE), eval_set)
    ok = score_verdicts(eval_set, results, {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE", "u2": "NOT_ANSWERABLE"})
    assert (ok.abstained, ok.unanswerable_total, ok.shown, ok.hit_total, ok.judge_errors) == (2, 2, 1, 1, 0)
    assert (ok.hard_abstained, ok.hard_total) == (1, 1)
    err = score_verdicts(eval_set, results, {"a1": "JUDGE_ERROR", "u1": "JUDGE_ERROR", "u2": "NOT_ANSWERABLE"})
    assert (err.abstained, err.shown, err.judge_errors) == (1, 0, 2)  # an error never helps a bar
    assert not bar_met(err.shown, err.hit_total) and not bar_met(err.abstained, err.unanswerable_total)
    assert [r.agreement for r in err.rows] == ["DIFF", "DIFF", "AGREE"]


def test_missing_right_file_is_not_scored_on_bar_2(work: Path) -> None:
    ev = eval_file(work, A_HIT + A_MISS + U1)
    eval_set = load_eval_set(ev)
    results = build_results(Searcher(make_index(DOCS), FAKE), eval_set)
    rep = score_verdicts(eval_set, results, {"a1": "ANSWERABLE", "a2": "NOT_ANSWERABLE", "u1": "NOT_ANSWERABLE"})
    assert (rep.shown, rep.hit_total, rep.answerable_total) == (1, 1, 2)
    row = rep.rows[1]
    assert (row.expected, row.agreement) == ("show (right file not in top 5)", "n/a")


def test_hit_matches_evaluate_score(work: Path) -> None:
    deep = '[[question]]\nid = "a4"\nquestion = "cats purr"\nsources = ["farm/hens.md"]\n'  # rank 3
    body = A_HIT + A_MISS + deep + '[[question]]\nid = "a3"\nquestion = "whales sing"\nsources = ["sea/whales.md", "x.md"]\n' + U1
    eval_set = load_eval_set(eval_file(work, body))
    searcher = Searcher(make_index(DOCS), FAKE)
    report = score(searcher, eval_set)
    results = build_results(searcher, eval_set)
    assert right_file_rank(results["a4"], ("farm/hens.md",)) == 3
    for q, outcome in zip(eval_set.questions, report.outcomes, strict=True):
        if q.answerable:
            assert (right_file_rank(results[q.id], q.sources) is not None) == outcome.hit, q.id


BARS_LINE = re.compile(
    r"^bars: unanswerable_abstained=(\d+)/(\d+) answerable_hit_not_abstained=(\d+)/(\d+) judge_errors=(\d+)$",
    re.MULTILINE,
)


def test_bars_line_fixed_format(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ev = eval_file(work, A_HIT + A_MISS + U1 + U2)
    vf = verdicts_file(work, ev, {"a1": "ANSWERABLE", "a2": "ANSWERABLE", "u1": "NOT_ANSWERABLE", "u2": "JUDGE_ERROR"})
    r = run_eval(capsys, ev, "--verdicts", str(vf))
    m = BARS_LINE.search(r.out)
    assert m is not None and m.groups() == ("1", "2", "1", "1", "1")
    lines = r.out.split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith("judge: verdicts "))
    assert lines[first].endswith(f"prompt answerability-judge-v1 sha256 {APPROVED_PROMPT_SHA256[:12]}…")
    assert lines[first + 1] == "a1  ANSWERABLE  show (right file rank 1)  AGREE"
    assert lines[first + 2] == "a2  ANSWERABLE  show (right file not in top 5)  n/a"
    assert lines[first + 3] == "u1  NOT_ANSWERABLE  abstain  AGREE"
    assert lines[first + 4] == "u2  JUDGE_ERROR  abstain  DIFF"
    assert lines[first + 5] == "bar 1 (unanswerable abstained):                         1/2 (50.0%)  required >= 80%  NOT MET"
    assert lines[first + 6] == "bar 2 (answerable, right file in top 5, not abstained): 1/1 (100.0%)  required >= 80%  MET"
    assert lines[first + 7] == "judge errors: 1 (counted as failures on both bars)"
    assert lines[first + 8] == "hard negatives abstained: 1/1 (diagnostic)"
    assert lines[first + 9] == "never abstain (today): bar 1 0/2, bar 2 1/1"
    assert lines[first + 10] == "end to end: answerable questions whose right file is shown after judging: 1/2 (diagnostic)"


def test_load_verdicts_direct_error_type(work: Path) -> None:
    ev = eval_file(work, A_HIT + U1)
    eval_set = load_eval_set(ev)
    results = build_results(Searcher(make_index(DOCS), FAKE), eval_set)
    vf = verdicts_file(work, ev, {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE"})
    assert load_verdicts(vf, eval_set, results) == {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE"}
    with pytest.raises(VerdictsFormatError):
        load_verdicts(work / "none.toml", eval_set, results)
