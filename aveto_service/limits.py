"""Limits that fail closed: question checks, the hashed visitor key, the hourly allowance
and the day's spend. Nothing here stores an IP address or a question."""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from aveto_service.abuse_log import Outcome
from aveto_support import judge

MAX_QUESTION_CHARS = 500
MAX_BODY_BYTES = 16_384
PER_VISITOR_PER_HOUR = 10
WINDOW_SECONDS = 3600.0
MAX_VISITOR_KEYS = 50_000
MAX_TOKENS = 1024  # the adapter's max_tokens; bounds the output part of a reservation
FRAMING_TOKENS = 64


def utc_day(now: datetime) -> str:
    return now.astimezone(UTC).strftime("%Y-%m-%d")


# --- question ---------------------------------------------------------------


@dataclass(frozen=True)
class QuestionCheck:
    """`refusal` is None when the question may go on; `text` is then the stripped question."""

    text: str
    refusal: Outcome | None
    length: int


def validate_question(raw: str) -> QuestionCheck:
    text = raw.replace("\r\n", "\n").strip()
    length = len(text)
    if not text:
        return QuestionCheck(text, Outcome.EMPTY_QUESTION, length)
    if length > MAX_QUESTION_CHARS:
        return QuestionCheck(text, Outcome.TOO_LONG, length)
    try:
        judge.normalise_question(text)
    except judge.QuestionFormatError:
        return QuestionCheck(text, Outcome.UNUSABLE_QUESTION, length)
    return QuestionCheck(text, None, length)


# --- visitor key ------------------------------------------------------------


def resolve_client_ip(xff: str | None, peer: str | None, mode: Literal["xff_last", "peer"]) -> str:
    """The address to key on: the rightmost X-Forwarded-For entry (the one the platform's
    ingress appended), else the connecting peer. Never the leftmost entry."""
    fallback = peer or "unknown"
    if mode == "peer" or not xff:
        return fallback
    last = xff.rsplit(",", 1)[-1].strip()
    try:
        return str(ipaddress.ip_address(last))
    except ValueError:
        return fallback


def client_key(ip_text: str, salt: bytes) -> str:
    """Full hex HMAC-SHA256 of the address; IPv6 by its /64, IPv4-mapped IPv6 as IPv4."""
    try:
        addr = ipaddress.ip_address(ip_text)
    except ValueError:
        material = b"x:" + ip_text.encode("utf-8", "replace")
    else:
        if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
            addr = addr.ipv4_mapped
        if isinstance(addr, ipaddress.IPv6Address):
            material = b"6:" + addr.packed[:8]
        else:
            material = b"4:" + addr.packed
    return hmac.new(salt, material, hashlib.sha256).hexdigest()


# --- hourly allowance -------------------------------------------------------


class RateLimiter:
    """Admitted questions per visitor key in a sliding hour. In memory; callers hold a lock."""

    def __init__(
        self,
        limit: int = PER_VISITOR_PER_HOUR,
        window: float = WINDOW_SECONDS,
        max_keys: int = MAX_VISITOR_KEYS,
    ) -> None:
        self._limit = limit
        self._window = window
        self._max_keys = max_keys
        self._stamps: dict[str, deque[float]] = {}

    def _recent(self, key: str, now: float) -> int:
        stamps = self._stamps.get(key)
        if stamps is None:
            return 0
        while stamps and stamps[0] <= now - self._window:
            stamps.popleft()
        return len(stamps)

    def _sweep(self, now: float) -> None:
        for key in [k for k in self._stamps if self._recent(k, now) == 0]:
            del self._stamps[key]

    def allowed(self, key: str, now: float) -> bool:
        """True if one more question may be admitted for `key`. Does not record anything."""
        if self._recent(key, now) >= self._limit:
            return False
        if key not in self._stamps and len(self._stamps) >= self._max_keys:
            self._sweep(now)
            if len(self._stamps) >= self._max_keys:
                return False
        return True

    def record(self, key: str, now: float) -> None:
        self._stamps.setdefault(key, deque()).append(now)


# --- day's spend ------------------------------------------------------------


@dataclass(frozen=True)
class Reservation:
    day: str
    amount: int  # nano-dollars


class SpendCounter:
    """The UTC day's spend in integer nano-dollars. Callers hold a lock."""

    def __init__(self, cap_nano: int, price_in_nano: int, price_out_nano: int) -> None:
        self.cap = cap_nano
        self.price_in = price_in_nano
        self.price_out = price_out_nano
        self.day = ""
        self.spent = 0
        self.in_flight = 0
        self.closed = False
        self.judged = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def roll(self, day: str) -> None:
        if day != self.day:
            self.day = day
            self.spent = 0
            self.in_flight = 0
            self.closed = False
            self.judged = 0
            self.input_tokens = 0
            self.output_tokens = 0

    def reservation_amount(self, system_bytes: int, payload_bytes: int) -> int:
        """Upper bound on one call: a token covers at least one byte; output is capped."""
        return (
            system_bytes + payload_bytes + FRAMING_TOKENS
        ) * self.price_in + MAX_TOKENS * self.price_out

    def peek(self, day: str, floor: int) -> bool:
        self.roll(day)
        return not self.closed and self.spent + self.in_flight + floor <= self.cap

    def reserve(self, day: str, amount: int) -> Reservation | None:
        """Reserve `amount` or close the day. None means paused."""
        self.roll(day)
        if self.closed:
            return None
        if self.spent + self.in_flight + amount > self.cap:
            self.closed = True
            return None
        self.in_flight += amount
        return Reservation(day, amount)

    def settle(
        self,
        reservation: Reservation,
        actual: int,
        input_tokens: int,
        output_tokens: int,
        *,
        counted: bool = True,
    ) -> None:
        """Replace the reservation by what the calls cost (or a charge kept in full)."""
        if reservation.day == self.day:
            self.in_flight -= reservation.amount
        self.spent += actual
        if counted:
            self.judged += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def cost(self, input_tokens: int, output_tokens: int) -> int:
        return input_tokens * self.price_in + output_tokens * self.price_out


def format_usd(nano: int) -> str:
    """Nano-dollars as `0.000000`, truncated to six decimals."""
    return f"{nano // 10**9}.{(nano % 10**9) // 1000:06d}"
