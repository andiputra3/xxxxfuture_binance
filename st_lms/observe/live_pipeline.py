"""
LivePipeline — Pipeline untuk data real-time (Live / Testnet).

Ini adalah wrapper di atas Pipeline biasa yang menggunakan BinanceObserver.
"""

from decimal import Decimal
from typing import List

from st_lms.common.enums import Timeframe
from st_lms.exchange.binance.binance_service import BinanceService
from st_lms.observe.binance_observer import BinanceObserver
from st_lms.pipeline import Pipeline, PipelineResult


class LivePipeline:
    """Pipeline yang menggunakan data real dari Binance (REST)."""

    def __init__(self, api_key: str = "", api_secret: str = "", initial_balance: Decimal = Decimal("10000")):
        service = BinanceService(api_key=api_key, api_secret=api_secret, testnet=True)
        observer = BinanceObserver(service)
        self._pipeline = Pipeline(observer, initial_balance=initial_balance)

    def run(self, symbol: str, timeframes: List[Timeframe], candle_limit: int = 100,
            risk_method: str = "fixed_fraction") -> PipelineResult:
        """Jalankan satu siklus pipeline dengan data live."""
        # Ambil data real dari Binance
        return self._pipeline.run(symbol, timeframes, {}, risk_method=risk_method)
