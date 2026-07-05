from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.measure.atr_calculator import calculate_atr
from st_lms.measure.macd_calculator import calculate_macd
from st_lms.measure.supertrend_calculator import calculate_supertrend_points
from st_lms.measure.volatility_calculator import calculate_volatility
from st_lms.measure.price_momentum_calculator import calculate_price_momentum


def _make_candles(count: int) -> list[Candle]:
    return [
        Candle("BTCUSDT", Timeframe.H1, i * 60_000, Decimal("100"), Decimal("105"), Decimal("95"), Decimal("101"), Decimal("100"))
        for i in range(count)
    ]


def test_calculate_atr() -> None:
    candles = _make_candles(20)
    atr = calculate_atr(candles, 10)
    assert atr.period == 10
    assert atr.value > Decimal("0")


def test_calculate_atr_insufficient_data() -> None:
    candles = _make_candles(5)
    try:
        calculate_atr(candles, 10)
        assert False
    except ValueError:
        pass


def test_calculate_macd() -> None:
    candles = _make_candles(40)
    macd = calculate_macd(candles)
    assert macd.timestamp > 0


def test_calculate_supertrend_points() -> None:
    candles = _make_candles(30)
    points = calculate_supertrend_points("BTCUSDT", Timeframe.H1, candles)
    assert len(points) > 0


def test_calculate_volatility() -> None:
    candles = _make_candles(20)
    vol = calculate_volatility(candles, 10)
    assert vol >= 0.0


def test_calculate_price_momentum() -> None:
    candles = _make_candles(30)
    mom = calculate_price_momentum(candles, 10)
    assert isinstance(mom, float)
