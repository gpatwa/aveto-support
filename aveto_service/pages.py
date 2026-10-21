"""`HtmlPages`: the `HtmlRenderer` the service uses. Every response carries the same headers."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from starlette.responses import Response

from aveto_service.abuse_log import Outcome
from aveto_service.pipeline import AskResult, Runtime
from aveto_service.render import page_html
from aveto_service.result_store import ResultStore

STATIC_DIR = Path(__file__).resolve().parent / "static"
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


class HtmlPages:
    def __init__(self, runtime: Runtime, store: ResultStore | None = None) -> None:
        index = runtime.searcher.index
        self._issue = f"https://github.com/{index.repo}/issues/new?title=Docs+question+not+answered"
        self._docs = f"https://github.com/{index.repo}/tree/{quote(index.commit)}"
        self._store = store or ResultStore()
        self._static = {name: (STATIC_DIR / name).read_bytes() for name in STATIC_TYPES}

    def _html(self, result: AskResult | None, raw: str, status: int = 200) -> Response:
        body = page_html(result, raw, self._issue, self._docs)
        return Response(
            body, status_code=status, media_type="text/html", headers=dict(SECURITY_HEADERS)
        )

    def page(self, state: Outcome | None) -> Response:
        return self._html(None if state is None else AskResult(state), "")

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
