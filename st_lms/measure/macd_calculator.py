from __future__ import annotations

from decimal import Decimal
from typing import List

from st_lms.common.enums import MACDBucket
from st_lms.models.candle import Candle
from st_lms.models.macd import MACD


def calculate_macd(candles: List[Candle], fast: int = 12, slow: int = 26, signal: int = 9) -> MACD:
    """MACD from close prices with bucket classification."""
    closes = [c.close for c in candles]
    if len(closes) < slow + signal:
        raise ValueError(f"Need at least {slow + signal} candles for MACD")

    ema_fast = _ema(closes, fast)
    ema_slow = _ema(closes, slow)
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = _ema(macd_line, signal)

    offset = len(closes) - len(signal_line)
    m = macd_line[-1]
    s = signal_line[-1]
    h = m - s

    if m > s and h > Decimal("0"):
        bucket = MACDBucket.BULLISH
    elif m < s and h < Decimal("0"):
        bucket = MACDBucket.BEARISH
    elif m > s and h < Decimal("0"):
        bucket = MACDBucket.WEAKENING
    else:
        bucket = MACDBucket.NEUTRAL

    return MACD(
        timestamp=candles[-1].timestamp,
        macd=m,
        signal=s,
        histogram=h,
        bucket=bucket,
    )


def _ema(values: List[Decimal], period: int) -> List[Decimal]:
    multiplier = Decimal("2") / Decimal(str(period + 1))
    result: List[Decimal] = []
    ema = sum(values[:period]) / Decimal(str(period))
    result.append(ema)
    for v in values[period:]:
        ema = (v - ema) * multiplier + ema
        result.append(ema)
    return result
