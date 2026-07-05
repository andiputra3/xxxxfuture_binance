"""
ST_LMS Live Dashboard
Features:
- Backtest mode
- Live Simulation mode (auto-refresh every 3 seconds)
- Full pipeline activity monitoring
- River & Darwin learning
- Rejected plans (Opportunity Cost)
"""

import streamlit as st
import time
import pandas as pd
import plotly.express as px
from decimal import Decimal
from datetime import datetime

from st_lms.common.enums import Timeframe
from st_lms.models.candle import Candle
from st_lms.observe.simulation_observer import SimulationObserver
from st_lms.pipeline import Pipeline
from st_lms.backtest.engine import BacktestEngine


st.set_page_config(page_title="ST_LMS Dashboard", layout="wide")
st.title("🧠 ST_LMS Trading Bot — Live Dashboard")
st.markdown("**13-Layer Pipeline** | Real-time monitoring, learning & decisions")

# ==================== SIDEBAR ====================
st.sidebar.header("Mode")
mode = st.sidebar.radio("Pilih Mode", ["Backtest", "Live Simulation"])

if mode == "Live Simulation":
    refresh_interval = st.sidebar.slider("Refresh Interval (detik)", 2, 10, 3)
    st.sidebar.warning("Live Simulation berjalan terus. Refresh halaman untuk stop.")

st.sidebar.header("Settings")
initial_balance = st.sidebar.number_input("Initial Balance", value=10000, step=1000)

# ==================== DATA GENERATOR ====================
@st.cache_data
def generate_base_candles(n=200):
    candles = []
    for i in range(n):
        close = Decimal("100") + Decimal(i) * Decimal("0.5")
        candles.append(Candle(
            "BTCUSDT", Timeframe.H4, i * 14400000,
            close - Decimal("0.1"),
            close * Decimal("1.01"),
            close * Decimal("0.99"),
            close,
            Decimal("1000")
        ))
    return {Timeframe.H4: candles}

base_candles = generate_base_candles()

# ==================== BACKTEST MODE ====================
if mode == "Backtest":
    if st.button("▶ Run Backtest"):
        with st.spinner("Running backtest..."):
            engine = BacktestEngine(initial_balance=Decimal(str(initial_balance)))
            result = engine.run("BTCUSDT", base_candles, step=1)

        st.success("Backtest selesai!")

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Trades", result.total_trades)
        c2.metric("Rejected", result.rejected_count)
        c3.metric("Final Balance", f"${result.final_balance:.2f}")
        c4.metric("Win Rate", f"{result.metrics.win_rate:.1%}")

        # Equity Curve
        equity_df = pd.DataFrame({"Step": range(len(result.equity_curve)), 
                                  "Equity": [float(e) for e in result.equity_curve]})
        fig = px.line(equity_df, x="Step", y="Equity", title="Equity Curve")
        st.plotly_chart(fig, use_container_width=True)

        # Trade Log
        if result.trades:
            trades_df = pd.DataFrame([{
                "Timestamp": t.timestamp,
                "Direction": t.direction,
                "Entry": float(t.entry_price),
                "Exit": float(t.exit_price),
                "PnL": float(t.pnl),
                "PnL%": float(t.pnl_percent),
            } for t in result.trades])
            st.dataframe(trades_df)

# ==================== LIVE SIMULATION MODE ====================
else:
    st.header("🔴 Live Simulation Mode")
    st.info("Bot akan terus berjalan dan memperbarui data setiap beberapa detik.")

    # Placeholder untuk live update
    placeholder = st.empty()

    # Inisialisasi state
    if "live_pipeline" not in st.session_state:
        observer = SimulationObserver()
        st.session_state.live_pipeline = Pipeline(observer, initial_balance=Decimal(str(initial_balance)))
        st.session_state.live_equity = [float(initial_balance)]
        st.session_state.live_trades = []
        st.session_state.candle_index = 50  # mulai dari candle ke-50

    pipeline = st.session_state.live_pipeline
    equity = st.session_state.live_equity
    trades = st.session_state.live_trades
    idx = st.session_state.candle_index

    # Loop simulasi
    while True:
        with placeholder.container():
            # Ambil window candle terbaru
            current_window = {Timeframe.H4: base_candles[Timeframe.H4][:idx+1]}
            result = pipeline.run("BTCUSDT", [Timeframe.H4], current_window)

            # Update equity
            equity.append(float(pipeline.get_balance()))

            # Update trade jika ada
            if result.position_id and result.trading_plan:
                # Simulasi sederhana: catat trade jika ada
                pass

            # Tampilan Dashboard
            st.subheader(f"Cycle #{idx}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Current Balance", f"${pipeline.get_balance():.2f}")
            col2.metric("Last Auth", str(result.authorization.status) if result.authorization else "N/A")
            col3.metric("Last Plan", result.trading_plan.strategy if result.trading_plan else "None")

            # Pipeline Stages
            st.markdown("### Pipeline Stages")
            stages = {
                "C001 Observe": "✅",
                "C002 Measure": "✅",
                "C003 Engine": "✅",
                "C004 Preserve": "✅",
                "C005 Remember": "✅",
                "C006 Select": "✅" if result.structure_snapshot else "⏭️",
                "C007 Understand": "✅" if result.understanding else "⏭️",
                "C008 Classify": "✅" if result.structural_snapshot else "⏭️",
                "C009 Trading Plan": "✅" if result.trading_plan else "⏭️",
                "C010 River Review": "✅",
                "C011 Authorize": "✅" if result.authorization else "⏭️",
                "C012 Execute": "✅" if result.position_id else "⏭️",
            }

            for stage, status in stages.items():
                st.write(f"{status} {stage}")

            # Learning
            if show_learning:
                st.markdown("### 🧠 Learning Status")
                learning = result.river_learning
                st.write(f"**Total Trades Learned**: {learning.total_trades}")
                st.write(f"**Win Rate**: {learning.win_rate:.1%}")
                st.write(f"**Profit Factor**: {learning.profit_factor:.2f}")

            # Rejected Plans
            rejected = pipeline._shared_repo.get_rejected_plans()
            if rejected:
                st.markdown("### 🚫 Recent Rejections")
                st.dataframe(pd.DataFrame(rejected[-5:]))

            # Equity Curve (live)
            equity_df = pd.DataFrame({"Step": range(len(equity)), "Equity": equity})
            fig = px.line(equity_df, x="Step", y="Equity", title="Live Equity Curve")
            st.plotly_chart(fig, use_container_width=True, key=f"equity_{idx}")

        # Update state
        st.session_state.candle_index = idx + 1
        st.session_state.live_equity = equity

        # Sleep & rerun
        time.sleep(refresh_interval)
        st.rerun()
