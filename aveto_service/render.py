"""HTML for every state, built by hand with `html.escape` on every dynamic string."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from aveto_service.abuse_log import Outcome
from aveto_service.pipeline import AskResult

LIMIT = 500


@dataclass(frozen=True)
class StateCopy:
    css: str  # state-answer, state-note or state-error
    title: str
    body: str
    alert: bool = False
    links: bool = False  # repeat the issue and docs links in the body
    issue_link: bool = False  # the issue link only
    field: bool = False  # message also shown under the field


EMPTY = StateCopy(
    "state-error",
    "Please enter a question",
    "Type a question about Aveto, then press Ask. Nothing was sent.",
    alert=True,
    field=True,
)
STATES: dict[str, StateCopy] = {
    "answer": StateCopy("state-answer", "The docs answer this", ""),
    "no_confident_match": StateCopy(
        "state-note",
        "The docs don't answer this",
        "No confident match was found, so nothing is shown. You can change your question and "
        "ask again, or open a GitHub issue.",
        issue_link=True,
    ),
    "judge_error": StateCopy(
        "state-error",
        "We couldn't decide this time",
        "Something went wrong while checking the passages, so none are shown. Please try again.",
        alert=True,
    ),
    "rate_limited": StateCopy(
        "state-error",
        "Question limit reached",
        "You can ask 10 questions an hour. Please try again later. "
        "Your question is still in the box.",
        alert=True,
    ),
    "paused": StateCopy(
        "state-note",
        "Paused for today",
        "Ask the Docs has a daily limit and today's has been used. This is not a fault. "
        "You can read the docs on GitHub or open an issue.",
        links=True,
    ),
    "service_off": StateCopy(
        "state-note",
        "The service is off",
        "Ask the Docs is switched off right now. You can read the docs on GitHub or open an issue.",
        alert=True,
        links=True,
    ),
    "empty_question": EMPTY,
    "unusable_question": EMPTY,
    "bad_request": EMPTY,
}


def too_long_copy(length: int | None) -> StateCopy:
    if length is None:
        yours = "Yours is much longer."
    else:
        yours = f"Yours is {length}."
    return StateCopy(
        "state-error",
        "Your question is too long",
        f"Questions can be up to {LIMIT} characters. {yours} Shorten it and ask again. "
        "Nothing was sent.",
        alert=True,
        field=True,
    )


def copy_for(result: AskResult) -> StateCopy:
    if result.outcome in (Outcome.TOO_LONG, Outcome.BODY_TOO_LARGE):
        return too_long_copy(result.length)
    return STATES[result.outcome.value]


def _lines(start: int, end: int) -> str:
    return f"Line {start}" if start == end else f"Lines {start} to {end}"


def _link_lines(start: int, end: int) -> str:
    return f"line {start}" if start == end else f"lines {start} to {end}"


def _links(issue_url: str, docs_url: str, *, docs: bool = True) -> str:
    out = (
        f'<a href="{escape(issue_url)}" rel="noopener noreferrer">Open a GitHub issue</a>'
    )
    if docs:
        out += (
            f' <a href="{escape(docs_url)}" rel="noopener noreferrer">Read the docs on GitHub</a>'
        )
    return out


def _passages(result: AskResult) -> str:
    cards: list[str] = []
    n = 0
    for f in result.files:
        for p in f.passages:
            n += 1
            span = _link_lines(p.line_start, p.line_end)
            label = f"Passage text from {f.path}, {span}"
            cards.append(
                f'<li><article aria-labelledby="p{n}-title">'
                f'<h3 id="p{n}-title"><code>{escape(f.path)}</code></h3>'
                f'<p class="meta">Section: {escape(p.heading)}. '
                f"{_lines(p.line_start, p.line_end)}</p>"
                f'<p><a href="{escape(p.url)}" rel="noopener noreferrer">'
                f"View {span} of {escape(f.path)} on GitHub</a></p>"
                f'<pre class="passage" tabindex="0" role="region" aria-label="{escape(label)}">'
                f"<code>{escape(p.text)}</code></pre></article></li>"
            )
    return f'<ol class="passages">{"".join(cards)}</ol>'


def _count(result: AskResult) -> int:
    return sum(len(f.passages) for f in result.files)


def result_region(result: AskResult | None, issue_url: str, docs_url: str) -> str:
    """The `#result` section. Passages sit outside the live wrapper so only the heading is read."""
    live = ""
    extra = ""
    if result is not None:
        c = copy_for(result)
        title = escape(c.title)
        if result.outcome is Outcome.ANSWER:
            n = _count(result)
            found = f"Found {n} passage." if n == 1 else f"Found {n} passages."
            title += f' <span class="found">{found}</span>'
            extra = _passages(result)
        role = ' role="alert"' if c.alert else ""
        body = f"<p>{escape(c.body)}</p>" if c.body else ""
        if c.issue_link:
            body += f"<p>{_links(issue_url, docs_url, docs=False)}</p>"
        if c.links:
            body += f'<p class="links">{_links(issue_url, docs_url)}</p>'
        live = (
            f'<div class="state {c.css}"><span class="icon" aria-hidden="true">'
            f'{"!" if c.css == "state-error" else ""}</span>'
            f'<h2 id="result-title"{role}>{title}</h2>{body}</div>'
        )
    return (
        '<section id="result" tabindex="-1" aria-labelledby="result-title">'
        f'<div id="result-live" aria-live="polite" aria-atomic="true">{live}</div>'
        f'<div id="result-extra">{extra}</div></section>'
    )


def page_html(
    result: AskResult | None,
    raw: str,
    issue_url: str,
    docs_url: str,
) -> str:
    c = copy_for(result) if result is not None else None
    in_field = c is not None and c.field
    q_error = (
        f'<p id="q-error" class="error">{escape(c.body.split(". ")[0])}.</p>'
        if c is not None and in_field
        else '<p id="q-error" class="error"></p>'
    )
    n = len(raw)
    over = n > LIMIT
    count = (
        f"{n - LIMIT} characters over the limit of {LIMIT}. Shorten your question."
        if over
        else f"{n} of {LIMIT} characters"
    )
    invalid = ' aria-invalid="true"' if in_field else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Ask the Aveto docs</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<link rel="stylesheet" href="/static/style.css">
<script src="/static/enhance.js" defer></script>
</head>
<body>
<main>
<h1>Ask the Aveto docs</h1>
<p>Verbatim passages from Aveto's docs; an AI model decides only whether they answer. Nothing on this page is written by an AI model.</p>
<h2 class="plain">What to expect</h2>
<ul>
<li>You get passages copied word for word from the docs, with the file and line numbers, or a plain note that the docs don't answer your question.</li>
<li>Limits: 10 questions an hour and 500 characters a question. The service pauses for the day when the day's allowance is used.</li>
<li>Please don't put personal or confidential information in your question.</li>
<li>This service does not store or log your question. To decide whether the passages answer, your question and the passages found are sent to Anthropic, the company that makes the AI model. Anthropic handles them under its own terms, which this page does not control.</li>
<li>To apply the limits we read your address, then keep only a scrambled form of it, the time and the outcome for 7 days. The service runs in the United States (Azure, East US 2).</li>
<li>The docs are in English. One question at a time; nothing is remembered between questions.</li>
</ul>
<form id="ask-form" method="post" action="/ask#result">
<label for="q">Your question about Aveto</label>
<textarea id="q" name="question" rows="4" autocomplete="off" spellcheck="true" aria-describedby="q-hint q-count q-error"{invalid}>{escape(raw)}</textarea>
<p id="q-hint">Up to 500 characters.</p>
<p id="q-count"{' class="error"' if over else ""}>{escape(count)}</p>
<p id="q-status" class="visually-hidden" role="status"></p>
{q_error}
<button type="submit" id="ask-button">Ask</button>
</form>
{result_region(result, issue_url, docs_url)}
</main>
<footer>
<p><a id="link-issue" href="{escape(issue_url)}" rel="noopener noreferrer">Open a GitHub issue</a>. Add your question to the issue yourself if you wish.</p>
<p><a id="link-docs" href="{escape(docs_url)}" rel="noopener noreferrer">Read the docs on GitHub</a></p>
</footer>
</body>
</html>
"""
