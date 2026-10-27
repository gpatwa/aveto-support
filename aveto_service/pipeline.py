"""The ask pipeline: the gates in a fixed fail-closed order, then retrieve, judge, map.

Every step before the model call makes no model call. Every request writes one abuse line.
The question is used for retrieval and the judge payload and then dropped: it is not in
`AskResult`, not in a log line, not stored.
"""

from __future__ import annotations

import secrets
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aveto_service.abuse_log import Outcome, emit_abuse
from aveto_service.judge_port import (
    MAX_ATTEMPTS,
    JudgeCall,
    JudgeClient,
    JudgeNotConfiguredError,
    JudgeTransportError,
)
from aveto_service.limits import (
    MAX_QUESTION_CHARS,
    RETRIEVALS_PER_VISITOR_PER_HOUR,
    RateLimiter,
    Reservation,
    SpendCounter,
    client_key,
    format_usd,
    utc_day,
    validate_question,
)
from aveto_service.settings import Settings
from aveto_support import judge
from aveto_support.search import RetrievalResult, Searcher

_STATUS: dict[Outcome, int] = {
    Outcome.ANSWER: 200,
    Outcome.NO_CONFIDENT_MATCH: 200,
    Outcome.JUDGE_ERROR: 502,
    Outcome.EMPTY_QUESTION: 400,
    Outcome.UNUSABLE_QUESTION: 400,
    Outcome.TOO_LONG: 400,
    Outcome.BAD_REQUEST: 400,
    Outcome.BODY_TOO_LARGE: 413,
    Outcome.RATE_LIMITED: 429,
    Outcome.PAUSED: 503,
    Outcome.SERVICE_OFF: 503,
}
_ADMITTED = frozenset({Outcome.ANSWER, Outcome.NO_CONFIDENT_MATCH, Outcome.JUDGE_ERROR})
NO_CONFIDENT_MATCH_TEXT = "no confident match"
JUDGE_ERROR_TEXT = "judge error"
TOP_OF_FILE = "(top of file)"
WARM_QUESTION = "How do I get started?"  # fixed and internal: never a visitor's text


@dataclass(frozen=True)
class PassageOut:
    heading: str
    line_start: int
    line_end: int
    url: str
    text: str


@dataclass(frozen=True)
class FileOut:
    rank: int
    path: str
    url: str
    passages: tuple[PassageOut, ...]


@dataclass(frozen=True)
class AskResult:
    """What a request came to. Holds public documentation text, never the question."""

    outcome: Outcome
    docs_repo: str = ""
    docs_commit: str = ""
    files: tuple[FileOut, ...] = ()
    signal: str = ""
    length: int | None = None  # only for too_long

    @property
    def status(self) -> int:
        return _STATUS[self.outcome]

    @property
    def admitted(self) -> bool:
        """True if the request got as far as the model call (the page redirects, not re-asks)."""
        return self.outcome in _ADMITTED

    def to_json(self) -> dict[str, Any]:
        o = self.outcome
        if o is Outcome.ANSWER:
            return {
                "outcome": o.value,
                "docs": {"repo": self.docs_repo, "commit": self.docs_commit},
                "files": [
                    {
                        "rank": f.rank,
                        "path": f.path,
                        "url": f.url,
                        "passages": [
                            {
                                "heading": p.heading,
                                "line_start": p.line_start,
                                "line_end": p.line_end,
                                "url": p.url,
                                "text": p.text,
                            }
                            for p in f.passages
                        ],
                    }
                    for f in self.files
                ],
                "signal": self.signal,
            }
        if o is Outcome.NO_CONFIDENT_MATCH:
            return {"outcome": o.value, "text": NO_CONFIDENT_MATCH_TEXT, "signal": self.signal}
        if o is Outcome.JUDGE_ERROR:
            return {"outcome": o.value, "text": JUDGE_ERROR_TEXT}
        if o is Outcome.TOO_LONG:
            return {"outcome": o.value, "length": self.length, "limit": MAX_QUESTION_CHARS}
        return {"outcome": o.value}


@dataclass(frozen=True)
class Runtime:
    system_prompt: str
    searcher: Searcher


def _files_out(result: RetrievalResult) -> tuple[FileOut, ...]:
    return tuple(
        FileOut(
            rank=hit.rank,
            path=hit.path,
            url=hit.url,
            passages=tuple(
                PassageOut(
                    heading=" > ".join(m.passage.heading_path)
                    if m.passage.heading_path
                    else TOP_OF_FILE,
                    line_start=m.passage.line_start,
                    line_end=m.passage.line_end,
                    url=m.url,
                    text=m.passage.text,
                )
                for m in hit.passages
            ),
        )
        for hit in result.files
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _search_once(searcher: Searcher, question: str) -> None:
    """One retrieval, result discarded: loads the index and the embedding model's first run."""
    judge.retrieve_for_judge(searcher, question)


class AskService:
    def __init__(
        self,
        runtime: Runtime,
        judge_client: JudgeClient,
        settings: Settings,
        *,
        clock: Callable[[], datetime] = _utcnow,
        monotonic: Callable[[], float] | None = None,
        limiter: RateLimiter | None = None,
    ) -> None:
        self._runtime = runtime
        self._judge = judge_client
        self._settings = settings
        self._clock = clock
        self._mono = monotonic or time.monotonic
        self._salt = secrets.token_bytes(32)
        self._rate = limiter or RateLimiter()
        self._retrievals = RateLimiter(limit=RETRIEVALS_PER_VISITOR_PER_HOUR)
        self._spend = SpendCounter(
            settings.daily_cap_nano,
            settings.price_in_nano_per_token,
            settings.price_out_nano_per_token,
        )
        self._lock = threading.Lock()  # admission and counters
        self._retrieval_lock = threading.Lock()  # the ONNX session: one thread at a time
        self._warm_lock = threading.Lock()
        self._warm_result: bool | None = None
        self._system_bytes = len(runtime.system_prompt.encode("utf-8"))
        self._floor = MAX_ATTEMPTS * self._spend.reservation_amount(self._system_bytes, 0)

    # --- request-level helpers -------------------------------------------------

    def key_of(self, client_ip: str) -> str:
        return client_key(client_ip, self._salt)

    def refuse(self, outcome: Outcome, client_ip: str) -> AskResult:
        """A refusal decided before the question is read (kill switch, body, shape)."""
        return self._finish(outcome, self.key_of(client_ip), AskResult(outcome))

    def _finish(self, outcome: Outcome, key: str, result: AskResult) -> AskResult:
        emit_abuse(key[:16], outcome, self._clock())
        return result

    # --- the pipeline ----------------------------------------------------------

    def ask(self, raw: str, client_ip: str) -> AskResult:
        key = self.key_of(client_ip)
        try:
            result = self._ask(raw, key)
        except Exception:  # noqa: BLE001 - fail closed: any failure is a refusal
            result = AskResult(Outcome.JUDGE_ERROR)
        return self._finish(result.outcome, key, result)

    def _ask(self, raw: str, key: str) -> AskResult:
        if self._settings.kill_switch != "off":  # 1
            return AskResult(Outcome.SERVICE_OFF)
        check = validate_question(raw)  # 3
        if check.refusal is not None:
            return AskResult(
                check.refusal, length=check.length if check.refusal is Outcome.TOO_LONG else None
            )
        day = utc_day(self._clock())
        now = self._mono()
        try:
            with self._lock:  # 4, 5
                if not self._rate.allowed(key, now):
                    return AskResult(Outcome.RATE_LIMITED)
                if not self._retrievals.allowed(key, now):  # bounds work refused after retrieval
                    return AskResult(Outcome.RATE_LIMITED)
                if not self._spend.peek(day, self._floor):
                    return AskResult(Outcome.PAUSED)
                self._retrievals.record(key, now)  # counted whatever happens next
        except Exception:  # noqa: BLE001 - fail closed: any failure is a refusal
            return AskResult(Outcome.RATE_LIMITED)
        try:  # 6
            with self._retrieval_lock:
                found = judge.retrieve_for_judge(self._runtime.searcher, check.text)
                payload = judge.format_judge_input(found)
        except judge.QuestionFormatError:
            return AskResult(Outcome.UNUSABLE_QUESTION)
        except Exception:  # noqa: BLE001 - fail closed: any failure is a refusal
            return AskResult(Outcome.JUDGE_ERROR)
        per_attempt = self._spend.reservation_amount(
            self._system_bytes, len(payload.encode("utf-8"))
        )
        with self._lock:  # 7: day and time are taken again, so a midnight straddle is safe
            day = utc_day(self._clock())
            now = self._mono()
            if not self._rate.allowed(key, now):
                return AskResult(Outcome.RATE_LIMITED)
            reservation = self._spend.reserve(day, MAX_ATTEMPTS * per_attempt)  # every attempt
            if reservation is None:
                return AskResult(Outcome.PAUSED)
            self._rate.record(key, now)
        return self._judged(found, payload, reservation, per_attempt)  # 8, 9

    def _judged(
        self, found: RetrievalResult, payload: str, reservation: Reservation, per_attempt: int
    ) -> AskResult:
        """Each attempt is charged on its own outcome; what was reserved and not used returns."""
        call: JudgeCall | None = None
        charge = 0
        in_tokens = out_tokens = 0
        try:
            call = self._judge.judge(self._runtime.system_prompt, payload)
        except JudgeNotConfiguredError:
            with self._lock:
                self._spend.settle(reservation, 0, 0, 0, counted=False)
            return AskResult(Outcome.JUDGE_ERROR)
        except JudgeTransportError as exc:
            charge = exc.billable_failures * per_attempt
        except Exception:  # noqa: BLE001 - an unexpected adapter failure is a failed attempt
            charge = per_attempt  # one attempt, in full
        if call is not None:
            failed = (
                call.billable_failures
                if call.billable_failures is not None
                else max(0, call.attempts - 1)
            )
            if call.input_tokens is None or call.output_tokens is None:
                charge = per_attempt + failed * per_attempt
            else:
                in_tokens, out_tokens = call.input_tokens, call.output_tokens
                charge = self._spend.cost(in_tokens, out_tokens) + failed * per_attempt
        with self._lock:
            self._spend.settle(reservation, charge, in_tokens, out_tokens)
        if call is None:
            return AskResult(Outcome.JUDGE_ERROR)
        if len(call.reply.encode("utf-8")) > judge.MAX_REPLY_BYTES:
            return AskResult(Outcome.JUDGE_ERROR)  # the core's "reply too long" (S-A4)
        try:
            verdict = judge.parse_verdict(call.reply, judge.BLOCK_ID)
        except judge.JudgeError:
            return AskResult(Outcome.JUDGE_ERROR)
        signal = judge.signal_line(verdict)
        if verdict.token == "NOT_ANSWERABLE":
            return AskResult(Outcome.NO_CONFIDENT_MATCH, signal=signal)
        index = self._runtime.searcher.index
        return AskResult(
            Outcome.ANSWER,
            docs_repo=index.repo,
            docs_commit=index.commit,
            files=_files_out(found),
            signal=signal,
        )

    # --- resting and warm-up (no model call, no spend, no limiter, no log line) -------

    def resting(self) -> bool:
        """True when settled spend already leaves no room for the smallest request today.

        A pure read: it rolls nothing and reserves nothing, so it changes no counter."""
        with self._lock:
            day = utc_day(self._clock())
            s = self._spend
            today = s.day == day
            return (today and s.closed) or ((s.spent if today else 0) + self._floor > s.cap)

    def warm(self) -> bool:
        """Run one fixed search so the first visitor's search is not the first one.
        Remembers only success; a failure answers not-ready and the next call retries."""
        with self._warm_lock:
            if not self._warm_result:
                try:
                    with self._retrieval_lock:
                        _search_once(self._runtime.searcher, WARM_QUESTION)
                    self._warm_result = True
                except Exception:  # noqa: BLE001 - not ready is the whole answer
                    return False
            return True

    # --- health ----------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        with self._lock:
            day = utc_day(self._clock())
            self._spend.roll(day)
            s = self._spend
            return {
                "status": "ok",
                "kill_switch": self._settings.kill_switch,
                "day": day,
                "judged_today": s.judged,
                "input_tokens_today": s.input_tokens,
                "output_tokens_today": s.output_tokens,
                "spend_today_usd": format_usd(s.spent),
                "daily_cap_usd": format_usd(s.cap),
            }
