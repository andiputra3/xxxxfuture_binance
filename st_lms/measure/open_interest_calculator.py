from __future__ import annotations

from decimal import Decimal
from typing import List

from st_lms.common.enums import OpenInterestState
from st_lms.models.open_interest import OpenInterest


def classify_open_interest(values: List[OpenInterest]) -> OpenInterest:
    """Classify the latest OI state based on trend."""
    if not values:
        raise ValueError("No OI data")

    latest = values[-1]
    if len(values) < 2:
        return OpenInterest(
            symbol=latest.symbol,
            timestamp=latest.timestamp,
            value=latest.value,
            state=OpenInterestState.FLAT,
        )

    prev = values[-2]
    change = latest.value - prev.value
    threshold = prev.value * Decimal("0.01")

    if change > threshold:
        state = OpenInterestState.INCREASING
    elif change < -threshold:
        state = OpenInterestState.DECREASING
    else:
        state = OpenInterestState.FLAT

    return OpenInterest(
        symbol=latest.symbol,
        timestamp=latest.timestamp,
        value=latest.value,
        state=state,
    )
