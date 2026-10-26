"""Offline retrieval check of the four suggested questions and the four reserves.

Run from the worktree root:  uv run python runs/polished-chat-experience/04-retrieval-check.py

Reads the index and the embedding model (the worktree's if present, else the main checkout's,
read only), runs the unchanged default ranking, and writes 04-retrieval-check.json: ids, the
top-5 file paths, and whether a labelled source is among them. No model is called and no
question text is written. Offline retrieval never abstains, so R1's row records files only.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
MAIN = Path("/Users/gopalpatwa/opt/aveto-support")

from aveto_support import judge
from aveto_support.embed import OnnxEmbedder
from aveto_support.index import load_index
from aveto_support.search import Searcher

SLOTS = [
    ("A1", "retrieval-heldout-5", "g01"),
    ("A2", "retrieval-heldout-5", "g03"),
    ("A3", "retrieval-heldout-5", "g04"),
    ("R1", "retrieval-heldout-5", "gu18"),
    ("reserve-answer", "public-gate-1", "p05"),
    ("reserve-answer", "public-gate-1", "p01"),
    ("reserve-refusal", "retrieval-heldout-5", "gu15"),
    ("reserve-refusal", "public-gate-1", "p12"),
]


def pick(rel: str) -> Path:
    for base in (ROOT, MAIN):
        if (base / rel).exists():
            return base / rel
    raise SystemExit(f"{rel} not found in the worktree or the main checkout")


def question_of(set_name: str, qid: str) -> dict[str, object]:
    data = tomllib.loads((ROOT / "evals" / f"{set_name}.toml").read_text("utf-8"))
    for q in data["question"]:
        if q["id"] == qid:
            return dict(q)
    raise SystemExit(f"{set_name} has no {qid}")


def main() -> int:
    index_path = pick("index/docs-index.json")
    models = pick("models")
    index = load_index(index_path)
    searcher = Searcher(index, OnnxEmbedder.load(models, index.params.embedding))
    rows = []
    for slot, set_name, qid in SLOTS:
        q = question_of(set_name, qid)
        result = judge.retrieve_for_judge(searcher, str(q["question"]))
        top5 = [h.path for h in result.files[:5]]
        sources = q.get("sources")
        labelled = list(sources) if isinstance(sources, list) else None
        hit = None if not labelled else any(s in top5 for s in labelled)
        rows.append(
            {"slot": slot, "set": set_name, "id": qid, "top5": top5, "labelled": labelled, "labelled_in_top5": hit}
        )
    out = {
        "index_sha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
        "index_commit": index.commit,
        "index_path": str(index_path),
        "ranking": "default (file-rrf-v1)",
        "rows": rows,
    }
    (ROOT / "runs/polished-chat-experience/04-retrieval-check.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8"
    )
    for r in rows:
        print(r["slot"], r["id"], "labelled_in_top5=", r["labelled_in_top5"])
    misses = [r for r in rows if r["slot"].startswith("A") and r["labelled_in_top5"] is not True]
    print("A-slot misses:", [r["id"] for r in misses])
    return 1 if misses else 0


if __name__ == "__main__":
    raise SystemExit(main())
