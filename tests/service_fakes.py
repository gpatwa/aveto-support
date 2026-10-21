"""Fakes for the service tests: no model, no network, no key."""

from __future__ import annotations

import logging
import sys
import threading
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from conftest import FakeEmbedder, embed_all
from fastapi import FastAPI

from aveto_service import abuse_log
from aveto_service.app import create_app
from aveto_service.html_port import HtmlRenderer
from aveto_service.judge_port import JudgeCall
from aveto_service.pipeline import AskService, Runtime
from aveto_service.settings import Settings
from aveto_support.index import Index, Passage, RetrievalParams, split_passages
from aveto_support.search import Searcher

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "answerability-judge-v1.txt"
CANARY = "zqxcanaryvelocity7731"

DOCS = {
    "guide/install.md": "# Install\n\nRun the installer to set up the tool.\n\n## Upgrade\n\nUpgrade by re-running the installer.\n",
    "guide/billing.md": "# Billing\n\nInvoices are issued monthly. Refunds take five days.\n",
    "notes/faq.md": "# FAQ\n\nHow do I reset my password? Use the reset link on the sign in page.\n",
    "README.md": "# Docs\n\nWelcome to the docs about install, billing and passwords.\n",
}

ANSWERABLE_REPLY = "Q1 ANSWERABLE the passages answer it"
NOT_ANSWERABLE_REPLY = "Q1 NOT_ANSWERABLE the passages do not answer it"


class CountingEmbedder(FakeEmbedder):
    """Counts query embeddings, i.e. retrievals."""

    def __init__(self) -> None:
        self.queries = 0

    def embed_query(self, question: str) -> bytes:
        self.queries += 1
        return super().embed_query(question)


class FakeJudgeClient:
    """Records every (system_prompt, payload). `script` items are returned or raised in order;
    when it runs out the default reply is used."""

    def __init__(
        self,
        script: Sequence[JudgeCall | Exception] | None = None,
        default: JudgeCall | None = None,
    ) -> None:
        self.calls: list[tuple[str, str]] = []
        self._script = list(script or [])
        self._default = default or JudgeCall(ANSWERABLE_REPLY, 2400, 20)

    def judge(self, system_prompt: str, payload: str) -> JudgeCall:
        self.calls.append((system_prompt, payload))
        item = self._script.pop(0) if self._script else self._default
        if isinstance(item, Exception):
            raise item
        return item


@dataclass
class FakeClock:
    now: datetime = field(default_factory=lambda: datetime(2026, 10, 21, 7, 0, 0, tzinfo=UTC))
    mono: float = 1000.0

    def utc(self) -> datetime:
        return self.now

    def monotonic(self) -> float:
        return self.mono

    def advance(self, seconds: float) -> None:
        self.now += timedelta(seconds=seconds)
        self.mono += seconds


def make_searcher(
    docs: dict[str, str] | None = None, embedder: CountingEmbedder | None = None
) -> Searcher:
    found: list[Passage] = []
    for path, text in (docs or DOCS).items():
        found.extend(split_passages(path, text))
    found.sort(key=lambda p: (p.path, p.line_start))
    ps = embed_all(found)
    index = Index("acme/docs", "c" * 40, len(docs or DOCS), (), tuple(ps), 0.0, RetrievalParams())
    return Searcher(index, embedder or CountingEmbedder())


def make_runtime(
    docs: dict[str, str] | None = None, embedder: CountingEmbedder | None = None
) -> Runtime:
    return Runtime(PROMPT_PATH.read_bytes().decode("utf-8"), make_searcher(docs, embedder))


def make_settings(**overrides: object) -> Settings:
    base: dict[str, object] = {"kill_switch": "off", "api_key": "test-key"}
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def make_service(
    judge_client: FakeJudgeClient,
    *,
    settings: Settings | None = None,
    runtime: Runtime | None = None,
    clock: FakeClock | None = None,
) -> AskService:
    clk = clock or FakeClock()
    return AskService(
        runtime or make_runtime(),
        judge_client,
        settings or make_settings(),
        clock=clk.utc,
        monotonic=clk.monotonic,
    )



@pytest.fixture
def logging_state() -> Iterator[None]:
    """Undo `configure_logging()`: handlers, levels, silenced libraries, excepthooks."""
    names = [*abuse_log._SILENCED, "aveto_service.abuse", "aveto_service.ops"]
    root = logging.getLogger()
    saved_root = (list(root.handlers), root.level)
    saved = {
        n: (list(logging.getLogger(n).handlers), logging.getLogger(n).level,
            logging.getLogger(n).propagate, logging.getLogger(n).disabled)
        for n in names
    }
    hooks = (sys.excepthook, threading.excepthook, abuse_log._installed)
    yield
    root.handlers[:] = saved_root[0]
    root.setLevel(saved_root[1])
    for n, (handlers, level, propagate, disabled) in saved.items():
        lg = logging.getLogger(n)
        lg.handlers[:] = handlers
        lg.setLevel(level)
        lg.propagate = propagate
        lg.disabled = disabled
    sys.excepthook, threading.excepthook, abuse_log._installed = hooks


def make_app(
    judge_client: FakeJudgeClient,
    *,
    settings: Settings | None = None,
    runtime: Runtime | None = None,
    clock: FakeClock | None = None,
    html: HtmlRenderer | None = None,
) -> FastAPI:
    clk = clock or FakeClock()
    return create_app(
        runtime or make_runtime(),
        judge_client,
        settings or make_settings(),
        html,
        clock=clk.utc,
        monotonic=clk.monotonic,
    )
