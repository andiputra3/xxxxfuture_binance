from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from st_lms.common.enums import Timeframe
from st_lms.config.supertrend_config import ATR_PERIOD
from st_lms.measure.atr_calculator import calculate_atr
from st_lms.measure.macd_calculator import calculate_macd
from st_lms.measure.price_momentum_calculator import calculate_price_momentum
from st_lms.measure.volatility_calculator import calculate_volatility
from st_lms.common.enums import MACDBucket
from st_lms.models.atr import ATR
from st_lms.models.candle import Candle
from st_lms.models.indicator_snapshot import IndicatorSnapshot
from st_lms.models.macd import MACD
from st_lms.models.market_snapshot import MarketSnapshot
from st_lms.utils.helpers import generate_snapshot_id


class MeasureOrchestrator:
    """C002 — Measure layer orchestrator.

    Mengubah observasi menjadi data terukur (ATR, MACD, Volatility, dll).
    Tidak membentuk struktur — hanya mengukur.
    """

    def measure(self, market: MarketSnapshot, candles: Dict[Timeframe, List[Candle]]) -> IndicatorSnapshot:
        """Run all calculators and package results into IndicatorSnapshot."""
        ts = market.timestamp

        primary_tf = next(iter(candles.keys())) if candles else Timeframe.H4
        primary_candles = candles.get(primary_tf, [])

        atr = calculate_atr(primary_candles, ATR_PERIOD) if len(primary_candles) >= ATR_PERIOD + 1 else None
        macd = calculate_macd(primary_candles) if len(primary_candles) >= 33 else None
        vol = calculate_volatility(primary_candles)
        momentum = calculate_price_momentum(primary_candles)

        return IndicatorSnapshot(
            snapshot_id=generate_snapshot_id("IND"),
            timestamp=ts,
            atr=atr or ATR(timestamp=ts, period=ATR_PERIOD, value=Decimal("0")),
            macd=macd or MACD(timestamp=ts, macd=Decimal("0"), signal=Decimal("0"), histogram=Decimal("0"), bucket=MACDBucket.NEUTRAL),
            volatility=vol,
            oi_delta=0.0,
            price_momentum=momentum,
        )
