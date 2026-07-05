from __future__ import annotations

from typing import Optional, Tuple

from st_lms.common.enums import StructuralState
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import TradingPlan
from st_lms.trading_plan.builders.long_builder import LongBuilder
from st_lms.trading_plan.builders.short_builder import ShortBuilder
from st_lms.trading_plan.builders.sideway_builder import SidewayBuilder
from st_lms.trading_plan.models.adaptive_grid import AdaptiveGrid


class Planner:
    """Creates Trading Plans based on Structural State.

    LONG → LongBuilder (Trend Following, Fib 0.382)
    SHORT → ShortBuilder (Trend Following, Fib 0.618)
    SIDEWAY → SidewayBuilder (Adaptive Grid)
    """

    def __init__(self) -> None:
        self._long_builder = LongBuilder()
        self._short_builder = ShortBuilder()
        self._sideway_builder = SidewayBuilder()

    def create_plan(self, snapshot: StructuralSnapshot) -> Optional[TradingPlan]:
        """Create a Trading Plan based on the current structural state."""
        state = snapshot.state
        if state == StructuralState.UPTREND:
            return self._long_builder.build(snapshot)
        elif state == StructuralState.DOWNTREND:
            return self._short_builder.build(snapshot)
        elif state == StructuralState.SIDEWAY:
            plan, _ = self._sideway_builder.build(snapshot)
            return plan
        return None

    def create_plan_with_grid(self, snapshot: StructuralSnapshot) -> Optional[Tuple[TradingPlan, AdaptiveGrid]]:
        """Create Trading Plan + AdaptiveGrid (khusus SIDEWAY)."""
        if snapshot.state != StructuralState.SIDEWAY:
            return None
        return self._sideway_builder.build(snapshot)
