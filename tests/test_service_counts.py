"""Counts without content: totals only, no question text, a bounded docs-click beacon.

Reached over HTTP only, so on the base commit each test fails on an assertion.
"""

from __future__ import annotations

import html.parser
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from service_fakes import (
    ANSWERABLE_REPLY,
    CANARY,
    NOT_ANSWERABLE_REPLY,
    FakeClock,
    FakeJudgeClient,
    make_app,
    make_runtime,
    make_settings,
)

from aveto_service.judge_port import JudgeCall
from aveto_service.pages import HtmlPages

QUESTION = "how do I install the tool"
FORM = {"Content-Type": "application/x-www-form-urlencoded"}


class _Rows(html.parser.HTMLParser):
    """`dt` text to the text of the `dd.value` that follows it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: dict[str, str] = {}
        self._in: str | None = None
        self._label = ""
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = (dict(attrs).get("class") or "").split()
        if tag == "dt":
            self._in = "dt"
        elif tag == "dd" and "value" in classes:
            self._in = "value"
        else:
            return
        self._buf = []

    def handle_data(self, data: str) -> None:
        if self._in is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag not in ("dt", "dd") or self._in is None:
            return
        text = "".join(self._buf).strip()
        if self._in == "dt":
            self._label = text
        else:
            self.rows[self._label] = text
        self._in = None


def figure_rows(page: str) -> dict[str, str]:
    parser = _Rows()
    parser.feed(page)
    parser.close()
    return parser.rows


def test_counts_record_no_question_text() -> None:
    fake = FakeJudgeClient([JudgeCall(ANSWERABLE_REPLY, 2400, 20), JudgeCall(NOT_ANSWERABLE_REPLY, 2400, 20)])
    runtime = make_runtime()
    app = make_app(fake, runtime=runtime, html=HtmlPages(runtime))
    c = TestClient(app, client=("203.0.113.9", 5000), follow_redirects=False)
    secret = f"{QUESTION} {CANARY}"
    assert c.get("/").status_code == 200
    assert c.post("/ask", json={"question": secret}).json()["outcome"] == "answer"
    assert c.post("/ask", content=urlencode({"question": secret}), headers=FORM).status_code == 303
    r = c.post("/count/docs-click")
    assert (r.status_code, r.content) == (204, b"")
    r = c.post("/count/docs-click", content=CANARY.encode())
    assert (r.status_code, r.content) == (204, b"")
    snap = app.state.counts.snapshot()
    assert (snap.visits, snap.asked, snap.answered, snap.refused, snap.docs_clicks) == (1, 2, 1, 1, 1)
    assert all(type(getattr(snap, f)) is int for f in ("visits", "answered", "refused", "docs_clicks"))
    assert CANARY not in repr(snap)
    assert set(type(app.state.counts).__slots__) == {
        "_lock",
        "_visits",
        "_answered",
        "_refused",
        "_docs_clicks",
        "_started_at",
        "_clicks",
        "_mono",
    }
    page = c.get("/scorecard")
    assert page.status_code == 200
    assert CANARY not in page.text and QUESTION not in page.text
    rows = figure_rows(page.text)
    labels = ("Visits", "Questions asked", "Answered", "Not answered", "Clicks to the docs")
    assert [rows[k] for k in labels] == ["1", "2", "1", "1", "1"]


def test_docs_click_rules() -> None:
    clock = FakeClock()
    runtime = make_runtime()
    app = make_app(FakeJudgeClient(), runtime=runtime, html=HtmlPages(runtime), clock=clock)
    c = TestClient(app, client=("203.0.113.9", 5000), follow_redirects=False)
    counts = app.state.counts

    def click(**kw: object) -> None:
        r = c.post("/count/docs-click", **kw)  # type: ignore[arg-type]
        assert (r.status_code, r.content) == (204, b"")

    click()
    assert counts.snapshot().docs_clicks == 1
    click(headers={"Origin": "http://testserver"})  # same origin is counted
    assert counts.snapshot().docs_clicks == 2
    before = counts.snapshot().docs_clicks
    click(headers={"Origin": "https://evil.example"})
    click(headers={"Sec-Fetch-Site": "cross-site"})
    click(content=b"x")
    assert counts.snapshot().docs_clicks == before
    # the kill switch on: not counted
    off_runtime = make_runtime()
    off = make_app(
        FakeJudgeClient(), runtime=off_runtime, html=HtmlPages(off_runtime),
        settings=make_settings(kill_switch="on"),
    )
    oc = TestClient(off, client=("203.0.113.9", 5000))
    r = oc.post("/count/docs-click")
    assert (r.status_code, r.content) == (204, b"")
    assert off.state.counts.snapshot().docs_clicks == 0
    # 60 counted in a rolling hour, then no more; an hour later one more
    for _ in range(60 - before):
        click()
    assert counts.snapshot().docs_clicks == 60
    click()
    assert counts.snapshot().docs_clicks == 60
    clock.advance(3601)
    click()
    assert counts.snapshot().docs_clicks == 61
