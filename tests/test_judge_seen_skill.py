"""The eval-only aveto-judge-seen skill: refusals, frontmatter, payload size.

The payload-size test needs the cached embedding model and the built index
(`ingest`), so it carries the `model` marker: `uv run pytest -m model`.
Nothing here spawns a judge or touches the network.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent
SKILL_DIR = ROOT / ".claude" / "skills" / "aveto-judge-seen"
SKILL = SKILL_DIR / "SKILL.md"
HELPER = SKILL_DIR / "seen_payload.py"
SEEN = ROOT / "runs" / "docs-answerability-2" / "judge-check"

# Bash tool inline ceiling: "Inline up to roughly 30,000 characters by default"
# (https://code.claude.com/docs/en/tools-reference#output-limits).
INLINE_CEILING = 30_000


def _load_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location("seen_payload", HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = _load_helper()


@pytest.fixture
def seen(tmp_path: Path) -> Path:
    """A copy of the batch files and the key's table headers (membership only)."""
    for batch in SEEN.glob("batch-*.txt"):
        shutil.copy(batch, tmp_path / batch.name)
    (tmp_path / "key").mkdir()
    shutil.copy(SEEN / "key" / "key.toml", tmp_path / "key" / "key.toml")
    return tmp_path


def _batch_ids(batch_glob: str = "batch-*.txt") -> list[str]:
    ids: list[str] = []
    for batch in sorted(SEEN.glob(batch_glob)):
        for line in batch.read_text(encoding="utf-8").splitlines():
            ids.append(line.split(" ", 1)[0])
    return ids


def test_ids_match_key() -> None:
    with (SEEN / "key" / "key.toml").open("rb") as handle:
        key = tomllib.load(handle)
    ids = _batch_ids()
    assert len(ids) == len(set(ids))
    assert set(ids) == set(key)
    assert all(re.fullmatch(r"r[0-9]{3}", i) for i in ids)
    assert _batch_ids("batch-1.txt") == [f"r{n:03d}" for n in range(1, 50)]
    if (SEEN / "batch-2.txt").exists():
        assert all(int(i[1:]) >= 101 for i in _batch_ids("batch-2.txt"))
    for run_id, table in key.items():
        assert set(table) == {"set", "id"}, run_id
        with (ROOT / table["set"]).open("rb") as handle:
            eval_ids = {q["id"] for q in tomllib.load(handle)["question"]}
        assert table["id"] in eval_ids, run_id


def test_skill_frontmatter_and_body() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    front, body = text[4:].split("\n---\n", 1)
    keys = [line.split(":", 1)[0] for line in front.splitlines() if re.match(r"^[a-z-]+:", line)]
    assert "context: fork" in front.splitlines()
    assert "agent: aveto-answerability-judge" in front.splitlines()
    assert "model" not in keys
    assert "disable-model-invocation" not in keys
    # The body is one injection line and nothing else.
    lines = [line for line in body.splitlines() if line.strip()]
    assert len(lines) == 1
    assert lines[0].startswith("!`") and lines[0].endswith("`")
    assert "seen_payload.py" in lines[0]
    assert "$ARGUMENTS" not in text and "$0" not in lines[0] and "'" not in lines[0]
    allowed = next(x for x in front.splitlines() if x.startswith("allowed-tools:"))
    assert allowed.endswith("seen_payload.py)") and "*)" not in allowed
    assert "key.toml" not in lines[0]


HOSTILE = [
    "",
    "r1",
    "r0001",
    "R001",
    "x001",
    "r001 ",
    "r001\n",
    "r001\r",
    "r000x",
    "r094",
    "r999",
    "r101' ; echo INJECTED ; '",
    'r101"; echo INJECTED; "',
    "$(echo INJECTED)",
    "r101`echo INJECTED`",
    "r101\necho INJECTED",
    "r101; echo INJECTED",
    "r101 && echo INJECTED",
    "r101|echo INJECTED",
    "../r101",
    "r101" + "1" * 5000,
    "What is the price?",
]


def _skill_line() -> str:
    body = SKILL.read_text(encoding="utf-8").split("\n---\n", 1)[1]
    line = next(x for x in body.splitlines() if x.strip())
    assert line.startswith("!`") and line.endswith("`")
    return line[2:-1]


@pytest.mark.parametrize("arg", HOSTILE)
def test_refuses_bad_ids(arg: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    id_file = tmp_path / "seen-id"
    id_file.write_text(arg, encoding="utf-8")
    assert helper.main([], id_file) == 2
    out = capsys.readouterr()
    assert out.out.startswith("refused:") and out.out.count("\n") == 1
    assert "INJECTED" not in out.out + out.err
    assert "=== " not in out.out
    assert not (tmp_path / "q").exists()


def test_refuses_missing_symlink_and_binary_id_file(tmp_path: Path) -> None:
    assert helper.main([], tmp_path / "absent") == 2
    real = tmp_path / "real"
    real.write_text("r001", encoding="utf-8")
    link = tmp_path / "link"
    link.symlink_to(real)
    assert helper.main([], link) == 2
    binary = tmp_path / "bin"
    binary.write_bytes(b"r001\xff")
    assert helper.main([], binary) == 2


@pytest.mark.parametrize("arg", HOSTILE)
def test_argv_is_refused_and_runs_nothing(arg: str, tmp_path: Path) -> None:
    done = subprocess.run(
        [sys.executable, str(HELPER), arg],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 2
    assert done.stdout.startswith("refused:") and done.stdout.count("\n") == 1
    assert "INJECTED" not in done.stdout + done.stderr


def test_read_id_accepts_one_trailing_newline(tmp_path: Path) -> None:
    id_file = tmp_path / "seen-id"
    id_file.write_text("r101\n", encoding="utf-8")
    assert helper.read_id(id_file) == "r101"


@pytest.mark.parametrize("arg", HOSTILE)
def test_shell_line_has_no_caller_text(arg: str, tmp_path: Path) -> None:
    """Render the line as Claude Code would (substituting every variable and
    $ARGUMENTS), run it with /bin/sh and a stub `uv`: exactly one command runs."""
    template = _skill_line()
    rendered = template.replace("$ARGUMENTS", arg)
    assert rendered == template  # no place for caller text
    assert arg not in rendered or arg == ""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    stub = bin_dir / "uv"
    stub.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$LOG"\n', encoding="utf-8")
    stub.chmod(0o755)
    skill_dir = SKILL_DIR
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "LOG": str(log),
        "CLAUDE_PROJECT_DIR": str(ROOT),
        "CLAUDE_SKILL_DIR": str(skill_dir),
    }
    done = subprocess.run(
        ["/bin/sh", "-c", rendered], env=env, capture_output=True, text=True, check=False
    )
    assert done.returncode == 0
    assert "INJECTED" not in done.stdout + done.stderr
    calls = log.read_text(encoding="utf-8").splitlines()
    assert calls == [f"run -q --project {ROOT} python {skill_dir}/seen_payload.py"]


def test_refuses_id_not_in_key(seen: Path) -> None:
    with pytest.raises(helper.Refusal, match="not a committed seen-set id"):
        helper.prepare("r094", seen)
    # Present in a batch file but removed from the key: still refused.
    text = (seen / "key" / "key.toml").read_text(encoding="utf-8")
    (seen / "key" / "key.toml").write_text(text.replace("[r001]", "[r999]"), encoding="utf-8")
    with pytest.raises(helper.Refusal, match="not a committed seen-set id"):
        helper.prepare("r001", seen)
    assert not (seen / "q").exists()


def test_refuses_wrong_argument_count(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (["r001"], ["r001", "r002"], [""]):
        assert helper.main(argv) == 2
        out = capsys.readouterr().out
        assert out == "refused: this skill takes no argument\n"
        assert "=== " not in out


def test_prepare_writes_question_only(seen: Path) -> None:
    path = helper.prepare("r001", seen)
    assert path == seen / "q" / "r001.txt"
    with (seen / "key" / "key.toml").open("rb") as handle:
        table = tomllib.load(handle)["r001"]
    with (ROOT / table["set"]).open("rb") as handle:
        entry = next(q for q in tomllib.load(handle)["question"] if q["id"] == table["id"])
    assert path.read_text(encoding="utf-8") == entry["question"]
    assert path.read_text(encoding="utf-8") == " ".join(entry["question"].split())


@pytest.mark.model
def test_largest_payload_is_below_inline_ceiling(seen: Path) -> None:
    sizes: dict[str, int] = {}
    for run_id in _batch_ids():
        question_file = helper.prepare(run_id, seen)
        done = subprocess.run(
            helper.judge_input_command(question_file),
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        assert done.returncode == 0, (run_id, done.stderr)
        assert b"input sha256: " in done.stderr
        sizes[run_id] = len(done.stdout.decode("utf-8"))
    with (SEEN / "key" / "key.toml").open("rb") as handle:
        assert len(sizes) == len(tomllib.load(handle))
    worst = max(sizes, key=lambda k: sizes[k])
    print(f"largest payload: {worst} {sizes[worst]} chars")
    assert sizes[worst] < INLINE_CEILING, (worst, sizes[worst])


@pytest.mark.model
def test_sample_derivation_reproducible(tmp_path: Path) -> None:
    """The committed key, batch and sample-eval are what `derive_sample` writes, byte for byte."""
    import hashlib

    from aveto_support.embed import OnnxEmbedder
    from aveto_support.evaluate import load_eval_set
    from aveto_support.index import load_index
    from aveto_support.search import Searcher
    from tools import judge_run

    index_path = ROOT / "index" / "docs-index.json"
    index = load_index(index_path)
    embedder = OnnxEmbedder.load(ROOT / "models", index.params.embedding)
    try:
        rows = judge_run.derive_sample(Searcher(index, embedder), ROOT)
    finally:
        embedder.close()
    commit = load_eval_set(ROOT / judge_run.KEY_ORDER[0]).pinned_commit
    digest = hashlib.sha256(index_path.read_bytes()).hexdigest()
    judge_run.write_check_dir(rows, tmp_path, digest, commit)
    for name in ("key/key.toml", "batch-1.txt", "sample-eval.toml"):
        assert (tmp_path / name).read_bytes() == (SEEN / name).read_bytes(), name
