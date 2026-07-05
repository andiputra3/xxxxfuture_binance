from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import GridState


@dataclass(slots=True, frozen=True)
class AdaptiveGrid:
    """Sideway-specific grid strategy — hanya dibuat oleh SidewayBuilder saat StructuralState == SIDEWAY.

    Field ini TIDAK boleh ada di TradingPlan karena Grid hanya milik Sideway.
    LongBuilder dan ShortBuilder tidak boleh mengetahui model ini.
    """

    grid_id: str
    plan_id: str
    entry_zone_low: Decimal
    entry_zone_high: Decimal
    grid_spacing: Decimal       # jarak antar level dalam ATR (misal 0.7 = 0.7 * ATR)
    grid_levels: int            # jumlah level buy/sell
    scale_in_size: Decimal      # ukuran order per level (sebagai fraksi, misal 0.1 = 10%)
    grid_take_profit: Decimal   # target TP keseluruhan grid
    risk_limit: Decimal         # maksimal exposure grid
    state: GridState

    def __post_init__(self) -> None:
        if self.entry_zone_low <= Decimal("0"):
            raise ValueError("entry_zone_low must be > 0")
        if self.entry_zone_high <= self.entry_zone_low:
            raise ValueError("entry_zone_high must be > entry_zone_low")
        if self.grid_spacing <= Decimal("0"):
            raise ValueError("grid_spacing must be > 0")
        if self.grid_levels < 1:
            raise ValueError("grid_levels must be >= 1")
        if self.scale_in_size <= Decimal("0") or self.scale_in_size > Decimal("1"):
            raise ValueError("scale_in_size must be between 0 and 1")
        if self.risk_limit <= Decimal("0"):
            raise ValueError("risk_limit must be > 0")
