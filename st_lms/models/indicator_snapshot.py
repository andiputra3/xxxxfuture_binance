from __future__ import annotations

from dataclasses import dataclass

from st_lms.models.atr import ATR
from st_lms.models.macd import MACD


@dataclass(slots=True, frozen=True)
class IndicatorSnapshot:
    """Measure layer output — seluruh indikator pada satu timestamp."""

    snapshot_id: str
    timestamp: int
    atr: ATR
    macd: MACD
    volatility: float  # standar deviasi return
    oi_delta: float    # perubahan OI dalam 24h (%)
    price_momentum: float  # perubahan harga dalam periode tertentu (%)

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
