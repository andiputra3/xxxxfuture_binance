"""
ST_LMS Comprehensive Dashboard
Visualisasi lengkap seluruh alur ST_LMS:
- Market Overview: Harga, Supertrend, Volatilitas
- Structure Status: Waves, Grid Levels, Market Structure
- River Opportunities: Entry/Exit signals dengan confidence
- Active Trades & Plans: Positions, Trading Plans, PnL Realtime
- System Health: Executor, Observer, Last Update
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from decimal import Decimal
import random
import time

# Import ST_LMS modules
from st_lms.common.enums import (
    Timeframe, Direction, StructuralState, StructuralGeometry,
    PositionSide, PositionState, LineStatus, WaveState,
    TradingPlanState, RiverRecommendation, RiverState,
    AuthorizationStatus, MACDBucket
)
from st_lms.models.candle import Candle
from st_lms.models.supertrend_line import SupertrendLine
from st_lms.models.supertrend_wave import SupertrendWave
from st_lms.models.structural_state import StructuralSnapshot
from st_lms.models.trading_plan import TradingPlan, PartialExit
from st_lms.models.position import Position
from st_lms.models.river_state import RiverState
from st_lms.core.telemetry import telemetry, PipelineStage

# Page configuration
st.set_page_config(
    page_title="ST_LMS Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visualization
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #2962ff;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #d1d4dc;
    }
    .metric-label {
        font-size: 12px;
        color: #787b86;
        text-transform: uppercase;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 11px;
    }
    .status-active { background-color: rgba(14, 203, 129, 0.15); color: #0ecb81; }
    .status-inactive { background-color: rgba(120, 123, 134, 0.15); color: #787b86; }
    .status-warning { background-color: rgba(240, 185, 11, 0.15); color: #f0b90b; }
    .status-danger { background-color: rgba(246, 70, 93, 0.15); color: #f6465d; }
    
    /* Hide Streamlit footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.mode = "Simulation"
    st.session_state.balance = Decimal("10000.00")
    st.session_state.equity = Decimal("10000.00")
    st.session_state.positions = []
    st.session_state.trading_plans = []
    st.session_state.waves = []
    supertrend_lines = []
    for tf in [Timeframe.M15, Timeframe.H1, Timeframe.H4]:
        for dir in [Direction.LONG, Direction.SHORT]:
            supertrend_lines.append(SupertrendLine(
                line_id=f"ST_{tf.value}_{dir.value}",
                symbol="BTCUSDT",
                timeframe=tf,
                direction=dir,
                price=Decimal(str(random.uniform(60000, 70000))),
                start_timestamp=int(time.time() * 1000) - random.randint(1000, 10000),
                end_timestamp=int(time.time() * 1000),
                candle_count=random.randint(10, 50),
                touch_count=random.randint(2, 10),
                status=LineStatus.ACTIVE if random.random() > 0.3 else LineStatus.BROKEN
            ))
    st.session_state.supertrend_lines = supertrend_lines
    st.session_state.river_opportunities = []
    st.session_state.market_structure = None
    st.session_state.last_update = datetime.now()
    st.session_state.system_status = {
        "observer": "ACTIVE",
        "executor": "READY",
        "pipeline": "RUNNING"
    }

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://img.shields.io/badge/ST_LMS-v1.0.1-blue", use_container_width=True)
    st.markdown("---")
    
    st.subheader("⚙️ Configuration")
    mode = st.selectbox(
        "Trading Mode",
        ["Simulation", "Testnet", "Live"],
        index=0
    )
    st.session_state.mode = mode
    
    symbol = st.text_input("Symbol", value="BTCUSDT")
    
    st.subheader("📈 Timeframes")
    selected_tfs = st.multiselect(
        "Active Timeframes",
        [tf.value for tf in Timeframe],
        default=["15m", "1h", "4h"]
    )
    
    st.subheader("🔄 Auto Refresh")
    auto_refresh = st.checkbox("Enable Auto Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 3)
    
    st.markdown("---")
    st.subheader("🎛️ Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Start", use_container_width=True):
            st.session_state.system_status["pipeline"] = "RUNNING"
            st.success("Pipeline started!")
    with col2:
        if st.button("⏹ Stop", use_container_width=True):
            st.session_state.system_status["pipeline"] = "STOPPED"
            st.warning("Pipeline stopped!")
    
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.positions = []
        st.session_state.trading_plans = []
        st.session_state.river_opportunities = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Trades", len(st.session_state.positions))
    st.metric("Active Plans", len([p for p in st.session_state.trading_plans if p.state == TradingPlanState.CREATED]))
    st.metric("River Signals", len(st.session_state.river_opportunities))

# ==================== HEADER ====================
st.title("🧠 ST_LMS Comprehensive Trading Dashboard")
st.markdown("**Real-time monitoring** | Supertrend • Waves • Grid • River • Execution")

# Last update indicator
last_update_str = st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"Last updated: {last_update_str} | Mode: **{mode}** | Symbol: **{symbol}**")

st.markdown("---")

# ==================== GENERATE SIMULATION DATA ====================
def generate_simulation_data():
    """Generate realistic simulation data for demonstration."""
    now = int(time.time() * 1000)
    
    # Generate candles
    candles = []
    base_price = Decimal("65000")
    for i in range(100):
        close = base_price + Decimal(str(random.uniform(-500, 500)))
        high = max(close, base_price + Decimal(str(random.uniform(0, 200))))
        low = min(close, base_price - Decimal(str(random.uniform(0, 200))))
        open = base_price + Decimal(str(random.uniform(-100, 100)))
        candles.append(Candle(
            symbol=symbol,
            timeframe=Timeframe.H4,
            timestamp=now - (100 - i) * 14400000,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=Decimal(str(random.uniform(1000, 5000)))
        ))
        base_price = close
    
    # Generate waves
    waves = []
    for i in range(3):
        waves.append(SupertrendWave(
            wave_id=f"WAVE_{i+1}",
            symbol=symbol,
            timeframe=random.choice(list(Timeframe)),
            direction=random.choice([Direction.LONG, Direction.SHORT]),
            start_line_id=f"ST_START_{i}",
            end_line_id=f"ST_END_{i}",
            amplitude=Decimal(str(random.uniform(500, 2000))),
            duration=random.randint(10, 50),
            status=random.choice([WaveState.ACTIVE, WaveState.COMPLETED, WaveState.BUILDING])
        ))
    st.session_state.waves = waves
    
    # Generate river opportunities
    opportunities = []
    for i in range(5):
        opportunities.append({
            "id": f"OPP_{i+1}",
            "type": random.choice(["ENTRY", "EXIT"]),
            "direction": random.choice([Direction.LONG, Direction.SHORT]),
            "confidence": Decimal(str(random.uniform(60, 95))),
            "price": Decimal(str(random.uniform(64000, 66000))),
            "reason": random.choice([
                "Strong momentum confirmation",
                "Support/Resistance bounce",
                "Multi-TF alignment",
                "Volume spike detected",
                "River pattern match"
            ]),
            "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 60))
        })
    st.session_state.river_opportunities = opportunities
    
    # Generate market structure
    st.session_state.market_structure = StructuralSnapshot(
        snapshot_id=f"SNAP_{now}",
        state=random.choice([StructuralState.UPTREND, StructuralState.DOWNTREND, StructuralState.SIDEWAY]),
        confidence=Decimal(str(random.uniform(70, 95))),
        geometry=random.choice([StructuralGeometry.ASCENDING, StructuralGeometry.DESCENDING, 
                               StructuralGeometry.CORRIDOR, StructuralGeometry.CONVERGING]),
        nearest_support=Decimal(str(random.uniform(63000, 64500))),
        nearest_resistance=Decimal(str(random.uniform(65500, 67000)))
    )
    
    # Generate trading plans
    plans = []
    for i in range(3):
        plans.append(TradingPlan(
            plan_id=f"PLAN_{i+1}",
            strategy=random.choice(["Trend Following", "Mean Reversion", "Breakout"]),
            direction=random.choice([Direction.LONG, Direction.SHORT]),
            entry_zone_low=Decimal(str(random.uniform(64500, 65000))),
            entry_zone_high=Decimal(str(random.uniform(65000, 65500))),
            stop_loss=Decimal(str(random.uniform(63500, 64000))),
            take_profit=Decimal(str(random.uniform(66500, 67500))),
            risk_percent=Decimal(str(random.uniform(1, 3))),
            confidence=Decimal(str(random.uniform(65, 90))),
            state=random.choice([TradingPlanState.CREATED, TradingPlanState.PENDING, 
                                TradingPlanState.ACTIVE, TradingPlanState.EXECUTED]),
            reason="Technical setup confirmed"
        ))
    st.session_state.trading_plans = plans
    
    # Update balance and equity
    st.session_state.balance = Decimal("10000.00") + Decimal(str(random.uniform(-500, 1000)))
    st.session_state.equity = st.session_state.balance + Decimal(str(random.uniform(-200, 300)))
    
    # Update last update time
    st.session_state.last_update = datetime.now()
    
    return candles

# Generate data on each run
candles = generate_simulation_data()
current_price = float(candles[-1].close) if candles else 65000

# ==================== ROW 1: MARKET OVERVIEW ====================
st.header("📊 Market Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Current Price</div>', unsafe_allow_html=True)
    price_change = random.uniform(-2, 2)
    price_color = "green" if price_change >= 0 else "red"
    st.markdown(f'<div class="metric-value" style="color: {"#0ecb81" if price_change >= 0 else "#f6465d"}">${current_price:,.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<span style="color: {"#0ecb81" if price_change >= 0 else "#f6465d"}; font-size: 14px;">{price_change:+.2f}%</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Balance</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">${float(st.session_state.balance):,.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Equity</div>', unsafe_allow_html=True)
    equity_val = float(st.session_state.equity)
    equity_color = "#0ecb81" if equity_val >= float(st.session_state.balance) else "#f6465d"
    st.markdown(f'<div class="metric-value" style="color: {equity_color}">${equity_val:,.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Unrealized PnL</div>', unsafe_allow_html=True)
    unrealized_pnl = equity_val - float(st.session_state.balance)
    pnl_color = "#0ecb81" if unrealized_pnl >= 0 else "#f6465d"
    st.markdown(f'<div class="metric-value" style="color: {pnl_color}">${unrealized_pnl:+,.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Price Chart with Supertrend
st.subheader("📈 Price Action & Supertrend")

# Create sample data for chart
df = pd.DataFrame([{
    "timestamp": datetime.fromtimestamp(c.timestamp / 1000),
    "open": float(c.open),
    "high": float(c.high),
    "low": float(c.low),
    "close": float(c.close),
    "volume": float(c.volume)
} for c in candles])

# Calculate Supertrend (simplified for demo)
df['ST_Long'] = df['close'] - df['close'].rolling(10).std() * 3
df['ST_Short'] = df['close'] + df['close'].rolling(10).std() * 3
df['ST_Direction'] = np.where(df['close'] > df['ST_Long'], 'LONG', 'SHORT')

# Create candlestick chart with Supertrend
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, row_heights=[0.7, 0.3],
                    subplot_titles=('Price & Supertrend', 'Volume'))

# Candlestick
fig.add_trace(go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'], low=df['low'], close=df['close'],
    name='Price',
    increasing_line_color='#0ecb81',
    decreasing_line_color='#f6465d'
), row=1, col=1)

# Supertrend Long
fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['ST_Long'],
    name='Supertrend Long',
    line=dict(color='#0ecb81', width=2)
), row=1, col=1)

# Supertrend Short
fig.add_trace(go.Scatter(
    x=df['timestamp'], y=df['ST_Short'],
    name='Supertrend Short',
    line=dict(color='#f6465d', width=2)
), row=1, col=1)

# Volume
colors = ['#0ecb81' if df['close'].iloc[i] > df['open'].iloc[i] else '#f6465d' for i in range(len(df))]
fig.add_trace(go.Bar(
    x=df['timestamp'], y=df['volume'],
    name='Volume',
    marker_color=colors,
    opacity=0.7
), row=2, col=1)

fig.update_layout(
    height=500,
    xaxis_rangeslider_visible=False,
    template='plotly_dark',
    showlegend=True,
    legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0.5)')
)

fig.update_yaxes(gridcolor='#2a2e39', row=1, col=1)
fig.update_yaxes(gridcolor='#2a2e39', row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# ==================== ROW 2: STRUCTURE STATUS & RIVER ====================
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🏗️ Structure Status")
    
    # Market Structure Card
    if st.session_state.market_structure:
        ms = st.session_state.market_structure
        
        # State badge
        state_colors = {
            StructuralState.UPTREND: "#0ecb81",
            StructuralState.DOWNTREND: "#f6465d",
            StructuralState.SIDEWAY: "#f0b90b"
        }
        state_color = state_colors.get(ms.state, "#787b86")
        
        st.markdown(f"""
        <div style="background-color: #1e222d; border-radius: 8px; padding: 15px; margin-bottom: 15px; border-left: 4px solid {state_color};">
            <div style="font-size: 12px; color: #787b86; text-transform: uppercase;">Market State</div>
            <div style="font-size: 20px; font-weight: bold; color: {state_color};">{ms.state.value}</div>
            <div style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #787b86; font-size: 12px;">Confidence</span>
                    <span style="color: #d1d4dc; font-size: 12px;">{float(ms.confidence):.1f}%</span>
                </div>
                <div style="background-color: #2a2e39; height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #2962ff, #0ecb81); height: 100%; width: {float(ms.confidence)}%;"></div>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 12px; color: #787b86;">
                <div><b>Geometry:</b> {ms.geometry.value}</div>
                <div><b>Support:</b> ${float(ms.nearest_support):,.2f}</div>
                <div><b>Resistance:</b> ${float(ms.nearest_resistance):,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Active Waves
    st.subheader("🌊 Active Supertrend Waves")
    if st.session_state.waves:
        waves_df = pd.DataFrame([{
            "Wave ID": w.wave_id,
            "TF": w.timeframe.value,
            "Direction": w.direction.value,
            "Amplitude": f"${float(w.amplitude):,.2f}",
            "Duration": f"{w.duration} candles",
            "Status": w.status.value
        } for w in st.session_state.waves])
        
        def color_status(status):
            colors = {
                "ACTIVE": "background-color: rgba(14, 203, 129, 0.15); color: #0ecb81;",
                "COMPLETED": "background-color: rgba(120, 123, 134, 0.15); color: #787b86;",
                "BUILDING": "background-color: rgba(240, 185, 11, 0.15); color: #f0b90b;"
            }
            return colors.get(status, "")
        
        st.dataframe(
            waves_df.style.applymap(lambda x: color_status(x) if x in ["ACTIVE", "COMPLETED", "BUILDING"] else "", subset=["Status"]),
            use_container_width=True,
            hide_index=True
        )
    
    # Supertrend Lines
    st.subheader("📏 Supertrend Lines")
    if st.session_state.supertrend_lines:
        lines_data = []
        for line in st.session_state.supertrend_lines[:6]:  # Show first 6
            lines_data.append({
                "Timeframe": line.timeframe.value,
                "Direction": line.direction.value,
                "Price": f"${float(line.price):,.2f}",
                "Touches": line.touch_count,
                "Status": line.status.value
            })
        st.dataframe(pd.DataFrame(lines_data), use_container_width=True, hide_index=True)

with col2:
    st.header("🌊 River Opportunities")
    
    # Active Opportunities
    if st.session_state.river_opportunities:
        opp_df = pd.DataFrame([{
            "ID": opp['id'],
            "Type": opp['type'],
            "Direction": opp['direction'].value,
            "Confidence": f"{float(opp['confidence']):.1f}%",
            "Price": f"${float(opp['price']):,.2f}",
            "Time": opp['timestamp'].strftime("%H:%M"),
            "Reason": opp['reason'][:30] + "..." if len(opp['reason']) > 30 else opp['reason']
        } for opp in st.session_state.river_opportunities])
        
        # Color by confidence
        def confidence_color(conf_str):
            conf = float(conf_str.replace('%', ''))
            if conf >= 80:
                return "background-color: rgba(14, 203, 129, 0.15); color: #0ecb81;"
            elif conf >= 60:
                return "background-color: rgba(240, 185, 11, 0.15); color: #f0b90b;"
            else:
                return "background-color: rgba(246, 70, 93, 0.15); color: #f6465d;"
        
        st.dataframe(
            opp_df.style.applymap(confidence_color, subset=["Confidence"]),
            use_container_width=True,
            hide_index=True
        )
    
    # River Learning Summary
    st.subheader("🧠 River Learning Status")
    river_summary = telemetry.get_river_learning_summary()
    
    rec_colors = {
        "ALLOW": "#0ecb81",
        "CAUTION": "#f0b90b",
        "REJECT": "#f6465d",
        "UNKNOWN": "#787b86"
    }
    rec_color = rec_colors.get(river_summary.get("last_recommendation", "UNKNOWN"), "#787b86")
    
    st.markdown(f"""
    <div style="background-color: #1e222d; border-radius: 8px; padding: 15px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <div style="font-size: 11px; color: #787b86;">Recommendation</div>
                <div style="font-size: 18px; font-weight: bold; color: {rec_color};">{river_summary.get('last_recommendation', 'UNKNOWN')}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #787b86;">Confidence</div>
                <div style="font-size: 18px; font-weight: bold; color: #d1d4dc;">{river_summary.get('confidence', 0):.1f}%</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #787b86;">Total Learned</div>
                <div style="font-size: 18px; font-weight: bold; color: #d1d4dc;">{river_summary.get('total_learned_trades', 0)}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #787b86;">Opportunity Cost</div>
                <div style="font-size: 18px; font-weight: bold; color: #f7931a;">${river_summary.get('opportunity_cost', 0):,.2f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== ROW 3: TRADING PLANS & POSITIONS ====================
st.header("💼 Active Trading Plans & Positions")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Trading Plans")
    if st.session_state.trading_plans:
        plans_data = []
        for plan in st.session_state.trading_plans:
            plans_data.append({
                "Plan ID": plan.plan_id,
                "Strategy": plan.strategy,
                "Direction": plan.direction.value,
                "Entry Zone": f"${float(plan.entry_zone_low):,.0f}-${float(plan.entry_zone_high):,.0f}",
                "SL/TP": f"${float(plan.stop_loss):,.0f}/${float(plan.take_profit):,.0f}",
                "Risk": f"{float(plan.risk_percent):.1f}%",
                "Confidence": f"{float(plan.confidence):.1f}%",
                "State": plan.state.value
            })
        
        plans_df = pd.DataFrame(plans_data)
        
        # Color by state
        def state_color(state):
            colors = {
                "CREATED": "background-color: rgba(41, 98, 255, 0.15); color: #2962ff;",
                "PENDING": "background-color: rgba(240, 185, 11, 0.15); color: #f0b90b;",
                "ACTIVE": "background-color: rgba(14, 203, 129, 0.15); color: #0ecb81;",
                "EXECUTED": "background-color: rgba(120, 123, 134, 0.15); color: #787b86;"
            }
            return colors.get(state, "")
        
        st.dataframe(
            plans_df.style.applymap(state_color, subset=["State"]),
            use_container_width=True,
            hide_index=True
        )

with col2:
    st.subheader("📊 Active Positions")
    if st.session_state.positions:
        pos_data = []
        for pos in st.session_state.positions:
            current_pnl = random.uniform(-100, 150)  # Simulated
            pos_data.append({
                "Position ID": pos.position_id,
                "Side": pos.side.value,
                "Entry": f"${float(pos.entry_price):,.2f}",
                "Qty": f"{float(pos.quantity):.4f}",
                "PnL": f"${current_pnl:+,.2f}",
                "State": pos.state.value
            })
        pos_df = pd.DataFrame(pos_data)
        st.dataframe(pos_df, use_container_width=True, hide_index=True)
    else:
        st.info("No active positions")
        
        # Quick action buttons
        st.markdown("### ⚡ Quick Actions")
        qc1, qc2 = st.columns(2)
        with qc1:
            if st.button("📈 Place LONG", use_container_width=True, type="primary"):
                st.toast("LONG order simulated!", icon="✅")
        with qc2:
            if st.button("📉 Place SHORT", use_container_width=True, type="primary"):
                st.toast("SHORT order simulated!", icon="✅")

# ==================== ROW 4: SYSTEM HEALTH ====================
st.header("🔧 System Health")

health_col1, health_col2, health_col3 = st.columns(3)

with health_col1:
    st.markdown("### Observer Status")
    obs_status = st.session_state.system_status["observer"]
    obs_color = "#0ecb81" if obs_status == "ACTIVE" else "#f6465d"
    st.markdown(f"""
    <div style="background-color: #1e222d; border-radius: 8px; padding: 15px; text-align: center;">
        <div style="font-size: 32px;">👁️</div>
        <div style="font-size: 18px; font-weight: bold; color: {obs_color}; margin-top: 10px;">{obs_status}</div>
        <div style="font-size: 11px; color: #787b86; margin-top: 5px;">Monitoring market data</div>
    </div>
    """, unsafe_allow_html=True)

with health_col2:
    st.markdown("### Executor Status")
    exec_status = st.session_state.system_status["executor"]
    exec_color = "#0ecb81" if exec_status == "READY" else "#f0b90b"
    st.markdown(f"""
    <div style="background-color: #1e222d; border-radius: 8px; padding: 15px; text-align: center;">
        <div style="font-size: 32px;">⚡</div>
        <div style="font-size: 18px; font-weight: bold; color: {exec_color}; margin-top: 10px;">{exec_status}</div>
        <div style="font-size: 11px; color: #787b86; margin-top: 5px;">Order execution engine</div>
    </div>
    """, unsafe_allow_html=True)

with health_col3:
    st.markdown("### Pipeline Status")
    pipe_status = st.session_state.system_status["pipeline"]
    pipe_color = "#0ecb81" if pipe_status == "RUNNING" else "#f6465d"
    st.markdown(f"""
    <div style="background-color: #1e222d; border-radius: 8px; padding: 15px; text-align: center;">
        <div style="font-size: 32px;">🔄</div>
        <div style="font-size: 18px; font-weight: bold; color: {pipe_color}; margin-top: 10px;">{pipe_status}</div>
        <div style="font-size: 11px; color: #787b86; margin-top: 5px;">13-layer pipeline</div>
    </div>
    """, unsafe_allow_html=True)

# Pipeline Activity Log
st.subheader("📜 Recent Pipeline Activity")
recent_events = telemetry.get_recent_events(10)

if recent_events:
    events_df = pd.DataFrame([{
        "Time": datetime.fromtimestamp(e['timestamp']).strftime("%H:%M:%S"),
        "Stage": e['stage'],
        "Action": e['action'],
        "Status": e['status']
    } for e in recent_events])
    
    # Color by status
    def status_style(status):
        colors = {
            "SUCCESS": "color: #0ecb81;",
            "WARNING": "color: #f0b90b;",
            "ERROR": "color: #f6465d;",
            "REJECTED": "color: #f6465d;"
        }
        return colors.get(status, "")
    
    st.dataframe(
        events_df.style.applymap(status_style, subset=["Status"]),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No pipeline activity yet")

# Last Update Footer
st.markdown("---")
st.caption(f"**Dashboard Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Mode:** {mode} | **Version:** 1.0.1")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
