from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.models.market_snapshot import MarketSnapshot
from st_lms.models.open_interest import OpenInterest
from st_lms.observe.observer import Observer
from st_lms.utils.helpers import generate_snapshot_id


class WebSocketObserver(Observer):
    """C001 — WebSocket observer untuk sub-H1 timeframes real-time.

    Mengamati pasar via WebSocket (simulated).
    Sub-H1 timeframes: 1m, 5m, 15m — untuk deteksi struktur lebih granular.
    """

    def __init__(self) -> None:
        self._candle_buffer: Dict[str, List[Candle]] = {}  # symbol:tf -> candles
        self._running = False

    def start(self) -> None:
        """Start WebSocket connection (simulated)."""
        self._running = True

    def stop(self) -> None:
        """Stop WebSocket connection."""
        self._running = False

    def feed_candle(self, candle: Candle) -> None:
        """Feed a new candle (simulated WebSocket message)."""
        key = f"{candle.symbol}:{candle.timeframe.value}"
        if key not in self._candle_buffer:
            self._candle_buffer[key] = []
        self._candle_buffer[key].append(candle)

    def get_candles(self, symbol: str, timeframes: List[Timeframe], limit: int = 100) -> Dict[Timeframe, List[Candle]]:
        """Get candles from buffer (sub-H1 real-time)."""
        result: Dict[Timeframe, List[Candle]] = {}
        for tf in timeframes:
            key = f"{symbol}:{tf.value}"
            buf = self._candle_buffer.get(key, [])
            result[tf] = buf[-limit:] if buf else []
        return result

    def get_open_interest(self, symbol: str) -> OpenInterest:
        """WebSocket OI — default flat untuk simulasi."""
        from st_lms.common.enums import OpenInterestState
        return OpenInterest(symbol=symbol, timestamp=0, value=Decimal("0"), state=OpenInterestState.FLAT)

    def observe(self, symbol: str, timeframes: List[Timeframe], candle_limit: int = 100) -> MarketSnapshot:
        """Observe: ambil candle terbaru dari buffer WebSocket."""
        candles = self.get_candles(symbol, timeframes, candle_limit)

        # Ambil primary TF (first in list)
        primary_tf = timeframes[0] if timeframes else Timeframe.M1
        tf_candles = candles.get(primary_tf, [])

        if tf_candles:
            latest = tf_candles[-1]
            return MarketSnapshot(
                snapshot_id=generate_snapshot_id("WS"),
                symbol=symbol,
                timestamp=latest.timestamp,
                candle=latest,
                open_interest=self.get_open_interest(symbol),
                volume=latest.volume,
                exchange_data={},
            )

        # Fallback
        return MarketSnapshot(
            snapshot_id=generate_snapshot_id("WS"),
            symbol=symbol,
            timestamp=0,
            candle=Candle(symbol, Timeframe.M1, 0, Decimal("1"), Decimal("1"), Decimal("1"), Decimal("1"), Decimal("0")),
            open_interest=self.get_open_interest(symbol),
            volume=Decimal("0"),
            exchange_data={},
        )
