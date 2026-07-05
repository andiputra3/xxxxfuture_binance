from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import OpenInterestState


@dataclass(slots=True, frozen=True)
class OpenInterest:
    """Immutable Open Interest model."""

    symbol: str
    timestamp: int
    value: Decimal
    state: OpenInterestState

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.value < Decimal("0"):
            raise ValueError("Open Interest cannot be negative")
