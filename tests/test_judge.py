from __future__ import annotations

import ast
import hashlib
import os
import re
import socket
import subprocess
from pathlib import Path

import pytest
from conftest import COMMIT, REPO, FakeEmbedder, FakeReranker, embed_all

from aveto_support import judge
from aveto_support.__main__ import main
from aveto_support.index import Index, RetrievalParams, split_passages, write_index
from aveto_support.search import Searcher, retrieve

FAKE = FakeEmbedder()
APPROVED_PROMPT_SHA256 = "24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427"
ROOT = Path(__file__).parent.parent

LONG_LINE = "w" * 200
DOCS = {
    "pets/cats.md": (
        "Preface about cats.\n\n# Cats\nCats purr and chase mice.\nline two\nline three\n"
        f"line four\n{LONG_LINE}\n"
    ),
    "pets/dogs.md": "# Dogs\nDogs bark and fetch sticks.\n",
    "farm/cows.md": "# Cows\nCows graze in meadows.\n",
    "farm/hens.md": "# Hens\nHens lay eggs daily.\n",
    "sea/whales.md": "# Whales\nWhales sing under water.\n",
    "sea/crabs.md": "# Crabs\nCrabs scuttle sideways.\n",
    "zzz/last.md": "# Last\nNothing about animals lives here.\n",
}
TWO_DOCS = {
    "a/one.md": "Preface line.\n\n# Alpha\nAlpha text here.\nmore\n\n## Sub\nsub text\n",
    "b/two.md": "# Beta\nBeta text here.\n",
}
QUESTION = "do cats purr"


def make_index(docs: dict[str, str], *, threshold: float = 0.3) -> Index:
    passages = []
    for path, text in docs.items():
        passages.extend(split_passages(path, text))
    passages.sort(key=lambda p: (p.path, p.line_start))
    return Index(REPO, COMMIT, len(docs), (), tuple(embed_all(passages)), threshold, RetrievalParams())


def write_idx(tmp_path: Path, docs: dict[str, str] | None = None) -> Path:
    path = tmp_path / "i.json"
    write_index(make_index(DOCS if docs is None else docs), path)
    return path


@pytest.fixture
def work(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A working directory holding an index and a `.aveto-judge/` transport directory."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".aveto-judge").mkdir()
    write_idx(tmp_path)
    return tmp_path


def verdicts_file(
    directory: Path,
    eval_file: Path,
    verdicts: dict[str, str],
    *,
    index: Path | None = None,
    name: str = "v.toml",
    prompt_sha: str = APPROVED_PROMPT_SHA256,
    fmt: str = "aveto-judge-verdicts-v1",
    hashes: dict[str, str] | None = None,
    extra: str = "",
) -> Path:
    """A well-formed verdicts file (hashes recomputed from the index) unless overridden."""
    from aveto_support.evaluate import load_eval_set
    from aveto_support.index import load_index
    from aveto_support.judge_eval import build_results

    eval_set = load_eval_set(eval_file)
    results = build_results(Searcher(load_index(index or directory / "i.json"), FAKE), eval_set)
    lines = [f'format = "{fmt}"', f'prompt_sha256 = "{prompt_sha}"', extra]
    for qid, token in verdicts.items():
        digest = (hashes or {}).get(qid) or judge.input_sha256(judge.format_judge_input(results[qid]))
        lines.append(f'[[verdict]]\nid = "{qid}"\nverdict = "{token}"\ninput_sha256 = "{digest}"')
    path = directory / name
    path.write_text("\n".join(lines) + "\n")
    return path


class Out:
    def __init__(self, code: int, out: str, err: str) -> None:
        self.code, self.out, self.err = code, out, err


def run(capsys: pytest.CaptureFixture[str], argv: list[str], idx: Path | None = None) -> Out:
    capsys.readouterr()
    full = list(argv)
    if argv[0] in ("retrieve", "eval", "judge-input", "judge-apply") and "--index" not in argv:
        full[1:1] = ["--index", str(idx if idx is not None else Path("i.json"))]
    code = main(full, embedder=FAKE, reranker=FakeReranker())
    got = capsys.readouterr()
    return Out(code, got.out, got.err)


def ask(work: Path, capsys: pytest.CaptureFixture[str], question: str = QUESTION) -> tuple[str, str]:
    """judge-input via the question file; returns (payload, hash from stderr)."""
    (work / ".aveto-judge" / "question.txt").write_text(question, encoding="utf-8")
    r = run(capsys, ["judge-input", "--question-file", ".aveto-judge/question.txt"])
    assert r.code == 0
    m = re.fullmatch(r"input sha256: ([0-9a-f]{64})\n", r.err)
    assert m is not None
    return r.out, m.group(1)


def apply(
    work: Path,
    capsys: pytest.CaptureFixture[str],
    reply: bytes,
    digest: str,
    *,
    verdict: str = ".aveto-judge/reply.txt",
) -> Out:
    target = work / verdict
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(reply)
    return run(
        capsys,
        [
            "judge-apply",
            "--question-file",
            ".aveto-judge/question.txt",
            "--input-sha256",
            digest,
            "--verdict-file",
            verdict,
        ],
    )


def transport_left(work: Path) -> list[str]:
    return sorted(p.name for p in (work / ".aveto-judge").iterdir())


# --- payload -----------------------------------------------------------------


def test_judge_input_layout_exact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                  capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.chdir(tmp_path)
    idx = write_idx(tmp_path, TWO_DOCS)
    r = run(capsys, ["judge-input", "alpha", "preface"], idx)
    assert r.code == 0
    assert r.out == (
        "=== Q1 ===\n"
        "Question: alpha preface\n"
        "\n"
        "File 1: a/one.md\n"
        "--- passage 1a | heading: (top of file) | lines 1-1 ---\n"
        "Preface line.\n"
        "--- end passage 1a ---\n"
        "\n"
        "--- passage 1b | heading: Alpha | lines 3-5 ---\n"
        "# Alpha\nAlpha text here.\nmore\n"
        "--- end passage 1b ---\n"
        "\n"
        "File 2: b/two.md\n"
        "--- passage 2a | heading: Beta | lines 1-2 ---\n"
        "# Beta\nBeta text here.\n"
        "--- end passage 2a ---\n"
        "\n"
        "=== end Q1 ===\n"
    )


def test_judge_input_full_text_not_excerpt(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    block, _ = ask(work, capsys)
    assert "line four\n" + LONG_LINE + "\n" in block
    assert "      | " not in block and "…" not in block


def test_judge_input_matches_retrieve_selection(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    block, _ = ask(work, capsys)
    result = retrieve(Searcher(make_index(DOCS), FAKE), QUESTION)
    files = re.findall(r"^File (\d+): (.+)$", block, flags=re.MULTILINE)
    assert files == [(str(f.rank), f.path) for f in result.files]
    passages = re.findall(r"^--- passage (\d+)([a-z]) \| heading: .* \| lines (\d+)-(\d+) ---$", block, flags=re.MULTILINE)
    expected = [
        (str(f.rank), letter, str(m.passage.line_start), str(m.passage.line_end))
        for f in result.files
        for letter, m in zip("abcdefghij", f.passages, strict=False)
    ]
    assert passages == expected
    for f in result.files:
        for m in f.passages:
            assert m.passage.text in block


def test_judge_input_has_no_scores_urls_labels(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    block, _ = ask(work, capsys)
    for banned in ("score", "http", COMMIT, "Ranking", "Sources for", "Docs:", "These are sources",
                   "reference", "ANSWERABLE", REPO):
        assert banned not in block, banned


def test_judge_input_deterministic_and_hash_on_stderr(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    first = run(capsys, ["judge-input", QUESTION])
    second = run(capsys, ["judge-input", QUESTION])
    assert first.code == second.code == 0
    assert first.out == second.out and first.err == second.err
    assert first.err == f"input sha256: {hashlib.sha256(first.out.encode()).hexdigest()}\n"
    assert first.out.endswith("\n") and not first.out.endswith("\n\n")


def test_question_normalised(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert judge.normalise_question("  do\tcats \n\n purr  ") == "do cats purr"
    block, _ = ask(work, capsys, "  do\tcats \n\n purr  \n")
    assert "\nQuestion: do cats purr\n" in block
    assert block == ask(work, capsys, QUESTION)[0]


@pytest.mark.parametrize("bad", ["do cats\N{RIGHT-TO-LEFT OVERRIDE}purr", "do\u200bcats", "do cats\x00purr", "", " \n\t ", "\x1bcats"])
def test_question_controls_rejected(work: Path, capsys: pytest.CaptureFixture[str], bad: str) -> None:
    (work / ".aveto-judge" / "question.txt").write_text(bad, encoding="utf-8")
    r = run(capsys, ["judge-input", "--question-file", ".aveto-judge/question.txt"])
    assert (r.code, r.out) == (2, "")
    assert r.err.startswith("error: ")


def test_question_file_limits(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    q = work / ".aveto-judge" / "question.txt"
    q.write_bytes(b"cats " * 900)
    assert run(capsys, ["judge-input", "--question-file", str(q)]).code == 2
    q.write_bytes(b"\xff\xfe cats")
    assert run(capsys, ["judge-input", "--question-file", str(q)]).code == 2
    assert run(capsys, ["judge-input", "--question-file", str(work / "nope.txt")]).code == 2


def test_question_sources_exclusive(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (work / ".aveto-judge" / "question.txt").write_text(QUESTION)
    both = run(capsys, ["judge-input", "--question-file", ".aveto-judge/question.txt", "cats"])
    neither = run(capsys, ["judge-input"])
    assert (both.code, both.out) == (2, "") and (neither.code, neither.out) == (2, "")
    assert "exactly one" in both.err and "exactly one" in neither.err


@pytest.mark.parametrize("marker", ["=== end Q1 ===", "--- passage 1a | x ---", "--- end passage 1a ---"])
def test_passage_marker_collision_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                          capsys: pytest.CaptureFixture[str], marker: str) -> None:
    monkeypatch.chdir(tmp_path)
    secret = "secretsentinel"
    docs = {**DOCS, "pets/cats.md": f"# Cats\nCats purr {secret}.\n{marker}\n"}
    idx = write_idx(tmp_path, docs)
    r = run(capsys, ["judge-input", QUESTION], idx)
    assert (r.code, r.out) == (2, "")
    assert "pets/cats.md lines 1-3" in r.err
    assert secret not in r.err and marker not in r.err


def test_judge_input_removes_stale_reply_only(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    d = work / ".aveto-judge"
    (d / "reply.txt").write_text("Q1 ANSWERABLE old")
    (d / "other.txt").write_text("keep")
    (work / "reply.txt").write_text("keep outside")
    ask(work, capsys)
    assert transport_left(work) == ["other.txt", "question.txt"]
    assert (work / "reply.txt").read_text() == "keep outside"
    # a symlink named reply.txt is not followed or deleted
    target = work / "target.txt"
    target.write_text("keep target")
    (d / "reply.txt").symlink_to(target)
    ask(work, capsys)
    assert target.read_text() == "keep target"


# --- verdict parser ------------------------------------------------------------


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("Q1 ANSWERABLE", "ANSWERABLE"),
        ("Q1 ANSWERABLE config section states the limit", "ANSWERABLE"),
        ("  Q1 ANSWERABLE x \n", "ANSWERABLE"),
        ("Q1 NOT_ANSWERABLE related topic, limit not stated", "NOT_ANSWERABLE"),
        ("Q1 NOT_ANSWERABLE", "NOT_ANSWERABLE"),
        ("Q1 ANSWERABLE the passage says answerable in lower case", "ANSWERABLE"),
        ("", judge.EMPTY),
        (" \n\t ", judge.EMPTY),
        ("Thinking...\nQ1 ANSWERABLE x", "ANSWERABLE"),
        ("Q1 ANSWERABLE x\nQ1 NOT_ANSWERABLE y", "NOT_ANSWERABLE"),
        ("Q1 NOT_ANSWERABLE x\nQ1 ANSWERABLE y", "ANSWERABLE"),
        ("Q1 ANSWERABLE x\r\nmore", judge.MALFORMED),
        ("Q1 ANSWERABLE x\n\nQ1 ANSWERABLE y\n\n", "ANSWERABLE"),
        ("Q1 ANSWERABLE? why\n\nQ1 NOT_ANSWERABLE reason", "NOT_ANSWERABLE"),
        ("1 ANSWERABLE x\n\nWait, I need to be more careful.\n\nQ1 ANSWERABLE reason", "ANSWERABLE"),
        ("Q1 ANSWERABLE x\r\n \r\nQ1 NOT_ANSWERABLE y\r", "NOT_ANSWERABLE"),
        ("Q1 ANSWERABLE x\nQ1 ANSWERABLE.", judge.MALFORMED),
        ("Q1 ANSWERABLE x\nQ2 ANSWERABLE", judge.WRONG_ID),
        ("Q1 ANSWERABLE x\nQ1 ANSWERABLE the passage says NOT_ANSWERABLE", judge.MULTI_TOKEN),
        ("Q1 ANSWERABLE x\nQ1 ANSWERABLE y\n\u202e", judge.CONTROL),
        ("Q1 ANSWERABLE\u200b x\nQ1 ANSWERABLE y", judge.CONTROL),
        ("a\tb\nQ1 ANSWERABLE y", judge.CONTROL),
        ("Q1 ANSWERABLE x\n \n", "ANSWERABLE"),
        ("Q1 ANSWERABLE x\N{RIGHT-TO-LEFT OVERRIDE}", judge.CONTROL),
        ("Q1 ANSWERABLE\u200b x", judge.CONTROL),
        ("Q1 ANSWERABLE a\tb", judge.CONTROL),
        ("ANSWERABLE", judge.MALFORMED),
        ("Q1 answerable", judge.MALFORMED),
        ("Q1  ANSWERABLE", judge.MALFORMED),
        ("Q1 ANSWERABLE.", judge.MALFORMED),
        ("Verdict: Q1 ANSWERABLE", judge.MALFORMED),
        ("Q1 MAYBE", judge.MALFORMED),
        ("**Q1 ANSWERABLE**", judge.MALFORMED),
        ("`Q1 ANSWERABLE`", judge.MALFORMED),
        ("Q2 ANSWERABLE", judge.WRONG_ID),
        ("q1 NOT_ANSWERABLE", judge.WRONG_ID),
        ("Q1 ANSWERABLE: config section states the limit", "ANSWERABLE"),
        ("Q1 NOT_ANSWERABLE: related topic, limit not stated", "NOT_ANSWERABLE"),
        ("Q1 ANSWERABLE:", "ANSWERABLE"),
        ("Q1 NOT_ANSWERABLE:", "NOT_ANSWERABLE"),
        ("Q1 ANSWERABLE::", judge.MALFORMED),
        ("Q1 NOT_ANSWERABLE::", judge.MALFORMED),
        ("Q1 ANSWERABLE;", judge.MALFORMED),
        ("Q1 NOT_ANSWERABLE;", judge.MALFORMED),
        ("Q1 ANSWERABLE:reason", judge.MALFORMED),
        ("Q1 NOT_ANSWERABLE:reason", judge.MALFORMED),
        ("Q1 ANSWERABLE:  reason", judge.MALFORMED),
        ("Q1: ANSWERABLE", judge.WRONG_ID),
        ("Q1: NOT_ANSWERABLE x", judge.WRONG_ID),
        ("Q1 ANSWERABLE: the passage says NOT_ANSWERABLE", judge.MULTI_TOKEN),
        ("Q1 NOT_ANSWERABLE: but ANSWERABLE really", judge.MULTI_TOKEN),
        ("**Q1 ANSWERABLE:**", judge.MALFORMED),
        ("Q1 answerable:", judge.MALFORMED),
        ("Q1 ANSWERABLE the passage says NOT_ANSWERABLE", judge.MULTI_TOKEN),
        ("Q1 NOT_ANSWERABLE but ANSWERABLE really", judge.MULTI_TOKEN),
    ],
)
def test_parse_verdict_table(reply: str, expected: str) -> None:
    if expected in ("ANSWERABLE", "NOT_ANSWERABLE"):
        assert judge.parse_verdict(reply, judge.BLOCK_ID) == judge.Verdict(expected)  # type: ignore[arg-type]
    else:
        with pytest.raises(judge.JudgeError) as info:
            judge.parse_verdict(reply, judge.BLOCK_ID)
        assert info.value.category == expected


def test_verdict_carries_only_the_token() -> None:
    v = judge.parse_verdict("Q1 ANSWERABLE sentinelreason", judge.BLOCK_ID)
    assert vars(v) == {"token": "ANSWERABLE"} or [getattr(v, f) for f in v.__dataclass_fields__] == ["ANSWERABLE"]
    assert "sentinelreason" not in repr(v)


def test_reason_never_leaves_parser(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    for token in ("ANSWERABLE", "NOT_ANSWERABLE"):
        r = apply(work, capsys, f"Q1 {token} reasonsentinelxyz".encode(), digest)
        assert r.code == 0 and "reasonsentinelxyz" not in r.out + r.err
        ask(work, capsys)
    r = apply(work, capsys, b"Q1 ANSWERABLE reasonsentinelxyz and NOT_ANSWERABLE", digest)
    assert r.code == 4 and "reasonsentinelxyz" not in r.out + r.err
    for path in work.rglob("*"):
        if path.is_file() and path.name != "i.json":
            assert b"reasonsentinelxyz" not in path.read_bytes()


# --- judge-apply ---------------------------------------------------------------


def test_apply_answerable_is_retrieve_plus_signal(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    plain = run(capsys, ["retrieve", QUESTION])
    r = apply(work, capsys, b"Q1 ANSWERABLE cats purr stated", digest)
    signal = (
        "Deciding signal: answerability judge verdict ANSWERABLE "
        f"(prompt answerability-judge-v1, sha256 {APPROVED_PROMPT_SHA256})\n"
    )
    assert r.code == 0 and r.err == ""
    assert r.out == plain.out + signal
    assert "no confident match" not in r.out


def test_apply_not_answerable_exact(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    r = apply(work, capsys, b"Q1 NOT_ANSWERABLE related topic only", digest)
    assert r.code == 0 and r.err == ""
    assert r.out == (
        "no confident match\n"
        "Deciding signal: answerability judge verdict NOT_ANSWERABLE "
        f"(prompt answerability-judge-v1, sha256 {APPROVED_PROMPT_SHA256})\n"
    )
    for leak in ("pets/", "http", "cats", "purr"):
        assert leak not in r.out


def test_apply_positional_question_works(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = run(capsys, ["judge-input", QUESTION])
    digest = out.err.split()[-1]
    (work / ".aveto-judge" / "reply.txt").write_text("Q1 NOT_ANSWERABLE x")
    r = run(capsys, ["judge-apply", "--input-sha256", digest, "--verdict-file",
                     ".aveto-judge/reply.txt", *QUESTION.split()])
    assert r.code == 0 and r.out.startswith("no confident match\n")
    assert transport_left(work) == []


GOOD = "Q1 ANSWERABLE x"


@pytest.mark.parametrize(
    ("reply", "category"),
    [
        (b"x" * 4097, judge.TOO_LONG),
        (b"Q1 ANSWERABLE \xff\xfe", judge.NOT_UTF8),
        (b"", judge.EMPTY),
        (b" \n ", judge.EMPTY),
        (b"Thinking...\nQ1 ANSWERABLE x\xe2\x80\xae", judge.CONTROL),
        (b"Q1 ANSWERABLE x\xe2\x80\xae", judge.CONTROL),
        (b"Q1 ANSWERABLE.", judge.MALFORMED),
        (b"Q2 ANSWERABLE", judge.WRONG_ID),
        (b"Q1 ANSWERABLE the passage says NOT_ANSWERABLE", judge.MULTI_TOKEN),
    ],
)
def test_apply_judge_error_shows_nothing(work: Path, capsys: pytest.CaptureFixture[str],
                                         reply: bytes, category: str) -> None:
    _, digest = ask(work, capsys)
    r = apply(work, capsys, reply, digest)
    assert (r.code, r.out, r.err) == (4, "judge error\n", f"judge error: {category}\n")
    assert transport_left(work) == []


def test_apply_exactly_4096_bytes_is_not_too_long(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    reply = b"Q1 ANSWERABLE " + b"a" * (4096 - 14)
    assert len(reply) == 4096
    assert apply(work, capsys, reply, digest).code == 0


def test_apply_missing_verdict_file(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    r = run(capsys, ["judge-apply", "--question-file", ".aveto-judge/question.txt",
                     "--input-sha256", digest, "--verdict-file", ".aveto-judge/none.txt"])
    assert (r.code, r.out, r.err) == (4, "judge error\n", f"judge error: {judge.UNREADABLE}\n")
    assert transport_left(work) == []


def test_apply_hash_mismatch(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, other = ask(work, capsys, "do whales sing")
    ask(work, capsys)
    r = apply(work, capsys, GOOD.encode(), other)
    assert (r.code, r.out, r.err) == (4, "judge error\n", f"judge error: {judge.DIFFERENT_INPUT}\n")
    ask(work, capsys)
    assert apply(work, capsys, GOOD.encode(), "0" * 64).code == 4
    ask(work, capsys)
    assert apply(work, capsys, GOOD.encode(), ask(work, capsys)[1].upper()).code == 4


def test_apply_after_reingest_is_refused(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    write_index(make_index({**DOCS, "pets/cats.md": "# Cats\nCats now sleep.\n"}), work / "i.json")
    r = apply(work, capsys, GOOD.encode(), digest)
    assert r.code == 4 and r.err == f"judge error: {judge.DIFFERENT_INPUT}\n"


def test_apply_outside_transport_dir_untouched(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    outside = work / "outside.txt"
    outside.write_text(GOOD)
    cmd = ["judge-apply", "--question-file", ".aveto-judge/question.txt", "--input-sha256", digest]
    r = run(capsys, [*cmd, "--verdict-file", "outside.txt"])
    assert (r.code, r.out, r.err) == (4, "judge error\n", f"judge error: {judge.OUTSIDE}\n")
    assert outside.read_text() == GOOD
    # a symlink inside the directory pointing outside: not read, not deleted
    (work / ".aveto-judge" / "link.txt").symlink_to(outside)
    r = run(capsys, [*cmd, "--verdict-file", ".aveto-judge/link.txt"])
    assert (r.code, r.err) == (4, f"judge error: {judge.OUTSIDE}\n")
    assert outside.read_text() == GOOD
    # a path that climbs out and back in resolves to the same directory only if it really is in it
    elsewhere = work / "sub"
    elsewhere.mkdir()
    (elsewhere / "reply.txt").write_text(GOOD)
    r = run(capsys, [*cmd, "--verdict-file", "sub/reply.txt"])
    assert r.err == f"judge error: {judge.OUTSIDE}\n" and (elsewhere / "reply.txt").exists()
    # the question file outside the directory is read but never deleted
    q = work / "q.txt"
    q.write_text(QUESTION)
    digest2 = run(capsys, ["judge-input", "--question-file", "q.txt"]).err.split()[-1]
    (work / ".aveto-judge" / "reply.txt").write_text(GOOD)
    r = run(capsys, ["judge-apply", "--question-file", "q.txt", "--input-sha256", digest2,
                     "--verdict-file", ".aveto-judge/reply.txt"])
    assert r.code == 0 and q.exists() and transport_left(work) == ["link.txt"]


def test_apply_deletes_transport_files_every_path(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    assert apply(work, capsys, GOOD.encode(), digest).code == 0
    assert transport_left(work) == []
    _, digest = ask(work, capsys)
    assert apply(work, capsys, b"nonsense", digest).code == 4
    assert transport_left(work) == []
    # exit-2 paths: bad question text, then a missing index
    (work / ".aveto-judge" / "question.txt").write_text("bad\N{RIGHT-TO-LEFT OVERRIDE}question")
    r = apply(work, capsys, GOOD.encode(), "0" * 64)
    assert (r.code, r.out) == (2, "") and r.err.startswith("error: ")
    assert transport_left(work) == []
    _, digest = ask(work, capsys)
    (work / ".aveto-judge" / "reply.txt").write_text(GOOD)
    r = run(capsys, ["judge-apply", "--index", "missing.json", "--question-file", ".aveto-judge/question.txt",
                     "--input-sha256", digest, "--verdict-file", ".aveto-judge/reply.txt"])
    assert (r.code, r.out) == (2, "") and r.err.startswith("error: ")
    assert transport_left(work) == []


def test_apply_deletion_failure_is_judge_error(work: Path, capsys: pytest.CaptureFixture[str],
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    _, digest = ask(work, capsys)

    def refuse(self: Path, *args: object, **kwargs: object) -> None:
        raise PermissionError("no")

    monkeypatch.setattr(Path, "unlink", refuse)
    r = apply(work, capsys, GOOD.encode(), digest)
    assert (r.code, r.out, r.err) == (4, "judge error\n", f"judge error: {judge.NOT_DELETED}\n")


def test_apply_requires_verdict_and_hash(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _, digest = ask(work, capsys)
    base = ["judge-apply", "--question-file", ".aveto-judge/question.txt"]
    assert main([*base, "--input-sha256", digest]) == 2
    assert main([*base, "--verdict-file", ".aveto-judge/reply.txt"]) == 2
    assert (work / ".aveto-judge" / "question.txt").exists()


def test_unjudged_outputs_never_look_judged(work: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ev = work / "e.toml"
    ev.write_text(
        f'pinned_commit = "{COMMIT}"\n'
        '[[question]]\nid = "a1"\nquestion = "cats purr"\nsources = ["pets/cats.md"]\n'
        '[[question]]\nid = "u1"\nquestion = "quantum spaceship"\nanswerable = false\n'
    )
    for argv in (["retrieve", QUESTION], ["eval", "--eval-file", str(ev)]):
        r = run(capsys, argv)
        assert r.code == 0
        low = (r.out + r.err).replace(str(ev), "EVALFILE").lower()  # the tmp path may hold test names
        for banned in ("deciding signal", "judge", "no confident match"):
            assert banned not in low, (argv, banned)


# --- offline, no model, no process -----------------------------------------------


def test_program_offline_no_model(work: Path, capsys: pytest.CaptureFixture[str],
                                  monkeypatch: pytest.MonkeyPatch) -> None:
    # The autouse socket guard is active: this test fails if the guard is ever removed.
    with pytest.raises(RuntimeError, match="network disabled"):
        socket.create_connection(("192.0.2.1", 80))

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("the program must not start a process")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    for name in ("system", "posix_spawn", "posix_spawnp", "execv", "execve", "execvp", "fork"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, forbidden)
    ev = work / "e.toml"
    ev.write_text(
        f'pinned_commit = "{COMMIT}"\n'
        '[[question]]\nid = "a1"\nquestion = "cats purr"\nsources = ["pets/cats.md"]\n'
        '[[question]]\nid = "u1"\nquestion = "quantum spaceship"\nanswerable = false\n'
    )
    vf = verdicts_file(work, ev, {"a1": "ANSWERABLE", "u1": "NOT_ANSWERABLE"})
    assert run(capsys, ["retrieve", QUESTION]).code == 0
    assert run(capsys, ["eval", "--eval-file", str(ev)]).code == 0
    r = run(capsys, ["eval", "--eval-file", str(ev), "--verdicts", str(vf)])
    assert r.code == 0 and "bars: unanswerable_abstained=1/1" in r.out
    for reply in (b"Q1 ANSWERABLE x", b"Q1 NOT_ANSWERABLE x", b"garbage"):
        _, digest = ask(work, capsys)
        assert apply(work, capsys, reply, digest).code == (4 if reply == b"garbage" else 0)


ALLOWED_IMPORTS = {
    "__future__", "argparse", "dataclasses", "hashlib", "os", "pathlib", "re", "sys", "tomllib",
    "typing", "unicodedata", "collections.abc",
}


@pytest.mark.parametrize("name", ["__main__.py", "judge.py", "judge_eval.py"])
def test_judge_modules_import_allow_list(name: str) -> None:
    tree = ast.parse((ROOT / "aveto_support" / name).read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0 and node.module is not None
            found.add(node.module)
    assert found, name
    for module in found:
        assert module in ALLOWED_IMPORTS or module == "aveto_support" or module.startswith("aveto_support."), module


# --- the prompt file -----------------------------------------------------------------


def test_prompt_file_hash_pinned() -> None:
    data = (ROOT / "prompts" / "answerability-judge-v1.txt").read_bytes()
    assert hashlib.sha256(data).hexdigest() == judge.PROMPT_SHA256 == APPROVED_PROMPT_SHA256
    assert data.endswith(b".\n") and data.count(b"\n") == 1 and not data.startswith(b"\xef\xbb\xbf")
    assert data.startswith(b"You judge documentation search results.")
