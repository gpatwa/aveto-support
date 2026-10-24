"""Service settings, read from the environment once at startup.

Fail closed: any value of ASK_KILL_SWITCH other than exactly `off`, and any setting that
cannot be parsed, turns the kill switch on.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Literal

# claude-sonnet-5-5: $2 per million input tokens, $10 per million output tokens (1 nano-dollar
# per token is $1 per million). Read 2026-10-23 from Anthropic's pricing page and matched by
# the owner's console bill.
DEFAULT_PRICE_IN_NANO = 2000
DEFAULT_PRICE_OUT_NANO = 10000
DEFAULT_MONTHLY_CAP_USD = "10"
DAYS_IN_LONGEST_MONTH = 31
NANO = 10**9


@dataclass(frozen=True)
class Settings:
    kill_switch: Literal["on", "off"] = "on"
    api_key: str = field(default="", repr=False)
    client_key: Literal["xff_last", "peer"] = "xff_last"
    price_in_nano_per_token: int = DEFAULT_PRICE_IN_NANO
    price_out_nano_per_token: int = DEFAULT_PRICE_OUT_NANO
    monthly_cap_usd: str = DEFAULT_MONTHLY_CAP_USD
    index_path: str = "index/docs-index.json"
    models_path: str = "models"
    prompt_path: str = "prompts/answerability-judge-v1.txt"

    @property
    def daily_cap_nano(self) -> int:
        """The day's share in integer nano-dollars: monthly cap over the longest month."""
        return int(Decimal(self.monthly_cap_usd) * NANO) // DAYS_IN_LONGEST_MONTH

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if environ is None else environ
        kill: Literal["on", "off"] = "off" if env.get("ASK_KILL_SWITCH") == "off" else "on"
        try:
            price_in = _positive_int(env.get("ASK_PRICE_IN_NANO_PER_TOKEN"), DEFAULT_PRICE_IN_NANO)
            price_out = _positive_int(
                env.get("ASK_PRICE_OUT_NANO_PER_TOKEN"), DEFAULT_PRICE_OUT_NANO
            )
            cap = env.get("ASK_MONTHLY_CAP_USD", DEFAULT_MONTHLY_CAP_USD)
            if Decimal(cap) <= 0 or not Decimal(cap).is_finite():
                raise ValueError("cap")
            mode = env.get("ASK_CLIENT_KEY", "xff_last")
            if mode not in ("xff_last", "peer"):
                raise ValueError("client key mode")
        except (ValueError, InvalidOperation):
            return cls(kill_switch="on", api_key=env.get("ANTHROPIC_API_KEY", ""))
        return cls(
            kill_switch=kill,
            api_key=env.get("ANTHROPIC_API_KEY", ""),
            client_key="peer" if mode == "peer" else "xff_last",
            price_in_nano_per_token=price_in,
            price_out_nano_per_token=price_out,
            monthly_cap_usd=cap,
            index_path=env.get("ASK_INDEX", "index/docs-index.json"),
            models_path=env.get("ASK_MODELS", "models"),
        )


def _positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    number = int(value)
    if number <= 0:
        raise ValueError("price")
    return number
