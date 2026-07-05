from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import AuthorizationStatus, Direction, RiverRecommendation, StructuralGeometry, StructuralState, TradingPlanState
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.trading_plan.planner import Planner
from st_lms.trading_plan.plan_manager import PlanManager


def _make_snapshot() -> StructuralSnapshot:
    return StructuralSnapshot(
        snapshot_id="SNAP-TEST",
        state=StructuralState.UPTREND,
        confidence=Decimal("85"),
        geometry=StructuralGeometry.ASCENDING,
        nearest_support=Decimal("100"),
        nearest_resistance=Decimal("110"),
    )


def test_planner_creates_long_plan() -> None:
    snap = _make_snapshot()
    planner = Planner()
    plan = planner.create_plan(snap)
    assert plan is not None
    assert plan.direction == Direction.LONG


def test_planner_returns_none_for_unknown_state() -> None:
    snap = StructuralSnapshot(
        snapshot_id="SNAP-TEST-2",
        state=StructuralState.UPTREND,
        confidence=Decimal("85"),
        geometry=StructuralGeometry.ASCENDING,
        nearest_support=Decimal("100"),
        nearest_resistance=Decimal("110"),
    )
    planner = Planner()
    plan = planner.create_plan(snap)
    assert plan is not None


def test_plan_manager_create_and_validate() -> None:
    snap = _make_snapshot()
    mgr = PlanManager()
    plan = mgr.create_and_validate(snap)
    assert plan is not None
    assert plan.state == TradingPlanState.READY  # CREATED → READY setelah validasi


def test_plan_manager_authorize_allowed() -> None:
    snap = _make_snapshot()
    mgr = PlanManager()
    plan = mgr.create_and_validate(snap)
    assert plan is not None
    auth = mgr.authorize(plan, RiverRecommendation.ALLOW)
    assert auth.status == AuthorizationStatus.APPROVED


def test_plan_manager_authorize_rejected_by_river() -> None:
    snap = _make_snapshot()
    mgr = PlanManager()
    plan = mgr.create_and_validate(snap)
    assert plan is not None
    auth = mgr.authorize(plan, RiverRecommendation.REJECT)
    assert auth.status == AuthorizationStatus.REJECTED
