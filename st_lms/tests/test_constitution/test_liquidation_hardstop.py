"""Test Liquidation Hard-Stop di AuthorizationGateway."""

from decimal import Decimal

from st_lms.authorize.authorization_gateway import AuthorizationGateway
from st_lms.common.enums import Direction, RiverRecommendation, TradingPlanState
from st_lms.models.trading_plan import TradingPlan
from st_lms.utils.helpers import generate_plan_id


def test_liquidation_hardstop_long_sl_above_liquidation():
    """LONG trade dengan SL di atas liquidation price harus APPROVED."""
    gateway = AuthorizationGateway()
    plan = TradingPlan(
        plan_id=generate_plan_id(),
        strategy="TEST_LONG",
        direction=Direction.LONG,
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("101"),
        stop_loss=Decimal("95"),  # SL di 95
        take_profit=Decimal("110"),
        risk_percent=Decimal("2"),
        confidence=Decimal("70"),
        state=TradingPlanState.READY,
        reason="Test",
        liquidation_price=Decimal("90"),  # Liquidation di 90 (SL > liq)
    )
    result = gateway.authorize(plan, RiverRecommendation.ALLOW, enable_liquidation_check=True)
    assert result.status.value == "APPROVED"


def test_liquidation_hardstop_long_sl_below_liquidation():
    """LONG trade dengan SL di bawah liquidation price harus REJECTED."""
    gateway = AuthorizationGateway()
    plan = TradingPlan(
        plan_id=generate_plan_id(),
        strategy="TEST_LONG",
        direction=Direction.LONG,
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("101"),
        stop_loss=Decimal("88"),  # SL di 88 (bahaya!)
        take_profit=Decimal("110"),
        risk_percent=Decimal("2"),
        confidence=Decimal("70"),
        state=TradingPlanState.READY,
        reason="Test",
        liquidation_price=Decimal("90"),  # Liquidation di 90
    )
    result = gateway.authorize(plan, RiverRecommendation.ALLOW, enable_liquidation_check=True)
    assert result.status.value == "REJECTED"
    assert "LIQUIDATION_RISK" in result.reason


def test_liquidation_hardstop_short_sl_below_liquidation():
    """SHORT trade dengan SL di bawah liquidation price harus APPROVED."""
    gateway = AuthorizationGateway()
    plan = TradingPlan(
        plan_id=generate_plan_id(),
        strategy="TEST_SHORT",
        direction=Direction.SHORT,
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("101"),
        stop_loss=Decimal("105"),  # SL di 105
        take_profit=Decimal("90"),
        risk_percent=Decimal("2"),
        confidence=Decimal("70"),
        state=TradingPlanState.READY,
        reason="Test",
        liquidation_price=Decimal("110"),  # Liquidation di 110
    )
    result = gateway.authorize(plan, RiverRecommendation.ALLOW, enable_liquidation_check=True)
    assert result.status.value == "APPROVED"


def test_liquidation_hardstop_short_sl_above_liquidation():
    """SHORT trade dengan SL di atas liquidation price harus REJECTED."""
    gateway = AuthorizationGateway()
    plan = TradingPlan(
        plan_id=generate_plan_id(),
        strategy="TEST_SHORT",
        direction=Direction.SHORT,
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("101"),
        stop_loss=Decimal("115"),  # SL di 115 (bahaya!)
        take_profit=Decimal("90"),
        risk_percent=Decimal("2"),
        confidence=Decimal("70"),
        state=TradingPlanState.READY,
        reason="Test",
        liquidation_price=Decimal("110"),  # Liquidation di 110
    )
    result = gateway.authorize(plan, RiverRecommendation.ALLOW, enable_liquidation_check=True)
    assert result.status.value == "REJECTED"
    assert "LIQUIDATION_RISK" in result.reason


def test_liquidation_check_disabled():
    """Liquidation check bisa dimatikan untuk backtest/simulasi."""
    gateway = AuthorizationGateway()
    plan = TradingPlan(
        plan_id=generate_plan_id(),
        strategy="TEST_LONG",
        direction=Direction.LONG,
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("101"),
        stop_loss=Decimal("88"),  # SL di bawah liquidation
        take_profit=Decimal("110"),
        risk_percent=Decimal("2"),
        confidence=Decimal("70"),
        state=TradingPlanState.READY,
        reason="Test",
        liquidation_price=Decimal("90"),
    )
    # Dengan enable_liquidation_check=False, harus APPROVED
    result = gateway.authorize(plan, RiverRecommendation.ALLOW, enable_liquidation_check=False)
    assert result.status.value == "APPROVED"


def test_no_liquidation_price_in_plan():
    """Jika liquidation_price = 0, check dilewati."""
    gateway = AuthorizationGateway()
    plan = TradingPlan(
        plan_id=generate_plan_id(),
        strategy="TEST_LONG",
        direction=Direction.LONG,
        entry_zone_low=Decimal("100"),
        entry_zone_high=Decimal("101"),
        stop_loss=Decimal("95"),
        take_profit=Decimal("110"),
        risk_percent=Decimal("2"),
        confidence=Decimal("70"),
        state=TradingPlanState.READY,
        reason="Test",
        liquidation_price=Decimal("0"),  # Tidak ada liquidation price
    )
    result = gateway.authorize(plan, RiverRecommendation.ALLOW, enable_liquidation_check=True)
    assert result.status.value == "APPROVED"
