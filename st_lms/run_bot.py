#!/usr/bin/env python3
"""
ST_LMS Bot Runner
Usage:
    python run_bot.py              # Run single pipeline cycle
    python run_bot.py --backtest   # Run backtest with 100 candles
"""

import argparse
from decimal import Decimal

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.observe.simulation_observer import SimulationObserver
from st_lms.pipeline import Pipeline
from st_lms.backtest.engine import BacktestEngine


def generate_demo_candles(count: int = 100) -> dict[Timeframe, list[Candle]]:
    """Generate demo candles (uptrend)."""
    candles = []
    for i in range(count):
        close = Decimal("100") + Decimal(i) * Decimal("0.5")
        candles.append(
            Candle(
                "BTCUSDT",
                Timeframe.H4,
                i * 14400000,
                close - Decimal("0.1"),
                close * Decimal("1.01"),
                close * Decimal("0.99"),
                close,
                Decimal("1000"),
            )
        )
    return {Timeframe.H4: candles}


def run_single_cycle():
    print("=== ST_LMS Single Pipeline Run ===\n")
    observer = SimulationObserver()
    pipeline = Pipeline(observer, initial_balance=Decimal("10000"))
    candles = generate_demo_candles(100)

    result = pipeline.run("BTCUSDT", [Timeframe.H4], candles)

    print(f"Plan          : {result.trading_plan.strategy if result.trading_plan else 'None'}")
    print(f"Direction     : {result.trading_plan.direction if result.trading_plan else 'N/A'}")
    print(f"State         : {result.structural_snapshot.state if result.structural_snapshot else 'N/A'}")
    print(f"Auth          : {result.authorization.status if result.authorization else 'N/A'}")
    print(f"Position Size : {result.position_size}")
    print(f"Position ID   : {result.position_id}")
    print(f"Darwin        : {result.darwin_recommendation.recommendation_id if result.darwin_recommendation else 'N/A'}")


def run_backtest():
    print("=== ST_LMS Backtest (100 candles) ===\n")
    candles = generate_demo_candles(100)
    engine = BacktestEngine(initial_balance=Decimal("10000"))
    result = engine.run("BTCUSDT", candles, step=1)

    print(f"Total Candles : {result.total_candles}")
    print(f"Total Trades  : {result.total_trades}")
    print(f"Rejected      : {result.rejected_count}")
    print(f"Final Balance : ${result.final_balance:.2f}")
    print(f"Win Rate      : {result.metrics.win_rate:.1%}")
    print(f"Profit Factor : {result.metrics.profit_factor:.2f}")
    print(f"Max Drawdown  : {result.metrics.max_drawdown:.1%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ST_LMS Trading Bot")
    parser.add_argument("--backtest", action="store_true", help="Run backtest instead of single cycle")
    args = parser.parse_args()

    if args.backtest:
        run_backtest()
    else:
        run_single_cycle()
