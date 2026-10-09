from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import pytest
from conftest import FakeEmbedder, FakeJudge, embed_all

from aveto_support.__main__ import main
from aveto_support.embed import INPUT_NAMES, ModelError, sha256_file
from aveto_support.index import Index, RetrievalParams, split_passages, write_index
from aveto_support.judge import (
    DEFAULT_PARAMS,
    JudgeParams,
    OnnxJudge,
    PlaceholderJudge,
    judge_dir,
    probability,
)

FAKE = FakeEmbedder()


@pytest.mark.parametrize("bad", ["abc123", "A" * 40, "main", "a" * 39, "a" * 41])
def test_judge_revision_must_be_40_hex(bad: str) -> None:
    with pytest.raises(ValueError, match="40-hex"):
        JudgeParams(revision=bad)
    assert len(DEFAULT_PARAMS.revision) == 40


@pytest.mark.parametrize("bad", ["abc", "G" * 64, "a" * 63, "a" * 65, "A" * 64])
def test_judge_sha256_must_be_64_hex(bad: str) -> None:
    with pytest.raises(ValueError, match="sha256"):
        JudgeParams(onnx_sha256=bad)
    with pytest.raises(ValueError, match="sha256"):
        JudgeParams(vocab_sha256=bad)


def test_judge_params_pin_is_the_approved_one() -> None:
    p = DEFAULT_PARAMS
    assert (p.model, p.revision) == (
        "cross-encoder/qnli-electra-base",
        "c7dea87c98b2269a935686c31336e97e837cbbeb",
    )
    assert p.onnx_sha256 == "595b37541289472b7b784ed2af05bcad6000991a2657aeee4f92f68b42ae61d9"
    assert p.vocab_sha256 == "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3"
    assert (p.head, p.positive_index, p.threshold, p.method) == ("sigmoid1", 0, 0.5, "abstain-judge-v1")
    with pytest.raises(ValueError, match="positive_index"):
        JudgeParams(positive_index=1)


def test_placeholder_judge_raises() -> None:
    with pytest.raises(RuntimeError, match="answerability judge model is not configured in this build"):
        PlaceholderJudge().logits("q", "p")


@pytest.mark.real_judge_load
def test_judge_absent_fails_closed_without_download(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ps = []
    for path, text in {"a.md": "# A\nalpha beta\n", "b.md": "# B\ngamma delta\n"}.items():
        ps.extend(split_passages(path, text))
    index = Index("acme/docs", "c" * 40, 2, (), tuple(embed_all(ps)), 0.3, RetrievalParams())
    idx = tmp_path / "i.json"
    write_index(index, idx)
    models = tmp_path / "none"
    models.mkdir()
    # The autouse fixture blocks every socket: a download attempt would raise RuntimeError.
    code = main(["retrieve", "--index", str(idx), "alpha"], embedder=FAKE, models_dir=models)
    captured = capsys.readouterr()
    assert code == 2 and "answerability judge files are not cached" in captured.err
    assert "run ingest" in captured.err and captured.out == ""
    assert list(models.rglob("*")) == []
    code = main(["eval", "--index", str(idx), "--eval-file", str(tmp_path / "e.toml")],
                embedder=FAKE, models_dir=models)
    assert code == 2 and capsys.readouterr().out == ""


@pytest.mark.real_judge_load
def test_judge_cached_file_rehashed_before_use(tmp_path: Path) -> None:
    onnx, vocab = b"pretend graph", b"[PAD]\n[UNK]\n"
    params = JudgeParams(
        model="acme/tiny-judge", revision="d" * 40,
        onnx_sha256=hashlib.sha256(onnx).hexdigest(), vocab_sha256=hashlib.sha256(vocab).hexdigest(),
    )
    base = judge_dir(tmp_path, params)
    (base / "onnx").mkdir(parents=True)
    (base / "onnx/model.onnx").write_bytes(b"corrupted after download")
    (base / "vocab.txt").write_bytes(vocab)
    with pytest.raises(ModelError, match="does not match"):
        OnnxJudge.load(tmp_path, params)
    assert not (base / "onnx/model.onnx").exists()  # a mismatching file is deleted, never used


class _Meta:
    def __init__(self, name: str = "", shape: list[object] | None = None) -> None:
        self.name, self.shape = name, shape


def _stub_session(inputs: list[str], shape: list[object]) -> type:
    class Session:
        def __init__(self, *a: Any, **k: Any) -> None:
            pass

        def get_inputs(self) -> list[_Meta]:
            return [_Meta(n) for n in inputs]

        def get_outputs(self) -> list[_Meta]:
            return [_Meta("logits", shape)]

    return Session


def test_judge_rejects_unexpected_inputs_or_output_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import onnxruntime

    vocab = tmp_path / "vocab.txt"
    vocab.write_text("[PAD]\n[UNK]\n[CLS]\n[SEP]\na\n")
    onnx = tmp_path / "m.onnx"
    onnx.write_bytes(b"x")
    names = sorted(INPUT_NAMES)
    cases: list[tuple[list[str], list[object], str]] = [
        (names[:2], ["batch", 1], "unexpected ONNX inputs"),
        ([*names, "extra"], ["batch", 1], "unexpected ONNX inputs"),
        (names, ["batch", 2], "unexpected judge output shape"),
        (names, ["batch"], "unexpected judge output shape"),
    ]
    for inputs, shape, message in cases:
        monkeypatch.setattr(onnxruntime, "InferenceSession", _stub_session(inputs, shape))
        with pytest.raises(ModelError, match=message):
            OnnxJudge(onnx, vocab)
    monkeypatch.setattr(onnxruntime, "InferenceSession", _stub_session(names, ["batch", 1]))
    assert OnnxJudge(onnx, vocab).signature().inputs == INPUT_NAMES
    softmax = JudgeParams(head="softmax2", positive_index=1)
    with pytest.raises(ModelError, match="unexpected judge output shape"):
        OnnxJudge(onnx, vocab, softmax)


def test_judge_returns_only_scores() -> None:
    marker = "INVENTED-BY-JUDGE"
    out = FakeJudge(0.7).logits("q", "p")
    assert isinstance(out, tuple) and all(isinstance(v, float) for v in out) and len(out) == 1
    assert marker not in repr(out)
    for bad in ("an invented sentence", None, True, ("a sentence",), (marker,)):
        with pytest.raises(ModelError):
            probability(bad, DEFAULT_PARAMS)  # type: ignore[arg-type]


def test_probability_head_transform() -> None:
    sig = DEFAULT_PARAMS
    assert probability((0.0,), sig) == 0.5
    assert probability((2.0,), sig) == pytest.approx(1 / (1 + math.exp(-2)))
    assert probability((-800.0,), sig) == 0.0 and probability((800.0,), sig) == 1.0
    soft = JudgeParams(head="softmax2", positive_index=1)
    assert probability((0.0, 0.0), soft) == 0.5
    assert probability((0.0, 2.0), soft) == pytest.approx(1 / (1 + math.exp(-2)))
    assert probability((1000.0, 1000.0), soft) == 0.5  # stable
    bads: list[tuple[float, ...]] = [(), (0.0, 0.0), (float("nan"),), (float("inf"),)]
    for bad in bads:
        with pytest.raises(ModelError):
            probability(bad, sig)
    for bad in ((0.0,), (0.0, 1.0, 2.0), (0.0, float("nan"))):
        with pytest.raises(ModelError):
            probability(bad, soft)


# --- the real model: needs the approved cached files (pytest -m model) -------


@pytest.mark.model
@pytest.mark.real_judge_load
def test_judge_onnx_signature_matches_pin() -> None:
    models = Path(__file__).parent.parent / "models"
    base = judge_dir(models, DEFAULT_PARAMS)
    assert sha256_file(base / "onnx/model.onnx") == DEFAULT_PARAMS.onnx_sha256
    assert sha256_file(base / "vocab.txt") == DEFAULT_PARAMS.vocab_sha256
    judge = OnnxJudge.load(models)
    sig = judge.signature()
    assert sig.inputs == INPUT_NAMES
    assert len(sig.output_shape) == 2 and sig.output_shape[-1] == 1
    first = judge.logits("What colour is the sky?", "The sky appears blue because of Rayleigh scattering.")
    assert first == judge.logits("What colour is the sky?", "The sky appears blue because of Rayleigh scattering.")
    assert len(first) == 1 and math.isfinite(first[0])
    judge.close()
    judge.close()
    with pytest.raises(ModelError, match="closed"):
        judge.logits("q", "p")
