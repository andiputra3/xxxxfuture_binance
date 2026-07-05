from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List

from st_lms.models.authorization import Authorization
from st_lms.models.learning_snapshot import TradeOutcome
from st_lms.models.metrics import TradingMetrics


@dataclass(slots=True, frozen=True)
class BacktestTrade:
    """Single trade dalam backtest."""
    timestamp: int
    plan_id: str
    symbol: str
    direction: str
    entry_price: Decimal
    exit_price: Decimal
    quantity: Decimal
    pnl: Decimal
    pnl_percent: Decimal
    exit_reason: str
    authorization: str


@dataclass(slots=True, frozen=True)
class BacktestResult:
    """Hasil backtest lengkap."""
    symbol: str
    total_candles: int
    total_trades: int
    initial_balance: Decimal
    final_balance: Decimal
    metrics: TradingMetrics
    trades: List[BacktestTrade]
    equity_curve: List[Decimal]
    rejected_count: int
    errors: List[str] = field(default_factory=list)
