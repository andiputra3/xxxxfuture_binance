from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from st_lms.models.structure_snapshot import StructureSnapshot


@dataclass
class StructureAge:
    """Umur struktur — berapa candle sejak terbentuk."""
    snapshot_id: str
    timestamp: int
    age_in_candles: int  # candle H4 sejak snapshot dibuat
    is_mature: bool      # True jika age >= threshold


@dataclass
class RankedStructure:
    """Struktur yang sudah di-rank untuk Adaptive Structure Stack."""
    snapshot: StructureSnapshot
    age: StructureAge
    price_distance: Decimal  # jarak harga ke harga saat ini (%)
    relevance_score: Decimal  # 0-100, makin tinggi = makin relevan


class AdaptiveStructureStack:
    """C006 — Adaptive Structure Stack.

    Memilih Living Market Structure:
    - Struktur terdekat dengan harga saat ini
    - Struktur dengan age yang成熟 (mature)
    - Struktur yang masih relevan (tidak terlalu tua)
    """

    def __init__(self, maturity_threshold: int = 5) -> None:
        self._maturity_threshold = maturity_threshold

    def build(self, snapshots: List[StructureSnapshot], current_price: Decimal) -> List[RankedStructure]:
        """Bangun stack dari seluruh snapshot, urut berdasarkan relevansi."""
        ranked: List[RankedStructure] = []
        for snap in snapshots:
            age = self._calculate_age(snap)
            distance = self._price_distance(snap, current_price)
            relevance = self._calculate_relevance(age, distance, snap)
            ranked.append(RankedStructure(
                snapshot=snap,
                age=age,
                price_distance=distance,
                relevance_score=relevance,
            ))
        ranked.sort(key=lambda r: r.relevance_score, reverse=True)
        return ranked[:10]  # max 10 struktur teratas

    def get_living_structures(self, ranked: List[RankedStructure]) -> List[RankedStructure]:
        """Filter hanya struktur yang masih 'hidup' (relevance > threshold)."""
        return [r for r in ranked if r.relevance_score > Decimal("30")]

    def _calculate_age(self, snapshot: StructureSnapshot) -> StructureAge:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        age_ms = max(0, now_ms - snapshot.timestamp)
        age_candles = int(age_ms / 14400000)  # 1 candle H4 = 14400000 ms
        return StructureAge(
            snapshot_id=snapshot.snapshot_id,
            timestamp=snapshot.timestamp,
            age_in_candles=age_candles,
            is_mature=age_candles >= self._maturity_threshold,
        )

    def _price_distance(self, snapshot: StructureSnapshot, current_price: Decimal) -> Decimal:
        if current_price <= Decimal("0"):
            return Decimal("100")
        snap_price = snapshot.nearest_support
        if snap_price <= Decimal("0"):
            return Decimal("100")
        return abs(current_price - snap_price) / snap_price * Decimal("100")

    def _calculate_relevance(self, age: StructureAge, distance: Decimal, snapshot: StructureSnapshot) -> Decimal:
        score = Decimal("50")
        if age.is_mature:
            score += Decimal("20")
        score -= distance * Decimal("2")
        if snapshot.trends:
            score += Decimal("10")
        score = max(Decimal("0"), min(score, Decimal("100")))
        return score
