from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from service_fakes import (
    CANARY,
    NOT_ANSWERABLE_REPLY,
    CountingEmbedder,
    FakeJudgeClient,
    logging_state,  # noqa: F401
    make_app,
    make_runtime,
    make_searcher,
    make_settings,
)
from starlette.responses import PlainTextResponse, Response

from aveto_service.abuse_log import Outcome
from aveto_service.app import create_app, load_runtime
from aveto_service.judge_port import JudgeCall, PlaceholderJudgeClient
from aveto_service.pipeline import AskResult
from aveto_service.settings import Settings
from aveto_support.index import write_index

pytestmark = pytest.mark.usefixtures("logging_state")

IP = "203.0.113.7"
QUESTION = "How do I upgrade the installer?"
JSON_HEADERS = {"content-type": "application/json"}
FORM_HEADERS = {"content-type": "application/x-www-form-urlencoded"}


def client_of(fake: FakeJudgeClient, **kw: object) -> TestClient:
    return TestClient(make_app(fake, **kw), client=(IP, 5000))  # type: ignore[arg-type]


def test_ask_json_contract() -> None:
    fake = FakeJudgeClient([
        JudgeCall("Q1 ANSWERABLE", 10, 1),
        JudgeCall(NOT_ANSWERABLE_REPLY, 10, 1),
        JudgeCall("nonsense", 10, 1),
    ])
    c = client_of(fake)
    cases: list[tuple[object, int, set[str]]] = [
        ({"question": QUESTION}, 200, {"outcome", "docs", "files", "signal"}),
        ({"question": QUESTION}, 200, {"outcome", "text", "signal"}),
        ({"question": QUESTION}, 502, {"outcome", "text"}),
        ({"question": ""}, 400, {"outcome"}),
        ({"question": "?!"}, 400, {"outcome"}),
        ({"question": "a" * 501}, 400, {"outcome", "length", "limit"}),
        ({"question": QUESTION, "x": 1}, 400, {"outcome"}),
        ({"question": 5}, 400, {"outcome"}),
        (["question"], 400, {"outcome"}),
    ]
    for body, status, keys in cases:
        r = c.post("/ask", json=body)
        assert r.status_code == status, body
        assert set(r.json()) == keys, body
        assert r.headers["cache-control"] == "no-store"
        assert "retry-after" not in r.headers
    assert c.post("/ask", json={"question": ""}).json()["outcome"] == "empty_question"
    assert len(fake.calls) == 3


@pytest.mark.parametrize(
    ("content", "headers"),
    [
        (b"", JSON_HEADERS),
        (b"not json", JSON_HEADERS),
        (b'{"question": "a", "question": "b"', JSON_HEADERS),
        (b'{"question": "\xff"}', JSON_HEADERS),
        (b'{"question": "ok"}', {"content-type": "text/plain"}),
        (b'{"question": "ok"}', {}),
        (b"question=a&question=b", FORM_HEADERS),
        (b"question=a&other=b", FORM_HEADERS),
        (b"other=b", FORM_HEADERS),
        (b"", FORM_HEADERS),
        (b"question=caf\xc3\xa9", FORM_HEADERS),
    ],
)
def test_bad_requests_are_bad_request(content: bytes, headers: dict[str, str]) -> None:
    fake = FakeJudgeClient()
    r = client_of(fake).post("/ask", content=content, headers=headers)
    assert (r.status_code, r.json()) == (400, {"outcome": "bad_request"})
    assert fake.calls == []


def test_form_post_without_a_renderer_is_bad_request() -> None:
    fake = FakeJudgeClient()
    c = client_of(fake)
    r = c.post("/ask", content=b"question=hello", headers=FORM_HEADERS)
    assert (r.status_code, r.json()) == (400, {"outcome": "bad_request"})
    assert c.get("/").status_code == 404
    assert fake.calls == []


def test_health_never_calls_model(capfd: pytest.CaptureFixture[str]) -> None:
    from aveto_service.abuse_log import configure_logging

    configure_logging()
    fake = FakeJudgeClient()
    embedder = CountingEmbedder()
    c = client_of(fake, runtime=make_runtime(embedder=embedder))
    r = c.get("/health")
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-store"
    assert r.json() == {
        "status": "ok",
        "kill_switch": "off",
        "day": "2026-10-21",
        "judged_today": 0,
        "input_tokens_today": 0,
        "output_tokens_today": 0,
        "spend_today_usd": "0.000000",
        "daily_cap_usd": "0.322580",
    }
    assert fake.calls == [] and embedder.queries == 0
    assert capfd.readouterr().out == ""  # no abuse line for /health
    c.post("/ask", json={"question": QUESTION})
    h = c.get("/health").json()
    assert (h["judged_today"], h["input_tokens_today"], h["output_tokens_today"]) == (1, 2400, 20)
    assert h["spend_today_usd"] == "0.005000"  # 2400 * 2000 + 20 * 10000 nano-dollars


def test_health_reports_kill_switch_on() -> None:
    c = client_of(FakeJudgeClient(), settings=make_settings(kill_switch="on"))
    assert c.get("/health").json()["kill_switch"] == "on"


def test_no_set_cookie_and_security_headers() -> None:
    c = client_of(FakeJudgeClient())
    responses = [
        c.post("/ask", json={"question": QUESTION}),
        c.post("/ask", json={"question": ""}),
        c.post("/ask", content=b"x", headers={"content-type": "text/plain"}),
        c.get("/health"),
        c.get("/nothing"),
        c.get("/docs"),
        c.get("/openapi.json"),
        c.get("/redoc"),
    ]
    for r in responses:
        assert "set-cookie" not in r.headers
    for r in responses[:4]:
        assert r.headers["cache-control"] == "no-store"
        assert r.headers["x-content-type-options"] == "nosniff"
    assert [r.status_code for r in responses[4:]] == [404, 404, 404, 404]


def test_unhandled_error_is_a_fixed_json_error(capfd: pytest.CaptureFixture[str]) -> None:
    from aveto_service.abuse_log import configure_logging

    configure_logging()
    app = make_app(FakeJudgeClient())

    def explode(raw: str, ip: str) -> AskResult:
        raise RuntimeError(CANARY)

    app.state.service.ask = explode
    r = TestClient(app, client=(IP, 1)).post("/ask", json={"question": QUESTION})
    assert (r.status_code, r.json()) == (502, {"outcome": "judge_error", "text": "judge error"})
    out = capfd.readouterr().out
    assert CANARY not in out and '"ops":"unhandled"' in out


def test_placeholder_judge_when_no_key() -> None:
    c = TestClient(
        create_app(make_runtime(), PlaceholderJudgeClient(), make_settings(api_key="")),
        client=(IP, 1),
    )
    r = c.post("/ask", json={"question": QUESTION})  # no network: the autouse block is on
    assert (r.status_code, r.json()) == (502, {"outcome": "judge_error", "text": "judge error"})
    assert c.get("/health").json()["spend_today_usd"] == "0.000000"


# --- startup ------------------------------------------------------------------------------


def good_prompt(tmp_path: Path) -> Path:
    path = tmp_path / "prompt.txt"
    path.write_bytes(Path("prompts/answerability-judge-v1.txt").read_bytes())
    return path


def test_startup_fails_closed_on_prompt_hash_mismatch(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    prompt = tmp_path / "prompt.txt"
    prompt.write_bytes(Path("prompts/answerability-judge-v1.txt").read_bytes() + b"\n")
    with pytest.raises(SystemExit) as exc:
        load_runtime(Settings(prompt_path=str(prompt)))
    assert exc.value.code == 1
    out = capfd.readouterr().out.splitlines()
    assert len(out) == 1
    assert json.loads(out[0])["ops"] == "startup_failed" and json.loads(out[0])["c"] == "prompt_hash"


def test_startup_fails_closed_on_missing_prompt(tmp_path: Path, capfd: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        load_runtime(Settings(prompt_path=str(tmp_path / "missing.txt")))
    assert json.loads(capfd.readouterr().out)["c"] == "prompt_hash"


def test_startup_fails_closed_on_bad_index(tmp_path: Path, capfd: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "index.json"
    bad.write_text("{not an index", encoding="utf-8")
    with pytest.raises(SystemExit):
        load_runtime(Settings(prompt_path=str(good_prompt(tmp_path)), index_path=str(bad)))
    assert json.loads(capfd.readouterr().out)["c"] == "index"


def test_startup_fails_closed_on_missing_model(tmp_path: Path, capfd: pytest.CaptureFixture[str]) -> None:
    index_path = tmp_path / "index.json"
    write_index(make_searcher().index, index_path)
    with pytest.raises(SystemExit):
        load_runtime(
            Settings(
                prompt_path=str(good_prompt(tmp_path)),
                index_path=str(index_path),
                models_path=str(tmp_path / "no-models"),
            )
        )
    assert json.loads(capfd.readouterr().out)["c"] == "model"


# --- the HTML port is a seam, not an implementation ---------------------------------------


class RecordingHtml:
    def __init__(self) -> None:
        self.forms: list[tuple[AskResult, str]] = []
        self.pages: list[Outcome | None] = []

    def page(self, state: Outcome | None) -> Response:
        self.pages.append(state)
        return PlainTextResponse("page")

    def form_outcome(self, result: AskResult, raw: str) -> Response:
        self.forms.append((result, raw))
        return PlainTextResponse("form")

    def result_page(self, token: str) -> Response:
        return PlainTextResponse(f"result {token}")

    def static(self, name: str) -> Response:
        return PlainTextResponse(f"static {name}")


def test_form_post_goes_to_the_renderer_and_echoes_only_when_no_model_ran() -> None:
    html = RecordingHtml()
    fake = FakeJudgeClient()
    c = client_of(fake, html=html)
    assert c.post("/ask", content=b"question=hello+there", headers=FORM_HEADERS).text == "form"
    result, raw = html.forms[-1]
    assert result.outcome is Outcome.ANSWER and result.admitted and raw == "hello there"
    c.post("/ask", content=b"question=", headers=FORM_HEADERS)
    assert html.forms[-1][0].outcome is Outcome.EMPTY_QUESTION and not html.forms[-1][0].admitted
    c.post("/ask", content=b"other=1", headers=FORM_HEADERS)
    assert html.forms[-1] == (AskResult(Outcome.BAD_REQUEST), "")
    c.post("/ask", content=b"question=" + b"a" * 20000, headers=FORM_HEADERS)
    assert html.forms[-1] == (AskResult(Outcome.BODY_TOO_LARGE), "")
    # the JSON path is untouched by a renderer
    assert c.post("/ask", json={"question": QUESTION}).json()["outcome"] == "answer"
    assert len(fake.calls) == 2  # "hello there" and the JSON question


def test_page_routes_exist_only_with_a_renderer() -> None:
    html = RecordingHtml()
    c = client_of(FakeJudgeClient(), html=html)
    assert c.get("/").text == "page" and html.pages == [None]
    assert c.get("/result/abc").text == "result abc"
    assert c.get("/static/style.css").text == "static style.css"
    off = client_of(FakeJudgeClient(), html=html, settings=make_settings(kill_switch="on"))
    off.get("/")
    assert html.pages[-1] is Outcome.SERVICE_OFF
    r = off.post("/ask", content=b"question=hi", headers=FORM_HEADERS)
    assert html.forms[-1][0].outcome is Outcome.SERVICE_OFF and r.text == "form"
    # these routes cannot reach the model
    plain = client_of(FakeJudgeClient())
    assert [plain.get(p).status_code for p in ("/", "/result/x", "/static/style.css")] == [404] * 3


def test_404_and_405_carry_no_store_and_nosniff() -> None:
    c = client_of(FakeJudgeClient())
    missing = c.get("/nope")
    wrong = c.get("/ask")
    assert (missing.status_code, wrong.status_code) == (404, 405)
    assert missing.json() == {"detail": "Not Found"}
    assert wrong.json() == {"detail": "Method Not Allowed"} and wrong.headers["allow"] == "POST"
    for r in (missing, wrong):
        assert r.headers["cache-control"] == "no-store"
        assert r.headers["x-content-type-options"] == "nosniff"


def test_form_post_catch_all_returns_the_error_page_with_a_renderer() -> None:
    html = RecordingHtml()
    app = make_app(FakeJudgeClient(), html=html)

    def explode(raw: str, ip: str) -> AskResult:
        raise RuntimeError("boom")

    app.state.service.ask = explode
    c = TestClient(app, client=(IP, 1))
    r = c.post("/ask", content=b"question=hello", headers=FORM_HEADERS)
    assert r.text == "form" and html.forms[-1] == (AskResult(Outcome.JUDGE_ERROR), "")
    j = c.post("/ask", json={"question": QUESTION})  # JSON stays JSON
    assert (j.status_code, j.json()["outcome"]) == (502, "judge_error")


def test_health_answers_while_the_thread_pool_is_saturated() -> None:
    import threading
    import time

    release = threading.Event()
    app = make_app(FakeJudgeClient())

    def slow(raw: str, ip: str) -> AskResult:
        release.wait(20)
        return AskResult(Outcome.NO_CONFIDENT_MATCH)

    app.state.service.ask = slow
    done: list[float] = []
    with TestClient(app, client=(IP, 1)) as c:  # one event loop, one thread pool
        posters = [
            threading.Thread(target=lambda: c.post("/ask", json={"question": QUESTION}))
            for _ in range(60)  # more than the pool's 40 threads
        ]
        try:
            for t in posters:
                t.start()
            time.sleep(1.0)

            def probe() -> None:
                start = time.monotonic()
                assert c.get("/health").status_code == 200
                done.append(time.monotonic() - start)

            prober = threading.Thread(target=probe)
            prober.start()
            prober.join(3)
            assert done and done[0] < 1.0
        finally:
            release.set()
            for t in posters:
                t.join(20)


def test_oversize_reply_shows_no_model_text_over_http() -> None:
    reply = "Q1 ANSWERABLE " + CANARY + "y" * 200_000
    c = client_of(FakeJudgeClient(default=JudgeCall(reply, 10, 1)))
    r = c.post("/ask", json={"question": QUESTION})
    assert (r.status_code, r.json()) == (502, {"outcome": "judge_error", "text": "judge error"})
    assert CANARY not in r.text


@pytest.mark.parametrize("path", ["/ask/", "/static/style.css/", "/result/abc/"])
def test_trailing_slash_is_404_not_a_redirect(path: str) -> None:
    c = client_of(FakeJudgeClient(), html=RecordingHtml())
    for method in (c.get, c.post):
        r = method(path, headers={"host": "evil.example"}, follow_redirects=False)
        assert r.status_code == 404 and "location" not in r.headers


def test_fastapi_telemetry_auto_configure_is_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FASTAPI_OTEL_AUTO_CONFIGURE", "true")
    assert make_app(FakeJudgeClient())._telemetry["auto_configure"] is False


CROSS_SITE = [
    {"sec-fetch-site": "cross-site"},
    {"origin": "https://evil.example"},
    {"origin": "http://testserver.evil.example"},
    {"origin": "null"},
    {"origin": "https://evil.example", "sec-fetch-site": "same-origin"},
]
SAME_ORIGIN = [
    {},
    {"sec-fetch-site": "same-origin"},
    {"sec-fetch-site": "none"},
    {"origin": "http://testserver"},
    {"origin": "HTTP://TestServer", "sec-fetch-site": "same-origin"},
]


@pytest.mark.parametrize("extra", CROSS_SITE)
@pytest.mark.parametrize("headers", [JSON_HEADERS, FORM_HEADERS])
def test_cross_site_post_is_refused_before_retrieval_and_model(
    extra: dict[str, str], headers: dict[str, str], capfd: pytest.CaptureFixture[str]
) -> None:
    from aveto_service.abuse_log import configure_logging

    configure_logging()
    embedder = CountingEmbedder()
    fake = FakeJudgeClient()
    html = RecordingHtml()
    app = make_app(fake, runtime=make_runtime(embedder=embedder), html=html)
    c = TestClient(app, client=(IP, 5000))
    body = b'{"question": "' + QUESTION.encode() + b'"}' if headers is JSON_HEADERS else b"question=hello"
    capfd.readouterr()
    r = c.post("/ask", content=body, headers={**headers, **extra})
    if headers is JSON_HEADERS:
        assert (r.status_code, r.json()) == (400, {"outcome": "bad_request"})
    else:
        assert r.text == "form" and html.forms[-1] == (AskResult(Outcome.BAD_REQUEST), "")
    assert fake.calls == [] and embedder.queries == 0
    lines = [ln for ln in capfd.readouterr().out.splitlines() if ln]
    assert len(lines) == 1 and "bad_request" in lines[0]


@pytest.mark.parametrize("extra", SAME_ORIGIN)
def test_same_origin_post_still_works(extra: dict[str, str]) -> None:
    fake = FakeJudgeClient()
    c = client_of(fake)
    r = c.post("/ask", json={"question": QUESTION}, headers=extra)
    assert r.status_code == 200 and r.json()["outcome"] == "answer"
    assert len(fake.calls) == 1
