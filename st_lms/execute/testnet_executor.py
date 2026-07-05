from __future__ import annotations

from st_lms.execute.executor import Executor
from st_lms.models.trading_plan import TradingPlan


class TestnetExecutor(Executor):
    """Testnet execution via Binance testnet."""

    def execute(self, plan: TradingPlan) -> str:
        raise NotImplementedError("Testnet execution not implemented")
