"""The new routes: `POST /warm`, `GET /` at the cap, the route inventory, no judge, no log line.

Reached over HTTP (and `inspect` for the warm-up's source), so on the base commit each test
fails on an assertion.
"""

from __future__ import annotations

import inspect

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from service_fakes import (
    CountingEmbedder,
    FakeJudgeClient,
    logging_state,  # noqa: F401
    make_app,
    make_runtime,
    make_settings,
)
from starlette.responses import PlainTextResponse, Response

from aveto_service.abuse_log import Outcome, configure_logging
from aveto_service.pages import HtmlPages
from aveto_service.pipeline import AskResult, AskService

QUESTION = "how do I install the tool"
PEER = ("203.0.113.9", 5000)


def _client(
    fake: FakeJudgeClient | None = None, *, embedder: CountingEmbedder | None = None, **kw: object
) -> tuple[TestClient, FakeJudgeClient]:
    fake = fake or FakeJudgeClient()
    runtime = make_runtime(embedder=embedder)
    app = make_app(fake, runtime=runtime, html=HtmlPages(runtime), **kw)  # type: ignore[arg-type]
    return TestClient(app, client=PEER, follow_redirects=False), fake


def test_warm_never_reaches_the_judge_or_spends(capfd: pytest.CaptureFixture[str]) -> None:
    embedder = CountingEmbedder()
    c, fake = _client(embedder=embedder)
    h0 = c.get("/health").json()
    capfd.readouterr()
    r = c.post("/warm")
    assert (r.status_code, r.content) == (200, b'{"ready":true}')
    assert embedder.queries == 1 and fake.calls == []
    for _ in range(20):
        assert c.post("/warm").content == b'{"ready":true}'
    assert embedder.queries == 1 and c.get("/health").json() == h0
    assert capfd.readouterr().out == ""
    for _ in range(10):
        assert c.post("/ask", json={"question": QUESTION}).json()["outcome"] == "answer"
    assert len(fake.calls) == 10  # the warm-up used none of the hour's ten
    src = inspect.getsource(AskService.warm)
    for name in ("_judge", "_spend", "_rate", "_retrievals", "emit_abuse", "emit_ops"):
        assert name not in src
    # kill switch on, a cross-site request, resting: not ready, and no retrieval at all
    e1 = CountingEmbedder()
    off, _ = _client(embedder=e1, settings=make_settings(kill_switch="on"))
    assert off.post("/warm").content == b'{"ready":false}'
    e2 = CountingEmbedder()
    cross, _ = _client(embedder=e2)
    assert cross.post("/warm", headers={"Origin": "https://evil.example"}).content == b'{"ready":false}'
    assert cross.post("/warm", headers={"Sec-Fetch-Site": "cross-site"}).content == b'{"ready":false}'
    e3 = CountingEmbedder()
    rest, _ = _client(embedder=e3)
    svc = rest.app.state.service  # type: ignore[attr-defined]
    svc._spend.cap = svc._floor - 1
    assert rest.post("/warm").content == b'{"ready":false}'
    assert e1.queries == e2.queries == e3.queries == 0


def test_warm_reports_not_ready_when_the_search_fails() -> None:
    class Broken(CountingEmbedder):
        def embed_query(self, question: str) -> bytes:
            raise RuntimeError("model missing")

    c, fake = _client(embedder=Broken())
    assert c.post("/warm").content == b'{"ready":false}'
    assert c.post("/warm").content == b'{"ready":false}'  # remembered, not retried
    assert fake.calls == []


class RecordingHtml:
    def __init__(self) -> None:
        self.pages: list[Outcome | None] = []

    def page(self, state: Outcome | None) -> Response:
        self.pages.append(state)
        return PlainTextResponse("page")

    def form_outcome(self, result: AskResult, raw: str) -> Response:
        return PlainTextResponse("form")

    def result_page(self, token: str) -> Response:
        return PlainTextResponse(f"result {token}")

    def static(self, name: str) -> Response:
        return PlainTextResponse(f"static {name}")


def test_get_root_at_the_cap_passes_paused_without_spending() -> None:
    html = RecordingHtml()
    embedder = CountingEmbedder()
    fake = FakeJudgeClient()
    app = make_app(fake, runtime=make_runtime(embedder=embedder), html=html)
    c = TestClient(app, client=PEER)
    service = app.state.service
    assert service.resting() is False  # a fresh service with the default cap
    assert c.get("/").text == "page" and html.pages[-1] is None
    service._spend.cap = service._floor - 1
    before_health = c.get("/health").json()
    before_spend = dict(vars(service._spend))
    assert c.get("/").text == "page"
    assert html.pages[-1] is Outcome.PAUSED
    assert dict(vars(service._spend)) == before_spend
    assert c.get("/health").json() == before_health
    assert fake.calls == [] and embedder.queries == 0
    # the kill switch wins
    off_html = RecordingHtml()
    off = TestClient(
        make_app(FakeJudgeClient(), html=off_html, settings=make_settings(kill_switch="on"))
    )
    off.app.state.service._spend.cap = 0  # type: ignore[attr-defined]
    off.get("/")
    assert off_html.pages[-1] is Outcome.SERVICE_OFF


def test_route_inventory() -> None:
    c, _ = _client()
    routes = sorted(
        (r.path, sorted(r.methods or ())) for r in c.app.routes if isinstance(r, APIRoute)  # type: ignore[attr-defined]
    )
    assert routes == [
        ("/", ["GET"]),
        ("/ask", ["POST"]),
        ("/count/docs-click", ["POST"]),
        ("/health", ["GET"]),
        ("/result/{token}", ["GET"]),
        ("/scorecard", ["GET"]),
        ("/static/{name}", ["GET"]),
        ("/warm", ["POST"]),
    ]
    plain = make_app(FakeJudgeClient())
    plain_routes = sorted((r.path, sorted(r.methods or ())) for r in plain.routes if isinstance(r, APIRoute))
    assert plain_routes == [("/ask", ["POST"]), ("/health", ["GET"])]  # no renderer, no new route
    pc = TestClient(plain)
    assert [pc.get("/scorecard").status_code, pc.post("/warm").status_code,
            pc.post("/count/docs-click").status_code] == [404, 404, 404]


def test_no_route_but_ask_reaches_the_judge() -> None:
    c, fake = _client()
    assert c.get("/").status_code == 200
    assert c.get("/result/x").status_code == 200
    assert c.get("/static/style.css").status_code == 200
    assert c.get("/scorecard").status_code == 200
    assert c.post("/warm").status_code == 200
    assert c.post("/warm").status_code == 200
    assert c.post("/count/docs-click").status_code == 204
    assert c.get("/health").status_code == 200
    assert fake.calls == []


@pytest.mark.usefixtures("logging_state")
def test_new_routes_write_no_log_line(capfd: pytest.CaptureFixture[str]) -> None:
    configure_logging()
    c, _ = _client()
    capfd.readouterr()
    assert c.get("/").status_code == 200
    assert c.get("/scorecard").status_code == 200
    assert c.post("/warm").status_code == 200
    assert c.post("/count/docs-click").status_code == 204
    assert c.post("/count/docs-click", content=b"zqx").status_code == 204
    assert capfd.readouterr().out == ""
