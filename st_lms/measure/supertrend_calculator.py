from __future__ import annotations

from decimal import Decimal
from typing import List

from st_lms.common.enums import Direction, Timeframe
from st_lms.models.atr import ATR
from st_lms.models.candle import Candle
from st_lms.models.supertrend_point import SupertrendPoint
from st_lms.measure.atr_calculator import calculate_atr
from st_lms.utils.helpers import generate_point_id


def calculate_supertrend_points(
    symbol: str,
    timeframe: Timeframe,
    candles: List[Candle],
    period: int = 10,
    multiplier: Decimal = Decimal("3.0"),
) -> List[SupertrendPoint]:
    """Calculate Supertrend Points from candle data."""
    atr = calculate_atr(candles, period)
    prev_direction = Direction.LONG
    prev_upper = Decimal("0")
    prev_lower = Decimal("0")

    points: List[SupertrendPoint] = []
    hl2_values = [(c.high + c.low) / Decimal("2") for c in candles]

    for i in range(period, len(candles)):
        c = candles[i]
        hl2 = hl2_values[i]
        basic_upper = hl2 + multiplier * atr.value
        basic_lower = hl2 - multiplier * atr.value

        if i == period:
            upper_band = basic_upper
            lower_band = basic_lower
        else:
            upper_band = basic_upper if basic_upper < prev_upper or candles[i - 1].close > prev_upper else prev_upper
            lower_band = basic_lower if basic_lower > prev_lower or candles[i - 1].close < prev_lower else prev_lower

        if c.close <= upper_band:
            direction = Direction.SHORT
        else:
            direction = Direction.LONG

        prev_upper = upper_band
        prev_lower = lower_band
        prev_direction = direction

        points.append(SupertrendPoint(
            point_id=generate_point_id(),
            symbol=symbol,
            timeframe=timeframe,
            timestamp=c.timestamp,
            price=c.close,
            atr=atr.value,
            direction=direction,
            candle_index=i,
        ))

    return points
