from __future__ import annotations

from typing import Dict, List, Optional

from st_lms.models.structure_snapshot import StructureSnapshot


class HistoricalStructureRepository:
    """C005 — Historical Structure Repository (Append-only).

    Menyimpan seluruh struktur yang pernah terbentuk.
    Tidak ada penghapusan. Hanya tambah.
    """

    def __init__(self) -> None:
        self._snapshots: Dict[str, StructureSnapshot] = {}

    def store(self, snapshot: StructureSnapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot

    def get(self, snapshot_id: str) -> Optional[StructureSnapshot]:
        return self._snapshots.get(snapshot_id)

    def list_all(self) -> List[StructureSnapshot]:
        return list(self._snapshots.values())

    def count(self) -> int:
        return len(self._snapshots)
