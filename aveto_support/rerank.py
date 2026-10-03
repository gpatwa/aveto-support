"""The reranker adapter boundary: a local cross-encoder that returns one score per pair.

Nothing here touches the network. The two model files are downloaded by ``ingest`` and
re-hashed against their pinned sha256 before every use. The model reads text and returns a
float; it never returns, selects or alters text (INV-4).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

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

_MODEL_ID = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class RerankParams:
    """The pinned reranker and the pre-registered constants of file-rerank-v1."""

    model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"
    revision: str = "233902d25c440f23af6f7d6e94d2946bac0bee0a"
    onnx_file: str = ONNX_FILE
    onnx_sha256: str = "5d3e70fd0c9ff14b9b5169a51e957b7a9c74897afd0a35ce4bd318150c1d4d4a"
    vocab_file: str = VOCAB_FILE
    vocab_sha256: str = "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3"
    candidates: int = 20
    max_tokens: int = 512
    max_question_tokens: int = 64
    scoring: str = "ce-maxp-shown-v1"

    def __post_init__(self) -> None:
        if not _MODEL_ID.match(self.model):
            raise ValueError("reranker model must be owner/name")
        if not _HEX40.match(self.revision):
            raise ValueError("reranker revision must be a full 40-hex commit")
        for value in (self.onnx_sha256, self.vocab_sha256):
            if not _HEX64.match(value):
                raise ValueError("reranker sha256 must be 64 lowercase hex characters")


DEFAULT_PARAMS = RerankParams()


class Reranker(Protocol):
    def score(self, question: str, passage_text: str) -> float: ...


class PlaceholderReranker:
    def score(self, question: str, passage_text: str) -> float:
        raise RuntimeError("reranker model is not configured in this build.")


def reranker_dir(models_dir: Path, params: RerankParams) -> Path:
    return models_dir / params.model.replace("/", "--") / params.revision


def encode_pair(
    tokenizer: WordPiece,
    question: str,
    passage: str,
    max_tokens: int = 512,
    max_question_tokens: int = 64,
) -> tuple[list[int], list[int]]:
    """``[CLS] q [SEP] p [SEP]`` with segment ids 0 then 1; question capped, passage gets the rest."""
    q_ids = tokenizer.content_ids(question)[:max_question_tokens]
    p_ids = tokenizer.content_ids(passage)[: max_tokens - 3 - len(q_ids)]
    input_ids = [tokenizer.cls, *q_ids, tokenizer.sep, *p_ids, tokenizer.sep]
    token_type_ids = [0] * (len(q_ids) + 2) + [1] * (len(p_ids) + 1)
    return input_ids, token_type_ids


class OnnxReranker:
    """MiniLM cross-encoder via onnxruntime on CPU: single-threaded, sequential, batch size 1."""

    def __init__(self, onnx_path: Path, vocab_path: Path, params: RerankParams = DEFAULT_PARAMS) -> None:
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
        shape = self._session.get_outputs()[0].shape
        if len(shape) != 2 or shape[-1] != 1:
            raise ModelError(f"unexpected reranker output shape {shape}; expected [batch, 1]")

    @classmethod
    def load(cls, models_dir: Path, params: RerankParams = DEFAULT_PARAMS) -> OnnxReranker:
        """Re-hash both cached files, then build the session. Never downloads."""
        base = reranker_dir(models_dir, params)
        onnx_path, vocab_path = base / params.onnx_file, base / params.vocab_file
        if not onnx_path.is_file() or not vocab_path.is_file():
            raise ModelError(
                f"reranker files are not cached in {base}; --ranking file-rerank-v1 needs them. "
                "Fetch them with: ingest --with-reranker (the default ranking, file-rrf-v1, "
                "does not need them)"
            )
        try:
            verify_file(onnx_path, params.onnx_sha256)
            verify_file(vocab_path, params.vocab_sha256)
        except ModelError as exc:
            raise ModelError(f"{exc} (reranker: run ingest --with-reranker)") from exc
        return cls(onnx_path, vocab_path, params)

    def close(self) -> None:
        """Release the ONNX session now rather than at interpreter teardown. Idempotent."""
        self._session = None

    def _live(self) -> Any:
        if self._session is None:
            raise ModelError("reranker is closed")
        return self._session

    def signature(self) -> GraphSignature:
        session = self._live()
        outputs = session.get_outputs()
        return GraphSignature(
            frozenset(i.name for i in session.get_inputs()), tuple(outputs[0].shape)
        )

    def score(self, question: str, passage_text: str) -> float:
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
        logits = np.asarray(session.run(None, feeds)[0])
        if logits.shape != (1, 1):
            raise ModelError(f"unexpected reranker output {logits.shape}; expected (1, 1)")
        value = float(logits[0][0])
        if not math.isfinite(value):
            raise ModelError("the reranker returned a non-finite score")
        return value
