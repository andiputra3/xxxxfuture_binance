from __future__ import annotations

from decimal import Decimal

from st_lms.common.core_constants import MAX_RISK_PER_TRADE

RISK_PER_TRADE = MAX_RISK_PER_TRADE
MAX_DAILY_DRAWDOWN = Decimal("0.05")
MAX_OPEN_POSITIONS = 1
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_QUANTITY = Decimal("0.001")
MAX_LEVERAGE = 3
MIN_CONFIDENCE_TO_TRADE = Decimal("60")
AUTHORIZATION_MIN_CONFIDENCE = Decimal("70")
