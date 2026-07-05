from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import Direction, Timeframe, WaveState


@dataclass(slots=True, frozen=True)
class SupertrendWave:
    """Immutable Supertrend Wave."""

    wave_id: str
    symbol: str
    timeframe: Timeframe
    direction: Direction
    start_line_id: str
    end_line_id: str
    amplitude: Decimal
    duration: int
    status: WaveState

    def __post_init__(self) -> None:
        if self.amplitude < Decimal("0"):
            raise ValueError("amplitude cannot be negative")
        if self.duration <= 0:
            raise ValueError("duration must be greater than zero")
