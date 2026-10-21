from __future__ import annotations

import json
import logging
import re
import sys
import threading
from datetime import UTC, datetime, timedelta, timezone
from urllib.parse import quote, urlencode

import pytest
from fastapi.testclient import TestClient
from service_fakes import (
    CANARY,
    NOT_ANSWERABLE_REPLY,
    FakeJudgeClient,
    logging_state,  # noqa: F401
    make_app,
    make_settings,
)

from aveto_service import abuse_log
from aveto_service.abuse_log import Outcome, abuse_line, configure_logging, ops_line
from aveto_service.judge_port import JudgeCall, JudgeTransportError
from aveto_support import judge

pytestmark = pytest.mark.usefixtures("logging_state")

ABUSE_RE = re.compile(
    r'\{"t":"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ","ip":"[0-9a-f]{16}","o":"[a-z_]+"\}'
)
OPS_RE = re.compile(
    r'\{"t":"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ","ops":"(startup_ok|unhandled)"\}'
    r'|\{"t":"[^"]+","ops":"startup_failed","c":"(prompt_hash|index|model)"\}'
)
QUESTION = f"how do I upgrade the installer {CANARY} & more/stuff é"
IP = "203.0.113.7"


def forms(text: str) -> set[str]:
    """The canary's visible forms: raw, JSON-escaped, URL-escaped, and its first 12 chars."""
    return {text, json.dumps(text), json.dumps(text, ensure_ascii=False), quote(text),
            urlencode({"question": text}), CANARY, CANARY[:12]}


def test_question_never_logged(
    capfd: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    logging.getLogger("anthropic").setLevel(logging.DEBUG)
    logging.getLogger("httpx2").setLevel(logging.DEBUG)
    configure_logging()
    caplog.set_level(logging.DEBUG)
    requests = 0

    def run(app_fake: FakeJudgeClient, *, settings: object = None, expect: int | None = None,
            **kw: object) -> TestClient:
        return TestClient(
            make_app(app_fake, settings=settings or make_settings(), **kw),  # type: ignore[arg-type]
            client=(IP, 5000), raise_server_exceptions=False,
        )

    def ask(client: TestClient, question: str = QUESTION) -> None:
        nonlocal requests
        requests += 1
        client.post("/ask", json={"question": question})

    # every model-reaching outcome, a judge that raises with the question in its message
    client = run(FakeJudgeClient([
        JudgeCall("Q1 ANSWERABLE", 10, 1),
        JudgeCall(NOT_ANSWERABLE_REPLY, 10, 1),
        JudgeCall(f"malformed {QUESTION}", 10, 1),
        RuntimeError(QUESTION),
        JudgeTransportError("timeout"),
    ]))
    for _ in range(5):
        ask(client)
    # refusals before the model
    ask(client, "")
    ask(client, QUESTION * 20)
    ask(client, QUESTION + "\x07")
    ask(client, "!!! ???")
    requests += 1
    client.post("/ask", content=json.dumps({"question": QUESTION, QUESTION: 1}),
                headers={"content-type": "application/json"})
    requests += 1
    client.post("/ask", content=QUESTION.encode() * 2000,
                headers={"content-type": "application/json"})
    requests += 1
    client.post("/ask", content=urlencode({"question": QUESTION}),
                headers={"content-type": "application/x-www-form-urlencoded"})
    requests += 1
    client.post("/ask", content=QUESTION, headers={"content-type": "text/plain"})
    client.get("/" + quote(QUESTION))  # a 404 for a path that holds the canary
    client.get("/health")
    # rate limit (10 an hour), after the admitted ones above
    for _ in range(12):
        ask(client)
    # a retrieval error that carries the question
    def boom(searcher: object, raw: str) -> object:
        raise ValueError(raw)

    with monkeypatch.context() as patch:  # not .undo(): that would lift the network block too
        patch.setattr(judge, "retrieve_for_judge", boom)
        ask(run(FakeJudgeClient()))
    # spend pause, kill switch
    paused = run(FakeJudgeClient())
    paused.app.state.service._spend.cap = 1  # type: ignore[attr-defined]
    ask(paused)
    ask(run(FakeJudgeClient(), settings=make_settings(kill_switch="on")))
    # an unexpected exception inside the service, the catch-all
    broken = run(FakeJudgeClient())

    def explode(raw: str, ip: str) -> object:
        raise RuntimeError(raw)

    broken.app.state.service.ask = explode  # type: ignore[attr-defined]
    ask(broken)
    # library loggers, forced to DEBUG before, stay silent
    for name in ("anthropic", "httpx2", "httpcore", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).error(QUESTION)
        logging.getLogger(name).debug(QUESTION)
    logging.getLogger("starlette").error(QUESTION)

    out = capfd.readouterr()
    everything = out.out + out.err + caplog.text + "".join(r.getMessage() for r in caplog.records)
    for needle in forms(QUESTION):
        assert needle not in everything, needle
    lines = [ln for ln in out.out.splitlines() if ln.strip()]
    assert all(ABUSE_RE.fullmatch(ln) or OPS_RE.fullmatch(ln) for ln in lines), lines
    assert out.err == ""
    abuse = [ln for ln in lines if ABUSE_RE.fullmatch(ln)]
    outcomes = {json.loads(ln)["o"] for ln in abuse}
    assert {"answer", "no_confident_match", "judge_error", "empty_question", "too_long",
            "unusable_question", "body_too_large", "bad_request", "rate_limited", "paused",
            "service_off"} <= outcomes
    assert len(abuse) == requests - 1  # the catch-all request wrote an ops line instead
    assert sum('"ops":"unhandled"' in ln for ln in lines) == 1
    # no record from a library reached the root logger (asyncio's own "Using selector" debug
    # line comes from TestClient's event loop at the DEBUG level this test forces)
    names = {r.name for r in caplog.records} - {"asyncio"}
    assert names <= {"aveto_service.abuse", "aveto_service.ops"}


def test_abuse_line_shape_exact() -> None:
    now = datetime(2026, 10, 21, 7, 0, 0, 999999, tzinfo=UTC)
    line = abuse_line("0123456789abcdef", Outcome.ANSWER, now)
    assert line == '{"t":"2026-10-21T07:00:00Z","ip":"0123456789abcdef","o":"answer"}'
    assert list(json.loads(line)) == ["t", "ip", "o"]
    local = datetime(2026, 10, 21, 9, 0, 0, tzinfo=timezone(timedelta(hours=2)))
    assert abuse_line("0123456789abcdef", Outcome.PAUSED, local).startswith('{"t":"2026-10-21T07:00:00Z"')
    for outcome in Outcome:
        assert ABUSE_RE.fullmatch(abuse_line("0123456789abcdef", outcome, now))
    for bad in ("", "0123456789ABCDEF", "0123456789abcde", '0123456789abcd"}', "0123456789abcdef0"):
        with pytest.raises(ValueError):
            abuse_line(bad, Outcome.ANSWER, now)
    with pytest.raises(TypeError):
        abuse_line("0123456789abcdef", Outcome.ANSWER, now, "extra")  # type: ignore[call-arg]
    assert {o.value for o in Outcome} == {
        "answer", "no_confident_match", "judge_error", "empty_question", "too_long",
        "unusable_question", "body_too_large", "bad_request", "rate_limited", "paused",
        "service_off",
    }


def test_ops_lines_fixed_codes_only() -> None:
    now = datetime(2026, 10, 21, 7, 0, 0, tzinfo=UTC)
    assert ops_line("startup_ok", now) == '{"t":"2026-10-21T07:00:00Z","ops":"startup_ok"}'
    assert ops_line("startup_failed", now, "index").endswith('"ops":"startup_failed","c":"index"}')
    for code, category in (
        ("whatever", None),
        ("startup_failed", None),
        ("startup_failed", "free text"),
        ("startup_ok", "index"),
    ):
        with pytest.raises(ValueError):
            ops_line(code, now, category)


def test_library_loggers_silenced(capfd: pytest.CaptureFixture[str]) -> None:
    for name in abuse_log._SILENCED:
        logging.getLogger(name).setLevel(logging.DEBUG)
    configure_logging()
    for name in abuse_log._SILENCED:
        lg = logging.getLogger(name)
        assert lg.disabled and not lg.propagate and not lg.handlers
        assert lg.level == logging.CRITICAL
        lg.critical(CANARY)
    logging.getLogger("some.other.module").error(CANARY)
    logging.getLogger().error(CANARY)
    sys.excepthook(ValueError, ValueError(CANARY), None)
    threading.excepthook(threading.ExceptHookArgs((ValueError, ValueError(CANARY), None, None)))
    configure_logging()  # idempotent: still one handler of ours
    abuse_log.emit_ops("startup_ok")
    out = capfd.readouterr()
    assert CANARY not in out.out + out.err
    lines = out.out.splitlines()
    assert [bool(OPS_RE.fullmatch(ln)) for ln in lines] == [True, True, True]
    assert lines[0].endswith('"ops":"unhandled"}') and lines[1].endswith('"ops":"unhandled"}')
    assert lines[2].endswith('"ops":"startup_ok"}')
