from __future__ import annotations

from typing import List

from st_lms.models.candle import Candle


def calculate_price_momentum(candles: List[Candle], period: int = 24) -> float:
    """Perubahan harga dalam periode tertentu dalam persen."""
    if len(candles) < period + 1:
        return 0.0

    latest = float(candles[-1].close)
    prev = float(candles[-(period + 1)].close)
    if prev == 0.0:
        return 0.0
    return ((latest - prev) / prev) * 100.0
