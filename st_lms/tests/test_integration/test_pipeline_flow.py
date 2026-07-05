"""Level 4 + 5: Integration & E2E Tests — Data Flow & Replay."""
from st_lms.pipeline import Pipeline
from st_lms.observe.simulation_observer import SimulationObserver
from decimal import Decimal
from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle

def test_pipeline_data_flow():
    obs = SimulationObserver()
    p = Pipeline(obs)
    candles = [Candle("BTCUSDT", Timeframe.H4, i*14400000, Decimal("100"), Decimal("101"), Decimal("99"), Decimal("100.5"), Decimal("100")) for i in range(50)]
    result = p.run("BTCUSDT", [Timeframe.H4], {Timeframe.H4: candles})
    assert result is not None
