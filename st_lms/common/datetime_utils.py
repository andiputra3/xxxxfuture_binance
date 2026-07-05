from __future__ import annotations

from datetime import datetime, timezone


def ms_to_datetime(ms: int) -> datetime:
    """Convert epoch milliseconds to UTC datetime."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def datetime_to_ms(dt: datetime) -> int:
    """Convert UTC datetime to epoch milliseconds."""
    return int(dt.timestamp() * 1000)
