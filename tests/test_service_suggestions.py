"""The four suggested questions are copied from spent eval sets (tech spec 3.3, 9 and 10.4)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from aveto_service.pages import SUGGESTIONS_PATH, load_suggestions

ROOT = Path(__file__).resolve().parent.parent

# The literals test_page_cards.py pins; kept here so a drift in either file fails.
EXPECTED = {
    "A1": 'Does saying "looks good" to an agent count as approving something?',
    "A2": "Can I keep a long-lived feature branch going while the agents work on it?",
    "A3": "If a deploy of the Aveto website goes wrong, how do I undo it?",
    "R1": "Does it support right-to-left languages?",
}


def _file() -> list[dict[str, str]]:
    data = tomllib.loads(SUGGESTIONS_PATH.read_text(encoding="utf-8"))
    assert data["schema"] == 1
    return list(data["suggestion"])


def test_suggestions_are_copied_from_spent_sets() -> None:
    rows = _file()
    assert [r["slot"] for r in rows] == ["A1", "A2", "A3", "R1"]
    for r in rows:
        eval_file = tomllib.loads((ROOT / r["set"]).read_text(encoding="utf-8"))
        by_id = {q["id"]: q for q in eval_file["question"]}
        q = by_id[r["id"]]
        assert r["text"] == q["question"]
        if r["slot"] == "R1":
            assert r["expect"] == "no_confident_match" and q.get("answerable") is False
        else:
            assert r["expect"] == "answer" and q.get("answerable", True) is True
        assert len(r["text"]) <= 90
        assert not any(c in r["text"] for c in "<>\n")
    assert {r["slot"]: r["text"] for r in rows} == EXPECTED


def test_loader_returns_the_four_in_order_and_fails_closed(tmp_path: Path) -> None:
    got = load_suggestions()
    assert [(s.slot, s.text, s.expect) for s in got] == [
        ("A1", EXPECTED["A1"], "answer"),
        ("A2", EXPECTED["A2"], "answer"),
        ("A3", EXPECTED["A3"], "answer"),
        ("R1", EXPECTED["R1"], "no_confident_match"),
    ]
    assert load_suggestions(tmp_path / "missing.toml") == ()
    bad = tmp_path / "bad.toml"
    bad.write_text('schema = 1\n[[suggestion]]\nslot = "A1"\nexpect = "answer"\ntext = "x <b>"\n')
    assert load_suggestions(bad) == ()
    bad.write_text("not toml [")
    assert load_suggestions(bad) == ()
