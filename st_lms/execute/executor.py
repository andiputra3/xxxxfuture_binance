from __future__ import annotations

from abc import ABC, abstractmethod

from st_lms.models.trading_plan import TradingPlan


class Executor(ABC):
    """Abstract trade executor."""

    @abstractmethod
    def execute(self, plan: TradingPlan) -> str:
        ...
