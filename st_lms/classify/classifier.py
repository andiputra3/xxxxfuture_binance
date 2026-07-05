from __future__ import annotations

from decimal import Decimal
from typing import Dict

from st_lms.common.enums import StructuralGeometry, StructuralState as StructuralStateEnum, Timeframe
from st_lms.models.market_understanding import MarketUnderstanding
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.select.selector import Candidate
from st_lms.utils.helpers import generate_snapshot_id


class StateClassifier:
    """C008 — SINGLE authority for Structural State.

    Classify layer — menentukan Structural State dari MarketUnderstanding.
    Menghasilkan confidence sendiri berdasarkan geometry + support/resistance range.
    """

    def classify(self, understanding: MarketUnderstanding, candidate: Candidate) -> StructuralSnapshot:
        """Produces StructuralSnapshot dari MarketUnderstanding + Candidate."""
        state = self._determine_state(understanding)
        confidence = self._calculate_confidence(understanding, candidate)
        support = candidate.snapshot.nearest_support
        resistance = candidate.snapshot.nearest_resistance

        return StructuralSnapshot(
            snapshot_id=generate_snapshot_id("CLASS"),
            state=state,
            confidence=confidence,
            geometry=understanding.geometry,
            nearest_support=support,
            nearest_resistance=resistance,
        )

    def _determine_state(self, understanding: MarketUnderstanding) -> StructuralStateEnum:
        geo = understanding.geometry
        if geo in (StructuralGeometry.ASCENDING,):
            return StructuralStateEnum.UPTREND
        elif geo in (StructuralGeometry.DESCENDING,):
            return StructuralStateEnum.DOWNTREND
        else:
            return StructuralStateEnum.SIDEWAY

    def _calculate_confidence(self, understanding: MarketUnderstanding, candidate: Candidate) -> Decimal:
        """Calculate classifier-specific confidence.

        Mulai dari structural_confidence, lalu adjust berdasarkan:
        - Geometry clarity (ASCENDING/DESCENDING +10, CHAOTIC -20)
        - Support/resistance range width
        - Structure age bonus
        """
        conf = understanding.structural_confidence

        if understanding.geometry in (StructuralGeometry.ASCENDING, StructuralGeometry.DESCENDING):
            conf += Decimal("10")
        elif understanding.geometry == StructuralGeometry.CHAOTIC:
            conf -= Decimal("20")
        elif understanding.geometry == StructuralGeometry.CONVERGING:
            conf += Decimal("5")

        snap = candidate.snapshot
        if snap.nearest_resistance > snap.nearest_support:
            range_pct = (snap.nearest_resistance - snap.nearest_support) / snap.nearest_support * Decimal("100")
            if range_pct > Decimal("5"):
                conf += Decimal("5")

        if candidate.structure_age >= 5:
            conf += Decimal("5")

        return max(Decimal("0"), min(conf, Decimal("100")))


def resolve_multi_tf_conflict(tf_states: Dict[Timeframe, StructuralStateEnum]) -> StructuralStateEnum:
    """Multi-TF Conflict Resolution Protocol.

    Rules:
    - All TF aligned → use that state
    - Higher TF aligned, Lower TF conflict → use higher TF
    - Higher TF conflict, Lower TF aligned → REJECT (return SIDEWAY)
    - All TF conflict → SIDEWAY
    """
    if not tf_states:
        return StructuralStateEnum.SIDEWAY

    # Check if all same
    unique = set(tf_states.values())
    if len(unique) == 1:
        return list(unique)[0]

    # Higher TF priority: H4 > H1 > M15 > M5 > M1
    priority = [Timeframe.H4, Timeframe.H1, Timeframe.M15, Timeframe.M5, Timeframe.M1]
    for tf in priority:
        if tf in tf_states:
            return tf_states[tf]

    # Fallback
    return StructuralStateEnum.SIDEWAY
