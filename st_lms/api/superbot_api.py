"""
SuperBot API - Complete Pipeline Tracking & Dashboard Backend
Features:
- Full pipeline traceability (C001-C012)
- Supertrend points & lines tracking across all timeframes
- River & Darwin learning tracking
- Binance Futures API integration with date range selection
- Real-time execution tracking
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from st_lms.common.enums import Timeframe
from st_lms.exchange.binance.binance_client import BinanceClient
from st_lms.models.candle import Candle
from st_lms.pipeline import Pipeline, PipelineResult
from st_lms.observe.simulation_observer import SimulationObserver
from st_lms.backtest.engine import BacktestEngine
from st_lms.persistence.sqlite_repository import init_database
from st_lms.trading_plan.builders.long_builder import LongBuilder
from st_lms.trading_plan.builders.short_builder import ShortBuilder
from st_lms.trading_plan.builders.sideway_builder import SidewayBuilder


# ==================== PYDANTIC MODELS ====================

class CandleRequest(BaseModel):
    symbol: str
    timeframe: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    limit: int = Field(default=1000, ge=1, le=5000)


class PipelineTraceResponse(BaseModel):
    pipeline_id: str
    timestamp: str
    symbol: str
    timeframe: str
    strategy: Optional[str] = "LONG_ONLY"
    stages: Dict[str, bool]
    market_snapshot_id: Optional[str]
    indicator_snapshot_id: Optional[str]
    structure_snapshot_id: Optional[str]
    understanding_id: Optional[str]
    structural_snapshot_id: Optional[str]
    trading_plan_id: Optional[str]
    authorization_id: Optional[str]
    position_id: Optional[str]
    position_size: str
    darwin_recommendation: Optional[Dict[str, Any]]


class SupertrendPointResponse(BaseModel):
    point_id: str
    timestamp: int
    price: float
    trend_direction: str  # "UP" or "DOWN"
    atr_value: float
    multiplier: float
    line_id: str
    timeframe: str
    symbol: str


class SupertrendLineResponse(BaseModel):
    line_id: str
    timeframe: str
    symbol: str
    trend_direction: str
    start_timestamp: int
    end_timestamp: Optional[int]
    start_price: float
    current_price: float
    points_count: int
    is_active: bool
    strength: int


class RiverLearningResponse(BaseModel):
    snapshot_id: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    best_trade: float
    worst_trade: float
    consecutive_wins: int
    consecutive_losses: int
    patterns_learned: List[Dict[str, Any]]


class DarwinRecommendationResponse(BaseModel):
    recommendation_id: str
    timestamp: str
    state: str
    adjustments: Dict[str, Any]
    confidence: float
    reasoning: str


class ExecutionTrackResponse(BaseModel):
    execution_id: str
    pipeline_trace_id: str
    plan_id: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float]
    position_size: float
    pnl: Optional[float]
    pnl_percent: Optional[float]
    status: str  # "OPEN", "CLOSED", "CANCELLED"
    entry_timestamp: str
    exit_timestamp: Optional[str]
    exit_reason: Optional[str]
    duration_seconds: Optional[int]


class PipelineRunRequest(BaseModel):
    """Request model for running pipeline with strategy selection."""
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    strategy: str = "LONG_ONLY"  # LONG_ONLY, SHORT_ONLY, SIDEWAY_ONLY
    initial_balance: float = 10000.0
    risk_method: str = "fixed_fraction"
    leverage: float = 10.0


class BacktestRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    strategy: str = "LONG_ONLY"  # LONG_ONLY, SHORT_ONLY, SIDEWAY_ONLY
    timeframes: List[str]
    initial_balance: float = 10000.0
    risk_method: str = "fixed_fraction"


class BacktestResultResponse(BaseModel):
    backtest_id: str
    symbol: str
    start_date: str
    end_date: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    final_balance: float
    max_drawdown: float
    sharpe_ratio: Optional[float]
    trades: List[ExecutionTrackResponse]
    equity_curve: List[float]


# ==================== API APP ====================

app = FastAPI(
    title="SuperBot API",
    description="Complete Pipeline Tracking & Dashboard Backend for ST_LMS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== GLOBAL STATE ====================

_db_path = "superbot.db"
_pipeline_traces: List[PipelineResult] = []
_execution_tracks: List[Dict[str, Any]] = []


# ==================== HELPER FUNCTIONS ====================

def get_db_connection():
    """Get SQLite connection."""
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_superbot_db():
    """Initialize SuperBot database tables."""
    init_database(_db_path)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Pipeline Traces table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_traces (
            trace_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            stages_json TEXT NOT NULL,
            market_snapshot_id TEXT,
            indicator_snapshot_id TEXT,
            structure_snapshot_id TEXT,
            understanding_id TEXT,
            structural_snapshot_id TEXT,
            trading_plan_id TEXT,
            authorization_id TEXT,
            position_id TEXT,
            position_size TEXT,
            darwin_recommendation_json TEXT
        )
    """)
    
    # Supertrend Lines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supertrend_lines (
            line_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            trend_direction TEXT NOT NULL,
            start_timestamp INTEGER NOT NULL,
            end_timestamp INTEGER,
            start_price REAL NOT NULL,
            current_price REAL NOT NULL,
            points_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            strength INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)
    
    # Supertrend Points table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supertrend_points (
            point_id TEXT PRIMARY KEY,
            line_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            price REAL NOT NULL,
            trend_direction TEXT NOT NULL,
            atr_value REAL NOT NULL,
            multiplier REAL NOT NULL,
            timeframe TEXT NOT NULL,
            symbol TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (line_id) REFERENCES supertrend_lines(line_id)
        )
    """)
    
    # Execution Tracks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_tracks (
            execution_id TEXT PRIMARY KEY,
            pipeline_trace_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL,
            position_size REAL NOT NULL,
            pnl REAL,
            pnl_percent REAL,
            status TEXT NOT NULL,
            entry_timestamp TEXT NOT NULL,
            exit_timestamp TEXT,
            exit_reason TEXT,
            duration_seconds INTEGER,
            river_learning_json TEXT,
            darwin_recommendation_json TEXT,
            FOREIGN KEY (pipeline_trace_id) REFERENCES pipeline_traces(trace_id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traces_symbol ON pipeline_traces(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traces_timestamp ON pipeline_traces(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lines_symbol_tf ON supertrend_lines(symbol, timeframe)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_points_line_id ON supertrend_points(line_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_symbol ON execution_tracks(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_executions_status ON execution_tracks(status)")
    
    conn.commit()
    conn.close()


def candle_to_dict(candle: Candle) -> Dict[str, Any]:
    """Convert Candle to dictionary."""
    return {
        "symbol": candle.symbol,
        "timeframe": candle.timeframe.value,
        "timestamp": candle.timestamp,
        "open": float(candle.open),
        "high": float(candle.high),
        "low": float(candle.low),
        "close": float(candle.close),
        "volume": float(candle.volume),
    }


def fetch_binance_candles(symbol: str, timeframe: Timeframe, start_date: str, 
                          end_date: str, limit: int = 1000) -> List[Candle]:
    """Fetch candles from Binance Futures API."""
    client = BinanceClient()
    
    # Convert timeframe to Binance interval
    interval_map = {
        Timeframe.M1: "1m",
        Timeframe.M5: "5m",
        Timeframe.M15: "15m",
        Timeframe.H1: "1h",
        Timeframe.H4: "4h",
        Timeframe.D1: "1d",
    }
    
    interval = interval_map.get(timeframe, "4h")
    
    # Convert dates to milliseconds
    start_ms = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_ms = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
    
    candles = []
    current_start = start_ms
    
    while current_start < end_ms and len(candles) < limit:
        klines = client._client.futures_klines(
            symbol=symbol,
            interval=interval,
            startTime=current_start,
            endTime=end_ms,
            limit=min(1000, limit - len(candles))
        ) if client._client else []
        
        if not klines:
            break
            
        for k in klines:
            candle = Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=int(k[0]),
                open=Decimal(str(k[1])),
                high=Decimal(str(k[2])),
                low=Decimal(str(k[3])),
                close=Decimal(str(k[4])),
                volume=Decimal(str(k[5])),
            )
            candles.append(candle)
        
        # Move to next batch
        if klines:
            current_start = int(klines[-1][0]) + 1
    
    return candles


def extract_supertrend_data(struct_snap: StructureSnapshot) -> List[Dict[str, Any]]:
    """Extract supertrend lines and points from structure snapshot."""
    lines_data = []
    
    if hasattr(struct_snap, 'supertrend_lines') and struct_snap.supertrend_lines:
        for line in struct_snap.supertrend_lines:
            line_data = {
                "line_id": getattr(line, 'line_id', f"line_{datetime.now().timestamp()}"),
                "timeframe": struct_snap.timeframe,
                "symbol": struct_snap.symbol,
                "trend_direction": getattr(line, 'trend_direction', 'UP'),
                "start_timestamp": getattr(line, 'start_timestamp', 0),
                "end_timestamp": getattr(line, 'end_timestamp', None),
                "start_price": float(getattr(line, 'start_price', 0)),
                "current_price": float(getattr(line, 'current_price', 0)),
                "points_count": len(getattr(line, 'points', [])),
                "is_active": getattr(line, 'is_active', True),
                "strength": getattr(line, 'strength', 1),
            }
            lines_data.append(line_data)
    
    return lines_data


# Initialize database on startup
init_superbot_db()


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API Root."""
    return {
        "message": "SuperBot API - Complete Pipeline Tracking System",
        "version": "1.0.0",
        "endpoints": {
            "fetch_candles": "POST /api/v1/candles/fetch",
            "run_pipeline": "POST /api/v1/pipeline/run",
            "get_pipeline_traces": "GET /api/v1/pipeline/traces",
            "get_supertrend_lines": "GET /api/v1/supertrend/lines",
            "get_supertrend_points": "GET /api/v1/supertrend/points/{line_id}",
            "get_river_learning": "GET /api/v1/river/learning",
            "get_darwin_recommendations": "GET /api/v1/darwin/recommendations",
            "get_execution_tracks": "GET /api/v1/executions",
            "run_backtest": "POST /api/v1/backtest/run",
            "dashboard_stats": "GET /api/v1/dashboard/stats",
        }
    }


@app.post("/api/v1/candles/fetch", response_model=List[Dict[str, Any]])
async def fetch_candles(request: CandleRequest):
    """
    Fetch candles from Binance Futures API for specified date range.
    
    Supports all timeframes: M1, M5, M15, H1, H4, D1
    """
    try:
        # Parse timeframe
        tf_map = {
            "M1": Timeframe.M1,
            "M5": Timeframe.M5,
            "M15": Timeframe.M15,
            "H1": Timeframe.H1,
            "H4": Timeframe.H4,
            "D1": Timeframe.D1,
        }
        
        if request.timeframe not in tf_map:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe: {request.timeframe}")
        
        timeframe = tf_map[request.timeframe]
        
        # Fetch from Binance
        candles = fetch_binance_candles(
            symbol=request.symbol,
            timeframe=timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit
        )
        
        if not candles:
            raise HTTPException(status_code=404, detail="No candles found for specified range")
        
        return [candle_to_dict(c) for c in candles]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candles: {str(e)}")


@app.post("/api/v1/pipeline/run", response_model=PipelineTraceResponse)
async def run_pipeline(
    symbol: str = Query(..., description="Trading symbol (e.g., BTCUSDT)"),
    timeframe: str = Query("H4", description="Timeframe"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    strategy: str = Query("LONG_ONLY", description="Strategy: LONG_ONLY, SHORT_ONLY, SIDEWAY_ONLY"),
    initial_balance: float = Query(10000.0, description="Initial balance"),
    risk_method: str = Query("fixed_fraction", description="Risk method"),
    leverage: float = Query(10.0, description="Leverage"),
):
    """
    Run complete pipeline (C001-C012) for specified date range with strategy selection.
    
    Strategies:
    - LONG_ONLY: Only builds long trading plans using LongBuilder
    - SHORT_ONLY: Only builds short trading plans using ShortBuilder  
    - SIDEWAY_ONLY: Only builds sideway grid strategies using SidewayBuilder
    
    Tracks all stages and stores results for traceability.
    Supports multi-coin (any Binance Futures symbol).
    Backend uses UTC, dashboard displays WIB (UTC+7).
    """
    try:
        # Validate strategy
        valid_strategies = ["LONG_ONLY", "SHORT_ONLY", "SIDEWAY_ONLY"]
        if strategy not in valid_strategies:
            raise HTTPException(status_code=400, detail=f"Invalid strategy. Choose from: {valid_strategies}")
        
        # Parse timeframe
        tf_map = {"M1": Timeframe.M1, "M5": Timeframe.M5, "M15": Timeframe.M15,
                  "H1": Timeframe.H1, "H4": Timeframe.H4, "D1": Timeframe.D1}
        
        if timeframe not in tf_map:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe: {timeframe}")
        
        tf = tf_map[timeframe]
        
        # Fetch candles from Binance Futures API
        candles = fetch_binance_candles(symbol, tf, start_date, end_date, limit=1000)
        
        if not candles:
            raise HTTPException(status_code=404, detail="No candles found")
        
        # Create observer and pipeline
        observer = SimulationObserver()
        pipeline = Pipeline(observer, initial_balance=Decimal(str(initial_balance)))
        
        # Run pipeline on latest candle
        candles_dict = {tf: candles}
        result = pipeline.run(symbol, [tf], candles_dict, risk_method=risk_method)
        
        # Apply strategy filter to trading plan if exists
        if result.trading_plan and strategy != "LONG_ONLY":
            # For SHORT_ONLY and SIDEWAY_ONLY, we rebuild the plan with appropriate builder
            if result.structural_snapshot:
                snap = result.structural_snapshot
                leverage_dec = Decimal(str(leverage))
                
                if strategy == "SHORT_ONLY":
                    builder = ShortBuilder()
                    new_plan = builder.build(snap, leverage_dec)
                    result.trading_plan = new_plan
                elif strategy == "SIDEWAY_ONLY":
                    builder = SidewayBuilder()
                    new_plan, _ = builder.build(snap, leverage_dec)
                    result.trading_plan = new_plan
        
        # Store trace
        trace_id = f"trace_{datetime.now().timestamp()}"
        
        stages = {
            "C001_Observe": result.market_snapshot is not None,
            "C002_Measure": result.indicator_snapshot is not None,
            "C003_Engine": result.structure_snapshot is not None,
            "C004_Preserve": result.structure_snapshot is not None,
            "C005_Remember": True,
            "C006_Select": result.understanding is not None,
            "C007_Understand": result.understanding is not None,
            "C008_Classify": result.structural_snapshot is not None,
            "C009_TradingPlan": result.trading_plan is not None,
            "C010_RiverReview": True,
            "C011_Authorize": result.authorization is not None,
            "C012_Execute": result.position_id is not None,
        }
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        darwin_rec_dict = None
        if result.darwin_recommendation:
            darwin_rec_dict = {
                "recommendation_id": result.darwin_recommendation.recommendation_id,
                "state": result.darwin_recommendation.state.value if hasattr(result.darwin_recommendation.state, 'value') else str(result.darwin_recommendation.state),
                "adjustments": result.darwin_recommendation.adjustments,
                "confidence": float(result.darwin_recommendation.confidence),
            }
        
        cursor.execute("""
            INSERT INTO pipeline_traces 
            (trace_id, timestamp, symbol, timeframe, stages_json, market_snapshot_id,
             indicator_snapshot_id, structure_snapshot_id, understanding_id,
             structural_snapshot_id, trading_plan_id, authorization_id, position_id,
             position_size, darwin_recommendation_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trace_id,
            datetime.now().isoformat(),
            symbol,
            timeframe,
            json.dumps(stages),
            getattr(result.market_snapshot, 'snapshot_id', None) if result.market_snapshot else None,
            getattr(result.indicator_snapshot, 'snapshot_id', None) if result.indicator_snapshot else None,
            getattr(result.structure_snapshot, 'snapshot_id', None) if result.structure_snapshot else None,
            getattr(result.understanding, 'snapshot_id', None) if result.understanding else None,
            getattr(result.structural_snapshot, 'snapshot_id', None) if result.structural_snapshot else None,
            getattr(result.trading_plan, 'plan_id', None) if result.trading_plan else None,
            getattr(result.authorization, 'auth_id', None) if result.authorization else None,
            result.position_id,
            str(result.position_size),
            json.dumps(darwin_rec_dict) if darwin_rec_dict else None,
        ))
        
        # Track execution if position opened
        if result.position_id and result.trading_plan:
            exec_id = f"exec_{datetime.now().timestamp()}"
            cursor.execute("""
                INSERT INTO execution_tracks
                (execution_id, pipeline_trace_id, plan_id, symbol, direction,
                 entry_price, position_size, status, entry_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                exec_id,
                trace_id,
                getattr(result.trading_plan, 'plan_id', 'unknown'),
                symbol,
                result.trading_plan.direction.value if hasattr(result.trading_plan.direction, 'value') else result.trading_plan.direction,
                float(result.trading_plan.entry_price) if result.trading_plan.entry_price else 0,
                float(result.position_size),
                "OPEN",
                datetime.now().isoformat(),
            ))
        
        conn.commit()
        conn.close()
        
        return PipelineTraceResponse(
            pipeline_id=trace_id,
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            timeframe=timeframe,
            strategy=strategy,
            stages=stages,
            market_snapshot_id=getattr(result.market_snapshot, 'snapshot_id', None) if result.market_snapshot else None,
            indicator_snapshot_id=getattr(result.indicator_snapshot, 'snapshot_id', None) if result.indicator_snapshot else None,
            structure_snapshot_id=getattr(result.structure_snapshot, 'snapshot_id', None) if result.structure_snapshot else None,
            understanding_id=getattr(result.understanding, 'snapshot_id', None) if result.understanding else None,
            structural_snapshot_id=getattr(result.structural_snapshot, 'snapshot_id', None) if result.structural_snapshot else None,
            trading_plan_id=getattr(result.trading_plan, 'plan_id', None) if result.trading_plan else None,
            authorization_id=getattr(result.authorization, 'auth_id', None) if result.authorization else None,
            position_id=result.position_id,
            position_size=str(result.position_size),
            darwin_recommendation=darwin_rec_dict,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


@app.get("/api/v1/pipeline/traces", response_model=List[PipelineTraceResponse])
async def get_pipeline_traces(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    timeframe: Optional[str] = Query(None, description="Filter by timeframe"),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all pipeline traces with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM pipeline_traces WHERE 1=1"
    params = []
    
    if symbol:
        query += " AND symbol = ?"
        params.append(symbol)
    
    if timeframe:
        query += " AND timeframe = ?"
        params.append(timeframe)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    traces = []
    for row in rows:
        darwin_rec = json.loads(row["darwin_recommendation_json"]) if row["darwin_recommendation_json"] else None
        traces.append(PipelineTraceResponse(
            pipeline_id=row["trace_id"],
            timestamp=row["timestamp"],
            symbol=row["symbol"],
            timeframe=row["timeframe"],
            strategy="LONG_ONLY",  # Default, can be enhanced to store in DB
            stages=json.loads(row["stages_json"]),
            market_snapshot_id=row["market_snapshot_id"],
            indicator_snapshot_id=row["indicator_snapshot_id"],
            structure_snapshot_id=row["structure_snapshot_id"],
            understanding_id=row["understanding_id"],
            structural_snapshot_id=row["structural_snapshot_id"],
            trading_plan_id=row["trading_plan_id"],
            authorization_id=row["authorization_id"],
            position_id=row["position_id"],
            position_size=row["position_size"],
            darwin_recommendation=darwin_rec,
        ))
    
    return traces


@app.get("/api/v1/supertrend/lines", response_model=List[SupertrendLineResponse])
async def get_supertrend_lines(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    timeframe: Optional[str] = Query(None, description="Filter by timeframe"),
    active_only: bool = Query(False, description="Show only active lines"),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get all Supertrend lines across all timeframes.
    Fully traceable with complete history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM supertrend_lines WHERE 1=1"
    params = []
    
    if symbol:
        query += " AND symbol = ?"
        params.append(symbol)
    
    if timeframe:
        query += " AND timeframe = ?"
        params.append(timeframe)
    
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY start_timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    lines = []
    for row in rows:
        lines.append(SupertrendLineResponse(
            line_id=row["line_id"],
            timeframe=row["timeframe"],
            symbol=row["symbol"],
            trend_direction=row["trend_direction"],
            start_timestamp=row["start_timestamp"],
            end_timestamp=row["end_timestamp"],
            start_price=row["start_price"],
            current_price=row["current_price"],
            points_count=row["points_count"],
            is_active=bool(row["is_active"]),
            strength=row["strength"],
        ))
    
    return lines


@app.get("/api/v1/supertrend/points/{line_id}", response_model=List[SupertrendPointResponse])
async def get_supertrend_points(line_id: str):
    """Get all points for a specific Supertrend line."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM supertrend_points 
        WHERE line_id = ? 
        ORDER BY timestamp ASC
    """, (line_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    points = []
    for row in rows:
        points.append(SupertrendPointResponse(
            point_id=row["point_id"],
            line_id=row["line_id"],
            timestamp=row["timestamp"],
            price=row["price"],
            trend_direction=row["trend_direction"],
            atr_value=row["atr_value"],
            multiplier=row["multiplier"],
            timeframe=row["timeframe"],
            symbol=row["symbol"],
        ))
    
    return points


@app.get("/api/v1/river/learning", response_model=RiverLearningResponse)
async def get_river_learning():
    """
    Get current River learning state.
    Tracks all learned patterns from past trades.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate metrics from execution tracks
    cursor.execute("""
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losses,
            SUM(pnl) as total_pnl,
            AVG(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as avg_win,
            AVG(CASE WHEN pnl <= 0 THEN pnl ELSE 0 END) as avg_loss,
            MAX(pnl) as best_trade,
            MIN(pnl) as worst_trade
        FROM execution_tracks
        WHERE status = 'CLOSED'
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    total = row["total_trades"] or 0
    wins = row["wins"] or 0
    losses = row["losses"] or 0
    total_pnl = row["total_pnl"] or 0.0
    avg_win = row["avg_win"] or 0.0
    avg_loss = abs(row["avg_loss"] or 0.0)
    
    win_rate = wins / total if total > 0 else 0.0
    profit_factor = abs(avg_win / avg_loss) if avg_loss > 0 else 0.0
    
    # Get learned patterns (simplified)
    patterns = []
    
    return RiverLearningResponse(
        snapshot_id=f"river_{datetime.now().timestamp()}",
        total_trades=total,
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        total_pnl=total_pnl,
        profit_factor=profit_factor,
        avg_win=avg_win,
        avg_loss=avg_loss,
        best_trade=row["best_trade"] or 0.0,
        worst_trade=row["worst_trade"] or 0.0,
        consecutive_wins=0,  # Would need more complex tracking
        consecutive_losses=0,
        patterns_learned=patterns,
    )


@app.get("/api/v1/darwin/recommendations", response_model=List[DarwinRecommendationResponse])
async def get_darwin_recommendations(limit: int = Query(50, ge=1, le=500)):
    """Get Darwin recommendations and adjustments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT darwin_recommendation_json, timestamp 
        FROM pipeline_traces 
        WHERE darwin_recommendation_json IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    recs = []
    for row in rows:
        darwin_data = json.loads(row["darwin_recommendation_json"])
        recs.append(DarwinRecommendationResponse(
            recommendation_id=f"darwin_{row['timestamp']}",
            timestamp=row["timestamp"],
            state=darwin_data.get("state", "UNKNOWN"),
            adjustments=darwin_data.get("adjustments", {}),
            confidence=darwin_data.get("confidence", 0.0),
            reasoning=darwin_data.get("reasoning", ""),
        ))
    
    return recs


@app.get("/api/v1/executions", response_model=List[ExecutionTrackResponse])
async def get_execution_tracks(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    status: Optional[str] = Query(None, description="Filter by status (OPEN/CLOSED)"),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get all execution tracks.
    Complete traceability of every trade executed by the bot.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM execution_tracks WHERE 1=1"
    params = []
    
    if symbol:
        query += " AND symbol = ?"
        params.append(symbol)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY entry_timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    executions = []
    for row in rows:
        executions.append(ExecutionTrackResponse(
            execution_id=row["execution_id"],
            pipeline_trace_id=row["pipeline_trace_id"],
            plan_id=row["plan_id"],
            symbol=row["symbol"],
            direction=row["direction"],
            entry_price=row["entry_price"],
            exit_price=row["exit_price"],
            position_size=row["position_size"],
            pnl=row["pnl"],
            pnl_percent=row["pnl_percent"],
            status=row["status"],
            entry_timestamp=row["entry_timestamp"],
            exit_timestamp=row["exit_timestamp"],
            exit_reason=row["exit_reason"],
            duration_seconds=row["duration_seconds"],
        ))
    
    return executions


@app.post("/api/v1/backtest/run", response_model=BacktestResultResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run backtest for specified date range.
    Uses complete pipeline with all stages tracked.
    """
    try:
        # Parse timeframes
        tf_map = {"M1": Timeframe.M1, "M5": Timeframe.M5, "M15": Timeframe.M15,
                  "H1": Timeframe.H1, "H4": Timeframe.H4, "D1": Timeframe.D1}
        
        timeframes = [tf_map[tf] for tf in request.timeframes if tf in tf_map]
        
        if not timeframes:
            raise HTTPException(status_code=400, detail="No valid timeframes provided")
        
        # Fetch candles for each timeframe
        all_candles = {}
        for tf in timeframes:
            candles = fetch_binance_candles(
                request.symbol, tf,
                request.start_date, request.end_date,
                limit=2000
            )
            all_candles[tf] = candles
        
        if not any(all_candles.values()):
            raise HTTPException(status_code=404, detail="No candles found for backtest period")
        
        # Run backtest
        engine = BacktestEngine(initial_balance=Decimal(str(request.initial_balance)))
        result = engine.run(request.symbol, all_candles, step=1)
        
        # Convert trades to execution tracks
        trades = []
        for i, trade in enumerate(result.trades or []):
            trades.append(ExecutionTrackResponse(
                execution_id=f"backtest_trade_{i}",
                pipeline_trace_id=f"backtest_{request.start_date}_{request.end_date}",
                plan_id=f"plan_{i}",
                symbol=trade.symbol if hasattr(trade, 'symbol') else request.symbol,
                direction=trade.direction.value if hasattr(trade.direction, 'value') else trade.direction,
                entry_price=float(trade.entry_price),
                exit_price=float(trade.exit_price),
                position_size=float(trade.position_size) if hasattr(trade, 'position_size') else 0,
                pnl=float(trade.pnl),
                pnl_percent=float(trade.pnl_percent),
                status="CLOSED",
                entry_timestamp=datetime.fromtimestamp(trade.timestamp).isoformat() if hasattr(trade, 'timestamp') else datetime.now().isoformat(),
                exit_timestamp=None,
                exit_reason=None,
                duration_seconds=None,
            ))
        
        # Convert equity curve
        equity_curve = [float(e) for e in result.equity_curve]
        
        backtest_id = f"backtest_{datetime.now().timestamp()}"
        
        return BacktestResultResponse(
            backtest_id=backtest_id,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            total_trades=result.total_trades,
            wins=result.metrics.wins if hasattr(result.metrics, 'wins') else 0,
            losses=result.metrics.losses if hasattr(result.metrics, 'losses') else 0,
            win_rate=result.metrics.win_rate,
            total_pnl=float(result.final_balance - Decimal(str(request.initial_balance))),
            final_balance=float(result.final_balance),
            max_drawdown=result.metrics.max_drawdown if hasattr(result.metrics, 'max_drawdown') else 0.0,
            sharpe_ratio=result.metrics.sharpe_ratio if hasattr(result.metrics, 'sharpe_ratio') else None,
            trades=trades,
            equity_curve=equity_curve,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")


@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics.
    All pipeline data in one endpoint for real-time dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Pipeline stats
    cursor.execute("SELECT COUNT(*) FROM pipeline_traces")
    total_pipelines = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pipeline_traces WHERE position_id IS NOT NULL")
    executed_pipelines = cursor.fetchone()[0]
    
    # Execution stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_positions,
            SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_positions,
            SUM(pnl) as total_pnl
        FROM execution_tracks
    """)
    exec_row = cursor.fetchone()
    
    # Win rate
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as win_rate
        FROM execution_tracks
        WHERE status = 'CLOSED' AND COUNT(*) > 0
    """)
    win_rate_row = cursor.fetchone()
    
    # Supertrend lines stats
    cursor.execute("SELECT COUNT(*) FROM supertrend_lines")
    total_lines = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM supertrend_lines WHERE is_active = 1")
    active_lines = cursor.fetchone()[0]
    
    # Supertrend points stats
    cursor.execute("SELECT COUNT(*) FROM supertrend_points")
    total_points = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "pipelines": {
            "total": total_pipelines,
            "executed": executed_pipelines,
            "success_rate": executed_pipelines / total_pipelines if total_pipelines > 0 else 0,
        },
        "executions": {
            "total": exec_row["total"] or 0,
            "open_positions": exec_row["open_positions"] or 0,
            "closed_positions": exec_row["closed_positions"] or 0,
            "total_pnl": exec_row["total_pnl"] or 0.0,
            "win_rate": win_rate_row["win_rate"] or 0.0,
        },
        "supertrend": {
            "total_lines": total_lines,
            "active_lines": active_lines,
            "total_points": total_points,
        },
        "learning": {
            "river_total_trades": exec_row["closed_positions"] or 0,
            "darwin_recommendations_count": 0,  # Would need separate count
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
