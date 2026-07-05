from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class ATR:
    """Immutable ATR model."""

    timestamp: int
    period: int
    value: Decimal

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.period <= 0:
            raise ValueError("period must be greater than zero")
        if self.value < Decimal("0"):
            raise ValueError("ATR value cannot be negative")
