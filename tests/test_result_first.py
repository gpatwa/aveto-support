"""A result page puts the question box and the result before "What to expect"; the home page is unchanged.

The goldens in `tests/golden/*-6ab5548.*` were written on commit 6ab5548, before the render change, by
`uv run python tests/test_result_first.py --write-goldens`. T2 and T3 pin that nothing but the order
moved (home pages byte-equal; every visible string and aria-label of each result page unchanged).
T4 is a pure pin on the script's strings. T1, T5, T6, T7 and the order assertions in T2 and T3 are new
behaviour and fail on 6ab5548.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode

REPO_ROOT = Path(__file__).resolve().parent.parent
if __name__ == "__main__":  # run as a script: the repo root is not on the path yet
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from service_fakes import (
    NOT_ANSWERABLE_REPLY,
    FakeJudgeClient,
    make_app,
    make_runtime,
    make_settings,
)

from aveto_service.judge_port import JudgeCall
from aveto_service.pages import HtmlPages
from aveto_service.pipeline import AskService

GOLDEN_DIR = Path(__file__).resolve().parent / "golden"
BASE = "6ab5548"
STATIC = REPO_ROOT / "aveto_service" / "static"
QUESTION = "how do I install the tool"
FORM = {"Content-Type": "application/x-www-form-urlencoded"}
STATEMENT = (
    "Verbatim passages from Aveto's docs; an AI model decides only whether they answer. "
    "Nothing on this page is written by an AI model."
)

HOME_GOLDENS = {
    "home": GOLDEN_DIR / f"home-{BASE}.html",
    "resting": GOLDEN_DIR / f"home-resting-{BASE}.html",
    "off": GOLDEN_DIR / f"home-off-{BASE}.html",
}
STRINGS_GOLDEN = GOLDEN_DIR / f"result-strings-{BASE}.json"


def _client(
    fake: FakeJudgeClient | None = None, **kw: object
) -> tuple[TestClient, AskService]:
    runtime = make_runtime()
    app = make_app(fake or FakeJudgeClient(), runtime=runtime, html=HtmlPages(runtime), **kw)  # type: ignore[arg-type]
    client = TestClient(app, client=("203.0.113.9", 5000), follow_redirects=False)
    return client, app.state.service


def _post(client: TestClient, text: str) -> object:
    return client.post("/ask", content=urlencode({"question": text}), headers=FORM)


def _followed(client: TestClient, text: str) -> str:
    r = _post(client, text)
    assert r.status_code == 303  # type: ignore[attr-defined]
    page = client.get(r.headers["location"].split("#")[0])  # type: ignore[attr-defined]
    assert page.status_code == 200
    return str(page.text)


def _text(r: object) -> str:
    return str(r.text)  # type: ignore[attr-defined]


def home_pages() -> dict[str, str]:
    client, _ = _client()
    out = {"home": client.get("/").text}
    unknown = client.get("/result/unknown-token")
    assert unknown.status_code == 200
    out["unknown"] = unknown.text
    resting, rservice = _client()
    rservice._spend.cap = rservice._floor - 1
    assert rservice.resting()
    out["resting"] = resting.get("/").text
    off, _ = _client(settings=make_settings(kill_switch="on"))
    out["off"] = off.get("/").text
    return out


def result_pages() -> dict[str, str]:
    out: dict[str, str] = {}
    client, _ = _client()
    out["answer"] = _followed(client, QUESTION)
    refused, _ = _client(FakeJudgeClient(default=JudgeCall(NOT_ANSWERABLE_REPLY, 100, 5)))
    out["refusal"] = _followed(refused, QUESTION)
    broken, _ = _client(FakeJudgeClient(default=JudgeCall("garbage", 100, 5)))
    out["judge_error"] = _followed(broken, QUESTION)
    limited, _ = _client()
    for _i in range(10):
        assert _post(limited, QUESTION).status_code == 303  # type: ignore[attr-defined]
    out["rate_limited"] = _text(_post(limited, QUESTION))
    paused, pservice = _client()
    pservice._spend.cap = pservice._floor + 1000
    out["paused"] = _text(_post(paused, QUESTION))
    off, _ = _client(settings=make_settings(kill_switch="on"))
    out["service_off"] = _text(_post(off, QUESTION))
    empty, _ = _client()
    out["empty"] = _text(_post(empty, "   "))
    long, _ = _client()
    out["too_long"] = _text(_post(long, "a" * 501))
    return out


class _Strings(HTMLParser):
    """Every visible text node and every aria-label value, in a flat list."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "title"):
            self._skip += 1
        for name, value in attrs:
            if name == "aria-label" and value:
                self.found.append(f"aria-label={value}")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "title") and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text and not self._skip:
            self.found.append(text)


def strings_of(page: str) -> list[str]:
    p = _Strings()
    p.feed(page)
    return sorted(p.found)


def write_goldens() -> None:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    homes = home_pages()
    for name, path in HOME_GOLDENS.items():
        path.write_text(homes[name], encoding="utf-8")
    assert homes["unknown"] == homes["home"]
    pages = result_pages()
    STRINGS_GOLDEN.write_text(
        json.dumps(
            {"base": BASE, "cases": {k: strings_of(v) for k, v in pages.items()}},
            indent=1,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(HOME_GOLDENS)} home goldens and {len(pages)} string cases")


def _order(page: str) -> list[int]:
    marks = [
        "<h1>",
        STATEMENT,
        '<form id="ask-form"',
        '<section id="result"',
        '<h2 class="plain">What to expect</h2>',
        '<h2 class="plain">Try a question</h2>',
        "<footer>",
    ]
    for m in marks:
        assert page.count(m) == 1, m
    return [page.index(m) for m in marks]


# --- T1 ---------------------------------------------------------------------------------------


def test_result_page_order_question_box_result_then_expectations() -> None:
    for name, page in result_pages().items():
        at = _order(page)
        assert at == sorted(at), f"{name}: title, statement, box, result, expectations, suggestions"


# --- T2 ---------------------------------------------------------------------------------------


def test_reorder_applies_only_to_answers_of_a_question() -> None:
    homes = home_pages()
    for name, path in HOME_GOLDENS.items():
        assert homes[name] == path.read_text("utf-8"), f"GET / ({name}) must not change"
    assert homes["unknown"] == HOME_GOLDENS["home"].read_text("utf-8")
    for key in ("home", "off"):
        page = homes[key]
        assert page.index("What to expect") < page.index('<form id="ask-form"')
    answer = result_pages()["answer"]
    assert answer.index('<form id="ask-form"') < answer.index("What to expect")


# --- T3 ---------------------------------------------------------------------------------------


def test_result_pages_keep_every_string_only_moved() -> None:
    golden = json.loads(STRINGS_GOLDEN.read_text("utf-8"))
    assert golden["base"] == BASE
    pages = result_pages()
    assert set(pages) == set(golden["cases"])
    for name, page in pages.items():
        assert Counter(strings_of(page)) == Counter(golden["cases"][name]), name
        title = re.search(r'id="result-title"[^>]*>([^<]*)<', page)
        assert title, name
        wanted = [
            page.index(STATEMENT),
            page.index(">Your question about Aveto<"),
            page.index(title.group(0)),
            page.index(">What to expect<"),
            page.index(">Try a question<"),
        ]
        assert wanted == sorted(wanted), f"{name}: strings out of order"


# --- T4 ---------------------------------------------------------------------------------------

SCRIPT_STRINGS = [
    "Looking through the docs",
    "Your question has been sent.",
    "Still working",
    "This is taking longer than usual. Please keep this page open.",
    "Still waiting",
    "This is taking more than a minute. You can keep waiting. If nothing changes, reload the page and ask again.",
    "Waiting: ",
    " second",
    " seconds",
    "Up to 500 characters. Press Ctrl+Enter or Cmd+Enter to send.",
    "Choose one to put it in the box, then press Ask. Three are answered in the docs and one is not, so you can see both outcomes.",
    "We couldn't reach the service",
    "Check your connection and try again. Your question is still in the box.",
    "Enter a question before you press Ask.",
    "Shorten your question to 500 characters or fewer.",
    "Asking...",
    '"Ask"',
    " characters over the limit of ",
    "Shorten your question.",
    "Over the limit by ",
    " characters left",
    " of ",
    " characters",
    "Question loaded. Press Ask to send it.",
    "Copied",
    "Copy link",
    "Link copied.",
    "Couldn't copy the link. Use the source link instead.",
    "Ready to search the docs.",
]


def test_script_strings_unchanged() -> None:
    js = (STATIC / "enhance.js").read_text("utf-8")
    for s in SCRIPT_STRINGS:
        assert s in js, s


# --- T5 to T7 ---------------------------------------------------------------------------------


def _function_body(js: str, name: str) -> str:
    start = js.index(f"function {name}(")
    depth = 0
    for i in range(js.index("{", start), len(js)):
        depth += js[i] == "{"
        depth -= js[i] == "}"
        if depth == 0:
            return js[start : i + 1]
    raise AssertionError(name)


def test_focus_lands_on_the_result_without_scrolling_it() -> None:
    js = (STATIC / "enhance.js").read_text("utf-8")
    assert "region.focus()" not in js
    assert "region.focus({ preventScroll: true })" in _function_body(js, "land")
    settle = _function_body(js, "settle")
    assert "land()" in settle and "q.focus()" in settle
    client, _ = _client()
    page = _text(client.get("/"))
    assert '<section id="result" tabindex="-1"' in page
    assert '<form id="ask-form" method="post" action="/ask#result">' in page
    r = _post(client, QUESTION)
    assert r.headers["location"].endswith("#result")  # type: ignore[attr-defined]


def test_script_scrolls_the_heading_to_the_top_without_motion() -> None:
    js = (STATIC / "enhance.js").read_text("utf-8")
    css = (STATIC / "style.css").read_text("utf-8")
    land = _function_body(js, "land")
    assert "scrollTo(" in land
    assert 'getElementById("result-title")' in land
    assert "TOP_GAP" in land and "var TOP_GAP" in js
    assert "smooth" not in js and "smooth" not in css
    rule = re.search(r"^#result\s*\{[^}]*\}", css, re.MULTILINE)
    assert rule and "scroll-margin-top" in rule.group(0)


def test_script_puts_result_first_once_after_ask() -> None:
    js = (STATIC / "enhance.js").read_text("utf-8")
    moved = _function_body(js, "resultFirst")
    assert "moved" in moved and "compareDocumentPosition" in moved
    assert "resultFirst()" in _function_body(js, "land")
    assert "land()" in _function_body(js, "settle")
    assert re.search(r'location\.hash === "#result"[^;]*\{?\s*land\(\)', js, re.DOTALL)


if __name__ == "__main__":
    if sys.argv[1:] == ["--write-goldens"]:
        write_goldens()
    else:
        raise SystemExit("usage: test_result_first.py --write-goldens")
