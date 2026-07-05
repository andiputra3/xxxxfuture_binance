from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from st_lms.common.enums import StructuralState
from st_lms.models.darwin_recommendation import DarwinRecommendation
from st_lms.models.learning_snapshot import LearningSnapshot
from st_lms.river.shared_learning_repository import SharedLearningRepository
from st_lms.utils.helpers import generate_snapshot_id


@dataclass
class StrategyRotationSignal:
    """Darwin recommendation to rotate strategy allocation."""
    from_strategy: str
    to_strategy: str
    reason: str
    confidence: Decimal


@dataclass
class OptimizedParameters:
    """Darwin internal — parameter optimal hasil optimasi.

    Trend parameters (LONG/SHORT):
    - atr_multiplier: SuperTrend multiplier
    - tp_multiplier: Take profit distance (dalam ATR)
    - sl_multiplier: Stop loss distance (dalam ATR)
    - confidence_threshold: Minimal confidence untuk trading

    Grid parameters (SIDEWAY):
    - grid_atr_multiplier: Jarak grid dalam ATR (0.7 = 0.7 * ATR)
    - grid_levels: Jumlah level grid
    """
    atr_multiplier: Decimal
    tp_multiplier: Decimal
    sl_multiplier: Decimal
    confidence_threshold: Decimal

    # Grid-specific (hanya digunakan saat StructuralState == SIDEWAY)
    grid_atr_multiplier: Decimal = Decimal("0.7")
    grid_levels: int = 5


class DarwinEngine:
    """Darwin layer — optimasi parameter strategi dari Shared Learning Repository.

    Darwin hanya mengoptimalkan parameter.
    Darwin tidak pernah trade.
    Darwin tidak mengubah core formula (ATR period, Fibonacci level, dll).
    """

    def __init__(self) -> None:
        self._params = OptimizedParameters(
            atr_multiplier=Decimal("3.0"),
            tp_multiplier=Decimal("3.0"),
            sl_multiplier=Decimal("1.5"),
            confidence_threshold=Decimal("60"),
        )

    def get_parameters(self) -> OptimizedParameters:
        return self._params

    def optimize(self, shared_repo: SharedLearningRepository, learning: LearningSnapshot, state: StructuralState = StructuralState.SIDEWAY) -> DarwinRecommendation:
        """Optimasi parameter dari Shared Learning Repository + River learning.

        Args:
            shared_repo: SharedLearningRepository — Constitution: Darwin analyzes Shared Learning Repository
            learning: LearningSnapshot dari River
            state: StructuralState saat ini

        Returns:
            DarwinRecommendation dengan parameter_changes dan confidence
        """
        params = self._params
        changes: dict[str, str] = {}
        affected: list[str] = []

        if learning.total_trades < 10:
            return DarwinRecommendation(
                recommendation_id=generate_snapshot_id("DARWIN"),
                parameter_changes={},
                confidence=Decimal("0"),
                reason=f"Insufficient data: only {learning.total_trades} trades",
                affected_strategies=[],
            )

        all_outcomes = shared_repo.get_all_outcomes()
        if not all_outcomes:
            return DarwinRecommendation(
                recommendation_id=generate_snapshot_id("DARWIN"),
                parameter_changes={},
                confidence=Decimal("0"),
                reason="Shared Learning Repository is empty",
                affected_strategies=[],
            )

        if state == StructuralState.SIDEWAY:
            params, changes, affected = self._optimize_grid(params, learning)
        else:
            params, changes, affected = self._optimize_trend(params, learning)

        self._params = params

        conf = Decimal(str(min(learning.win_rate * 100, 90)))
        conf = max(conf, Decimal("10"))

        return DarwinRecommendation(
            recommendation_id=generate_snapshot_id("DARWIN"),
            parameter_changes=changes,
            confidence=conf,
            reason=f"Optimized {len(changes)} parameters from {learning.total_trades} trades",
            affected_strategies=affected,
        )

    def _optimize_grid(self, params: OptimizedParameters, learning: LearningSnapshot) -> tuple[OptimizedParameters, dict[str, str], list[str]]:
        """Optimasi grid parameters dari hasil sideway trades."""
        grid_patterns = ["GRID_TOO_TIGHT", "GRID_TOO_WIDE", "FALSE_BREAKOUT", "VALID_BREAKOUT"]
        grid_trades = [o for o in learning.recent_outcomes if o.exit_reason in grid_patterns]
        changes: dict[str, str] = {}
        affected = ["ADAPTIVE_GRID_SIDEWAY"]

        if not grid_trades:
            return params, changes, affected

        false_breakouts = sum(1 for o in grid_trades if o.exit_reason == "FALSE_BREAKOUT")
        too_tight = sum(1 for o in grid_trades if o.exit_reason == "GRID_TOO_TIGHT")
        too_wide = sum(1 for o in grid_trades if o.exit_reason == "GRID_TOO_WIDE")

        new_grid_atr = params.grid_atr_multiplier
        new_levels = params.grid_levels

        if too_tight > false_breakouts:
            new_grid_atr = min(params.grid_atr_multiplier + Decimal("0.1"), Decimal("2.0"))
            changes["grid_atr_multiplier"] = str(new_grid_atr)
        if too_wide > false_breakouts:
            new_grid_atr = max(params.grid_atr_multiplier - Decimal("0.1"), Decimal("0.3"))
            changes["grid_atr_multiplier"] = str(new_grid_atr)
        if false_breakouts > 3:
            new_levels = min(params.grid_levels + 1, 10)
            changes["grid_levels"] = str(new_levels)

        return OptimizedParameters(
            atr_multiplier=params.atr_multiplier,
            tp_multiplier=params.tp_multiplier,
            sl_multiplier=params.sl_multiplier,
            confidence_threshold=params.confidence_threshold,
            grid_atr_multiplier=new_grid_atr,
            grid_levels=new_levels,
        ), changes, affected

    def _optimize_trend(self, params: OptimizedParameters, learning: LearningSnapshot) -> tuple[OptimizedParameters, dict[str, str], list[str]]:
        """Optimasi trend parameters dari hasil trend-following trades."""
        changes: dict[str, str] = {}
        affected = ["TREND_FOLLOWING_LONG", "TREND_FOLLOWING_SHORT"]

        if learning.win_rate < 0.4:
            new_params = OptimizedParameters(
                atr_multiplier=params.atr_multiplier + Decimal("0.5"),
                tp_multiplier=params.tp_multiplier,
                sl_multiplier=params.sl_multiplier + Decimal("0.5"),
                confidence_threshold=min(params.confidence_threshold + Decimal("10"), Decimal("90")),
            )
            changes["atr_multiplier"] = str(new_params.atr_multiplier)
            changes["sl_multiplier"] = str(new_params.sl_multiplier)
            changes["confidence_threshold"] = str(new_params.confidence_threshold)
            return new_params, changes, affected
        elif learning.win_rate > 0.6:
            new_params = OptimizedParameters(
                atr_multiplier=max(params.atr_multiplier - Decimal("0.5"), Decimal("1.0")),
                tp_multiplier=params.tp_multiplier + Decimal("0.5"),
                sl_multiplier=max(params.sl_multiplier - Decimal("0.5"), Decimal("1.0")),
                confidence_threshold=max(params.confidence_threshold - Decimal("5"), Decimal("30")),
            )
            changes["atr_multiplier"] = str(new_params.atr_multiplier)
            changes["tp_multiplier"] = str(new_params.tp_multiplier)
            changes["sl_multiplier"] = str(new_params.sl_multiplier)
            changes["confidence_threshold"] = str(new_params.confidence_threshold)
            return new_params, changes, affected
        return params, changes, affected

    def detect_strategy_rotation(self, worker_win_rates: dict[str, float]) -> Optional[StrategyRotationSignal]:
        """Detect if a worker's win rate dropped >25% over 200 trades → recommend rotation."""
        for strategy, rate in worker_win_rates.items():
            if rate < 0.4:  # 40% threshold (25% drop from 65%)
                return StrategyRotationSignal(
                    from_strategy=strategy,
                    to_strategy="SIDEWAY" if "LONG" in strategy or "SHORT" in strategy else "TREND",
                    reason=f"{strategy} win_rate dropped to {rate:.0%}",
                    confidence=Decimal("70"),
                )
        return None
