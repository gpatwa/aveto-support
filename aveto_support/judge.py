"""The answerability judge adapter boundary: a local cross-encoder that returns logits per pair.

Nothing here touches the network. The two model files are downloaded by ``ingest`` and
re-hashed against their pinned sha256 before every use. The model reads a question and a
shown passage and returns floats; it never returns, selects or alters text (INV-4).
Method ``abstain-judge-v1`` (ADR 0007): threshold 0.5, the model's own decision boundary,
fixed in the tech spec before any run and not fitted to any data.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

import numpy as np

from aveto_support.embed import (
    INPUT_NAMES,
    ONNX_FILE,
    VOCAB_FILE,
    GraphSignature,
    ModelError,
    WordPiece,
    verify_file,
)
from aveto_support.rerank import encode_pair

_MODEL_ID = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class JudgeParams:
    """The pinned judge and the pre-registered constants of abstain-judge-v1."""

    model: str = "cross-encoder/qnli-electra-base"
    revision: str = "c7dea87c98b2269a935686c31336e97e837cbbeb"
    onnx_file: str = ONNX_FILE
    onnx_sha256: str = "595b37541289472b7b784ed2af05bcad6000991a2657aeee4f92f68b42ae61d9"
    vocab_file: str = VOCAB_FILE
    vocab_sha256: str = "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3"
    head: Literal["sigmoid1", "softmax2"] = "sigmoid1"
    positive_index: int = 0
    max_tokens: int = 512
    max_question_tokens: int = 64
    threshold: float = 0.5
    method: str = "abstain-judge-v1"

    def __post_init__(self) -> None:
        if not _MODEL_ID.match(self.model):
            raise ValueError("judge model must be owner/name")
        if not _HEX40.match(self.revision):
            raise ValueError("judge revision must be a full 40-hex commit")
        for value in (self.onnx_sha256, self.vocab_sha256):
            if not _HEX64.match(value):
                raise ValueError("judge sha256 must be 64 lowercase hex characters")
        if self.head not in ("sigmoid1", "softmax2"):
            raise ValueError("judge head must be sigmoid1 or softmax2")
        arity = 1 if self.head == "sigmoid1" else 2
        if not 0 <= self.positive_index < arity:
            raise ValueError("judge positive_index is outside the head")
        if not 0.0 < self.threshold < 1.0:
            raise ValueError("judge threshold must be a probability in (0, 1)")


DEFAULT_PARAMS = JudgeParams()


class Judge(Protocol):
    def logits(self, question: str, passage_text: str) -> tuple[float, ...]: ...


class PlaceholderJudge:
    name = "answerability-judge-boundary"

    def logits(self, question: str, passage_text: str) -> tuple[float, ...]:
        raise RuntimeError("answerability judge model is not configured in this build.")


def judge_dir(models_dir: Path, params: JudgeParams) -> Path:
    return models_dir / params.model.replace("/", "--") / params.revision


def probability(logits: tuple[float, ...], params: JudgeParams) -> float:
    """sigmoid for a one-logit head; softmax[positive_index] for a two-logit head."""
    arity = 1 if params.head == "sigmoid1" else 2
    if not isinstance(logits, tuple):
        raise ModelError("the judge returned a non-numeric score")
    if len(logits) != arity:
        raise ModelError(f"the judge returned {len(logits)} logits; expected {arity}")
    for value in logits:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ModelError("the judge returned a non-numeric score")
        if not math.isfinite(value):
            raise ModelError("the judge returned a non-finite score")
    if params.head == "sigmoid1":
        x = float(logits[0])
        return 1.0 / (1.0 + math.exp(-x)) if x >= 0 else math.exp(x) / (1.0 + math.exp(x))
    peak = max(logits)
    exps = [math.exp(float(v) - peak) for v in logits]
    return exps[params.positive_index] / sum(exps)


class OnnxJudge:
    """QNLI cross-encoder via onnxruntime on CPU: single-threaded, sequential, batch size 1."""

    def __init__(self, onnx_path: Path, vocab_path: Path, params: JudgeParams = DEFAULT_PARAMS) -> None:
        import onnxruntime as ort

        vocab = vocab_path.read_text(encoding="utf-8").split("\n")
        while vocab and vocab[-1] == "":
            vocab.pop()
        self.tokenizer = WordPiece([line.strip() for line in vocab])
        self._params = params
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        self._session = ort.InferenceSession(
            str(onnx_path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        names = frozenset(i.name for i in self._session.get_inputs())
        if names != INPUT_NAMES:
            raise ModelError(f"unexpected ONNX inputs {sorted(names)}; expected {sorted(INPUT_NAMES)}")
        width = 1 if params.head == "sigmoid1" else 2
        shape = self._session.get_outputs()[0].shape
        if len(shape) != 2 or shape[-1] != width:
            raise ModelError(f"unexpected judge output shape {shape}; expected [batch, {width}]")

    @classmethod
    def load(cls, models_dir: Path, params: JudgeParams = DEFAULT_PARAMS) -> OnnxJudge:
        """Re-hash both cached files, then build the session. Never downloads."""
        base = judge_dir(models_dir, params)
        onnx_path, vocab_path = base / params.onnx_file, base / params.vocab_file
        if not onnx_path.is_file() or not vocab_path.is_file():
            raise ModelError(f"answerability judge files are not cached in {base}; run ingest")
        try:
            verify_file(onnx_path, params.onnx_sha256)
            verify_file(vocab_path, params.vocab_sha256)
        except ModelError as exc:
            raise ModelError(f"{exc} (judge: run ingest)") from exc
        return cls(onnx_path, vocab_path, params)

    def close(self) -> None:
        """Release the ONNX session now rather than at interpreter teardown. Idempotent."""
        self._session = None

    def _live(self) -> Any:
        if self._session is None:
            raise ModelError("judge is closed")
        return self._session

    def signature(self) -> GraphSignature:
        session = self._live()
        outputs = session.get_outputs()
        return GraphSignature(
            frozenset(i.name for i in session.get_inputs()), tuple(outputs[0].shape)
        )

    def logits(self, question: str, passage_text: str) -> tuple[float, ...]:
        session = self._live()
        ids, types = encode_pair(
            self.tokenizer,
            question,
            passage_text,
            self._params.max_tokens,
            self._params.max_question_tokens,
        )
        n = len(ids)
        feeds = {
            "input_ids": np.array([ids], dtype=np.int64),
            "attention_mask": np.ones((1, n), dtype=np.int64),
            "token_type_ids": np.array([types], dtype=np.int64),
        }
        out = np.asarray(session.run(None, feeds)[0])
        width = 1 if self._params.head == "sigmoid1" else 2
        if out.shape != (1, width):
            raise ModelError(f"unexpected judge output {out.shape}; expected (1, {width})")
        values = tuple(float(v) for v in out[0])
        if not all(math.isfinite(v) for v in values):
            raise ModelError("the judge returned a non-finite score")
        return values
