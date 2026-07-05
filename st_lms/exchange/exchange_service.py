from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.models.open_interest import OpenInterest
from st_lms.models.position import Position


class ExchangeService(ABC):
    """Abstract interface for exchange operations."""

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: Timeframe, limit: int) -> List[Candle]:
        ...

    @abstractmethod
    def get_open_interest(self, symbol: str) -> Optional[OpenInterest]:
        ...

    @abstractmethod
    def get_positions(self, symbol: str) -> List[Position]:
        ...

    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: Decimal) -> Optional[str]:
        ...

    @abstractmethod
    def close_position(self, symbol: str) -> bool:
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        ...

    @abstractmethod
    def get_account(self) -> dict:
        ...
