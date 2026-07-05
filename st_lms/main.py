from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.utils.logger import setup_logging


def _generate_demo_candles() -> dict[Timeframe, list[Candle]]:
    """Generate 50 demo candles for pipeline testing."""
    candles = [Candle('BTCUSDT', Timeframe.H4, i*14400000,
        Decimal('100')+Decimal(str(i))*Decimal('0.3'),
        Decimal('101')+Decimal(str(i))*Decimal('0.3'),
        Decimal('99')+Decimal(str(i))*Decimal('0.3'),
        Decimal('100.5')+Decimal(str(i))*Decimal('0.3'), Decimal('100'))
        for i in range(50)]
    return {Timeframe.H4: candles}


def main() -> None:
    """ST_LMS v1.1 — Final Pipeline (C001-C012 + Post-Trade)."""
    setup_logging()
    print("ST_LMS v1.1 — 13-Layer Pipeline")
    print()
    print("  C001 Observe → C002 Measure → C003 Engine → C004 Preserve")
    print("  → C005 Remember → C006 Select → C007 Understand → C008 Classify")
    print("  → C009 Trading Plan → C010 River Review → C011 Authorize")
    print("  → C012 Execute → Post-Trade (River + Darwin)")
    print()
    print("  5 Prinsip Mutlak:")
    print("    1. Structure First")
    print("    2. Plan Before Trade")
    print("    3. Review Before Authorize")
    print("    4. Learn After Result")
    print("    5. Improve Without Touching Core")
    print()
    print("  Modules: RiskManager | OrderManager | BacktestEngine | Metrics | WebSocketObserver")
    print("  Run: pytest tests/ -v  (36 tests)")
    print("  Run: python3 -c 'from st_lms.pipeline import Pipeline; ...'")
    print()

    # Demo pipeline jika dijalankan langsung
    from st_lms.observe.simulation_observer import SimulationObserver
    from st_lms.pipeline import Pipeline

    observer = SimulationObserver()
    pipeline = Pipeline(observer)
    candles = _generate_demo_candles()
    result = pipeline.run("BTCUSDT", [Timeframe.H4], candles)

    print(f"  Pipeline result: plan={result.trading_plan is not None}")
    print(f"  State: {result.structural_snapshot.state if result.structural_snapshot else 'N/A'}")
    print(f"  Auth: {result.authorization.status if result.authorization else 'N/A'}")
    print(f"  Position: {result.position_id}")
    print(f"  Darwin rec: {result.darwin_recommendation.recommendation_id if result.darwin_recommendation else 'N/A'}")
    print()


if __name__ == "__main__":
    main()
