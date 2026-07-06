"""
SuperBot Dashboard - Complete Pipeline Tracking UI
Features:
- Full pipeline traceability visualization (C001-C012)
- Supertrend points & lines tracking across all timeframes
- River & Darwin learning visualization
- Binance Futures data with date range selection
- Real-time execution tracking
- Interactive charts and tables
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# Configure page
st.set_page_config(
    page_title="SuperBot Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000"

# WIB Timezone offset (UTC+7)
WIB_OFFSET_HOURS = 7

def convert_utc_to_wib(utc_timestamp):
    """Convert UTC timestamp to WIB (UTC+7)."""
    try:
        if isinstance(utc_timestamp, str):
            # Parse ISO format string
            utc_dt = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
        elif isinstance(utc_timestamp, datetime):
            utc_dt = utc_timestamp
        else:
            return utc_timestamp
        
        # Add 7 hours for WIB
        wib_dt = utc_dt + timedelta(hours=WIB_OFFSET_HOURS)
        return wib_dt.strftime("%Y-%m-%d %H:%M:%S WIB")
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

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .pipeline-stage {
        display: inline-block;
        padding: 5px 10px;
        margin: 2px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stage-success {
        background-color: #d4edda;
        color: #155724;
    }
    .stage-fail {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 SuperBot Dashboard")
st.markdown("**Complete Pipeline Tracking System** | C001-C012 Full Traceability")

# Sidebar
st.sidebar.header("⚙️ Configuration")

# API Connection Check
try:
    response = requests.get(f"{API_BASE_URL}/", timeout=2)
    api_status = "✅ Connected"
except:
    api_status = "❌ Disconnected"
    st.sidebar.warning("API not connected. Start the API server first.")

st.sidebar.markdown(f"**API Status:** {api_status}")

# Date Range Selector
st.sidebar.subheader("📅 Date Range")
default_start = datetime.now() - timedelta(days=30)
start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=datetime.now())

# Symbol Selector
st.sidebar.subheader("💱 Trading Pair")
symbol = st.sidebar.text_input("Symbol", value="BTCUSDT")

# Timeframe Selector
st.sidebar.subheader("⏱️ Timeframe")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["M1", "M5", "M15", "H1", "H4", "D1"],
    index=4  # Default H4
)

# Strategy Selector
st.sidebar.subheader("🎯 Trading Strategy")
strategy = st.sidebar.selectbox(
    "Select Strategy",
    ["LONG_ONLY", "SHORT_ONLY", "SIDEWAY_ONLY"],
    index=0  # Default LONG_ONLY
)

# Navigation
st.sidebar.subheader("📊 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Dashboard Overview",
        "🔍 Pipeline Traces",
        "📈 Supertrend Lines",
        "🎯 Supertrend Points",
        "🧠 River Learning",
        "🔬 Darwin Recommendations",
        "⚡ Execution Tracks",
        "🧪 Run Backtest",
        "▶️ Run Pipeline",
    ]
)

# Helper functions
@st.cache_data(ttl=60)
def fetch_dashboard_stats():
    """Fetch dashboard statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/dashboard/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=30)
def fetch_pipeline_traces(symbol=None, timeframe=None, limit=100):
    """Fetch pipeline traces."""
    try:
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if timeframe:
            params["timeframe"] = timeframe
        
        response = requests.get(f"{API_BASE_URL}/api/v1/pipeline/traces", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_supertrend_lines(symbol=None, timeframe=None, active_only=False, limit=100):
    """Fetch supertrend lines."""
    try:
        params = {"limit": limit, "active_only": active_only}
        if symbol:
            params["symbol"] = symbol
        if timeframe:
            params["timeframe"] = timeframe
        
        response = requests.get(f"{API_BASE_URL}/api/v1/supertrend/lines", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_supertrend_points(line_id):
    """Fetch supertrend points for a line."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/supertrend/points/{line_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_river_learning():
    """Fetch river learning state."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/river/learning", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=30)
def fetch_darwin_recommendations(limit=50):
    """Fetch darwin recommendations."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/darwin/recommendations", params={"limit": limit}, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_execution_tracks(symbol=None, status=None, limit=100):
    """Fetch execution tracks."""
    try:
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        
        response = requests.get(f"{API_BASE_URL}/api/v1/executions", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []


# ==================== PAGES ====================

if page == "🏠 Dashboard Overview":
    st.header("🏠 Dashboard Overview")
    
    # Fetch stats
    stats = fetch_dashboard_stats()
    
    if stats:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Pipelines",
                stats["pipelines"]["total"],
                delta=f"{stats['pipelines']['success_rate']:.1%} success rate"
            )
        
        with col2:
            st.metric(
                "Total Trades",
                stats["executions"]["total"],
                delta=f"{stats['executions']['win_rate']:.1%} win rate"
            )
        
        with col3:
            st.metric(
                "Active Supertrend Lines",
                stats["supertrend"]["active_lines"],
                delta=f"{stats['supertrend']['total_lines']} total"
            )
        
        with col4:
            st.metric(
                "Total PnL",
                f"${stats['executions']['total_pnl']:,.2f}",
                delta="Closed positions"
            )
        
        # Pipeline Success Rate Chart
        st.subheader("📊 Pipeline Performance")
        
        pipeline_data = {
            "Metric": ["Executed", "Not Executed"],
            "Count": [
                stats["pipelines"]["executed"],
                stats["pipelines"]["total"] - stats["pipelines"]["executed"]
            ]
        }
        pipeline_df = pd.DataFrame(pipeline_data)
        
        fig = px.pie(
            pipeline_df,
            values="Count",
            names="Metric",
            title="Pipeline Execution Rate",
            color_discrete_sequence=["#28a745", "#dc3545"]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Supertrend Stats
        st.subheader("📈 Supertrend Statistics")
        
        supertrend_col1, supertrend_col2 = st.columns(2)
        
        with supertrend_col1:
            st.info(f"""
            **Active Lines:** {stats['supertrend']['active_lines']}
            
            **Total Lines:** {stats['supertrend']['total_lines']}
            
            **Total Points:** {stats['supertrend']['total_points']}
            """)
        
        with supertrend_col2:
            st.success(f"""
            **River Total Trades:** {stats['learning']['river_total_trades']}
            
            **Win Rate:** {stats['executions']['win_rate']:.1%}
            
            **Open Positions:** {stats['executions']['open_positions']}
            """)
    
    else:
        st.warning("Unable to fetch dashboard stats. Make sure the API server is running.")
        st.info("Start the API server with: `python -m st_lms.api.superbot_api`")


elif page == "🔍 Pipeline Traces":
    st.header("🔍 Pipeline Traces")
    st.markdown("Track every pipeline execution from C001 to C012")
    
    # Filters
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_symbol = st.text_input("Filter by Symbol", value=symbol)
    with filter_col2:
        filter_tf = st.selectbox("Filter by Timeframe", ["All", "M1", "M5", "M15", "H1", "H4", "D1"])
    
    # Fetch traces
    tf_param = None if filter_tf == "All" else filter_tf
    traces = fetch_pipeline_traces(symbol=filter_symbol, timeframe=tf_param, limit=100)
    
    if traces:
        # Convert to DataFrame
        df_traces = pd.DataFrame(traces)
        
        # Display summary
        st.subheader(f"Found {len(traces)} pipeline traces")
        
        # Stage completion heatmap
        if "stages" in df_traces.columns:
            st.subheader("🎯 Stage Completion Heatmap")
            
            stage_cols = ["C001_Observe", "C002_Measure", "C003_Engine", "C004_Preserve",
                         "C005_Remember", "C006_Select", "C007_Understand", "C008_Classify",
                         "C009_TradingPlan", "C010_RiverReview", "C011_Authorize", "C012_Execute"]
            
            stage_data = []
            for idx, trace in enumerate(traces[:20]):  # Show last 20
                row = {"Pipeline": f"#{idx+1}"}
                stages = trace.get("stages", {})
                for stage in stage_cols:
                    row[stage] = "✅" if stages.get(stage, False) else "❌"
                stage_data.append(row)
            
            stage_df = pd.DataFrame(stage_data)
            st.dataframe(stage_df, use_container_width=True)
        
        # Detailed table
        st.subheader("📋 Detailed Traces")
        
        display_cols = ["pipeline_id", "timestamp", "symbol", "timeframe", "position_id", "position_size"]
        display_df = df_traces[display_cols].copy()
        display_df.columns = ["Pipeline ID", "Timestamp", "Symbol", "Timeframe", "Position ID", "Position Size"]
        
        # Convert timestamp to WIB
        display_df = convert_timestamps_in_df(display_df, ["Timestamp"])
        
        st.dataframe(display_df, use_container_width=True)
        
        # Click to view details
        selected_trace = st.selectbox(
            "Select pipeline to view details",
            options=[t["pipeline_id"] for t in traces],
            format_func=lambda x: f"{x[:20]}..."
        )
        
        if selected_trace:
            trace_detail = next((t for t in traces if t["pipeline_id"] == selected_trace), None)
            if trace_detail:
                st.subheader(f"Details for {selected_trace}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Basic Info:**")
                    st.write(f"- Symbol: {trace_detail['symbol']}")
                    st.write(f"- Timeframe: {trace_detail['timeframe']}")
                    # Convert timestamp to WIB
                    timestamp_wib = convert_utc_to_wib(trace_detail.get('timestamp', ''))
                    st.write(f"- Timestamp (WIB): {timestamp_wib}")
                
                with col2:
                    st.write("**Results:**")
                    st.write(f"- Position ID: {trace_detail.get('position_id', 'None')}")
                    st.write(f"- Position Size: {trace_detail.get('position_size', '0')}")
                
                # Stages
                st.write("**Stage Results:**")
                stages = trace_detail.get("stages", {})
                for stage, completed in stages.items():
                    status = "✅" if completed else "❌"
                    st.write(f"{status} {stage}")
                
                # Darwin recommendation
                if trace_detail.get("darwin_recommendation"):
                    st.write("**Darwin Recommendation:**")
                    darwin = trace_detail["darwin_recommendation"]
                    st.json(darwin)
    
    else:
        st.info("No pipeline traces found. Run a pipeline first.")


elif page == "📈 Supertrend Lines":
    st.header("📈 Supertrend Lines")
    st.markdown("Track all Supertrend lines across all timeframes")
    
    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        filter_symbol = st.text_input("Symbol", value=symbol)
    with filter_col2:
        filter_tf = st.selectbox("Timeframe", ["All", "M1", "M5", "M15", "H1", "H4", "D1"])
    with filter_col3:
        active_only = st.checkbox("Active Only", value=False)
    
    # Fetch lines
    tf_param = None if filter_tf == "All" else filter_tf
    lines = fetch_supertrend_lines(symbol=filter_symbol, timeframe=tf_param, active_only=active_only, limit=100)
    
    if lines:
        st.subheader(f"Found {len(lines)} Supertrend lines")
        
        # Convert to DataFrame
        df_lines = pd.DataFrame(lines)
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            up_lines = len([l for l in lines if l["trend_direction"] == "UP"])
            st.metric("UP Trends", up_lines)
        with col2:
            down_lines = len([l for l in lines if l["trend_direction"] == "DOWN"])
            st.metric("DOWN Trends", down_lines)
        with col3:
            active_lines = len([l for l in lines if l["is_active"]])
            st.metric("Active Lines", active_lines)
        
        # Lines table
        st.subheader("📋 All Lines")
        
        display_cols = ["line_id", "symbol", "timeframe", "trend_direction", 
                       "start_price", "current_price", "points_count", "is_active", "strength"]
        display_df = df_lines[display_cols].copy()
        display_df.columns = ["Line ID", "Symbol", "Timeframe", "Direction", 
                             "Start Price", "Current Price", "Points", "Active", "Strength"]
        
        st.dataframe(display_df, use_container_width=True)
        
        # Select line to view points
        selected_line = st.selectbox(
            "Select line to view points",
            options=[l["line_id"] for l in lines],
            format_func=lambda x: f"{x[:15]}... ({next(l['timeframe'] for l in lines if l['line_id']==x)})"
        )
        
        if selected_line:
            st.session_state.selected_line_id = selected_line
            st.rerun()
    
    else:
        st.info("No Supertrend lines found.")


elif page == "🎯 Supertrend Points":
    st.header("🎯 Supertrend Points")
    st.markdown("View individual points for each Supertrend line")
    
    # Get selected line from previous page or let user select
    if "selected_line_id" in st.session_state:
        default_line = st.session_state.selected_line_id
    else:
        default_line = None
    
    # Fetch all lines for selection
    all_lines = fetch_supertrend_lines(limit=100)
    
    if all_lines:
        line_options = [l["line_id"] for l in all_lines]
        selected_line = st.selectbox(
            "Select Supertrend Line",
            options=line_options,
            index=line_options.index(default_line) if default_line in line_options else 0,
            format_func=lambda x: f"{x[:20]}... ({next(l['timeframe'] for l in all_lines if l['line_id']==x)})"
        )
        
        # Fetch points
        points = fetch_supertrend_points(selected_line)
        
        if points:
            st.subheader(f"Points for line: {selected_line}")
            
            # Convert to DataFrame
            df_points = pd.DataFrame(points)
            
            # Plot price chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=[datetime.fromtimestamp(p["timestamp"]/1000) for p in points],
                y=[p["price"] for p in points],
                mode="lines+markers",
                name="Price",
                line=dict(color="#007bff", width=2)
            ))
            
            # Color by trend direction
            up_points = [p for p in points if p["trend_direction"] == "UP"]
            down_points = [p for p in points if p["trend_direction"] == "DOWN"]
            
            if up_points:
                fig.add_trace(go.Scatter(
                    x=[datetime.fromtimestamp(p["timestamp"]/1000) for p in up_points],
                    y=[p["atr_value"] for p in up_points],
                    mode="markers",
                    name="UP Trend (ATR)",
                    marker=dict(color="#28a745", size=8)
                ))
            
            if down_points:
                fig.add_trace(go.Scatter(
                    x=[datetime.fromtimestamp(p["timestamp"]/1000) for p in down_points],
                    y=[p["atr_value"] for p in down_points],
                    mode="markers",
                    name="DOWN Trend (ATR)",
                    marker=dict(color="#dc3545", size=8)
                ))
            
            fig.update_layout(
                title="Supertrend Points Analysis",
                xaxis_title="Time",
                yaxis_title="Price / ATR Value",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.subheader("📋 Points Data")
            st.dataframe(df_points, use_container_width=True)
        else:
            st.info("No points found for this line.")
    else:
        st.info("No Supertrend lines available. Go to Supertrend Lines page first.")


elif page == "🧠 River Learning":
    st.header("🧠 River Learning")
    st.markdown("Track all learned patterns from past trades")
    
    # Fetch learning data
    learning = fetch_river_learning()
    
    if learning:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", learning["total_trades"])
        with col2:
            st.metric("Win Rate", f"{learning['win_rate']:.1%}")
        with col3:
            st.metric("Profit Factor", f"{learning['profit_factor']:.2f}")
        with col4:
            st.metric("Total PnL", f"${learning['total_pnl']:,.2f}")
        
        # Detailed metrics
        st.subheader("📊 Detailed Metrics")
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.info(f"""
            **Wins:** {learning['wins']}
            
            **Losses:** {learning['losses']}
            
            **Avg Win:** ${learning['avg_win']:,.2f}
            
            **Avg Loss:** ${learning['avg_loss']:,.2f}
            """)
        
        with metrics_col2:
            st.warning(f"""
            **Best Trade:** ${learning['best_trade']:,.2f}
            
            **Worst Trade:** ${learning['worst_trade']:,.2f}
            
            **Consecutive Wins:** {learning['consecutive_wins']}
            
            **Consecutive Losses:** {learning['consecutive_losses']}
            """)
        
        # Patterns learned
        st.subheader("🔍 Patterns Learned")
        if learning.get("patterns_learned"):
            for pattern in learning["patterns_learned"]:
                st.json(pattern)
        else:
            st.info("No specific patterns recorded yet.")
    
    else:
        st.info("No River learning data available. Run some trades first.")


elif page == "🔬 Darwin Recommendations":
    st.header("🔬 Darwin Recommendations")
    st.markdown("View Darwin's optimization recommendations")
    
    # Fetch recommendations
    recs = fetch_darwin_recommendations(limit=50)
    
    if recs:
        st.subheader(f"Found {len(recs)} recommendations")
        
        # Display as cards
        for i, rec in enumerate(recs[:10]):  # Show last 10
            with st.expander(f"Recommendation #{i+1} - {rec['timestamp']}", expanded=(i==0)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**State:** {rec['state']}")
                    st.write(f"**Confidence:** {rec['confidence']:.2f}")
                
                with col2:
                    st.write(f"**Timestamp:** {rec['timestamp']}")
                
                st.write("**Adjustments:**")
                st.json(rec.get("adjustments", {}))
                
                if rec.get("reasoning"):
                    st.write(f"**Reasoning:** {rec['reasoning']}")
        
        # All recommendations table
        st.subheader("📋 All Recommendations")
        df_recs = pd.DataFrame(recs)
        display_cols = ["recommendation_id", "timestamp", "state", "confidence"]
        st.dataframe(df_recs[display_cols], use_container_width=True)
    
    else:
        st.info("No Darwin recommendations available. Run the pipeline first.")


elif page == "⚡ Execution Tracks":
    st.header("⚡ Execution Tracks")
    st.markdown("Complete traceability of every trade executed by the bot")
    
    # Filters
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_symbol = st.text_input("Symbol", value=symbol)
    with filter_col2:
        filter_status = st.selectbox("Status", ["All", "OPEN", "CLOSED", "CANCELLED"])
    
    # Fetch executions
    status_param = None if filter_status == "All" else filter_status
    executions = fetch_execution_tracks(symbol=filter_symbol, status=status_param, limit=100)
    
    if executions:
        st.subheader(f"Found {len(executions)} executions")
        
        # Convert to DataFrame
        df_exec = pd.DataFrame(executions)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            open_pos = len([e for e in executions if e["status"] == "OPEN"])
            st.metric("Open Positions", open_pos)
        with col2:
            closed_pos = len([e for e in executions if e["status"] == "CLOSED"])
            st.metric("Closed Positions", closed_pos)
        with col3:
            total_pnl = sum([e.get("pnl", 0) or 0 for e in executions if e["status"] == "CLOSED"])
            st.metric("Total PnL", f"${total_pnl:,.2f}")
        
        # Detailed table
        st.subheader("📋 Execution Details")
        
        display_cols = ["execution_id", "symbol", "direction", "entry_price", 
                       "exit_price", "pnl", "pnl_percent", "status", "entry_timestamp"]
        display_df = df_exec[display_cols].copy()
        display_df.columns = ["Execution ID", "Symbol", "Direction", "Entry Price",
                             "Exit Price", "PnL", "PnL %", "Status", "Entry Time"]
        
        # Convert timestamp to WIB
        display_df = convert_timestamps_in_df(display_df, ["Entry Time"])
        
        st.dataframe(display_df, use_container_width=True)
        
        # PnL distribution chart
        closed_execs = [e for e in executions if e["status"] == "CLOSED" and e.get("pnl")]
        if closed_execs:
            st.subheader("📊 PnL Distribution")
            
            pnl_df = pd.DataFrame(closed_execs)
            fig = px.histogram(
                pnl_df,
                x="pnl",
                nbins=20,
                title="PnL Distribution",
                labels={"pnl": "PnL ($)"},
                color_discrete_sequence=["#28a745"]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No execution tracks found. Run the pipeline first.")


elif page == "🧪 Run Backtest":
    st.header("🧪 Run Backtest")
    st.markdown("Run complete pipeline backtest for specified date range")
    
    # Form
    with st.form("backtest_form"):
        bt_symbol = st.text_input("Symbol", value="BTCUSDT")
        
        bt_col1, bt_col2 = st.columns(2)
        with bt_col1:
            bt_start = st.date_input("Start Date (WIB)", value=datetime.now() - timedelta(days=30))
        with bt_col2:
            bt_end = st.date_input("End Date (WIB)", value=datetime.now())
        
        # Strategy selector for backtest
        bt_strategy = st.selectbox(
            "Trading Strategy",
            ["LONG_ONLY", "SHORT_ONLY", "SIDEWAY_ONLY"],
            index=0
        )
        
        bt_timeframes = st.multiselect(
            "Timeframes",
            ["M1", "M5", "M15", "H1", "H4", "D1"],
            default=["H4"]
        )
        
        bt_balance = st.number_input("Initial Balance", value=10000.0, min_value=1000.0)
        bt_risk_method = st.selectbox("Risk Method", ["fixed_fraction", "kelly"])
        
        submitted = st.form_submit_button("▶️ Run Backtest", type="primary")
        
        if submitted:
            if not bt_timeframes:
                st.error("Please select at least one timeframe")
            else:
                with st.spinner("Running backtest... This may take a while."):
                    try:
                        request_data = {
                            "symbol": bt_symbol,
                            "strategy": bt_strategy,
                            "start_date": bt_start.strftime("%Y-%m-%d"),
                            "end_date": bt_end.strftime("%Y-%m-%d"),
                            "timeframes": bt_timeframes,
                            "initial_balance": bt_balance,
                            "risk_method": bt_risk_method
                        }
                        
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/backtest/run",
                            json=request_data,
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("Backtest completed!")
                            
                            # Results
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Trades", result["total_trades"])
                            with col2:
                                st.metric("Win Rate", f"{result['win_rate']:.1%}")
                            with col3:
                                st.metric("Final Balance", f"${result['final_balance']:,.2f}")
                            with col4:
                                st.metric("Total PnL", f"${result['total_pnl']:,.2f}")
                            
                            # Equity curve
                            if result.get("equity_curve"):
                                st.subheader("📈 Equity Curve")
                                equity_df = pd.DataFrame({
                                    "Step": range(len(result["equity_curve"])),
                                    "Equity": result["equity_curve"]
                                })
                                fig = px.line(equity_df, x="Step", y="Equity", title="Equity Curve")
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Trades table
                            if result.get("trades"):
                                st.subheader("📋 All Trades")
                                trades_df = pd.DataFrame(result["trades"])
                                
                                # Convert timestamps to WIB if present
                                timestamp_cols = [col for col in trades_df.columns if 'time' in col.lower() or 'date' in col.lower()]
                                if timestamp_cols:
                                    trades_df = convert_timestamps_in_df(trades_df, timestamp_cols)
                                
                                st.dataframe(trades_df, use_container_width=True)
                        else:
                            st.error(f"Backtest failed: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Error running backtest: {str(e)}")


elif page == "▶️ Run Pipeline":
    st.header("▶️ Run Pipeline")
    st.markdown("Execute live pipeline run with real-time tracking")
    
    # Form
    with st.form("pipeline_form"):
        pl_symbol = st.text_input("Symbol", value="BTCUSDT")
        pl_timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"], index=4)
        
        # Strategy selector for pipeline run
        pl_strategy = st.selectbox(
            "Trading Strategy",
            ["LONG_ONLY", "SHORT_ONLY", "SIDEWAY_ONLY"],
            index=0
        )
        
        pl_col1, pl_col2 = st.columns(2)
        with pl_col1:
            pl_start = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
        with pl_col2:
            pl_end = st.date_input("End Date", value=datetime.now())
        
        pl_balance = st.number_input("Initial Balance", value=10000.0, min_value=1000.0)
        pl_risk_method = st.selectbox("Risk Method", ["fixed_fraction", "kelly"])
        
        submitted = st.form_submit_button("▶️ Run Pipeline", type="primary")
        
        if submitted:
            with st.spinner("Running pipeline...") as spinner:
                try:
                    params = {
                        "symbol": pl_symbol,
                        "timeframe": pl_timeframe,
                        "strategy": pl_strategy,
                        "start_date": pl_start.strftime("%Y-%m-%d"),
                        "end_date": pl_end.strftime("%Y-%m-%d"),
                        "initial_balance": pl_balance,
                        "risk_method": pl_risk_method
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/pipeline/run",
                        params=params,
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("Pipeline executed successfully!")
                        
                        # Pipeline ID
                        st.info(f"**Pipeline ID:** `{result['pipeline_id']}`")
                        
                        # Stage results
                        st.subheader("🎯 Stage Results")
                        
                        stages = result.get("stages", {})
                        for stage, completed in stages.items():
                            status = "✅" if completed else "❌"
                            st.write(f"{status} {stage}")
                        
                        # Results summary
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Basic Info:**")
                            st.write(f"- Symbol: {result['symbol']}")
                            st.write(f"- Timeframe: {result['timeframe']}")
                            st.write(f"- Strategy: {result.get('strategy', 'N/A')}")
                            # Convert timestamp to WIB
                            timestamp_wib = convert_utc_to_wib(result.get('timestamp', ''))
                            st.write(f"- Timestamp (WIB): {timestamp_wib}")
                        
                        with col2:
                            st.write("**Execution:**")
                            st.write(f"- Position ID: {result.get('position_id', 'None')}")
                            st.write(f"- Position Size: {result.get('position_size', '0')}")
                        
                        # Darwin recommendation
                        if result.get("darwin_recommendation"):
                            st.subheader("🔬 Darwin Recommendation")
                            st.json(result["darwin_recommendation"])
                        
                        # Link to trace
                        st.success(f"View full trace in Pipeline Traces page: `{result['pipeline_id']}`")
                    
                    else:
                        st.error(f"Pipeline execution failed: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error running pipeline: {str(e)}")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**SuperBot Dashboard v1.0**

Built with Streamlit & FastAPI

Complete Pipeline Tracking System
""")

st.markdown("---")
st.caption("SuperBot Dashboard | Complete Pipeline Tracking (C001-C012) | River & Darwin Learning")
