"""Ingest: fetch the pinned archive (the only network code), split, calibrate, write."""

from __future__ import annotations

import dataclasses
import hashlib
import io
import os
import re
import tarfile
import tempfile
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from http.client import HTTPMessage
from pathlib import Path
from typing import IO, Any
from urllib.parse import urlparse

from aveto_support.embed import (
    MAX_TOKENS,
    ONNX_FILE,
    VOCAB_FILE,
    Embedder,
    OnnxEmbedder,
    model_dir,
    passage_input,
    sha256_file,
)
from aveto_support.index import (
    EmbeddingParams,
    Index,
    Passage,
    RetrievalParams,
    split_sections,
    write_index,
)
from aveto_support.search import calibrate, eligible_passages_by_file

ALLOWED_HOSTS = frozenset({"github.com", "codeload.github.com"})
HF_HOST = "huggingface.co"
HF_SUFFIX = ".hf.co"
MODEL_MAX_BYTES = 200_000_000
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
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
    embedding: EmbeddingParams = field(default_factory=EmbeddingParams)
    offtopic_path: str | None = None


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
    truncated_for_embedding: int = 0
    tau_salad: float = 0.0
    tau_offtopic: float | None = None
    model_status: str = ""


def _load_embedding(raw: object) -> tuple[EmbeddingParams, str | None]:
    if not isinstance(raw, dict):
        raise ConfigError("docs-source.toml needs an [embedding] table")
    allowed = {"model", "revision", "onnx_sha256", "vocab_sha256", "offtopic_path", "offtopic_sha256"}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ConfigError(f"unknown key(s) in [embedding]: {', '.join(unknown)}")
    model = raw.get("model")
    if not isinstance(model, str) or not _REPO.match(model):
        raise ConfigError("embedding.model must be a Hugging Face 'owner/name'")
    revision = raw.get("revision")
    if not isinstance(revision, str) or not _HEX40.match(revision):
        raise ConfigError("embedding.revision must be a full 40-character lowercase hex commit")
    hashes: dict[str, str] = {}
    for key in ("onnx_sha256", "vocab_sha256"):
        value = raw.get(key)
        if not isinstance(value, str) or not _HEX64.match(value):
            raise ConfigError(f"embedding.{key} must be a 64-character lowercase hex sha256")
        hashes[key] = value
    offtopic_path = raw.get("offtopic_path")
    offtopic_sha = raw.get("offtopic_sha256")
    if (offtopic_path is None) != (offtopic_sha is None):
        raise ConfigError("embedding.offtopic_path and embedding.offtopic_sha256 go together")
    if offtopic_path is not None:
        if not isinstance(offtopic_path, str) or offtopic_path.startswith("/") or ".." in offtopic_path.split("/"):
            raise ConfigError("embedding.offtopic_path must be repo-relative with no '..'")
        if not isinstance(offtopic_sha, str) or not _HEX64.match(offtopic_sha):
            raise ConfigError("embedding.offtopic_sha256 must be a 64-character lowercase hex sha256")
    params = EmbeddingParams(
        model=model,
        revision=revision,
        onnx_sha256=hashes["onnx_sha256"],
        vocab_sha256=hashes["vocab_sha256"],
        offtopic_sha256=offtopic_sha,
    )
    return params, offtopic_path


def load_source_config(path: Path) -> SourceConfig:
    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path} is not valid TOML: {exc}") from exc
    unknown = sorted(set(raw) - {"repo", "commit", "exclude", "embedding"})
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
    embedding, offtopic_path = _load_embedding(raw.get("embedding"))
    return SourceConfig(
        repo=repo,
        commit=commit,
        exclude=tuple(exclude),
        embedding=embedding,
        offtopic_path=offtopic_path,
    )


def load_offtopic(config: SourceConfig, config_path: Path) -> tuple[str, ...]:
    """Load the frozen off-topic list by path, after checking its pinned sha256."""
    if config.offtopic_path is None:
        return ()
    path = config_path.parent / config.offtopic_path
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"cannot read off-topic list {config.offtopic_path}: {exc.strerror or exc}") from exc
    if hashlib.sha256(raw).hexdigest() != config.embedding.offtopic_sha256:
        raise ConfigError(f"off-topic list {config.offtopic_path} does not match its pinned sha256")
    try:
        doc = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"off-topic list {config.offtopic_path} is not valid TOML") from exc
    entries = doc.get("question")
    if not isinstance(entries, list) or not entries:
        raise ConfigError("off-topic list has no [[question]] entries")
    questions: list[str] = []
    for entry in entries:
        text = entry.get("question") if isinstance(entry, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise ConfigError("every off-topic [[question]] needs a question string")
        questions.append(text)
    return tuple(questions)


def _github_host_allowed(host: str) -> bool:
    return host in ALLOWED_HOSTS


def _hf_host_allowed(host: str) -> bool:
    return host == HF_HOST or host.endswith(HF_SUFFIX)


def _normalise_host(host: str | None) -> str:
    if not host:
        return ""
    try:
        return host.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return ""


class _HostRestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed: Callable[[str], bool] = _github_host_allowed) -> None:
        self._allowed = allowed

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
        if parsed.scheme != "https" or not self._allowed(_normalise_host(parsed.hostname)):
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


def download_model_file(
    params: EmbeddingParams,
    name: str,
    dest: Path,
    expected_sha256: str,
    *,
    opener: urllib.request.OpenerDirector | None = None,
    max_bytes: int = MODEL_MAX_BYTES,
    timeout: float = 300,
) -> None:
    """Download one pinned model file, hashing as it streams. Only a matching file is kept."""
    url = f"https://{HF_HOST}/{params.model}/resolve/{params.revision}/{name}"
    request = urllib.request.Request(url, headers={"User-Agent": "aveto-support-ingest"})
    active = opener if opener is not None else urllib.request.build_opener(
        _HostRestrictedRedirect(_hf_host_allowed)
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=dest.parent, suffix=".part")
    try:
        digest = hashlib.sha256()
        total = 0
        with os.fdopen(fd, "wb") as out:
            try:
                with active.open(request, timeout=timeout) as response:
                    status = getattr(response, "status", 200)
                    if status != 200:
                        raise FetchError(f"unexpected HTTP status {status} fetching {url}")
                    while True:
                        block: bytes = response.read(1 << 20)
                        if not block:
                            break
                        total += len(block)
                        if total > max_bytes:
                            raise FetchError(f"{name} exceeds the {max_bytes}-byte size cap")
                        digest.update(block)
                        out.write(block)
            except urllib.error.HTTPError as exc:
                raise FetchError(f"HTTP {exc.code} fetching {url}") from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                raise FetchError(f"network error fetching {url}: {exc}") from exc
            out.flush()
            os.fsync(out.fileno())
        if digest.hexdigest() != expected_sha256:
            raise FetchError(f"{name} does not match its pinned sha256; discarded")
        os.replace(tmp_name, dest)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def ensure_model_files(
    params: EmbeddingParams,
    models_dir: Path,
    *,
    opener: urllib.request.OpenerDirector | None = None,
) -> str:
    """Make sure both pinned files are cached and match their sha256. Returns the status."""
    base = model_dir(models_dir, params)
    pins = ((ONNX_FILE, params.onnx_sha256), (VOCAB_FILE, params.vocab_sha256))
    downloaded = False
    for name, expected in pins:
        target = base / name
        if target.is_file():
            if sha256_file(target) == expected:
                continue
            target.unlink()
        download_model_file(params, name, target, expected, opener=opener)
        downloaded = True
    return "downloaded" if downloaded else "cached"


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
    model_opener: urllib.request.OpenerDirector | None = None,
    models_dir: Path = Path("models"),
    embedder: Embedder | None = None,
) -> IngestReport:
    source = load_source_config(config_path)
    offtopic = load_offtopic(source, config_path)
    archive = fetch_archive(source, opener=opener)
    files, skipped = read_markdown(archive, source)
    split: list[Passage] = []
    dropped = 0
    for doc in files:
        found, empty = split_sections(doc.path, doc.text)
        split.extend(found)
        dropped += empty
    split.sort(key=lambda p: (p.path, p.line_start))
    if embedder is None:
        model_status = ensure_model_files(source.embedding, models_dir, opener=model_opener)
        embedder = OnnxEmbedder.load(models_dir, source.embedding)
    else:
        model_status = "injected"
    passages: list[Passage] = []
    truncated = 0
    for passage in split:
        text = passage_input(passage)
        if embedder.token_count(text) + 2 > MAX_TOKENS:
            truncated += 1
        passages.append(dataclasses.replace(passage, embedding=embedder.embed_passage(text)))
    calibration = calibrate(passages, embedder, offtopic)
    warnings: list[str] = []
    if len(eligible_passages_by_file(passages)) < 5:
        warnings.append("fewer than 5 files have searchable text; threshold set to 1000000.0")
    if not offtopic:
        warnings.append(
            "no off-topic calibration list configured; abstention is calibrated only on "
            "word salads and is likely too permissive"
        )
    elif len(offtopic) < 50:
        warnings.append(f"off-topic calibration list has {len(offtopic)} questions; at least 50 are expected")
    index = Index(
        repo=source.repo,
        commit=source.commit,
        files_indexed=len(files),
        skipped=tuple(skipped),
        passages=tuple(passages),
        threshold=calibration.threshold,
        params=RetrievalParams(embedding=source.embedding),
        empty_sections_dropped=dropped,
        tau_salad=calibration.tau_salad,
        tau_offtopic=calibration.tau_offtopic,
        truncated_for_embedding=truncated,
    )
    digest = write_index(index, out_path)
    return IngestReport(
        repo=source.repo,
        commit=source.commit,
        files_indexed=len(files),
        passages=len(passages),
        skipped=tuple(skipped),
        empty_sections_dropped=dropped,
        threshold=calibration.threshold,
        sha256=digest,
        warnings=tuple(warnings),
        truncated_for_embedding=truncated,
        tau_salad=calibration.tau_salad,
        tau_offtopic=calibration.tau_offtopic,
        model_status=model_status,
    )
