from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.common.enums import Direction
from st_lms.models.order import Fill, Order
from st_lms.models.trading_plan import TradingPlan
from st_lms.utils.helpers import generate_authorization_id


class OrderManager:
    """C012 — Order management with partial fills, OCO, cancel-replace.

    Menangani lifecycle order:
    - PENDING → FILLED (full fill)
    - PENDING → PARTIAL (partial fill, tetap open)
    - PENDING → CANCELLED
    - OCO: dua orders, satu terisi yang lain otomatis cancel
    """

    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    def place_market(self, plan: TradingPlan, quantity: Decimal, max_slippage_pct: Decimal = Decimal("0.001")) -> Order:
        """Place MARKET order — langsung terisi penuh.

        Args:
            plan: TradingPlan
            quantity: Order quantity
            max_slippage_pct: Maximum allowed slippage (default 0.1%). If exceeded, order is REJECTED.

        Returns:
            Order with state FILLED or REJECTED
        """
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        order_id = f"MKT-{generate_authorization_id()}"

        # Simulate realistic slippage (0-0.2% random)
        import random
        slippage = Decimal(str(random.uniform(0, 0.002)))
        fill_price = plan.entry_zone_low * (Decimal("1") + slippage)

        if slippage > max_slippage_pct:
            # Slippage exceeded tolerance → REJECT
            order = Order(
                order_id=order_id,
                plan_id=plan.plan_id,
                symbol="SIM",
                direction=plan.direction,
                order_type="MARKET",
                price=plan.entry_zone_low,
                quantity=quantity,
                filled_quantity=Decimal("0"),
                state="REJECTED",
                timestamp=now_ms,
                fills=[],
            )
            self._orders[order_id] = order
            return order

        fill = Fill(
            fill_id=f"FILL-{order_id}",
            price=fill_price,
            quantity=quantity,
            timestamp=now_ms,
            fee=Decimal("0"),
        )

        order = Order(
            order_id=order_id,
            plan_id=plan.plan_id,
            symbol="SIM",
            direction=plan.direction,
            order_type="MARKET",
            price=plan.entry_zone_low,
            quantity=quantity,
            filled_quantity=quantity,
            state="FILLED",
            timestamp=now_ms,
            fills=[fill],
        )
        self._orders[order_id] = order
        return order

    def place_limit(self, plan: TradingPlan, quantity: Decimal, limit_price: Decimal) -> Order:
        """Place LIMIT order — menunggu sampai harga tersentuh."""
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        order_id = f"LMT-{generate_authorization_id()}"

        order = Order(
            order_id=order_id,
            plan_id=plan.plan_id,
            symbol="SIM",
            direction=plan.direction,
            order_type="LIMIT",
            price=limit_price,
            quantity=quantity,
            filled_quantity=Decimal("0"),
            state="PENDING",
            timestamp=now_ms,
            fills=[],
        )
        self._orders[order_id] = order
        return order

    def place_oco(self, plan: TradingPlan, quantity: Decimal,
                  entry_price: Decimal, stop_price: Decimal, limit_price: Decimal) -> tuple[Order, Order]:
        """Place OCO (One Cancels Other) orders.

        Args:
            plan: Trading plan
            quantity: Order quantity
            entry_price: Harga entry
            stop_price: Harga stop (untuk stop-loss order)
            limit_price: Harga limit (untuk take-profit order)

        Returns:
            Tuple (stop_order, limit_order)
        """
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        stop_id = f"OCO-STOP-{generate_authorization_id()}"
        limit_id = f"OCO-LMT-{generate_authorization_id()}"

        stop_order = Order(
            order_id=stop_id,
            plan_id=plan.plan_id,
            symbol="SIM",
            direction=Direction.SHORT if plan.direction == Direction.LONG else Direction.LONG,
            order_type="STOP",
            price=stop_price,
            quantity=quantity,
            filled_quantity=Decimal("0"),
            state="PENDING",
            timestamp=now_ms,
            fills=[],
            oco_order_id=limit_id,
        )

        limit_order = Order(
            order_id=limit_id,
            plan_id=plan.plan_id,
            symbol="SIM",
            direction=plan.direction,
            order_type="LIMIT",
            price=limit_price,
            quantity=quantity,
            filled_quantity=Decimal("0"),
            state="PENDING",
            timestamp=now_ms,
            fills=[],
            oco_order_id=stop_id,
        )

        self._orders[stop_id] = stop_order
        self._orders[limit_id] = limit_order
        return stop_order, limit_order

    def fill_partial(self, order_id: str, fill_price: Decimal, fill_qty: Decimal) -> Optional[Order]:
        """Isi sebagian order (partial fill)."""
        order = self._orders.get(order_id)
        if order is None or order.state not in ("PENDING", "PARTIAL"):
            return None

        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        new_filled = order.filled_quantity + fill_qty

        fill = Fill(
            fill_id=f"FILL-PARTIAL-{generate_authorization_id()}",
            price=fill_price,
            quantity=fill_qty,
            timestamp=now_ms,
            fee=Decimal("0"),
        )

        new_state = "FILLED" if new_filled >= order.quantity else "PARTIAL"

        updated = Order(
            order_id=order.order_id,
            plan_id=order.plan_id,
            symbol=order.symbol,
            direction=order.direction,
            order_type=order.order_type,
            price=order.price,
            quantity=order.quantity,
            filled_quantity=min(new_filled, order.quantity),
            state=new_state,
            timestamp=order.timestamp,
            fills=list(order.fills) + [fill],
            oco_order_id=order.oco_order_id,
        )

        self._orders[order_id] = updated

        # Jika OCO dan terisi, cancel order satunya
        if new_state == "FILLED" and order.oco_order_id:
            self.cancel(order.oco_order_id)

        return updated

    def cancel_replace(self, order_id: str, new_price: Decimal) -> Optional[Order]:
        """Cancel existing order dan replace dengan harga baru (cancel-replace).

        Old order → CANCELLED
        New order → PENDING dengan harga baru
        """
        old = self._orders.get(order_id)
        if old is None or old.state not in ("PENDING", "PARTIAL"):
            return None

        # Cancel old
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        cancelled = Order(
            order_id=old.order_id,
            plan_id=old.plan_id,
            symbol=old.symbol,
            direction=old.direction,
            order_type=old.order_type,
            price=old.price,
            quantity=old.quantity,
            filled_quantity=old.filled_quantity,
            state="CANCELLED",
            timestamp=old.timestamp,
            fills=old.fills,
            oco_order_id=old.oco_order_id,
        )
        self._orders[order_id] = cancelled

        # Create new
        remaining = old.quantity - old.filled_quantity
        if remaining <= Decimal("0"):
            return None

        new_id = f"CR-{generate_authorization_id()}"
        new_order = Order(
            order_id=new_id,
            plan_id=old.plan_id,
            symbol=old.symbol,
            direction=old.direction,
            order_type=old.order_type,
            price=new_price,
            quantity=remaining,
            filled_quantity=Decimal("0"),
            state="PENDING",
            timestamp=now_ms,
            fills=[],
        )
        self._orders[new_id] = new_order
        return new_order

    def cancel(self, order_id: str) -> bool:
        """Cancel a pending/partial order."""
        order = self._orders.get(order_id)
        if order is None or order.state not in ("PENDING", "PARTIAL"):
            return False

        self._orders[order_id] = Order(
            order_id=order.order_id,
            plan_id=order.plan_id,
            symbol=order.symbol,
            direction=order.direction,
            order_type=order.order_type,
            price=order.price,
            quantity=order.quantity,
            filled_quantity=order.filled_quantity,
            state="CANCELLED",
            timestamp=order.timestamp,
            fills=order.fills,
            oco_order_id=order.oco_order_id,
        )
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_orders_by_plan(self, plan_id: str) -> List[Order]:
        return [o for o in self._orders.values() if o.plan_id == plan_id]
