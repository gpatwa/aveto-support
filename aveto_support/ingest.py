"""Ingest: fetch the pinned archive (the only network code), split, calibrate, write."""

from __future__ import annotations

import io
import re
import tarfile
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.client import HTTPMessage
from pathlib import Path
from typing import IO, Any
from urllib.parse import urlparse

from aveto_support.index import (
    Index,
    Passage,
    RetrievalParams,
    split_sections,
    write_index,
)
from aveto_support.search import calibrate, eligible_passages_by_file

ALLOWED_HOSTS = frozenset({"github.com", "codeload.github.com"})
_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


class ConfigError(Exception):
    """docs-source.toml is invalid."""


class FetchError(Exception):
    """The pinned archive could not be fetched or does not match the pinned commit."""


@dataclass(frozen=True)
class SourceConfig:
    repo: str
    commit: str
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocFile:
    path: str
    text: str


@dataclass(frozen=True)
class IngestReport:
    repo: str
    commit: str
    files_indexed: int
    passages: int
    skipped: tuple[tuple[str, str], ...]
    empty_sections_dropped: int
    threshold: float
    sha256: str
    warnings: tuple[str, ...] = ()


def load_source_config(path: Path) -> SourceConfig:
    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path} is not valid TOML: {exc}") from exc
    unknown = sorted(set(raw) - {"repo", "commit", "exclude"})
    if unknown:
        raise ConfigError(f"unknown key(s) in {path}: {', '.join(unknown)}")
    repo = raw.get("repo")
    if not isinstance(repo, str) or not _REPO.match(repo):
        raise ConfigError("repo must be a GitHub 'owner/name'")
    commit = raw.get("commit")
    if not isinstance(commit, str) or not _COMMIT.match(commit):
        raise ConfigError("commit must be a full 40-character lowercase hex SHA (branches, tags and short SHAs are rejected)")
    exclude = raw.get("exclude", [])
    if not isinstance(exclude, list) or not all(isinstance(e, str) for e in exclude):
        raise ConfigError("exclude must be a list of path-prefix strings")
    for prefix in exclude:
        if prefix.startswith("/") or ".." in prefix.split("/"):
            raise ConfigError(f"exclude prefix {prefix!r} must be repo-relative with no '..'")
    return SourceConfig(repo=repo, commit=commit, exclude=tuple(exclude))


class _HostRestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> urllib.request.Request | None:
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise FetchError(f"redirect to a disallowed host: {parsed.hostname or newurl!r}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _default_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_HostRestrictedRedirect())


def fetch_archive(
    source: SourceConfig,
    *,
    opener: urllib.request.OpenerDirector | None = None,
    max_bytes: int = 50_000_000,
    timeout: float = 60,
) -> bytes:
    """Download the pinned source archive. The only network call in the product."""
    url = f"https://github.com/{source.repo}/archive/{source.commit}.tar.gz"
    request = urllib.request.Request(url, headers={"User-Agent": "aveto-support-ingest"})
    active = opener if opener is not None else _default_opener()
    try:
        with active.open(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise FetchError(f"unexpected HTTP status {status} fetching {url}")
            data: bytes = response.read(max_bytes + 1)
    except urllib.error.HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} fetching {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"network error fetching {url}: {exc}") from exc
    if len(data) > max_bytes:
        raise FetchError(f"archive exceeds the {max_bytes}-byte size cap")
    return data


def read_markdown(
    archive: bytes, source: SourceConfig
) -> tuple[list[DocFile], list[tuple[str, str]]]:
    """Read .md files from the archive in memory. Nothing is written to disk."""
    top = f"{source.repo.split('/', 1)[1]}-{source.commit}"
    files: list[DocFile] = []
    skipped: list[tuple[str, str]] = []
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            members = tar.getmembers()
            comment = tar.pax_headers.get("comment")
            if comment is not None and comment != source.commit:
                raise FetchError("archive does not match pinned commit")
            for member in members:
                if member.name.split("/", 1)[0] != top:
                    raise FetchError("archive does not match pinned commit")
            for member in members:
                if not member.isfile():
                    continue
                rel = member.name.split("/", 1)[1] if "/" in member.name else ""
                if not rel or rel.startswith("/") or ".." in rel.split("/"):
                    continue
                if not rel.lower().endswith(".md"):
                    continue
                if any(rel.startswith(prefix) for prefix in source.exclude):
                    continue
                handle = tar.extractfile(member)
                if handle is None:
                    continue
                try:
                    text = handle.read().decode("utf-8-sig")
                except UnicodeDecodeError:
                    skipped.append((rel, "not utf-8"))
                    continue
                files.append(DocFile(rel, text.replace("\r\n", "\n").replace("\r", "\n")))
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise FetchError(f"archive is not a readable tar.gz: {exc}") from exc
    files.sort(key=lambda f: f.path)
    skipped.sort()
    return files, skipped


def run_ingest(
    config_path: Path,
    out_path: Path,
    *,
    opener: urllib.request.OpenerDirector | None = None,
) -> IngestReport:
    source = load_source_config(config_path)
    archive = fetch_archive(source, opener=opener)
    files, skipped = read_markdown(archive, source)
    passages: list[Passage] = []
    dropped = 0
    for doc in files:
        found, empty = split_sections(doc.path, doc.text)
        passages.extend(found)
        dropped += empty
    passages.sort(key=lambda p: (p.path, p.line_start))
    params = RetrievalParams()
    threshold = calibrate(passages, params)
    warnings: tuple[str, ...] = ()
    if len(eligible_passages_by_file(passages)) < 5:
        warnings = ("fewer than 5 files have searchable text; threshold set to 1.0",)
    index = Index(
        repo=source.repo,
        commit=source.commit,
        files_indexed=len(files),
        skipped=tuple(skipped),
        passages=tuple(passages),
        threshold=threshold,
        params=params,
        empty_sections_dropped=dropped,
    )
    digest = write_index(index, out_path)
    return IngestReport(
        repo=source.repo,
        commit=source.commit,
        files_indexed=len(files),
        passages=len(passages),
        skipped=tuple(skipped),
        empty_sections_dropped=dropped,
        threshold=threshold,
        sha256=digest,
        warnings=warnings,
    )
