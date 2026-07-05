from __future__ import annotations

from st_lms.common.enums import (
    AuthorizationStatus,
    DarwinState,
    Direction,
    Environment,
    GridState,
    LineStatus,
    MACDBucket,
    MarketSession,
    OpenInterestState,
    PositionSide,
    PositionState,
    RiverRecommendation,
    RiverState,
    StructuralGeometry,
    StructuralState,
    Timeframe,
    TradingPlanState,
    WaveState,
)


def test_all_enums_have_values() -> None:
    assert len(Timeframe) == 5
    assert len(Direction) == 3
    assert len(StructuralState) == 3
    assert len(StructuralGeometry) == 8
    assert len(PositionSide) == 2
    assert len(PositionState) == 5
    assert len(MACDBucket) == 4
    assert len(OpenInterestState) == 4
    assert len(LineStatus) == 3
    assert len(WaveState) == 4
    assert len(TradingPlanState) == 7
    assert len(GridState) == 6
    assert len(RiverState) == 6
    assert len(RiverRecommendation) == 4
    assert len(DarwinState) == 6
    assert len(AuthorizationStatus) == 2
    assert len(MarketSession) == 4
    assert len(Environment) == 3


def test_timeframe_values() -> None:
    assert Timeframe.M1.value == "1m"
    assert Timeframe.H4.value == "4h"


def test_direction_values() -> None:
    assert Direction.LONG.value == "LONG"
    assert Direction.SHORT.value == "SHORT"
    assert Direction.NEUTRAL.value == "NEUTRAL"
