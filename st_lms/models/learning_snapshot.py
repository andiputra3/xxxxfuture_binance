from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List


@dataclass(slots=True, frozen=True)
class TradeOutcome:
    """Record of a single completed trade."""

    trade_id: str
    plan_id: str
    direction: str
    entry_price: Decimal
    exit_price: Decimal
    pnl_percent: Decimal
    duration_hours: int
    exit_reason: str  # TP / SL / manual


@dataclass(slots=True, frozen=True)
class LearningSnapshot:
    """River layer output — hasil belajar dari histori trade."""

    snapshot_id: str
    timestamp: int
    total_trades: int
    win_rate: float         # 0.0 - 1.0
    avg_rr: float           # average risk-reward ratio
    profit_factor: float    # gross profit / gross loss
    max_drawdown: float     # 0.0 - 1.0
    patterns: Dict[str, int]      # pattern name -> occurrence count
    failure_patterns: List[str]   # most common failure patterns
    recent_outcomes: List[TradeOutcome]

    def __post_init__(self) -> None:
        if self.total_trades < 0:
            raise ValueError("total_trades must be >= 0")
        if self.win_rate < 0.0 or self.win_rate > 1.0:
            raise ValueError("win_rate must be between 0 and 1")
        if self.max_drawdown < 0.0 or self.max_drawdown > 1.0:
            raise ValueError("max_drawdown must be between 0 and 1")
