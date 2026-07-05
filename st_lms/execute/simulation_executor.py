from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from st_lms.common.enums import PositionSide, PositionState
from st_lms.execute.executor import Executor
from st_lms.models.position import Position
from st_lms.models.trading_plan import TradingPlan


class SimulationExecutor(Executor):
    """C012 — Simulated trade execution with SL/TP simulation.

    Melaksanakan izin di mode simulasi.
    Mencatat posisi untuk tracking.
    simulate_price() untuk menguji apakah SL/TP tersentuh.
    """

    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}
        self._plans: dict[str, TradingPlan] = {}

    def execute(self, plan: TradingPlan, quantity: Decimal | None = None) -> str:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        position_id = f"SIM-POS-{plan.plan_id}"

        side = PositionSide.LONG if plan.direction.value == "LONG" else PositionSide.SHORT

        pos_qty = quantity if quantity is not None else plan.risk_percent / Decimal("100")

        position = Position(
            position_id=position_id,
            symbol="SIM",
            side=side,
            entry_price=plan.entry_zone_low,
            quantity=pos_qty,
            state=PositionState.OPEN,
            timestamp=now_ms,
        )

        self._positions[position_id] = position
        self._plans[position_id] = plan
        return position_id

    def simulate_price(self, position_id: str, current_price: Decimal) -> Position | None:
        """Simulasi pergerakan harga — cek apakah SL/TP tersentuh."""
        pos = self._positions.get(position_id)
        if pos is None or pos.state != PositionState.OPEN:
            return pos

        plan = self._plans.get(position_id)
        if plan is None:
            return pos

        sl_hit = False
        tp_hit = False
        exit_reason = ""

        if pos.side == PositionSide.LONG:
            if current_price <= plan.stop_loss:
                sl_hit = True
                exit_reason = "SL"
            elif current_price >= plan.take_profit:
                tp_hit = True
                exit_reason = "TP"
        else:
            if current_price >= plan.stop_loss:
                sl_hit = True
                exit_reason = "SL"
            elif current_price <= plan.take_profit:
                tp_hit = True
                exit_reason = "TP"

        if sl_hit or tp_hit:
            closed = Position(
                position_id=pos.position_id,
                symbol=pos.symbol,
                side=pos.side,
                entry_price=pos.entry_price,
                quantity=pos.quantity,
                state=PositionState.CLOSED,
                timestamp=pos.timestamp,
            )
            self._positions[position_id] = closed
            return closed

        return pos

    def close_position(self, position_id: str, exit_reason: str = "manual") -> None:
        if position_id in self._positions:
            pos = self._positions[position_id]
            self._positions[position_id] = Position(
                position_id=pos.position_id,
                symbol=pos.symbol,
                side=pos.side,
                entry_price=pos.entry_price,
                quantity=pos.quantity,
                state=PositionState.CLOSED,
                timestamp=pos.timestamp,
            )

    def get_position(self, position_id: str) -> Position | None:
        return self._positions.get(position_id)

    def compute_liquidation_price(self, position: Position, leverage: Decimal = Decimal("10")) -> Decimal:
        """Compute liquidation price (approx 90% of margin)."""
        if leverage <= Decimal("0"):
            return position.entry_price
        distance = position.entry_price / leverage * Decimal("0.9")
        if position.side == PositionSide.LONG:
            return position.entry_price - distance
        else:
            return position.entry_price + distance
