from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from st_lms.models.learning_snapshot import LearningSnapshot, TradeOutcome
from st_lms.utils.helpers import generate_snapshot_id


class RiverLearning:
    """River learning — statistical pattern accumulation."""

    def __init__(self) -> None:
        self._outcomes: List[TradeOutcome] = []

    def record_outcome(self, outcome: TradeOutcome) -> None:
        self._outcomes.append(outcome)

    def get_snapshot(self) -> LearningSnapshot:
        total = len(self._outcomes)
        if total == 0:
            return LearningSnapshot(
                snapshot_id=generate_snapshot_id("RIVER"),
                timestamp=0,
                total_trades=0,
                win_rate=0.0,
                avg_rr=0.0,
                profit_factor=0.0,
                max_drawdown=0.0,
                patterns={},
                failure_patterns=[],
                recent_outcomes=[],
            )

        wins = [o for o in self._outcomes if o.pnl_percent > Decimal("0")]
        losses = [o for o in self._outcomes if o.pnl_percent <= Decimal("0")]
        win_rate = len(wins) / total
        avg_rr = float(sum(abs(o.pnl_percent) for o in wins) / len(wins)) if wins else 0.0

        gross_profit = float(sum(o.pnl_percent for o in wins))
        gross_loss = float(abs(sum(o.pnl_percent for o in losses))) if losses else 1.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        # max drawdown sederhana
        peak = Decimal("0")
        dd = Decimal("0")
        for o in self._outcomes:
            peak = max(peak, o.pnl_percent)
            dd = max(dd, peak - o.pnl_percent)
        max_dd = float(dd / 100) if peak > 0 else 0.0

        # failure patterns
        failure_exits = [o.exit_reason for o in losses]
        failure_patterns = list(set(failure_exits))

        # patterns
        patterns: Dict[str, int] = {}
        for o in self._outcomes:
            patterns[o.exit_reason] = patterns.get(o.exit_reason, 0) + 1

        return LearningSnapshot(
            snapshot_id=generate_snapshot_id("RIVER"),
            timestamp=0,
            total_trades=total,
            win_rate=win_rate,
            avg_rr=avg_rr,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            patterns=patterns,
            failure_patterns=failure_patterns[:5],
            recent_outcomes=self._outcomes[-20:],
        )
