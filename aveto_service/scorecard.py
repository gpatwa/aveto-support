"""The quality scorecard: recorded figures from a committed file, plus the service's own counts.

`scorecard.toml` is read once at startup by a strict reader. Any rule broken makes the whole file
unreadable and the page answers 503 with one fixed card, so a broken figure is a broken build, not
a number on the page. A row with no record is never written, so it is never shown: the page has no
placeholder, dash or "n/a". The page has no script and holds no question text (it is given none).
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from datetime import UTC, date
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import quote

from starlette.responses import Response

from aveto_service.counts import UsageSnapshot
from aveto_service.pipeline import Runtime

FIGURES_PATH = Path(__file__).resolve().parent / "scorecard.toml"
CODEX_LABEL = "Independent Codex review"
SECTION_TITLES = {"speed": "Speed", "checks": "Checks", "reviews": "Reviews"}
SECTION_LABELS: dict[str, tuple[str, ...]] = {
    "speed": ("Cold start", "Warm response time", "Cost per question"),
    "checks": ("Accessibility checks", "Mobile checks (375 px)", "Tests", "Open findings"),
    "reviews": (CODEX_LABEL,),
}
LINK_LABELS = (
    ("pull_request", "The pull request"),
    ("charter", "The Charter"),
    ("event_log", "The event log summary"),
    ("end_review", "The end review"),
    ("cost_and_time", "Cost and time"),
    ("owner_decisions", "What the owner decided"),
)
LINK_KEYS = frozenset(k for k, _ in LINK_LABELS) | {"run_record"}
DRAWER_LINK_KEYS = ("charter", "run_record")

_TOP_KEYS = frozenset({"schema", "source_base", "figure", "decision", "links"})
_FIGURE_KEYS = frozenset({"section", "label", "value", "basis", "record", "findings"})
_FIGURE_REQUIRED = frozenset({"section", "label", "value", "basis", "record"})
_DECISION_KEYS = frozenset({"who", "when", "what", "record"})
_RECORD_PATH = re.compile(r"[A-Za-z0-9._/-]+")
_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")
_URL_PREFIX = "https://github.com/"

S2 = (
    "Figures recorded while this service was built and released. A figure is shown only when a "
    "record sits behind it, with how and when it was measured."
)
S5 = "No figures have been recorded yet."
S6 = "The scorecard can't be shown right now. Please try again later."
N1 = (
    "These are totals since the service last started. They go back to zero each time it "
    "restarts, so they are not lifetime totals. This page lists totals only; it shows no "
    "question and no answer."
)
COUNT_ROWS = (
    ("Visits", "Each load of the ask page counts once."),
    ("Questions asked", "Questions that reached an answer or a refusal."),
    ("Answered", "The docs answered."),
    ("Not answered", "The docs did not answer."),
    (
        "Clicks to the docs",
        "Clicks on the docs link from the ask page, counted only when the page's script is running.",
    ),
)


class FiguresError(Exception):
    """The figures file broke a reader rule. The message never carries file content."""


@dataclass(frozen=True)
class Figure:
    section: str
    label: str
    value: str
    basis: str
    record: str
    findings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    who: str
    when: str
    what: str
    record: str


@dataclass(frozen=True)
class Figures:
    source_base: str | None
    figures: tuple[Figure, ...]
    decisions: tuple[Decision, ...]
    links: dict[str, str]


def _text(value: Any, name: str, max_len: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_len:
        raise FiguresError(f"{name} must be a non-empty string of at most {max_len} characters")
    if "\n" in value or "\r" in value:
        raise FiguresError(f"{name} must be a single line")
    return value


def _record(value: Any, name: str) -> str:
    if not isinstance(value, str) or _RECORD_PATH.fullmatch(value) is None:
        raise FiguresError(f"{name} must be a relative repository path")
    if value.startswith("/") or any(seg in ("", ".", "..") for seg in value.split("/")):
        raise FiguresError(f"{name} must be a relative repository path")
    return value


def _url(value: Any, name: str) -> str:
    if (
        not isinstance(value, str)
        or not value.startswith(_URL_PREFIX)
        or re.search(r'[\s"<>]', value) is not None
    ):
        raise FiguresError(f"{name} must be a https://github.com/ address")
    return value


def _keys(table: Any, allowed: frozenset[str], required: frozenset[str], name: str) -> None:
    if not isinstance(table, dict):
        raise FiguresError(f"{name} must be a table")
    if not set(table) <= allowed or not required <= set(table):
        raise FiguresError(f"{name} has the wrong keys")


def _figure(table: Any) -> Figure:
    _keys(table, _FIGURE_KEYS, _FIGURE_REQUIRED, "figure")
    section = table["section"]
    if section not in SECTION_LABELS:
        raise FiguresError("figure section is not one of speed, checks, reviews")
    label = table["label"]
    if label not in SECTION_LABELS[section]:
        raise FiguresError("figure label is not one of its section's labels")
    basis = _text(table["basis"], "basis", 300)
    if not basis.startswith(("Measured ", "Recorded ")):
        raise FiguresError("basis must start with Measured or Recorded")
    findings: tuple[str, ...] = ()
    if "findings" in table:
        raw = table["findings"]
        if label != CODEX_LABEL or not isinstance(raw, list):
            raise FiguresError("findings belong only on the Codex review row, as a list")
        findings = tuple(_text(f, "finding", 300) for f in raw)
    return Figure(
        section,
        label,
        _text(table["value"], "value", 120),
        basis,
        _record(table["record"], "record"),
        findings,
    )


def _decision(table: Any) -> Decision:
    _keys(table, _DECISION_KEYS, _DECISION_KEYS, "decision")
    when = table["when"]
    if not isinstance(when, str) or _DAY.fullmatch(when) is None:
        raise FiguresError("when must be YYYY-MM-DD")
    try:
        date.fromisoformat(when)
    except ValueError as exc:
        raise FiguresError("when must be a real date") from exc
    return Decision(
        _text(table["who"], "who", 40),
        when,
        _text(table["what"], "what", 300),
        _record(table["record"], "record"),
    )


def load_figures(path: Path = FIGURES_PATH) -> Figures:
    """Read and check the figures file, or raise `FiguresError`."""
    try:
        data = tomllib.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise FiguresError("the figures file could not be read") from exc
    if not set(data) <= _TOP_KEYS:
        raise FiguresError("the figures file has an unknown key")
    if type(data.get("schema")) is not int or data["schema"] != 1:
        raise FiguresError("the figures file must say schema = 1")
    source_base = data.get("source_base")
    if source_base is not None:
        source_base = _url(source_base, "source_base")
        if not source_base.endswith("/"):
            raise FiguresError("source_base must end with a slash")
    figures = data.get("figure", [])
    decisions = data.get("decision", [])
    if not isinstance(figures, list) or not isinstance(decisions, list):
        raise FiguresError("figure and decision must be lists of tables")
    links = data.get("links", {})
    if not isinstance(links, dict) or not set(links) <= LINK_KEYS:
        raise FiguresError("links has the wrong keys")
    return Figures(
        source_base,
        tuple(_figure(t) for t in figures),
        tuple(_decision(t) for t in decisions),
        {k: _url(v, f"links.{k}") for k, v in links.items()},
    )


def build_links(path: Path = FIGURES_PATH) -> dict[str, str]:
    """The Charter and run-record links for the receipts drawer; `{}` on any error."""
    try:
        links = load_figures(path).links
    except Exception:  # noqa: BLE001 - a drawer without links is the safe answer
        return {}
    return {k: links[k] for k in DRAWER_LINK_KEYS if k in links}


class ScorecardPage:
    def __init__(self, runtime: Runtime, path: Path = FIGURES_PATH) -> None:
        index = runtime.searcher.index
        self._issue = f"https://github.com/{index.repo}/issues/new?title=Docs+question+not+answered"
        self._docs = f"https://github.com/{index.repo}/tree/{quote(index.commit)}"
        self._figures: Figures | None
        try:
            self._figures = load_figures(path)
        except FiguresError:
            self._figures = None

    def response(self, usage: UsageSnapshot) -> Response:
        from aveto_service.pages import (
            SECURITY_HEADERS,  # late: pages.py imports this module
        )

        status = 200 if self._figures is not None else 503
        return Response(
            self._page(usage),
            status_code=status,
            media_type="text/html",
            headers=dict(SECURITY_HEADERS),
        )

    # --- markup ------------------------------------------------------------------------

    def _source(self, record: str) -> str:
        base = self._figures.source_base if self._figures is not None else None
        if base is None:
            return ""
        return f' <a href="{escape(base + record)}" rel="noopener noreferrer">Source</a>'

    def _figure_section(self, section: str, rows: list[Figure]) -> str:
        out = [f'<h2>{SECTION_TITLES[section]}</h2><dl class="figures">']
        for f in rows:
            findings = ""
            if f.findings:
                items = "".join(f"<li>{escape(t)}</li>" for t in f.findings)
                findings = f'<dd><h3>What it found</h3><ul class="findings">{items}</ul></dd>'
            out.append(
                f'<div><dt>{escape(f.label)}</dt><dd class="value">{escape(f.value)}</dd>'
                f'<dd class="basis">{escape(f.basis)}{self._source(f.record)}</dd>{findings}</div>'
            )
        out.append("</dl>")
        return "".join(out)

    def _decisions(self, decisions: tuple[Decision, ...]) -> str:
        items = "".join(
            f'<li><span class="when">{escape(d.when)}</span> {escape(d.who)}: {escape(d.what)}'
            f"{self._source(d.record)}</li>"
            for d in decisions
        )
        return f'<h2>Who decided what</h2><ul class="decisions">{items}</ul>'

    def _counts(self, usage: UsageSnapshot) -> str:
        values = (usage.visits, usage.asked, usage.answered, usage.refused, usage.docs_clicks)
        rows = "".join(
            f'<div><dt>{escape(label)}</dt><dd class="value">{value}</dd>'
            f'<dd class="basis">{escape(basis)}</dd></div>'
            for (label, basis), value in zip(COUNT_ROWS, values, strict=True)
        )
        started = usage.started_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M")
        return (
            "<h2>Use since the service last started</h2>"
            f"<p>{escape(N1)}</p><p>The service started {started} UTC.</p>"
            f'<dl class="figures">{rows}</dl>'
        )

    def _built(self, links: dict[str, str]) -> str:
        items = "".join(
            f'<li><a href="{escape(links[key])}" rel="noopener noreferrer">{label}</a></li>'
            for key, label in LINK_LABELS
            if key in links
        )
        return f"<h2>How this was built</h2><ul>{items}</ul>" if items else ""

    def _body(self, usage: UsageSnapshot) -> str:
        figures = self._figures
        if figures is None:
            return f'<div class="state state-note"><h2>{escape(S6)}</h2></div>'
        parts = []
        if not figures.figures and not figures.decisions:
            parts.append(f"<p>{S5}</p>")
        for section in SECTION_TITLES:
            rows = [f for f in figures.figures if f.section == section]
            if rows:
                parts.append(self._figure_section(section, rows))
        if figures.decisions:
            parts.append(self._decisions(figures.decisions))
        parts.append(self._counts(usage))
        parts.append(self._built(figures.links))
        return "".join(parts)

    def _page(self, usage: UsageSnapshot) -> str:
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Quality scorecard - Ask the Aveto docs</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<main>
<h1>Quality scorecard</h1>
<p>{escape(S2)}</p>
<p><a href="/">Back to Ask the Aveto docs</a></p>
{self._body(usage)}
</main>
<footer>
<p><a id="link-issue" href="{escape(self._issue)}" rel="noopener noreferrer">Open a GitHub issue</a>. Add your question to the issue yourself if you wish.</p>
<p><a id="link-docs" href="{escape(self._docs)}" rel="noopener noreferrer">Read the docs on GitHub</a></p>
</footer>
</body>
</html>
"""
