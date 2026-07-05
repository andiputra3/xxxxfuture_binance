from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.models.market_snapshot import MarketSnapshot
from st_lms.models.open_interest import OpenInterest
from st_lms.utils.helpers import generate_snapshot_id


class Observer(ABC):
    """C001 — Abstract data collection orchestrator.

    Mengamati pasar apa adanya (Candle, Volume, Open Interest).
    Tidak ada analisis di tahap ini.
    """

    @abstractmethod
    def get_candles(self, symbol: str, timeframes: List[Timeframe], limit: int) -> Dict[Timeframe, List[Candle]]:
        ...

    @abstractmethod
    def get_open_interest(self, symbol: str) -> OpenInterest:
        ...

    def observe(self, symbol: str, timeframes: List[Timeframe], candle_limit: int = 100) -> MarketSnapshot:
        """C001 — Observe: kumpulkan data market dan bungkus dalam MarketSnapshot.

        Returns MarketSnapshot dengan candle terakhir, OI, dan volume.
        """
        candles = self.get_candles(symbol, timeframes, candle_limit)
        oi = self.get_open_interest(symbol)

        primary_tf = timeframes[0]
        tf_candles = candles.get(primary_tf, [])
        latest_candle = tf_candles[-1] if tf_candles else Candle(
            symbol=symbol, timeframe=Timeframe.H4, timestamp=0,
            open=Decimal("1"), high=Decimal("1"), low=Decimal("1"),
            close=Decimal("1"), volume=Decimal("0"),
        )
        volume = latest_candle.volume
        ts = latest_candle.timestamp

        return MarketSnapshot(
            snapshot_id=generate_snapshot_id("OBS"),
            symbol=symbol,
            timestamp=ts,
            candle=latest_candle,
            open_interest=oi,
            volume=volume,
            exchange_data={},
        )
