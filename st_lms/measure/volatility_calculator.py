from __future__ import annotations

from math import sqrt
from statistics import stdev
from typing import List

from st_lms.models.candle import Candle


def calculate_volatility(candles: List[Candle], period: int = 14) -> float:
    """Standar deviasi dari close price return sebagai ukuran volatilitas."""
    if len(candles) < period + 1:
        raise ValueError(f"Need at least {period + 1} candles")

    returns = [
        float((candles[i].close - candles[i - 1].close) / candles[i - 1].close)
        for i in range(len(candles) - period, len(candles))
    ]
    return float(stdev(returns)) if len(returns) > 1 else 0.0
