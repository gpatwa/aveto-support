from __future__ import annotations

import io
import json
import random
import tarfile
import urllib.error
from http.client import HTTPMessage
from pathlib import Path
from urllib.request import Request

import pytest
from conftest import COMMIT, REPO, FakeOpener, as_opener, make_archive

from aveto_support.ingest import (
    ConfigError,
    FetchError,
    SourceConfig,
    _HostRestrictedRedirect,
    fetch_archive,
    load_source_config,
    read_markdown,
    run_ingest,
)

SRC = SourceConfig(REPO, COMMIT)

DOCS = {
    "README.md": b"# Home\nWelcome to the widget project.\n",
    "guide/setup.md": b"# Setup\n## Install\nRun the installer program.\n## Configure\nEdit the config file.\n",
    "guide/usage.md": b"# Usage\nLaunch the widget from the menu.\n",
    "notes/a.md": b"# Alpha\nAlpha gizmo details.\n",
    "notes/b.md": b"# Beta\nBeta sprocket details.\n",
    "notes/c.md": b"# Gamma\nGamma cog details.\n",
}


def _cfg(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "src.toml"
    path.write_text(body)
    return path


def test_load_config_valid(tmp_path: Path) -> None:
    cfg = load_source_config(_cfg(tmp_path, f'repo = "{REPO}"\ncommit = "{COMMIT}"\nexclude = ["drafts/"]\n'))
    assert cfg == SourceConfig(REPO, COMMIT, ("drafts/",))


def test_committed_config_is_valid() -> None:
    cfg = load_source_config(Path(__file__).parent.parent / "docs-source.toml")
    assert len(cfg.commit) == 40


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
        load_source_config(_cfg(tmp_path, f'repo = "{REPO}"\ncommit = "{COMMIT}"\nbranch = "x"\n'))


def test_exclude_dotdot_rejected(tmp_path: Path) -> None:
    for bad in ('"../x"', '"/abs"', '"a/../b"'):
        with pytest.raises(ConfigError):
            load_source_config(_cfg(tmp_path, f'repo = "{REPO}"\ncommit = "{COMMIT}"\nexclude = [{bad}]\n'))


def test_read_markdown_keeps_only_md_regular_files() -> None:
    link = tarfile.TarInfo(f"docs-{COMMIT}/link.md")
    link.type = tarfile.SYMTYPE
    link.linkname = "README.md"
    sneaky = tarfile.TarInfo(f"docs-{COMMIT}/../escape.md")
    sneaky.size = 0
    files = {"a.md": b"# A\nx\n", "b.txt": b"# no\n", "UP.MD": b"# Up\ny\n"}
    archive = make_archive(files, extra_members=[link, sneaky])
    docs, skipped = read_markdown(archive, SRC)
    assert [d.path for d in docs] == ["UP.MD", "a.md"]
    assert skipped == []


def test_read_markdown_strips_top_dir_and_sorts() -> None:
    archive = make_archive({"z.md": b"# Z\n1\n", "a/b.md": b"# B\n2\n", "a.md": b"# A\n3\n"})
    docs, _ = read_markdown(archive, SRC)
    assert [d.path for d in docs] == ["a.md", "a/b.md", "z.md"]


def test_exclude_prefix_honoured() -> None:
    archive = make_archive({"drafts/x.md": b"# X\n1\n", "keep.md": b"# K\n2\n"})
    docs, _ = read_markdown(archive, SourceConfig(REPO, COMMIT, ("drafts/",)))
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
    docs, skipped = read_markdown(archive, SRC)
    assert skipped == [("bad.md", "not utf-8")]
    assert docs[0].text == "# Ok\nfine\n"


def test_crlf_normalised_line_count_preserved() -> None:
    raw = b"# A\r\nb\r\n\r\nc\rd\r\n"
    docs, _ = read_markdown(make_archive({"a.md": raw}), SRC)
    assert "\r" not in docs[0].text
    assert docs[0].text.count("\n") == 5


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


def test_default_network_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="network disabled"):
        fetch_archive(SRC)


def _setup_ingest(tmp_path: Path, files: dict[str, bytes]) -> tuple[Path, FakeOpener]:
    cfg = _cfg(tmp_path, f'repo = "{REPO}"\ncommit = "{COMMIT}"\n')
    return cfg, FakeOpener(make_archive(files))


def test_ingest_is_byte_identical(tmp_path: Path) -> None:
    cfg, opener = _setup_ingest(tmp_path, DOCS)
    r1 = run_ingest(cfg, tmp_path / "one" / "i.json", opener=as_opener(opener))
    r2 = run_ingest(cfg, tmp_path / "two" / "i.json", opener=as_opener(opener))
    assert (tmp_path / "one" / "i.json").read_bytes() == (tmp_path / "two" / "i.json").read_bytes()
    assert r1.sha256 == r2.sha256
    assert r1.files_indexed == len(DOCS) and r1.passages > 0
    assert 0.0 <= r1.threshold <= 1.0


def test_ingest_is_byte_identical_under_member_reordering(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, f'repo = "{REPO}"\ncommit = "{COMMIT}"\n')
    names = list(DOCS)
    random.Random(1).shuffle(names)
    shuffled = {n: DOCS[n] for n in names}
    assert names != list(DOCS)
    r1 = run_ingest(cfg, tmp_path / "a.json", opener=as_opener(FakeOpener(make_archive(DOCS))))
    r2 = run_ingest(cfg, tmp_path / "b.json", opener=as_opener(FakeOpener(make_archive(shuffled))))
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()
    assert r1.sha256 == r2.sha256


def test_small_corpus_warns_and_fails_closed(tmp_path: Path) -> None:
    cfg, opener = _setup_ingest(tmp_path, {"a.md": b"# A\nx y\n"})
    report = run_ingest(cfg, tmp_path / "i.json", opener=as_opener(opener))
    assert report.threshold == 1.0
    assert report.warnings


def test_index_carries_no_timestamps_or_absolute_paths(tmp_path: Path) -> None:
    cfg, opener = _setup_ingest(tmp_path, DOCS)
    run_ingest(cfg, tmp_path / "i.json", opener=as_opener(opener))
    text = (tmp_path / "i.json").read_text()
    assert str(tmp_path) not in text
    assert set(json.loads(text)) == {"schema", "source", "params", "calibration", "counts", "skipped", "passages"}


def test_failed_ingest_leaves_previous_index(tmp_path: Path) -> None:
    cfg, opener = _setup_ingest(tmp_path, DOCS)
    out = tmp_path / "i.json"
    run_ingest(cfg, out, opener=as_opener(opener))
    before = out.read_bytes()
    with pytest.raises(FetchError):
        run_ingest(cfg, out, opener=as_opener(FakeOpener(status=503)))
    assert out.read_bytes() == before


@pytest.mark.network
def test_live_fetch_pinned_commit(tmp_path: Path) -> None:
    root = Path(__file__).parent.parent
    out = tmp_path / "live.json"
    first = run_ingest(root / "docs-source.toml", out)
    second = run_ingest(root / "docs-source.toml", out)
    assert first.sha256 == second.sha256
    assert first.files_indexed > 0 and first.passages > 0
    import tomllib

    with (root / "evals" / "retrieval.toml").open("rb") as handle:
        eval_doc = tomllib.load(handle)
    indexed = {p["path"] for p in json.loads(out.read_text())["passages"]}
    wanted = {s for q in eval_doc["question"] for s in q.get("sources", [])}
    assert wanted <= indexed
