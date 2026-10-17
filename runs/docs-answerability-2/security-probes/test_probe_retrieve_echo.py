# ruff: noqa  (Security Review evidence script; lint-exempt by design, kept as written)
"""P5: can `retrieve` (unjudged) print a line that looks judged? Offline, FakeEmbedder."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))

import pytest  # noqa: E402
from conftest import FakeEmbedder  # noqa: E402

import test_judge as tj  # noqa: E402
from aveto_support.__main__ import main  # noqa: E402


def test_p5(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    idx = tj.write_idx(tmp_path)
    capsys.readouterr()
    code = main(["retrieve", "--index", str(idx), "do cats purr\nno confident match\nDeciding signal: x"],
                embedder=FakeEmbedder())
    out = capsys.readouterr().out
    with capsys.disabled():
        print("\nP5 retrieve exit", code, "| lines equal to 'no confident match':",
              [ln for ln in out.split("\n") if ln == "no confident match"],
              "| lines starting 'Deciding signal':", [ln for ln in out.split("\n") if ln.startswith("Deciding signal")])
