from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Direction, LineStatus, StructuralGeometry, StructuralState, Timeframe, WaveState
from st_lms.classify.classifier import StateClassifier
from st_lms.models.market_understanding import MarketUnderstanding
from st_lms.models.structure_snapshot import CompressionZone, FibLevel, StructureSnapshot, TrendInfo
from st_lms.models.supertrend_line import SupertrendLine
from st_lms.models.supertrend_point import SupertrendPoint
from st_lms.models.supertrend_wave import SupertrendWave
from st_lms.remember.memory import HistoricalContext
from st_lms.select.selector import Candidate


def _make_snapshot(state_str: str) -> StructureSnapshot:
    lines = [
        SupertrendLine("L1", "BTCUSDT", Timeframe.H4, Direction.LONG, Decimal("100"), 0, 100, 5, 1, LineStatus.ACTIVE),
        SupertrendLine("L2", "BTCUSDT", Timeframe.H4, Direction.LONG, Decimal("105"), 100, 200, 5, 1, LineStatus.ACTIVE),
    ]
    return StructureSnapshot(
        snapshot_id="STRUC-TEST",
        symbol="BTCUSDT",
        timestamp=200,
        points={},
        lines={"h4": lines},
        waves={},
        trends=[TrendInfo(direction="LONG", strength=5, start_timestamp=0, end_timestamp=200, slope=Decimal("0.5"))],
        compressions=[],
        fib_levels=[],
        nearest_support=Decimal("100"),
        nearest_resistance=Decimal("110"),
    )


def test_classify_uptrend() -> None:
    snap = _make_snapshot("UPTREND")
    context = HistoricalContext(similar_structures=[], similar_waves=[], similar_compressions=[], similar_trends=[], total_snapshots=5)
    candidate = Candidate(snapshot=snap, context=context, rank_score=Decimal("70"), reason="test")
    understanding = MarketUnderstanding(
        snapshot_id="UND-TEST",
        timestamp=200,
        trend_strength=Decimal("80"),
        compression_level=Decimal("10"),
        wave_quality=Decimal("50"),
        structural_confidence=Decimal("70"),
        geometry=StructuralGeometry.ASCENDING,
    )

    classifier = StateClassifier()
    result = classifier.classify(understanding, candidate)
    assert result.state == StructuralState.UPTREND
    # 70 + 10(ASCENDING) + 5(range>5%) = 85
    assert result.confidence == Decimal("85")


def test_classify_downrend() -> None:
    lines = [
        SupertrendLine("L1", "BTCUSDT", Timeframe.H4, Direction.SHORT, Decimal("105"), 0, 100, 5, 1, LineStatus.ACTIVE),
        SupertrendLine("L2", "BTCUSDT", Timeframe.H4, Direction.SHORT, Decimal("100"), 100, 200, 5, 1, LineStatus.ACTIVE),
    ]
    snap = StructureSnapshot(
        snapshot_id="STRUC-TEST-2",
        symbol="BTCUSDT",
        timestamp=200,
        points={},
        lines={"h4": lines},
        waves={},
        trends=[TrendInfo(direction="SHORT", strength=6, start_timestamp=0, end_timestamp=200, slope=Decimal("-0.5"))],
        compressions=[],
        fib_levels=[],
        nearest_support=Decimal("95"),
        nearest_resistance=Decimal("105"),
    )
    context = HistoricalContext(similar_structures=[], similar_waves=[], similar_compressions=[], similar_trends=[], total_snapshots=5)
    candidate = Candidate(snapshot=snap, context=context, rank_score=Decimal("70"), reason="test")
    understanding = MarketUnderstanding(
        snapshot_id="UND-TEST-2",
        timestamp=200,
        trend_strength=Decimal("20"),
        compression_level=Decimal("10"),
        wave_quality=Decimal("50"),
        structural_confidence=Decimal("65"),
        geometry=StructuralGeometry.DESCENDING,
    )

    classifier = StateClassifier()
    result = classifier.classify(understanding, candidate)
    assert result.state == StructuralState.DOWNTREND
    # 65 + 10(DESCENDING) + 5(range>5%) = 80
