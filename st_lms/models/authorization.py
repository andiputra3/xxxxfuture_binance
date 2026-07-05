from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from st_lms.common.enums import AuthorizationStatus


@dataclass(slots=True, frozen=True)
class Authorization:
    """Authorization result with confidence and reason."""

    authorization_id: str
    status: AuthorizationStatus
    confidence: Decimal
    reason: str
    timestamp: int

    def __post_init__(self) -> None:
        if self.confidence < Decimal("0") or self.confidence > Decimal("100"):
            raise ValueError("confidence must be between 0 and 100")
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
