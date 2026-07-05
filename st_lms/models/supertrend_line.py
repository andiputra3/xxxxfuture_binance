from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import Direction, LineStatus, Timeframe


@dataclass(slots=True, frozen=True)
class SupertrendLine:
    """Immutable Supertrend Line."""

    line_id: str
    symbol: str
    timeframe: Timeframe
    direction: Direction
    price: Decimal
    start_timestamp: int
    end_timestamp: int
    candle_count: int
    touch_count: int
    status: LineStatus

    def __post_init__(self) -> None:
        if self.price <= Decimal("0"):
            raise ValueError("price must be greater than zero")
        if self.start_timestamp < 0:
            raise ValueError("start_timestamp must be >= 0")
        if self.end_timestamp < self.start_timestamp:
            raise ValueError("end_timestamp must be >= start_timestamp")
        if self.candle_count <= 0:
            raise ValueError("candle_count must be greater than zero")
        if self.touch_count < 0:
            raise ValueError("touch_count must be >= 0")
