"""Usage counts without content: four integers and a start time, in memory only.

Every method takes an `Outcome` or nothing, so no caller can hand this module a question, an
answer, an address or any other text. Nothing here writes a log line or touches disk.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from aveto_service.abuse_log import Outcome
from aveto_service.limits import RateLimiter

DOCS_CLICKS_PER_HOUR = 60
_CLICK_WINDOW_SECONDS = 3600.0
_CLICK_KEY = "docs"  # one constant key: the limiter keeps timestamps only


@dataclass(frozen=True)
class UsageSnapshot:
    visits: int
    answered: int
    refused: int
    docs_clicks: int
    started_at: datetime  # UTC, when the app was built (process start in production)

    @property
    def asked(self) -> int:
        return self.answered + self.refused


class UsageCounts:
    __slots__ = (
        "_answered",
        "_clicks",
        "_docs_clicks",
        "_lock",
        "_mono",
        "_refused",
        "_started_at",
        "_visits",
    )

    def __init__(self, started_at: datetime, monotonic: Callable[[], float]) -> None:
        self._lock = threading.Lock()
        self._visits = 0
        self._answered = 0
        self._refused = 0
        self._docs_clicks = 0
        self._started_at = started_at
        self._clicks = RateLimiter(
            limit=DOCS_CLICKS_PER_HOUR, window=_CLICK_WINDOW_SECONDS, max_keys=1
        )
        self._mono = monotonic

    def visit(self) -> None:
        with self._lock:
            self._visits += 1

    def record(self, outcome: Outcome) -> None:
        """Count a question that reached an answer or a refusal; every other outcome is ignored."""
        with self._lock:
            if outcome is Outcome.ANSWER:
                self._answered += 1
            elif outcome is Outcome.NO_CONFIDENT_MATCH:
                self._refused += 1

    def docs_click(self) -> bool:
        """Count one click unless 60 are already counted in the rolling hour."""
        with self._lock:
            now = self._mono()
            if not self._clicks.allowed(_CLICK_KEY, now):
                return False
            self._clicks.record(_CLICK_KEY, now)
            self._docs_clicks += 1
            return True

    def snapshot(self) -> UsageSnapshot:
        with self._lock:
            return UsageSnapshot(
                self._visits,
                self._answered,
                self._refused,
                self._docs_clicks,
                self._started_at,
            )
