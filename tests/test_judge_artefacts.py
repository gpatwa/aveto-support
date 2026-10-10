"""Static and deterministic checks on the judge's agent, skill and transport dir.

The hook test here proves the hook COMMAND refuses every input. It does NOT
show that Claude Code runs it for the judge: APPROVAL_RECORD-5 Amendment 2 is
satisfied only by the live refusal probe (a later QA stage), not by this file.
Nothing here spawns a model; /bin/sh is spawned only by the hook test.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from aveto_support import judge

ROOT = Path(__file__).parent.parent
APPROVED_PROMPT_SHA256 = (
    "24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427"
)
PROMPT = ROOT / "prompts" / "answerability-judge-v1.txt"
AGENT = ROOT / ".claude" / "agents" / "aveto-answerability-judge.md"
SKILL = ROOT / ".claude" / "skills" / "aveto-judge" / "SKILL.md"

# Tool names from the official tools reference (02d-doc-facts.md), Agent and
# Task first, then the docs' order. Written out here on purpose.
DENY_LIST = (
    "Agent, Task, Bash, Read, Write, Edit, WebFetch, WebSearch, Artifact, AskUserQuestion, "
    "CronCreate, CronDelete, CronList, EndConversation, EnterPlanMode, EnterWorktree, "
    "ExitPlanMode, ExitWorktree, Glob, Grep, LSP, ListAgents, ListMcpResourcesTool, Monitor, "
    "NotebookEdit, PowerShell, PushNotification, ReadMcpResourceTool, RemoteTrigger, "
    "ReportFindings, ScheduleWakeup, SendFeedback, SendMessage, SendUserFile, "
    "ShareOnboardingGuide, Skill, SubagentHandback, TaskCreate, TaskGet, TaskList, "
    "TaskOutput, TaskStop, TaskUpdate, TodoWrite, ToolSearch, WaitForMcpServers, Workflow"
)
HOOK_COMMAND = 'echo "aveto-answerability-judge has no tools" >&2; exit 2'
FRONTMATTER = f"""---
name: aveto-answerability-judge
description: Product-local answerability judge, used only by the /aveto-judge command. Never delegate to it otherwise. Not a pack role.
disallowedTools: {DENY_LIST}
model: claude-haiku-5-5
hooks:
  PreToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: '{HOOK_COMMAND}'
          timeout: 10
---
"""
SKILL_FRONTMATTER = """---
name: aveto-judge
description: Judge whether the docs search results answer a question (attended; runs only when you type it).
disable-model-invocation: true
---
"""
BUDGET_SENTENCE = (
    "The pack's `budget-guard.mjs` is a `PreToolUse` hook on the `Agent` tool, so it fires on "
    "every Agent spawn, including each judge spawn made by `/aveto-judge`, inside a slice or "
    "not. It scans `runs/` in this checkout and in every worktree, and if any in-progress slice "
    'there is at or over its budget, it may "ask" on the judge spawn, naming that slice. It '
    "asks; it does not block, and it cannot tell a judge spawn from a stage spawn. With no "
    "`runs/` directory, or no `Status` line in a `STATE.md`, it allows silently. If you "
    "decline the ask, no judge runs, and `judge-apply` prints `judge error`."
)


def _top_level_keys(frontmatter: str) -> list[str]:
    lines = frontmatter.splitlines()[1:-1]  # drop the two --- fences
    return [ln.split(":", 1)[0] for ln in lines if ln and not ln[0].isspace()]


def test_prompt_file_hash() -> None:
    digest = hashlib.sha256(PROMPT.read_bytes()).hexdigest()
    assert digest == judge.PROMPT_SHA256 == APPROVED_PROMPT_SHA256


def test_prompt_file_shape() -> None:
    data = PROMPT.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf")
    assert data.count(b"\n") == 1 and data.endswith(b"\n")
    assert data.startswith(b"You judge documentation search results.")


def test_agent_definition() -> None:
    assert AGENT.parent.name == "agents" and AGENT.parent.parent.name == ".claude"
    text = AGENT.read_bytes().decode("utf-8")
    assert text.startswith(FRONTMATTER)  # (1) byte for byte, final deny list
    assert _top_level_keys(FRONTMATTER) == [
        "name",
        "description",
        "disallowedTools",
        "model",
        "hooks",
    ]  # (2) no `tools` key
    assert _top_level_keys(text[: len(FRONTMATTER)]) == _top_level_keys(FRONTMATTER)
    assert text[len(FRONTMATTER) :] == "\n" + PROMPT.read_bytes().decode("utf-8")  # (3)
    names = DENY_LIST.split(", ")
    assert "Agent" in names and "Task" in names
    assert len(names) == len(set(names))
    assert "model: claude-haiku-5-5\n" in text
    assert "model: haiku" not in text
    assert "\ntools:" not in text.split("\n---\n", 1)[0]


def test_deny_hook_refuses_every_input(tmp_path: Path) -> None:
    text = AGENT.read_text(encoding="utf-8")
    assert (
        f"command: '{HOOK_COMMAND}'" in text
    )  # the string run below is the one in the file
    names = [*DENY_LIST.split(", "), "mcp__probe__fetch", "Write", "FutureTool", ""]

    def event(name: str, with_agent_type: bool) -> bytes:
        payload: dict[str, object] = {
            "hook_event_name": "PreToolUse",
            "tool_name": name,
            "tool_input": {"command": "touch x", "file_path": "/x"},
            "session_id": "s",
            "cwd": str(tmp_path),
        }
        if with_agent_type:
            payload["agent_id"] = "a1"
            payload["agent_type"] = "aveto-answerability-judge"
        return json.dumps(payload).encode()

    inputs = [event(n, t) for n in names for t in (True, False)]
    inputs += [b"{not json", b"", b"\x00\xff"]
    for data in inputs:
        proc = subprocess.run(
            ["/bin/sh", "-c", HOOK_COMMAND],
            input=data,
            capture_output=True,
            timeout=10,
            check=False,
        )
        assert proc.returncode == 2, data
        assert proc.stderr.strip() == b"aveto-answerability-judge has no tools", data
        assert proc.stdout == b"", data


def test_command_definition() -> None:
    """The /aveto-judge command, shipped as a skill (APPROVAL_RECORD-7)."""
    assert not (ROOT / ".claude" / "commands" / "aveto-judge.md").exists()
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith(SKILL_FRONTMATTER)
    assert _top_level_keys(SKILL_FRONTMATTER) == [
        "name",
        "description",
        "disable-model-invocation",
    ]
    assert "allowed-tools" not in text and "model:" not in SKILL_FRONTMATTER
    body = text[len(SKILL_FRONTMATTER) :]
    for needed in (
        "aveto-answerability-judge",
        "judge-input",
        "judge-apply",
        ".aveto-judge/",
        "claude-haiku-5-5",
        "$ARGUMENTS",
        "do not pass a `model` parameter",
        BUDGET_SENTENCE,
        "The judge's deny hook runs only in a workspace whose trust you have accepted.",
    ):
        assert needed in body, needed
    # Only prohibitions may mention `claude -p`; the other strings never appear.
    for banned in ("API_KEY", "--ranking"):
        assert banned not in body, banned
    for line in body.splitlines():
        if "claude -p" in line or "general-purpose" in line:
            assert "Never" in line, line


def test_transport_dir_ignored() -> None:
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".aveto-judge/" in lines


@pytest.mark.parametrize("path", [AGENT, SKILL])
def test_artefacts_are_not_empty(path: Path) -> None:
    assert path.stat().st_size > 200
