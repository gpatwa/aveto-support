"""Short-lived store behind the Post/Redirect/Get step: results only, never the question."""

from __future__ import annotations

import secrets
import threading
import time
from collections import OrderedDict
from collections.abc import Callable

from aveto_service.pipeline import AskResult

TTL_SECONDS = 600.0
MAX_ENTRIES = 1000


class ResultStore:
    def __init__(self, monotonic: Callable[[], float] = time.monotonic) -> None:
        self._monotonic = monotonic
        self._lock = threading.Lock()
        self._items: OrderedDict[str, tuple[float, AskResult]] = OrderedDict()

    def put(self, result: AskResult) -> str:
        token = secrets.token_urlsafe(16)
        now = self._monotonic()
        with self._lock:
            self._sweep(now)
            self._items[token] = (now + TTL_SECONDS, result)
            while len(self._items) > MAX_ENTRIES:
                self._items.popitem(last=False)
        return token

    def get(self, token: str) -> AskResult | None:
        now = self._monotonic()
        with self._lock:
            self._sweep(now)
            item = self._items.get(token)
        return item[1] if item is not None else None

    def _sweep(self, now: float) -> None:
        while self._items:
            first = next(iter(self._items))
            if self._items[first][0] > now:
                break
            del self._items[first]
