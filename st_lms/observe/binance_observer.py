from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from st_lms.common.enums import Timeframe
from st_lms.exchange.binance.binance_service import BinanceService
from st_lms.models.candle import Candle
from st_lms.models.market_snapshot import MarketSnapshot
from st_lms.models.open_interest import OpenInterest
from st_lms.observe.observer import Observer
from st_lms.utils.helpers import generate_snapshot_id


class BinanceObserver(Observer):
    """C001 — Real data collection from Binance Futures (REST + WebSocket ready)."""

    def __init__(self, service: BinanceService) -> None:
        self._service = service

    def get_candles(self, symbol: str, timeframes: List[Timeframe], limit: int) -> Dict[Timeframe, List[Candle]]:
        result: Dict[Timeframe, List[Candle]] = {}
        for tf in timeframes:
            candles = self._service.get_candles(symbol, tf, limit)
            result[tf] = candles
        return result

    def get_open_interest(self, symbol: str) -> OpenInterest:
        oi = self._service.get_open_interest(symbol)
        if oi is None:
            raise ValueError(f"Open Interest not available for {symbol}")
        return oi

    def observe(self, symbol: str, timeframes: List[Timeframe], candle_limit: int = 100) -> MarketSnapshot:
        """Override observe untuk mengambil data real dari Binance."""
        candles = self.get_candles(symbol, timeframes, candle_limit)
        oi = self.get_open_interest(symbol)

        primary_tf = timeframes[0]
        tf_candles = candles.get(primary_tf, [])
        latest_candle = tf_candles[-1] if tf_candles else Candle(
            symbol=symbol,
            timeframe=primary_tf,
            timestamp=0,
            open=Decimal("0"),
            high=Decimal("0"),
            low=Decimal("0"),
            close=Decimal("0"),
            volume=Decimal("0"),
        )

        return MarketSnapshot(
            snapshot_id=generate_snapshot_id("OBS"),
            symbol=symbol,
            timestamp=latest_candle.timestamp,
            candle=latest_candle,
            open_interest=oi,
            volume=latest_candle.volume,
            exchange_data={},
        )
