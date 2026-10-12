"""Seen-set check preparer (tech spec 5.2 step 1). Run from the repo root.

Reads the four seen eval files only, assigns neutral run ids r001-r093 in
shuffled order, writes batch-<n>.txt (run id + question only) and key/key.toml.
"""
import json, random, tomllib
from pathlib import Path

SEED = 20261009
SIZES = [16, 16, 16, 15, 15, 15]
FILES = ["retrieval", "retrieval-heldout", "retrieval-heldout-3", "retrieval-heldout-4"]
OUT = Path("runs/docs-answerability/seen-check")

items = []  # file order
for f in FILES:
    path = f"evals/{f}.toml"
    for q in tomllib.load(open(path, "rb"))["question"]:
        text = " ".join(q["question"].split())
        assert text == q["question"] and "\t" not in text
        items.append({
            "eval_file": path, "eval_id": q["id"], "question": text,
            "answerable": q.get("answerable", True),
            "hard_negative": "hard_negative" in q,
        })
assert len(items) == 93 and sum(not i["answerable"] for i in items) == 20

random.Random(SEED).shuffle(items)
assert sum(SIZES) == 93
(OUT / "key").mkdir(parents=True, exist_ok=True)
key, pos = [], 0
for n, size in enumerate(SIZES, 1):
    lines = []
    for it in items[pos:pos + size]:
        pos += 1
        rid = f"r{pos:03d}"
        lines.append(f"{rid} {it['question']}")
        key.append((rid, it))
    (OUT / f"batch-{n}.txt").write_text("\n".join(lines) + "\n")
with open(OUT / "key" / "key.toml", "w") as fh:
    fh.write("# Seen-set check key. Driver and judges must never read this file.\n")
    for rid, it in key:
        fh.write(f'\n[{rid}]\neval_file = {json.dumps(it["eval_file"])}\n'
                 f'eval_id = {json.dumps(it["eval_id"])}\n'
                 f'answerable = {str(it["answerable"]).lower()}\n'
                 f'hard_negative = {str(it["hard_negative"]).lower()}\n')
