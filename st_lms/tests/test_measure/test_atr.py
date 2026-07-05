"""Level 1: Formula Authority Tests — ATR, Supertrend, MACD accuracy."""
from decimal import Decimal
from st_lms.measure.atr_calculator import calculate_atr
from st_lms.models.candle import Candle
from st_lms.common.enums import Timeframe

def test_atr_basic():
    candles = [Candle("BTCUSDT", Timeframe.H4, i*14400000, Decimal("100"), Decimal("101"), Decimal("99"), Decimal("100.5"), Decimal("100")) for i in range(20)]
    atr = calculate_atr(candles, 14)
    assert atr is not None
    assert atr.value > Decimal("0")
