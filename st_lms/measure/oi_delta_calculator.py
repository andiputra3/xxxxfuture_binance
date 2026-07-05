from __future__ import annotations

from typing import List

from st_lms.models.open_interest import OpenInterest


def calculate_oi_delta(values: List[OpenInterest]) -> float:
    """Perubahan OI dalam 24h dalam persen."""
    if len(values) < 2:
        return 0.0

    latest = float(values[-1].value)
    prev = float(values[0].value)
    if prev == 0.0:
        return 0.0
    return ((latest - prev) / prev) * 100.0
