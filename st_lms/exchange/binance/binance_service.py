from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from st_lms.common.enums import OpenInterestState, Timeframe
from st_lms.exchange.binance.binance_client import BinanceClient
from st_lms.exchange.exchange_service import ExchangeService
from st_lms.models.candle import Candle
from st_lms.models.open_interest import OpenInterest
from st_lms.models.position import Position


_INTERVAL_MAP = {
    Timeframe.M1: "1m",
    Timeframe.M5: "5m",
    Timeframe.M15: "15m",
    Timeframe.H1: "1h",
    Timeframe.H4: "4h",
}


class BinanceService(ExchangeService):
    """Concrete Binance Futures exchange service."""

    def __init__(self) -> None:
        self._client = BinanceClient()

    def get_candles(self, symbol: str, timeframe: Timeframe, limit: int) -> List[Candle]:
        interval = _INTERVAL_MAP[timeframe]
        klines = self._client.get_klines(symbol, interval, limit)
        return [
            Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=int(k[0]),
                open=Decimal(str(k[1])),
                high=Decimal(str(k[2])),
                low=Decimal(str(k[3])),
                close=Decimal(str(k[4])),
                volume=Decimal(str(k[5])),
            )
            for k in klines
        ]

    def get_open_interest(self, symbol: str) -> Optional[OpenInterest]:
        data = self._client.get_open_interest(symbol)
        if data is None:
            return None
        return OpenInterest(
            symbol=symbol,
            timestamp=int(data["timestamp"]),
            value=Decimal(str(data["openInterest"])),
            state=OpenInterestState.FLAT,
        )

    def get_positions(self, symbol: str) -> List[Position]:
        return []

    def place_order(self, symbol: str, side: str, quantity: Decimal) -> Optional[str]:
        result = self._client.place_order(symbol, side, float(quantity))
        return str(result["orderId"]) if result else None

    def close_position(self, symbol: str) -> bool:
        return False

    def cancel_order(self, order_id: str) -> bool:
        result = self._client.cancel_order("", order_id)
        return result is not None

    def get_account(self) -> dict:
        return self._client.get_account_info()
