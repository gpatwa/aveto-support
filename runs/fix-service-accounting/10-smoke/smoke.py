"""Live smoke for fix-service-accounting (tech spec 8.1). Run from the worktree root:

    uv run python runs/fix-service-accounting/10-smoke/smoke.py watch on|off [--dry-run]
    uv run python runs/fix-service-accounting/10-smoke/smoke.py ask --index <path> --models <path> [--dry-run]

Standard-library HTTP only, plus the local `aveto_support` for the byte comparison. It calls no
`az` command and no host other than SERVICE_URL, never retries a POST (except the watcher's
bounded empty-question POST, spec 8.1), and prints and writes ids, codes, counts and times
only: never question text, passage text or any reply body. `--dry-run` prints the plan and
makes no network call and reads no file other than the eval file's ids.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import tomllib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

SERVICE_URL = "https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io"
EVAL_FILE = Path("evals/retrieval-heldout-5.toml")
OUT_DIR = Path("runs/fix-service-accounting/10-smoke")
QUESTIONS: list[tuple[str, str]] = [  # (id, expected outcome), sent in this order
    ("g01", "answer"),
    ("g03", "answer"),
    ("g04", "answer"),
    ("gu15", "no_confident_match"),
    ("gu18", "no_confident_match"),
]
BUILD_INGEST_SHA_PREFIX = "f36ef5d4"  # the previous build's ingest hash (spec 7.1), prefix
PRICE_IN_NANO = 2000
PRICE_OUT_NANO = 10000
BAND_LOW_USD, BAND_HIGH_USD = Decimal("0.00663"), Decimal("0.00897")  # 15% around $0.0078
CHECK_TOLERANCE_NANO = 2000  # each spend_today_usd reading is truncated to 1,000 nano-dollars
WATCH_TIMEOUT_S = 600
WATCH_POLL_S = 2
HTTP_TIMEOUT_S = 90  # one judged question takes seconds; the service times a call out at 20 s
NANO = 10**9


def now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def http(method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, Any]:
    """One request to SERVICE_URL. Returns (status, parsed JSON or None). Never retries."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    request = urllib.request.Request(SERVICE_URL + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_S) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as err:
        status, raw = err.code, err.read()
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, None


def load_questions() -> dict[str, str]:
    with EVAL_FILE.open("rb") as handle:
        entries = tomllib.load(handle)["question"]
    by_id = {e["id"]: e["question"] for e in entries}
    return {qid: by_id[qid] for qid, _ in QUESTIONS}


def write(name: str, record: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# --- watch ---------------------------------------------------------------------------------


def watch(want: str, dry_run: bool) -> int:
    plan = [
        f"poll GET {SERVICE_URL}/health every {WATCH_POLL_S} s, up to {WATCH_TIMEOUT_S} s",
        f"record the first time kill_switch == {want!r}",
    ]
    if want == "on":
        plan.append('then POST /ask {"question": ""}: require 503 service_off '
                    "(400 empty_question: wait 5 s and repeat, at most 10 times)")
    else:
        plan.append("require three consecutive 'off' reads")
    plan.append(f"write {OUT_DIR / f'watch-{want}.json'}; exit 1 on timeout")
    if dry_run:
        print("DRY RUN (watch): no network call")
        for line in plan:
            print(" -", line)
        return 0
    started = now_utc()
    t0 = time.monotonic()
    first_seen: float | None = None
    consecutive = 0
    reached = False
    polls = 0
    while time.monotonic() - t0 < WATCH_TIMEOUT_S:
        polls += 1
        try:
            status, body = http("GET", "/health")
        except OSError:
            status, body = 0, None
        seen = body.get("kill_switch") if status == 200 and isinstance(body, dict) else None
        if seen == want:
            first_seen = first_seen if first_seen is not None else time.monotonic() - t0
            consecutive += 1
            if want == "on" or consecutive >= 3:
                reached = True
                break
        else:
            consecutive = 0
        time.sleep(WATCH_POLL_S)
    record: dict[str, Any] = {
        "mode": f"watch {want}", "start_utc": started, "polls": polls, "reached": reached,
        "seconds_to_first_wanted_state": None if first_seen is None else round(first_seen, 1),
    }
    ok = reached
    if reached and want == "on":
        attempts: list[dict[str, Any]] = []
        refused = False
        for _ in range(10):
            try:
                status, body = http("POST", "/ask", {"question": ""})
            except OSError:
                status, body = 0, None
            outcome = body.get("outcome") if isinstance(body, dict) else None
            attempts.append({"status": status, "outcome": outcome})
            if status == 503 and outcome == "service_off":
                refused = True
                break
            time.sleep(5)
        record["empty_question_posts"] = attempts
        record["service_off_confirmed"] = refused
        ok = refused
    record["ok"] = ok
    record["end_utc"] = now_utc()
    write(f"watch-{want}.json", record)
    print(json.dumps(record, sort_keys=True))
    return 0 if ok else 1


# --- ask -----------------------------------------------------------------------------------


def local_files(searcher: Any, question: str) -> list[dict[str, Any]]:
    from aveto_support import judge
    from aveto_support.search import retrieve  # imported late: --dry-run needs no index

    result = retrieve(searcher, judge.normalise_question(question))
    return [
        {
            "rank": hit.rank, "path": hit.path, "url": hit.url,
            "passages": [
                {
                    "heading": " > ".join(m.passage.heading_path)
                    if m.passage.heading_path else "(top of file)",
                    "line_start": m.passage.line_start, "line_end": m.passage.line_end,
                    "url": m.url, "text": m.passage.text,
                }
                for m in hit.passages
            ],
        }
        for hit in result.files
    ]


def first_difference(remote: list[dict[str, Any]], local: list[dict[str, Any]]) -> str | None:
    """The name of the first differing field, else None. `text` is compared as UTF-8 bytes."""
    if len(remote) != len(local):
        return "files.length"
    for r_file, l_file in zip(remote, local, strict=True):
        for key in ("rank", "path", "url"):
            if r_file.get(key) != l_file[key]:
                return f"file.{key}"
        r_passages = r_file.get("passages") or []
        if len(r_passages) != len(l_file["passages"]):
            return "passages.length"
        for r_p, l_p in zip(r_passages, l_file["passages"], strict=True):
            for key in ("heading", "line_start", "line_end", "url"):
                if r_p.get(key) != l_p[key]:
                    return f"passage.{key}"
            r_text, l_text = r_p.get("text"), l_p["text"]
            if not isinstance(r_text, str) or r_text.encode("utf-8") != l_text.encode("utf-8"):
                return "passage.text"
    return None


def to_nano(usd: str) -> int:
    return int(Decimal(usd) * NANO)


def figures(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    d_judged = after["judged_today"] - before["judged_today"]
    d_in = after["input_tokens_today"] - before["input_tokens_today"]
    d_out = after["output_tokens_today"] - before["output_tokens_today"]
    d_spend = to_nano(after["spend_today_usd"]) - to_nano(before["spend_today_usd"])
    valid = before["day"] == after["day"] and d_judged >= 0
    out: dict[str, Any] = {
        "window_valid": valid, "delta_judged": d_judged, "delta_input_tokens": d_in,
        "delta_output_tokens": d_out, "delta_spend_nano": d_spend,
    }
    if not valid or d_judged <= 0:
        out["cost_per_judged_question"] = "not measured"
        return out
    token_cost = d_in * PRICE_IN_NANO + d_out * PRICE_OUT_NANO
    per_question = Decimal(token_cost) / d_judged / NANO
    out["token_cost_nano"] = token_cost
    out["cost_per_judged_question_usd"] = str(per_question.quantize(Decimal("0.000001")))
    out["within_15pct_band_of_0.0078"] = bool(BAND_LOW_USD <= per_question <= BAND_HIGH_USD)
    gap = d_spend - token_cost
    out["spend_minus_token_cost_nano"] = gap
    out["issue_8_check"] = (
        "pass: counter charges at $2/$10" if abs(gap) <= CHECK_TOLERANCE_NANO
        else "a billable retry may have happened (gap near one per-attempt reservation)"
        if gap > CHECK_TOLERANCE_NANO else "finding: spend below token cost"
    )
    return out


def ask(index_arg: str, models_arg: str, dry_run: bool) -> int:
    plan = [
        f"read the ids {[q for q, _ in QUESTIONS]} from {EVAL_FILE} (question text is never written)",
        (
            "load the local index and models; record the index sha256; run local retrieve for all "
            "five BEFORE sending anything"
        ),
        f"GET {SERVICE_URL}/health (require status ok, kill_switch off)",
        (
            "POST /ask for each id in order, once each, no retry; compare every answer's files and "
            "passages (text as UTF-8 bytes) with the local retrieve"
        ),
        (
            "GET /health again; compute delta judged/in/out/spend, cost per judged question "
            "(band $0.00663 to $0.00897) and the #8 check (within 2,000 nano-dollars of "
            f"in x {PRICE_IN_NANO} + out x {PRICE_OUT_NANO})"
        ),
        f"write {OUT_DIR / 'smoke-result.json'} (ids, statuses, outcomes, seconds, byte_equal)",
    ]
    if dry_run:
        print("DRY RUN (ask): no network call, no index load")
        for line in plan:
            print(" -", line)
        for qid, expected in QUESTIONS:
            print(f"   {qid}: expected outcome {expected}")
        print(f" index={index_arg} models={models_arg}")
        return 0
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.index import load_index
    from aveto_support.search import Searcher

    started = now_utc()
    questions = load_questions()
    index_path = Path(index_arg)
    index_sha = hashlib.sha256(index_path.read_bytes()).hexdigest()
    index = load_index(index_path)
    searcher = Searcher(index, OnnxEmbedder.load(Path(models_arg), index.params.embedding))
    local = {qid: local_files(searcher, questions[qid]) for qid, _ in QUESTIONS}  # nothing sent yet
    index_matches_build = index_sha.startswith(BUILD_INGEST_SHA_PREFIX)

    status, before = http("GET", "/health")
    if status != 200 or not isinstance(before, dict) or before.get("status") != "ok" \
            or before.get("kill_switch") != "off":
        print(json.dumps({"abort": "health before", "status": status,
                          "kill_switch": before.get("kill_switch") if isinstance(before, dict) else None}))
        return 1
    results: list[dict[str, Any]] = []
    for qid, expected in QUESTIONS:
        t0 = time.monotonic()
        try:
            status, body = http("POST", "/ask", {"question": questions[qid]})  # once, no retry
        except OSError as err:
            status, body = 0, None
            outcome = f"network_error:{type(err).__name__}"
        else:
            outcome = body.get("outcome") if isinstance(body, dict) else None
        row: dict[str, Any] = {
            "id": qid, "status": status, "outcome": outcome, "expected_outcome": expected,
            "seconds": round(time.monotonic() - t0, 1), "byte_equal": None,
            "first_difference": None,
        }
        if outcome == "answer" and isinstance(body, dict):
            diff = first_difference(body.get("files") or [], local[qid])
            row["byte_equal"] = diff is None
            row["first_difference"] = diff
        results.append(row)
        print(json.dumps({k: row[k] for k in ("id", "status", "outcome", "seconds")}))
    status, after = http("GET", "/health")
    record: dict[str, Any] = {
        "start_utc": started, "end_utc": now_utc(), "index_sha256": index_sha,
        "index_matches_build_ingest_prefix": index_matches_build,
        "byte_equality_established": index_matches_build,
        "questions": results, "health_before": before, "health_after": after if status == 200 else None,
    }
    if status == 200 and isinstance(after, dict):
        record["figures"] = figures(before, after)
    write("smoke-result.json", record)
    print(json.dumps(record.get("figures", {}), sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    w = sub.add_parser("watch")
    w.add_argument("want", choices=["on", "off"])
    w.add_argument("--dry-run", action="store_true")
    a = sub.add_parser("ask")
    a.add_argument("--index", required=True)
    a.add_argument("--models", required=True)
    a.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.mode == "watch":
        return watch(args.want, args.dry_run)
    return ask(args.index, args.models, args.dry_run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
