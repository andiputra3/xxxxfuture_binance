from __future__ import annotations

from decimal import Decimal

from st_lms.common.core_constants import SUPERTREND_ATR_PERIOD, SUPERTREND_MULTIPLIER

ATR_PERIOD = SUPERTREND_ATR_PERIOD
MULTIPLIER = SUPERTREND_MULTIPLIER
MIN_LINE_CANDLES = 5

# Default grid spacing — akan di-override oleh DarwinEngine.optimize()
GRID_ATR_MULTIPLIER = Decimal("1.0")
