from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.common.enums import Timeframe
from st_lms.models.authorization import Authorization
from st_lms.models.backtest_result import BacktestResult, BacktestTrade
from st_lms.models.candle import Candle
from st_lms.models.learning_snapshot import TradeOutcome
from st_lms.observe.simulation_observer import SimulationObserver
from st_lms.pipeline import Pipeline
from st_lms.models.metrics import calculate_metrics
from st_lms.utils.helpers import generate_trade_id


class BacktestEngine:
    """Backtest Engine — replay historical candles through the pipeline.

    Cara kerja:
    1. Iterasi candle per-step
    2. Setiap step: jalankan pipeline dengan data sampai candle tersebut
    3. Track semua trade, equity, metrics
    """

    def __init__(self, initial_balance: Decimal = Decimal("10000"),
                 risk_method: str = "fixed_fraction") -> None:
        self._observer = SimulationObserver()
        self._pipeline = Pipeline(self._observer, initial_balance)
        self._risk_method = risk_method
        self._balance = initial_balance
        self._pipeline.set_balance(initial_balance)

    def run(self, symbol: str, candles: Dict[Timeframe, List[Candle]],
            step: int = 1) -> BacktestResult:
        """Run backtest dengan historical candle replay.

        Args:
            symbol: Trading pair
            candles: Dict timeframe -> list of candles (sorted)
            step: Process every N candles (1 = every candle)

        Returns:
            BacktestResult dengan metrics lengkap
        """
        errors: List[str] = []
        trades: List[BacktestTrade] = []
        equity: List[Decimal] = [self._balance]
        rejected_count = 0

        # Pastikan candles terurut
        primary_tf = max(candles.keys(), key=lambda tf: list(Timeframe).index(tf)) if candles else Timeframe.H4
        all_candles = sorted(candles.get(primary_tf, []), key=lambda c: c.timestamp)

        for i in range(0, len(all_candles), step):
            current_candle = all_candles[i]
            current_price = current_candle.close

            # Siapkan data sampai candle ini
            window = all_candles[:i + 1]
            data: Dict[Timeframe, List[Candle]] = {primary_tf: window}

            # Sync Pipeline balance before each run
            self._pipeline.set_balance(self._balance)

            try:
                result = self._pipeline.run(symbol, [primary_tf], data, self._risk_method)
            except Exception as e:
                errors.append(f"candle {i}: {e}")
                equity.append(self._balance)
                continue

            # Cek apakah ada trade
            if result.position_id and result.trading_plan and result.authorization:
                pos = self._pipeline.get_position(result.position_id)
                if pos and pos.state.value == "CLOSED":
                    # Hitung PnL aktual
                    pnl = current_price - pos.entry_price
                    if pos.side.value == "SHORT":
                        pnl = -pnl
                    pnl_pct = (pnl / pos.entry_price) * Decimal("100")
                    pnl_total = pnl * pos.quantity

                    trade = BacktestTrade(
                        timestamp=current_candle.timestamp,
                        plan_id=result.trading_plan.plan_id,
                        symbol=symbol,
                        direction=pos.side.value,
                        entry_price=pos.entry_price,
                        exit_price=current_price,
                        quantity=pos.quantity,
                        pnl=pnl_total,
                        pnl_percent=pnl_pct,
                        exit_reason="SL/TP",
                        authorization=result.authorization.status.value,
                    )
                    trades.append(trade)

                    # Update balance after trade
                    self._balance = max(self._balance + pnl_total, Decimal("0"))
                    self._pipeline.set_balance(self._balance)
                    equity.append(self._balance)
                    continue

            if result.authorization and result.authorization.status.value == "REJECTED":
                rejected_count += 1

            equity.append(self._balance)

        metrics = calculate_metrics([
            TradeOutcome(
                trade_id=generate_trade_id(),
                plan_id=t.plan_id,
                direction=t.direction,
                entry_price=t.entry_price,
                exit_price=t.exit_price,
                pnl_percent=t.pnl_percent,
                duration_hours=0,
                exit_reason=t.exit_reason,
            ) for t in trades
        ])

        return BacktestResult(
            symbol=symbol,
            total_candles=len(all_candles),
            total_trades=len(trades),
            initial_balance=Decimal("10000"),
            final_balance=self._balance,
            metrics=metrics,
            trades=trades,
            equity_curve=equity,
            rejected_count=rejected_count,
            errors=errors,
        )
