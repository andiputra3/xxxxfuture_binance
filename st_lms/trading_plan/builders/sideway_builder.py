from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction, GridState, TradingPlanState
from st_lms.config.supertrend_config import GRID_ATR_MULTIPLIER
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import PartialExit, TradingPlan
from st_lms.trading_plan.models.adaptive_grid import AdaptiveGrid
from st_lms.utils.helpers import generate_grid_id, generate_plan_id


class SidewayBuilder:
    """Builds SIDEWAY Adaptive Grid strategy with Partial Exit and Funding Awareness.

    Menghasilkan dua output:
    1. TradingPlan — generik, berisi entry zone dan risk dengan partial exits
    2. AdaptiveGrid — spesifik sideway, berisi grid parameters

    LongBuilder dan ShortBuilder tidak mengetahui model AdaptiveGrid.
    """

    def build(self, snapshot: StructuralSnapshot, leverage: Decimal = Decimal("10")) -> tuple[TradingPlan, AdaptiveGrid]:
        """Create TradingPlan + AdaptiveGrid dari StructuralSnapshot SIDEWAY.
        
        Features added:
        - Liquidation price monitoring
        - Funding cost estimate for grid holding period
        - Partial exits for grid levels
        """
        plan_id = generate_plan_id()
        grid_top = snapshot.nearest_resistance
        grid_bottom = snapshot.nearest_support
        grid_range = grid_top - grid_bottom
        spacing = grid_range / Decimal(str(max(GRID_ATR_MULTIPLIER, Decimal("1"))))
        num_levels = max(int(grid_range / spacing) if spacing > Decimal("0") else 3, 3)
        
        # Calculate liquidation price (approximate for neutral position)
        mid_price = (grid_top + grid_bottom) / Decimal("2")
        distance = mid_price / leverage * Decimal("0.9")
        liquidation_low = grid_bottom - distance  # Worst case for long positions
        liquidation_high = grid_top + distance    # Worst case for short positions
        
        # Estimate funding cost for grid strategy (typically held longer)
        # Conservative: 0.03% per day, average hold 5 days
        funding_cost_estimate = mid_price * Decimal("0.0003") * Decimal("5")
        
        # Partial exits for grid: exit at each grid level
        # Example: 3 levels → 33% at each level
        partial_exits = []
        if num_levels >= 3:
            step = grid_range / Decimal(str(num_levels))
            for i in range(1, num_levels + 1):
                partial_exits.append(PartialExit(
                    price=grid_bottom + step * Decimal(str(i)),
                    percent=Decimal("1") / Decimal(str(num_levels)),
                ))

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
            reason="Adaptive grid plan from sideways structure with partial exits",
            partial_exits=partial_exits,
            funding_cost_estimate=funding_cost_estimate,
            liquidation_price=liquidation_low,  # Use worst-case for monitoring
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
