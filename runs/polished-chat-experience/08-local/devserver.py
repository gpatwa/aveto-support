"""Local dev server for the stage 8 browser checks (never shipped, never deployed).

Run from the worktree root:
    uv run python runs/polished-chat-experience/08-local/devserver.py --port 8765 [--resting]

Instances: 8765 (browser checks), 8766 (timing only), 8767 (--resting). It loads the real index
and embedding model (the worktree's if present, else the main checkout's, read only) and answers
with a stand-in judge, so no key is needed and no model is called. `--resting` sets a monthly cap
whose daily share is below the service's floor, so `GET /` shows the resting card: the same thing
the production `ASK_MONTHLY_CAP_USD` setting does. Nothing in the product changes for this.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
MAIN = Path("/Users/gopalpatwa/opt/aveto-support")

import uvicorn

from aveto_service.app import create_app, load_runtime
from aveto_service.judge_port import JudgeCall
from aveto_service.pages import HtmlPages
from aveto_service.settings import Settings


def _pick(rel: str) -> str:
    for base in (ROOT, MAIN):
        if (base / rel).exists():
            return str(base / rel)
    raise SystemExit(f"{rel} not found in the worktree or the main checkout")


def _unanswerable() -> frozenset[str]:
    """The questions of the two spent eval sets that the docs do not answer."""
    found: set[str] = set()
    for name in ("retrieval-heldout-5", "public-gate-1"):
        data = tomllib.loads((ROOT / "evals" / f"{name}.toml").read_text("utf-8"))
        for q in data["question"]:
            if q.get("answerable") is False or q.get("kind") in ("unanswerable", "hostile"):
                found.add(" ".join(str(q["question"]).split()))
    return frozenset(found)


class DevJudge:
    """Refuses a known unanswerable question, answers every other one. Dev only."""

    def __init__(self) -> None:
        self._refuse = _unanswerable()

    def judge(self, system_prompt: str, payload: str) -> JudgeCall:
        for line in payload.splitlines():
            if line.startswith("Question: "):
                if line[len("Question: ") :] in self._refuse:
                    return JudgeCall("Q1 NOT_ANSWERABLE", 2400, 20)
                break
        return JudgeCall("Q1 ANSWERABLE", 2400, 20)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--resting", action="store_true")
    args = parser.parse_args()
    settings = Settings(
        kill_switch="off",
        api_key="",
        client_key="peer",
        monthly_cap_usd="0.000001" if args.resting else "10",
        index_path=_pick("index/docs-index.json"),
        models_path=_pick("models"),
        prompt_path=str(ROOT / "prompts" / "answerability-judge-v1.txt"),
    )
    runtime = load_runtime(settings)
    app = create_app(runtime, DevJudge(), settings, html=HtmlPages(runtime))
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="critical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
