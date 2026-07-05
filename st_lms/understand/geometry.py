from __future__ import annotations

from decimal import Decimal

from st_lms.common.enums import StructuralGeometry
from st_lms.models.market_understanding import MarketUnderstanding
from st_lms.models.structure_snapshot import StructureSnapshot
from st_lms.select.selector import Candidate
from st_lms.utils.helpers import generate_snapshot_id


class GeometryAnalyzer:
    """C007 — Understand layer.

    Menganalisis bentuk geometri struktur:
    ASCENDING, DESCENDING, CORRIDOR, CONVERGING, DIVERGING,
    CHAOTIC, SINGLE_DIRECTION, NO_STRUCTURE
    """

    def analyze(self, candidate: Candidate) -> MarketUnderstanding:
        """Produces MarketUnderstanding dari kandidat struktur terpilih."""
        snap = candidate.snapshot
        ts = snap.timestamp

        trend_strength = self._calculate_trend_strength(snap)
        compression_level = self._calculate_compression_level(snap)
        wave_quality = self._calculate_wave_quality(snap)
        geometry = self._detect_geometry(snap)

        structural_confidence = (
            trend_strength * Decimal("0.4")
            + compression_level * Decimal("0.2")
            + wave_quality * Decimal("0.2")
            + candidate.rank_score * Decimal("0.2")
        )
        structural_confidence = min(structural_confidence, Decimal("100"))

        return MarketUnderstanding(
            snapshot_id=generate_snapshot_id("GEOM"),
            timestamp=ts,
            trend_strength=trend_strength,
            compression_level=compression_level,
            wave_quality=wave_quality,
            structural_confidence=structural_confidence,
            geometry=geometry,
        )

    def _calculate_trend_strength(self, snap: StructureSnapshot) -> Decimal:
        if not snap.trends:
            return Decimal("0")
        return Decimal(str(min(max(snap.trends[-1].strength * 10, 0), 100)))

    def _calculate_compression_level(self, snap: StructureSnapshot) -> Decimal:
        if not snap.compressions:
            return Decimal("0")
        latest = snap.compressions[-1]
        return max(Decimal("0"), Decimal("100") - latest.atr_percent * Decimal("50"))

    def _calculate_wave_quality(self, snap: StructureSnapshot) -> Decimal:
        total_waves = sum(len(w) for w in snap.waves.values())
        return min(Decimal(str(total_waves * 10)), Decimal("100"))

    def _detect_geometry(self, snap: StructureSnapshot) -> StructuralGeometry:
        """Deteksi semua 8 tipe geometry dari struktur."""
        lines_list = []
        for tf_lines in snap.lines.values():
            lines_list.extend(tf_lines)

        if not lines_list:
            return StructuralGeometry.NO_STRUCTURE

        directions = [l.direction.value for l in lines_list]
        all_long = all(d == "LONG" for d in directions)
        all_short = all(d == "SHORT" for d in directions)

        if all_long:
            return StructuralGeometry.ASCENDING
        if all_short:
            return StructuralGeometry.DESCENDING

        # Mixed directions — cek pola lainnya
        long_count = sum(1 for d in directions if d == "LONG")
        short_count = sum(1 for d in directions if d == "SHORT")
        total = len(directions)

        # CHAOTIC: hampir sama jumlah LONG dan SHORT, tidak ada dominasi
        if total >= 4:
            long_ratio = long_count / total
            short_ratio = short_count / total
            if 0.4 <= long_ratio <= 0.6 or 0.4 <= short_ratio <= 0.6:
                if snap.compressions:
                    return StructuralGeometry.CONVERGING
                return StructuralGeometry.CHAOTIC

        # DIVERGING: dominasi bergantian (indikasi range expansion)
        if snap.waves:
            wave_count = sum(len(wv) for wv in snap.waves.values())
            if wave_count >= 3:
                return StructuralGeometry.DIVERGING

        # Mixed directions, no waves, no compressions → CORRIDOR
        return StructuralGeometry.CORRIDOR
