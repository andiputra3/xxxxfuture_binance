from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from st_lms.common.enums import Direction, TradingPlanState


@dataclass(slots=True, frozen=True)
class PartialExit:
    """Partial exit level for scaled exit strategy."""
    price: Decimal
    percent: Decimal  # e.g., Decimal("0.5") = 50% of position


@dataclass(slots=True, frozen=True)
class TradingPlan:
    """Adaptive Trading Plan - core object of the system."""

    plan_id: str
    strategy: str
    direction: Direction
    entry_zone_low: Decimal
    entry_zone_high: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    risk_percent: Decimal
    confidence: Decimal
    state: TradingPlanState
    reason: str
    revision: int = 0
    partial_exits: List[PartialExit] = field(default_factory=list)
    funding_cost_estimate: Decimal = Decimal("0")  # estimated funding cost for 3-day hold
    liquidation_price: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.entry_zone_low <= Decimal("0"):
            raise ValueError("entry_zone_low must be greater than zero")
        if self.entry_zone_high <= self.entry_zone_low:
            raise ValueError("entry_zone_high must be greater than entry_zone_low")
        if self.stop_loss <= Decimal("0"):
            raise ValueError("stop_loss must be greater than zero")
        if self.take_profit <= Decimal("0"):
            raise ValueError("take_profit must be greater than zero")
        if self.risk_percent < Decimal("0") or self.risk_percent > Decimal("100"):
            raise ValueError("risk_percent must be between 0 and 100")
        if self.confidence < Decimal("0") or self.confidence > Decimal("100"):
            raise ValueError("confidence must be between 0 and 100")
        if self.revision < 0:
            raise ValueError("revision must be >= 0")
        for pe in self.partial_exits:
            if pe.percent <= Decimal("0") or pe.percent > Decimal("1"):
                raise ValueError("partial_exit percent must be between 0 and 1")
