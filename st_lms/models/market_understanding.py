from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import StructuralGeometry


@dataclass(slots=True, frozen=True)
class MarketUnderstanding:
    """Understand layer output — pemahaman struktur yang sudah dianalisis."""

    snapshot_id: str
    timestamp: int
    trend_strength: Decimal      # 0-100
    compression_level: Decimal   # 0-100 (100 = sangat terkompresi)
    wave_quality: Decimal        # 0-100 (100 = wave sempurna)
    structural_confidence: Decimal  # 0-100 — confidence gabungan
    geometry: StructuralGeometry

    def __post_init__(self) -> None:
        for name in ("trend_strength", "compression_level", "wave_quality", "structural_confidence"):
            val = getattr(self, name)
            if val < Decimal("0") or val > Decimal("100"):
                raise ValueError(f"{name} must be between 0 and 100")
