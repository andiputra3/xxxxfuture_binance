from __future__ import annotations

from st_lms.execute.executor import Executor
from st_lms.models.trading_plan import TradingPlan


class LiveExecutor(Executor):
    """Live trade execution."""

    def execute(self, plan: TradingPlan) -> str:
        raise NotImplementedError("Live execution not implemented")
