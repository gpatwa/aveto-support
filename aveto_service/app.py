"""The HTTP surface: `POST /ask`, `GET /health` and, when a renderer is given, the page routes.

`POST /ask` is the only route that can reach the judge. Route functions catch every
exception themselves so no traceback (which could hold request bytes) reaches a log.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse, Response

from aveto_service.abuse_log import Outcome, configure_logging, emit_ops
from aveto_service.html_port import HtmlRenderer
from aveto_service.judge_port import JudgeClient
from aveto_service.limits import MAX_BODY_BYTES, resolve_client_ip
from aveto_service.pipeline import AskResult, AskService, Runtime
from aveto_service.settings import Settings
from aveto_support import judge
from aveto_support.embed import OnnxEmbedder
from aveto_support.index import load_index
from aveto_support.search import Searcher

_JSON_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
_FORM = "application/x-www-form-urlencoded"
_JSON = "application/json"


def load_runtime(settings: Settings) -> Runtime:
    """Load the prompt, index and embedder or exit non-zero with one fixed ops line."""
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    configure_logging()
    category = "prompt_hash"
    try:
        prompt_bytes = Path(settings.prompt_path).read_bytes()
        if hashlib.sha256(prompt_bytes).hexdigest() != judge.PROMPT_SHA256:
            raise ValueError("prompt hash")
        system_prompt = prompt_bytes.decode("utf-8")
        category = "index"
        index = load_index(Path(settings.index_path))
        category = "model"
        embedder = OnnxEmbedder.load(Path(settings.models_path), index.params.embedding)
        searcher = Searcher(index, embedder)
    except Exception:  # noqa: BLE001 - fail closed: any failure is a refusal
        emit_ops("startup_failed", category=category)
        raise SystemExit(1) from None
    emit_ops("startup_ok")
    return Runtime(system_prompt, searcher)


def _json(result: AskResult) -> JSONResponse:
    return JSONResponse(result.to_json(), status_code=result.status, headers=_JSON_HEADERS)


def _content_type(request: Request) -> str:
    return request.headers.get("content-type", "").split(";", 1)[0].strip().lower()


async def _read_body(request: Request) -> bytes | None:
    """The body, or None when it is over the cap (reading stops at the cap)."""
    declared = request.headers.get("content-length")
    if declared is not None and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        return None
    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > MAX_BODY_BYTES:
            return None
        chunks.append(chunk)
    return b"".join(chunks)


def _question_of(body: bytes, kind: str) -> str | None:
    """The `question` field, or None if the body is not exactly one string field."""
    try:
        if kind == _JSON:
            data = json.loads(body)
            if isinstance(data, dict) and set(data) == {"question"}:
                value = data["question"]
                return value if isinstance(value, str) else None
            return None
        fields = parse_qs(
            body.decode("ascii"),
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=1,
        )
    except ValueError:
        return None
    values = fields.get("question")
    return values[0] if values is not None and len(fields) == 1 and len(values) == 1 else None


def create_app(
    runtime: Runtime,
    judge_client: JudgeClient,
    settings: Settings,
    html: HtmlRenderer | None = None,
    *,
    clock: Callable[[], datetime] | None = None,
    monotonic: Callable[[], float] | None = None,
) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    extra = {}
    if clock is not None:
        extra["clock"] = clock
    service = AskService(runtime, judge_client, settings, monotonic=monotonic, **extra)  # type: ignore[arg-type]
    app.state.service = service

    def respond(result: AskResult, kind: str, raw: str) -> Response:
        if kind == _FORM and html is not None:
            echo = raw if result.outcome not in (Outcome.BODY_TOO_LARGE, Outcome.BAD_REQUEST) else ""
            return html.form_outcome(result, echo)
        return _json(result)

    @app.post("/ask")
    async def ask(request: Request) -> Response:
        peer = request.client.host if request.client else None
        xff = ",".join(request.headers.getlist("x-forwarded-for")) or None
        ip = resolve_client_ip(xff, peer, settings.client_key)
        kind = _content_type(request)
        try:
            if settings.kill_switch != "off":
                return respond(service.refuse(Outcome.SERVICE_OFF, ip), kind, "")
            body = await _read_body(request)
            if body is None:
                return respond(service.refuse(Outcome.BODY_TOO_LARGE, ip), kind, "")
            raw = _question_of(body, kind) if kind in (_JSON, _FORM) else None
            if raw is None or (kind == _FORM and html is None):
                return respond(service.refuse(Outcome.BAD_REQUEST, ip), kind, "")
            result = await run_in_threadpool(service.ask, raw, ip)
            return respond(result, kind, raw)
        except Exception:  # noqa: BLE001 - fail closed: any failure is a refusal
            emit_ops("unhandled")
            return _json(AskResult(Outcome.JUDGE_ERROR))

    @app.get("/health")
    def health() -> Response:
        return JSONResponse(service.health(), headers=_JSON_HEADERS)

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> Response:
        emit_ops("unhandled")
        return _json(AskResult(Outcome.JUDGE_ERROR))

    if html is not None:
        pages = html

        @app.get("/")
        def index_page() -> Response:
            return pages.page(Outcome.SERVICE_OFF if settings.kill_switch != "off" else None)

        @app.get("/result/{token}")
        def result_page(token: str) -> Response:
            return pages.result_page(token)

        @app.get("/static/{name}")
        def static_file(name: str) -> Response:
            return pages.static(name)

    return app
