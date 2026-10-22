"""Gate scorer for public-gate-1 (run artefact, not product code). Scores once: it refuses to
post a question whose response file already exists. Usage:
  python3 score.py post p01 p02 ...   # post these ids through the live service, save responses
  python3 score.py report             # apply the pre-registered bars to what is saved
"""
import json
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE.parent.parent.parent / "evals" / "public-gate-1.toml"
URL = "https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io"
RESP = HERE / "responses"
with GATE.open("rb") as _f:
    Q = {q["id"]: q for q in tomllib.load(_f)["question"]}

def get(path, timeout=150):
    with urllib.request.urlopen(URL + path, timeout=timeout) as r:
        return json.load(r)

def post(question):
    req = urllib.request.Request(URL + "/ask", data=json.dumps({"question": question}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    t = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=150) as r:
            return r.status, json.load(r), time.monotonic() - t
    except urllib.error.HTTPError as e:
        return e.code, json.load(e), time.monotonic() - t

def do_post(ids):
    before = get("/health")
    print("health before:", before)
    for i in ids:
        f = RESP / f"{i}.json"
        if f.exists():
            print(i, "already scored: refusing to post again"); continue
        status, body, secs = post(Q[i]["question"])
        f.write_text(json.dumps({"id": i, "kind": Q[i]["kind"], "http": status, "seconds": round(secs, 3),
                                 "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "response": body}, indent=1))
        n = sum(len(x["passages"]) for x in body.get("files", []))
        print(i, Q[i]["kind"], status, body.get("outcome"), "passages", n, f"{secs:.2f}s", flush=True)
        time.sleep(2)
    after = get("/health")
    print("health after:", after)
    (HERE / f"health-{ids[0]}-{ids[-1]}.json").write_text(json.dumps({"before": before, "after": after}, indent=1))

def report():
    rows, a_ok, a_n, n_ok, n_n = [], 0, 0, 0, 0
    for i, q in Q.items():
        f = RESP / f"{i}.json"
        if not f.exists(): rows.append((i, q["kind"], "NOT RUN", "")); continue
        r = json.loads(f.read_text()); b = r["response"]; o = b.get("outcome")
        files = [x["path"] for x in b.get("files", [])]
        if q["kind"] == "answerable":
            a_n += 1
            hit = o == "answer" and any(p in q["sources"] for p in files)
            a_ok += hit
            rows.append((i, "answerable", "PASS" if hit else "FAIL", f"{o}; files {files[:5]}; listed {q['sources']}"))
        else:
            n_n += 1
            ok = o in ("no_confident_match", "empty_question", "unusable_question", "too_long", "bad_request", "body_too_large") and not b.get("files")
            n_ok += ok
            rows.append((i, q["kind"], "PASS" if ok else "FAIL", f"{o}; passages {sum(len(x['passages']) for x in b.get('files', []))}"))
    for r in rows: print(*r, sep=" | ")
    print(f"\nBar 1 (unanswerable + hostile, no passage shown, no judge error): {n_ok}/{n_n}  need {n_n}/{n_n} (all of 10)")
    print(f"Bar 2 (answerable, a listed source shown): {a_ok}/{a_n}  need >= 8/10")
    secs = sorted(json.loads(p.read_text())["seconds"] for p in RESP.glob("*.json"))
    if secs: print(f"seconds per request: median {secs[len(secs)//2]:.2f}, slowest {secs[-1]:.2f}, n={len(secs)}")

if __name__ == "__main__":
    {"post": lambda: do_post(sys.argv[2:]), "report": report}[sys.argv[1]]()
