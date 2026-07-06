# ST-LMS Quick Reference Guide

## 📊 Summary Statistics

- **Total Files:** 130 Python files
- **Total Modules:** 32 modules
- **Total Classes:** 136 classes
- **Total Public Functions:** 250 functions
- **Total Module Variables:** 220 variables

---

## 🔑 Core Pipeline Components (C001-C012)

### C001 - OBSERVE Layer
**Location:** `st_lms/observe/`

| Class/Function | Purpose |
|----------------|---------|
| `Observer` (base class) | Base observer interface |
| `BinanceObserver` | Live market data from Binance |
| `SimulationObserver` | Simulated market data |
| `WebSocketObserver` | WebSocket connection handler |
| `LivePipeline` | Production pipeline orchestrator |

### C002 - MEASURE Layer
**Location:** `st_lms/measure/`

| Class/Function | Purpose |
|----------------|---------|
| `Orchestrator` | Coordinates all calculators |
| `ATRCalculator` | Calculate Average True Range |
| `SupertrendCalculator` | Calculate Supertrend indicator |
| `MACDCalculator` | Calculate MACD indicator |
| `VolatilityCalculator` | Market volatility metrics |
| `OIIDeltaCalculator` | Open Interest delta |
| `PriceMomentumCalculator` | Price momentum analysis |

### C003 - PRESERVE Layer
**Location:** `st_lms/preserve/`

| Class/Function | Purpose |
|----------------|---------|
| `Preserver` | Build Supertrend Lines |
| `LineStatusManager` | Manage line lifecycle |

### C004 - REMEMBER Layer
**Location:** `st_lms/remember/`

| Class/Function | Purpose |
|----------------|---------|
| `Memory` | Historical data storage |
| `HistoricalRepository` | Query historical structures |

### C005 - SELECT Layer
**Location:** `st_lms/select/`

| Class/Function | Purpose |
|----------------|---------|
| `Selector` | Select relevant structures |
| `AdaptiveStack` | Stack of candidates |

### C006 - UNDERSTAND Layer
**Location:** `st_lms/understand/`

| Class/Function | Purpose |
|----------------|---------|
| `GeometryAnalyzer` | Analyze structure geometry |

### C007 - CLASSIFY Layer
**Location:** `st_lms/classify/`

| Class/Function | Purpose |
|----------------|---------|
| `Classifier` | Classify market regime |

### C008 - TRADING PLAN Layer
**Location:** `st_lms/trading_plan/`

| Class/Function | Purpose |
|----------------|---------|
| `Planner` | Create trading plans |
| `PlanManager` | Manage plan lifecycle |
| `PlanRepository` | Store/retrieve plans |
| `PlanValidator` | Validate plans |
| `LongBuilder` | Build LONG plans |
| `ShortBuilder` | Build SHORT plans |
| `SidewayBuilder` | Build SIDEWAY plans |
| `AdaptiveGrid` | Dynamic grid system |

### C009 - RIVER REVIEW Layer
**Location:** `st_lms/river/`

| Class/Function | Purpose |
|----------------|---------|
| `RiverReview` | Performance review system |
| `RiverEntry` | Entry analysis |
| `RiverExit` | Exit analysis |
| `RiverLearning` | Learn from trades |
| `OpportunityLearning` | Opportunity analysis |
| `SharedLearningRepository` | Shared knowledge base |

### C010 - AUTHORIZE Layer
**Location:** `st_lms/authorize/`

| Class/Function | Purpose |
|----------------|---------|
| `AuthorizationGateway` | Final trade approval |

### C011 - EXECUTE Layer
**Location:** `st_lms/execute/`

| Class/Function | Purpose |
|----------------|---------|
| `Executor` (base) | Base execution interface |
| `LiveExecutor` | Live trading execution |
| `TestnetExecutor` | Testnet execution |
| `SimulationExecutor` | Simulation mode |
| `OrderManager` | Order lifecycle management |

### C012 - RISK MANAGE Layer
**Location:** `st_lms/risk/`

| Class/Function | Purpose |
|----------------|---------|
| `RiskManager` | Risk calculations & limits |

### C013 - DARWIN OPTIMIZE Layer
**Location:** `st_lms/darwin/`

| Class/Function | Purpose |
|----------------|---------|
| `DarwinEngine` | Adaptive optimization |

---

## 📦 Key Models

**Location:** `st_lms/models/`

| Model | Purpose |
|-------|---------|
| `Candle` | OHLCV candle data |
| `MarketSnapshot` | Market state at point in time |
| `IndicatorSnapshot` | All indicators values |
| `StructureSnapshot` | Structural analysis state |
| `SupertrendPoint` | Individual Supertrend point |
| `SupertrendLine` | Complete Supertrend line |
| `SupertrendWave` | Wave of Supertrend lines |
| `TradingPlan` | Complete trading plan |
| `Position` | Active/open position |
| `Order` | Order details |
| `Authorization` | Trade authorization record |
| `MarketUnderstanding` | Geometry analysis result |
| `RiverState` | River learning state |
| `LearningSnapshot` | Performance snapshot |
| `DarwinRecommendation` | Optimization suggestion |
| `DarwinState` | Darwin engine state |
| `OpenInterest` | OI data |
| `ATR` | ATR values |
| `MACD` | MACD values |
| `Metrics` | Performance metrics |
| `Provenance` | Data lineage tracking |
| `BacktestResult` | Backtest results |

---

## ⚙️ Configuration Files

**Location:** `st_lms/config/`

| Variable | Purpose |
|----------|---------|
| `CORE_CONFIG` | Core system settings |
| `TRADING_CONFIG` | Trading parameters |
| `SUPERTREND_CONFIG` | Supertrend settings |
| `EXCHANGE_CONFIG` | Exchange credentials |

---

## 🔧 Utility Functions

**Location:** `st_lms/utils/`

| Function | Purpose |
|----------|---------|
| `generate_plan_id()` | Generate unique plan ID |
| `generate_line_id(symbol, price)` | Generate line ID |
| `generate_point_id()` | Generate point ID |
| `generate_snapshot_id(prefix)` | Generate snapshot ID |
| `generate_grid_id()` | Generate grid ID |
| `generate_trade_id()` | Generate trade ID |
| `generate_authorization_id()` | Generate auth ID |
| `get_logger()` | Get logger instance |
| `setup_logging(level)` | Configure logging |

---

## 🚀 Entry Points

| File | Purpose |
|------|---------|
| `main.py` | Main application entry |
| `run_bot.py` | Bot runner script |
| `main_server.py` | API server |
| `pipeline.py` | Core pipeline logic |
| `improve.py` | Improvement utilities |

---

## 🧪 Testing

**Location:** `st_lms/tests/`

| Test Module | Coverage |
|-------------|----------|
| `test_models.py` | All models |
| `test_measure.py` | Measure layer |
| `test_classifier.py` | Classification |
| `test_trading_plan.py` | Plan generation |
| `test_adaptive_grid.py` | Grid system |
| `test_pipeline_flow.py` | Integration tests |
| `test_constitution/` | Constitution rules |
| `test_structure/` | Structure tests |
| `test_stress/` | Stress tests |

---

## 🌐 API & Dashboard

**Location:** `st_lms/api/`, `st_lms/dashboard/`

| Component | Purpose |
|-----------|---------|
| `SuperbotAPI` | REST API endpoints |
| `DashboardServer` | Web dashboard |
| `SuperbotDashboard` | Main dashboard UI |
| `App` | Streamlit dashboard |

---

## 💾 Persistence

**Location:** `st_lms/persistence/`

| Class | Purpose |
|-------|---------|
| `BaseRepository` | Abstract repository |
| `SQLiteRepository` | SQLite implementation |

---

## 📈 Multi-Timeframe Engine

**Location:** `st_lms/multi_timeframe_structural_engine/`

| Component | Purpose |
|-----------|---------|
| `Engine` | MTF analysis coordinator |
| `SupertrendLine` | MTF line builder |

---

## 🔄 Exchange Integration

**Location:** `st_lms/exchange/`

| Class | Purpose |
|-------|---------|
| `ExchangeService` | Exchange abstraction |
| `BinanceClient` | Binance API client |
| `BinanceService` | Binance service layer |

---

## 📝 Common Utilities

**Location:** `st_lms/common/`

| Module | Purpose |
|--------|---------|
| `enums.py` | System enums (Timeframe, Trend, etc.) |
| `types.py` | Type definitions |
| `datetime_utils.py` | Date/time utilities |
| `math_utils.py` | Math helpers |
| `price_utils.py` | Price calculations |
| `core_constants.py` | System constants |

---

## 🎯 Five Absolute Principles (Constitution)

1. **Trend Authority** - Higher timeframe trend dominates
2. **Multi-TF Conflict Detection** - Detect conflicting signals
3. **Liquidation Hardstop** - Prevent liquidation scenarios
4. **Structure Integrity** - Maintain structural validity
5. **Risk First** - Risk management before profit

---

## 📖 Full Documentation

For complete details with all 136 classes, 250 functions, and 220 variables:
- See `/workspace/st_lms/VARIABLES_FUNCTIONS_REFERENCE.md` (3675 lines)
- See `/workspace/st_lms/PIPELINE_ARCHITECTURE.md` for pipeline flow

---

**Generated:** $(date)
**Project:** ST-LMS (Supertrend Learning Management System)
