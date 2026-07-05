from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.models.learning_snapshot import TradeOutcome


@dataclass(slots=True, frozen=True)
class RejectedOpportunity:
    """Record of a rejected trading plan that became an opportunity (or correct rejection)."""
    
    plan_id: str
    timestamp: int
    direction: str
    reason: str
    entry_price: Decimal
    actual_direction: str = ""  # filled after market moves
    price_movement: Decimal = Decimal("0")  # % movement after rejection
    was_missed_opportunity: bool = False  # True if we should have taken it
    confidence_at_rejection: Decimal = Decimal("0")


@dataclass(slots=True)
class OpportunityLearning:
    """Opportunity Cost Tracking — belajar dari trade yang DITOLAK.
    
    Mencatat semua trading plan yang ditolak oleh Authorize, lalu menganalisis:
    - Apakah penolakan itu benar? (harga bergerak berlawanan → correct rejection)
    - Apakah kita melewatkan peluang? (harga bergerak searah → missed opportunity)
    
    Output: Pattern analisis untuk memperbaiki gate authorization di masa depan.
    """
    
    _rejected_plans: List[RejectedOpportunity] = field(default_factory=list)
    _missed_count: int = 0
    _correct_rejection_count: int = 0
    
    def record_rejection(
        self,
        plan_id: str,
        timestamp: int,
        direction: str,
        reason: str,
        entry_price: Decimal,
        confidence: Decimal,
    ) -> None:
        """Catat rencana trading yang ditolak."""
        opportunity = RejectedOpportunity(
            plan_id=plan_id,
            timestamp=timestamp,
            direction=direction,
            reason=reason,
            entry_price=entry_price,
            confidence_at_rejection=confidence,
        )
        self._rejected_plans.append(opportunity)
    
    def update_outcome(self, plan_id: str, current_price: Decimal, market_direction: str) -> None:
        """Update hasil dari penolakan — apakah ini missed opportunity atau correct rejection?
        
        Args:
            plan_id: ID dari rencana yang ditolak
            current_price: Harga pasar saat ini (setelah penolakan)
            market_direction: Arah pergerakan pasar setelah penolakan ("LONG" atau "SHORT")
        """
        for i, opp in enumerate(self._rejected_plans):
            if opp.plan_id == plan_id and not opp.actual_direction:
                # Hitung price movement
                if opp.direction == "LONG":
                    price_move = (current_price - opp.entry_price) / opp.entry_price * Decimal("100")
                else:  # SHORT
                    price_move = (opp.entry_price - current_price) / opp.entry_price * Decimal("100")
                
                # Tentukan apakah ini missed opportunity
                was_missed = (opp.direction == market_direction)
                
                self._rejected_plans[i] = RejectedOpportunity(
                    plan_id=opp.plan_id,
                    timestamp=opp.timestamp,
                    direction=opp.direction,
                    reason=opp.reason,
                    entry_price=opp.entry_price,
                    actual_direction=market_direction,
                    price_movement=price_move,
                    was_missed_opportunity=was_missed,
                    confidence_at_rejection=opp.confidence_at_rejection,
                )
                
                if was_missed:
                    self._missed_count += 1
                else:
                    self._correct_rejection_count += 1
                break
    
    def get_missed_opportunity_rate(self, reason: Optional[str] = None) -> float:
        """Hitung persentase missed opportunity secara global atau per reason.
        
        Returns:
            Float 0.0-1.0 menunjukkan seberapa sering kita melewatkan peluang
        """
        if not self._rejected_plans:
            return 0.0
        
        filtered = self._rejected_plans
        if reason:
            filtered = [p for p in self._rejected_plans if p.reason == reason and p.actual_direction]
        
        if not filtered:
            return 0.0
        
        missed = sum(1 for p in filtered if p.was_missed_opportunity)
        return missed / len(filtered)
    
    def get_analysis(self) -> Dict:
        """Dapatkan analisis lengkap opportunity cost.
        
        Returns:
            {
                "total_rejected": int,
                "missed_opportunities": int,
                "correct_rejections": int,
                "missed_rate": float,
                "by_reason": {reason: {"missed": int, "correct": int, "rate": float}},
            }
        """
        by_reason: Dict[str, Dict] = {}
        
        for opp in self._rejected_plans:
            if not opp.actual_direction:
                continue
            
            reason = opp.reason
            if reason not in by_reason:
                by_reason[reason] = {"missed": 0, "correct": 0, "total": 0}
            
            by_reason[reason]["total"] += 1
            if opp.was_missed_opportunity:
                by_reason[reason]["missed"] += 1
            else:
                by_reason[reason]["correct"] += 1
        
        # Hitung rate per reason
        for reason, data in by_reason.items():
            data["rate"] = data["missed"] / data["total"] if data["total"] > 0 else 0.0
        
        total_evaluated = sum(1 for p in self._rejected_plans if p.actual_direction)
        
        return {
            "total_rejected": len(self._rejected_plans),
            "missed_opportunities": self._missed_count,
            "correct_rejections": self._correct_rejection_count,
            "missed_rate": self._missed_count / total_evaluated if total_evaluated > 0 else 0.0,
            "by_reason": by_reason,
        }
    
    def get_patterns_to_relax(self, threshold: float = 0.7) -> List[str]:
        """Identifikasi rejection reasons yang terlalu ketat (missed rate > threshold).
        
        Args:
            threshold: Jika missed rate > threshold, reason ini perlu direlaksasi
            
        Returns:
            List of reasons yang perlu direlaksasi
        """
        analysis = self.get_analysis()
        patterns = []
        
        for reason, data in analysis["by_reason"].items():
            if data["total"] >= 5 and data["rate"] > threshold:  # Minimal 5 sampel
                patterns.append(reason)
        
        return patterns
    
    def count(self) -> int:
        """Total rejected plans yang tercatat."""
        return len(self._rejected_plans)
