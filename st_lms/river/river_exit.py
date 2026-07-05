from __future__ import annotations

from decimal import Decimal

from st_lms.models.position import Position


class RiverExit:
    """River exit — trailing stop + take profit bertahap."""

    def should_exit(self, position: Position, current_price: Decimal, atr: Decimal) -> bool:
        """Cek exit signal: trailing stop berdasarkan ATR."""
        if position.side.value == "LONG":
            trail_stop = current_price - atr * Decimal("2")
            return trail_stop >= position.entry_price
        else:
            trail_stop = current_price + atr * Decimal("2")
            return trail_stop <= position.entry_price
