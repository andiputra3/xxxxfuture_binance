from __future__ import annotations

from typing import Dict, List, Optional

from st_lms.models.trading_plan import TradingPlan


class PlanRepository:
    """In-memory repository for Trading Plans."""

    def __init__(self) -> None:
        self._plans: Dict[str, TradingPlan] = {}

    def save(self, plan: TradingPlan) -> None:
        self._plans[plan.plan_id] = plan

    def get(self, plan_id: str) -> Optional[TradingPlan]:
        return self._plans.get(plan_id)

    def list_all(self) -> List[TradingPlan]:
        return list(self._plans.values())
