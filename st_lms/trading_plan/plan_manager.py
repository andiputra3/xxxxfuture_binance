from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from st_lms.authorize.authorization_gateway import AuthorizationGateway
from st_lms.common.enums import RiverRecommendation, TradingPlanState
from st_lms.models.river_state import RiverState
from st_lms.models.authorization import Authorization
from st_lms.models.learning_snapshot import LearningSnapshot
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import TradingPlan
from st_lms.trading_plan.models.adaptive_grid import AdaptiveGrid
from st_lms.trading_plan.planner import Planner
from st_lms.trading_plan.validators.plan_validator import PlanValidator
from st_lms.trading_plan.repository.plan_repository import PlanRepository
from st_lms.river.river_review import RiverReview


class PlanManager:
    """C009/C010/C011 — Orchestrates the full plan lifecycle.

    Flow: PlanManager → RiverReview → AuthorizationGateway (single authority)
    """

    def __init__(self) -> None:
        self._planner = Planner()
        self._validator = PlanValidator()
        self._repository = PlanRepository()
        self._river_review = RiverReview()
        self._auth_gateway = AuthorizationGateway()
        self._grids: dict[str, AdaptiveGrid] = {}

    def create_and_validate(self, snapshot: StructuralSnapshot) -> TradingPlan | None:
        """Create, validate and store a Trading Plan.

        Transitions CREATED → READY after successful validation.
        """
        plan = self._planner.create_plan(snapshot)
        if plan is None:
            return None
        if not self._validator.validate(plan):
            return None

        plan = TradingPlan(
            plan_id=plan.plan_id,
            strategy=plan.strategy,
            direction=plan.direction,
            entry_zone_low=plan.entry_zone_low,
            entry_zone_high=plan.entry_zone_high,
            stop_loss=plan.stop_loss,
            take_profit=plan.take_profit,
            risk_percent=plan.risk_percent,
            confidence=plan.confidence,
            state=TradingPlanState.READY,
            reason=plan.reason,
            revision=plan.revision,
        )
        self._repository.save(plan)

        # Jika SIDEWAY, simpan juga AdaptiveGrid
        result = self._planner.create_plan_with_grid(snapshot)
        if result is not None:
            _, grid = result
            self._grids[grid.plan_id] = grid

        return plan

    def get_grid(self, plan_id: str) -> AdaptiveGrid | None:
        """Ambil AdaptiveGrid untuk plan tertentu (hanya SIDEWAY)."""
        return self._grids.get(plan_id)

    def review_plan(self, plan: TradingPlan, learning: LearningSnapshot) -> RiverState:
        """C010 — River Plan Review: review plan sebelum authorize."""
        return self._river_review.review(plan, learning)

    def authorize(
        self,
        plan: TradingPlan,
        river_recommendation: RiverRecommendation,
        enable_time_filter: bool = False,
        enable_liquidation_check: bool = True,
    ) -> Authorization:
        """C011 — Authorize: delegasi ke AuthorizationGateway (single authority).

        Args:
            plan: TradingPlan must be in READY state
            river_recommendation: Wajib — hasil dari River Plan Review (Prinsip Mutlak #3)
            enable_time_filter: Enable Time-Based Filter (default False)
            enable_liquidation_check: Enable Liquidation Hard-Stop (default True)
        """
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

        if plan.state != TradingPlanState.READY:
            from st_lms.models.authorization import Authorization
            from st_lms.common.enums import AuthorizationStatus
            return Authorization(
                authorization_id="AUTH-SKIP",
                status=AuthorizationStatus.REJECTED,
                confidence=plan.confidence,
                reason=f"Plan is in {plan.state.value} state, not READY",
                timestamp=now_ms,
            )

        return self._auth_gateway.authorize(plan, river_recommendation, enable_time_filter, enable_liquidation_check)
