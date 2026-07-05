from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction, TradingPlanState
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import TradingPlan
from st_lms.utils.helpers import generate_plan_id


class ShortBuilder:
    """Builds SHORT Trading Plans from Structural State."""

    def build(self, snapshot: StructuralSnapshot) -> TradingPlan:
        """Create a SHORT plan using Fibonacci 0.618 entry zone."""
        spread = max(snapshot.nearest_resistance - snapshot.nearest_support, Decimal("0.01"))
        entry_low = snapshot.nearest_support + spread * Decimal("0.618")
        entry_high = snapshot.nearest_support + spread
        return TradingPlan(
            plan_id=generate_plan_id(),
            strategy="TREND_FOLLOWING_SHORT",
            direction=Direction.SHORT,
            entry_zone_low=entry_low,
            entry_zone_high=entry_high,
            stop_loss=snapshot.nearest_resistance * Decimal("1.01"),
            take_profit=snapshot.nearest_support,
            risk_percent=Decimal("2.0"),
            confidence=snapshot.confidence,
            state=TradingPlanState.CREATED,
            reason="Short plan from downtrend structure",
        )
