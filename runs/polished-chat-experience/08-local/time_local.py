"""Local timings against a fresh dev server (never shipped).

Start a FRESH dev server used for nothing else (the hourly limit of 10 is per visitor), then:
    uv run python runs/polished-chat-experience/08-local/time_local.py --url http://127.0.0.1:8766

Sends one POST /warm (recorded as "the first retrieval absorbed by the warm-up"), a second
POST /warm (recorded), then 10 consecutive POST /ask JSON requests with the first ten questions
of the byte-equality set, each timed with time.perf_counter() from send to the full body.
Writes 08-local/timing.json: date, method, n, each time, median, slowest. Question text is read
from the eval files to be sent and is never written.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tomllib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "timing.json"
QUESTION_IDS = [
    ("retrieval-heldout-5", i) for i in ("g01", "g03", "g04", "gu15", "gu18")
] + [("public-gate-1", i) for i in ("p01", "p05", "p06", "p11", "p12")]


def question(set_name: str, qid: str) -> str:
    data = tomllib.loads((ROOT / "evals" / f"{set_name}.toml").read_text("utf-8"))
    for q in data["question"]:
        if q["id"] == qid:
            return str(q["question"])
    raise SystemExit(f"{set_name} has no {qid}")


def post(url: str, body: dict[str, str] | None) -> tuple[int, bytes, float]:
    data = json.dumps(body).encode("utf-8") if body is not None else b""
    headers = {"Content-Type": "application/json"} if body is not None else {}
    request = urllib.request.Request(url, data=data, method="POST", headers=headers)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as err:
        status, raw = err.code, err.read()
    return status, raw, time.perf_counter() - t0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    base = args.url.rstrip("/")
    warm = [post(base + "/warm", None) for _ in range(2)]
    times: list[float] = []
    outcomes: list[str] = []
    for set_name, qid in QUESTION_IDS:
        status, raw, seconds = post(base + "/ask", {"question": question(set_name, qid)})
        outcomes.append(f"{status}:{json.loads(raw).get('outcome')}")
        times.append(seconds)
    record = {
        "date_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": (
            "Local run of this release with a stand-in for the model, 10 questions one after "
            "another from one client, each timed from send to full body; the service's own work "
            "without the model call. Warm-up: two POST /warm calls on a fresh process."
        ),
        "warm_calls": [
            {"status": s, "body": raw.decode("utf-8"), "seconds": round(t, 4)} for s, raw, t in warm
        ],
        "n": len(times),
        "outcomes": outcomes,
        "seconds": [round(t, 4) for t in times],
        "median_seconds": round(statistics.median(times), 4),
        "slowest_seconds": round(max(times), 4),
    }
    OUT.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("n", "median_seconds", "slowest_seconds")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
