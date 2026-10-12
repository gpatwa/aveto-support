"""Print the answerability judge's payload for one committed seen-set question.

Eval-only helper of the aveto-judge-seen skill. Input: one run id (r001..r093).
Fail closed: an id that does not match ^r[0-9]{3}$, or is not a table in
seen-check/key/key.toml, or has no line in a batch file, prints one refusal
line to stdout and stderr and exits 2 (a non-zero exit aborts the skill, so no
judge starts). It reads key.toml for membership only, never an answer field.

On success it writes the question (from the batch line, id stripped) to
seen-check/q/<id>.txt and prints `judge-input --question-file` stdout, unchanged.
The `input sha256:` line on judge-input's stderr is discarded here: stderr
would be merged into the injected text.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEEN = ROOT / "runs" / "docs-answerability" / "seen-check"
ID_RE = re.compile(r"^r[0-9]{3}$")  # matched with fullmatch on a str without newline


class Refusal(Exception):
    pass


def key_ids(seen: Path = SEEN) -> set[str]:
    with (seen / "key" / "key.toml").open("rb") as handle:
        return set(tomllib.load(handle))


def question_for(run_id: str, seen: Path = SEEN) -> str:
    for batch in sorted(seen.glob("batch-*.txt")):
        for line in batch.read_text(encoding="utf-8").splitlines():
            head, _, rest = line.partition(" ")
            if head == run_id and rest.strip():
                return rest.strip()
    raise Refusal(f"refused: no batch line for {run_id}")


def prepare(raw: str, seen: Path = SEEN) -> Path:
    """Validate the id and write its question file. Returns the file's path."""
    if "\n" in raw or "\r" in raw or not ID_RE.fullmatch(raw):
        raise Refusal("refused: the argument must be one run id such as r001")
    if raw not in key_ids(seen):
        raise Refusal(f"refused: {raw} is not a committed seen-set id")
    question = question_for(raw, seen)
    target = seen / "q" / f"{raw}.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(question, encoding="utf-8")
    return target


def judge_input_command(question_file: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "aveto_support",
        "judge-input",
        "--question-file",
        str(question_file),
    ]


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        message = "refused: exactly one run id is required"
        print(message)
        print(message, file=sys.stderr)
        return 2
    try:
        question_file = prepare(argv[0])
    except Refusal as exc:
        print(exc)
        print(exc, file=sys.stderr)
        return 2
    done = subprocess.run(  # fixed argv, no shell
        judge_input_command(question_file),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if done.returncode != 0:
        message = f"refused: judge-input failed (exit {done.returncode})"
        print(message)
        print(message, file=sys.stderr)
        return 2
    sys.stdout.flush()
    sys.stdout.buffer.write(done.stdout)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
