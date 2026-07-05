from __future__ import annotations

from typing import Dict, Optional

from st_lms.models.learning_snapshot import LearningSnapshot


class RiverRepository:
    """Repository untuk LearningSnapshot."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, LearningSnapshot] = {}

    def save(self, symbol: str, snapshot: LearningSnapshot) -> None:
        self._snapshots[symbol] = snapshot

    def get(self, symbol: str) -> Optional[LearningSnapshot]:
        return self._snapshots.get(symbol)
