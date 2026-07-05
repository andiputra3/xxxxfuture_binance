from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import RiverRecommendation, RiverState as RiverStateEnum


@dataclass(slots=True, frozen=True)
class RiverState:
    """River learning state with recommendation."""

    snapshot_id: str
    state: RiverStateEnum
    recommendation: RiverRecommendation
    learning_confidence: Decimal
    total_trades: int

    def __post_init__(self) -> None:
        if self.learning_confidence < Decimal("0") or self.learning_confidence > Decimal("100"):
            raise ValueError("learning_confidence must be between 0 and 100")
        if self.total_trades < 0:
            raise ValueError("total_trades must be >= 0")
