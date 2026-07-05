from __future__ import annotations

from decimal import Decimal
from typing import List

from st_lms.models.atr import ATR
from st_lms.models.candle import Candle


def calculate_atr(candles: List[Candle], period: int = 10) -> ATR:
    """Wilder-smoothed ATR from candle high/low/close."""
    if len(candles) < period + 1:
        raise ValueError(f"Need at least {period + 1} candles")

    tr_values: List[Decimal] = []
    for i in range(1, len(candles)):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i - 1].close
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_values.append(tr)

    raw_atr = sum(tr_values[:period]) / Decimal(str(period))
    for val in tr_values[period:]:
        raw_atr = (raw_atr * Decimal(str(period - 1)) + val) / Decimal(str(period))

    return ATR(
        timestamp=candles[-1].timestamp,
        period=period,
        value=raw_atr,
    )
