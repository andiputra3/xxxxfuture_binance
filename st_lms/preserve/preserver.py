from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.models.indicator_snapshot import IndicatorSnapshot
from st_lms.models.market_snapshot import MarketSnapshot
from st_lms.models.provenance import Provenance
from st_lms.models.structure_snapshot import StructureSnapshot
from st_lms.models.supertrend_line import SupertrendLine
from st_lms.preserve.line_status_manager import LineStatusManager


class SnapshotRepository:
    """C004 — Preserve layer.

    Menyimpan seluruh snapshot dengan provenance.
    Menjaga kontinuitas Supertrend Line via LineStatusManager.
    """

    def __init__(self) -> None:
        self._market: Dict[str, MarketSnapshot] = {}
        self._indicators: Dict[str, IndicatorSnapshot] = {}
        self._structures: Dict[str, StructureSnapshot] = {}
        self._provenance: Dict[str, Provenance] = {}
        self._line_manager = LineStatusManager()

    def store_market(self, snapshot: MarketSnapshot, parent_snapshots: Optional[List[str]] = None) -> str:
        snap_id = snapshot.snapshot_id
        self._market[snap_id] = snapshot
        self._provenance[snap_id] = Provenance(
            source_layer="Observe",
            source_timestamp=snapshot.timestamp,
            parent_snapshots=parent_snapshots or [],
        )
        return snap_id

    def store_indicators(self, snapshot: IndicatorSnapshot, parent_snapshots: Optional[List[str]] = None) -> str:
        snap_id = snapshot.snapshot_id
        self._indicators[snap_id] = snapshot
        self._provenance[snap_id] = Provenance(
            source_layer="Measure",
            source_timestamp=snapshot.timestamp,
            parent_snapshots=parent_snapshots or [],
        )
        return snap_id

    def store_structure(self, snapshot: StructureSnapshot, current_price: Decimal | None = None,
                        parent_snapshots: Optional[List[str]] = None) -> str:
        """Store structure + evaluasi LineStatus terhadap harga terkini.

        Args:
            snapshot: StructureSnapshot dari Engine
            current_price: Harga market aktual. Jika None, pakai nearest_support.
        """
        snap_id = snapshot.snapshot_id
        price = snapshot.nearest_support if current_price is None else current_price

        # Evaluasi semua lines dengan LineStatusManager
        updated_lines: Dict[str, List[SupertrendLine]] = {}
        for tf, lines in snapshot.lines.items():
            updated_lines[tf] = self._line_manager.evaluate(price, lines)

        # Buat snapshot baru dengan lines yang sudah diupdate statusnya
        updated_snapshot = StructureSnapshot(
            snapshot_id=snapshot.snapshot_id,
            symbol=snapshot.symbol,
            timestamp=snapshot.timestamp,
            points=snapshot.points,
            lines=updated_lines,
            waves=snapshot.waves,
            trends=snapshot.trends,
            compressions=snapshot.compressions,
            fib_levels=snapshot.fib_levels,
            nearest_support=snapshot.nearest_support,
            nearest_resistance=snapshot.nearest_resistance,
        )

        self._structures[snap_id] = updated_snapshot
        self._provenance[snap_id] = Provenance(
            source_layer="Multi-Timeframe Structure Engine",
            source_timestamp=snapshot.timestamp,
            parent_snapshots=[],
        )
        return snap_id

    def evaluate_lines(self, snapshot: StructureSnapshot, current_price: Decimal) -> StructureSnapshot:
        """Evaluasi ulang semua lines terhadap harga terbaru (untuk C004)."""
        updated_lines: Dict[str, List[SupertrendLine]] = {}
        for tf, lines in snapshot.lines.items():
            updated_lines[tf] = self._line_manager.evaluate(current_price, lines)

        return StructureSnapshot(
            snapshot_id=snapshot.snapshot_id,
            symbol=snapshot.symbol,
            timestamp=snapshot.timestamp,
            points=snapshot.points,
            lines=updated_lines,
            waves=snapshot.waves,
            trends=snapshot.trends,
            compressions=snapshot.compressions,
            fib_levels=snapshot.fib_levels,
            nearest_support=snapshot.nearest_support,
            nearest_resistance=snapshot.nearest_resistance,
        )

    def get_market(self, snap_id: str) -> Optional[MarketSnapshot]:
        return self._market.get(snap_id)

    def get_indicators(self, snap_id: str) -> Optional[IndicatorSnapshot]:
        return self._indicators.get(snap_id)

    def get_structure(self, snap_id: str) -> Optional[StructureSnapshot]:
        return self._structures.get(snap_id)

    def get_provenance(self, snap_id: str) -> Optional[Provenance]:
        return self._provenance.get(snap_id)

    def get_latest_structure(self) -> Optional[StructureSnapshot]:
        if not self._structures:
            return None
        return list(self._structures.values())[-1]

    def list_all_structures(self) -> List[StructureSnapshot]:
        return list(self._structures.values())
