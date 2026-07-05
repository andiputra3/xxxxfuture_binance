from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import Direction, Timeframe


@dataclass(slots=True, frozen=True)
class SupertrendPoint:
    """Immutable Supertrend Point."""

    point_id: str
    symbol: str
    timeframe: Timeframe
    timestamp: int
    price: Decimal
    atr: Decimal
    direction: Direction
    candle_index: int

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.price <= Decimal("0"):
            raise ValueError("price must be greater than zero")
        if self.atr < Decimal("0"):
            raise ValueError("atr cannot be negative")
        if self.candle_index < 0:
            raise ValueError("candle_index must be >= 0")
