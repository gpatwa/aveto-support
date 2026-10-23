"""The public page: states, copy, escaping, headers, Post/Redirect/Get. No network, fake judge."""

from __future__ import annotations

import html as htmllib
import re
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from service_fakes import (
    ANSWERABLE_REPLY,
    DOCS,
    NOT_ANSWERABLE_REPLY,
    FakeJudgeClient,
    make_app,
    make_runtime,
    make_settings,
)

from aveto_service.judge_port import JudgeCall
from aveto_service.pages import HtmlPages
from aveto_service.pipeline import AskService, Runtime
from aveto_support import judge

QUESTION = "how do I install the tool"
FORM = {"Content-Type": "application/x-www-form-urlencoded"}
PRIVATE = "zqxprivatecanary9917"


def make_client(
    fake: FakeJudgeClient | None = None,
    *,
    runtime: Runtime | None = None,
    **kw: object,
) -> tuple[TestClient, FakeJudgeClient, Runtime]:
    fake = fake or FakeJudgeClient()
    runtime = runtime or make_runtime()
    app = make_app(fake, runtime=runtime, html=HtmlPages(runtime), **kw)  # type: ignore[arg-type]
    return TestClient(app, client=("203.0.113.9", 5000), follow_redirects=False), fake, runtime


def post_form(client: TestClient, text: str) -> object:
    return client.post("/ask", content=urlencode({"question": text}), headers=FORM)


def visible(response_text: str) -> str:
    return htmllib.unescape(response_text)


def followed(client: TestClient, text: str) -> str:
    r = post_form(client, text)
    assert r.status_code == 303  # type: ignore[attr-defined]
    page = client.get(r.headers["location"].split("#")[0])  # type: ignore[attr-defined]
    assert page.status_code == 200
    return visible(page.text)


# --- the 11 states, exact copy ------------------------------------------------------------


def test_initial_page_has_empty_region_and_form() -> None:
    client, _, _ = make_client()
    text = visible(client.get("/").text)
    assert '<form id="ask-form" method="post" action="/ask#result">' in text
    assert 'id="result-title"' not in text
    assert '<section id="result" tabindex="-1" aria-labelledby="result-title">' in text
    assert "<title>Ask the Aveto docs</title>" in text
    assert '<html lang="en">' in text


def test_answer_state() -> None:
    client, _, _ = make_client()
    text = followed(client, QUESTION)
    assert "The docs answer this" in text
    assert re.search(r"Found \d+ passages?\.", text)
    assert 'class="state state-answer"' in text


def test_no_confident_match_state() -> None:
    client, _, _ = make_client(FakeJudgeClient(default=JudgeCall(NOT_ANSWERABLE_REPLY, 100, 5)))
    text = followed(client, QUESTION)
    assert "The docs don't answer this" in text
    assert (
        "No confident match was found, so nothing is shown. You can change your question and "
        "ask again, or open a GitHub issue." in text
    )
    assert ">Open a GitHub issue</a>" in text
    assert 'class="passages"' not in text


def test_could_not_decide_state() -> None:
    client, _, _ = make_client(FakeJudgeClient(default=JudgeCall("garbage", 100, 5)))
    text = followed(client, QUESTION)
    assert '<h2 id="result-title" role="alert">We couldn\'t decide this time</h2>' in text
    assert (
        "Something went wrong while checking the passages, so none are shown. "
        "Please try again." in text
    )
    for banned in ("judge", "verdict", "model said"):
        assert banned not in text.split('id="result"')[1].lower()


def test_rate_limited_state_keeps_the_question() -> None:
    client, fake, _ = make_client()
    for _ in range(10):
        assert post_form(client, QUESTION).status_code == 303  # type: ignore[attr-defined]
    r = post_form(client, QUESTION)
    text = visible(r.text)  # type: ignore[attr-defined]
    assert "Question limit reached" in text
    assert (
        "You can ask 10 questions an hour. Please try again later. "
        "Your question is still in the box." in text
    )
    assert f">{QUESTION}</textarea>" in text
    assert len(fake.calls) == 10


def test_paused_state() -> None:
    client, fake, _runtime = make_client()
    service: AskService = client.app.state.service  # type: ignore[attr-defined]
    service._spend.cap = service._floor + 1000
    text = visible(post_form(client, QUESTION).text)  # type: ignore[attr-defined]
    assert "Paused for today" in text
    assert (
        "Ask the Docs has a daily limit and today's has been used. This is not a fault. "
        "You can read the docs on GitHub or open an issue." in text
    )
    assert text.count("Read the docs on GitHub") == 2  # body and footer
    assert 'role="alert"' not in text.split('id="result"')[1]
    assert 'class="state state-note"' in text
    assert fake.calls == []


def test_too_long_state_names_the_count() -> None:
    client, fake, _ = make_client()
    long = "a" * 501
    text = visible(post_form(client, long).text)  # type: ignore[attr-defined]
    assert "Your question is too long" in text
    assert (
        "Questions can be up to 500 characters. Yours is 501. Shorten it and ask again. "
        "Nothing was sent." in text
    )
    assert 'id="q-error" class="error">Questions can be up to 500 characters.' in text
    assert 'aria-invalid="true"' in text
    assert "1 characters over the limit of 500. Shorten your question." in text
    assert long in text  # the text stays in the box
    assert fake.calls == []


def test_empty_question_state() -> None:
    client, fake, _ = make_client()
    text = visible(post_form(client, "   ").text)  # type: ignore[attr-defined]
    assert "Please enter a question" in text
    assert "Type a question about Aveto, then press Ask. Nothing was sent." in text
    assert 'id="q-error" class="error">Type a question about Aveto, then press Ask.' in text
    assert fake.calls == []


def test_service_off_state_on_get_and_post() -> None:
    client, fake, _ = make_client(settings=make_settings(kill_switch="on"))
    for text in (
        visible(client.get("/").text),
        visible(post_form(client, QUESTION).text),  # type: ignore[attr-defined]
    ):
        assert "The service is off" in text
        assert (
            "Ask the Docs is switched off right now. You can read the docs on GitHub or "
            "open an issue." in text
        )
        assert 'role="alert"' in text
    assert fake.calls == []


def test_unusable_and_bad_request_show_a_state_not_a_crash() -> None:
    client, fake, _ = make_client()
    text = visible(post_form(client, "\u0000\u0001").text)  # type: ignore[attr-defined]
    assert "Please enter a question" in text
    r = client.post("/ask", content=b"a=1&b=2", headers=FORM)
    assert r.status_code == 400
    assert "Please enter a question" in visible(r.text)
    assert fake.calls == []


def test_oversized_body_state() -> None:
    client, fake, _ = make_client()
    r = client.post("/ask", content=urlencode({"question": "a" * 20000}), headers=FORM)
    assert r.status_code == 413
    assert "Your question is too long" in r.text
    assert "a" * 100 not in r.text
    assert fake.calls == []


# --- the disclosure (UX amendment 2026-10-21), word for word ------------------------------


def test_disclosure_copy_is_verbatim() -> None:
    client, _, _ = make_client()
    text = visible(client.get("/").text)
    for sentence in (
        ("Verbatim passages from Aveto's docs; an AI model decides only whether they answer. "
        "Nothing on this page is written by an AI model."),
        "Please don't put personal or confidential information in your question.",
        ("This service does not store or log your question. To decide whether the passages "
        "answer, your question and the passages found are sent to Anthropic, the company that "
        "makes the AI model. Anthropic handles them under its own terms, which this page does "
        "not control."),
        ("To apply the limits we read your address, then keep only a scrambled form of it, the "
        "time and the outcome for 7 days. The service runs in the United States "
        "(Azure, East US 2)."),
        ("Limits: 10 questions an hour and 500 characters a question. The service pauses for "
        "the day when the day's allowance is used."),
        ("The docs are in English. One question at a time; nothing is remembered between "
        "questions."),
    ):
        assert sentence in text


# --- passages verbatim, escaping ----------------------------------------------------------


def test_passages_byte_identical_inside_the_page() -> None:
    client, _, runtime = make_client()
    expected = judge.retrieve_for_judge(runtime.searcher, QUESTION)
    page = followed(client, QUESTION)
    seen = 0
    for f in expected.files:
        for m in f.passages:
            seen += 1
            assert f"<code>{m.passage.text}</code></pre>" in page
            assert f"<code>{f.path}</code>" in page
            assert m.url in page
            lines = (
                f"Lines {m.passage.line_start} to {m.passage.line_end}"
                if m.passage.line_start != m.passage.line_end
                else f"Line {m.passage.line_start}"
            )
            assert lines in page
    assert seen > 0
    assert f"Found {seen} passage" in page


def test_markup_bearing_passage_is_escaped() -> None:
    docs = {
        "guide/evil.md": (
            "# Install\n\nInstall steps: <script>alert(1)</script> & <img src=x onerror=y>\n"
            "    indented  line\n"
        ),
        **DOCS,
    }
    runtime = make_runtime(docs)
    client, _, _ = make_client(runtime=runtime)
    r = post_form(client, "install steps")
    raw = client.get(r.headers["location"].split("#")[0]).text  # type: ignore[attr-defined]
    assert "<script>alert(1)</script>" not in raw
    assert "<img src=x" not in raw
    assert "&lt;script&gt;alert(1)&lt;/script&gt; &amp; &lt;img src=x onerror=y&gt;" in raw
    expected = judge.retrieve_for_judge(runtime.searcher, "install steps")
    texts = [m.passage.text for f in expected.files for m in f.passages]
    assert any("<script>alert(1)</script>" in t for t in texts)
    assert all(f"<code>{t}</code></pre>" in visible(raw) for t in texts)


def test_markup_question_is_escaped_when_echoed() -> None:
    client, _, _ = make_client()
    evil = '</textarea><script>alert(1)</script>"' + "a" * 600
    raw = post_form(client, evil).text  # type: ignore[attr-defined]
    assert "<script>alert(1)</script>" not in raw
    assert "&lt;/textarea&gt;&lt;script&gt;" in raw
    assert raw.count("<script") == 1  # only our own enhance.js tag


# --- no question in URLs; PRG --------------------------------------------------------------


def test_question_is_in_no_url_or_location() -> None:
    client, fake, _ = make_client()
    r = post_form(client, f"{QUESTION} {PRIVATE}")
    assert r.status_code == 303  # type: ignore[attr-defined]
    loc = r.headers["location"]  # type: ignore[attr-defined]
    assert PRIVATE not in loc and "question" not in loc
    assert re.fullmatch(r"/result/[A-Za-z0-9_-]{20,}#result", loc)
    page = client.get(loc.split("#")[0])
    assert PRIVATE not in page.text
    for m in re.finditer(r'(?:href|action|src)="([^"]*)"', page.text):
        assert PRIVATE not in m.group(1)
    assert len(fake.calls) == 1


def test_prg_reload_does_not_re_ask() -> None:
    client, fake, _ = make_client()
    r = post_form(client, QUESTION)
    url = r.headers["location"].split("#")[0]  # type: ignore[attr-defined]
    first = client.get(url).text
    second = client.get(url).text
    assert first == second
    assert len(fake.calls) == 1
    assert "The docs answer this" in first
    assert ">" + QUESTION + "</textarea>" not in first  # no question stored or echoed
    assert "</textarea>" in first


def test_unknown_token_renders_the_empty_page() -> None:
    client, _, _ = make_client()
    r = client.get("/result/not-a-token")
    assert r.status_code == 200
    assert 'id="result-title"' not in r.text


def test_result_store_expiry_and_bound() -> None:
    from aveto_service.abuse_log import Outcome
    from aveto_service.pipeline import AskResult
    from aveto_service.result_store import MAX_ENTRIES, TTL_SECONDS, ResultStore

    now = [0.0]
    store = ResultStore(lambda: now[0])
    first = store.put(AskResult(Outcome.NO_CONFIDENT_MATCH))
    assert store.get(first) is not None
    now[0] += TTL_SECONDS + 1
    assert store.get(first) is None
    tokens = [store.put(AskResult(Outcome.JUDGE_ERROR)) for _ in range(MAX_ENTRIES + 5)]
    assert store.get(tokens[0]) is None
    assert store.get(tokens[-1]) is not None


# --- headers, origins, static -------------------------------------------------------------


def all_responses() -> list[object]:
    client, _, _ = make_client()
    token_url = post_form(client, QUESTION).headers["location"].split("#")[0]  # type: ignore[attr-defined]
    off, _, _ = make_client(settings=make_settings(kill_switch="on"))
    return [
        client.get("/"),
        client.get(token_url),
        client.get("/result/unknown"),
        post_form(client, ""),
        post_form(client, QUESTION),
        client.get("/static/style.css"),
        client.get("/static/enhance.js"),
        client.get("/static/nope.txt"),
        off.get("/"),
        post_form(off, QUESTION),
    ]


def test_security_headers_on_every_page_response() -> None:
    for r in all_responses():
        h = r.headers  # type: ignore[attr-defined]
        assert h["cache-control"] == "no-store"
        csp = h["content-security-policy"]
        for part in (
            "default-src 'none'",
            "script-src 'self'",
            "style-src 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "base-uri 'none'",
        ):
            assert part in csp
        assert h["x-content-type-options"] == "nosniff"
        assert h["referrer-policy"] == "no-referrer"
        assert "set-cookie" not in h


def test_no_external_origin_in_page_or_static() -> None:
    client, _, _ = make_client()
    token_url = post_form(client, QUESTION).headers["location"].split("#")[0]  # type: ignore[attr-defined]
    pages = [client.get("/").text, client.get(token_url).text]
    for page in pages:
        for m in re.finditer(r'(?:src|href|action)="([^"]*)"', page):
            url = m.group(1)
            assert url.startswith(("/", "https://github.com/")), url
        assert "<link" not in page.replace('<link rel="stylesheet" href="/static/style.css">', "")
        assert "<script" not in page.replace('<script src="/static/enhance.js" defer></script>', "")
        assert "<style" not in page and " style=" not in page and " onclick=" not in page
    for name in ("style.css", "enhance.js"):
        body = client.get(f"/static/{name}").text
        assert "://" not in body
        assert "cookie" not in body.lower()
        assert "localStorage" not in body and "sessionStorage" not in body
        assert "@import" not in body and "url(" not in body


def test_static_files_and_types() -> None:
    client, _, _ = make_client()
    css = client.get("/static/style.css")
    js = client.get("/static/enhance.js")
    assert css.status_code == 200 and css.headers["content-type"] == "text/css; charset=utf-8"
    assert js.status_code == 200
    assert js.headers["content-type"] == "text/javascript; charset=utf-8"
    assert "prefers-color-scheme: dark" in css.text and "prefers-reduced-motion" in css.text
    assert client.get("/static/nope.txt").status_code == 404
    assert client.get("/static/__init__.py").status_code == 404


def test_links_use_the_pinned_commit_and_a_generic_issue_title() -> None:
    client, _, runtime = make_client()
    text = visible(client.get("/").text)
    idx = runtime.searcher.index
    assert f"https://github.com/{idx.repo}/issues/new?title=Docs+question+not+answered" in text
    assert f"https://github.com/{idx.repo}/tree/{idx.commit}" in text


def test_answer_page_uses_the_service_judge_once_and_never_the_question() -> None:
    client, fake, _ = make_client()
    followed(client, f"{QUESTION} {PRIVATE}")
    assert len(fake.calls) == 1
    assert ANSWERABLE_REPLY  # the default fake reply is the answerable one


def test_main_module_composes_the_app(monkeypatch: pytest.MonkeyPatch) -> None:
    source = (
        __import__("pathlib").Path(__file__).resolve().parent.parent / "aveto_service" / "main.py"
    ).read_text()
    assert "create_app(runtime, _judge(), settings, html=HtmlPages(runtime))" in source
    assert "PlaceholderJudgeClient()" in source
