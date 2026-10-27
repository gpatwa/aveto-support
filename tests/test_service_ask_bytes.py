"""`POST /ask` JSON and every response header set stay byte-identical to commit 32e54a6.

The golden file `tests/golden/ask-json-32e54a6.json` was written by this module run as a script
(`uv run python tests/test_service_ask_bytes.py --write-golden`) on a tree whose
`aveto_service`, `aveto_support` and `prompts` were identical to 32e54a6. These are guards: they
pass on 32e54a6 and on the final tree. Only `test_new_routes_carry_existing_header_sets` is new
behaviour and fails on 32e54a6.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

REPO_ROOT = Path(__file__).resolve().parent.parent
if __name__ == "__main__":  # run as a script: the repo root and tests/ are not on the path yet
    sys.path.insert(0, str(REPO_ROOT))

import httpx2 as httpx
from fastapi.testclient import TestClient
from service_fakes import (
    ANSWERABLE_REPLY,
    NOT_ANSWERABLE_REPLY,
    FakeJudgeClient,
    make_app,
    make_runtime,
    make_settings,
)

from aveto_service import app as app_module
from aveto_service import pages
from aveto_service.judge_port import JudgeCall
from aveto_service.pages import HtmlPages

GOLDEN = Path(__file__).resolve().parent / "golden" / "ask-json-32e54a6.json"
BASE = "32e54a6"
QUESTION = "how do I install the tool"
FORM = {"Content-Type": "application/x-www-form-urlencoded"}
JSON_HEADERS = {"Content-Type": "application/json"}
PEER = ("203.0.113.7", 5000)

# (eval file, question id): all from spent sets (see 05-tech-spec.md section 8)
EVAL_QUESTIONS = [
    ("retrieval-heldout-5", i) for i in ("g01", "g03", "g04", "gu15", "gu18")
] + [("public-gate-1", i) for i in ("p01", "p05", "p06", "p11", "p12", "p17", "p20")]

EXPECTED_SECURITY = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}
SECURITY_NAMES = {k.lower() for k in EXPECTED_SECURITY}


def _eval_question(set_name: str, qid: str) -> str:
    data = tomllib.loads((REPO_ROOT / "evals" / f"{set_name}.toml").read_text("utf-8"))
    for q in data["question"]:
        if q["id"] == qid:
            text = q["question"]
            assert isinstance(text, str)
            return text
    raise AssertionError(f"{set_name} has no question {qid}")


def _client(
    reply: str = ANSWERABLE_REPLY, *, settings: Any = None
) -> tuple[TestClient, FakeJudgeClient]:
    fake = FakeJudgeClient(default=JudgeCall(reply, 2400, 20))
    app = make_app(fake, runtime=make_runtime(), settings=settings)
    return TestClient(app, client=PEER), fake


def _record(case_id: str, r: httpx.Response) -> dict[str, Any]:
    return {
        "id": case_id,
        "status": r.status_code,
        "headers": [[k.decode("latin-1"), v.decode("latin-1")] for k, v in r.headers.raw],
        "body": r.content.decode("utf-8"),
    }


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for set_name, qid in EVAL_QUESTIONS:
        question = _eval_question(set_name, qid)
        for label, reply in (("answer", ANSWERABLE_REPLY), ("refusal", NOT_ANSWERABLE_REPLY)):
            c, _ = _client(reply)
            cases.append(_record(f"{qid}-{label}", c.post("/ask", json={"question": question})))
    shapes: list[tuple[str, dict[str, Any]]] = [
        ("empty", {"json": {"question": ""}}),
        ("blank", {"json": {"question": "   "}}),
        ("over-500", {"json": {"question": "a" * 501}}),
        ("unusable", {"json": {"question": "?!"}}),
        ("extra-field", {"json": {"question": "x", "x": 1}}),
        ("not-a-string", {"json": {"question": 5}}),
        ("not-an-object", {"json": ["question"]}),
        ("huge-body", {"content": b"x" * 20000, "headers": JSON_HEADERS}),
    ]
    for case_id, kwargs in shapes:
        c, _ = _client()
        cases.append(_record(case_id, c.post("/ask", **kwargs)))
    c, _ = _client("garbage")
    cases.append(_record("judge-error-garbage", c.post("/ask", json={"question": QUESTION})))
    c, _ = _client("Q1 ANSWERABLE " + "x" * 5000)
    cases.append(_record("judge-error-long-reply", c.post("/ask", json={"question": QUESTION})))
    c, _ = _client()
    last = None
    for _ in range(11):
        last = c.post("/ask", json={"question": QUESTION})
    assert last is not None
    cases.append(_record("rate-limited-11th", last))
    c, _ = _client()
    c.app.state.service._spend.cap = 0  # type: ignore[attr-defined]
    cases.append(_record("paused", c.post("/ask", json={"question": QUESTION})))
    c, _ = _client(settings=make_settings(kill_switch="on"))
    cases.append(_record("service-off", c.post("/ask", json={"question": QUESTION})))
    c, _ = _client()
    cases.append(
        _record(
            "cross-site-origin",
            c.post("/ask", json={"question": QUESTION}, headers={"Origin": "https://evil.example"}),
        )
    )
    c, _ = _client()
    assert c.post("/ask", json={"question": QUESTION}).json()["outcome"] == "answer"
    cases.append(_record("health-after-one-answer", c.get("/health")))
    return cases


def write_golden() -> None:
    cases = build_cases()
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_text(
        json.dumps({"base": BASE, "cases": cases}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {GOLDEN} with {len(cases)} cases")


def test_ask_json_bytes_equal_main() -> None:
    golden = json.loads(GOLDEN.read_text("utf-8"))
    assert golden["base"] == BASE
    now = build_cases()
    assert [c["id"] for c in now] == [c["id"] for c in golden["cases"]]  # none silently dropped
    for got, want in zip(now, golden["cases"], strict=True):
        assert got["status"] == want["status"], got["id"]
        assert got["body"].encode("utf-8") == want["body"].encode("utf-8"), got["id"]
        assert got["headers"] == want["headers"], got["id"]
    # the labelled replies really produced both outcomes for every question
    judged = [json.loads(c["body"])["outcome"] for c in now[: 2 * len(EVAL_QUESTIONS)]]
    assert judged == ["answer", "no_confident_match"] * len(EVAL_QUESTIONS)
    assert len(now) >= 36


# --- headers -----------------------------------------------------------------------------------


def _names(r: httpx.Response) -> set[str]:
    return {k.decode("latin-1").lower() for k, _ in r.headers.raw}


def _html_client(**kw: Any) -> tuple[TestClient, FakeJudgeClient]:
    fake = FakeJudgeClient()
    runtime = make_runtime()
    app = make_app(fake, runtime=runtime, html=HtmlPages(runtime), **kw)
    return TestClient(app, client=PEER, follow_redirects=False), fake


def _check_security(label: str, r: httpx.Response, *, typed: bool = True) -> None:
    for k, v in EXPECTED_SECURITY.items():
        assert r.headers[k] == v, (label, k)
    expected = SECURITY_NAMES | {"content-length"}
    if typed:
        expected |= {"content-type"}
    if r.status_code == 303:
        expected |= {"location"}
        expected -= {"content-type"}
    assert _names(r) == expected, (label, sorted(_names(r)))
    assert "set-cookie" not in _names(r)


def test_security_and_json_header_sets_are_byte_identical() -> None:
    assert pages.SECURITY_HEADERS == EXPECTED_SECURITY
    assert app_module._JSON_HEADERS == {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
    client, _ = _html_client()
    answered = client.post("/ask", content=urlencode({"question": QUESTION}), headers=FORM)
    assert answered.status_code == 303
    _check_security("form 303", answered)
    result = client.get(answered.headers["location"].split("#")[0])
    assert result.status_code == 200
    _check_security("result page", result)
    _check_security("get /", client.get("/"))
    _check_security("unknown token", client.get("/result/nope"))
    _check_security("style.css", client.get("/static/style.css"))
    _check_security("enhance.js", client.get("/static/enhance.js"))
    missing = client.get("/static/nope.txt")
    assert missing.status_code == 404
    _check_security("static 404", missing, typed=False)
    for text, label in (("", "empty"), ("a" * 501, "too long")):
        r = client.post("/ask", content=urlencode({"question": text}), headers=FORM)
        assert r.status_code == 400
        _check_security(label, r)
    limited, _ = _html_client()
    for _ in range(10):
        assert limited.post("/ask", content=urlencode({"question": QUESTION}), headers=FORM).status_code == 303
    r = limited.post("/ask", content=urlencode({"question": QUESTION}), headers=FORM)
    assert r.status_code == 429
    _check_security("rate limited", r)
    off, _ = _html_client(settings=make_settings(kill_switch="on"))
    _check_security("get / kill switch", off.get("/"))
    resting, _ = _html_client()
    service = resting.app.state.service  # type: ignore[attr-defined]
    service._spend.cap = service._floor - 1
    _check_security("get / resting", resting.get("/"))
    # the JSON route
    j = client.post("/ask", json={"question": QUESTION})
    assert j.status_code == 200
    assert _names(j) == {"cache-control", "x-content-type-options", "content-type", "content-length"}
    h = client.get("/health")
    assert _names(h) == {"cache-control", "x-content-type-options", "content-type", "content-length"}


def test_new_routes_carry_existing_header_sets() -> None:
    client, fake = _html_client()
    card = client.get("/scorecard")
    assert card.status_code == 200
    _check_security("scorecard", card)
    warm = client.post("/warm")
    assert warm.status_code == 200
    assert _names(warm) == {"cache-control", "x-content-type-options", "content-type", "content-length"}
    assert warm.headers["cache-control"] == "no-store"
    assert warm.headers["x-content-type-options"] == "nosniff"
    click = client.post("/count/docs-click")
    assert click.status_code == 204 and click.content == b""
    assert _names(click) == {"cache-control", "x-content-type-options"}
    assert click.headers["cache-control"] == "no-store"
    assert fake.calls == []


if __name__ == "__main__":
    if sys.argv[1:] == ["--write-golden"]:
        write_golden()
    else:
        raise SystemExit("usage: test_service_ask_bytes.py --write-golden")
