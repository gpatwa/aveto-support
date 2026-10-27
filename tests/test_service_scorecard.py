"""The figures file and the scorecard page: recorded figures only, fail closed.

On the base commit this module fails at import (`aveto_service.scorecard` does not exist yet).
"""

from __future__ import annotations

import html as htmllib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from service_fakes import FakeClock, FakeJudgeClient, make_runtime, make_settings

from aveto_service.app import create_app
from aveto_service.pages import SECURITY_HEADERS, HtmlPages
from aveto_service.scorecard import (
    FIGURES_PATH,
    FiguresError,
    ScorecardPage,
    build_links,
    load_figures,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/gpatwa/aveto-support/"
RECORD = "runs/polished-chat-experience/07-qa-evidence.md"

TESTS_ROW = f"""
[[figure]]
section = "checks"
label = "Tests"
value = "700 passed, 0 failed"
basis = "Measured 2026-10-27 on the final code: uv run pytest, mypy and ruff clean."
record = "{RECORD}"
"""
HEAD = "schema = 1\n"


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "scorecard.toml"
    path.write_text(text, encoding="utf-8")
    return path


def figure(**over: str) -> str:
    base = {
        "section": "checks",
        "label": "Tests",
        "value": "700 passed",
        "basis": "Measured 2026-10-27 on the final code.",
        "record": RECORD,
    }
    base.update(over)
    rows = "\n".join(f'{k} = "{v}"' for k, v in base.items())
    return f"[[figure]]\n{rows}\n"


INVALID = {
    "unknown label": HEAD + figure(label="Uptime"),
    "label in the wrong section": HEAD + figure(section="speed", label="Tests"),
    "unknown section": HEAD + figure(section="other"),
    "missing record": HEAD
    + '[[figure]]\nsection = "checks"\nlabel = "Tests"\nvalue = "1"\nbasis = "Measured today."\n',
    "missing basis": HEAD
    + f'[[figure]]\nsection = "checks"\nlabel = "Tests"\nvalue = "1"\nrecord = "{RECORD}"\n',
    "basis does not start Measured or Recorded": HEAD + figure(basis="Probably fine."),
    "record with a dotdot segment": HEAD + figure(record="runs/../secret.md"),
    "record with a leading slash": HEAD + figure(record="/etc/passwd"),
    "record with a space": HEAD + figure(record="runs/a b.md"),
    "empty value": HEAD + figure(value=""),
    "value too long": HEAD + figure(value="9" * 121),
    "value over two lines": HEAD + figure(value="a\\nb"),
    "basis too long": HEAD + figure(basis="Measured " + "x" * 300),
    "link not on github": HEAD + '[links]\ncharter = "https://example.com/Charter.md"\n',
    "link with a quote": HEAD + '[links]\ncharter = "https://github.com/a/b\\"c"\n',
    "unknown link key": HEAD + '[links]\nhomepage = "https://github.com/a/b"\n',
    "source_base without trailing slash": 'schema = 1\nsource_base = "https://github.com/a/b/blob/x"\n',
    "source_base not on github": 'schema = 1\nsource_base = "http://github.com/a/b/blob/x/"\n',
    "findings on a non-codex row": HEAD
    + figure().rstrip()
    + '\nfindings = ["one"]\n',
    "unknown figure key": HEAD + figure().rstrip() + '\nextra = "x"\n',
    "unknown top-level key": HEAD + 'colour = "red"\n',
    "schema 2": "schema = 2\n",
    "no schema": "",
    "not toml": "schema = = 1",
    "decision with a bad date": HEAD
    + f'[[decision]]\nwho = "The owner"\nwhen = "26/10/2026"\nwhat = "x"\nrecord = "{RECORD}"\n',
    "decision without a record": HEAD
    + '[[decision]]\nwho = "The owner"\nwhen = "2026-10-26"\nwhat = "x"\n',
}


@pytest.mark.parametrize("text", list(INVALID.values()), ids=list(INVALID))
def test_figures_reader_rules(tmp_path: Path, text: str) -> None:
    with pytest.raises(FiguresError):
        load_figures(write(tmp_path, text))


def test_missing_file_is_a_figures_error(tmp_path: Path) -> None:
    with pytest.raises(FiguresError):
        load_figures(tmp_path / "nope.toml")


def test_figures_reader_accepts_a_valid_file(tmp_path: Path) -> None:
    codex = (
        '[[figure]]\nsection = "reviews"\nlabel = "Independent Codex review"\n'
        f'value = "Reviewed"\nbasis = "Recorded 2026-11-01 by the owner."\nrecord = "{RECORD}"\n'
        'findings = ["A finding."]\n'
    )
    decision = (
        f'[[decision]]\nwho = "The owner"\nwhen = "2026-10-26"\nwhat = "Chose."\nrecord = "{RECORD}"\n'
    )
    links = f'[links]\ncharter = "{GITHUB}blob/b/CHARTER.md"\nrun_record = "{GITHUB}tree/b/runs/x"\n'
    text = f'schema = 1\nsource_base = "{GITHUB}blob/b/"\n{TESTS_ROW}{codex}{decision}{links}'
    figures = load_figures(write(tmp_path, text))
    assert [f.label for f in figures.figures] == ["Tests", "Independent Codex review"]
    assert figures.figures[1].findings == ("A finding.",)
    assert figures.decisions[0].who == "The owner"
    assert build_links(write(tmp_path, text)) == {
        "charter": f"{GITHUB}blob/b/CHARTER.md",
        "run_record": f"{GITHUB}tree/b/runs/x",
    }


def test_build_links_is_empty_on_any_error_and_never_raises(tmp_path: Path) -> None:
    assert build_links(write(tmp_path, "schema = 2\n")) == {}
    assert build_links(tmp_path / "nope.toml") == {}
    assert build_links(write(tmp_path, TESTS_ROW)) == {}


def test_committed_figures_file_is_valid_and_every_record_exists() -> None:
    figures = load_figures()
    assert FIGURES_PATH.is_file()
    assert figures.figures and figures.decisions
    for record in [f.record for f in figures.figures] + [d.record for d in figures.decisions]:
        assert (REPO_ROOT / record).is_file(), record
    assert {f.label for f in figures.figures} >= {"Cold start", "Warm response time", "Cost per question"}
    assert all(f.basis.startswith(("Measured ", "Recorded ")) for f in figures.figures)


def card_client(path: Path | None, *, clock: FakeClock | None = None) -> TestClient:
    clk = clock or FakeClock()
    runtime = make_runtime()
    app = create_app(
        runtime,
        FakeJudgeClient(),
        make_settings(),
        HtmlPages(runtime),
        clock=clk.utc,
        monotonic=clk.monotonic,
        scorecard=ScorecardPage(runtime, path=path) if path is not None else None,
    )
    return TestClient(app, client=("203.0.113.9", 5000))


def test_scorecard_shows_only_rows_with_a_record(tmp_path: Path) -> None:
    r = card_client(write(tmp_path, HEAD + TESTS_ROW)).get("/scorecard")
    assert r.status_code == 200
    text = htmllib.unescape(r.text)
    for shown in ("Checks", "Tests", "700 passed, 0 failed", "Measured 2026-10-27 on the final code"):
        assert shown in text
    for hidden in (
        "Speed",
        "Cold start",
        "Reviews",
        "Independent Codex review",
        "Who decided what",
        "How this was built",
        "n/a",
        "coming soon",
        "—",
        "–",
    ):
        assert hidden not in text
    assert "Use since the service last started" in text  # the service's own counts
    empty = htmllib.unescape(card_client(write(tmp_path, HEAD)).get("/scorecard").text)
    assert "No figures have been recorded yet." in empty
    for heading in ("Speed", "Checks", "Reviews", "Who decided what", "How this was built"):
        assert f">{heading}<" not in empty
    assert "Use since the service last started" in empty


def test_scorecard_escapes_recorded_text(tmp_path: Path) -> None:
    text = HEAD + figure(value="1 < 2 & <b>3</b>")
    page = card_client(write(tmp_path, text)).get("/scorecard").text
    assert "<b>3</b>" not in page
    assert "1 &lt; 2 &amp; &lt;b&gt;3&lt;/b&gt;" in page


def test_unreadable_figures_show_s6_with_503(tmp_path: Path) -> None:
    r = card_client(write(tmp_path, "schema = 2\n")).get("/scorecard")
    assert r.status_code == 503
    text = htmllib.unescape(r.text)
    assert "The scorecard can't be shown right now. Please try again later." in text
    assert "Back to Ask the Aveto docs" in text
    for k, v in SECURITY_HEADERS.items():
        assert r.headers[k] == v
    assert "<dl" not in text and "Tests" not in text
    missing = card_client(tmp_path / "nope.toml").get("/scorecard")
    assert missing.status_code == 503


def test_scorecard_markup(tmp_path: Path) -> None:
    base = f"{GITHUB}blob/b/"
    text = (
        f'schema = 1\nsource_base = "{base}"\n{TESTS_ROW}'
        f'[links]\ncharter = "{base}CHARTER.md"\nend_review = "{base}END_REVIEW.md"\n'
    )
    for path in (write(tmp_path, text), None):  # a file with links, then the committed file
        r = card_client(path).get("/scorecard")
        assert r.status_code == 200
        page = r.text
        assert "<script" not in page
        assert re.findall(r"<link\b[^>]*>", page) == ['<link rel="stylesheet" href="/static/style.css">']
        for attr in ("href", "src", "action"):
            for value in re.findall(rf'\s{attr}="([^"]*)"', page):
                assert value.startswith(("/", "https://github.com/")), value
        main = page.split("<main>", 1)[1]
        assert re.search(r'href="([^"]*)"', main).group(1) == "/"  # type: ignore[union-attr]
        flat = htmllib.unescape(page)
        assert (
            "These are totals since the service last started. They go back to zero each time it "
            "restarts, so they are not lifetime totals. This page lists totals only; it shows no "
            "question and no answer."
        ) in flat
        assert "The service started 2026-10-21 07:00 UTC." in flat
        assert "<title>Quality scorecard - Ask the Aveto docs</title>" in page
        for banned in ("style=", "<style", " onclick="):
            assert banned not in page
    page = card_client(write(tmp_path, text)).get("/scorecard").text
    assert f'href="{base}{RECORD}"' in page  # the Source link
    assert f'href="{base}CHARTER.md"' in page and f'href="{base}END_REVIEW.md"' in page
    assert "The Charter" in page and "The end review" in page
    assert "The pull request" not in page  # a link with no target is not rendered
