from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import Timeframe


@dataclass(slots=True, frozen=True)
class Candle:
    """Immutable market candle."""

    symbol: str
    timeframe: Timeframe
    timestamp: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        if self.open <= Decimal("0"):
            raise ValueError("open must be greater than zero")
        if self.high <= Decimal("0"):
            raise ValueError("high must be greater than zero")
        if self.low <= Decimal("0"):
            raise ValueError("low must be greater than zero")
        if self.close <= Decimal("0"):
            raise ValueError("close must be greater than zero")
        if self.volume < Decimal("0"):
            raise ValueError("volume cannot be negative")
