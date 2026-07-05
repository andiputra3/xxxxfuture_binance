from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from st_lms.common.enums import OpenInterestState, Timeframe
from st_lms.models.candle import Candle
from st_lms.models.open_interest import OpenInterest
from st_lms.observe.observer import Observer


class SimulationObserver(Observer):
    """Data collection from simulation data source.

    Mengembalikan data default untuk simulasi.
    """

    def get_candles(self, symbol: str, timeframes: List[Timeframe], limit: int) -> Dict[Timeframe, List[Candle]]:
        return {}

    def get_open_interest(self, symbol: str) -> OpenInterest:
        return OpenInterest(
            symbol=symbol,
            timestamp=0,
            value=Decimal("1000"),
            state=OpenInterestState.FLAT,
        )
