from __future__ import annotations

from decimal import Decimal
from typing import List

from st_lms.models.trading_plan import TradingPlan
from st_lms.models.learning_snapshot import LearningSnapshot
from st_lms.models.open_interest import OpenInterest


class RiverEntry:
    """River entry — validasi entry dengan konfirmasi tambahan."""

    def validate_entry(
        self,
        plan: TradingPlan,
        current_price: Decimal,
        oi: OpenInterest,
        learning: LearningSnapshot,
    ) -> bool:
        """Validasi entry: price in zone + konfirmasi dari River learning."""
        if not (plan.entry_zone_low <= current_price <= plan.entry_zone_high):
            return False

        # River learning filter: hindari pattern yang sering gagal
        if learning.win_rate < 0.4 and learning.total_trades > 5:
            return False

        return True
