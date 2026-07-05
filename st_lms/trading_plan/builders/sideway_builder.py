from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction, GridState, TradingPlanState
from st_lms.config.supertrend_config import GRID_ATR_MULTIPLIER
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import TradingPlan
from st_lms.trading_plan.models.adaptive_grid import AdaptiveGrid
from st_lms.utils.helpers import generate_grid_id, generate_plan_id


class SidewayBuilder:
    """Builds SIDEWAY Adaptive Grid strategy.

    Menghasilkan dua output:
    1. TradingPlan — generik, berisi entry zone dan risk
    2. AdaptiveGrid — spesifik sideway, berisi grid parameters

    LongBuilder dan ShortBuilder tidak mengetahui model AdaptiveGrid.
    """

    def build(self, snapshot: StructuralSnapshot) -> tuple[TradingPlan, AdaptiveGrid]:
        """Create TradingPlan + AdaptiveGrid dari StructuralSnapshot SIDEWAY."""
        plan_id = generate_plan_id()
        grid_top = snapshot.nearest_resistance
        grid_bottom = snapshot.nearest_support
        grid_range = grid_top - grid_bottom
        spacing = grid_range / Decimal(str(max(GRID_ATR_MULTIPLIER, Decimal("1"))))
        num_levels = max(int(grid_range / spacing) if spacing > Decimal("0") else 3, 3)

        plan = TradingPlan(
            plan_id=plan_id,
            strategy="ADAPTIVE_GRID_SIDEWAY",
            direction=Direction.NEUTRAL,
            entry_zone_low=grid_bottom,
            entry_zone_high=grid_top,
            stop_loss=grid_bottom * Decimal("0.98"),
            take_profit=grid_top * Decimal("1.02"),
            risk_percent=Decimal("1.0"),
            confidence=snapshot.confidence,
            state=TradingPlanState.CREATED,
            reason="Adaptive grid plan from sideways structure",
        )

        grid = AdaptiveGrid(
            grid_id=generate_grid_id(),
            plan_id=plan_id,
            entry_zone_low=grid_bottom,
            entry_zone_high=grid_top,
            grid_spacing=spacing,
            grid_levels=num_levels,
            scale_in_size=Decimal("1.0") / Decimal(str(num_levels)),
            grid_take_profit=grid_top * Decimal("1.02"),
            risk_limit=Decimal("0.05"),
            state=GridState.WAITING,
        )

        return plan, grid
