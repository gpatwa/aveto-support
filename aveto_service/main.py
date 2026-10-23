"""Composition root: `uvicorn aveto_service.main:app`."""

from __future__ import annotations

from aveto_service.app import create_app, load_runtime
from aveto_service.judge_port import JudgeClient, PlaceholderJudgeClient
from aveto_service.pages import HtmlPages
from aveto_service.settings import Settings

settings = Settings.from_env()
runtime = load_runtime(settings)


def _judge() -> JudgeClient:
    if not settings.api_key:
        return PlaceholderJudgeClient()
    from aveto_service.anthropic_judge import AnthropicJudgeClient

    return AnthropicJudgeClient(settings.api_key)


app = create_app(runtime, _judge(), settings, html=HtmlPages(runtime))
