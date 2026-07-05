from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List

from st_lms.models.supertrend_line import SupertrendLine
from st_lms.models.supertrend_point import SupertrendPoint
from st_lms.models.supertrend_wave import SupertrendWave


@dataclass(slots=True, frozen=True)
class TrendInfo:
    """Trend line identified from Supertrend Lines."""
    direction: str  # UPTREND / DOWNTREND
    strength: int   # 1-10
    start_timestamp: int
    end_timestamp: int
    slope: Decimal


@dataclass(slots=True, frozen=True)
class CompressionZone:
    """Sideways / low volatility zone."""
    start_timestamp: int
    end_timestamp: int
    upper_price: Decimal
    lower_price: Decimal
    atr_percent: Decimal  # ATR sebagai % dari harga


@dataclass(slots=True, frozen=True)
class FibLevel:
    """Fibonacci retracement level."""
    level: Decimal  # 0.0, 0.382, 0.5, 0.618, 1.0
    price: Decimal


@dataclass(slots=True, frozen=True)
class StructureSnapshot:
    """Multi-Timeframe Structure Engine output — seluruh struktur market."""

    snapshot_id: str
    symbol: str
    timestamp: int
    points: Dict[str, List[SupertrendPoint]]  # timeframe -> points
    lines: Dict[str, List[SupertrendLine]]    # timeframe -> lines
    waves: Dict[str, List[SupertrendWave]]    # timeframe -> waves
    trends: List[TrendInfo]
    compressions: List[CompressionZone]
    fib_levels: List[FibLevel]
    nearest_support: Decimal
    nearest_resistance: Decimal

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.nearest_support < Decimal("0"):
            raise ValueError("support must be >= 0")
        if self.nearest_resistance < self.nearest_support:
            raise ValueError("nearest_resistance must not be less than nearest_support")
