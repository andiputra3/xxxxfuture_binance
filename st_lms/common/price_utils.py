from __future__ import annotations

from decimal import Decimal


def validate_positive_price(price: Decimal, name: str = "price") -> None:
    """Validate that a price value is positive."""
    if price <= Decimal("0"):
        raise ValueError(f"{name} must be greater than zero")
