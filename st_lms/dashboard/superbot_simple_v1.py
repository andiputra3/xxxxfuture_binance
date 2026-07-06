"""
SuperBot Simple v1 - Simplified Dashboard with Expandable Tables
Focus: Clean table-based UI with full pipeline traceability
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
DB_PATH = "st_lms/superbot.db"
WIB_OFFSET_HOURS = 7

st.set_page_config(
    page_title="SuperBot Simple v1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def convert_utc_to_wib(utc_timestamp):
    """Convert UTC timestamp to WIB (UTC+7)."""
    if utc_timestamp is None or pd.isna(utc_timestamp):
        return "N/A"
    
    try:
        if isinstance(utc_timestamp, str):
            # Handle ISO format string
            if 'T' in utc_timestamp:
                dt = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(utc_timestamp, "%Y-%m-%d %H:%M:%S")
        elif isinstance(utc_timestamp, datetime):
            dt = utc_timestamp
        else:
            return str(utc_timestamp)
        
        # Add 7 hours for WIB
        wib_time = dt + timedelta(hours=WIB_OFFSET_HOURS)
        return wib_time.strftime("%Y-%m-%d %H:%M:%S WIB")
    except Exception as e:
        return str(utc_timestamp)

def convert_timestamps_in_df(df, timestamp_columns):
    """Convert timestamp columns in DataFrame to WIB."""
    if df is None or df.empty:
        return df
    
    df_copy = df.copy()
    for col in timestamp_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(convert_utc_to_wib)
    return df_copy

def get_db_connection():
    """Get SQLite database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def fetch_table_data(query, params=None):
    """Fetch data from database and return as DataFrame."""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def format_pipeline_stages(row):
    """Format pipeline stages as ✅/❌ indicators."""
    stages = []
    stage_mapping = [
        ("C001", "Observe"),
        ("C002", "Measure"),
        ("C003", "Engine"),
        ("C004", "Preserve"),
        ("C005", "Remember"),
        ("C006", "Select"),
        ("C007", "Understand"),
        ("C008", "Classify"),
        ("C009", "TradingPlan"),
        ("C010", "RiverReview"),
        ("C011", "Authorize"),
        ("C012", "Execute"),
    ]
    
    for stage_code, stage_name in stage_mapping:
        col_name = f"{stage_code}_{stage_name}"
        if col_name in row:
            status = "✅" if row[col_name] else "❌"
            stages.append(f"{stage_code}: {status}")
        else:
            stages.append(f"{stage_code}: ❓")
    
    return " | ".join(stages)

# ============================================================================
# SIDEBAR - GLOBAL FILTERS
# ============================================================================

st.sidebar.title("🔍 Filters")

# Symbol filter
all_symbols = fetch_table_data("SELECT DISTINCT symbol FROM pipeline_traces ORDER BY symbol")
symbol_list = all_symbols['symbol'].tolist() if not all_symbols.empty else ['BTCUSDT']
selected_symbol = st.sidebar.selectbox("Symbol", symbol_list, index=0 if 'BTCUSDT' in symbol_list else 0)

# Timeframe filter
timeframes = ['M1', 'M5', 'M15', 'H1', 'H4', 'D1', 'ALL']
selected_timeframe = st.sidebar.selectbox("Timeframe", timeframes, index=0)

# Date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())

# Strategy filter
strategies = ['ALL', 'LONG_ONLY', 'SHORT_ONLY', 'SIDEWAY_ONLY']
selected_strategy = st.sidebar.selectbox("Strategy", strategies, index=0)

st.sidebar.markdown("---")
st.sidebar.info(f"**Filters Applied:**\n- Symbol: {selected_symbol}\n- Timeframe: {selected_timeframe}\n- Strategy: {selected_strategy}\n- Date: {start_date} to {end_date}")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

st.title("🤖 SuperBot Simple v1")
st.markdown("**Simplified Dashboard with Expandable Tables**")

# Create tabs for different data views
tabs = st.tabs([
    "📊 Pipeline Traces",
    "📈 Supertrend Lines",
    "🎯 Supertrend Points",
    "🌊 Market Waves",
    "⚡ Executions",
    "🧠 River Learning",
    "🔬 Darwin Recommendations",
    "📋 Summary Stats"
])

# ============================================================================
# TAB 1: PIPELINE TRACES
# ============================================================================

with tabs[0]:
    st.header("Pipeline Traces (C001-C012)")
    
    # Build query
    query = """
    SELECT 
        id, symbol, timeframe, strategy,
        created_at,
        C001_Observe, C002_Measure, C003_Engine, C004_Preserve,
        C005_Remember, C006_Select, C007_Understand, C008_Classify,
        C009_TradingPlan, C010_RiverReview, C011_Authorize, C012_Execute,
        snapshot_id, market_snapshot, indicator_snapshot, structure_snapshot,
        understanding, structural_snapshot, trading_plan, authorization,
        position_id, entry_price, exit_price, pnl
    FROM pipeline_traces
    WHERE symbol = ?
    AND created_at BETWEEN ? AND ?
    """
    
    params = [selected_symbol, start_date.isoformat(), end_date.isoformat()]
    
    if selected_strategy != 'ALL':
        query += " AND strategy = ?"
        params.append(selected_strategy)
    
    if selected_timeframe != 'ALL':
        query += " AND timeframe = ?"
        params.append(selected_timeframe)
    
    query += " ORDER BY created_at DESC"
    
    df_traces = fetch_table_data(query, params)
    
    if not df_traces.empty:
        # Convert timestamps
        df_traces = convert_timestamps_in_df(df_traces, ['created_at'])
        
        # Create summary columns
        df_traces['Stages'] = df_traces.apply(format_pipeline_stages, axis=1)
        df_traces['Success Rate'] = df_traces.apply(
            lambda row: sum([
                row.get('C001_Observe', False),
                row.get('C002_Measure', False),
                row.get('C003_Engine', False),
                row.get('C004_Preserve', False),
                row.get('C005_Remember', False),
                row.get('C006_Select', False),
                row.get('C007_Understand', False),
                row.get('C008_Classify', False),
                row.get('C009_TradingPlan', False),
                row.get('C010_RiverReview', False),
                row.get('C011_Authorize', False),
                row.get('C012_Execute', False),
            ]) / 12 * 100,
            axis=1
        )
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        total_runs = len(df_traces)
        full_success = len(df_traces[df_traces['C012_Execute'] == True])
        avg_success_rate = df_traces['Success Rate'].mean()
        
        col1.metric("Total Runs", total_runs)
        col2.metric("Full Success (C012)", full_success)
        col3.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")
        col4.metric("Strategy", selected_strategy if selected_strategy != 'ALL' else 'Mixed')
        
        st.markdown("---")
        
        # Main table with expandable rows
        st.subheader("📋 All Pipeline Executions")
        
        # Select columns for main table
        display_cols = [
            'id', 'created_at', 'timeframe', 'strategy',
            'Stages', 'Success Rate', 'position_id', 'pnl'
        ]
        
        df_display = df_traces[display_cols].copy()
        df_display = df_display.rename(columns={
            'created_at': 'Time (WIB)',
            'timeframe': 'TF',
            'strategy': 'Strategy',
            'position_id': 'Position ID',
            'pnl': 'PnL'
        })
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
        
        # Expandable section for detailed view
        st.markdown("### 🔍 Detailed View (Click to Expand)")
        
        for idx, row in df_traces.iterrows():
            with st.expander(f"Run #{row['id']} - {row['created_at']} - {row['timeframe']} - {row['strategy']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Basic Info:**")
                    st.write(f"- Symbol: {row['symbol']}")
                    st.write(f"- Timeframe: {row['timeframe']}")
                    st.write(f"- Strategy: {row['strategy']}")
                    st.write(f"- Time: {row['created_at']}")
                    st.write(f"- Position ID: {row['position_id'] or 'N/A'}")
                
                with col2:
                    st.markdown("**Performance:**")
                    st.write(f"- Entry Price: {row['entry_price'] or 'N/A'}")
                    st.write(f"- Exit Price: {row['exit_price'] or 'N/A'}")
                    st.write(f"- PnL: {row['pnl'] or '0'}")
                    st.write(f"- Success Rate: {row['Success Rate']:.1f}%")
                
                st.markdown("**Stage Details:**")
                stage_details = {
                    'C001_Observe': row.get('C001_Observe'),
                    'C002_Measure': row.get('C002_Measure'),
                    'C003_Engine': row.get('C003_Engine'),
                    'C004_Preserve': row.get('C004_Preserve'),
                    'C005_Remember': row.get('C005_Remember'),
                    'C006_Select': row.get('C006_Select'),
                    'C007_Understand': row.get('C007_Understand'),
                    'C008_Classify': row.get('C008_Classify'),
                    'C009_TradingPlan': row.get('C009_TradingPlan'),
                    'C010_RiverReview': row.get('C010_RiverReview'),
                    'C011_Authorize': row.get('C011_Authorize'),
                    'C012_Execute': row.get('C012_Execute'),
                }
                
                stage_df = pd.DataFrame([stage_details])
                st.dataframe(stage_df, use_container_width=True)
                
                # Show snapshots if available
                if row.get('snapshot_id'):
                    st.markdown("**Snapshots:**")
                    st.code(f"Snapshot ID: {row['snapshot_id']}")
                    if row.get('market_snapshot'):
                        st.json(row['market_snapshot'] if isinstance(row['market_snapshot'], dict) else {})
                    if row.get('indicator_snapshot'):
                        st.json(row['indicator_snapshot'] if isinstance(row['indicator_snapshot'], dict) else {})
    
    else:
        st.warning("No pipeline traces found for the selected filters.")

# ============================================================================
# TAB 2: SUPERTREND LINES
# ============================================================================

with tabs[1]:
    st.header("Supertrend Lines")
    
    query = """
    SELECT 
        id, symbol, timeframe,
        created_at,
        trend_direction,
        multiplier,
        atr_period,
        start_price,
        end_price,
        is_active,
        points_count
    FROM supertrend_lines
    WHERE symbol = ?
    """
    
    params = [selected_symbol]
    
    if selected_timeframe != 'ALL':
        query += " AND timeframe = ?"
        params.append(selected_timeframe)
    
    query += " ORDER BY created_at DESC"
    
    df_lines = fetch_table_data(query, params)
    
    if not df_lines.empty:
        # Convert timestamps
        df_lines = convert_timestamps_in_df(df_lines, ['created_at'])
        
        # Format trend direction
        df_lines['Trend'] = df_lines['trend_direction'].apply(
            lambda x: "🟢 UP" if x == 'UP' else ("🔴 DOWN" if x == 'DOWN' else "⚪ NEUTRAL")
        )
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        total_lines = len(df_lines)
        active_lines = len(df_lines[df_lines['is_active'] == 1])
        up_trends = len(df_lines[df_lines['trend_direction'] == 'UP'])
        
        col1.metric("Total Lines", total_lines)
        col2.metric("Active Lines", active_lines)
        col3.metric("UP Trends", f"{up_trends} ({up_trends/total_lines*100:.1f}%)")
        
        st.markdown("---")
        
        # Main table
        display_cols = [
            'id', 'created_at', 'timeframe', 'Trend',
            'start_price', 'end_price', 'is_active', 'points_count'
        ]
        
        df_display = df_lines[display_cols].copy()
        df_display = df_display.rename(columns={
            'created_at': 'Created (WIB)',
            'timeframe': 'TF',
            'start_price': 'Start Price',
            'end_price': 'End Price',
            'is_active': 'Active',
            'points_count': 'Points'
        })
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Expandable details
        st.markdown("### 🔍 Line Details (Click to Expand)")
        
        for idx, row in df_lines.iterrows():
            with st.expander(f"Line #{row['id']} - {row['timeframe']} - {row['Trend']} - {row['created_at']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Line Info:**")
                    st.write(f"- Symbol: {row['symbol']}")
                    st.write(f"- Timeframe: {row['timeframe']}")
                    st.write(f"- Trend: {row['trend_direction']}")
                    st.write(f"- Created: {row['created_at']}")
                    st.write(f"- Active: {'Yes' if row['is_active'] else 'No'}")
                
                with col2:
                    st.markdown("**Parameters:**")
                    st.write(f"- ATR Period: {row['atr_period']}")
                    st.write(f"- Multiplier: {row['multiplier']}")
                    st.write(f"- Start Price: {row['start_price']}")
                    st.write(f"- End Price: {row['end_price']}")
                    st.write(f"- Points Count: {row['points_count']}")
                
                # Fetch and show points for this line
                st.markdown("**Points in this Line:**")
                points_query = """
                SELECT id, timestamp, price, trend_value, direction
                FROM supertrend_points
                WHERE line_id = ?
                ORDER BY timestamp ASC
                """
                df_points = fetch_table_data(points_query, [row['id']])
                
                if not df_points.empty:
                    df_points = convert_timestamps_in_df(df_points, ['timestamp'])
                    st.dataframe(df_points, use_container_width=True)
                else:
                    st.info("No points found for this line.")
    
    else:
        st.warning("No supertrend lines found for the selected filters.")

# ============================================================================
# TAB 3: SUPERTREND POINTS
# ============================================================================

with tabs[2]:
    st.header("Supertrend Points")
    
    query = """
    SELECT 
        sp.id, sp.line_id, sp.symbol, sp.timeframe,
        sp.timestamp, sp.price, sp.trend_value, sp.direction,
        sl.trend_direction as line_trend
    FROM supertrend_points sp
    LEFT JOIN supertrend_lines sl ON sp.line_id = sl.id
    WHERE sp.symbol = ?
    """
    
    params = [selected_symbol]
    
    if selected_timeframe != 'ALL':
        query += " AND sp.timeframe = ?"
        params.append(selected_timeframe)
    
    query += " ORDER BY sp.timestamp DESC LIMIT 1000"
    
    df_points = fetch_table_data(query, params)
    
    if not df_points.empty:
        # Convert timestamps
        df_points = convert_timestamps_in_df(df_points, ['timestamp'])
        
        # Format direction
        df_points['Direction'] = df_points['direction'].apply(
            lambda x: "🟢 UP" if x == 'UP' else ("🔴 DOWN" if x == 'DOWN' else "⚪")
        )
        
        # Summary
        col1, col2, col3 = st.columns(3)
        total_points = len(df_points)
        up_points = len(df_points[df_points['direction'] == 'UP'])
        down_points = len(df_points[df_points['direction'] == 'DOWN'])
        
        col1.metric("Total Points", total_points)
        col2.metric("UP Points", up_points)
        col3.metric("DOWN Points", down_points)
        
        st.markdown("---")
        
        # Main table
        display_cols = [
            'id', 'line_id', 'timeframe', 'timestamp',
            'price', 'trend_value', 'Direction', 'line_trend'
        ]
        
        df_display = df_points[display_cols].copy()
        df_display = df_display.rename(columns={
            'line_id': 'Line ID',
            'timeframe': 'TF',
            'timestamp': 'Time (WIB)',
            'price': 'Price',
            'trend_value': 'Trend Value',
            'line_trend': 'Line Trend'
        })
        
        st.dataframe(df_display, use_container_width=True, height=500)
        
        # Expandable view by line
        st.markdown("### 📊 Grouped by Line (Click to Expand)")
        
        unique_lines = df_points['line_id'].unique()
        
        for line_id in unique_lines[:20]:  # Limit to 20 lines
            line_points = df_points[df_points['line_id'] == line_id]
            line_trend = line_points['line_trend'].iloc[0] if len(line_points) > 0 else 'UNKNOWN'
            
            with st.expander(f"Line #{line_id} - {line_trend} - {len(line_points)} points"):
                st.dataframe(line_points, use_container_width=True)
    
    else:
        st.warning("No supertrend points found for the selected filters.")

# ============================================================================
# TAB 4: MARKET WAVES
# ============================================================================

with tabs[3]:
    st.header("Market Waves")
    
    # Query for wave data (assuming waves table exists)
    query = """
    SELECT 
        id, symbol, timeframe,
        created_at,
        wave_type,
        wave_start,
        wave_end,
        wave_high,
        wave_low,
        amplitude,
        duration_minutes,
        is_complete
    FROM market_waves
    WHERE symbol = ?
    """
    
    params = [selected_symbol]
    
    if selected_timeframe != 'ALL':
        query += " AND timeframe = ?"
        params.append(selected_timeframe)
    
    query += " ORDER BY created_at DESC"
    
    df_waves = fetch_table_data(query, params)
    
    if not df_waves.empty:
        # Convert timestamps
        df_waves = convert_timestamps_in_df(df_waves, ['created_at'])
        
        # Format wave type
        df_waves['Wave Type'] = df_waves['wave_type'].apply(
            lambda x: "📈 IMPULSE" if x == 'IMPULSE' else ("📉 CORRECTION" if x == 'CORRECTION' else "➡️ SIDEWAY")
        )
        
        # Summary
        col1, col2, col3 = st.columns(3)
        total_waves = len(df_waves)
        complete_waves = len(df_waves[df_waves['is_complete'] == 1])
        impulse_waves = len(df_waves[df_waves['wave_type'] == 'IMPULSE'])
        
        col1.metric("Total Waves", total_waves)
        col2.metric("Complete Waves", complete_waves)
        col3.metric("Impulse Waves", impulse_waves)
        
        st.markdown("---")
        
        # Main table
        display_cols = [
            'id', 'created_at', 'timeframe', 'Wave Type',
            'wave_start', 'wave_end', 'wave_high', 'wave_low',
            'amplitude', 'duration_minutes', 'is_complete'
        ]
        
        df_display = df_waves[display_cols].copy()
        df_display = df_display.rename(columns={
            'created_at': 'Created (WIB)',
            'timeframe': 'TF',
            'wave_start': 'Start',
            'wave_end': 'End',
            'wave_high': 'High',
            'wave_low': 'Low',
            'is_complete': 'Complete'
        })
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Expandable details
        st.markdown("### 🔍 Wave Details (Click to Expand)")
        
        for idx, row in df_waves.iterrows():
            with st.expander(f"Wave #{row['id']} - {row['Wave Type']} - {row['created_at']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Wave Info:**")
                    st.write(f"- Symbol: {row['symbol']}")
                    st.write(f"- Timeframe: {row['timeframe']}")
                    st.write(f"- Type: {row['wave_type']}")
                    st.write(f"- Created: {row['created_at']}")
                    st.write(f"- Complete: {'Yes' if row['is_complete'] else 'No'}")
                
                with col2:
                    st.markdown("**Metrics:**")
                    st.write(f"- Start: {row['wave_start']}")
                    st.write(f"- End: {row['wave_end']}")
                    st.write(f"- High: {row['wave_high']}")
                    st.write(f"- Low: {row['wave_low']}")
                    st.write(f"- Amplitude: {row['amplitude']}")
                    st.write(f"- Duration: {row['duration_minutes']} min")
    
    else:
        st.info("No market waves table found or no data available. This table will populate once wave detection is implemented.")

# ============================================================================
# TAB 5: EXECUTIONS
# ============================================================================

with tabs[4]:
    st.header("Trade Executions")
    
    query = """
    SELECT 
        id, symbol, timeframe, strategy,
        entry_time, exit_time,
        entry_price, exit_price,
        quantity, leverage,
        pnl, pnl_percent,
        status, exit_reason,
        duration_minutes
    FROM executions
    WHERE symbol = ?
    """
    
    params = [selected_symbol]
    
    if selected_timeframe != 'ALL':
        query += " AND timeframe = ?"
        params.append(selected_timeframe)
    
    if selected_strategy != 'ALL':
        query += " AND strategy = ?"
        params.append(selected_strategy)
    
    query += " ORDER BY entry_time DESC"
    
    df_executions = fetch_table_data(query, params)
    
    if not df_executions.empty:
        # Convert timestamps
        df_executions = convert_timestamps_in_df(df_executions, ['entry_time', 'exit_time'])
        
        # Format status
        df_executions['Status'] = df_executions['status'].apply(
            lambda x: "🟢 OPEN" if x == 'OPEN' else ("🔴 CLOSED" if x == 'CLOSED' else "⚪ PENDING")
        )
        
        # Format PnL color
        def format_pnl(pnl):
            if pnl is None or pd.isna(pnl):
                return "0"
            if pnl > 0:
                return f"🟢 +{pnl}"
            elif pnl < 0:
                return f"🔴 {pnl}"
            else:
                return "⚪ 0"
        
        df_executions['PnL Display'] = df_executions['pnl'].apply(format_pnl)
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        total_trades = len(df_executions)
        open_trades = len(df_executions[df_executions['status'] == '🟢 OPEN'])
        closed_trades = len(df_executions[df_executions['status'] == '🔴 CLOSED'])
        total_pnl = df_executions['pnl'].sum() if 'pnl' in df_executions.columns else 0
        
        col1.metric("Total Trades", total_trades)
        col2.metric("Open Trades", open_trades)
        col3.metric("Closed Trades", closed_trades)
        col4.metric("Total PnL", f"{total_pnl:.2f}")
        
        st.markdown("---")
        
        # Main table
        display_cols = [
            'id', 'entry_time', 'timeframe', 'strategy',
            'entry_price', 'exit_price', 'quantity',
            'PnL Display', 'Status', 'exit_reason'
        ]
        
        df_display = df_executions[display_cols].copy()
        df_display = df_display.rename(columns={
            'entry_time': 'Entry Time (WIB)',
            'timeframe': 'TF',
            'strategy': 'Strategy',
            'entry_price': 'Entry',
            'exit_price': 'Exit',
            'quantity': 'Qty',
            'exit_reason': 'Exit Reason'
        })
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Expandable details
        st.markdown("### 🔍 Trade Details (Click to Expand)")
        
        for idx, row in df_executions.iterrows():
            with st.expander(f"Trade #{row['id']} - {row['entry_time']} - {row['strategy']} - {row['PnL Display']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Trade Info:**")
                    st.write(f"- Symbol: {row['symbol']}")
                    st.write(f"- Timeframe: {row['timeframe']}")
                    st.write(f"- Strategy: {row['strategy']}")
                    st.write(f"- Entry Time: {row['entry_time']}")
                    st.write(f"- Exit Time: {row['exit_time'] or 'N/A'}")
                    st.write(f"- Status: {row['status']}")
                
                with col2:
                    st.markdown("**Execution:**")
                    st.write(f"- Entry Price: {row['entry_price']}")
                    st.write(f"- Exit Price: {row['exit_price'] or 'N/A'}")
                    st.write(f"- Quantity: {row['quantity']}")
                    st.write(f"- Leverage: {row['leverage']}x")
                    st.write(f"- PnL: {row['pnl']}")
                    st.write(f"- PnL %: {row['pnl_percent']}%")
                    st.write(f"- Duration: {row['duration_minutes']} min")
                    st.write(f"- Exit Reason: {row['exit_reason'] or 'N/A'}")
    
    else:
        st.warning("No executions found for the selected filters.")

# ============================================================================
# TAB 6: RIVER LEARNING
# ============================================================================

with tabs[5]:
    st.header("River Learning Metrics")
    
    query = """
    SELECT 
        id, symbol, timeframe,
        created_at,
        total_trades,
        wins, losses,
        win_rate,
        profit_factor,
        avg_win, avg_loss,
        consecutive_wins, consecutive_losses,
        best_trade, worst_trade,
        patterns_learned
    FROM river_learning
    WHERE symbol = ?
    ORDER BY created_at DESC
    """
    
    df_learning = fetch_table_data(query, [selected_symbol])
    
    if not df_learning.empty:
        # Convert timestamps
        df_learning = convert_timestamps_in_df(df_learning, ['created_at'])
        
        # Latest metrics
        latest = df_learning.iloc[0] if len(df_learning) > 0 else None
        
        if latest is not None:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Trades", latest['total_trades'])
            col2.metric("Win Rate", f"{latest['win_rate']:.1f}%")
            col3.metric("Profit Factor", f"{latest['profit_factor']:.2f}")
            col4.metric("Patterns Learned", latest['patterns_learned'])
            
            st.markdown("---")
        
        # Main table
        display_cols = [
            'id', 'created_at', 'timeframe',
            'total_trades', 'wins', 'losses', 'win_rate',
            'profit_factor', 'avg_win', 'avg_loss',
            'consecutive_wins', 'consecutive_losses'
        ]
        
        df_display = df_learning[display_cols].copy()
        df_display = df_display.rename(columns={
            'created_at': 'Created (WIB)',
            'timeframe': 'TF',
            'total_trades': 'Trades',
            'win_rate': 'Win %',
            'profit_factor': 'PF',
            'avg_win': 'Avg Win',
            'avg_loss': 'Avg Loss',
            'consecutive_wins': 'Consec Wins',
            'consecutive_losses': 'Consec Losses'
        })
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Expandable details
        st.markdown("### 🔍 Learning Details (Click to Expand)")
        
        for idx, row in df_learning.iterrows():
            with st.expander(f"Learning #{row['id']} - {row['created_at']} - {row['timeframe']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Performance:**")
                    st.write(f"- Total Trades: {row['total_trades']}")
                    st.write(f"- Wins: {row['wins']}")
                    st.write(f"- Losses: {row['losses']}")
                    st.write(f"- Win Rate: {row['win_rate']:.1f}%")
                    st.write(f"- Profit Factor: {row['profit_factor']:.2f}")
                
                with col2:
                    st.markdown("**Metrics:**")
                    st.write(f"- Avg Win: {row['avg_win']}")
                    st.write(f"- Avg Loss: {row['avg_loss']}")
                    st.write(f"- Consec Wins: {row['consecutive_wins']}")
                    st.write(f"- Consec Losses: {row['consecutive_losses']}")
                    st.write(f"- Best Trade: {row['best_trade']}")
                    st.write(f"- Worst Trade: {row['worst_trade']}")
                
                st.markdown("**Patterns Learned:**")
                st.code(str(row['patterns_learned']))
    
    else:
        st.warning("No river learning data found.")

# ============================================================================
# TAB 7: DARWIN RECOMMENDATIONS
# ============================================================================

with tabs[6]:
    st.header("Darwin Recommendations")
    
    query = """
    SELECT 
        id, symbol, timeframe,
        created_at,
        recommendation_type,
        adjustment_type,
        old_value, new_value,
        confidence_score,
        reasoning,
        status
    FROM darwin_recommendations
    WHERE symbol = ?
    ORDER BY created_at DESC
    """
    
    df_darwin = fetch_table_data(query, [selected_symbol])
    
    if not df_darwin.empty:
        # Convert timestamps
        df_darwin = convert_timestamps_in_df(df_darwin, ['created_at'])
        
        # Format status
        df_darwin['Status'] = df_darwin['status'].apply(
            lambda x: "✅ ACCEPTED" if x == 'ACCEPTED' else ("⏳ PENDING" if x == 'PENDING' else "❌ REJECTED")
        )
        
        # Format confidence
        def format_confidence(score):
            if score >= 0.8:
                return f"🟢 {score:.2f}"
            elif score >= 0.5:
                return f"🟡 {score:.2f}"
            else:
                return f"🔴 {score:.2f}"
        
        df_darwin['Confidence'] = df_darwin['confidence_score'].apply(format_confidence)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        total_recs = len(df_darwin)
        accepted = len(df_darwin[df_darwin['status'] == 'ACCEPTED'])
        pending = len(df_darwin[df_darwin['status'] == 'PENDING'])
        
        col1.metric("Total Recommendations", total_recs)
        col2.metric("Accepted", accepted)
        col3.metric("Pending", pending)
        
        st.markdown("---")
        
        # Main table
        display_cols = [
            'id', 'created_at', 'timeframe', 'recommendation_type',
            'adjustment_type', 'old_value', 'new_value',
            'Confidence', 'Status'
        ]
        
        df_display = df_darwin[display_cols].copy()
        df_display = df_display.rename(columns={
            'created_at': 'Created (WIB)',
            'timeframe': 'TF',
            'recommendation_type': 'Type',
            'adjustment_type': 'Adjustment',
            'old_value': 'Old',
            'new_value': 'New'
        })
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Expandable details
        st.markdown("### 🔍 Recommendation Details (Click to Expand)")
        
        for idx, row in df_darwin.iterrows():
            with st.expander(f"Rec #{row['id']} - {row['Type']} - {row['Confidence']} - {row['Status']}"):
                st.markdown("**Details:**")
                st.write(f"- Symbol: {row['symbol']}")
                st.write(f"- Timeframe: {row['timeframe']}")
                st.write(f"- Created: {row['created_at']}")
                st.write(f"- Type: {row['recommendation_type']}")
                st.write(f"- Adjustment: {row['adjustment_type']}")
                st.write(f"- Old Value: {row['old_value']}")
                st.write(f"- New Value: {row['new_value']}")
                st.write(f"- Confidence: {row['confidence_score']}")
                st.write(f"- Status: {row['status']}")
                
                st.markdown("**Reasoning:**")
                st.info(row['reasoning'])
    
    else:
        st.warning("No darwin recommendations found.")

# ============================================================================
# TAB 8: SUMMARY STATS
# ============================================================================

with tabs[7]:
    st.header("Summary Statistics")
    
    # Overall stats
    stats_query = """
    SELECT 
        COUNT(DISTINCT symbol) as total_symbols,
        COUNT(DISTINCT timeframe) as total_timeframes,
        COUNT(DISTINCT strategy) as total_strategies,
        COUNT(*) as total_pipeline_runs,
        SUM(CASE WHEN C012_Execute = 1 THEN 1 ELSE 0 END) as successful_executions,
        AVG(CASE 
            WHEN C001_Observe + C002_Measure + C003_Engine + C004_Preserve +
                 C005_Remember + C006_Select + C007_Understand + C008_Classify +
                 C009_TradingPlan + C010_RiverReview + C011_Authorize + C012_Execute = 12
            THEN 100.0
            ELSE 0.0
        END) as full_success_rate
    FROM pipeline_traces
    WHERE symbol = ?
    """
    
    df_stats = fetch_table_data(stats_query, [selected_symbol])
    
    if not df_stats.empty and len(df_stats) > 0:
        row = df_stats.iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Symbols Tracked", row['total_symbols'])
        col2.metric("Timeframes Used", row['total_timeframes'])
        col3.metric("Strategies Tested", row['total_strategies'])
        col4.metric("Total Pipeline Runs", row['total_pipeline_runs'])
        
        col5, col6 = st.columns(2)
        col5.metric("Successful Executions", row['successful_executions'])
        col6.metric("Full Success Rate", f"{row['full_success_rate']:.1f}%")
        
        st.markdown("---")
        
        # Timeframe distribution
        tf_query = """
        SELECT timeframe, COUNT(*) as count
        FROM pipeline_traces
        WHERE symbol = ?
        GROUP BY timeframe
        ORDER BY count DESC
        """
        
        df_tf = fetch_table_data(tf_query, [selected_symbol])
        
        if not df_tf.empty:
            st.subheader("📊 Pipeline Runs by Timeframe")
            st.bar_chart(df_tf.set_index('timeframe'))
        
        # Strategy distribution
        strat_query = """
        SELECT strategy, COUNT(*) as count
        FROM pipeline_traces
        WHERE symbol = ?
        GROUP BY strategy
        ORDER BY count DESC
        """
        
        df_strat = fetch_table_data(strat_query, [selected_symbol])
        
        if not df_strat.empty:
            st.subheader("📊 Pipeline Runs by Strategy")
            st.bar_chart(df_strat.set_index('strategy'))
    
    else:
        st.warning("No statistics available.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("SuperBot Simple v1 | Full Pipeline Traceability | All times displayed in WIB (UTC+7)")
