"""HTML for every state, built by hand with `html.escape` on every dynamic string."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from html import escape

from aveto_service.abuse_log import Outcome
from aveto_service.pipeline import AskResult

LIMIT = 500

SUGGEST_HINT = (
    "Choose one to ask it straight away. Three are answered in the docs and one is not, "
    "so you can see both outcomes."
)
RESTING_HINT = "Questions open again after midnight UTC."
CHARTER_LINK = "Read the Charter for this build (the plan approved before it was built)"
RUN_RECORD_LINK = "Read the run record"


@dataclass(frozen=True)
class Suggestion:
    slot: str
    text: str
    expect: str  # "answer" or "no_confident_match"


@dataclass(frozen=True)
class StateCopy:
    css: str  # state-answer, state-note or state-error
    title: str
    body: str
    alert: bool = False
    links: bool = False  # repeat the issue and docs links in the body
    field: bool = False  # message also shown under the field
    more: str = ""  # a fixed paragraph between the body and the links


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
        links=True,
        more="Rephrasing can help: name the command, setting or feature you mean, "
        "and ask about one thing at a time.",
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
        more="Ask the Docs is back after midnight UTC.",
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


def _links(issue_url: str, docs_url: str) -> str:
    return (
        f'<a href="{escape(issue_url)}" rel="noopener noreferrer">Open a GitHub issue</a> '
        f'<a href="{escape(docs_url)}" rel="noopener noreferrer" data-count="docs">'
        "Read the docs on GitHub</a>"
    )


def _suggestion_forms(items: Sequence[Suggestion]) -> str:
    return "".join(
        '<form class="suggest" method="post" action="/ask#result">'
        f'<input type="hidden" name="question" value="{escape(s.text)}">'
        f'<button type="submit" class="chip">{escape(s.text)}</button></form>'
        for s in items
    )


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
                f'<div class="actions"><a class="chip" href="{escape(p.url)}" '
                f'rel="noopener noreferrer">View {span} of {escape(f.path)} on GitHub</a>'
                f'<button type="button" class="secondary copy" hidden>Copy link'
                f'<span class="visually-hidden"> to {escape(f.path)}, {span}</span></button></div>'
                '<p class="caption">Quoted from the docs, word for word</p>'
                f'<pre class="passage" tabindex="0" role="region" aria-label="{escape(label)}">'
                f"<code>{escape(p.text)}</code></pre></article></li>"
            )
    return f'<ol class="passages">{"".join(cards)}</ol>'


def _count(result: AskResult) -> int:
    return sum(len(f.passages) for f in result.files)


def _drawer(
    result: AskResult, title: str, docs_url: str, commit: str, links: Mapping[str, str]
) -> str:
    """What this request already held: the outcome, the docs commit and the listed passages."""
    if result.outcome is Outcome.ANSWER:
        summary = "How this answer was made"
        items = "".join(
            f'<li><a href="{escape(p.url)}" rel="noopener noreferrer">{escape(f.path)}, '
            f"{_link_lines(p.line_start, p.line_end)}</a></li>"
            for f in result.files
            for p in f.passages
        )
        listed = f"<p>{_count(result)}</p><ul>{items}</ul>"
    else:
        summary = "How this result was made"
        listed = "<p>None. Nothing is listed when the docs don't answer.</p>"
    extra = ""
    for key, text in (("charter", CHARTER_LINK), ("run_record", RUN_RECORD_LINK)):
        if key in links:
            extra += (
                f'<li><a href="{escape(links[key])}" rel="noopener noreferrer">{text}</a></li>'
            )
    if extra:
        extra = f'<ul class="receipt-links">{extra}</ul>'
    return (
        f'<details class="receipts"><summary>{summary}</summary><dl>'
        f"<div><dt>Outcome</dt><dd>{escape(title)}</dd></div>"
        f'<div><dt>Docs version</dt><dd><a href="{escape(docs_url)}" rel="noopener noreferrer">'
        f"Commit {escape(commit)} on GitHub</a></dd></div>"
        f"<div><dt>Passages listed</dt><dd>{listed}</dd></div></dl>{extra}</details>"
    )


def result_region(
    result: AskResult | None,
    issue_url: str,
    docs_url: str,
    *,
    suggestions: Sequence[Suggestion] = (),
    commit: str = "",
    links: Mapping[str, str] | None = None,
) -> str:
    """The `#result` section. Passages sit outside the live wrapper so only the heading is read."""
    live = ""
    extra = ""
    labelled = ""
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
        if c.more:
            body += f"<p>{escape(c.more)}</p>"
        if c.links:
            body += f'<p class="links">{_links(issue_url, docs_url)}</p>'
        live = (
            f'<div class="state {c.css}"><span class="icon" aria-hidden="true">'
            f'{"!" if c.css == "state-error" else ""}</span>'
            f'<h2 id="result-title"{role}>{title}</h2>{body}</div>'
        )
        labelled = ' aria-labelledby="result-title"'
        if result.outcome is Outcome.NO_CONFIDENT_MATCH:
            answered = [s for s in suggestions if s.expect == "answer"]
            if answered:
                extra += (
                    f'<div class="try"><h3>Questions the docs do answer</h3>'
                    f"{_suggestion_forms(answered)}</div>"
                )
        if result.outcome in (Outcome.ANSWER, Outcome.NO_CONFIDENT_MATCH):
            extra += _drawer(result, c.title, docs_url, commit, links or {})
    return (
        f'<section id="result" tabindex="-1"{labelled}>'
        f'<div id="result-live" aria-live="polite" aria-atomic="true">{live}</div>'
        f'<div id="result-extra">{extra}</div></section>'
    )


EXPECT = (
    '<h2 class="plain">What to expect</h2>\n'
    '<ul>\n'
    "<li>You get passages copied word for word from the docs, with the file and line numbers, or a plain note that the docs don't answer your question.</li>\n"
    "<li>Limits: 10 questions an hour and 500 characters a question. The service pauses for the day when the day's allowance is used.</li>\n"
    "<li>Please don't put personal or confidential information in your question.</li>\n"
    '<li>This service does not store or log your question. To decide whether the passages answer, your question and the passages found are sent to Anthropic, the company that makes the AI model. Anthropic handles them under its own terms, which this page does not control.</li>\n'
    '<li>To apply the limits we read your address, then keep only a scrambled form of it, the time and the outcome for 7 days. The service runs in the United States (Azure, East US 2).</li>\n'
    '<li>The docs are in English. One question at a time; nothing is remembered between questions.</li>\n'
    '</ul>\n'
)


def page_html(
    result: AskResult | None,
    raw: str,
    issue_url: str,
    docs_url: str,
    *,
    suggestions: Sequence[Suggestion] = (),
    commit: str = "",
    links: Mapping[str, str] | None = None,
    at_load: bool = False,
    result_first: bool = False,
) -> str:
    """`at_load` is the resting page: the card above a disabled form, no suggestions, no skip link.

    `result_first` is the page that answers a question: the box, then the result, then the notes."""
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
    region = result_region(
        result, issue_url, docs_url, suggestions=suggestions, commit=commit, links=links
    )
    skip = "" if at_load else '<a class="skip" href="#q">Skip to the question box</a>\n'
    try_block = ""
    if suggestions and not at_load:
        try_block = (
            '<h2 class="plain">Try a question</h2>\n'
            f'<p id="sugg-hint">{SUGGEST_HINT}</p>\n'
            f'<div id="suggestions">{_suggestion_forms(suggestions)}</div>\n'
        )
    off = " disabled" if at_load else ""
    hint = RESTING_HINT if at_load else "Up to 500 characters."
    above, below = (region, "") if at_load else ("", region)
    first = result_first and result is not None and not at_load
    lead, tail = ("", EXPECT + try_block) if first else (EXPECT + above + try_block, "")
    ready = "" if at_load else '<p id="ready" class="ready"></p>\n'
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
{skip}<main>
<h1>Ask the Aveto docs</h1>
<p>Verbatim passages from Aveto's docs; an AI model decides only whether they answer. Nothing on this page is written by an AI model.</p>
{lead}<form id="ask-form" method="post" action="/ask#result">
<label for="q">Your question about Aveto</label>
<textarea id="q" name="question" rows="4" autocomplete="off" spellcheck="true" aria-describedby="q-hint q-count q-error"{invalid}{off}>{escape(raw)}</textarea>
<p id="q-hint">{hint}</p>
<p id="q-count"{' class="error"' if over else ""}>{escape(count)}</p>
<p id="q-status" class="visually-hidden" role="status"></p>
{q_error}
<button type="submit" id="ask-button"{off}>Ask</button>
</form>
{ready}{below}
{tail}</main>
<footer>
<p><a id="link-issue" href="{escape(issue_url)}" rel="noopener noreferrer">Open a GitHub issue</a>. Add your question to the issue yourself if you wish.</p>
<p><a id="link-docs" href="{escape(docs_url)}" rel="noopener noreferrer" data-count="docs">Read the docs on GitHub</a></p>
<p><a href="/scorecard">See the quality scorecard</a></p>
</footer>
</body>
</html>
"""
