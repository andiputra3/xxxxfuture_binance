from __future__ import annotations

from decimal import Decimal

import pytest

from st_lms.common.enums import (
    AuthorizationStatus,
    DarwinState as DarwinStateEnum,
    Direction,
    LineStatus,
    MACDBucket,
    OpenInterestState,
    PositionSide,
    PositionState,
    RiverRecommendation,
    RiverState as RiverStateEnum,
    StructuralGeometry,
    StructuralState as StructuralStateEnum,
    Timeframe,
    TradingPlanState,
    WaveState,
)
from st_lms.models.atr import ATR
from st_lms.models.authorization import Authorization
from st_lms.models.candle import Candle
from st_lms.models.darwin_state import DarwinState
from st_lms.models.macd import MACD
from st_lms.models.open_interest import OpenInterest
from st_lms.models.position import Position
from st_lms.models.river_state import RiverState
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.supertrend_line import SupertrendLine
from st_lms.models.supertrend_point import SupertrendPoint
from st_lms.models.supertrend_wave import SupertrendWave
from st_lms.models.trading_plan import TradingPlan


def test_candle_valid() -> None:
    c = Candle("BTCUSDT", Timeframe.H1, 1000, Decimal("100"), Decimal("110"), Decimal("90"), Decimal("105"), Decimal("1000"))
    assert c.symbol == "BTCUSDT"
    assert c.close == Decimal("105")


def test_candle_invalid_negative_price() -> None:
    with pytest.raises(ValueError):
        Candle("BTCUSDT", Timeframe.H1, 1000, Decimal("-1"), Decimal("110"), Decimal("90"), Decimal("105"), Decimal("1000"))


def test_candle_high_low_violation() -> None:
    with pytest.raises(ValueError):
        Candle("BTCUSDT", Timeframe.H1, 1000, Decimal("100"), Decimal("80"), Decimal("90"), Decimal("105"), Decimal("1000"))


def test_atr_valid() -> None:
    a = ATR(1000, 10, Decimal("2.5"))
    assert a.value == Decimal("2.5")


def test_macd_valid() -> None:
    m = MACD(1000, Decimal("0.5"), Decimal("0.3"), Decimal("0.2"), MACDBucket.BULLISH)
    assert m.bucket == MACDBucket.BULLISH


def test_open_interest_valid() -> None:
    oi = OpenInterest("BTCUSDT", 1000, Decimal("500000"), OpenInterestState.INCREASING)
    assert oi.state == OpenInterestState.INCREASING


def test_supertrend_point_valid() -> None:
    sp = SupertrendPoint("STP-001", "BTCUSDT", Timeframe.H1, 1000, Decimal("105"), Decimal("2.5"), Direction.LONG, 10)
    assert sp.direction == Direction.LONG
    assert sp.point_id == "STP-001"


def test_supertrend_line_valid() -> None:
    sl = SupertrendLine("STL-001", "BTCUSDT", Timeframe.H1, Direction.LONG, Decimal("100"), 1000, 2000, 10, 3, LineStatus.ACTIVE)
    assert sl.status == LineStatus.ACTIVE
    assert sl.line_id == "STL-001"


def test_supertrend_wave_valid() -> None:
    sw = SupertrendWave("WAV-001", "BTCUSDT", Timeframe.H1, Direction.LONG, "L-1", "L-2", Decimal("50"), 100, WaveState.ACTIVE)
    assert sw.status == WaveState.ACTIVE
    assert sw.wave_id == "WAV-001"


def test_structural_snapshot_valid() -> None:
    ss = StructuralSnapshot("SS-001", StructuralStateEnum.UPTREND, Decimal("85"), StructuralGeometry.ASCENDING, Decimal("100"), Decimal("110"))
    assert ss.state == StructuralStateEnum.UPTREND
    assert ss.snapshot_id == "SS-001"


def test_trading_plan_valid() -> None:
    tp = TradingPlan("PLAN-001", "TREND_FOLLOWING", Direction.LONG, Decimal("100"), Decimal("105"), Decimal("98"), Decimal("115"), Decimal("2"), Decimal("80"), TradingPlanState.CREATED, "test")
    assert tp.state == TradingPlanState.CREATED


def test_authorization_valid() -> None:
    az = Authorization("AUTH-001", AuthorizationStatus.APPROVED, Decimal("85"), "OK", 1000)
    assert az.timestamp == 1000
    assert az.authorization_id == "AUTH-001"


def test_position_valid() -> None:
    pos = Position("POS-001", "BTCUSDT", PositionSide.LONG, Decimal("100"), Decimal("1.0"), PositionState.OPEN, 1000)
    assert pos.state == PositionState.OPEN
    assert pos.position_id == "POS-001"


def test_river_state_valid() -> None:
    rs = RiverState("RIVER-001", RiverStateEnum.LEARNING, RiverRecommendation.ALLOW, Decimal("60"), 100)
    assert rs.recommendation == RiverRecommendation.ALLOW
    assert rs.snapshot_id == "RIVER-001"


def test_darwin_state_valid() -> None:
    ds = DarwinState("DARWIN-001", DarwinStateEnum.EMPTY, Decimal("30"), 50)
    assert ds.state == DarwinStateEnum.EMPTY
    assert ds.snapshot_id == "DARWIN-001"
