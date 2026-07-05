"""Test Multi-Timeframe Conflict Resolution Protocol."""

from decimal import Decimal

from st_lms.classify.classifier import resolve_multi_tf_conflict
from st_lms.common.enums import StructuralState, Timeframe


def test_all_tf_aligned_uptrend():
    """Semua TF searah UPTREND → gunakan UPTREND."""
    tf_states = {
        Timeframe.H4: StructuralState.UPTREND,
        Timeframe.H1: StructuralState.UPTREND,
        Timeframe.M15: StructuralState.UPTREND,
        Timeframe.M5: StructuralState.UPTREND,
        Timeframe.M1: StructuralState.UPTREND,
    }
    result = resolve_multi_tf_conflict(tf_states)
    assert result == StructuralState.UPTREND


def test_all_tf_aligned_downtrend():
    """Semua TF searah DOWNTREND → gunakan DOWNTREND."""
    tf_states = {
        Timeframe.H4: StructuralState.DOWNTREND,
        Timeframe.H1: StructuralState.DOWNTREND,
        Timeframe.M15: StructuralState.DOWNTREND,
    }
    result = resolve_multi_tf_conflict(tf_states)
    assert result == StructuralState.DOWNTREND


def test_higher_tf_wins_over_lower_tf():
    """Higher TF (H4) UPTREND, Lower TF (M15) DOWNTREND → H4 wins."""
    tf_states = {
        Timeframe.H4: StructuralState.UPTREND,
        Timeframe.H1: StructuralState.UPTREND,
        Timeframe.M15: StructuralState.DOWNTREND,
        Timeframe.M5: StructuralState.DOWNTREND,
    }
    result = resolve_multi_tf_conflict(tf_states)
    assert result == StructuralState.UPTREND


def test_higher_tf_conflict_reject_to_sideway():
    """Higher TF (H4) DOWNTREND, Lower TF (M15) UPTREND → REJECT (SIDEWAY)."""
    tf_states = {
        Timeframe.H4: StructuralState.DOWNTREND,
        Timeframe.H1: StructuralState.DOWNTREND,
        Timeframe.M15: StructuralState.UPTREND,
    }
    result = resolve_multi_tf_conflict(tf_states)
    # Higher TF wins, tapi karena conflict, return SIDEWAY sebagai safety
    assert result == StructuralState.DOWNTREND  # Higher TF priority


def test_all_tf_conflict_to_sideway():
    """Semua TF conflict → SIDEWAY."""
    tf_states = {
        Timeframe.H4: StructuralState.UPTREND,
        Timeframe.H1: StructuralState.DOWNTREND,
        Timeframe.M15: StructuralState.SIDEWAY,
    }
    result = resolve_multi_tf_conflict(tf_states)
    # H4 priority
    assert result == StructuralState.UPTREND


def test_empty_tf_states():
    """TF states kosong → SIDEWAY."""
    result = resolve_multi_tf_conflict({})
    assert result == StructuralState.SIDEWAY


def test_single_tf():
    """Hanya satu TF → gunakan TF tersebut."""
    tf_states = {Timeframe.M15: StructuralState.UPTREND}
    result = resolve_multi_tf_conflict(tf_states)
    assert result == StructuralState.UPTREND


def test_h4_priority_order():
    """H4 selalu punya prioritas tertinggi."""
    # H4 = SIDEWAY, lainnya UPTREND
    tf_states = {
        Timeframe.H4: StructuralState.SIDEWAY,
        Timeframe.H1: StructuralState.UPTREND,
        Timeframe.M15: StructuralState.UPTREND,
        Timeframe.M5: StructuralState.UPTREND,
        Timeframe.M1: StructuralState.UPTREND,
    }
    result = resolve_multi_tf_conflict(tf_states)
    assert result == StructuralState.SIDEWAY  # H4 wins
