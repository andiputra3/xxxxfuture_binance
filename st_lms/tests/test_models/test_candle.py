"""Level 1: Unit Tests — Model validation & immutability."""
import pytest
from decimal import Decimal
from st_lms.models.candle import Candle
from st_lms.common.enums import Timeframe

def test_candle_validation():
    with pytest.raises(ValueError):
        Candle("BTCUSDT", Timeframe.H4, 0, Decimal("-1"), Decimal("1"), Decimal("0"), Decimal("0.5"), Decimal("100"))

def test_candle_immutable():
    c = Candle("BTCUSDT", Timeframe.H4, 0, Decimal("100"), Decimal("101"), Decimal("99"), Decimal("100.5"), Decimal("100"))
    with pytest.raises(AttributeError):
        c.close = Decimal("200")
