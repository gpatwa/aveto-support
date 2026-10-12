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
SEEN = ROOT / "runs" / "docs-answerability" / "seen-check"

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


def _batch_ids() -> list[str]:
    ids: list[str] = []
    for batch in sorted(SEEN.glob("batch-*.txt")):
        for line in batch.read_text(encoding="utf-8").splitlines():
            ids.append(line.split(" ", 1)[0])
    return ids


def test_ids_match_key() -> None:
    with (SEEN / "key" / "key.toml").open("rb") as handle:
        key = set(tomllib.load(handle))
    ids = _batch_ids()
    assert len(ids) == 93 and len(set(ids)) == 93
    assert set(ids) == key
    assert all(re.fullmatch(r"r[0-9]{3}", i) for i in ids)


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
    assert "'$ARGUMENTS'" in lines[0]
    assert "key.toml" not in lines[0]


@pytest.mark.parametrize(
    "arg",
    [
        "",
        "r1",
        "r0001",
        "R001",
        "x001",
        "r001 ",
        "r001\n",
        "r000x",
        "r001; touch pwned",
        "r001$(touch pwned)",
        "r001`touch pwned`",
        "r001 && ls",
        "r001|cat",
        "../r001",
        "What is the price?",
    ],
)
def test_refuses_bad_ids(arg: str, tmp_path: Path) -> None:
    done = subprocess.run(
        [sys.executable, str(HELPER), arg],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 2
    assert done.stdout.startswith("refused:") and done.stdout.count("\n") == 1
    assert "=== " not in done.stdout
    assert not (tmp_path / "pwned").exists()


def test_refuses_id_not_in_key(seen: Path) -> None:
    with pytest.raises(helper.Refusal, match="not a committed seen-set id"):
        helper.prepare("r094", seen)
    # Present in a batch file but removed from the key: still refused.
    text = (seen / "key" / "key.toml").read_text(encoding="utf-8")
    (seen / "key" / "key.toml").write_text(text.replace("[r001]", "[r999]"), encoding="utf-8")
    with pytest.raises(helper.Refusal, match="not a committed seen-set id"):
        helper.prepare("r001", seen)
    assert not (seen / "q").exists()


def test_refuses_wrong_argument_count() -> None:
    assert helper.main([]) == 2
    assert helper.main(["r001", "r002"]) == 2


def test_prepare_writes_question_only(seen: Path) -> None:
    path = helper.prepare("r001", seen)
    assert path == seen / "q" / "r001.txt"
    assert path.read_text(encoding="utf-8") == "Can I get approval requests in Microsoft Teams?"


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
    assert len(sizes) == 93
    worst = max(sizes, key=lambda k: sizes[k])
    print(f"largest payload: {worst} {sizes[worst]} chars")
    assert sizes[worst] < INLINE_CEILING, (worst, sizes[worst])
