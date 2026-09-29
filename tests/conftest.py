from __future__ import annotations

import io
import socket
import tarfile
from collections.abc import Iterator
from typing import Any, Self, cast
from urllib.request import OpenerDirector

import pytest

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

    def __init__(self, data: bytes = b"", status: int = 200, error: Exception | None = None) -> None:
        self.data = data
        self.status = status
        self.error = error
        self.urls: list[str] = []

    def open(self, request: Any, timeout: float | None = None) -> FakeResponse:
        self.urls.append(request.full_url)
        if self.error is not None:
            raise self.error
        return FakeResponse(self.data, self.status)


def as_opener(fake: FakeOpener) -> OpenerDirector:
    return cast(OpenerDirector, fake)
