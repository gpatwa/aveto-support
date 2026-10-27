"""The page's cards, resting state, receipts drawer and one-renderer rule (stage 5's contract).

Written tests-first in stage 4 from `runs/polished-chat-experience/05-tech-spec.md` section 10
and frozen: stage 5 makes these pass and does not edit this file. Everything new is reached over
HTTP, so on the untouched base commit each test fails on an assertion, not at import.
"""

from __future__ import annotations

import dataclasses
import html as htmllib
import re
from html.parser import HTMLParser
from urllib.parse import urlencode

import httpx2 as httpx
from fastapi.testclient import TestClient
from service_fakes import (
    DOCS,
    NOT_ANSWERABLE_REPLY,
    CountingEmbedder,
    FakeJudgeClient,
    make_app,
    make_runtime,
    make_settings,
)

from aveto_service.judge_port import JudgeCall
from aveto_service.pages import HtmlPages
from aveto_service.pipeline import TOP_OF_FILE, AskResult, Runtime
from aveto_support import judge

QUESTION = "how do I install the tool"
FORM = {"Content-Type": "application/x-www-form-urlencoded"}
MODEL_CANARY = "zqxmodelwords5521"

F1 = "Rephrasing can help: name the command, setting or feature you mean, and ask about one thing at a time."
F2 = "Questions the docs do answer"
REST1 = "Ask the Docs is back after midnight UTC."
REST3 = "Questions open again after midnight UTC."
CAPTION = "Quoted from the docs, word for word"
COPY = "Copy link"
D1 = "How this answer was made"
D2 = "How this result was made"
D5 = "None. Nothing is listed when the docs don't answer."
D7 = "Read the Charter for this build (the plan approved before it was built)"
D8 = "Read the run record"
G1 = "Try a question"
SA1 = 'Does saying "looks good" to an agent count as approving something?'
SA2 = "Can I keep a long-lived feature branch going while the agents work on it?"
SA3 = "If a deploy of the Aveto website goes wrong, how do I undo it?"
SR1 = "Does it support right-to-left languages?"
RESTING_BODY = (
    "Ask the Docs has a daily limit and today's has been used. This is not a fault. "
    "You can read the docs on GitHub or open an issue."
)
REFUSAL_BODY = (
    "No confident match was found, so nothing is shown. You can change your question and ask "
    "again, or open a GitHub issue."
)

# Lines 203 to 212 of `git show 32e54a6:aveto_service/render.py`: the intro paragraph through
# `</ul>`. Copied as literals so the test needs no git.
DISCLOSURE_LINES = [
    "<p>Verbatim passages from Aveto's docs; an AI model decides only whether they answer. Nothing on this page is written by an AI model.</p>",
    '<h2 class="plain">What to expect</h2>',
    "<ul>",
    "<li>You get passages copied word for word from the docs, with the file and line numbers, or a plain note that the docs don't answer your question.</li>",
    "<li>Limits: 10 questions an hour and 500 characters a question. The service pauses for the day when the day's allowance is used.</li>",
    "<li>Please don't put personal or confidential information in your question.</li>",
    "<li>This service does not store or log your question. To decide whether the passages answer, your question and the passages found are sent to Anthropic, the company that makes the AI model. Anthropic handles them under its own terms, which this page does not control.</li>",
    "<li>To apply the limits we read your address, then keep only a scrambled form of it, the time and the outcome for 7 days. The service runs in the United States (Azure, East US 2).</li>",
    "<li>The docs are in English. One question at a time; nothing is remembered between questions.</li>",
    "</ul>",
]

_VOID = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
)


class ResultText(HTMLParser):
    """What sits inside the element `id="result"`, fed the whole document once.

    `runs`: the text between two tags, stripped, empty runs dropped (a run inside `pre` keeps its
    exact bytes). `pre_runs` / `non_pre_runs`: the same, split by being inside `pre` or not.
    `hrefs`: every href. `drawer_runs` / `drawer_hrefs`: the same for `details.receipts`.
    `drawers`: how many `details.receipts` there are. `raw`: the element's source text.
    """

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self._source = source
        self._starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self._stack: list[tuple[str, bool, bool, bool]] = []  # tag, is_root, is_pre, is_drawer
        self._buf: list[str] = []
        self._in_root = False
        self._root_start = 0
        self.found = False
        self.raw = ""
        self.runs: list[str] = []
        self.pre_runs: list[str] = []
        self.non_pre_runs: list[str] = []
        self.hrefs: list[str] = []
        self.drawer_runs: list[str] = []
        self.drawer_hrefs: list[str] = []
        self.drawers = 0

    def _offset(self) -> int:
        line, col = self.getpos()
        return self._starts[line - 1] + col

    def _pre(self) -> bool:
        return any(e[2] for e in self._stack)

    def _drawer(self) -> bool:
        return any(e[3] for e in self._stack)

    def _flush(self) -> None:
        if not self._buf:
            return
        text = "".join(self._buf)
        self._buf = []
        if self._pre():
            if not text.strip():
                return
            self.pre_runs.append(text)
            self.runs.append(text)
            return
        text = text.strip()
        if not text:
            return
        self.non_pre_runs.append(text)
        self.runs.append(text)
        if self._drawer():
            self.drawer_runs.append(text)

    def handle_data(self, data: str) -> None:
        if self._in_root:
            self._buf.append(data)

    def _open(self, tag: str, attrs: list[tuple[str, str | None]], *, void: bool) -> None:
        self._flush()
        a = dict(attrs)
        is_root = not self._in_root and a.get("id") == "result"
        if is_root:
            self._in_root = True
            self.found = True
            self._root_start = self._offset()
        if not self._in_root:
            return
        href = a.get("href")
        if href is not None:
            self.hrefs.append(href)
            if self._drawer():
                self.drawer_hrefs.append(href)
        if void:
            return
        classes = (a.get("class") or "").split()
        is_drawer = tag == "details" and "receipts" in classes
        if is_drawer:
            self.drawers += 1
        self._stack.append((tag, is_root, tag == "pre", is_drawer))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, void=tag in _VOID)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, void=True)

    def handle_endtag(self, tag: str) -> None:
        if not self._in_root:
            return
        self._flush()
        names = [e[0] for e in self._stack]
        if tag not in names:
            return
        while self._stack:
            _, is_root, _, _ = entry = self._stack.pop()
            if is_root:
                start = self._offset()
                end = self._source.index(">", start) + 1
                self.raw = self._source[self._root_start : end]
                self._in_root = False
                break
            if entry[0] == tag:
                break


def result_of(page: str) -> ResultText:
    parsed = ResultText(page)
    parsed.feed(page)
    parsed.close()
    assert parsed.found, "no element with id=result"
    return parsed


class _Tags(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))


def has_attr(page: str, *, tag: str, id: str, attr: str) -> bool:
    parsed = _Tags()
    parsed.feed(page)
    for name, attrs in parsed.tags:
        if name == tag and attrs.get("id") == id:
            return attr in attrs
    raise AssertionError(f"no <{tag} id={id}> in the page")


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


def refusing(runtime: Runtime | None = None) -> tuple[TestClient, FakeJudgeClient, Runtime]:
    return make_client(
        FakeJudgeClient(default=JudgeCall(NOT_ANSWERABLE_REPLY, 100, 5)), runtime=runtime
    )


def post_form(client: TestClient, text: str) -> httpx.Response:
    return client.post("/ask", content=urlencode({"question": text}), headers=FORM)


def followed(client: TestClient, text: str) -> str:
    """The raw HTML of the result page a form post leads to (the 303 target)."""
    r = post_form(client, text)
    assert r.status_code == 303
    page = client.get(r.headers["location"].split("#")[0])
    assert page.status_code == 200
    return page.text


def span(m: object) -> str:
    p = m.passage  # type: ignore[attr-defined]
    return f"line {p.line_start}" if p.line_start == p.line_end else f"lines {p.line_start} to {p.line_end}"


def cap_span(m: object) -> str:
    s = span(m)
    return s[0].upper() + s[1:]


def heading(m: object) -> str:
    path = m.passage.heading_path  # type: ignore[attr-defined]
    return " > ".join(path) if path else TOP_OF_FILE


def listed_passages(runtime: Runtime) -> list[tuple[str, object]]:
    found = judge.retrieve_for_judge(runtime.searcher, QUESTION)
    return [(f.path, m) for f in found.files for m in f.passages]


def docs_url_of(runtime: Runtime) -> str:
    idx = runtime.searcher.index
    return f"https://github.com/{idx.repo}/tree/{idx.commit}"


# --- intent test 1: the refusal card (C1.4.2, second half) -------------------------------------


def test_refusal_card_shows_no_model_written_text() -> None:
    client, _, runtime = make_client(
        FakeJudgeClient(default=JudgeCall(f"Q1 NOT_ANSWERABLE {MODEL_CANARY}", 100, 5))
    )
    page = followed(client, QUESTION)
    res = result_of(page)
    c7 = runtime.searcher.index.commit[:7]
    assert MODEL_CANARY not in page
    for s in ("Deciding signal", "NOT_ANSWERABLE", "answerability-judge-v1", judge.PROMPT_SHA256):
        assert s not in page
    assert res.pre_runs == [] and 'class="passages"' not in res.raw
    assert not any(path in res.raw for path in DOCS)
    required = {
        "The docs don't answer this",
        REFUSAL_BODY,
        F1,
        "Open a GitHub issue",
        "Read the docs on GitHub",
        F2,
        SA1,
        SA2,
        SA3,
        D2,
        "Outcome",
        "Docs version",
        f"Commit {c7} on GitHub",
        "Passages listed",
        D5,
    }
    assert required <= set(res.runs) <= required | {D7, D8}
    assert SR1 not in res.runs


# --- intent test 2: the resting state at the cap -----------------------------------------------


def test_resting_state_at_the_cap() -> None:
    embedder = CountingEmbedder()
    client, fake, _ = make_client(runtime=make_runtime(embedder=embedder))
    service = client.app.state.service  # type: ignore[attr-defined]
    service._spend.cap = service._floor - 1  # the day's share cannot fit one more request
    before = client.get("/health").json()
    r = client.get("/")
    text = htmllib.unescape(r.text)
    assert r.status_code == 200
    assert "Paused for today" in text and REST1 in text and REST3 in text
    assert RESTING_BODY in text
    assert has_attr(r.text, tag="textarea", id="q", attr="disabled")
    assert has_attr(r.text, tag="button", id="ask-button", attr="disabled")
    assert G1 not in text and SA1 not in text
    assert text.count("Read the docs on GitHub") == 2
    assert 'role="alert"' not in text and "state-error" not in text
    assert client.get("/health").json() == before
    assert fake.calls == [] and embedder.queries == 0
    # (b) the day closed by a refused reservation, then a page load
    client2, fake2, _ = make_client()
    s2 = client2.app.state.service  # type: ignore[attr-defined]
    s2._spend.cap = s2._floor  # peek passes, the two-attempt reservation closes the day
    assert "Paused for today" in htmllib.unescape(post_form(client2, QUESTION).text)
    r2 = client2.get("/")
    assert REST1 in htmllib.unescape(r2.text)
    assert has_attr(r2.text, tag="textarea", id="q", attr="disabled")
    assert fake2.calls == []


# --- intent test 4: the receipts drawer --------------------------------------------------------


def test_receipts_drawer_shows_only_what_the_service_held() -> None:
    client, _, runtime = make_client()
    c7 = runtime.searcher.index.commit[:7]
    docs_url = docs_url_of(runtime)
    github = "https://github.com/gpatwa/aveto-support/"
    # answer
    res = result_of(followed(client, QUESTION))
    listed = listed_passages(runtime)
    n = len(listed)
    assert res.drawers == 1  # exactly one details.receipts inside #result
    req = {
        D1,
        "Outcome",
        "The docs answer this",
        "Docs version",
        f"Commit {c7} on GitHub",
        "Passages listed",
        str(n),
    } | {f"{p}, {span(m)}" for p, m in listed}
    assert req <= set(res.drawer_runs) <= req | {D7, D8}
    own = {m.url for _, m in listed} | {docs_url}  # type: ignore[attr-defined]
    assert own <= set(res.drawer_hrefs)
    assert all(h in own or h.startswith(github) for h in res.drawer_hrefs)
    words = " ".join(res.drawer_runs).lower()
    assert not any(w in words for w in ("judge", "verdict", "signal", "score", "model"))
    # refusal
    rclient, _, _ = refusing(runtime)
    rres = result_of(followed(rclient, QUESTION))
    assert rres.drawers == 1
    req = {
        D2,
        "Outcome",
        "The docs don't answer this",
        "Docs version",
        f"Commit {c7} on GitHub",
        "Passages listed",
        D5,
    }
    assert req <= set(rres.drawer_runs) <= req | {D7, D8}
    assert all(h == docs_url or h.startswith(github) for h in rres.drawer_hrefs)
    # nothing new is held
    assert [f.name for f in dataclasses.fields(AskResult)] == [
        "outcome",
        "docs_repo",
        "docs_commit",
        "files",
        "signal",
        "length",
    ]
    # not rendered where the service held nothing about an answer
    judge_error_page = followed(
        make_client(FakeJudgeClient(default=JudgeCall("garbage", 100, 5)))[0], QUESTION
    )
    limited, _, _ = make_client()
    for _ in range(10):
        assert post_form(limited, QUESTION).status_code == 303
    rate_limited_post_page = post_form(limited, QUESTION).text
    paused, _, _ = make_client()
    ps = paused.app.state.service  # type: ignore[attr-defined]
    ps._spend.cap = ps._floor + 1000
    paused_post_page = post_form(paused, QUESTION).text
    kill_switch_get_page = make_client(settings=make_settings(kill_switch="on"))[0].get("/").text
    plain, _, _ = make_client()
    too_long_post_page = post_form(plain, "a" * 501).text
    empty_post_page = post_form(plain, "").text
    for p in (
        judge_error_page,
        rate_limited_post_page,
        paused_post_page,
        kill_switch_get_page,
        too_long_post_page,
        empty_post_page,
    ):
        assert 'class="receipts"' not in p
    assert "Question limit reached" in rate_limited_post_page  # the pages above are the real ones
    assert "Paused for today" in paused_post_page


# --- C1.4.2: the answer card holds only listed text --------------------------------------------


def test_answer_card_holds_only_text_from_a_listed_passage() -> None:
    client, _, runtime = make_client(
        FakeJudgeClient(default=JudgeCall(f"Q1 ANSWERABLE {MODEL_CANARY}", 2400, 20))
    )
    page = followed(client, QUESTION)
    res = result_of(page)
    c7 = runtime.searcher.index.commit[:7]
    listed = listed_passages(runtime)
    n = len(listed)
    assert n >= 1
    assert res.pre_runs == [m.passage.text for _, m in listed]  # type: ignore[attr-defined]
    assert MODEL_CANARY not in page
    for s in ("Deciding signal", "ANSWERABLE", "answerability-judge-v1", judge.PROMPT_SHA256):
        assert s not in page
    found = "Found 1 passage." if n == 1 else f"Found {n} passages."
    required = {
        "The docs answer this",
        found,
        D1,
        "Outcome",
        "Docs version",
        f"Commit {c7} on GitHub",
        "Passages listed",
    }
    allowed = required | {CAPTION, COPY, str(n), D7, D8}
    for path, m in listed:
        per = {
            path,
            f"Section: {heading(m)}. {cap_span(m)}",
            f"View {span(m)} of {path} on GitHub",
            f"to {path}, {span(m)}",
            f"{path}, {span(m)}",
        }
        required |= per
        allowed |= per
    assert required <= set(res.non_pre_runs) <= allowed
    assert res.non_pre_runs.count(CAPTION) == n and res.non_pre_runs.count(COPY) == n


# --- the aria-prohibited-attr fix (UX 6.1) -----------------------------------------------------


def test_every_aria_reference_resolves() -> None:
    client, _, runtime = make_client()
    rclient, _, _ = refusing(runtime)
    resting, _, _ = make_client()
    rs = resting.app.state.service  # type: ignore[attr-defined]
    rs._spend.cap = rs._floor - 1
    docs = {
        "get": client.get("/").text,
        "answer": followed(client, QUESTION),
        "refusal": followed(rclient, QUESTION),
        "resting": resting.get("/").text,
        "scorecard": client.get("/scorecard").text,
    }
    for name, d in docs.items():
        ids = set(re.findall(r'\sid="([^"]+)"', d))
        for attr in ("aria-labelledby", "aria-describedby"):
            for value in re.findall(rf'\s{attr}="([^"]+)"', d):
                assert set(value.split()) <= ids, (name, attr, value)
    assert '<section id="result" tabindex="-1">' in docs["get"]
    assert 'aria-labelledby="result-title"' not in docs["get"]
    assert '<section id="result" tabindex="-1" aria-labelledby="result-title">' in docs["answer"]
    assert 'id="result-title"' in docs["answer"]


# --- one renderer (O2): the page script builds no result card ----------------------------------


def test_page_script_builds_no_result_card() -> None:
    client, _, _ = make_client()
    js = client.get("/static/enhance.js").text
    for s in (
        "The docs answer this",
        "The docs don't answer this",
        "Paused for today",
        "The service is off",
        "Question limit reached",
        "We couldn't decide this time",
        "Your question is too long",
        "Please enter a question",
        "Found ",
        "Section: ",
        "No confident match",
    ):
        assert s not in js
    assert "DOMParser" in js and "application/x-www-form-urlencoded" in js
    assert '"/warm"' in js and '"/count/docs-click"' in js
    assert "JSON.stringify" not in js and "application/json" not in js


# --- guard: the privacy and Article 50 block is byte-identical (passes on 32e54a6) ---------------


def test_disclosure_block_byte_identical() -> None:
    block = "\n".join(DISCLOSURE_LINES)
    client, _, _ = make_client()
    assert block in client.get("/").text
    resting, _, _ = make_client()
    rs = resting.app.state.service  # type: ignore[attr-defined]
    rs._spend.cap = rs._floor - 1
    assert block in resting.get("/").text
