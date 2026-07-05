from __future__ import annotations

import uuid
from datetime import datetime, timezone


def generate_plan_id() -> str:
    """Generate a unique Trading Plan ID."""
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"PLAN-{date_part}-{unique_part}"


def generate_line_id(symbol: str, price: str) -> str:
    """Generate a Supertrend Line ID."""
    return f"STL-{symbol}-{price}"


def generate_point_id() -> str:
    """Generate a Supertrend Point ID."""
    return f"STP-{uuid.uuid4().hex[:12].upper()}"


def generate_snapshot_id(prefix: str = "SNAP") -> str:
    """Generate a unique Snapshot ID."""
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def generate_grid_id() -> str:
    """Generate a unique Adaptive Grid ID."""
    return f"GRID-{uuid.uuid4().hex[:8].upper()}"


def generate_trade_id() -> str:
    """Generate a unique Trade ID."""
    return f"TRADE-{uuid.uuid4().hex[:8].upper()}"


def generate_authorization_id() -> str:
    """Generate a unique Authorization ID."""
    return f"AUTH-{uuid.uuid4().hex[:8].upper()}"
