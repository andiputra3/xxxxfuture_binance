from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.models.learning_snapshot import TradeOutcome


class SharedLearningRepository:
    """Shared Learning Repository — pusat pengetahuan bersama.

    Menyimpan semua TradeOutcome (termasuk rejected trades untuk Opportunity Learning).
    Bisa diakses oleh Long, Short, dan Sideway Worker.
    Append-only — tidak ada penghapusan.
    """

    def __init__(self) -> None:
        self._outcomes: Dict[str, TradeOutcome] = {}
        self._rejected_plans: List[Dict] = []

    def record_outcome(self, outcome: TradeOutcome) -> None:
        self._outcomes[outcome.trade_id] = outcome

    def record_rejected_plan(self, plan_id: str, reason: str, confidence: Decimal, direction: str) -> None:
        self._rejected_plans.append({
            "plan_id": plan_id,
            "reason": reason,
            "confidence": str(confidence),
            "direction": direction,
        })

    def get_all_outcomes(self) -> List[TradeOutcome]:
        return list(self._outcomes.values())

    def get_rejected_plans(self) -> List[Dict]:
        return list(self._rejected_plans)

    def get_outcomes_by_direction(self, direction: str) -> List[TradeOutcome]:
        return [o for o in self._outcomes.values() if o.direction == direction]

    def count(self) -> int:
        return len(self._outcomes)

    def analyze_rejections(self, current_price: Decimal, actual_direction: str) -> Dict:
        """Analyze opportunity cost from rejected plans.

        Returns:
            {
                "total_rejected": int,
                "missed_opportunities": int,  # price moved in rejected direction
                "correct_rejections": int,    # price moved against rejected direction
            }
        """
        if not self._rejected_plans:
            return {"total_rejected": 0, "missed_opportunities": 0, "correct_rejections": 0}

        missed = 0
        correct = 0
        for rp in self._rejected_plans:
            if rp["direction"] == actual_direction:
                missed += 1
            else:
                correct += 1

        return {
            "total_rejected": len(self._rejected_plans),
            "missed_opportunities": missed,
            "correct_rejections": correct,
        }
