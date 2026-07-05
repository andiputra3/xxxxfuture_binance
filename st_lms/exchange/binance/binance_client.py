from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from binance.client import Client
except ImportError:
    Client = None  # type: ignore[assignment,misc]

from st_lms.common.enums import Environment
from st_lms.config.exchange_config import API_KEY, API_SECRET, ENVIRONMENT, TESTNET_API_KEY, TESTNET_API_SECRET


class BinanceClient:
    """Low-level Binance Futures client wrapper."""

    def __init__(self) -> None:
        self._client: Optional[Client] = None
        if Client is not None:
            if ENVIRONMENT == Environment.LIVE:
                self._client = Client(API_KEY, API_SECRET)
            elif ENVIRONMENT == Environment.TESTNET:
                self._client = Client(TESTNET_API_KEY, TESTNET_API_SECRET)

    def get_klines(self, symbol: str, interval: str, limit: int) -> List[List[Any]]:
        if self._client is None or ENVIRONMENT == Environment.SIMULATION:
            return []
        return self._client.futures_klines(symbol=symbol, interval=interval, limit=limit)

    def get_open_interest(self, symbol: str) -> Optional[Dict[str, Any]]:
        if self._client is None or ENVIRONMENT == Environment.SIMULATION:
            return None
        return self._client.futures_open_interest(symbol=symbol)  # type: ignore[no-any-return]

    def place_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict[str, Any]]:
        if self._client is None or ENVIRONMENT == Environment.SIMULATION:
            return None
        return self._client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )

    def cancel_order(self, symbol: str, order_id: str) -> Optional[Dict[str, Any]]:
        if self._client is None or ENVIRONMENT == Environment.SIMULATION:
            return None
        return self._client.futures_cancel_order(symbol=symbol, orderId=order_id)

    def get_account_info(self) -> Dict[str, Any]:
        if self._client is None or ENVIRONMENT == Environment.SIMULATION:
            return {}
        return self._client.futures_account()  # type: ignore[no-any-return]
