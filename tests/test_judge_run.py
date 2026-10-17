"""tools/judge_run.py: sample derivation, transcript reading, the audit's void rules, applying
replies through the product's judge-apply, and offline behaviour.

Everything runs on a fake index, FakeEmbedder and synthetic transcripts in tmp_path: no
network, no process, no model, no key.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import socket
import subprocess
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from conftest import COMMIT
from test_judge import FAKE, ROOT, write_idx

from aveto_support import judge
from aveto_support.__main__ import main as product_main
from aveto_support.evaluate import load_eval_set
from aveto_support.index import load_index
from aveto_support.search import Searcher
from tools import judge_run as jr

LINE = "Base directory for this skill: /x/.claude/skills/aveto-judge-seen"
LINE_LEN = len(LINE)
S1, S2 = "s1.toml", "s2.toml"


def _q(qid: str, text: str, source: str | None) -> str:
    if source is None:
        return f'[[question]]\nid = "{qid}"\nquestion = "{text}"\nanswerable = false\n'
    return f'[[question]]\nid = "{qid}"\nquestion = "{text}"\nsources = ["{source}"]\nwhere = "w"\n'


CATS, LAST = "pets/cats.md", "zzz/last.md"
SET1 = [
    ("a1", "cats purr", CATS), ("a2", "cats purr loudly", LAST), ("a3", "cats chase mice", CATS),
    ("u1", "quantum spaceship", None),
]
SET2 = [
    ("a4", "do cats purr", CATS), ("u2", "rocket fuel", None), ("a5", "cats purr softly", CATS),
    ("u3", "ice cream flavours", None), ("a6", "cats purr at night", CATS),
]
GOOD_REPLY = {"ANSWERABLE": "Q1 ANSWERABLE shows it", "NOT_ANSWERABLE": "Q1 NOT_ANSWERABLE no match"}


@dataclass
class World:
    root: Path
    rows: list[jr.Row]
    check: Path
    sample_eval: Path
    searcher: Searcher

    def payload(self, run_id: str) -> str:
        row = next(r for r in self.rows if r.run_id == run_id)
        return judge.format_judge_input(judge.retrieve_for_judge(self.searcher, row.question))

    def want(self, run_id: str) -> str:
        row = next(r for r in self.rows if r.run_id == run_id)
        return "NOT_ANSWERABLE" if row.entry.get("answerable") is False else "ANSWERABLE"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> World:
    monkeypatch.chdir(tmp_path)
    write_idx(tmp_path)
    for name, items in ((S1, SET1), (S2, SET2)):
        (tmp_path / name).write_text(
            f'pinned_commit = "{COMMIT}"\n' + "".join(_q(i, t, s) for i, t, s in items)
        )
    searcher = Searcher(load_index(tmp_path / "i.json"), FAKE)
    rows = jr.derive_sample(
        searcher, tmp_path, sets=(S1, S2), expected_u=(1, 2), expected_h=(2, 3)
    )
    check = tmp_path / "check"
    jr.write_check_dir(rows, check, "0" * 64, COMMIT)
    return World(tmp_path, rows, check, check / "sample-eval.toml", searcher)


# --- T1: derivation ----------------------------------------------------------------------


def test_derive_order_parity_and_smoke(world: World) -> None:
    got = [(r.run_id, r.eval_id, r.role) for r in world.rows]
    assert got == [
        ("r001", "a1", "sample"), ("r002", "u1", "sample"), ("r003", "a4", "sample"),
        ("r004", "u2", "sample"), ("r005", "u3", "sample"), ("r006", "a6", "sample"),
        ("r049", "a3", "smoke"),
    ]
    assert world.rows[0].set_path == S1 and world.rows[2].set_path == S2


@pytest.mark.parametrize(
    ("u", "h"), [((2, 2), (2, 3)), ((1, 2), (3, 2)), ((1, 2), (2, 4)), ((1, 3), (2, 3))]
)
def test_derive_refuses_when_counts_are_off(
    world: World, u: tuple[int, int], h: tuple[int, int]
) -> None:
    with pytest.raises(jr.SampleError, match="nothing written"):
        jr.derive_sample(world.searcher, world.root, sets=(S1, S2), expected_u=u, expected_h=h)


def test_derive_refuses_mixed_commits(world: World) -> None:
    text = (world.root / S2).read_text().replace(COMMIT, "f" * 40)
    (world.root / S2).write_text(text)
    with pytest.raises(jr.SampleError, match="one commit"):
        jr.derive_sample(world.searcher, world.root, sets=(S1, S2), expected_u=(1, 2), expected_h=(2, 3))


def test_write_check_dir_refuses_existing_key(world: World, tmp_path: Path) -> None:
    before = (world.check / "key" / "key.toml").read_bytes()
    with pytest.raises(jr.SampleError, match="never redrawn"):
        jr.write_check_dir(world.rows, world.check, "1" * 64, COMMIT)
    assert (world.check / "key" / "key.toml").read_bytes() == before


def test_key_has_membership_only_and_no_label(world: World) -> None:
    text = (world.check / "key" / "key.toml").read_text()
    with (world.check / "key" / "key.toml").open("rb") as handle:
        key = tomllib.load(handle)
    assert list(key) == [r.run_id for r in world.rows]
    assert all(set(t) == {"set", "id"} for t in key.values())
    body = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
    assert "answerable" not in body and "sources" not in body and "hard_negative" not in body
    batch = (world.check / "batch-1.txt").read_text().splitlines()
    assert batch[0] == f"r001 {world.rows[0].question}" and len(batch) == 7


def test_sample_eval_round_trip(world: World) -> None:
    with world.sample_eval.open("rb") as handle:
        got = tomllib.load(handle)
    assert got["pinned_commit"] == COMMIT
    assert got["question"] == [r.entry for r in world.rows if r.role == "sample"]
    assert [q["id"] for q in got["question"]] == ["a1", "u1", "a4", "u2", "u3", "a6"]
    assert len(load_eval_set(world.sample_eval).questions) == 6  # the product's loader accepts it


@pytest.mark.parametrize(
    "text", ['plain', 'quote " and \\ backslash', "tab\tand\nnewline", "del\x7f", "ünï — «x»", "[a]\n# b"]
)
def test_toml_string_round_trip(text: str) -> None:
    assert tomllib.loads(f"k = {jr.toml_str(text)}\n")["k"] == text


def test_add_set(world: World, tmp_path: Path) -> None:
    gate = tmp_path / "gate.toml"
    gate.write_text(
        f'pinned_commit = "{COMMIT}"\n'
        '[[question]]\nid = "g1"\nquestion = "cats purr"\nsources = ["pets/cats.md"]\n'
        '[[question]]\nid = "g2"\nquestion = "rocket fuel"\nanswerable = false\n'
    )
    with pytest.raises(jr.SampleError, match="r999"):
        jr.add_set(gate, world.check, first=999)
    assert not (world.check / "batch-2.txt").exists()
    rows = jr.add_set(gate, world.check)
    assert [r.run_id for r in rows] == ["r101", "r102"]
    assert (world.check / "batch-2.txt").read_text() == "r101 cats purr\nr102 rocket fuel\n"
    key = jr.load_key(world.check)
    assert key["r101"] == (str(gate), "g1") and "r049" in key
    assert "answerable" not in (world.check / "key" / "key.toml").read_text().split("Gate set")[1]
    with pytest.raises(jr.SampleError, match="already exists"):
        jr.add_set(gate, world.check)


# --- synthetic transcripts -------------------------------------------------------------------


def write_spawn(
    directory: Path,
    agent: str,
    payload: str | None,
    reply: str | None,
    *,
    model: str = jr.JUDGE_MODEL,
    tools: tuple[str, ...] = (),
    tool_use: bool = False,
    agent_type: str = jr.JUDGE_AGENT,
    line: str = LINE,
    usage: tuple[int, int, int, int] = (2, 100, 0, 10),
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"agent-{agent}"
    (directory / f"{stem}.meta.json").write_text(json.dumps({"agentType": agent_type}))
    (directory / f"{stem}.prefix.json").write_text(json.dumps({"state": {"toolNames": list(tools)}}))
    prompt = line + "\n\n" + (payload or "")
    recs: list[dict[str, object]] = [
        {"type": "user", "message": {"role": "user", "content": prompt}},
        {"type": "attachment", "attachment": {}},
    ]
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    content: list[dict[str, object]] = []
    if tool_use:
        content.append({"type": "tool_use", "id": "t1", "name": "Bash", "input": {}})
    if reply is not None:
        content.append({"type": "text", "text": reply})
    recs.append(
        {
            "type": "assistant",
            "message": {
                "id": "m1", "role": "assistant", "model": model, "content": content,
                "usage": dict(zip(keys, usage, strict=True)),
            },
        }
    )
    (directory / f"{stem}.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\n")


def write_batch(w: World, directory: Path, replies: dict[str, str | None] | None = None) -> None:
    for row in w.rows:
        reply = GOOD_REPLY[w.want(row.run_id)] if replies is None else replies.get(row.run_id)
        if replies is not None and row.run_id not in replies:
            reply = GOOD_REPLY[w.want(row.run_id)]
        write_spawn(directory, f"a{row.run_id}", w.payload(row.run_id), reply)


def run_record(w: World, directory: Path, stage: str = "stage", tools: tuple[str, ...] = ()) -> jr.RecordResult:
    return jr.record(
        directory, w.check, w.sample_eval, w.root / stage, tools,
        embedder=FAKE, index=w.root / "i.json", root=w.root, expect_line_len=LINE_LEN,
    )


# --- T2: read_spawn ------------------------------------------------------------------------------


def test_read_spawn_fields(world: World, tmp_path: Path) -> None:
    d = tmp_path / "sub"
    write_spawn(d, "x1", world.payload("r001"), "thinking\nQ1 ANSWERABLE ok", tools=("A", "B"), usage=(2, 100, 50, 10))
    s = jr.read_spawn(d / "agent-x1.jsonl")
    assert (s.agent_id, s.agent_type, s.models) == ("x1", jr.JUDGE_AGENT, (jr.JUDGE_MODEL,))
    assert s.offered_tools == ("A", "B") and s.tool_uses == 0
    assert s.base_line_len == LINE_LEN and s.layout_ok and s.payload == world.payload("r001")
    assert s.reply == "thinking\nQ1 ANSWERABLE ok"
    assert (s.requests, s.peak) == (1, 162)
    assert s.in_equiv == pytest.approx(2 + 125 + 5 + 10)


def test_read_spawn_counts_tool_use_and_missing_reply(world: World, tmp_path: Path) -> None:
    write_spawn(tmp_path / "s", "x2", world.payload("r001"), None, tool_use=True)
    s = jr.read_spawn(tmp_path / "s" / "agent-x2.jsonl")
    assert s.tool_uses == 1 and s.reply is None


def test_read_spawn_layout_forms(world: World, tmp_path: Path) -> None:
    for name, line in (
        ("nopath", "Base directory for this skill: relative/.claude/skills/aveto-judge-seen"),
        ("wrongskill", "Base directory for this skill: /x/.claude/skills/other"),
        ("noprefix", "/x/.claude/skills/aveto-judge-seen"),
    ):
        write_spawn(tmp_path / "s", name, world.payload("r001"), "Q1 ANSWERABLE", line=line)
        s = jr.read_spawn(tmp_path / "s" / f"agent-{name}.jsonl")
        assert not s.layout_ok and s.payload is None, name


def _rewrite(path: Path, edit: Callable[[list[dict[str, object]]], None]) -> None:
    recs = [json.loads(x) for x in path.read_text().splitlines()]
    edit(recs)
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\n")


@pytest.mark.parametrize("case", ["type", "block", "usage", "model", "prompt", "json", "meta", "tools"])
def test_read_spawn_unknown_shapes_fail_closed(world: World, tmp_path: Path, case: str) -> None:
    d = tmp_path / "s"
    write_spawn(d, "bad", world.payload("r001"), "Q1 ANSWERABLE")
    path = d / "agent-bad.jsonl"
    if case == "type":
        _rewrite(path, lambda r: r.append({"type": "mystery", "message": {}}))
    elif case == "block":
        _rewrite(path, lambda r: r[-1]["message"]["content"].append({"type": "image"}))  # type: ignore[index]
    elif case == "usage":
        _rewrite(path, lambda r: r[-1]["message"].pop("usage"))  # type: ignore[attr-defined]
    elif case == "model":
        _rewrite(path, lambda r: r[-1]["message"].pop("model"))  # type: ignore[attr-defined]
    elif case == "prompt":
        _rewrite(path, lambda r: r[0]["message"].update(content=[{"type": "text", "text": "x"}]))  # type: ignore[attr-defined]
    elif case == "json":
        path.write_text("not json\n")
    elif case == "meta":
        (d / "agent-bad.meta.json").write_text("{}")
    else:
        (d / "agent-bad.prefix.json").write_text("{}")
    with pytest.raises(jr.TranscriptFormatError):
        jr.read_spawn(path)


# --- T3: record and the void rules -------------------------------------------------------------


def test_record_valid_batch_scores_through_the_product(
    world: World, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    d = tmp_path / "sub"
    write_batch(world, d)
    write_spawn(d, "other", None, "hello", agent_type="general-purpose")
    result = run_record(world, d)
    assert not result.void and result.reasons == ()
    assert result.others == ("other (general-purpose)",)
    assert len(result.rows) == 7 and len(result.batch_rows) == 6  # r049 is the smoke row
    smoke = next(r for r in result.rows if r.run_id == "r049")
    assert not smoke.in_batch
    verdicts = world.root / "stage" / "verdicts.toml"
    assert verdicts.exists() and (world.root / "stage" / "audit.md").exists()
    capsys.readouterr()
    code = product_main(
        ["eval", "--index", "i.json", "--eval-file", str(world.sample_eval), "--verdicts", str(verdicts)],
        embedder=FAKE,
    )
    out = capsys.readouterr().out
    assert "judge errors: 0" in out and "NOT MET" not in out
    assert "bars: unanswerable_abstained=3/3 answerable_hit_not_abstained=3/3 judge_errors=0" in out
    assert code in (0, 1)  # the retrieval gate on the file, not the judge's result
    audit = (world.root / "stage" / "audit.md").read_text()
    assert "Q1 ANSWERABLE" not in audit and "shows it" not in audit  # no reply text in the audit
    assert (world.root / "stage" / "diffs.md").read_text() == "# Differing replies and judge errors (run record only)\n"
    assert not (world.root / ".aveto-judge" / "reply.txt").exists()


VOID_CASES = ["tool_use", "model", "offered", "line_len", "bad_layout", "unknown_payload", "duplicate", "missing"]


@pytest.mark.parametrize("case", VOID_CASES)
def test_record_voids_the_whole_batch(world: World, tmp_path: Path, case: str) -> None:
    d = tmp_path / "sub"
    write_batch(world, d)
    victim = d / "agent-ar003.jsonl"
    p = world.payload("r003")
    if case == "tool_use":
        write_spawn(d, "ar003", p, "Q1 ANSWERABLE", tool_use=True)
    elif case == "model":
        write_spawn(d, "ar003", p, "Q1 ANSWERABLE", model="claude-opus-5-5")
    elif case == "offered":
        write_spawn(d, "ar003", p, "Q1 ANSWERABLE", tools=("DesignSync",))
    elif case == "line_len":
        write_spawn(d, "ar003", p, "Q1 ANSWERABLE", line=LINE + "xx")
    elif case == "bad_layout":
        write_spawn(d, "ar003", p, "Q1 ANSWERABLE", line="Base directory: /x")
    elif case == "unknown_payload":
        write_spawn(d, "ar003", p + "extra\n", "Q1 ANSWERABLE")
    elif case == "duplicate":
        write_spawn(d, "dup", p, "Q1 ANSWERABLE")
    else:
        for suffix in (".jsonl", ".meta.json", ".prefix.json"):
            (d / f"agent-ar003{suffix}").unlink()
    assert victim.exists() or case == "missing"
    result = run_record(world, d)
    assert result.void and result.reasons and result.verdicts_path is None
    assert (world.root / "stage" / "audit.md").exists()
    assert "VOID" in (world.root / "stage" / "audit.md").read_text()
    assert not (world.root / "stage" / "verdicts.toml").exists()
    assert not (world.root / "stage" / "diffs.md").exists()


def test_record_expect_tools_must_match(world: World, tmp_path: Path) -> None:
    d = tmp_path / "sub"
    seven = tuple(f"T{i}" for i in range(7))
    for row in world.rows:
        write_spawn(d, f"a{row.run_id}", world.payload(row.run_id), GOOD_REPLY[world.want(row.run_id)], tools=seven)
    assert run_record(world, d).void  # registered as 0
    assert not run_record(world, d, stage="stage2", tools=seven).void  # registered as the 7 measured
    assert run_record(world, d, stage="stage3", tools=seven[:6]).void


# --- T4: apply_reply, scoring, R5 ----------------------------------------------------------------


def _apply(w: World, reply: str | None, run_id: str = "r001", sha: str | None = None) -> jr.Applied:
    row = next(r for r in w.rows if r.run_id == run_id)
    digest = sha or hashlib.sha256(w.payload(run_id).encode()).hexdigest()
    return jr.apply_reply(row.question, digest, reply, embedder=FAKE, index=w.root / "i.json")


@pytest.mark.parametrize(
    ("reply", "token", "category"),
    [
        ("Q1 ANSWERABLE", "ANSWERABLE", None),
        ("Q1 ANSWERABLE: the passage says so", "ANSWERABLE", None),
        ("reasoning first\nQ1 NOT_ANSWERABLE", "NOT_ANSWERABLE", None),
        ("Q1 NOT_ANSWERABLE: nothing on this", "NOT_ANSWERABLE", None),
        ("", "JUDGE_ERROR", judge.EMPTY),
        (None, "JUDGE_ERROR", judge.EMPTY),
        ("\n  \n", "JUDGE_ERROR", judge.EMPTY),
        ("Q1 ANSWERABLE.", "JUDGE_ERROR", judge.MALFORMED),
        ("**Q1 ANSWERABLE**", "JUDGE_ERROR", judge.MALFORMED),
        ("Q2 ANSWERABLE", "JUDGE_ERROR", judge.WRONG_ID),
        ("Q1: ANSWERABLE", "JUDGE_ERROR", judge.WRONG_ID),
        ("Q1 ANSWERABLE not ANSWERABLE", "JUDGE_ERROR", judge.MULTI_TOKEN),
        ("tab\there\nQ1 ANSWERABLE", "JUDGE_ERROR", judge.CONTROL),
        ("zero\u200bwidth\nQ1 ANSWERABLE", "JUDGE_ERROR", judge.CONTROL),
        ("x" * 5000 + "\nQ1 ANSWERABLE", "JUDGE_ERROR", judge.TOO_LONG),
    ],
)
def test_apply_reply_matches_the_product_grammar(
    world: World, reply: str | None, token: str, category: str | None
) -> None:
    assert _apply(world, reply) == jr.Applied(token, category)


def test_apply_reply_not_utf8_and_different_input(world: World) -> None:
    assert _apply(world, "\ud800 Q1 ANSWERABLE") == jr.Applied("JUDGE_ERROR", judge.NOT_UTF8)
    assert _apply(world, "Q1 ANSWERABLE", sha="0" * 64) == jr.Applied("JUDGE_ERROR", judge.DIFFERENT_INPUT)


def test_apply_reply_unexpected_exit_or_stdout_is_an_anomaly(
    world: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    import aveto_support.__main__ as product

    real = product.main

    def exits(code: int, text: str = "") -> Callable[..., int]:
        def fake(argv: list[str], **kwargs: object) -> int:
            print(text, end="")
            return code

        return fake

    monkeypatch.setattr(product, "main", exits(2))
    with pytest.raises(jr.ApplyError, match="exited 2"):
        _apply(world, "Q1 ANSWERABLE")
    monkeypatch.setattr(product, "main", exits(0, "no confident match\n"))
    with pytest.raises(jr.ApplyError, match="deciding-signal"):
        _apply(world, "Q1 ANSWERABLE")
    monkeypatch.setattr(product, "main", exits(4, "judge error\n"))
    with pytest.raises(jr.ApplyError, match="unexpected output shape"):
        _apply(world, "Q1 ANSWERABLE")
    monkeypatch.setattr(product, "main", real)
    signal = judge.signal_line(judge.Verdict("NOT_ANSWERABLE"))
    monkeypatch.setattr(product, "main", exits(0, "extra line\nno confident match\n" + signal + "\n"))
    with pytest.raises(jr.ApplyError, match="two registered lines"):
        _apply(world, "Q1 NOT_ANSWERABLE")


def test_record_differing_rows_and_error_split(
    world: World, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    d = tmp_path / "sub"
    write_batch(
        world,
        d,
        {
            "r001": "SECRET REASONING one\nQ1 NOT_ANSWERABLE",  # answerable with hit, abstained: differs
            "r002": "Q1 ANSWERABLE",  # unanswerable, shown: differs
            "r004": "Q1 ANSWERABLE.",  # unanswerable, MALFORMED: judge error on bar 1
            "r006": None,  # answerable with hit, no reply: EMPTY, judge error on bar 2
        },
    )
    result = run_record(world, d)
    assert not result.void
    diffs = (world.root / "stage" / "diffs.md").read_text()
    for run_id in ("r001", "r002", "r004", "r006"):
        assert f"## {run_id} " in diffs
    for run_id in ("r003", "r005"):
        assert f"## {run_id} " not in diffs
    assert "SECRET REASONING one" in diffs and "(no reply)" in diffs
    assert "SECRET REASONING" not in (world.root / "stage" / "audit.md").read_text()
    text = jr.diagnostics(
        world.searcher, world.sample_eval, world.root / "stage" / "verdicts.toml",
        json.loads((world.root / "stage" / "audit.json").read_text()),
    )
    assert "judge errors: 2; bar 1 1 / bar 2 1 / neither 0" in text
    assert "over-abstention: 1/3" in text  # r001 only; the judge error is excluded
    assert "judge error categories: empty reply x1, malformed verdict line x1" in text
    assert "usage: 6 spawns; peak sum 672" in text
    assert "ANSWERABLE without a hit: 0/0" in text
    capsys.readouterr()
    code = product_main(
        ["eval", "--index", "i.json", "--eval-file", str(world.sample_eval),
         "--verdicts", str(world.root / "stage" / "verdicts.toml")], embedder=FAKE,
    )
    out = capsys.readouterr().out
    assert code in (0, 1) and "judge errors: 2 (counted as failures on both bars)" in out
    assert "bars: unanswerable_abstained=1/3 answerable_hit_not_abstained=1/3 judge_errors=2" in out


def test_diagnostics_judge_error_on_a_question_without_a_hit(world: World, tmp_path: Path) -> None:
    ev = world.root / "n.toml"
    ev.write_text(
        f'pinned_commit = "{COMMIT}"\n' + _q("n1", "cats purr", LAST) + _q("n2", "cats purr", CATS)
        + _q("n3", "rocket fuel", None)
    )
    results = {q.id: judge.retrieve_for_judge(world.searcher, q.question) for q in load_eval_set(ev).questions}
    shas = {k: judge.input_sha256(judge.format_judge_input(v)) for k, v in results.items()}
    lines = [f'format = "aveto-judge-verdicts-v1"\nprompt_sha256 = "{judge.PROMPT_SHA256}"\n']
    for qid, token in (("n1", "JUDGE_ERROR"), ("n2", "ANSWERABLE"), ("n3", "NOT_ANSWERABLE")):
        lines.append(f'[[verdict]]\nid = "{qid}"\nverdict = "{token}"\ninput_sha256 = "{shas[qid]}"\n')
    verdicts = world.root / "v.toml"
    verdicts.write_text("\n".join(lines))
    text = jr.diagnostics(world.searcher, ev, verdicts, None)
    assert "judge errors: 1; bar 1 0 / bar 2 0 / neither 1" in text
    assert "ANSWERABLE without a hit: 0/1" in text


def test_best_score_rule_counts(world: World) -> None:
    got = jr.best_score_rule(world.searcher, load_eval_set(world.sample_eval))
    assert got.unanswerable == 3 and got.hits == 3
    assert 0 <= got.abstained <= 3 and 0 <= got.shown <= 3


# --- T5: offline ----------------------------------------------------------------------------------------


def test_judge_run_import_allow_list() -> None:
    allowed = {
        "__future__", "argparse", "contextlib", "dataclasses", "hashlib", "io", "json", "os",
        "pathlib", "re", "sys", "tomllib", "typing", "collections.abc",
    }
    tree = ast.parse((ROOT / "tools" / "judge_run.py").read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0 and node.module is not None
            found.add(node.module)
    assert found
    for module in found:
        assert module in allowed or module == "aveto_support" or module.startswith("aveto_support."), module
    for banned in ("subprocess", "socket", "urllib", "http"):
        assert not any(m == banned or m.startswith(banned + ".") for m in found)


def test_judge_run_offline_no_process(
    world: World, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("the tool must not start a process")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    for name in ("system", "posix_spawn", "posix_spawnp", "execv", "execve", "execvp", "fork"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, forbidden)
    with pytest.raises(RuntimeError, match="network disabled"):
        socket.create_connection(("192.0.2.1", 80))
    d = tmp_path / "sub"
    write_batch(world, d)
    result = run_record(world, d)
    assert not result.void
    jr.diagnostics(world.searcher, world.sample_eval, world.root / "stage" / "verdicts.toml", None)
    assert jr.check_transcripts(d).count("\n") == 7
