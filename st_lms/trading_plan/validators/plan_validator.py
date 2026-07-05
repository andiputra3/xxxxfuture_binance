from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction
from st_lms.models.trading_plan import TradingPlan


class PlanValidator:
    """Validates Trading Plan integrity and risk compliance."""

    def validate(self, plan: TradingPlan) -> bool:
        """Check if a Trading Plan passes all validation rules."""
        if plan.entry_zone_low >= plan.entry_zone_high:
            return False

        if plan.direction == Direction.LONG:
            if plan.stop_loss >= plan.entry_zone_low:
                return False
            if plan.take_profit <= plan.entry_zone_high:
                return False
        elif plan.direction == Direction.SHORT:
            if plan.stop_loss <= plan.entry_zone_high:
                return False
            if plan.take_profit >= plan.entry_zone_low:
                return False

        if plan.risk_percent < Decimal("0") or plan.risk_percent > Decimal("100"):
            return False
        return True
