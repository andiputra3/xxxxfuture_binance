from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from st_lms.common.enums import Direction


@dataclass(slots=True, frozen=True)
class Fill:
    """Partial fill of an order."""
    fill_id: str
    price: Decimal
    quantity: Decimal
    timestamp: int
    fee: Decimal


@dataclass(slots=True, frozen=True)
class Order:
    """An order placed on an exchange (real or simulated).

    order_type: MARKET / LIMIT / STOP / OCO
    state:      PENDING / FILLED / PARTIAL / CANCELLED / REJECTED
    """
    order_id: str
    plan_id: str
    symbol: str
    direction: Direction
    order_type: str  # MARKET, LIMIT, STOP, OCO
    price: Decimal
    quantity: Decimal
    filled_quantity: Decimal
    state: str  # PENDING, FILLED, PARTIAL, CANCELLED, REJECTED
    timestamp: int
    fills: List[Fill]
    oco_order_id: Optional[str] = None  # untuk OCO orders

    def __post_init__(self) -> None:
        if self.quantity <= Decimal("0"):
            raise ValueError("quantity must be > 0")
        if self.filled_quantity < Decimal("0") or self.filled_quantity > self.quantity:
            raise ValueError("filled_quantity out of range")
        if self.price <= Decimal("0"):
            raise ValueError("price must be > 0")
