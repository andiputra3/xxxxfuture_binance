from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from st_lms.models.learning_snapshot import TradeOutcome
from st_lms.models.trading_plan import TradingPlan
from st_lms.models.metrics import TradingMetrics, calculate_metrics


class RiskManager:
    """Risk Manager — position sizing dengan Kelly / Fixed Fraction.

    Menghitung ukuran posisi berdasarkan:
    - Kelly Criterion (optimal f)
    - Fixed Fraction (fixed % per trade)
    - Account balance constraints
    """

    def __init__(self, account_balance: Decimal = Decimal("10000")) -> None:
        self._balance = account_balance

    @property
    def balance(self) -> Decimal:
        return self._balance

    def set_balance(self, balance: Decimal) -> None:
        self._balance = balance

    def kelly_percent(self, outcomes: List[TradeOutcome]) -> Decimal:
        """Kelly Criterion: f* = (p * b - q) / b

        p = win_rate, q = 1-p, b = avg_win/avg_loss (odds)
        Returns fraction of bankroll to risk (0.0 - 1.0).
        """
        metrics = calculate_metrics(outcomes)
        if metrics.total_trades < 5 or metrics.avg_loss >= Decimal("0"):
            return Decimal("0")

        p = Decimal(str(metrics.win_rate))
        q = Decimal("1") - p
        b = abs(metrics.avg_win / metrics.avg_loss) if metrics.avg_loss != Decimal("0") else Decimal("1")

        # Kelly: f = (p * b - q) / b
        f = (p * b - q) / b if b > Decimal("0") else Decimal("0")
        # Fractional Kelly (25%) untuk konservatif
        f = max(Decimal("0"), min(f * Decimal("0.25"), Decimal("0.25")))
        return f

    def fixed_fraction_size(self, risk_percent: Decimal) -> Decimal:
        """Fixed Fraction sizing: position_size = balance * risk_percent / 100"""
        return self._balance * risk_percent / Decimal("100")

    def kelly_size(self, outcomes: List[TradeOutcome], plan: Optional[TradingPlan] = None) -> Decimal:
        """Kelly-based position size: balance * kelly_fraction"""
        kelly = self.kelly_percent(outcomes)
        if plan is not None:
            kelly = min(kelly, plan.risk_percent / Decimal("100"))
        return self._balance * kelly / Decimal("100")

    def compute_position(self, plan: TradingPlan, outcomes: Optional[List[TradeOutcome]] = None,
                          method: str = "fixed_fraction") -> Decimal:
        """Compute position size untuk TradingPlan.

        Args:
            plan: TradingPlan dengan risk_percent
            outcomes: Trade history untuk Kelly (optional)
            method: "fixed_fraction" atau "kelly"

        Returns:
            Position size in quote currency
        """
        if method == "kelly" and outcomes and len(outcomes) >= 5:
            return self.kelly_size(outcomes, plan)
        return self.fixed_fraction_size(plan.risk_percent)

    def compute_actual_quantity(self, plan: TradingPlan, balance: Decimal, leverage: Decimal = Decimal("1")) -> Decimal:
        """Compute actual contract quantity using formula: Quantity = (Balance × Risk%) / |Entry - SL|

        Args:
            plan: TradingPlan with entry_zone_low and stop_loss
            balance: Current account balance
            leverage: Account leverage (default 1x)

        Returns:
            Actual contract quantity (lot size) to trade
        """
        risk_amount = balance * plan.risk_percent / Decimal("100")
        price_distance = abs(plan.entry_zone_low - plan.stop_loss)
        if price_distance <= Decimal("0"):
            return Decimal("0")
        quantity = risk_amount / price_distance
        # Apply leverage (quantity increases with leverage)
        quantity = quantity * leverage
        return max(quantity, Decimal("0"))

    # ── Progressive Drawdown Control ──
    _consecutive_losses: int = 0

    def record_loss(self) -> None:
        """Record a consecutive loss for drawdown control."""
        self._consecutive_losses += 1

    def record_win(self) -> None:
        """Reset consecutive loss counter on a win."""
        self._consecutive_losses = 0

    def get_risk_multiplier(self) -> Decimal:
        """Return risk size multiplier based on consecutive losses.

        Loss #1-2 → 100% (normal)
        Loss #3 → 50%
        Loss #4 → 25%
        Loss #5+ → 0% (PAUSE)
        """
        if self._consecutive_losses >= 5:
            return Decimal("0")
        elif self._consecutive_losses >= 4:
            return Decimal("0.25")
        elif self._consecutive_losses >= 3:
            return Decimal("0.5")
        return Decimal("1")

    def should_pause(self) -> bool:
        """Return True if trading should pause (5+ consecutive losses)."""
        return self._consecutive_losses >= 5
