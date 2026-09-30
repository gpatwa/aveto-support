"""The embedding adapter boundary: WordPiece, int8 vectors, and the ONNX model.

Nothing here touches the network. The model files are downloaded by ``ingest``
and re-hashed against their pinned sha256 before every use.
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
import numpy.typing as npt

from aveto_support.index import EmbeddingParams, Passage

DIM = 384
MAX_TOKENS = 512
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
INT8_SCALE = 127
ONNX_FILE = "onnx/model.onnx"
VOCAB_FILE = "vocab.txt"
INPUT_NAMES = frozenset({"input_ids", "attention_mask", "token_type_ids"})
_MAX_CHARS_PER_WORD = 100


class ModelError(Exception):
    """Model files are missing, fail their pinned hash, or have the wrong shape."""


# --- int8 vectors ----------------------------------------------------------


def quantise(vector: Sequence[float] | npt.NDArray[np.float64]) -> bytes:
    """clamp(round(x * 127), -127, 127) as signed bytes."""
    scaled = np.rint(np.asarray(vector, dtype=np.float64) * INT8_SCALE)
    return np.clip(scaled, -INT8_SCALE, INT8_SCALE).astype(np.int8).tobytes()


def dequantise(data: bytes) -> npt.NDArray[np.float64]:
    return np.frombuffer(data, dtype=np.int8).astype(np.float64) / INT8_SCALE


def passage_input(passage: Passage) -> str:
    """Heading trail, a newline, then the verbatim body after the heading line."""
    lines = passage.text.split("\n")
    body = "\n".join(lines[1:] if passage.heading_path else lines)
    return " > ".join(passage.heading_path) + "\n" + body


# --- the adapter protocol --------------------------------------------------


class Embedder(Protocol):
    def embed_passage(self, text: str) -> bytes: ...

    def embed_query(self, question: str) -> bytes: ...

    def token_count(self, text: str) -> int:
        """Number of content tokens, excluding [CLS] and [SEP]."""
        ...


class PlaceholderEmbedder:
    """The default wherever a model has not been explicitly loaded. Always raises."""

    def embed_passage(self, text: str) -> bytes:
        raise RuntimeError("embedding model is not configured in this build.")

    def embed_query(self, question: str) -> bytes:
        raise RuntimeError("embedding model is not configured in this build.")

    def token_count(self, text: str) -> int:
        raise RuntimeError("embedding model is not configured in this build.")


# --- WordPiece -------------------------------------------------------------


def _is_whitespace(ch: str) -> bool:
    return ch in " \t\n\r" or unicodedata.category(ch) == "Zs"


def _is_control(ch: str) -> bool:
    if ch in "\t\n\r":
        return False
    return unicodedata.category(ch).startswith("C")


def _is_punctuation(ch: str) -> bool:
    cp = ord(ch)
    if 33 <= cp <= 47 or 58 <= cp <= 64 or 91 <= cp <= 96 or 123 <= cp <= 126:
        return True
    return unicodedata.category(ch).startswith("P")


_CJK_RANGES = (
    (0x4E00, 0x9FFF),
    (0x3400, 0x4DBF),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2B73F),
    (0x2B740, 0x2B81F),
    (0x2B820, 0x2CEAF),
    (0xF900, 0xFAFF),
    (0x2F800, 0x2FA1F),
)


def _is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _CJK_RANGES)


def _basic_tokens(text: str) -> list[str]:
    """BERT basic tokenizer: clean, split CJK, lowercase, strip accents, split punctuation."""
    cleaned: list[str] = []
    for ch in text:
        if ord(ch) == 0 or ord(ch) == 0xFFFD or _is_control(ch):
            continue
        if _is_whitespace(ch):
            cleaned.append(" ")
        elif _is_cjk(ch):
            cleaned.extend((" ", ch, " "))
        else:
            cleaned.append(ch)
    tokens: list[str] = []
    for word in "".join(cleaned).split():
        word = unicodedata.normalize("NFD", word.lower())
        word = "".join(c for c in word if unicodedata.category(c) != "Mn")
        current = ""
        for ch in word:
            if _is_punctuation(ch):
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(ch)
            else:
                current += ch
        if current:
            tokens.append(current)
    return tokens


class WordPiece:
    """Greedy longest-match WordPiece over a BERT vocab, with [CLS]/[SEP] and truncation."""

    def __init__(self, vocab: Sequence[str]) -> None:
        self._ids = {token: i for i, token in enumerate(vocab)}
        for special in ("[CLS]", "[SEP]", "[UNK]"):
            if special not in self._ids:
                raise ModelError(f"vocab is missing {special}")
        self.cls = self._ids["[CLS]"]
        self.sep = self._ids["[SEP]"]
        self.unk = self._ids["[UNK]"]

    def _word_ids(self, word: str) -> list[int]:
        if len(word) > _MAX_CHARS_PER_WORD:
            return [self.unk]
        pieces: list[int] = []
        start = 0
        while start < len(word):
            end = len(word)
            found: int | None = None
            while start < end:
                piece = word[start:end]
                if start > 0:
                    piece = "##" + piece
                if piece in self._ids:
                    found = self._ids[piece]
                    break
                end -= 1
            if found is None:
                return [self.unk]
            pieces.append(found)
            start = end
        return pieces

    def content_ids(self, text: str) -> list[int]:
        ids: list[int] = []
        for word in _basic_tokens(text):
            ids.extend(self._word_ids(word))
        return ids

    def encode(self, text: str, max_tokens: int = MAX_TOKENS) -> list[int]:
        return [self.cls, *self.content_ids(text)[: max_tokens - 2], self.sep]


# --- integrity -------------------------------------------------------------


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_file(path: Path, expected_sha256: str) -> None:
    """Re-hash a cached model file. A mismatch deletes the file and raises."""
    if not path.is_file():
        raise ModelError(f"model file {path} is missing; run ingest")
    if sha256_file(path) != expected_sha256:
        path.unlink(missing_ok=True)
        raise ModelError(f"model file {path.name} does not match its pinned sha256; deleted, run ingest")


def model_dir(models_dir: Path, params: EmbeddingParams) -> Path:
    return models_dir / params.model.replace("/", "--") / params.revision


# --- the real embedder -----------------------------------------------------


@dataclass(frozen=True)
class GraphSignature:
    inputs: frozenset[str]
    output_shape: tuple[object, ...]


class OnnxEmbedder:
    """bge-small via onnxruntime on CPU: single-threaded, sequential, batch size 1."""

    def __init__(self, onnx_path: Path, vocab_path: Path) -> None:
        import onnxruntime as ort

        vocab = vocab_path.read_text(encoding="utf-8").split("\n")
        while vocab and vocab[-1] == "":
            vocab.pop()
        self.tokenizer = WordPiece([line.strip() for line in vocab])
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

    @classmethod
    def load(cls, models_dir: Path, params: EmbeddingParams) -> OnnxEmbedder:
        """Re-hash both cached files, then build the session. Never downloads."""
        base = model_dir(models_dir, params)
        onnx_path, vocab_path = base / ONNX_FILE, base / VOCAB_FILE
        verify_file(onnx_path, params.onnx_sha256)
        verify_file(vocab_path, params.vocab_sha256)
        return cls(onnx_path, vocab_path)

    def signature(self) -> GraphSignature:
        outputs = self._session.get_outputs()
        return GraphSignature(
            frozenset(i.name for i in self._session.get_inputs()), tuple(outputs[0].shape)
        )

    def _embed(self, text: str) -> bytes:
        ids = self.tokenizer.encode(text)
        n = len(ids)
        feeds = {
            "input_ids": np.array([ids], dtype=np.int64),
            "attention_mask": np.ones((1, n), dtype=np.int64),
            "token_type_ids": np.zeros((1, n), dtype=np.int64),
        }
        hidden = self._session.run(None, feeds)[0]
        cls_vector = np.asarray(hidden[0][0], dtype=np.float64)
        if cls_vector.shape != (DIM,):
            raise ModelError(f"unexpected embedding shape {cls_vector.shape}; expected ({DIM},)")
        norm = float(np.linalg.norm(cls_vector))
        return quantise(cls_vector / norm if norm > 0 else cls_vector)

    def embed_passage(self, text: str) -> bytes:
        return self._embed(text)

    def embed_query(self, question: str) -> bytes:
        return self._embed(QUERY_PREFIX + question)

    def token_count(self, text: str) -> int:
        return len(self.tokenizer.content_ids(text))
