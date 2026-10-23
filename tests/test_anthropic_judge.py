"""AnthropicJudgeClient against a fake Messages client: no network, no key."""

from __future__ import annotations

import ast
import inspect
import json
import logging
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2 as httpx
import pytest

from aveto_service import anthropic_judge
from aveto_service.anthropic_judge import (
    AnthropicJudgeClient,
    build_request,
    extract_reply,
)
from aveto_service.judge_port import JudgeTransportError
from aveto_support import judge

ROOT = Path(__file__).resolve().parent.parent
PROMPT = (ROOT / "prompts" / "answerability-judge-v1.txt").read_text(encoding="utf-8")
PAYLOAD = "judge-input payload: question and passages\n"
KEY = "sk-ant-test-key-zzz999"
SECRET = "secretpayloadcanary4471"


def message(
    blocks: list[Any] | None = None,
    stop: str | None = "end_turn",
    i: int = 11,
    o: int = 7,
) -> Any:
    if blocks is None:
        blocks = [SimpleNamespace(type="text", text="Q1 ANSWERABLE reason")]
    return SimpleNamespace(
        stop_reason=stop,
        content=blocks,
        usage=SimpleNamespace(input_tokens=i, output_tokens=o),
    )


class FakeMessages:
    def __init__(self, *outcomes: Any) -> None:
        self.outcomes = list(outcomes)
        self.requests: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.requests.append(kwargs)
        out = self.outcomes.pop(0)
        if isinstance(out, BaseException):
            raise out
        return out


def make(*outcomes: Any) -> tuple[AnthropicJudgeClient, FakeMessages, list[float]]:
    fake = FakeMessages(*outcomes)
    sleeps: list[float] = []
    client = AnthropicJudgeClient(
        KEY, client=SimpleNamespace(messages=fake), sleep=sleeps.append
    )
    return client, fake, sleeps


def _req() -> httpx.Request:
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages")


def _status(cls: type, code: int) -> Any:
    resp = httpx.Response(code, request=_req(), text=SECRET)
    return cls(SECRET, response=resp, body={"x": SECRET})


def test_request_has_no_tools() -> None:
    client, fake, _ = make(message())
    client.judge(PROMPT, PAYLOAD)
    sent = fake.requests[0]
    assert "tools" not in sent and "tool_choice" not in sent


def test_request_body_only_c41_data() -> None:
    client, fake, _ = make(message())
    client.judge(PROMPT, PAYLOAD)
    sent = fake.requests[0]
    assert set(sent) == {"model", "max_tokens", "system", "messages", "output_config"}
    assert sent["system"] == PROMPT
    assert sent["messages"] == [{"role": "user", "content": PAYLOAD}]
    assert "metadata" not in sent
    assert KEY not in json.dumps(sent)


def test_request_model_and_effort_pinned() -> None:
    sent = build_request(PROMPT, PAYLOAD)
    assert sent["model"] == "claude-sonnet-5-5"
    assert sent["output_config"] == {"effort": "high"}
    assert sent["max_tokens"] == 1024


def test_sdk_accepts_the_request_shape() -> None:
    sdk = anthropic.Anthropic(api_key=KEY)
    params = set(inspect.signature(sdk.messages.create).parameters)
    assert {"output_config", "metadata", "tools", "system"} <= params


def test_success_returns_reply_usage_attempts_1() -> None:
    client, _, sleeps = make(message())
    call = client.judge(PROMPT, PAYLOAD)
    assert (call.reply, call.input_tokens, call.output_tokens, call.attempts) == (
        "Q1 ANSWERABLE reason",
        11,
        7,
        1,
    )
    assert sleeps == []


def test_extract_reply_text_blocks_only() -> None:
    blocks = [
        SimpleNamespace(type="thinking", thinking="hidden"),
        SimpleNamespace(type="text", text="Q1 "),
        SimpleNamespace(type="redacted_thinking", data="x"),
        SimpleNamespace(type="text", text="ANSWERABLE"),
    ]
    assert extract_reply(message(blocks)) == "Q1 ANSWERABLE"
    assert extract_reply(message([])) == ""
    for kind in ("tool_use", "server_tool_use"):
        with pytest.raises(JudgeTransportError) as info:
            extract_reply(message([SimpleNamespace(type=kind)]))
        assert info.value.category == "tool_use"


@pytest.mark.parametrize(
    "stop", ["max_tokens", "refusal", "tool_use", "pause_turn", "stop_sequence", None]
)
def test_stop_reason_not_end_turn_is_judge_error(stop: str | None) -> None:
    client, fake, _ = make(message(stop=stop))
    with pytest.raises(JudgeTransportError) as info:
        client.judge(PROMPT, PAYLOAD)
    assert info.value.category == "stop_reason" and info.value.attempts == 1
    assert len(fake.requests) == 1


def test_sdk_errors_map_to_fixed_categories() -> None:
    cases = [
        (anthropic.APITimeoutError(request=_req()), "timeout"),
        (_status(anthropic.BadRequestError, 400), "status_4xx"),
        (_status(anthropic.AuthenticationError, 401), "status_4xx"),
        (_status(anthropic.PermissionDeniedError, 403), "status_4xx"),
        (_status(anthropic.NotFoundError, 404), "status_4xx"),
        (ValueError(SECRET), "other"),
        (RuntimeError(KEY), "other"),
    ]
    for exc, category in cases:
        client, fake, sleeps = make(exc)
        with pytest.raises(JudgeTransportError) as info:
            client.judge(PROMPT, PAYLOAD)
        err = info.value
        assert err.category == category and err.attempts == 1
        assert len(fake.requests) == 1 and sleeps == []
        text = repr(err) + str(err) + repr(err.args)
        assert SECRET not in text and KEY not in text
        assert err.__cause__ is None and err.__suppress_context__


def test_retry_once_only_on_retryable() -> None:
    retryable: list[tuple[Callable[[], Any], str]] = [
        (lambda: _status(anthropic.RateLimitError, 429), "status_4xx"),
        (lambda: _status(anthropic.InternalServerError, 500), "status_5xx"),
        (lambda: _status(anthropic.InternalServerError, 529), "status_5xx"),
        (lambda: anthropic.APIConnectionError(request=_req()), "connection"),
    ]
    for make_exc, category in retryable:
        client, fake, sleeps = make(make_exc(), message())
        call = client.judge(PROMPT, PAYLOAD)
        assert call.attempts == 2 and len(fake.requests) == 2 and sleeps == [1.0]
        assert call.reply == "Q1 ANSWERABLE reason"
        client, fake, sleeps = make(make_exc(), make_exc(), message())
        with pytest.raises(JudgeTransportError) as info:
            client.judge(PROMPT, PAYLOAD)
        assert info.value.category == category and info.value.attempts == 2
        assert len(fake.requests) == 2


def test_no_retry_on_timeout() -> None:
    client, fake, sleeps = make(anthropic.APITimeoutError(request=_req()), message())
    with pytest.raises(JudgeTransportError) as info:
        client.judge(PROMPT, PAYLOAD)
    assert info.value.category == "timeout" and info.value.attempts == 1
    assert len(fake.requests) == 1 and sleeps == []


def test_bad_stop_reason_on_retry_reports_attempts_2() -> None:
    client, _, _ = make(
        _status(anthropic.InternalServerError, 503), message(stop="max_tokens")
    )
    with pytest.raises(JudgeTransportError) as info:
        client.judge(PROMPT, PAYLOAD)
    assert info.value.category == "stop_reason" and info.value.attempts == 2


def test_prompt_hash_mismatch_fails_closed() -> None:
    client, fake, _ = make(message())
    for bad in (PROMPT + " ", PROMPT.rstrip("\n"), "", "other prompt"):
        with pytest.raises(JudgeTransportError) as info:
            client.judge(bad, PAYLOAD)
        assert info.value.category == "prompt_hash"
    assert fake.requests == []
    assert anthropic_judge.prompt_matches_pin(PROMPT)


def test_pinned_hash_is_the_core_pin() -> None:
    assert (
        judge.PROMPT_SHA256
        == "24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427"
    )


def test_empty_key_refused_without_echo() -> None:
    with pytest.raises(ValueError) as info:
        AnthropicJudgeClient("")
    assert "sk-" not in str(info.value)


def test_real_client_blocked_offline(
    caplog: pytest.LogCaptureFixture, capfd: pytest.CaptureFixture[str]
) -> None:
    caplog.set_level(logging.DEBUG)
    sleeps: list[float] = []
    client = AnthropicJudgeClient(KEY, sleep=sleeps.append)
    with pytest.raises(JudgeTransportError) as info:
        client.judge(PROMPT, PAYLOAD + SECRET)
    assert info.value.category in {"connection", "other"}
    out = capfd.readouterr()
    blob = caplog.text + out.out + out.err + repr(info.value)
    assert KEY not in blob and SECRET not in blob


def test_real_client_config() -> None:
    client = AnthropicJudgeClient(KEY)
    sdk = client._client
    assert sdk.max_retries == 0 and sdk.timeout == 20.0


def test_no_logging_calls_and_no_key_in_source() -> None:
    src = (ROOT / "aveto_service" / "anthropic_judge.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not names & {"print", "getenv"}
    # The only environment read is the fail-closed check of the SDK's header setting.
    env_reads = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and n.value.startswith("ANTHROPIC_")
    }
    assert env_reads == {"ANTHROPIC_CUSTOM_HEADERS"}
    assert "sk-ant" not in src


def test_anthropic_judge_import_allow_list() -> None:
    tree = ast.parse(
        (ROOT / "aveto_service" / "anthropic_judge.py").read_text(encoding="utf-8")
    )
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            roots.add(node.module.split(".")[0])
    assert roots <= {
        "__future__",
        "hashlib",
        "logging",
        "os",
        "time",
        "collections",
        "typing",
        "anthropic",
        "aveto_service",
        "aveto_support",
    }
    mods = {
        n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module
    }
    assert {m for m in mods if m.startswith("aveto")} <= {
        "aveto_service.judge_port",
        "aveto_support",
    }


def test_adapter_mutes_sdk_loggers() -> None:
    logging.getLogger("anthropic").setLevel(logging.DEBUG)
    AnthropicJudgeClient(KEY, client=SimpleNamespace(messages=FakeMessages()))
    assert not logging.getLogger("anthropic").isEnabledFor(logging.CRITICAL)


def _mock_sdk(monkeypatch: pytest.MonkeyPatch) -> list[httpx.Request]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        body = {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "model": anthropic_judge.MODEL,
            "content": [{"type": "text", "text": "Q1 ANSWERABLE reason"}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 3, "output_tokens": 2},
        }
        return httpx.Response(200, json=body)

    real = anthropic.Anthropic

    def factory(**kwargs: Any) -> Any:
        http = httpx.Client(transport=httpx.MockTransport(handler))
        return real(http_client=http, **kwargs)

    monkeypatch.setattr(anthropic, "Anthropic", factory)
    return seen


# Observed from SDK 1.7.0 (lower-cased); the x-stainless-* values describe the runtime only.
EXPECTED_HEADER_NAMES = {
    "host",
    "accept",
    "accept-encoding",
    "connection",
    "content-length",
    "content-type",
    "user-agent",
    "anthropic-version",
    "x-api-key",
    "x-stainless-arch",
    "x-stainless-async",
    "x-stainless-lang",
    "x-stainless-os",
    "x-stainless-package-version",
    "x-stainless-read-timeout",
    "x-stainless-retry-count",
    "x-stainless-runtime",
    "x-stainless-runtime-version",
    "x-stainless-timeout",
}


def test_base_url_env_cannot_redirect_and_header_set_is_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://evil.example.test")
    monkeypatch.delenv("ANTHROPIC_CUSTOM_HEADERS", raising=False)
    seen = _mock_sdk(monkeypatch)
    call = AnthropicJudgeClient(KEY).judge(PROMPT, PAYLOAD)
    assert call.reply.startswith("Q1")
    assert len(seen) == 1
    assert seen[0].url.host == "api.anthropic.com"
    assert seen[0].url.scheme == "https"
    assert {k.lower() for k in seen[0].headers} == EXPECTED_HEADER_NAMES


@pytest.mark.parametrize("value", ["X-Evil: 1", "", "no colon here"])
def test_custom_headers_env_fails_closed(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("ANTHROPIC_CUSTOM_HEADERS", value)
    seen = _mock_sdk(monkeypatch)
    with pytest.raises(ValueError) as info:
        AnthropicJudgeClient(KEY)
    assert value not in str(info.value) or value == ""
    assert KEY not in str(info.value) and "CUSTOM_HEADERS" not in str(info.value)
    assert seen == []


def test_injected_client_skips_env_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_CUSTOM_HEADERS", "X-Evil: 1")
    AnthropicJudgeClient(KEY, client=SimpleNamespace(messages=FakeMessages()))


def _timeout() -> Any:
    return anthropic.APITimeoutError(request=_req())


def _conn() -> Any:
    return anthropic.APIConnectionError(request=_req())


@pytest.mark.parametrize(
    ("script", "category", "attempts", "billable"),
    [
        (lambda: [_status(anthropic.InternalServerError, 503), _status(anthropic.BadRequestError, 400)], "status_4xx", 2, 1),
        (lambda: [_status(anthropic.RateLimitError, 429), _status(anthropic.BadRequestError, 400)], "status_4xx", 2, 0),
        (lambda: [_conn(), _conn()], "connection", 2, 0),
        (lambda: [_status(anthropic.InternalServerError, 503), _status(anthropic.InternalServerError, 503)], "status_5xx", 2, 2),
        (lambda: [_status(anthropic.InternalServerError, 503), message(stop="max_tokens")], "stop_reason", 2, 2),
        (lambda: [_timeout()], "timeout", 1, 1),
        (lambda: [_status(anthropic.BadRequestError, 400)], "status_4xx", 1, 0),
        (lambda: [message(stop="max_tokens")], "stop_reason", 1, 1),
    ],
)
def test_billable_failures_counted_per_attempt(
    script: Callable[[], list[Any]], category: str, attempts: int, billable: int
) -> None:
    client, _, _ = make(*script())
    with pytest.raises(JudgeTransportError) as info:
        client.judge(PROMPT, PAYLOAD)
    err = info.value
    assert (err.category, err.attempts, err.billable_failures) == (category, attempts, billable)
    assert type(err.billable_failures) is int
    assert err.args == (category,)
    assert SECRET not in repr(err) + str(err)


@pytest.mark.parametrize(
    ("script", "attempts", "billable"),
    [
        (lambda: [message()], 1, 0),
        (lambda: [_status(anthropic.RateLimitError, 429), message()], 2, 0),
        (lambda: [_status(anthropic.InternalServerError, 503), message()], 2, 1),
        (lambda: [_conn(), message()], 2, 0),
    ],
)
def test_billable_failures_on_success(
    script: Callable[[], list[Any]], attempts: int, billable: int
) -> None:
    client, _, _ = make(*script())
    call = client.judge(PROMPT, PAYLOAD)
    assert (call.attempts, call.billable_failures) == (attempts, billable)


def test_prompt_hash_mismatch_bills_nothing() -> None:
    client, _, _ = make(message())
    with pytest.raises(JudgeTransportError) as info:
        client.judge("other prompt", PAYLOAD)
    assert info.value.billable_failures == 0
