"""Live checks for polished-chat-experience (tech spec 12.3, 12.4, 12.6). WRITTEN, NOT RUN by stage 4.

Run from the worktree root (not curl; Charter C6.P):
    uv run python runs/polished-chat-experience/13-live/live.py check new|old
    uv run python runs/polished-chat-experience/13-live/live.py watch new|old
    uv run python runs/polished-chat-experience/13-live/live.py ask --index <path> --models <path>
    uv run python runs/polished-chat-experience/13-live/live.py cold

Takes no credential and no argument that could carry one. Standard-library HTTP only, plus the
local `aveto_support` for the byte comparison in `ask`. It calls no `az` command and no host
other than SERVICE_URL, never retries a POST /ask, and writes ids, codes, counts and times only:
never question text, passage text or a reply body. `ask` sends exactly seven questions.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SERVICE_URL = "https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io"
ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "runs/polished-chat-experience/13-live"
HTTP_TIMEOUT_S = 90
WATCH_TIMEOUT_S = 600
WATCH_POLL_S = 2
COLD_TIMEOUT_S = 180
EXPECTED_INGEST_SHA = "f36ef5d4fbf4b3f5542f59381867d992fe6619a6450cbbb19526f8493804a756"
SKIP_LINK = "Skip to the question box"
EXPECTED_SECURITY = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}
SUGGESTIONS = [  # slot, eval set, id: the texts are read from the eval files, never written out
    ("A1", "retrieval-heldout-5", "g01"),
    ("A2", "retrieval-heldout-5", "g03"),
    ("A3", "retrieval-heldout-5", "g04"),
    ("R1", "retrieval-heldout-5", "gu18"),
]
# (number, path, set, id, expected outcome); #7 is the form path
ASK_PLAN = [
    (1, "json", "retrieval-heldout-5", "g01", "answer"),
    (2, "json", "retrieval-heldout-5", "g03", "answer"),
    (3, "json", "retrieval-heldout-5", "g04", "answer"),
    (4, "json", "retrieval-heldout-5", "gu18", "no_confident_match"),
    (5, "json", "public-gate-1", "p05", "answer"),
    (6, "json", "retrieval-heldout-5", "gu15", "no_confident_match"),
    (7, "form", "retrieval-heldout-5", "g01", "answer"),
]
COUNT_LABELS = ("Visits", "Questions asked", "Answered", "Not answered", "Clicks to the docs")


def now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def http(
    method: str, path: str, *, body: bytes | None = None, content_type: str | None = None,
    timeout: float = HTTP_TIMEOUT_S,
) -> tuple[int, dict[str, str], bytes]:
    """One request to SERVICE_URL, redirects not followed. Never retries."""
    headers = {"Content-Type": content_type} if content_type else {}
    request = urllib.request.Request(SERVICE_URL + path, data=body, method=method, headers=headers)
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers.items()), err.read()


def get_json(path: str) -> tuple[int, Any]:
    status, _, raw = http("GET", path)
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, None


def write(name: str, record: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def eval_question(set_name: str, qid: str) -> str:
    data = tomllib.loads((ROOT / "evals" / f"{set_name}.toml").read_text("utf-8"))
    for q in data["question"]:
        if q["id"] == qid:
            return str(q["question"])
    raise SystemExit(f"{set_name} has no {qid}")


def security_ok(headers: dict[str, str]) -> bool:
    lowered = {k.lower(): v for k, v in headers.items()}
    return all(lowered.get(k.lower()) == v for k, v in EXPECTED_SECURITY.items())


# --- check ---------------------------------------------------------------------------------


def check(which: str) -> int:
    started = now_utc()
    checks: dict[str, bool] = {}
    status, health = get_json("/health")
    checks["health_200_kill_switch_off"] = (
        status == 200 and isinstance(health, dict) and health.get("kill_switch") == "off"
    )
    status, headers, raw = http("GET", "/")
    page = html.unescape(raw.decode("utf-8", "replace"))
    checks["root_200"] = status == 200
    sc_status, sc_headers, _ = http("GET", "/scorecard")
    if which == "new":
        checks["root_has_skip_link"] = SKIP_LINK in page
        checks["root_has_four_suggestions"] = all(
            eval_question(s, i) in page for _, s, i in SUGGESTIONS
        )
        checks["scorecard_200"] = sc_status == 200
        checks["enhance_js_200"] = http("GET", "/static/enhance.js")[0] == 200
        checks["security_headers_on_root"] = security_ok(headers)
        checks["security_headers_on_scorecard"] = security_ok(sc_headers)
        w_status, _, w_raw = http("POST", "/warm")
        checks["warm_ready_true"] = w_status == 200 and w_raw == b'{"ready":true}'
    else:
        checks["root_has_no_skip_link"] = SKIP_LINK not in page
        checks["scorecard_404"] = sc_status == 404
    ok = all(checks.values())
    record = {"mode": f"check {which}", "start_utc": started, "end_utc": now_utc(), "checks": checks, "ok": ok}
    write(f"check-{which}.json", record)
    print(json.dumps(record, sort_keys=True))
    return 0 if ok else 1


# --- watch ---------------------------------------------------------------------------------


def serving(which: str) -> bool:
    try:
        h_status, _ = get_json("/health")
        s_status = http("GET", "/scorecard", timeout=15)[0]
    except OSError:
        return False
    if which == "new":
        return h_status == 200 and s_status == 200
    return h_status == 200 and s_status == 404


def watch(which: str) -> int:
    started = now_utc()
    t0 = time.monotonic()
    first_seen: float | None = None
    consecutive = 0
    polls = 0
    reached = False
    while time.monotonic() - t0 < WATCH_TIMEOUT_S:
        polls += 1
        if serving(which):
            first_seen = first_seen if first_seen is not None else time.monotonic() - t0
            consecutive += 1
            if consecutive >= 3:
                reached = True
                break
        else:
            consecutive = 0
            first_seen = None
        time.sleep(WATCH_POLL_S)
    record = {
        "mode": f"watch {which}", "start_utc": started, "end_utc": now_utc(), "polls": polls,
        "reached": reached,
        "seconds_to_first_of_three": None if first_seen is None else round(first_seen, 1),
        "seconds_to_confirmed": round(time.monotonic() - t0, 1) if reached else None,
    }
    n = 1
    while (OUT_DIR / f"watch-{which}-{n}.json").exists():
        n += 1
    write(f"watch-{which}-{n}.json", record)
    print(json.dumps(record, sort_keys=True))
    return 0 if reached else 1


# --- ask -----------------------------------------------------------------------------------


class _Counts(HTMLParser):
    """`dt` text to the text of the `dd.value` after it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: dict[str, str] = {}
        self._in: str | None = None
        self._label = ""
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = (dict(attrs).get("class") or "").split()
        if tag == "dt":
            self._in = "dt"
        elif tag == "dd" and "value" in classes:
            self._in = "value"
        else:
            return
        self._buf = []

    def handle_data(self, data: str) -> None:
        if self._in is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("dt", "dd") and self._in is not None:
            text = "".join(self._buf).strip()
            if self._in == "dt":
                self._label = text
            else:
                self.rows[self._label] = text
            self._in = None


class _Passages(HTMLParser):
    """The text of every `pre.passage > code`, in order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.texts: list[str] = []
        self._in_pre = False
        self._in_code = False
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "pre" and "passage" in (dict(attrs).get("class") or "").split():
            self._in_pre = True
        elif tag == "code" and self._in_pre:
            self._in_code = True
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self._in_code:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and self._in_code:
            self.texts.append("".join(self._buf))
            self._in_code = False
        elif tag == "pre":
            self._in_pre = False


def read_counts() -> dict[str, int] | None:
    status, _, raw = http("GET", "/scorecard")
    if status != 200:
        return None
    parser = _Counts()
    parser.feed(raw.decode("utf-8", "replace"))
    try:
        return {k: int(parser.rows[k]) for k in COUNT_LABELS}
    except (KeyError, ValueError):
        return None


def local_files(searcher: Any, question: str) -> list[dict[str, Any]]:
    from aveto_support import judge
    from aveto_support.search import retrieve

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


def ask(index_arg: str, models_arg: str) -> int:
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.index import load_index
    from aveto_support.search import Searcher

    started = now_utc()
    index_path = Path(index_arg)
    index_sha = hashlib.sha256(index_path.read_bytes()).hexdigest()
    index = load_index(index_path)
    searcher = Searcher(index, OnnxEmbedder.load(Path(models_arg), index.params.embedding))
    established = index_sha == EXPECTED_INGEST_SHA
    questions = {n: eval_question(s, i) for n, _, s, i, _ in ASK_PLAN}
    local = {n: local_files(searcher, q) for n, q in questions.items()}  # before anything is sent
    status, before = get_json("/health")
    if status != 200 or not isinstance(before, dict) or before.get("kill_switch") != "off":
        print(json.dumps({"abort": "health before", "status": status}))
        return 1
    counts_before = read_counts()
    rows: list[dict[str, Any]] = []
    for n, path, set_name, qid, expected in ASK_PLAN:
        t0 = time.perf_counter()
        row: dict[str, Any] = {
            "n": n, "path": path, "id": qid, "set": set_name, "expected_outcome": expected,
            "status": None, "outcome": None, "seconds": None, "byte_equal": None,
            "first_difference": None, "behaviour_ok": False,
        }
        try:
            if path == "json":
                st, _, raw = http(
                    "POST", "/ask", body=json.dumps({"question": questions[n]}).encode("utf-8"),
                    content_type="application/json",
                )
                body = json.loads(raw)
                row["status"], row["outcome"] = st, body.get("outcome")
                row["behaviour_ok"] = st == 200 and body.get("outcome") in ("answer", "no_confident_match")
                if body.get("outcome") == "answer":
                    diff = first_difference(body.get("files") or [], local[n])
                    row["byte_equal"], row["first_difference"] = diff is None, diff
            else:
                form = urllib.parse.urlencode({"question": questions[n]}).encode("ascii")
                st, headers, _ = http(
                    "POST", "/ask", body=form, content_type="application/x-www-form-urlencoded"
                )
                location = headers.get("Location") or headers.get("location") or ""
                row["status"] = st
                if st == 303 and location.startswith("/result/"):
                    st2, _, page = http("GET", location.split("#")[0])
                    parsed = _Passages()
                    parsed.feed(page.decode("utf-8", "replace"))
                    wanted = [p["text"] for f in local[n] for p in f["passages"]]
                    same = [t.encode("utf-8") for t in parsed.texts] == [w.encode("utf-8") for w in wanted]
                    row["outcome"] = "answer" if parsed.texts else "no_passages"
                    row["result_status"] = st2
                    row["byte_equal"] = same
                    row["behaviour_ok"] = st2 == 200 and same
        except (OSError, ValueError) as err:
            row["outcome"] = f"error:{type(err).__name__}"
        row["seconds"] = round(time.perf_counter() - t0, 2)
        rows.append(row)
        print(json.dumps({k: row[k] for k in ("n", "id", "status", "outcome", "seconds")}))
    status, after = get_json("/health")
    counts_after = read_counts()
    behaviour_failure = any(not r["behaviour_ok"] for r in rows) or (
        established and any(r["byte_equal"] is False for r in rows)
    )
    warm = [r["seconds"] for r in rows[1:] if isinstance(r["seconds"], float)]
    record = {
        "start_utc": started, "end_utc": now_utc(), "index_sha256": index_sha,
        "byte_equality_established": established, "questions": rows,
        "outcome_differs_from_expected": [r["n"] for r in rows if r["outcome"] != r["expected_outcome"]],
        "behaviour_failure": behaviour_failure,
        "warm_requests_2_to_7": {
            "n": len(warm),
            "median_seconds": sorted(warm)[len(warm) // 2] if warm else None,
            "slowest_seconds": max(warm) if warm else None,
        },
        "health_before": before, "health_after": after if status == 200 else None,
        "counts_before": counts_before, "counts_after": counts_after,
        "counts_delta": None if counts_before is None or counts_after is None
        else {k: counts_after[k] - counts_before[k] for k in COUNT_LABELS},
    }
    write("ask-result.json", record)
    print(json.dumps({"behaviour_failure": behaviour_failure, "established": established}))
    return 1 if behaviour_failure else 0


# --- cold ----------------------------------------------------------------------------------


def cold() -> int:
    started = now_utc()
    t0 = time.perf_counter()
    status, _, _ = http("GET", "/health", timeout=COLD_TIMEOUT_S)
    first = time.perf_counter() - t0
    t1 = time.perf_counter()
    page_status, _, _ = http("GET", "/")
    page = time.perf_counter() - t1
    record = {
        "date_utc": started,
        "method": (
            "One GET /health with a 180 s timeout after the replica had scaled to zero with no "
            "request sent, timed from send to the 200 (the method of the 30.8 s record), then "
            "one GET / timed."
        ),
        "health_status": status, "health_seconds": round(first, 1),
        "root_status": page_status, "root_seconds": round(page, 2),
    }
    write("cold.json", record)
    print(json.dumps(record, sort_keys=True))
    return 0 if status == 200 else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("check", "watch"):
        s = sub.add_parser(name)
        s.add_argument("which", choices=["new", "old"])
    a = sub.add_parser("ask")
    a.add_argument("--index", required=True)
    a.add_argument("--models", required=True)
    sub.add_parser("cold")
    args = parser.parse_args(argv)
    if args.mode == "check":
        return check(args.which)
    if args.mode == "watch":
        return watch(args.which)
    if args.mode == "ask":
        return ask(args.index, args.models)
    return cold()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
