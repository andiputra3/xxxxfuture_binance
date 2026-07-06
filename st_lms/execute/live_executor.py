from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from st_lms.common.enums import PositionSide, PositionState
from st_lms.config.exchange_config import ENVIRONMENT
from st_lms.execute.executor import Executor
from st_lms.exchange.binance.binance_client import BinanceClient
from st_lms.models.position import Position
from st_lms.models.trading_plan import TradingPlan


class LiveExecutor(Executor):
    """C012 — Live production trading execution.
    
    Melaksanakan trading plan di Binance Futures LIVE.
    Menggunakan BinanceClient dengan API_KEY / API_SECRET production.
    Mencatat posisi untuk tracking dan monitoring.
    
    WARNING: Gunakan hanya di environment LIVE dengan risk management ketat!
    """

    def __init__(self) -> None:
        self._client = BinanceClient()
        self._positions: dict[str, Position] = {}
        self._plans: dict[str, TradingPlan] = {}

    def execute(self, plan: TradingPlan, quantity: Decimal | None = None) -> str:
        """Execute trading plan di Binance LIVE.
        
        Args:
            plan: TradingPlan yang sudah di-authorize
            quantity: Optional quantity override (default dari plan.risk_percent)
            
        Returns:
            position_id
            
        Raises:
            RuntimeError: Jika environment bukan LIVE atau eksekusi gagal
        """
        if ENVIRONMENT.value != "LIVE":
            raise RuntimeError(
                f"LiveExecutor hanya bisa digunakan di LIVE environment. "
                f"Current: {ENVIRONMENT.value}. "
                f"Gunakan TestnetExecutor untuk TESTNET atau SimulationExecutor untuk SIMULATION."
            )
        
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        position_id = f"LIVE-POS-{plan.plan_id}"
        
        # Tentukan quantity
        pos_qty = quantity if quantity is not None else plan.risk_percent
        
        # Konversi ke side Binance
        side = "BUY" if plan.direction.value == "LONG" else "SELL"
        
        # Place order di Binance LIVE
        order_result = self._client.place_order(
            symbol=plan.symbol.replace("_SIM", ""),  # Remove _SIM suffix jika ada
            side=side,
            quantity=float(pos_qty),
        )
        
        if order_result is None:
            raise RuntimeError(
                "Gagal place order di Binance LIVE - cek koneksi API, saldo, atau limit account"
            )
        
        # Extract fill price dari order result
        fill_price = Decimal(str(order_result.get("avgPrice", order_result.get("price", "0"))))
        if fill_price == Decimal("0"):
            fill_price = plan.entry_zone_low
        
        # Catat posisi lokal
        binance_side = PositionSide.LONG if plan.direction.value == "LONG" else PositionSide.SHORT
        position = Position(
            position_id=position_id,
            symbol=plan.symbol,
            side=binance_side,
            entry_price=fill_price,
            quantity=pos_qty,
            state=PositionState.OPEN,
            timestamp=now_ms,
        )
        
        self._positions[position_id] = position
        self._plans[position_id] = plan
        
        return position_id
    
    def get_position(self, position_id: str) -> Position | None:
        """Get position by ID."""
        return self._positions.get(position_id)
    
    def close_position(self, position_id: str, reason: str = "manual") -> bool:
        """Close position di Binance LIVE.
        
        Args:
            position_id: ID posisi yang akan ditutup
            reason: Alasan penutupan (SL/TP/manual)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        position = self._positions.get(position_id)
        if position is None or position.state != PositionState.OPEN:
            return False
        
        plan = self._plans.get(position_id)
        if plan is None:
            return False
        
        # Place close order (reverse side)
        close_side = "SELL" if position.side == PositionSide.LONG else "BUY"
        
        order_result = self._client.place_order(
            symbol=plan.symbol.replace("_SIM", ""),
            side=close_side,
            quantity=float(position.quantity),
        )
        
        if order_result is None:
            return False
        
        # Update status lokal
        closed = Position(
            position_id=position.position_id,
            symbol=position.symbol,
            side=position.side,
            entry_price=position.entry_price,
            quantity=position.quantity,
            state=PositionState.CLOSED,
            timestamp=position.timestamp,
        )
        self._positions[position_id] = closed
        
        return True
    
    def simulate_price(self, position_id: str, current_price: Decimal) -> Position | None:
        """Simulasi pengecekan SL/TP untuk monitoring.
        
        Tidak menutup posisi secara otomatis di LIVE,
        hanya mengembalikan status apakah SL/TP tersentuh.
        Penutupan harus dilakukan manual via close_position().
        """
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
        
        # Return updated position info (tidak auto-close di LIVE)
        return pos
    
    def get_all_positions(self) -> list[Position]:
        """Get semua posisi aktif."""
        return [p for p in self._positions.values() if p.state == PositionState.OPEN]
    
    def emergency_close_all(self) -> dict[str, bool]:
        """Emergency close semua posisi aktif.
        
        Gunakan hanya dalam kondisi darurat (system failure, margin call, dll).
        
        Returns:
            Dict mapping position_id -> success status
        """
        results: dict[str, bool] = {}
        for position in self.get_all_positions():
            results[position.position_id] = self.close_position(position.position_id, reason="emergency")
        return results
