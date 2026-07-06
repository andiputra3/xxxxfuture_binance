#!/usr/bin/env python3
"""
ST_LMS Main Server
Port Default: 8084
Mode: Simulator, Testnet, Live
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from pydantic import BaseModel

# Import ST_LMS Core Components
# Note: Ensure these paths match your actual project structure
try:
    from st_lms.common.enums import StructuralState, AuthorizationStatus, RiverState
    from st_lms.common.core_constants import MAX_DAILY_DRAWDOWN
    from st_lms.pipeline.engine import PipelineEngine  # Asumsi ada engine utama
    from st_lms.simulation.backtest_engine import BacktestEngine
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}")
    print("Running in Mock Mode for demonstration.")

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ST_LMS_Server")

app = FastAPI(title="ST_LMS Trading Bot API", version="1.0.0")

# Enable CORS for Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State (In-Memory for now, replace with DB in production)
class BotState:
    def __init__(self):
        self.mode = "simulator"
        self.is_running = False
        self.current_price = Decimal("0.0")
        self.structural_state = StructuralState.SIDEWAY
        self.authorization_status = AuthorizationStatus.REJECTED
        self.river_state = RiverState.COLLECTING
        self.account_balance = Decimal("10000.00")
        self.daily_pnl = Decimal("0.00")
        self.trade_history = []
        self.pipeline_logs = []
        self.last_update = datetime.now()

bot_state = BotState()

# --- Pydantic Models for API ---
class ControlCommand(BaseModel):
    action: str  # start, stop, pause
    mode: Optional[str] = None

class TradeHistoryItem(BaseModel):
    timestamp: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    pnl: float
    status: str

# --- API Endpoints ---

@app.get("/")
def root():
    return {"status": "online", "service": "ST_LMS Core", "version": "1.0.0"}

@app.get("/status")
def get_status():
    """Get real-time bot status for dashboard"""
    return {
        "mode": bot_state.mode,
        "is_running": bot_state.is_running,
        "current_price": str(bot_state.current_price),
        "structural_state": bot_state.structural_state.value,
        "authorization_status": bot_state.authorization_status.value,
        "river_state": bot_state.river_state.value,
        "account_balance": str(bot_state.account_balance),
        "daily_pnl": str(bot_state.daily_pnl),
        "last_update": bot_state.last_update.isoformat()
    }

@app.get("/pipeline/logs")
def get_pipeline_logs(limit: int = 50):
    """Get recent pipeline execution logs"""
    return bot_state.pipeline_logs[-limit:]

@app.get("/trades/history")
def get_trade_history():
    """Get full trade history"""
    return bot_state.trade_history

@app.get("/learning/river")
def get_river_learning():
    """Get River learning stats and opportunity cost"""
    # Mock data - replace with actual River engine stats
    return {
        "state": bot_state.river_state.value,
        "confidence": 0.75,
        "patterns_learned": 142,
        "opportunity_cost_tracked": 23,
        "false_negatives": 5,
        "false_positives": 8
    }

@app.get("/learning/darwin")
def get_darwin_stats():
    """Get Darwin improvement stats"""
    return {
        "state": "STABLE",
        "improvements_applied": 3,
        "pending_validations": 0,
        "strategy_rotation_signal": "NONE"
    }

@app.post("/control")
async def control_bot(cmd: ControlCommand):
    """Control bot execution (start/stop/pause)"""
    global bot_state
    
    if cmd.action == "start":
        bot_state.is_running = True
        if cmd.mode:
            bot_state.mode = cmd.mode
        logger.info(f"Bot started in {bot_state.mode} mode")
        return {"status": "started", "mode": bot_state.mode}
    
    elif cmd.action == "stop":
        bot_state.is_running = False
        logger.info("Bot stopped")
        return {"status": "stopped"}
    
    elif cmd.action == "pause":
        bot_state.is_running = False # Temporary pause
        return {"status": "paused"}
    
    raise HTTPException(status_code=400, detail="Invalid action")

# --- Background Simulation Loop ---
async def simulation_loop():
    """Simulates market data processing and pipeline execution"""
    logger.info("Simulation loop started")
    while True:
        if bot_state.is_running:
            try:
                # 1. Simulate Market Data (Mock)
                import random
                base_price = 50000.0
                fluctuation = random.uniform(-50, 50)
                bot_state.current_price = Decimal(str(base_price + fluctuation))
                
                # 2. Run Pipeline Step (Mock)
                # In real implementation: result = pipeline_engine.process(candle)
                
                # 3. Update State based on mock logic
                if fluctuation > 20:
                    bot_state.structural_state = StructuralState.UPTREND
                elif fluctuation < -20:
                    bot_state.structural_state = StructuralState.DOWNTREND
                else:
                    bot_state.structural_state = StructuralState.SIDEWAY
                
                # 4. Log Pipeline Activity
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "step": "C008_Classify",
                    "data": {"state": bot_state.structural_state.value},
                    "confidence": 0.85
                }
                bot_state.pipeline_logs.append(log_entry)
                if len(bot_state.pipeline_logs) > 100:
                    bot_state.pipeline_logs.pop(0)

                # 5. Simulate occasional trade
                if random.random() < 0.05: # 5% chance of trade per tick
                    trade = {
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "symbol": "BTCUSDT",
                        "side": "LONG" if bot_state.structural_state == StructuralState.UPTREND else "SHORT",
                        "entry_price": float(bot_state.current_price),
                        "exit_price": None,
                        "pnl": 0.0,
                        "status": "OPEN"
                    }
                    bot_state.trade_history.append(trade)
                    logger.info(f"Trade opened: {trade['side']} at {trade['entry_price']}")

            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
        
        await asyncio.sleep(1) # 1 second tick

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())
    logger.info("ST_LMS Server starting up...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ST_LMS Trading Bot Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8084, help="Port number")
    parser.add_argument("--mode", type=str, default="simulator", choices=["simulator", "testnet", "live"], help="Trading mode")
    
    args = parser.parse_args()
    
    bot_state.mode = args.mode
    logger.info(f"Starting server on {args.host}:{args.port} in {args.mode} mode")
    
    run(app, host=args.host, port=args.port)