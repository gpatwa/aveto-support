"""`HtmlPages`: the `HtmlRenderer` the service uses. Every response carries the same headers."""

from __future__ import annotations

import tomllib
from pathlib import Path
from urllib.parse import quote

from starlette.responses import Response

from aveto_service.abuse_log import Outcome
from aveto_service.pipeline import AskResult, Runtime
from aveto_service.render import Suggestion, page_html
from aveto_service.result_store import ResultStore
from aveto_service.scorecard import build_links

STATIC_DIR = Path(__file__).resolve().parent / "static"
SUGGESTIONS_PATH = Path(__file__).resolve().parent / "suggestions.toml"
SUGGESTION_SLOTS = ("A1", "A2", "A3", "R1")
STATIC_TYPES = {
    "enhance.js": "text/javascript; charset=utf-8",
    "style.css": "text/css; charset=utf-8",
}
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
    ),
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}


def load_suggestions(path: Path = SUGGESTIONS_PATH) -> tuple[Suggestion, ...]:
    """The four suggested questions; `()` on any reading or shape error, so the page still works."""
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        rows = data["suggestion"]
        found = tuple(
            Suggestion(str(r["slot"]), str(r["text"]), str(r["expect"])) for r in rows
        )
    except (OSError, ValueError, KeyError, TypeError):
        return ()
    if data.get("schema") != 1 or tuple(s.slot for s in found) != SUGGESTION_SLOTS:
        return ()
    for s in found:
        if not s.text or len(s.text) > 90 or any(c in s.text for c in "<>\n"):
            return ()
        if s.expect != ("no_confident_match" if s.slot == "R1" else "answer"):
            return ()
    return found


class HtmlPages:
    def __init__(
        self,
        runtime: Runtime,
        store: ResultStore | None = None,
        *,
        suggestions_path: Path = SUGGESTIONS_PATH,
    ) -> None:
        index = runtime.searcher.index
        self._issue = f"https://github.com/{index.repo}/issues/new?title=Docs+question+not+answered"
        self._docs = f"https://github.com/{index.repo}/tree/{quote(index.commit)}"
        self._commit = index.commit[:7]
        self._suggestions = load_suggestions(suggestions_path)
        self._links = build_links()
        self._store = store or ResultStore()
        self._static = {name: (STATIC_DIR / name).read_bytes() for name in STATIC_TYPES}

    def _html(
        self, result: AskResult | None, raw: str, status: int = 200, *, at_load: bool = False
    ) -> Response:
        body = page_html(
            result,
            raw,
            self._issue,
            self._docs,
            suggestions=self._suggestions,
            commit=self._commit,
            links=self._links,
            at_load=at_load,
        )
        return Response(
            body, status_code=status, media_type="text/html", headers=dict(SECURITY_HEADERS)
        )

    def page(self, state: Outcome | None) -> Response:
        if state is None:
            return self._html(None, "")
        return self._html(AskResult(state), "", at_load=state is Outcome.PAUSED)

    def form_outcome(self, result: AskResult, raw: str) -> Response:
        if result.admitted:
            token = self._store.put(result)
            headers = dict(SECURITY_HEADERS)
            headers["Location"] = f"/result/{token}#result"
            return Response(status_code=303, headers=headers)
        return self._html(result, raw, result.status)

    def result_page(self, token: str) -> Response:
        result = self._store.get(token)
        return self._html(result, "")

    def static(self, name: str) -> Response:
        data = self._static.get(name)
        if data is None:
            return Response("Not found", status_code=404, headers=dict(SECURITY_HEADERS))
        return Response(data, media_type=STATIC_TYPES[name], headers=dict(SECURITY_HEADERS))
