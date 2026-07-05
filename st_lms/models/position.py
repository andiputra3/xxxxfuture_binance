from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import PositionSide, PositionState


@dataclass(slots=True, frozen=True)
class Position:
    """Trading position with lifecycle state."""

    position_id: str
    symbol: str
    side: PositionSide
    entry_price: Decimal
    quantity: Decimal
    state: PositionState
    timestamp: int

    def __post_init__(self) -> None:
        if self.entry_price <= Decimal("0"):
            raise ValueError("entry_price must be greater than zero")
        if self.quantity <= Decimal("0"):
            raise ValueError("quantity must be greater than zero")
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
