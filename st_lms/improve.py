from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from st_lms.models.learning_snapshot import TradeOutcome
from st_lms.models.position import Position
from st_lms.river.river_learning import RiverLearning
from st_lms.river.shared_learning_repository import SharedLearningRepository
from st_lms.utils.helpers import generate_trade_id


def improve(
    river_learning: RiverLearning,
    position: Position,
    exit_price: Decimal,
    exit_reason: str,
    shared_repository: SharedLearningRepository | None = None,
) -> None:
    """Post-Trade — Improve → River feedback loop.

    Setelah trade closed, feedback dikirim ke River dan SharedLearningRepository.
    Hanya mencatat outcome — tidak merekam rejection (itu untuk OpportunityLearning terpisah).
    """
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    duration = 0
    if position.timestamp > 0:
        duration = max(0, (now_ms - position.timestamp) // 3600000)

    pnl_pct = ((exit_price - position.entry_price) / position.entry_price) * Decimal("100")
    if position.side.value == "SHORT":
        pnl_pct = -pnl_pct

    outcome = TradeOutcome(
        trade_id=generate_trade_id(),
        plan_id=position.position_id,
        direction=position.side.value,
        entry_price=position.entry_price,
        exit_price=exit_price,
        pnl_percent=pnl_pct,
        duration_hours=max(duration, 0),
        exit_reason=exit_reason,
    )

    river_learning.record_outcome(outcome)

    if shared_repository is not None:
        shared_repository.record_outcome(outcome)
