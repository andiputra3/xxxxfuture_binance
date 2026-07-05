from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import DarwinState as DarwinStateEnum


@dataclass(slots=True, frozen=True)
class DarwinState:
    """Darwin improvement state."""

    snapshot_id: str
    state: DarwinStateEnum
    improvement_confidence: Decimal
    recommendations_count: int

    def __post_init__(self) -> None:
        if self.improvement_confidence < Decimal("0") or self.improvement_confidence > Decimal("100"):
            raise ValueError("improvement_confidence must be between 0 and 100")
        if self.recommendations_count < 0:
            raise ValueError("recommendations_count must be >= 0")
