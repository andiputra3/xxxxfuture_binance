from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def round_price(value: Decimal, tick_size: Decimal) -> Decimal:
    """Round price to nearest tick size."""
    return (value / tick_size).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * tick_size


def percentage_change(old: Decimal, new: Decimal) -> Decimal:
    """Calculate percentage change between two values."""
    if old == Decimal("0"):
        return Decimal("0")
    return ((new - old) / old) * Decimal("100")
