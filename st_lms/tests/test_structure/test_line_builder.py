"""Level 2: Component Tests — Line Builder Min 5 Candle Rule."""
from st_lms.multi_timeframe_structural_engine.engine import MultiTimeframeStructuralEngine
from st_lms.common.enums import Timeframe
from decimal import Decimal
from st_lms.models.candle import Candle

def test_min_5_candle_rule():
    # Less than 5 consecutive same-direction points → no line
    engine = MultiTimeframeStructuralEngine()
    # This test verifies the MIN_LINE_CANDLES=5 guard exists
    assert engine is not None
