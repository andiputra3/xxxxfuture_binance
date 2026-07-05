from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from st_lms.common.enums import AuthorizationStatus, RiverRecommendation
from st_lms.config.trading_config import AUTHORIZATION_MIN_CONFIDENCE
from st_lms.models.authorization import Authorization
from st_lms.models.trading_plan import TradingPlan
from st_lms.utils.helpers import generate_authorization_id

# Low volume hours (UTC): 00:00-08:00 and weekends
LOW_VOLUME_HOURS = list(range(0, 8))


class AuthorizationGateway:
    """C011 — SINGLE authorization authority.

    4-layer evaluation:
    1. Plan state must be READY
    2. Confidence >= AUTHORIZATION_MIN_CONFIDENCE
    3. Risk <= 5%
    4. River Recommendation != REJECT
    """

    def authorize(
        self,
        plan: TradingPlan,
        river_recommendation: RiverRecommendation,
        enable_time_filter: bool = False,
    ) -> Authorization:
        """Run all authorization layers and return result.

        Args:
            plan: TradingPlan must be in READY state
            river_recommendation: Wajib — Prinsip Mutlak #3 (Review Before Authorize)
            enable_time_filter: Enable Time-Based Filter (default False for simulation/backtest)
        """
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        current_hour = datetime.now(timezone.utc).hour
        is_weekend = datetime.now(timezone.utc).weekday() >= 5

        if plan.state.value != "READY":
            return Authorization(
                authorization_id=generate_authorization_id(),
                status=AuthorizationStatus.REJECTED,
                confidence=plan.confidence,
                reason=f"Plan state is {plan.state.value}, not READY",
                timestamp=now_ms,
            )

        if plan.confidence < AUTHORIZATION_MIN_CONFIDENCE:
            return Authorization(
                authorization_id=generate_authorization_id(),
                status=AuthorizationStatus.REJECTED,
                confidence=plan.confidence,
                reason=f"Confidence {plan.confidence} below minimum {AUTHORIZATION_MIN_CONFIDENCE}",
                timestamp=now_ms,
            )

        if plan.risk_percent > Decimal("5.0"):
            return Authorization(
                authorization_id=generate_authorization_id(),
                status=AuthorizationStatus.REJECTED,
                confidence=plan.confidence,
                reason="Risk exceeds 5%",
                timestamp=now_ms,
            )

        if river_recommendation == RiverRecommendation.REJECT:
            return Authorization(
                authorization_id=generate_authorization_id(),
                status=AuthorizationStatus.REJECTED,
                confidence=plan.confidence,
                reason="River Plan Review rejected this plan",
                timestamp=now_ms,
            )

        # Time-Based Filter (Layer 5) — only when explicitly enabled (live trading)
        if enable_time_filter and (current_hour in LOW_VOLUME_HOURS or is_weekend) and plan.direction.value != "NEUTRAL":
            return Authorization(
                authorization_id=generate_authorization_id(),
                status=AuthorizationStatus.REJECTED,
                confidence=plan.confidence,
                reason="LOW_VOLUME_PERIOD — non-SIDEWAY trading disabled",
                timestamp=now_ms,
            )

        return Authorization(
            authorization_id=generate_authorization_id(),
            status=AuthorizationStatus.APPROVED,
            confidence=plan.confidence,
            reason="All authorization layers passed",
            timestamp=now_ms,
        )
