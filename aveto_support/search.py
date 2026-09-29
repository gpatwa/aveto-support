"""Lexical retrieval: tokenizer, BM25 ranking, coverage confidence, calibration."""

from __future__ import annotations

import math
import random
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from aveto_support.index import (
    CALIBRATION_LENGTHS,
    CALIBRATION_QUANTILE,
    CALIBRATION_QUERIES,
    CALIBRATION_SEED,
    Index,
    Passage,
    RetrievalParams,
)

# The NLTK English stopword list (179 words), alphanumeric entries only. Fixed by
# the tech spec; nothing is added or removed.
STOPWORDS: frozenset[str] = frozenset(
    ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "you're", "you've", "you'll", "you'd", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "she's", "her", "hers", "herself", "it", "it's", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "that'll", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "don't", "should", "should've", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "aren't", "couldn", "couldn't", "didn", "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn", "hasn't", "haven", "haven't", "isn", "isn't", "ma", "mightn", "mightn't", "mustn", "mustn't", "needn", "needn't", "shan", "shan't", "shouldn", "shouldn't", "wasn", "wasn't", "weren", "weren't", "won", "won't", "wouldn", "wouldn't"]
)
_STOP_ALNUM: frozenset[str] = frozenset(w for w in STOPWORDS if w.isalnum())

_WORD = re.compile(r"[^\W_]+")


def stem(word: str) -> str:
    """Harman's S-stemmer: folds plurals only."""
    if len(word) <= 3:
        return word
    if word.endswith("ies") and not word.endswith(("eies", "aies")):
        return word[:-3] + "y"
    if word.endswith("es") and not word.endswith(("aes", "ees", "oes")):
        return word[:-2] + "e"
    if word.endswith("s") and not word.endswith(("us", "ss")):
        return word[:-1]
    return word


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
    coverage: float
    threshold: float
    reason: Literal["ok", "no-searchable-words", "no-passage-matched", "below-threshold"]
    generation_mode: Literal["deterministic"] = "deterministic"

    def __post_init__(self) -> None:
        if not (self.confident == (self.reason == "ok") == (len(self.hits) > 0)):
            raise ValueError("inconsistent RetrievalResult: confident, reason and hits must agree")


# --- ranking ---------------------------------------------------------------


def _body_text(passage: Passage) -> str:
    lines = passage.text.split("\n")
    return "\n".join(lines[1:] if passage.heading_path else lines)


def _bag(passage: Passage, params: RetrievalParams) -> Counter[str]:
    bag: Counter[str] = Counter(tokenize(_body_text(passage)))
    for token in tokenize(" ".join(passage.heading_path)):
        bag[token] += params.heading_weight
    stem_path = passage.path.rsplit(".", 1)[0] if "." in passage.path.rsplit("/", 1)[-1] else passage.path
    for token in tokenize(stem_path):
        bag[token] += params.path_weight
    return bag


def body_tokens(passage: Passage) -> set[str]:
    return set(tokenize(_body_text(passage)))


class Searcher:
    def __init__(self, index: Index) -> None:
        self.index = index
        params = index.params
        self._params = params
        self._passages = index.passages
        self._bags = [_bag(p, params) for p in self._passages]
        self._pos = {(p.path, p.line_start): i for i, p in enumerate(self._passages)}
        self._lengths = [sum(b.values()) for b in self._bags]
        n = len(self._passages)
        self._avgdl = (sum(self._lengths) / n) if n else 0.0
        self._postings: dict[str, list[tuple[int, int]]] = {}
        for pid, bag in enumerate(self._bags):
            for term in sorted(bag):
                self._postings.setdefault(term, []).append((pid, bag[term]))

    def idf(self, term: str) -> float:
        n = len(self._passages)
        df = len(self._postings.get(term, ()))
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def rank(self, terms: Sequence[str]) -> list[tuple[Passage, float]]:
        """All passages with score > 0, ordered by (-score, path, line_start)."""
        k1, b = self._params.k1, self._params.b
        scores: dict[int, float] = {}
        for term in sorted(set(terms)):
            postings = self._postings.get(term)
            if not postings:
                continue
            idf = self.idf(term)
            for pid, tf in postings:
                norm = k1 * (1 - b + b * self._lengths[pid] / self._avgdl)
                scores[pid] = scores.get(pid, 0.0) + idf * tf * (k1 + 1) / (tf + norm)
        ranked = [(self._passages[pid], s) for pid, s in scores.items() if s > 0]
        ranked.sort(key=lambda item: (-item[1], item[0].path, item[0].line_start))
        return ranked

    def coverage(self, terms: Sequence[str], passage: Passage) -> float:
        bag = self._bags[self._pos[(passage.path, passage.line_start)]]
        unique = sorted(set(terms))
        total = sum(self.idf(t) for t in unique)
        if total <= 0:
            return 0.0
        found = sum(self.idf(t) for t in unique if t in bag)
        return found / total


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


def retrieve(searcher: Searcher, question: str) -> RetrievalResult:
    index = searcher.index
    terms = sorted(set(tokenize(question)))
    threshold = index.threshold
    if not terms:
        return RetrievalResult(question, False, (), 0.0, threshold, "no-searchable-words")
    ranked = searcher.rank(terms)
    if not ranked:
        return RetrievalResult(question, False, (), 0.0, threshold, "no-passage-matched")
    coverage = searcher.coverage(terms, ranked[0][0])
    if coverage < threshold:
        return RetrievalResult(question, False, (), coverage, threshold, "below-threshold")
    hits = tuple(
        Hit(rank, passage, score, permalink(index.repo, index.commit, passage))
        for rank, (passage, score) in enumerate(capped(ranked, index.params), start=1)
    )
    return RetrievalResult(question, True, hits, coverage, threshold, "ok")


# --- calibration -----------------------------------------------------------


def eligible_passages_by_file(passages: Sequence[Passage]) -> dict[str, list[Passage]]:
    by_file: dict[str, list[Passage]] = {}
    for passage in sorted(passages, key=lambda p: (p.path, p.line_start)):
        if body_tokens(passage):
            by_file.setdefault(passage.path, []).append(passage)
    return by_file


def calibrate(passages: Sequence[Passage], params: RetrievalParams) -> float:
    """Method cross-file-null-v1: p90 of top-1 coverage of cross-file null queries."""
    by_file = eligible_passages_by_file(passages)
    files = sorted(by_file)
    if len(files) < max(CALIBRATION_LENGTHS):
        return 1.0
    ordered = tuple(sorted(passages, key=lambda p: (p.path, p.line_start)))
    searcher = Searcher(Index("", "", 0, (), ordered, 1.0, params))
    rng = random.Random(CALIBRATION_SEED)
    values: list[float] = []
    for _ in range(CALIBRATION_QUERIES):
        length = rng.choice(list(CALIBRATION_LENGTHS))
        tokens: set[str] = set()
        for path in rng.sample(files, length):
            passage = rng.choice(by_file[path])
            tokens.add(rng.choice(sorted(body_tokens(passage))))
        query = sorted(tokens)
        ranked = searcher.rank(query)
        values.append(searcher.coverage(query, ranked[0][0]) if ranked else 0.0)
    values.sort()
    rank = math.ceil(CALIBRATION_QUANTILE * CALIBRATION_QUERIES) - 1
    return round(values[rank], 6)
