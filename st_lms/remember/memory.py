from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from st_lms.models.structure_snapshot import CompressionZone, StructureSnapshot, TrendInfo
from st_lms.models.supertrend_wave import SupertrendWave
from st_lms.remember.historical_repository import HistoricalStructureRepository


@dataclass
class HistoricalContext:
    """Remember layer output — konteks historis yang relevan."""
    similar_structures: List[StructureSnapshot]
    similar_waves: List[SupertrendWave]
    similar_compressions: List[CompressionZone]
    similar_trends: List[TrendInfo]
    total_snapshots: int


class StructureMemory:
    """C005 — Remember layer (Append-only).

    Menyimpan seluruh histori struktur ke HistoricalStructureRepository.
    Tidak ada penghapusan — append-only sesuai Constitution.
    """

    def __init__(self, repository: HistoricalStructureRepository | None = None) -> None:
        self._repository = repository or HistoricalStructureRepository()

    def store(self, snapshot: StructureSnapshot) -> None:
        self._repository.store(snapshot)

    def find_similar(self, snapshot: StructureSnapshot) -> HistoricalContext:
        """Cari snapshot dengan struktur serupa dari repository append-only."""
        similar_structures: List[StructureSnapshot] = []
        similar_waves: List[SupertrendWave] = []
        similar_compressions: List[CompressionZone] = []
        similar_trends: List[TrendInfo] = []

        current_price = snapshot.nearest_support
        all_snapshots = self._repository.list_all()

        for hist in all_snapshots[-50:]:
            if hist.snapshot_id == snapshot.snapshot_id:
                continue
            hist_price = hist.nearest_support
            if hist_price > Decimal("0"):
                ratio = abs(current_price - hist_price) / hist_price
                if ratio < Decimal("0.05"):
                    similar_structures.append(hist)
                    for wv_list in hist.waves.values():
                        similar_waves.extend(wv_list)
                    similar_compressions.extend(hist.compressions)
                    similar_trends.extend(hist.trends)

        return HistoricalContext(
            similar_structures=similar_structures[:10],
            similar_waves=similar_waves[:20],
            similar_compressions=similar_compressions[:10],
            similar_trends=similar_trends[:10],
            total_snapshots=self._repository.count(),
        )

    def get_repository(self) -> HistoricalStructureRepository:
        return self._repository
