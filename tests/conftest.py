from __future__ import annotations

import dataclasses
import hashlib
import io
import math
import re
import socket
import tarfile
from collections.abc import Callable, Iterator
from typing import Any, Self, cast
from urllib.request import OpenerDirector

import pytest

from aveto_support.embed import DIM, passage_input, quantise
from aveto_support.index import Passage
from aveto_support.judge import OnnxJudge

REPO = "acme/docs"
COMMIT = "0123456789abcdef0123456789abcdef01234567"


@pytest.fixture(autouse=True)
def _network_block(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    if request.node.get_closest_marker("network"):
        yield
        return

    def blocked(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("network disabled in tests; mark with @pytest.mark.network")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    yield


def make_archive(
    files: dict[str, bytes],
    *,
    repo_name: str = "docs",
    commit: str = COMMIT,
    pax_comment: str | None = None,
    extra_members: list[tarfile.TarInfo] | None = None,
    top: str | None = None,
) -> bytes:
    """Build a GitHub-shaped tar.gz in memory: top dir `{repo_name}-{commit}/`."""
    root = top if top is not None else f"{repo_name}-{commit}"
    buf = io.BytesIO()
    pax = {"comment": pax_comment} if pax_comment is not None else {}
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.PAX_FORMAT, pax_headers=pax) as tar:
        directory = tarfile.TarInfo(root)
        directory.type = tarfile.DIRTYPE
        tar.addfile(directory)
        for name, data in files.items():
            info = tarfile.TarInfo(f"{root}/{name}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        for member in extra_members or []:
            tar.addfile(member)
    return buf.getvalue()


class FakeResponse:
    def __init__(self, data: bytes, status: int = 200) -> None:
        self._buf = io.BytesIO(data)
        self.status = status

    def read(self, n: int = -1) -> bytes:
        return self._buf.read(n)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class FakeOpener:
    """Stands in for urllib's OpenerDirector; serves fixed bytes or raises."""

    def __init__(
        self,
        data: bytes = b"",
        status: int = 200,
        error: Exception | None = None,
        routes: dict[str, bytes] | None = None,
    ) -> None:
        self.data = data
        self.routes = routes or {}
        self.status = status
        self.error = error
        self.urls: list[str] = []

    def open(self, request: Any, timeout: float | None = None) -> FakeResponse:
        self.urls.append(request.full_url)
        if self.error is not None:
            raise self.error
        for suffix, payload in self.routes.items():
            if request.full_url.endswith(suffix):
                return FakeResponse(payload, self.status)
        return FakeResponse(self.data, self.status)


def as_opener(fake: FakeOpener) -> OpenerDirector:
    return cast(OpenerDirector, fake)


MODEL = "acme/tiny-embed"
REVISION = "b" * 40
ONNX_SHA = "a" * 64
VOCAB_SHA = "c" * 64

EMBEDDING_TOML = f"""
[embedding]
model = "{MODEL}"
revision = "{REVISION}"
onnx_sha256 = "{ONNX_SHA}"
vocab_sha256 = "{VOCAB_SHA}"
"""


INCLUDE_TOML = 'include = ["README.md", "guide/", "notes/"]\n'


def config_text(
    extra: str = "", *, embedding: str = EMBEDDING_TOML, include: str = INCLUDE_TOML
) -> str:
    """A docs-source.toml body. `include` and `extra` go before the [embedding] table."""
    return f'repo = "{REPO}"\ncommit = "{COMMIT}"\n{include}{extra}\n{embedding}'


class FakeEmbedder:
    """Deterministic hashed bag-of-words vectors: no model, no network, no key."""

    @staticmethod
    def _words(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _vec(self, text: str) -> bytes:
        acc = [0.0] * DIM
        for word in self._words(text):
            digest = hashlib.sha256(word.encode()).digest()
            acc[int.from_bytes(digest[:4], "big") % DIM] += 1.0 if digest[4] % 2 else -1.0
        norm = sum(x * x for x in acc) ** 0.5
        return quantise([x / norm for x in acc] if norm else acc)

    def embed_passage(self, text: str) -> bytes:
        return self._vec(text)

    def embed_query(self, question: str) -> bytes:
        return self._vec(question)

    def token_count(self, text: str) -> int:
        return len(self._words(text))


def embed_all(passages: list[Passage], embedder: FakeEmbedder | None = None) -> list[Passage]:
    fake = embedder or FakeEmbedder()
    return [dataclasses.replace(p, embedding=fake.embed_passage(passage_input(p))) for p in passages]


class FakeReranker:
    """Deterministic token-overlap scores with a call log: no model, no network, no key."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def score(self, question: str, passage_text: str) -> float:
        self.calls.append((question, passage_text))
        q = set(re.findall(r"\w+", question.lower()))
        return float(len(q & set(re.findall(r"\w+", passage_text.lower()))))


def _logit(p: float) -> float:
    if p <= 0.0:
        return -50.0
    if p >= 1.0:
        return 50.0
    return math.log(p / (1.0 - p))


class FakeJudge:
    """Fixed or per-pair probabilities with a call log: no model, no network, no key."""

    def __init__(self, p: float | Callable[[str, str], float] = 1.0) -> None:
        self.p = p
        self.calls: list[tuple[str, str]] = []

    def logits(self, question: str, passage_text: str) -> tuple[float, ...]:
        self.calls.append((question, passage_text))
        p = self.p(question, passage_text) if callable(self.p) else self.p
        return (_logit(p),)

    def close(self) -> None:
        return None


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "real_judge_load: use the real OnnxJudge.load (default: an always-answers fake)"
    )


@pytest.fixture(autouse=True)
def _fake_judge_load(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI tests that do not inject a judge get an always-answers fake, so their output keeps
    its shape; the judge fetch in ingest is likewise stubbed (no 438 MB download in tests)."""
    if request.node.get_closest_marker("real_judge_load"):
        return
    monkeypatch.setattr(OnnxJudge, "load", staticmethod(lambda *a, **k: FakeJudge(1.0)))
    monkeypatch.setattr("aveto_support.ingest.ensure_judge_files", lambda *a, **k: "cached")
