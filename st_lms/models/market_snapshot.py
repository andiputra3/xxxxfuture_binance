from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

from st_lms.models.candle import Candle
from st_lms.models.open_interest import OpenInterest


@dataclass(slots=True, frozen=True)
class MarketSnapshot:
    """Observe layer output — seluruh snapshot market pada satu timestamp."""

    snapshot_id: str
    symbol: str
    timestamp: int
    candle: Candle
    open_interest: OpenInterest
    volume: Decimal
    exchange_data: Dict  # metadata exchange (funding rate, dll)

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.volume < Decimal("0"):
            raise ValueError("volume cannot be negative")
