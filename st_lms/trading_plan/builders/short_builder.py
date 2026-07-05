from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction, TradingPlanState
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import PartialExit, TradingPlan
from st_lms.utils.helpers import generate_plan_id


class ShortBuilder:
    """Builds SHORT Trading Plans from Structural State with Partial Exit Strategy."""

    def build(self, snapshot: StructuralSnapshot, leverage: Decimal = Decimal("10")) -> TradingPlan:
        """Create a SHORT plan using Fibonacci 0.618 entry zone with scaled exit strategy.
        
        Partial Exit Strategy:
        - TP1 (50%): Fib 0.382 level (from bottom)
        - TP2 (25%): Nearest support
        - Runner (25%): Trailing stop based on Supertrend Line
        """
        spread = max(snapshot.nearest_resistance - snapshot.nearest_support, Decimal("0.01"))
        entry_low = snapshot.nearest_support + spread * Decimal("0.618")
        entry_high = snapshot.nearest_support + spread
        stop_loss = snapshot.nearest_resistance * Decimal("1.01")
        
        # Calculate liquidation price for risk monitoring
        distance = entry_low / leverage * Decimal("0.9")
        liquidation_price = entry_low + distance
        
        # Partial Exit Strategy - scaled exit for better profit realization
        partial_exits = [
            # First exit: 50% at Fib 0.382 (from support towards resistance)
            PartialExit(
                price=snapshot.nearest_support + spread * Decimal("0.382"),
                percent=Decimal("0.5"),
            ),
            # Second exit: 25% at nearest support
            PartialExit(
                price=snapshot.nearest_support,
                percent=Decimal("0.25"),
            ),
            # Runner: 25% will use trailing stop (handled by executor)
        ]
        
        # Estimate funding cost for 3-day hold (typical Binance Futures: 0.01-0.1% per 8h)
        # Conservative estimate: 0.03% per day
        funding_cost_estimate = entry_low * Decimal("0.0003") * Decimal("3")
        
        return TradingPlan(
            plan_id=generate_plan_id(),
            strategy="TREND_FOLLOWING_SHORT",
            direction=Direction.SHORT,
            entry_zone_low=entry_low,
            entry_zone_high=entry_high,
            stop_loss=stop_loss,
            take_profit=snapshot.nearest_support,
            risk_percent=Decimal("2.0"),
            confidence=snapshot.confidence,
            state=TradingPlanState.CREATED,
            reason="Short plan from downtrend structure with partial exits",
            partial_exits=partial_exits,
            funding_cost_estimate=funding_cost_estimate,
            liquidation_price=liquidation_price,
        )
