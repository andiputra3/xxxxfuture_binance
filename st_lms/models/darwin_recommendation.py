from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class DarwinRecommendation:
    """Darwin output — rekomendasi optimasi dengan confidence dan reason.

    Sesuai Constitution: "Menghasilkan Darwin Recommendation."
    """
    recommendation_id: str
    parameter_changes: dict[str, str]  # "atr_multiplier" -> "3.5", dll
    confidence: Decimal
    reason: str
    affected_strategies: list[str]  # "TREND_FOLLOWING_LONG", "ADAPTIVE_GRID_SIDEWAY", dll

    def __post_init__(self) -> None:
        if self.confidence < Decimal("0") or self.confidence > Decimal("100"):
            raise ValueError("confidence must be between 0 and 100")
