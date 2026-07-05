from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction, GridState, StructuralGeometry, StructuralState, TradingPlanState
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.trading_plan.builders.sideway_builder import SidewayBuilder
from st_lms.trading_plan.models.adaptive_grid import AdaptiveGrid


def test_adaptive_grid_valid() -> None:
    grid = AdaptiveGrid(
        grid_id="GRID-001",
        plan_id="PLAN-001",
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("110"),
        grid_spacing=Decimal("2"),
        grid_levels=5,
        scale_in_size=Decimal("0.2"),
        grid_take_profit=Decimal("112"),
        risk_limit=Decimal("0.05"),
        state=GridState.WAITING,
    )
    assert grid.grid_levels == 5
    assert grid.state == GridState.WAITING
    assert grid.grid_id == "GRID-001"


def test_adaptive_grid_invalid_levels() -> None:
    try:
        AdaptiveGrid(
            grid_id="GRID-002",
            plan_id="PLAN-002",
            entry_zone_low=Decimal("100"),
            entry_zone_high=Decimal("110"),
            grid_spacing=Decimal("2"),
            grid_levels=0,
            scale_in_size=Decimal("0.2"),
            grid_take_profit=Decimal("112"),
            risk_limit=Decimal("0.05"),
            state=GridState.WAITING,
        )
        assert False
    except ValueError:
        pass


def test_sideway_builder_returns_both() -> None:
    snap = StructuralSnapshot(
        snapshot_id="SNAP-001",
        state=StructuralState.SIDEWAY,
        confidence=Decimal("70"),
        geometry=StructuralGeometry.CORRIDOR,
        nearest_support=Decimal("100"),
        nearest_resistance=Decimal("110"),
    )
    builder = SidewayBuilder()
    plan, grid = builder.build(snap)
    assert plan.direction == Direction.NEUTRAL
    assert plan.strategy == "ADAPTIVE_GRID_SIDEWAY"
    assert grid.grid_levels >= 3
    assert grid.plan_id == plan.plan_id
    assert grid.state == GridState.WAITING


def test_long_builder_no_grid() -> None:
    """LongBuilder tidak boleh menghasilkan AdaptiveGrid."""
    from st_lms.trading_plan.builders.long_builder import LongBuilder
    snap = StructuralSnapshot(
        snapshot_id="SNAP-002",
        state=StructuralState.UPTREND,
        confidence=Decimal("85"),
        geometry=StructuralGeometry.ASCENDING,
        nearest_support=Decimal("100"),
        nearest_resistance=Decimal("110"),
    )
    plan = LongBuilder().build(snap)
    assert plan.strategy != "ADAPTIVE_GRID_SIDEWAY"
    assert plan.direction == Direction.LONG


def test_short_builder_no_grid() -> None:
    """ShortBuilder tidak boleh menghasilkan AdaptiveGrid."""
    from st_lms.trading_plan.builders.short_builder import ShortBuilder
    snap = StructuralSnapshot(
        snapshot_id="SNAP-003",
        state=StructuralState.DOWNTREND,
        confidence=Decimal("85"),
        geometry=StructuralGeometry.DESCENDING,
        nearest_support=Decimal("100"),
        nearest_resistance=Decimal("110"),
    )
    plan = ShortBuilder().build(snap)
    assert plan.strategy != "ADAPTIVE_GRID_SIDEWAY"
    assert plan.direction == Direction.SHORT
