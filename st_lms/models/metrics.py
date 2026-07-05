from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from st_lms.models.learning_snapshot import TradeOutcome


@dataclass(slots=True, frozen=True)
class TradingMetrics:
    """Comprehensive trading metrics from a set of trade outcomes.

    win_rate:         0.0 - 1.0
    sharpe_ratio:     annualized, based on daily returns
    max_drawdown:     0.0 - 1.0
    profit_factor:    gross profit / gross loss
    avg_rr:           average risk-reward ratio
    total_trades:     total number of trades
    avg_win:          average win percentage
    avg_loss:         average loss percentage
    expectancy:       expected value per trade (%)
    """
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    avg_rr: float
    total_trades: int
    avg_win: Decimal
    avg_loss: Decimal
    expectancy: Decimal
    equity_curve: List[Decimal]

    def __post_init__(self) -> None:
        if self.win_rate < 0.0 or self.win_rate > 1.0:
            raise ValueError("win_rate must be between 0 and 1")
        if self.max_drawdown < 0.0 or self.max_drawdown > 1.0:
            raise ValueError("max_drawdown must be between 0 and 1")
        if self.total_trades < 0:
            raise ValueError("total_trades must be >= 0")


def calculate_metrics(outcomes: List[TradeOutcome]) -> TradingMetrics:
    """Calculate comprehensive metrics from a list of trade outcomes."""
    total = len(outcomes)
    if total == 0:
        return TradingMetrics(
            win_rate=0.0, sharpe_ratio=0.0, max_drawdown=0.0,
            profit_factor=0.0, avg_rr=0.0, total_trades=0,
            avg_win=Decimal("0"), avg_loss=Decimal("0"),
            expectancy=Decimal("0"), equity_curve=[],
        )

    wins = [o for o in outcomes if o.pnl_percent > Decimal("0")]
    losses = [o for o in outcomes if o.pnl_percent <= Decimal("0")]
    win_rate = len(wins) / total

    avg_win = sum(o.pnl_percent for o in wins) / len(wins) if wins else Decimal("0")
    avg_loss = sum(o.pnl_percent for o in losses) / len(losses) if losses else Decimal("0")
    expectancy = (avg_win * Decimal(str(win_rate)) + avg_loss * (Decimal("1") - Decimal(str(win_rate))))

    gross_profit = float(sum(o.pnl_percent for o in wins))
    gross_loss = float(abs(sum(o.pnl_percent for o in losses))) if losses else 1.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

    avg_rr = float(abs(avg_win / avg_loss)) if avg_loss != Decimal("0") else 0.0

    # Equity curve dari cumulative pnl
    equity = [Decimal("100")]  # mulai dari 100 (basis)
    for o in sorted(outcomes, key=lambda x: x.duration_hours):
        equity.append(equity[-1] + o.pnl_percent / Decimal("100") * equity[-1])
    equity = equity[1:]

    # Max drawdown
    peak = equity[0]
    max_dd = Decimal("0")
    for e in equity:
        if e > peak:
            peak = e
        dd = (peak - e) / peak
        if dd > max_dd:
            max_dd = dd
    max_drawdown = float(max_dd)

    # Sharpe ratio (annualized, assuming 4h candles ≈ 1 trade per 4h)
    if len(equity) > 1:
        returns = [float((equity[i] - equity[i - 1]) / equity[i - 1]) for i in range(1, len(equity))]
        mean_ret = sum(returns) / len(returns)
        var_ret = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
        std_ret = var_ret ** 0.5
        sharpe_ratio = (mean_ret / std_ret * (365 * 6) ** 0.5) if std_ret > 0 else 0.0
    else:
        sharpe_ratio = 0.0

    return TradingMetrics(
        win_rate=win_rate,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        profit_factor=profit_factor,
        avg_rr=avg_rr,
        total_trades=total,
        avg_win=avg_win,
        avg_loss=avg_loss,
        expectancy=expectancy,
        equity_curve=equity,
    )
