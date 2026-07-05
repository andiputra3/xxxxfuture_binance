from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

from st_lms.classify.classifier import StateClassifier
from st_lms.common.enums import Timeframe
from st_lms.darwin.darwin_engine import DarwinEngine
from st_lms.models.darwin_recommendation import DarwinRecommendation
from st_lms.execute.order_manager import OrderManager
from st_lms.execute.simulation_executor import SimulationExecutor
from st_lms.measure.orchestrator import MeasureOrchestrator
from st_lms.multi_timeframe_structural_engine.engine import MultiTimeframeStructuralEngine
from st_lms.observe.observer import Observer
from st_lms.models.candle import Candle
from st_lms.models.market_snapshot import MarketSnapshot
from st_lms.models.indicator_snapshot import IndicatorSnapshot
from st_lms.models.structure_snapshot import StructureSnapshot
from st_lms.models.market_understanding import MarketUnderstanding
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import TradingPlan
from st_lms.models.learning_snapshot import LearningSnapshot
from st_lms.models.position import Position
from st_lms.models.authorization import Authorization
from st_lms.preserve.preserver import SnapshotRepository
from st_lms.remember.memory import StructureMemory
from st_lms.remember.historical_repository import HistoricalStructureRepository
from st_lms.select.selector import Selector
from st_lms.understand.geometry import GeometryAnalyzer
from st_lms.trading_plan.plan_manager import PlanManager
from st_lms.risk.risk_manager import RiskManager
from st_lms.river.river_learning import RiverLearning
from st_lms.river.river_review import RiverReview
from st_lms.river.shared_learning_repository import SharedLearningRepository
from st_lms.improve import improve


@dataclass
class PipelineResult:
    """Hasil dari satu siklus pipeline penuh."""
    market_snapshot: Optional[MarketSnapshot]
    indicator_snapshot: Optional[IndicatorSnapshot]
    structure_snapshot: Optional[StructureSnapshot]
    understanding: Optional[MarketUnderstanding]
    structural_snapshot: Optional[StructuralSnapshot]
    trading_plan: Optional[TradingPlan]
    authorization: Optional[Authorization]
    position_id: Optional[str]
    river_learning: LearningSnapshot
    darwin_recommendation: Optional[DarwinRecommendation]
    position_size: Decimal = Decimal("0")
    parent_snapshot_ids: List[str] = field(default_factory=list)


class Pipeline:
    """Pipeline ST_LMS — C001 sampai C012 + Post-Trade.

    Sesuai Constitution Final v1.0.
    5 Prinsip Mutlak enforced:
    1. Structure First: semua dari Supertrend Line
    2. Plan Before Trade: TradingPlan wajib sebelum execute
    3. Review Before Authorize: RiverReview wajib sebelum authorize
    4. Learn After Result: improve() setelah trade closed
    5. Improve Without Touching Core: Darwin tidak sentuh formula ATR/ST/MACD
    """

    def __init__(self, observer: Observer, initial_balance: Decimal = Decimal("10000")) -> None:
        # C001
        self._observer = observer
        # C002
        self._measure = MeasureOrchestrator()
        # C003
        self._engine = MultiTimeframeStructuralEngine()
        # C004
        self._preserver = SnapshotRepository()
        # C005
        self._hist_repo = HistoricalStructureRepository()
        self._memory = StructureMemory(self._hist_repo)
        # C006
        self._selector = Selector()
        # C007
        self._geometry = GeometryAnalyzer()
        # C008
        self._classifier = StateClassifier()
        # C009/C010/C011
        self._plan_manager = PlanManager()
        # C012
        self._executor = SimulationExecutor()
        self._order_manager = OrderManager()
        # Risk
        self._risk = RiskManager(initial_balance)
        # Post-Trade
        self._river = RiverLearning()
        self._review = RiverReview()
        self._shared_repo = SharedLearningRepository()
        self._darwin = DarwinEngine()

    def get_position(self, position_id: str) -> Optional[Position]:
        """Public accessor for BacktestEngine."""
        return self._executor.get_position(position_id)

    def get_balance(self) -> Decimal:
        """Public accessor for BacktestEngine."""
        return self._risk.balance

    def set_balance(self, balance: Decimal) -> None:
        """Public accessor for BacktestEngine."""
        self._risk.set_balance(balance)

    def run(self, symbol: str, timeframes: List[Timeframe],
            candles: Dict[Timeframe, List[Candle]],
            risk_method: str = "fixed_fraction") -> PipelineResult:
        """Jalankan pipeline penuh dari C001 ke Post-Trade.

        Args:
            symbol: Pasangan trading (e.g. BTCUSDT)
            timeframes: Daftar timeframe
            candles: Data candle per timeframe
            risk_method: "fixed_fraction" atau "kelly"

        Returns:
            PipelineResult dengan semua output stage
        """
        # ── C001: Observe ──
        market_snap = self._observer.observe(symbol, timeframes, candle_limit=100)
        self._preserver.store_market(market_snap)
        snap_ids: List[str] = [market_snap.snapshot_id]

        # ── C002: Measure ──
        indicator_snap = self._measure.measure(market_snap, candles)
        self._preserver.store_indicators(indicator_snap, snap_ids)
        snap_ids.append(indicator_snap.snapshot_id)

        # ── C003: Engine ──
        struct_snap = self._engine.process(symbol, candles)

        # ── C004: Preserve (dengan harga aktual) ──
        current_price = market_snap.candle.close
        self._preserver.store_structure(struct_snap, current_price, snap_ids)
        evaluated = self._preserver.evaluate_lines(struct_snap, current_price)

        # ── C005: Remember (append-only) ──
        self._memory.store(evaluated)
        ctx = self._memory.find_similar(evaluated)

        # ── C006: Select ──
        candidate = self._selector.select_candidate(evaluated, ctx)
        if candidate is None:
            return PipelineResult(
                market_snapshot=market_snap,
                indicator_snapshot=indicator_snap,
                structure_snapshot=struct_snap,
                understanding=None,
                structural_snapshot=None,
                trading_plan=None,
                authorization=None,
                position_id=None,
                river_learning=self._river.get_snapshot(),
                darwin_recommendation=None,
                parent_snapshot_ids=snap_ids,
            )

        # ── C007: Understand ──
        understanding = self._geometry.analyze(candidate)
        snap_ids.append(understanding.snapshot_id)

        # ── C008: Classify ──
        structural = self._classifier.classify(understanding, candidate)
        snap_ids.append(structural.snapshot_id)

        # ── C009: Trading Plan ──
        plan = self._plan_manager.create_and_validate(structural)
        if plan is None:
            return PipelineResult(
                market_snapshot=market_snap,
                indicator_snapshot=indicator_snap,
                structure_snapshot=struct_snap,
                understanding=understanding,
                structural_snapshot=structural,
                trading_plan=None,
                authorization=None,
                position_id=None,
                river_learning=self._river.get_snapshot(),
                darwin_recommendation=None,
                parent_snapshot_ids=snap_ids,
            )

        # ── C010: River Plan Review dengan Shared Learning pattern matching ──
        learning = self._river.get_snapshot()
        river_state = self._review.review(plan, learning, self._shared_repo)

        # ── C011: Authorize (via PlanManager → AuthorizationGateway) ──
        auth = self._plan_manager.authorize(plan, river_state.recommendation)

        # ── C012: Execute dengan RiskManager + OrderManager ──
        pos_id: Optional[str] = None
        pos_size = Decimal("0")

        if auth.status.value == "APPROVED":
            # Hitung position size via RiskManager
            all_outcomes = self._shared_repo.get_all_outcomes()
            pos_size = self._risk.compute_position(plan, all_outcomes if all_outcomes else None, risk_method)

            # Execute via OrderManager (MARKET order) + RiskManager position size
            order = self._order_manager.place_market(plan, pos_size)
            if order.state == "FILLED":
                pos_id = self._executor.execute(plan, pos_size)
                if pos_id:
                    pos = self._executor.simulate_price(pos_id, current_price)
                    if pos is not None and pos.state.value == "CLOSED":
                        improve(self._river, pos, current_price, "SL/TP", self._shared_repo)
        else:
            # Rejected plan → Opportunity Cost recording
            self._shared_repo.record_rejected_plan(
                plan.plan_id, auth.reason, auth.confidence, plan.direction.value
            )

        # ── Post-Trade: Darwin ──
        darwin_rec = self._darwin.optimize(self._shared_repo, self._river.get_snapshot(), structural.state)

        return PipelineResult(
            market_snapshot=market_snap,
            indicator_snapshot=indicator_snap,
            structure_snapshot=struct_snap,
            understanding=understanding,
            structural_snapshot=structural,
            trading_plan=plan,
            authorization=auth,
            position_id=pos_id,
            river_learning=self._river.get_snapshot(),
            darwin_recommendation=darwin_rec,
            position_size=pos_size,
            parent_snapshot_ids=snap_ids,
        )
