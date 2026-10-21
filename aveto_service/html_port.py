"""The boundary to the HTML pages (Frontend fills it). The service core never renders HTML."""

from __future__ import annotations

from typing import Protocol

from starlette.responses import Response

from aveto_service.abuse_log import Outcome
from aveto_service.pipeline import AskResult


class HtmlRenderer(Protocol):
    def page(self, state: Outcome | None) -> Response:
        """`GET /`. `state` is None for the empty page, or the outcome to show, for example
        `Outcome.SERVICE_OFF` when the kill switch is on."""
        ...

    def form_outcome(self, result: AskResult, raw: str) -> Response:
        """The answer to a no-JS form post. `raw` is the visitor's text, to put back in the
        textarea when no model call happened; it is `""` for body_too_large and bad_request.
        When `result.admitted` is true the question must not be echoed and the response is a
        303 to `/result/<token>#result`."""
        ...

    def result_page(self, token: str) -> Response:
        """`GET /result/{token}`; an unknown or expired token renders the empty page."""
        ...

    def static(self, name: str) -> Response:
        """`GET /static/{name}`; only `enhance.js` and `style.css`, else 404."""
        ...
