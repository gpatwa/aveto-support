from __future__ import annotations

import hashlib
import io
import json
import random
import tarfile
import urllib.error
from collections.abc import Callable
from http.client import HTTPMessage
from pathlib import Path
from urllib.request import Request

import pytest
from conftest import (
    COMMIT,
    EMBEDDING_TOML,
    INCLUDE_TOML,
    MODEL,
    REPO,
    REVISION,
    FakeEmbedder,
    FakeJudge,
    FakeOpener,
    FakeReranker,
    as_opener,
    make_archive,
)

from aveto_support.__main__ import main
from aveto_support.embed import ONNX_FILE, VOCAB_FILE, ModelError, OnnxEmbedder
from aveto_support.index import (
    EmbeddingParams,
    Index,
    RetrievalParams,
    load_index,
    write_index,
)
from aveto_support.ingest import (
    ConfigError,
    FetchError,
    IngestReport,
    SourceConfig,
    _hf_host_allowed,
    _HostRestrictedRedirect,
    download_model_file,
    ensure_judge_files,
    ensure_model_files,
    ensure_reranker_files,
    fetch_archive,
    load_source_config,
    read_markdown,
    run_ingest,
)
from aveto_support.judge import JudgeParams, OnnxJudge, judge_dir
from aveto_support.rerank import OnnxReranker, RerankParams, reranker_dir


def _src(*include: str, exclude: tuple[str, ...] = ()) -> SourceConfig:
    return SourceConfig(REPO, COMMIT, include, exclude)


SRC = _src("a.md")
FAKE = FakeEmbedder()

DOCS = {
    "README.md": b"# Home\nWelcome to the widget project.\n",
    "guide/setup.md": b"# Setup\n## Install\nRun the installer program.\n## Configure\nEdit the config file.\n",
    "guide/usage.md": b"# Usage\nLaunch the widget from the menu.\n",
    "notes/a.md": b"# Alpha\nAlpha gizmo details.\n",
    "notes/b.md": b"# Beta\nBeta sprocket details.\n",
    "notes/c.md": b"# Gamma\nGamma cog details.\n",
}


def _cfg(tmp_path: Path, body: str, embedding: str = EMBEDDING_TOML) -> Path:
    path = tmp_path / "src.toml"
    path.write_text(body + "\n" + embedding)
    return path


def _base(extra: str = "", include: str = INCLUDE_TOML) -> str:
    return f'repo = "{REPO}"\ncommit = "{COMMIT}"\n{include}{extra}'


def _ingest(cfg: Path, out: Path, opener: FakeOpener, tmp_path: Path) -> IngestReport:
    return run_ingest(cfg, out, opener=as_opener(opener), models_dir=tmp_path / "models", embedder=FAKE)


# --- config ----------------------------------------------------------------


def test_load_config_valid(tmp_path: Path) -> None:
    cfg = load_source_config(_cfg(tmp_path, _base('exclude = ["drafts/"]')))
    assert cfg.repo == REPO and cfg.commit == COMMIT and cfg.exclude == ("drafts/",)
    assert cfg.include == ("README.md", "guide/", "notes/")
    assert cfg.embedding.model == MODEL and cfg.embedding.revision == REVISION
    assert cfg.offtopic_path is None and cfg.embedding.offtopic_sha256 is None


def test_committed_config_is_valid() -> None:
    cfg = load_source_config(Path(__file__).parent.parent / "docs-source.toml")
    assert len(cfg.commit) == 40 and len(cfg.embedding.revision) == 40
    assert cfg.embedding.model == "BAAI/bge-small-en-v1.5"
    assert cfg.offtopic_path is not None and cfg.embedding.offtopic_sha256 is not None


def test_short_sha_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="40"):
        load_source_config(_cfg(tmp_path, f'repo = "{REPO}"\ncommit = "0123abc"\n'))


def test_branch_name_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_source_config(_cfg(tmp_path, f'repo = "{REPO}"\ncommit = "main"\n'))


def test_bad_repo_rejected(tmp_path: Path) -> None:
    for bad in ("nodash", "a/b/c", "https://evil.example/x"):
        with pytest.raises(ConfigError):
            load_source_config(_cfg(tmp_path, f'repo = "{bad}"\ncommit = "{COMMIT}"\n'))


def test_unknown_key_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="unknown"):
        load_source_config(_cfg(tmp_path, _base('branch = "x"\n')))


def test_exclude_dotdot_rejected(tmp_path: Path) -> None:
    for bad in ('"../x"', '"/abs"', '"a/../b"'):
        with pytest.raises(ConfigError):
            load_source_config(_cfg(tmp_path, _base(f"exclude = [{bad}]\n")))


def test_model_revision_must_be_40_hex(tmp_path: Path) -> None:
    for bad in ("main", "b" * 39, "B" * 40, "v1.5"):
        emb = EMBEDDING_TOML.replace(REVISION, bad)
        with pytest.raises(ConfigError, match="revision"):
            load_source_config(_cfg(tmp_path, _base(), emb))


def test_embedding_table_validated(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="embedding"):
        load_source_config(_cfg(tmp_path, _base(), ""))
    with pytest.raises(ConfigError, match="sha256"):
        load_source_config(_cfg(tmp_path, _base(), EMBEDDING_TOML.replace("a" * 64, "abc")))
    with pytest.raises(ConfigError, match="unknown"):
        load_source_config(_cfg(tmp_path, _base(), EMBEDDING_TOML + 'extra = "x"\n'))
    with pytest.raises(ConfigError, match="go together"):
        load_source_config(_cfg(tmp_path, _base(), EMBEDDING_TOML + 'offtopic_path = "x.toml"\n'))
    bad_path = EMBEDDING_TOML + 'offtopic_path = "../x.toml"\n' + 'offtopic_sha256 = "' + "1" * 64 + '"\n'
    with pytest.raises(ConfigError, match="repo-relative"):
        load_source_config(_cfg(tmp_path, _base(), bad_path))


def test_include_required_and_validated(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="include"):
        load_source_config(_cfg(tmp_path, _base(include="")))
    for bad in ("[]", "[1]", '"README.md"', '["a.md", "a.md"]', '["/a.md"]', '["../a.md"]',
                '["a/../b.md"]', '["notes"]', '["a.txt"]'):
        with pytest.raises(ConfigError):
            load_source_config(_cfg(tmp_path, _base(include=f"include = {bad}\n")))


def test_read_markdown_admits_only_included_paths() -> None:
    names = ["README.md", "nested/README.md", "agents/a.md", "agents-old/a.md", "docs/BACKLOG.md",
             "docs/NEW.md", "runs/x.md", "site/x.md"]
    archive = make_archive({n: b"# T\nx\n" for n in names})
    docs, _ = read_markdown(archive, _src("README.md", "agents/", "docs/NEW.md"))
    assert [d.path for d in docs] == ["README.md", "agents/a.md", "docs/NEW.md"]


def test_include_entry_matching_no_file_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cfg = _cfg(tmp_path, _base(include='include = ["README.md", "typo/"]\n'))
    out = tmp_path / "i.json"
    archive = make_archive(DOCS)
    with pytest.raises(ConfigError, match="typo/ matches no .md file"):
        _ingest(cfg, out, FakeOpener(archive), tmp_path)
    assert not out.exists()
    good = _cfg(tmp_path, _base(include='include = ["README.md"]\n'))
    assert _ingest(good, out, FakeOpener(archive), tmp_path).files_indexed == 1


def test_committed_config_include_is_decision_2() -> None:
    cfg = load_source_config(Path(__file__).parent.parent / "docs-source.toml")
    assert cfg.include == (
        "README.md",
        "docs/GETTING_STARTED.md", "docs/AGENTIC_SDLC.md", "docs/AGENT_ROLES.md",
        "docs/HUMAN_APPROVAL_RULES.md", "docs/RELEASE_GATES.md", "docs/OPERATING_MODEL.md",
        "docs/DEPLOYMENT.md", "docs/STANDARDS_WATCH.md", "docs/VALIDATION_MATRIX.md",
        "docs/PIPELINE_ANALYTICS.md",
        "agents/", "templates/", "project-packs/", "prompts/", "skills/", "examples/", "execution/",
    )
    assert cfg.exclude == ()


# --- reading the archive ---------------------------------------------------


def test_read_markdown_keeps_only_md_regular_files() -> None:
    link = tarfile.TarInfo(f"docs-{COMMIT}/link.md")
    link.type = tarfile.SYMTYPE
    link.linkname = "README.md"
    sneaky = tarfile.TarInfo(f"docs-{COMMIT}/../escape.md")
    sneaky.size = 0
    files = {"a.md": b"# A\nx\n", "b.txt": b"# no\n", "UP.MD": b"# Up\ny\n"}
    archive = make_archive(files, extra_members=[link, sneaky])
    docs, skipped = read_markdown(archive, _src("a.md", "b.txt", "UP.MD", "link.md"))
    assert [d.path for d in docs] == ["UP.MD", "a.md"]
    assert skipped == []


def test_read_markdown_strips_top_dir_and_sorts() -> None:
    archive = make_archive({"z.md": b"# Z\n1\n", "a/b.md": b"# B\n2\n", "a.md": b"# A\n3\n"})
    docs, _ = read_markdown(archive, _src("z.md", "a/", "a.md"))
    assert [d.path for d in docs] == ["a.md", "a/b.md", "z.md"]


def test_exclude_prefix_honoured() -> None:
    archive = make_archive({"drafts/x.md": b"# X\n1\n", "keep.md": b"# K\n2\n"})
    docs, _ = read_markdown(archive, _src("drafts/", "keep.md", exclude=("drafts/",)))
    assert [d.path for d in docs] == ["keep.md"]


def test_archive_for_other_commit_rejected() -> None:
    other = "f" * 40
    with pytest.raises(FetchError, match="pinned commit"):
        read_markdown(make_archive({"a.md": b"# A\nx\n"}, commit=other), SRC)
    with pytest.raises(FetchError, match="pinned commit"):
        read_markdown(make_archive({"a.md": b"# A\nx\n"}, pax_comment=other), SRC)
    docs, _ = read_markdown(make_archive({"a.md": b"# A\nx\n"}, pax_comment=COMMIT), SRC)
    assert len(docs) == 1


def test_unreadable_archive_is_fetch_error() -> None:
    with pytest.raises(FetchError):
        read_markdown(b"not a tarball", SRC)


def test_non_utf8_file_skipped_with_reason() -> None:
    archive = make_archive({"bad.md": b"# T\n\xff\xfe\n", "ok.md": b"\xef\xbb\xbf# Ok\nfine\n"})
    docs, skipped = read_markdown(archive, _src("bad.md", "ok.md"))
    assert skipped == [("bad.md", "not utf-8")]
    assert docs[0].text == "# Ok\nfine\n"


def test_crlf_normalised_line_count_preserved() -> None:
    raw = b"# A\r\nb\r\n\r\nc\rd\r\n"
    docs, _ = read_markdown(make_archive({"a.md": raw}), SRC)
    assert "\r" not in docs[0].text
    assert docs[0].text.count("\n") == 5


# --- network: redirects, status, size --------------------------------------


def test_redirect_to_other_host_refused() -> None:
    handler = _HostRestrictedRedirect()
    req = Request("https://github.com/acme/docs/archive/x.tar.gz")
    for target in (
        "https://evil.example/x.tar.gz",
        "http://codeload.github.com/x.tar.gz",
        "https://github.com.evil.example/x",
    ):
        with pytest.raises(FetchError, match="disallowed host"):
            handler.redirect_request(req, io.BytesIO(), 302, "Found", HTTPMessage(), target)
    ok = handler.redirect_request(
        req, io.BytesIO(), 302, "Found", HTTPMessage(), "https://codeload.github.com/acme/docs/tar.gz/x"
    )
    assert ok is not None
    with pytest.raises(FetchError, match="disallowed host"):
        handler.redirect_request(
            req, io.BytesIO(), 302, "Found", HTTPMessage(), "https://us.aws.cdn.hf.co/x"
        )


def test_hf_redirect_outside_hf_co_refused() -> None:
    handler = _HostRestrictedRedirect(_hf_host_allowed)
    req = Request(f"https://huggingface.co/{MODEL}/resolve/{REVISION}/vocab.txt")
    for target in (
        "https://evilhf.co/x",
        "https://hf.co.evil.example/x",
        "https://evil.example/hf.co",
        "http://us.aws.cdn.hf.co/x",
        "https://github.com/x",
        "https://huggingface.co.evil.example/x",
    ):
        with pytest.raises(FetchError, match="disallowed host"):
            handler.redirect_request(req, io.BytesIO(), 302, "Found", HTTPMessage(), target)


def test_hf_redirect_to_cdn_allowed() -> None:
    handler = _HostRestrictedRedirect(_hf_host_allowed)
    req = Request(f"https://huggingface.co/{MODEL}/resolve/{REVISION}/vocab.txt")
    for target in ("https://us.aws.cdn.hf.co/repos/xx/file?sig=1", "https://huggingface.co/other/path"):
        assert handler.redirect_request(req, io.BytesIO(), 302, "Found", HTTPMessage(), target) is not None


def test_fetch_requests_only_the_archive_url_without_credentials() -> None:
    opener = FakeOpener(b"data")
    assert fetch_archive(SRC, opener=as_opener(opener)) == b"data"
    assert opener.urls == [f"https://github.com/{REPO}/archive/{COMMIT}.tar.gz"]


def test_non_200_raises_fetch_error() -> None:
    with pytest.raises(FetchError, match="404|status"):
        fetch_archive(SRC, opener=as_opener(FakeOpener(status=404)))
    err = urllib.error.HTTPError("u", 500, "boom", HTTPMessage(), None)
    with pytest.raises(FetchError, match="500"):
        fetch_archive(SRC, opener=as_opener(FakeOpener(error=err)))
    with pytest.raises(FetchError):
        fetch_archive(SRC, opener=as_opener(FakeOpener(error=urllib.error.URLError("down"))))
    with pytest.raises(FetchError):
        fetch_archive(SRC, opener=as_opener(FakeOpener(error=TimeoutError())))


def test_size_cap_enforced() -> None:
    with pytest.raises(FetchError, match="size cap"):
        fetch_archive(SRC, opener=as_opener(FakeOpener(b"x" * 11)), max_bytes=10)
    assert fetch_archive(SRC, opener=as_opener(FakeOpener(b"x" * 10)), max_bytes=10)


def test_default_network_is_blocked(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="network disabled"):
        fetch_archive(SRC)
    with pytest.raises(RuntimeError, match="network disabled"):
        download_model_file(EmbeddingParams(), "vocab.txt", tmp_path / "x", "0" * 64)


# --- the pinned model download ---------------------------------------------

ONNX_BYTES = b"pretend onnx graph"
VOCAB_BYTES = b"[PAD]\n[UNK]\n"


def _params() -> EmbeddingParams:
    return EmbeddingParams(
        model=MODEL,
        revision=REVISION,
        onnx_sha256=hashlib.sha256(ONNX_BYTES).hexdigest(),
        vocab_sha256=hashlib.sha256(VOCAB_BYTES).hexdigest(),
    )


def _model_opener() -> FakeOpener:
    return FakeOpener(routes={"/onnx/model.onnx": ONNX_BYTES, "/vocab.txt": VOCAB_BYTES})


def _cached(models: Path, params: EmbeddingParams) -> Path:
    base = models / MODEL.replace("/", "--") / REVISION
    (base / "onnx").mkdir(parents=True)
    (base / ONNX_FILE).write_bytes(ONNX_BYTES)
    (base / VOCAB_FILE).write_bytes(VOCAB_BYTES)
    return base


def test_model_download_requests_pinned_urls_and_caches(tmp_path: Path) -> None:
    opener = _model_opener()
    status = ensure_model_files(_params(), tmp_path / "models", opener=as_opener(opener))
    assert status == "downloaded"
    assert sorted(opener.urls) == sorted(
        [
            f"https://huggingface.co/{MODEL}/resolve/{REVISION}/onnx/model.onnx",
            f"https://huggingface.co/{MODEL}/resolve/{REVISION}/vocab.txt",
        ]
    )
    base = tmp_path / "models" / MODEL.replace("/", "--") / REVISION
    assert (base / ONNX_FILE).read_bytes() == ONNX_BYTES
    assert (base / VOCAB_FILE).read_bytes() == VOCAB_BYTES


def test_model_hash_mismatch_rejected_and_deleted(tmp_path: Path) -> None:
    params = _params()
    bad = FakeOpener(routes={"/onnx/model.onnx": b"tampered", "/vocab.txt": VOCAB_BYTES})
    models = tmp_path / "models"
    with pytest.raises(FetchError, match="pinned sha256"):
        ensure_model_files(params, models, opener=as_opener(bad))
    leftovers = [p for p in models.rglob("*") if p.is_file()]
    assert leftovers == []  # nothing kept, not even a partial file


def test_download_size_cap_and_status(tmp_path: Path) -> None:
    dest = tmp_path / "m" / "f.bin"
    with pytest.raises(FetchError, match="size cap"):
        download_model_file(_params(), "vocab.txt", dest, "0" * 64,
                            opener=as_opener(FakeOpener(b"x" * 11)), max_bytes=10)
    with pytest.raises(FetchError, match="status"):
        download_model_file(_params(), "vocab.txt", dest, "0" * 64, opener=as_opener(FakeOpener(status=503)))
    assert not dest.exists() and list(dest.parent.iterdir()) == []


def test_cached_model_skips_download(tmp_path: Path) -> None:
    params = _params()
    _cached(tmp_path / "models", params)
    opener = FakeOpener(error=RuntimeError("must not be called"))
    assert ensure_model_files(params, tmp_path / "models", opener=as_opener(opener)) == "cached"
    assert opener.urls == []


def test_cached_file_rehashed_before_use(tmp_path: Path) -> None:
    params = _params()
    base = _cached(tmp_path / "models", params)
    (base / ONNX_FILE).write_bytes(b"corrupted after download")
    # retrieve/eval path: re-hash before any ONNX session or vocab read; delete on mismatch
    with pytest.raises(ModelError, match="does not match"):
        OnnxEmbedder.load(tmp_path / "models", params)
    assert not (base / ONNX_FILE).exists()
    # ingest path: a mismatched cached file is replaced by a fresh, verified download
    (base / ONNX_FILE).parent.mkdir(exist_ok=True)
    (base / ONNX_FILE).write_bytes(b"corrupted again")
    opener = _model_opener()
    assert ensure_model_files(params, tmp_path / "models", opener=as_opener(opener)) == "downloaded"
    assert (base / ONNX_FILE).read_bytes() == ONNX_BYTES
    assert opener.urls == [f"https://huggingface.co/{MODEL}/resolve/{REVISION}/onnx/model.onnx"]


# --- the pinned reranker download ------------------------------------------

RR_REVISION = "d" * 40


def _rr_params() -> RerankParams:
    return RerankParams(
        model="acme/tiny-rerank",
        revision=RR_REVISION,
        onnx_sha256=hashlib.sha256(ONNX_BYTES).hexdigest(),
        vocab_sha256=hashlib.sha256(VOCAB_BYTES).hexdigest(),
    )


def _rr_cached(models: Path, params: RerankParams) -> Path:
    base = reranker_dir(models, params)
    (base / "onnx").mkdir(parents=True)
    (base / ONNX_FILE).write_bytes(ONNX_BYTES)
    (base / VOCAB_FILE).write_bytes(VOCAB_BYTES)
    return base


def test_reranker_download_requests_pinned_urls_and_caches(tmp_path: Path) -> None:
    params = _rr_params()
    opener = _model_opener()
    assert ensure_reranker_files(params, tmp_path / "models", opener=as_opener(opener)) == "downloaded"
    assert sorted(opener.urls) == sorted(
        [
            f"https://huggingface.co/acme/tiny-rerank/resolve/{RR_REVISION}/onnx/model.onnx",
            f"https://huggingface.co/acme/tiny-rerank/resolve/{RR_REVISION}/vocab.txt",
        ]
    )
    base = reranker_dir(tmp_path / "models", params)
    assert (base / ONNX_FILE).read_bytes() == ONNX_BYTES and (base / VOCAB_FILE).read_bytes() == VOCAB_BYTES
    again = FakeOpener(error=RuntimeError("must not be called"))
    assert ensure_reranker_files(params, tmp_path / "models", opener=as_opener(again)) == "cached"
    assert again.urls == []


def test_reranker_revision_must_be_40_hex_for_download() -> None:
    with pytest.raises(ValueError, match="40-hex"):
        RerankParams(revision="main")


def test_reranker_hash_mismatch_rejected_and_deleted(tmp_path: Path) -> None:
    bad = FakeOpener(routes={"/onnx/model.onnx": b"tampered", "/vocab.txt": VOCAB_BYTES})
    models = tmp_path / "models"
    with pytest.raises(FetchError, match="pinned sha256"):
        ensure_reranker_files(_rr_params(), models, opener=as_opener(bad))
    assert [p for p in models.rglob("*") if p.is_file()] == []
    assert main(["ingest", "--config", str(tmp_path / "missing.toml")]) == 2


def test_reranker_cached_file_rehashed_before_use(tmp_path: Path) -> None:
    params = _rr_params()
    base = _rr_cached(tmp_path / "models", params)
    (base / ONNX_FILE).write_bytes(b"corrupted after download")
    with pytest.raises(ModelError, match="does not match"):
        OnnxReranker.load(tmp_path / "models", params)
    assert not (base / ONNX_FILE).exists()
    (base / ONNX_FILE).write_bytes(b"corrupted again")
    opener = _model_opener()
    assert ensure_reranker_files(params, tmp_path / "models", opener=as_opener(opener)) == "downloaded"
    assert (base / ONNX_FILE).read_bytes() == ONNX_BYTES


def test_reranker_redirect_outside_hf_co_refused() -> None:
    handler = _HostRestrictedRedirect(_hf_host_allowed)
    req = Request(f"https://huggingface.co/acme/tiny-rerank/resolve/{RR_REVISION}/onnx/model.onnx")
    for target in ("https://evilhf.co/x", "https://hf.co.evil.example/x", "http://us.aws.cdn.hf.co/x"):
        with pytest.raises(FetchError, match="disallowed host"):
            handler.redirect_request(req, io.BytesIO(), 302, "Found", HTTPMessage(), target)
    assert handler.redirect_request(
        req, io.BytesIO(), 302, "Found", HTTPMessage(), "https://us.aws.cdn.hf.co/repos/x"
    ) is not None


def _record(calls: list[str], name: str, result: object) -> Callable[..., object]:
    def inner(*args: object, **kwargs: object) -> object:
        calls.append(name)
        return result

    return inner


class _Closable(FakeEmbedder):
    def __init__(self, calls: list[str], name: str) -> None:
        super().__init__()
        self.calls, self.name = calls, name

    def close(self) -> None:
        self.calls.append(f"close-{self.name}")


def _no_reranker(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> object:
        raise AssertionError("the reranker must not be fetched or loaded on the default path")

    monkeypatch.setattr("aveto_support.ingest.ensure_reranker_files", fail)
    monkeypatch.setattr("aveto_support.ingest.OnnxReranker.load", fail)


def test_default_ingest_fetches_no_reranker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr("aveto_support.ingest.ensure_model_files", _record(calls, "fetch-embed", "cached"))
    monkeypatch.setattr("aveto_support.ingest.OnnxEmbedder.load", _record(calls, "load-embed", _Closable(calls, "embed")))
    _no_reranker(monkeypatch)
    cfg = _cfg(tmp_path, _base())
    opener = FakeOpener(make_archive(DOCS))
    report = run_ingest(cfg, tmp_path / "i.json", opener=as_opener(opener), models_dir=tmp_path / "models")
    assert calls == ["fetch-embed", "load-embed", "close-embed"] and report.reranker_status == "not fetched"


def test_default_ingest_cli_line_says_not_fetched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _no_reranker(monkeypatch)
    cfg = _cfg(tmp_path, _base())
    monkeypatch.setattr(
        "aveto_support.ingest.fetch_archive", lambda *a, **k: make_archive(DOCS)
    )
    assert main(["ingest", "--config", str(cfg), "--out", str(tmp_path / "i.json")], embedder=FAKE) == 0
    assert "reranker files: not fetched" in capsys.readouterr().out


def test_default_ingest_makes_no_reranker_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    opener = _model_opener()
    monkeypatch.setattr("aveto_support.ingest.OnnxEmbedder.load", lambda *a, **k: _Closable([], "e"))
    p = _params()
    embedding = (
        f'[embedding]\nmodel = "{MODEL}"\nrevision = "{REVISION}"\n'
        f'onnx_sha256 = "{p.onnx_sha256}"\nvocab_sha256 = "{p.vocab_sha256}"\n'
    )
    cfg = _cfg(tmp_path, _base(), embedding=embedding)
    run_ingest(
        cfg, tmp_path / "i.json", opener=as_opener(FakeOpener(make_archive(DOCS))),
        model_opener=as_opener(opener), models_dir=tmp_path / "models",
    )
    assert opener.urls and not any("cross-encoder/ms-marco-MiniLM-L6-v2" in u for u in opener.urls)


def test_ingest_with_reranker_fetches_and_rehashes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr("aveto_support.ingest.ensure_reranker_files", _record(calls, "fetch-rr", "downloaded"))
    monkeypatch.setattr(
        "aveto_support.ingest.OnnxReranker.load", _record(calls, "load-rr", _Closable(calls, "rr"))
    )
    cfg = _cfg(tmp_path, _base())
    report = run_ingest(
        cfg, tmp_path / "i.json", opener=as_opener(FakeOpener(make_archive(DOCS))),
        models_dir=tmp_path / "models", embedder=FAKE, with_reranker=True,
    )
    assert calls == ["fetch-rr", "load-rr", "close-rr"] and report.reranker_status == "downloaded"


def test_reranker_opt_in_does_not_change_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = _cfg(tmp_path, _base())
    opener = FakeOpener(make_archive(DOCS))
    off = _ingest(cfg, tmp_path / "off.json", opener, tmp_path)
    calls: list[str] = []
    monkeypatch.setattr("aveto_support.ingest.ensure_reranker_files", _record(calls, "fetch-rr", "cached"))
    monkeypatch.setattr(
        "aveto_support.ingest.OnnxReranker.load", _record(calls, "load-rr", _Closable(calls, "rr"))
    )
    on = run_ingest(
        cfg, tmp_path / "on.json", opener=as_opener(opener), models_dir=tmp_path / "models",
        embedder=FAKE, with_reranker=True,
    )
    assert calls and (tmp_path / "off.json").read_bytes() == (tmp_path / "on.json").read_bytes()
    assert off.sha256 == on.sha256


def test_ingest_closes_embedder_it_loaded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr("aveto_support.ingest.ensure_model_files", _record(calls, "fetch-embed", "cached"))
    monkeypatch.setattr(
        "aveto_support.ingest.OnnxEmbedder.load", _record(calls, "load-embed", _Closable(calls, "embed"))
    )
    cfg = _cfg(tmp_path, _base())
    run_ingest(
        cfg, tmp_path / "i.json", opener=as_opener(FakeOpener(make_archive(DOCS))),
        models_dir=tmp_path / "models",
    )
    assert calls == ["fetch-embed", "load-embed", "close-embed"]
    calls.clear()
    injected = _Closable(calls, "inj")
    run_ingest(
        cfg, tmp_path / "j.json", opener=as_opener(FakeOpener(make_archive(DOCS))),
        models_dir=tmp_path / "models", embedder=injected,
    )
    assert calls == []  # the caller owns an injected embedder


def test_retrieve_is_offline_with_cached_reranker(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # The autouse fixture blocks every socket for this test; a connection would raise RuntimeError.
    cfg = _cfg(tmp_path, _base())
    out = tmp_path / "i.json"
    _ingest(cfg, out, FakeOpener(make_archive(DOCS)), tmp_path)
    question = "Usage Launch the widget from the menu."
    assert main(["retrieve", "--index", str(out), "--ranking", "file-rerank-v1", question], embedder=FAKE, reranker=FakeReranker()) == 0
    assert "Ranking: file-rerank-v1" in capsys.readouterr().out


@pytest.mark.network
def test_live_reranker_download_verifies_hashes(tmp_path: Path) -> None:
    params = RerankParams()
    assert ensure_reranker_files(params, tmp_path / "models") == "downloaded"
    base = reranker_dir(tmp_path / "models", params)
    assert (base / ONNX_FILE).stat().st_size == 91_011_230
    assert (base / VOCAB_FILE).stat().st_size == 231_508
    assert ensure_reranker_files(params, tmp_path / "models") == "cached"


# --- ingest ----------------------------------------------------------------


def test_ingest_is_byte_identical(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base())
    opener = FakeOpener(make_archive(DOCS))
    r1 = _ingest(cfg, tmp_path / "one" / "i.json", opener, tmp_path)
    r2 = _ingest(cfg, tmp_path / "two" / "i.json", opener, tmp_path)
    assert (tmp_path / "one" / "i.json").read_bytes() == (tmp_path / "two" / "i.json").read_bytes()
    assert r1.sha256 == r2.sha256
    assert r1.files_indexed == len(DOCS) and r1.passages > 0
    assert 0.0 <= r1.threshold <= 1.0
    assert load_index(tmp_path / "one" / "i.json").passages[0].embedding


def test_ingest_is_byte_identical_under_member_reordering(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base())
    names = list(DOCS)
    random.Random(1).shuffle(names)
    shuffled = {n: DOCS[n] for n in names}
    assert names != list(DOCS)
    r1 = _ingest(cfg, tmp_path / "a.json", FakeOpener(make_archive(DOCS)), tmp_path)
    r2 = _ingest(cfg, tmp_path / "b.json", FakeOpener(make_archive(shuffled)), tmp_path)
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()
    assert r1.sha256 == r2.sha256


def test_small_corpus_warns_and_fails_closed(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base(include='include = ["README.md"]\n'))
    report = _ingest(cfg, tmp_path / "i.json", FakeOpener(make_archive({"README.md": b"# A\nx y\n"})), tmp_path)
    assert report.threshold == 1_000_000.0
    assert any("fewer than 5" in w for w in report.warnings)


def test_no_offtopic_list_warns_and_uses_salad(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base())
    report = _ingest(cfg, tmp_path / "i.json", FakeOpener(make_archive(DOCS)), tmp_path)
    assert report.tau_offtopic is None and report.threshold == report.tau_salad
    assert any("off-topic" in w and "too permissive" in w for w in report.warnings)


def _offtopic_config(tmp_path: Path, questions: list[str], sha: str | None = None) -> Path:
    body = 'pinned_commit = "' + COMMIT + '"\n' + "".join(
        f'[[question]]\nid = "o{i}"\nquestion = "{q}"\n' for i, q in enumerate(questions)
    )
    (tmp_path / "offtopic.toml").write_text(body)
    digest = sha or hashlib.sha256(body.encode()).hexdigest()
    extra = f'offtopic_path = "offtopic.toml"\nofftopic_sha256 = "{digest}"\n'
    return _cfg(tmp_path, _base(), EMBEDDING_TOML + extra)


def test_offtopic_list_calibrates_and_is_recorded(tmp_path: Path) -> None:
    questions = ["alpha gizmo details", "widget project menu", "quantum spaceship", "lunar module", "opera"]
    cfg = _offtopic_config(tmp_path, questions)
    out = tmp_path / "i.json"
    report = _ingest(cfg, out, FakeOpener(make_archive(DOCS)), tmp_path)
    assert report.tau_offtopic is not None
    assert report.threshold == max(report.tau_salad, report.tau_offtopic)
    assert any("5 questions" in w for w in report.warnings)
    doc = json.loads(out.read_text())
    assert doc["params"]["embedding"]["offtopic_sha256"] == hashlib.sha256(
        (tmp_path / "offtopic.toml").read_bytes()
    ).hexdigest()
    assert doc["calibration"]["tau_offtopic"] == report.tau_offtopic
    assert doc["calibration"]["method"] == "cross-file-null-v3+offtopic-v1"


def test_offtopic_list_hash_mismatch_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cfg = _offtopic_config(tmp_path, ["one", "two"], sha="9" * 64)
    out = tmp_path / "i.json"
    code = main(["ingest", "--config", str(cfg), "--out", str(out)], embedder=FAKE, models_dir=tmp_path / "m")
    assert code == 2 and not out.exists()
    err = capsys.readouterr().err
    assert "off-topic list" in err and "pinned sha256" in err


def test_failed_ingest_leaves_previous_index(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base())
    out = tmp_path / "i.json"
    _ingest(cfg, out, FakeOpener(make_archive(DOCS)), tmp_path)
    before = out.read_bytes()
    with pytest.raises(FetchError):
        _ingest(cfg, out, FakeOpener(status=503), tmp_path)
    assert out.read_bytes() == before


def test_index_carries_no_timestamps_or_absolute_paths(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base())
    _ingest(cfg, tmp_path / "i.json", FakeOpener(make_archive(DOCS)), tmp_path)
    text = (tmp_path / "i.json").read_text()
    assert str(tmp_path) not in text
    assert set(json.loads(text)) == {"schema", "source", "params", "calibration", "counts", "skipped", "passages"}


def test_truncated_passages_are_counted(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, _base())
    long_body = ("word " * 600).encode()
    files = {**DOCS, "notes/long.md": b"# Long\n" + long_body + b"\n"}
    report = _ingest(cfg, tmp_path / "i.json", FakeOpener(make_archive(files)), tmp_path)
    assert report.truncated_for_embedding == 1


def test_retrieve_is_offline_with_cached_model(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # The autouse fixture blocks every socket for this test; a connection would raise RuntimeError.
    cfg = _cfg(tmp_path, _base())
    out = tmp_path / "i.json"
    _ingest(cfg, out, FakeOpener(make_archive(DOCS)), tmp_path)
    question = "Usage Launch the widget from the menu."
    assert main(["retrieve", "--index", str(out), "--ranking", "file-rerank-v1", question], embedder=FAKE, reranker=FakeReranker()) == 0
    assert "guide/usage.md" in capsys.readouterr().out


def test_retrieve_without_cached_model_exits_2_and_never_downloads(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    idx = Index(REPO, COMMIT, 0, (), (), 0.5, RetrievalParams())
    out = tmp_path / "i.json"
    write_index(idx, out)
    assert main(["retrieve", "--index", str(out), "anything"], models_dir=tmp_path / "none") == 2
    assert "run ingest" in capsys.readouterr().err


@pytest.mark.network
def test_live_model_download_verifies_hashes(tmp_path: Path) -> None:
    root = Path(__file__).parent.parent
    cfg = load_source_config(root / "docs-source.toml")
    assert ensure_model_files(cfg.embedding, tmp_path / "models") == "downloaded"
    base = tmp_path / "models" / cfg.embedding.model.replace("/", "--") / cfg.embedding.revision
    assert (base / ONNX_FILE).stat().st_size == 133_093_490
    assert (base / VOCAB_FILE).stat().st_size == 231_508
    assert ensure_model_files(cfg.embedding, tmp_path / "models") == "cached"


@pytest.mark.network
def test_live_ingest_byte_identical() -> None:
    root = Path(__file__).parent.parent
    out = root / "index" / "test-live.json"
    try:
        first = run_ingest(root / "docs-source.toml", out, models_dir=root / "models")
        second = run_ingest(root / "docs-source.toml", out, models_dir=root / "models")
        assert first.sha256 == second.sha256
        assert first.files_indexed > 0 and first.passages > 0
        cfg = load_source_config(root / "docs-source.toml")
        indexed = {p.path for p in load_index(out).passages}
        assert all(
            any(path.startswith(e) if e.endswith("/") else path == e for e in cfg.include)
            for path in indexed
        )
    finally:
        out.unlink(missing_ok=True)


# --- the pinned answerability judge ----------------------------------------

JD_REVISION = "e" * 40


def _jd_params() -> JudgeParams:
    return JudgeParams(
        model="acme/tiny-judge",
        revision=JD_REVISION,
        onnx_sha256=hashlib.sha256(ONNX_BYTES).hexdigest(),
        vocab_sha256=hashlib.sha256(VOCAB_BYTES).hexdigest(),
    )


def test_default_ingest_fetches_and_rehashes_judge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    seen: list[object] = []

    def fetch(params: object, *a: object, **k: object) -> str:
        seen.append(params)
        calls.append("fetch-judge")
        return "downloaded"

    monkeypatch.setattr("aveto_support.ingest.ensure_judge_files", fetch)
    monkeypatch.setattr(
        "aveto_support.ingest.OnnxJudge.load", _record(calls, "load-judge", _Closable(calls, "judge"))
    )
    report = run_ingest(
        _cfg(tmp_path, _base()), tmp_path / "i.json", opener=as_opener(FakeOpener(make_archive(DOCS))),
        models_dir=tmp_path / "models", embedder=FAKE,
    )
    assert calls == ["fetch-judge", "load-judge", "close-judge"] and report.judge_status == "downloaded"
    assert seen == [JudgeParams()]  # the pinned default, on every ingest (no flag)
    params = _jd_params()
    opener = _model_opener()
    assert ensure_judge_files(params, tmp_path / "m2", opener=as_opener(opener)) == "downloaded"
    assert sorted(opener.urls) == sorted(
        [
            f"https://huggingface.co/acme/tiny-judge/resolve/{JD_REVISION}/onnx/model.onnx",
            f"https://huggingface.co/acme/tiny-judge/resolve/{JD_REVISION}/vocab.txt",
        ]
    )
    base = judge_dir(tmp_path / "m2", params)
    assert (base / ONNX_FILE).read_bytes() == ONNX_BYTES and (base / VOCAB_FILE).read_bytes() == VOCAB_BYTES
    again = FakeOpener(error=RuntimeError("must not be called"))
    assert ensure_judge_files(params, tmp_path / "m2", opener=as_opener(again)) == "cached"
    assert again.urls == []


def test_judge_hash_mismatch_rejected_and_deleted(tmp_path: Path) -> None:
    bad = FakeOpener(routes={"/onnx/model.onnx": b"tampered", "/vocab.txt": VOCAB_BYTES})
    models = tmp_path / "models"
    with pytest.raises(FetchError, match="pinned sha256"):
        ensure_judge_files(_jd_params(), models, opener=as_opener(bad))
    assert [p for p in models.rglob("*") if p.is_file()] == []


def test_judge_redirect_outside_hf_co_refused() -> None:
    handler = _HostRestrictedRedirect(_hf_host_allowed)
    req = Request(f"https://huggingface.co/acme/tiny-judge/resolve/{JD_REVISION}/onnx/model.onnx")
    for target in ("https://evilhf.co/x", "https://hf.co.evil.example/x", "http://us.aws.cdn.hf.co/x"):
        with pytest.raises(FetchError, match="disallowed host"):
            handler.redirect_request(req, io.BytesIO(), 302, "Found", HTTPMessage(), target)
    assert handler.redirect_request(
        req, io.BytesIO(), 302, "Found", HTTPMessage(), "https://us.aws.cdn.hf.co/repos/x"
    ) is not None


def test_retrieve_is_offline_with_cached_judge(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # The autouse fixture blocks every socket for this test; a connection would raise RuntimeError.
    cfg = _cfg(tmp_path, _base())
    out = tmp_path / "i.json"
    _ingest(cfg, out, FakeOpener(make_archive(DOCS)), tmp_path)
    question = "Usage Launch the widget from the menu."
    assert main(["retrieve", "--index", str(out), question], embedder=FAKE, judge=FakeJudge(1.0)) == 0
    text = capsys.readouterr().out
    assert "guide/usage.md" in text and "Judge: answers" in text
    assert main(["retrieve", "--index", str(out), question], embedder=FAKE) == 0  # judge loaded from cache
    assert "Judge: answers" in capsys.readouterr().out


def test_index_bytes_unchanged_by_judge_fetch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = _cfg(tmp_path, _base())
    opener = FakeOpener(make_archive(DOCS))
    outs = []
    for status in ("downloaded", "cached"):
        monkeypatch.setattr("aveto_support.ingest.ensure_judge_files", lambda *a, _s=status, **k: _s)
        path = tmp_path / f"{status}.json"
        run_ingest(cfg, path, opener=as_opener(opener), models_dir=tmp_path / "models", embedder=FAKE)
        outs.append(path.read_bytes())
    assert outs[0] == outs[1]


def test_ingest_cli_prints_judge_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("aveto_support.ingest.fetch_archive", lambda *a, **k: make_archive(DOCS))
    cfg = _cfg(tmp_path, _base())
    assert main(["ingest", "--config", str(cfg), "--out", str(tmp_path / "i.json")], embedder=FAKE) == 0
    assert "judge files: cached (sha256 verified before use)" in capsys.readouterr().out


def test_judge_cached_file_rehashed_before_use_ingest_path(tmp_path: Path) -> None:
    params = _jd_params()
    base = judge_dir(tmp_path / "models", params)
    (base / "onnx").mkdir(parents=True)
    (base / ONNX_FILE).write_bytes(b"corrupted")
    (base / VOCAB_FILE).write_bytes(VOCAB_BYTES)
    opener = _model_opener()
    assert ensure_judge_files(params, tmp_path / "models", opener=as_opener(opener)) == "downloaded"
    assert (base / ONNX_FILE).read_bytes() == ONNX_BYTES
    assert opener.urls == [f"https://huggingface.co/acme/tiny-judge/resolve/{JD_REVISION}/onnx/model.onnx"]
    assert OnnxJudge is not None
