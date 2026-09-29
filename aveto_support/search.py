"""Hybrid retrieval: Porter tokenizer, BM25 ranking-v2, dense similarity, RRF fusion,
and the calibrated confidence rule. No text is ever generated or altered."""

from __future__ import annotations

import math
import random
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

import numpy as np
import numpy.typing as npt

from aveto_support.embed import Embedder, PlaceholderEmbedder
from aveto_support.index import (
    CALIBRATION_LENGTHS,
    CALIBRATION_QUANTILE,
    CALIBRATION_QUERIES,
    CALIBRATION_SEED,
    Index,
    Passage,
    RetrievalParams,
)

SENTINEL_THRESHOLD = 1_000_000.0
INT8_UNIT = 127 * 127

# The NLTK English stopword list (179 words), alphanumeric entries only. Fixed by
# the tech spec; nothing is added or removed.
STOPWORDS: frozenset[str] = frozenset(
    ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "you're", "you've", "you'll", "you'd", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "she's", "her", "hers", "herself", "it", "it's", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "that'll", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "don't", "should", "should've", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "aren't", "couldn", "couldn't", "didn", "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn", "hasn't", "haven", "haven't", "isn", "isn't", "ma", "mightn", "mightn't", "mustn", "mustn't", "needn", "needn't", "shan", "shan't", "shouldn", "shouldn't", "wasn", "wasn't", "weren", "weren't", "won", "won't", "wouldn", "wouldn't"]
)
_STOP_ALNUM: frozenset[str] = frozenset(w for w in STOPWORDS if w.isalnum())

_WORD = re.compile(r"[^\W_]+")


# --- Porter (1980), as published: steps 1a 1b 1c 2 3 4 5a 5b --------------------


def _is_consonant(word: str, i: int) -> bool:
    if word[i] in "aeiou":
        return False
    if word[i] == "y":
        return i == 0 or not _is_consonant(word, i - 1)
    return True


def _measure(stem: str) -> int:
    runs: list[bool] = []
    for i in range(len(stem)):
        kind = _is_consonant(stem, i)
        if not runs or runs[-1] != kind:
            runs.append(kind)
    if runs and runs[0]:
        runs = runs[1:]
    return len(runs) // 2


def _has_vowel(stem: str) -> bool:
    return any(not _is_consonant(stem, i) for i in range(len(stem)))


def _double_consonant(word: str) -> bool:
    return len(word) >= 2 and word[-1] == word[-2] and _is_consonant(word, len(word) - 1)


def _cvc(word: str) -> bool:
    n = len(word)
    return (
        n >= 3
        and _is_consonant(word, n - 3)
        and not _is_consonant(word, n - 2)
        and _is_consonant(word, n - 1)
        and word[-1] not in "wxy"
    )


_STEP2 = {
    "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance", "izer": "ize",
    "abli": "able", "alli": "al", "entli": "ent", "eli": "e", "ousli": "ous",
    "ization": "ize", "ation": "ate", "ator": "ate", "alism": "al", "iveness": "ive",
    "fulness": "ful", "ousness": "ous", "aliti": "al", "iviti": "ive", "biliti": "ble",
}
_STEP3 = {
    "icate": "ic", "ative": "", "alize": "al", "iciti": "ic", "ical": "ic", "ful": "", "ness": "",
}
_STEP4 = (
    "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement", "ment", "ent",
    "ion", "ou", "ism", "ate", "iti", "ous", "ive", "ize",
)


def _replace_longest(word: str, rules: dict[str, str]) -> str:
    for suffix in sorted(rules, key=len, reverse=True):
        if word.endswith(suffix):
            stem = word[: -len(suffix)]
            return stem + rules[suffix] if _measure(stem) > 0 else word
    return word


def stem(word: str) -> str:
    """Porter's 1980 suffix-stripping algorithm. Tokens of length <= 2 are unchanged."""
    if len(word) <= 2:
        return word
    w = word
    # step 1a
    if w.endswith(("sses", "ies")):
        w = w[:-2]
    elif w.endswith("ss"):
        pass
    elif w.endswith("s"):
        w = w[:-1]
    # step 1b
    if w.endswith("eed"):
        if _measure(w[:-3]) > 0:
            w = w[:-1]
    else:
        trimmed: str | None = None
        for suffix in ("ed", "ing"):
            if w.endswith(suffix):
                if _has_vowel(w[: -len(suffix)]):
                    trimmed = w[: -len(suffix)]
                break
        if trimmed is not None:
            w = trimmed
            if w.endswith(("at", "bl", "iz")):
                w += "e"
            elif _double_consonant(w) and w[-1] not in "lsz":
                w = w[:-1]
            elif _measure(w) == 1 and _cvc(w):
                w += "e"
    # step 1c
    if w.endswith("y") and _has_vowel(w[:-1]):
        w = w[:-1] + "i"
    # steps 2 and 3
    w = _replace_longest(w, _STEP2)
    w = _replace_longest(w, _STEP3)
    # step 4
    for suffix in sorted(_STEP4, key=len, reverse=True):
        if w.endswith(suffix):
            base = w[: -len(suffix)]
            if _measure(base) > 1 and (suffix != "ion" or base.endswith(("s", "t"))):
                w = base
            break
    # step 5a
    if w.endswith("e"):
        base = w[:-1]
        measure = _measure(base)
        if measure > 1 or (measure == 1 and not _cvc(base)):
            w = base
    # step 5b
    if _measure(w) > 1 and _double_consonant(w) and w.endswith("l"):
        w = w[:-1]
    return w


def tokenize(text: str) -> list[str]:
    return [stem(w) for w in _WORD.findall(text.casefold()) if w not in _STOP_ALNUM]


# --- result types ----------------------------------------------------------


@dataclass(frozen=True)
class Hit:
    rank: int
    passage: Passage
    score: float
    url: str


@dataclass(frozen=True)
class RetrievalResult:
    question: str
    confident: bool
    hits: tuple[Hit, ...]
    confidence: float
    threshold: float
    reason: Literal["ok", "no-searchable-words", "no-passage-matched", "below-threshold"]
    corroboration: float = 0.0
    ranking_mode: str = "lexical"
    generation_mode: Literal["deterministic"] = "deterministic"

    def __post_init__(self) -> None:
        if not (self.confident == (self.reason == "ok") == (len(self.hits) > 0)):
            raise ValueError("inconsistent RetrievalResult: confident, reason and hits must agree")


@dataclass(frozen=True)
class Analysis:
    """Everything retrieval learns about a question, before the confidence rule."""

    question: str
    searchable: bool
    top: tuple[tuple[Passage, float], ...]  # fused, capped, in rank order; not confidence-gated
    dense_top1: float
    corroboration: float


# --- ranking ---------------------------------------------------------------


def _body_text(passage: Passage) -> str:
    lines = passage.text.split("\n")
    return "\n".join(lines[1:] if passage.heading_path else lines)


def _path_tokens(path: str) -> list[str]:
    name = path.rsplit("/", 1)[-1]
    stem_path = path.rsplit(".", 1)[0] if "." in name else path
    return tokenize(stem_path)


def _bag(passage: Passage, params: RetrievalParams) -> Counter[str]:
    bag: Counter[str] = Counter(tokenize(_body_text(passage)))
    for token in tokenize(" ".join(passage.heading_path)):
        bag[token] += params.heading_weight
    for token in _path_tokens(passage.path):
        bag[token] += params.path_weight
    return bag


def body_tokens(passage: Passage) -> set[str]:
    return set(tokenize(_body_text(passage)))


def _idf(n: int, df: int) -> float:
    return math.log(1 + (n - df + 0.5) / (df + 0.5))


class _Corpus:
    """BM25 statistics over a list of bags."""

    def __init__(self, bags: Sequence[Counter[str]]) -> None:
        self.n = len(bags)
        self.lengths = [sum(b.values()) for b in bags]
        self.avgdl = (sum(self.lengths) / self.n) if self.n else 0.0
        self.postings: dict[str, list[tuple[int, int]]] = {}
        for bag_id, bag in enumerate(bags):
            for term in sorted(bag):
                self.postings.setdefault(term, []).append((bag_id, bag[term]))

    def idf(self, term: str) -> float:
        return _idf(self.n, len(self.postings.get(term, ())))

    def scores(self, terms: Sequence[str], k1: float, b: float) -> dict[int, float]:
        out: dict[int, float] = {}
        for term in sorted(set(terms)):
            postings = self.postings.get(term)
            if not postings:
                continue
            idf = self.idf(term)
            for bag_id, tf in postings:
                norm = k1 * (1 - b + b * self.lengths[bag_id] / self.avgdl)
                out[bag_id] = out.get(bag_id, 0.0) + idf * tf * (k1 + 1) / (tf + norm)
        return out


class DenseMatrix:
    """int8 passage vectors; similarity is an exact integer dot product / 127^2."""

    def __init__(self, passages: Sequence[Passage]) -> None:
        self._matrix: npt.NDArray[np.int32] = (
            np.array([np.frombuffer(p.embedding, dtype=np.int8) for p in passages], dtype=np.int32)
            if passages
            else np.zeros((0, 0), dtype=np.int32)
        )

    def dots(self, query: bytes) -> npt.NDArray[np.int64]:
        vector = np.frombuffer(query, dtype=np.int8).astype(np.int32)
        return (self._matrix @ vector).astype(np.int64)

    def top1(self, query: bytes) -> float:
        return int(self.dots(query).max()) / INT8_UNIT


class Searcher:
    def __init__(self, index: Index, embedder: Embedder | None = None) -> None:
        self.index = index
        self.embedder: Embedder = embedder if embedder is not None else PlaceholderEmbedder()
        params = index.params
        self._params = params
        self._passages = index.passages
        self._pos = {(p.path, p.line_start): i for i, p in enumerate(self._passages)}
        self._bags = [_bag(p, params) for p in self._passages]
        self._passage_corpus = _Corpus(self._bags)
        files: dict[str, list[int]] = {}
        for pid, passage in enumerate(self._passages):
            files.setdefault(passage.path, []).append(pid)
        self._file_names = sorted(files)
        self._file_index = {name: i for i, name in enumerate(self._file_names)}
        file_bags: list[Counter[str]] = []
        for name in self._file_names:
            bag: Counter[str] = Counter()
            for pid in files[name]:
                bag.update(tokenize(self._passages[pid].text))
            for token in _path_tokens(name):
                bag[token] += params.path_weight
            file_bags.append(bag)
        self._file_corpus = _Corpus(file_bags)
        self._dense = DenseMatrix(self._passages)

    def idf(self, term: str) -> float:
        return self._passage_corpus.idf(term)

    def _rank_ids(self, terms: Sequence[str]) -> list[tuple[int, float]]:
        p = self._params
        passage_scores = self._passage_corpus.scores(terms, p.k1, p.b)
        candidates = {pid: s for pid, s in passage_scores.items() if s > 0}
        if not candidates:
            return []
        file_scores = self._file_corpus.scores(terms, p.k1, p.b)
        file_of = {pid: self._file_index[self._passages[pid].path] for pid in candidates}
        p_max = max(candidates.values())
        f_max = max(file_scores.get(f, 0.0) for f in set(file_of.values()))
        combined: list[tuple[int, float]] = []
        for pid, ps in candidates.items():
            fs = file_scores.get(file_of[pid], 0.0)
            f_part = fs / f_max if f_max > 0 else 0.0
            combined.append((pid, p.file_lambda * ps / p_max + (1 - p.file_lambda) * f_part))
        combined.sort(key=lambda item: (-item[1], self._passages[item[0]].path, self._passages[item[0]].line_start))
        return combined

    def rank(self, terms: Sequence[str]) -> list[tuple[Passage, float]]:
        """Lexical candidates (P > 0) ordered by (-combined score, path, line_start)."""
        return [(self._passages[pid], s) for pid, s in self._rank_ids(terms)]

    def corroboration(self, terms: Sequence[str], passage: Passage) -> float:
        bag = self._bags[self._pos[(passage.path, passage.line_start)]]
        matched = [self.idf(t) for t in sorted(set(terms)) if t in bag]
        return sum(matched) - max(matched) if matched else 0.0

    def dense_ranked(self, query: bytes) -> list[tuple[int, float]]:
        dots = self._dense.dots(query)
        order = sorted(
            range(len(self._passages)),
            key=lambda i: (-int(dots[i]), self._passages[i].path, self._passages[i].line_start),
        )
        return [(i, int(dots[i]) / INT8_UNIT) for i in order]

    def fused(self, terms: Sequence[str], query: bytes) -> list[tuple[int, float]]:
        """Reciprocal Rank Fusion over the top `fusion_depth` of the lexical and dense lists."""
        emb = self._params.embedding
        lists = (
            [pid for pid, _ in self._rank_ids(terms)[: emb.fusion_depth]],
            [pid for pid, _ in self.dense_ranked(query)[: emb.fusion_depth]],
        )
        scores: dict[int, float] = {}
        for ranked in lists:
            for rank, pid in enumerate(ranked, start=1):
                scores[pid] = scores.get(pid, 0.0) + 1.0 / (emb.rrf_k + rank)
        return sorted(
            scores.items(),
            key=lambda item: (-item[1], self._passages[item[0]].path, self._passages[item[0]].line_start),
        )

    def passage(self, pid: int) -> Passage:
        return self._passages[pid]


def capped(ranked: Sequence[tuple[Passage, float]], params: RetrievalParams) -> list[tuple[Passage, float]]:
    """Apply the per-file cap and top_k to a ranked list."""
    kept: list[tuple[Passage, float]] = []
    per_file: Counter[str] = Counter()
    for passage, score in ranked:
        if per_file[passage.path] >= params.per_file_cap:
            continue
        per_file[passage.path] += 1
        kept.append((passage, score))
        if len(kept) == params.top_k:
            break
    return kept


def _escape_path(path: str) -> str:
    return path.replace("%", "%25").replace(" ", "%20").replace("#", "%23").replace("?", "%3F")


def permalink(repo: str, commit: str, passage: Passage) -> str:
    return (
        f"https://github.com/{repo}/blob/{commit}/{_escape_path(passage.path)}"
        f"?plain=1#L{passage.line_start}-L{passage.line_end}"
    )


def analyse(searcher: Searcher, question: str) -> Analysis:
    """Rank a question. Runs the embedder on the question, locally."""
    embedder = searcher.embedder
    searchable = embedder.token_count(question) > 0
    if not searchable or not searcher.index.passages:
        return Analysis(question, searchable, (), 0.0, 0.0)
    terms = sorted(set(tokenize(question)))
    query = embedder.embed_query(question)
    dense = searcher.dense_ranked(query)
    fused = searcher.fused(terms, query)
    params = searcher.index.params
    top = capped([(searcher.passage(pid), score) for pid, score in fused], params)
    corroboration = searcher.corroboration(terms, top[0][0]) if top and terms else 0.0
    return Analysis(question, True, tuple(top), dense[0][1], corroboration)


def decide(searcher: Searcher, analysis: Analysis) -> RetrievalResult:
    index = searcher.index
    emb = index.params.embedding
    mode = f"hybrid:{emb.model}@{emb.revision}"
    threshold = index.threshold
    q = analysis.question

    def refuse(reason: Literal["no-searchable-words", "no-passage-matched", "below-threshold"]) -> RetrievalResult:
        return RetrievalResult(
            q, False, (), analysis.dense_top1, threshold, reason, analysis.corroboration, mode
        )

    if not analysis.searchable:
        return refuse("no-searchable-words")
    if not analysis.top:
        return refuse("no-passage-matched")
    if analysis.dense_top1 < threshold:
        return refuse("below-threshold")
    hits = tuple(
        Hit(rank, passage, score, permalink(index.repo, index.commit, passage))
        for rank, (passage, score) in enumerate(analysis.top, start=1)
    )
    return RetrievalResult(q, True, hits, analysis.dense_top1, threshold, "ok", analysis.corroboration, mode)


def retrieve(searcher: Searcher, question: str) -> RetrievalResult:
    return decide(searcher, analyse(searcher, question))


# --- calibration -----------------------------------------------------------


@dataclass(frozen=True)
class Calibration:
    tau_salad: float
    tau_offtopic: float | None
    threshold: float


def eligible_passages_by_file(passages: Sequence[Passage]) -> dict[str, list[Passage]]:
    by_file: dict[str, list[Passage]] = {}
    for passage in sorted(passages, key=lambda p: (p.path, p.line_start)):
        if body_tokens(passage):
            by_file.setdefault(passage.path, []).append(passage)
    return by_file


def _nearest_rank(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[math.ceil(quantile * len(ordered)) - 1]


def calibrate(
    passages: Sequence[Passage],
    embedder: Embedder,
    offtopic: Sequence[str] = (),
) -> Calibration:
    """Method cross-file-null-v3+offtopic-v1: tau = max(p90 word salads, p90 off-topic questions).

    Passages must already carry their embeddings.
    """
    by_file = eligible_passages_by_file(passages)
    files = sorted(by_file)
    ordered = sorted(passages, key=lambda p: (p.path, p.line_start))
    dense = DenseMatrix(ordered)
    if len(files) < max(CALIBRATION_LENGTHS):
        tau_salad = SENTINEL_THRESHOLD
    else:
        rng = random.Random(CALIBRATION_SEED)
        values: list[float] = []
        for _ in range(CALIBRATION_QUERIES):
            length = rng.choice(list(CALIBRATION_LENGTHS))
            tokens: set[str] = set()
            for path in rng.sample(files, length):
                passage = rng.choice(by_file[path])
                tokens.add(rng.choice(sorted(body_tokens(passage))))
            values.append(dense.top1(embedder.embed_query(" ".join(sorted(tokens)))))
        tau_salad = round(_nearest_rank(values, CALIBRATION_QUANTILE), 6)
    tau_offtopic: float | None = None
    if offtopic and ordered:
        sims = [dense.top1(embedder.embed_query(question)) for question in offtopic]
        tau_offtopic = round(_nearest_rank(sims, CALIBRATION_QUANTILE), 6)
    threshold = round(max(tau_salad, tau_offtopic if tau_offtopic is not None else tau_salad), 6)
    return Calibration(tau_salad, tau_offtopic, threshold)
