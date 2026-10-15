"""P4: what a shell would run if the harness substitutes $ARGUMENTS textually into the
aveto-judge-seen `!` line. The program `uv run ... seen_payload.py` is replaced by
`printf '[%s]\n'` so nothing but printf and echo runs. Offline; no judge."""
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[3]
line = (root / ".claude/skills/aveto-judge-seen/SKILL.md").read_text().strip().splitlines()[-1]
cmd_tpl = line[2:-1]  # strip !` and `
print("template:", cmd_tpl)
stub = cmd_tpl.replace('uv run -q --project "${CLAUDE_PROJECT_DIR}" python "${CLAUDE_SKILL_DIR}/seen_payload.py"', "printf '[%s]\\n'")
assert stub != cmd_tpl
for arg in ["r101", "r101; echo INJECTED", "r101$(echo INJECTED)", "r101' ; echo INJECTED ; '", "r101'$(echo INJECTED)'"]:
    cmd = stub.replace("$ARGUMENTS", arg)
    out = subprocess.run(["/bin/sh", "-c", cmd], capture_output=True, text=True, timeout=10)
    print(f"arg {arg!r:32} -> sh argv/out {out.stdout.strip()!r}")
