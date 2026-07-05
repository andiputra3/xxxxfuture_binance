from __future__ import annotations

from decimal import Decimal
from typing import Optional

from st_lms.common.enums import RiverRecommendation, RiverState as RiverStateEnum
from st_lms.models.learning_snapshot import LearningSnapshot
from st_lms.models.river_state import RiverState
from st_lms.models.trading_plan import TradingPlan
from st_lms.river.shared_learning_repository import SharedLearningRepository
from st_lms.utils.helpers import generate_snapshot_id


class RiverReview:
    """C010 — River Plan Review dengan Shared Learning pattern matching.

    Membandingkan Trading Plan dengan pengalaman historis.
    Menghasilkan RiverRecommendation + RiverLearningConfidence.

    Jika shared_repo tersedia, lakukan per-pattern matching:
    - Cocokkan strategy + direction plan ini dengan outcome historis
    - Hitung win_rate spesifik untuk pattern ini
    - Adjust recommendation berdasarkan pattern-specific metrics
    """

    def review(self, plan: TradingPlan, learning: LearningSnapshot,
               shared_repo: Optional[SharedLearningRepository] = None) -> RiverState:
        """Review Trading Plan berdasarkan historical learning + pattern matching.

        Args:
            plan: TradingPlan yang akan direview
            learning: LearningSnapshot dari River
            shared_repo: Optional — untuk per-pattern matching dari Shared Learning Repository

        Returns:
            RiverState dengan recommendation + confidence
        """
        if learning.total_trades < 3:
            return RiverState(
                snapshot_id=generate_snapshot_id("RIVER"),
                state=RiverStateEnum.LEARNING,
                recommendation=RiverRecommendation.UNKNOWN,
                learning_confidence=Decimal("0"),
                total_trades=learning.total_trades,
            )

        confidence = Decimal(str(min(Decimal(str(learning.win_rate * 100)), Decimal("100"))))
        confidence = max(confidence, Decimal("10"))

        # Per-pattern matching dari Shared Learning Repository
        if shared_repo is not None:
            return self._review_with_patterns(plan, learning, shared_repo, confidence)

        # Tanpa shared_repo: pakai logika global
        return self._review_global(plan, learning, confidence)

    def _build_state(self, rec: RiverRecommendation, conf: Decimal, total: int) -> RiverState:
        state = RiverStateEnum.STABLE if rec == RiverRecommendation.ALLOW else RiverStateEnum.LEARNING
        return RiverState(
            snapshot_id=generate_snapshot_id("RIVER"),
            state=state,
            recommendation=rec,
            learning_confidence=conf,
            total_trades=total,
        )

    def _review_global(self, plan: TradingPlan, learning: LearningSnapshot,
                       confidence: Decimal) -> RiverState:
        """Review tanpa pattern matching — pakai metrics global."""
        if learning.win_rate < 0.3:
            return self._build_state(RiverRecommendation.REJECT, confidence, learning.total_trades)

        if learning.win_rate < 0.45:
            return self._build_state(RiverRecommendation.CAUTION, confidence, learning.total_trades)

        if plan.strategy in learning.failure_patterns:
            return self._build_state(RiverRecommendation.CAUTION, confidence, learning.total_trades)

        if learning.win_rate >= 0.5 and learning.profit_factor > 1.5:
            return self._build_state(RiverRecommendation.ALLOW, confidence, learning.total_trades)

        return self._build_state(RiverRecommendation.ALLOW, confidence, learning.total_trades)

    def _review_with_patterns(self, plan: TradingPlan, learning: LearningSnapshot,
                              shared_repo: SharedLearningRepository,
                              global_confidence: Decimal) -> RiverState:
        """Review dengan per-pattern matching dari Shared Learning Repository."""
        all_outcomes = shared_repo.get_all_outcomes()
        if not all_outcomes:
            return self._review_global(plan, learning, global_confidence)

        strategy_outcomes = [
            o for o in all_outcomes
            if o.direction == plan.direction.value
        ]

        if not strategy_outcomes:
            return self._review_global(plan, learning, global_confidence)

        total = len(strategy_outcomes)
        wins = [o for o in strategy_outcomes if o.pnl_percent > Decimal("0")]
        losses = [o for o in strategy_outcomes if o.pnl_percent <= Decimal("0")]
        pattern_win_rate = len(wins) / total if total > 0 else 0.0

        pattern_confidence = Decimal(str(min(Decimal(str(pattern_win_rate * 100)), Decimal("100"))))
        pattern_confidence = max(pattern_confidence, Decimal("10"))
        blended = (global_confidence * Decimal("0.3") + pattern_confidence * Decimal("0.7"))

        failure_exits = [o.exit_reason for o in losses]
        dominant_failure = max(set(failure_exits), key=failure_exits.count) if failure_exits else ""
        # Jika >60% loss berasal dari 1 exit_reason, waspadai
        if failure_exits and failure_exits.count(dominant_failure) / len(failure_exits) > 0.6:
            return self._build_state(RiverRecommendation.CAUTION, blended, learning.total_trades)

        if pattern_win_rate < 0.3:
            return self._build_state(RiverRecommendation.REJECT, blended, learning.total_trades)

        if pattern_win_rate < 0.45:
            return self._build_state(RiverRecommendation.CAUTION, blended, learning.total_trades)

        gross_profit = float(sum(o.pnl_percent for o in wins))
        gross_loss = float(abs(sum(o.pnl_percent for o in losses))) if losses else 1.0
        pattern_pf = gross_profit / gross_loss if gross_loss > 0 else 0.0

        if pattern_win_rate >= 0.5 and pattern_pf > 1.5:
            return self._build_state(RiverRecommendation.ALLOW, blended, learning.total_trades)

        return self._build_state(RiverRecommendation.ALLOW, blended, learning.total_trades)
