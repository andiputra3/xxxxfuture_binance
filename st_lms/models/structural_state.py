from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import StructuralGeometry, StructuralState as StructuralStateEnum


@dataclass(slots=True, frozen=True)
class StructuralSnapshot:
    """Official market structural snapshot with state, confidence and geometry."""

    snapshot_id: str
    state: StructuralStateEnum
    confidence: Decimal
    geometry: StructuralGeometry
    nearest_support: Decimal
    nearest_resistance: Decimal

    def __post_init__(self) -> None:
        if self.confidence < Decimal("0") or self.confidence > Decimal("100"):
            raise ValueError("confidence must be between 0 and 100")
        if self.nearest_support <= Decimal("0"):
            raise ValueError("nearest_support must be greater than zero")
        if self.nearest_resistance <= Decimal("0"):
            raise ValueError("nearest_resistance must be greater than zero")
        if self.nearest_support > self.nearest_resistance:
            raise ValueError("nearest_support must not exceed nearest_resistance")
