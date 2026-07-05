from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import MACDBucket


@dataclass(slots=True, frozen=True)
class MACD:
    """Immutable MACD model."""

    timestamp: int
    macd: Decimal
    signal: Decimal
    histogram: Decimal
    bucket: MACDBucket

    def __post_init__(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
