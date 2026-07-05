from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from st_lms.common.enums import Timeframe
from st_lms.config.core_config import DEFAULT_TIMEFRAMES, PRIMARY_TIMEFRAME
from st_lms.models.structure_snapshot import StructureSnapshot
from st_lms.remember.memory import HistoricalContext
from st_lms.select.adaptive_stack import AdaptiveStructureStack, RankedStructure


@dataclass
class Candidate:
    """C006 — Select layer output: kandidat struktur terbaik untuk dianalisis."""
    snapshot: StructureSnapshot
    context: HistoricalContext
    rank_score: Decimal
    reason: str
    structure_age: int = 0  # age_in_candles dari AdaptiveStructureStack


class Selector:
    """C006 — Select layer.

    Menggunakan AdaptiveStructureStack untuk memilih Living Market Structure.
    Memperhitungkan Structure Age (kematangan struktur).
    """

    def __init__(self) -> None:
        self._all_timeframes = DEFAULT_TIMEFRAMES
        self._stack = AdaptiveStructureStack()

    def get_active_timeframes(self) -> List[Timeframe]:
        return list(self._all_timeframes)

    def get_primary_timeframe(self) -> Timeframe:
        return PRIMARY_TIMEFRAME

    def get_confirmation_timeframes(self) -> List[Timeframe]:
        return [tf for tf in self._all_timeframes if tf != PRIMARY_TIMEFRAME]

    def select_candidate(
        self, snapshot: StructureSnapshot, context: HistoricalContext
    ) -> Optional[Candidate]:
        """Rank dan filter kandidat — menggunakan AdaptiveStructureStack."""
        all_snapshots = [snapshot] + [s for s in context.similar_structures if s.snapshot_id != snapshot.snapshot_id]
        current_price = snapshot.nearest_support
        ranked = self._stack.build(all_snapshots, current_price)
        living = self._stack.get_living_structures(ranked)

        if not living:
            return None

        best = living[0]
        age_candles = best.age.age_in_candles

        score = Decimal("50")
        reasons: List[str] = []

        if len(context.similar_structures) > 0:
            score += Decimal("10")
            reasons.append("similar structures found")

        if len(context.similar_trends) > 0:
            score += Decimal("10")
            reasons.append("similar trends found")

        if snapshot.trends and snapshot.trends[-1].strength >= 3:
            score += Decimal("10")
            reasons.append(f"trend strength {snapshot.trends[-1].strength}")

        if snapshot.compressions:
            score += Decimal("5")
            reasons.append("compression detected")

        if best.age.is_mature:
            score += Decimal("10")
            reasons.append(f"mature structure ({age_candles} candles)")

        if score < Decimal("50"):
            return None

        return Candidate(
            snapshot=snapshot,
            context=context,
            rank_score=score,
            reason=" | ".join(reasons),
            structure_age=age_candles,
        )
