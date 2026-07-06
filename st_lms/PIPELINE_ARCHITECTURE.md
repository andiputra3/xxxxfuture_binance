# ST-LMS Pipeline Architecture

## Overview

Proyek **ST-LMS (Supertrend Line Multi-Timeframe System)** adalah sistem trading algoritmik yang mengimplementasikan pipeline lengkap dari observasi pasar hingga eksekusi trading dengan prinsip-prinsip konstitusi yang ketat.

## Pipeline Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ST-LMS PIPELINE                                    │
│                         (Constitution Final v1.0)                               │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │   C001:      │
                                    │   OBSERVE    │
                                    │  (Observer)  │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ MarketSnapshot│
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   C002:      │
                                    │   MEASURE    │
                                    │(Orchestrator)│
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │IndicatorSnap │
                                    └──────┬───────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-TIMEFRAME ENGINE                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐               │
│     │   C003:      │      │   C004:      │      │   C005:      │               │
│     │   ENGINE     │─────▶│   PRESERVE   │─────▶│   REMEMBER   │               │
│     │ (Structural) │      │(Repository)  │      │   (Memory)   │               │
│     └──────┬───────┘      └──────────────┘      └──────┬───────┘               │
│            │                                           │                        │
│            ▼                                           ▼                        │
│     StructureSnapshot                            Historical Context              │
│            │                                           │                        │
│            └───────────────────┬───────────────────────┘                        │
│                                │                                                │
│                                ▼                                                │
│                         ┌──────────────┐                                        │
│                         │   C006:      │                                        │
│                         │   SELECT     │                                        │
│                         │  (Selector)  │                                        │
│                         └──────┬───────┘                                        │
│                                │                                                │
│                                ▼                                                │
│                         Candidate Line                                          │
│                                │                                                │
│                                ▼                                                │
│                         ┌──────────────┐                                        │
│                         │   C007:      │                                        │
│                         │  UNDERSTAND  │                                        │
│                         │  (Geometry)  │                                        │
│                         └──────┬───────┘                                        │
│                                │                                                │
│                                ▼                                                │
│                      MarketUnderstanding                                        │
│                                │                                                │
│                                ▼                                                │
│                         ┌──────────────┐                                        │
│                         │   C008:      │                                        │
│                         │  CLASSIFY    │                                        │
│                         │ (Classifier) │                                        │
│                         └──────┬───────┘                                        │
│                                │                                                │
│                                ▼                                                │
│                       StructuralState                                           │
│                                │                                                │
└────────────────────────────────┼────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TRADING PLAN PHASE                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐               │
│     │   C009:      │      │   C010:      │      │   C011:      │               │
│     │ TRADING PLAN │─────▶│ RIVER REVIEW │─────▶│  AUTHORIZE   │               │
│     │  (Planner)   │      │  (Review)    │      │  (Gateway)   │               │
│     └──────┬───────┘      └──────┬───────┘      └──────┬───────┘               │
│            │                     │                     │                        │
│            ▼                     ▼                     ▼                        │
│       TradingPlan          RiverState           Authorization                  │
│                                                                        │        │
└────────────────────────────────┼────────────────────────────────────────┼────────┘
                                 │                                        │
                                 └──────────────────┬─────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          EXECUTION & POST-TRADE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐               │
│     │   C012:      │      │   RISK       │      │   LEARN      │               │
│     │   EXECUTE    │─────▶│   MANAGE     │─────▶│ (RiverLearn) │               │
│     │  (Executor)  │      │   (Risk)     │      │   (Improve)  │               │
│     └──────┬───────┘      └──────────────┘      └──────┬───────┘               │
│            │                                           │                        │
│            ▼                                           ▼                        │
│        Position                                   Learning Data                 │
│            │                                           │                        │
│            ▼                                           │                        │
│     ┌──────────────┐                                   │                        │
│     │   DARWIN     │◀──────────────────────────────────┘                        │
│     │   ENGINE     │                                                            │
│     │ (Optimize)   │                                                            │
│     └──────────────┘                                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 5 Prinsip Mutlak (Constitution)

1. **Structure First**: Semua keputusan berasal dari Supertrend Line
2. **Plan Before Trade**: TradingPlan wajib dibuat sebelum eksekusi
3. **Review Before Authorize**: RiverReview wajib sebelum authorize
4. **Learn After Result**: improve() dipanggil setelah trade closed
5. **Improve Without Touching Core**: Darwin tidak mengubah formula ATR/ST/MACD

---

## Komponen Pipeline Detail

### C001: OBSERVE (Observer)

**File**: `st_lms/observe/observer.py`

**Fungsi**: Mengumpulkan data pasar dari berbagai sumber

**Komponen terkait**:
- `binance_observer.py` - Observer untuk data Binance live
- `websocket_observer.py` - Observer via WebSocket
- `simulation_observer.py` - Observer untuk backtest/simulasi
- `live_pipeline.py` - Pipeline untuk live trading

**Output**: `MarketSnapshot`

```python
market_snap = self._observer.observe(symbol, timeframes, candle_limit=100)
```

---

### C002: MEASURE (MeasureOrchestrator)

**File**: `st_lms/measure/orchestrator.py`

**Fungsi**: Menghitung semua indikator teknis

**Sub-komponen**:
| Indikator | File | Deskripsi |
|-----------|------|-----------|
| Supertrend | `supertrend_calculator.py` | Trend following indicator |
| ATR | `atr_calculator.py` | Average True Range (volatility) |
| MACD | `macd_calculator.py` | Moving Average Convergence Divergence |
| Open Interest | `open_interest_calculator.py` | Data kontrak terbuka |
| OI Delta | `oi_delta_calculator.py` | Perubahan open interest |
| Volatility | `volatility_calculator.py` | Kalkulator volatilitas |
| Price Momentum | `price_momentum_calculator.py` | Momentum harga |

**Output**: `IndicatorSnapshot`

```python
indicator_snap = self._measure.measure(market_snap, candles)
```

---

### C003: ENGINE (MultiTimeframeStructuralEngine)

**File**: `st_lms/multi_timeframe_structural_engine/engine.py`

**Fungsi**: Membangun struktur Supertrend Line multi-timeframe

**Proses**:
1. Analisis Supertrend per timeframe
2. Identifikasi wave dan line
3. Konfliks resolusi antar timeframe
4. Building structural hierarchy

**Output**: `StructureSnapshot`

```python
struct_snap = self._engine.process(symbol, candles)
```

---

### C004: PRESERVE (SnapshotRepository)

**File**: `st_lms/preserve/preserver.py`

**Fungsi**: Menyimpan snapshot ke repository dengan evaluasi line status

**Metode**:
- `store_market()` - Simpan MarketSnapshot
- `store_indicators()` - Simpan IndicatorSnapshot
- `store_structure()` - Simpan StructureSnapshot dengan harga aktual
- `evaluate_lines()` - Evaluasi status line (active/broken/untouched)

**Output**: Snapshot IDs untuk provenance tracking

---

### C005: REMEMBER (StructureMemory)

**File**: `st_lms/remember/memory.py`

**Fungsi**: Append-only memory untuk pattern matching historis

**Komponen**:
- `historical_repository.py` - Repository struktur historis
- `memory.py` - Logic pencarian similar pattern

**Proses**:
1. Store evaluated structure (append-only)
2. Find similar historical context

**Output**: Historical context untuk Select phase

```python
self._memory.store(evaluated)
ctx = self._memory.find_similar(evaluated)
```

---

### C006: SELECT (Selector)

**File**: `st_lms/select/selector.py`

**Fungsi**: Memilih candidate line terbaik untuk analisis

**Input**:
- Evaluated structure dari C004
- Historical context dari C005

**Output**: Candidate Supertrend Line

```python
candidate = self._selector.select_candidate(evaluated, ctx)
```

---

### C007: UNDERSTAND (GeometryAnalyzer)

**File**: `st_lms/understand/geometry.py`

**Fungsi**: Menganalisis geometri market dari candidate line

**Analisis**:
- Slope dan angle
- Support/Resistance levels
- Price distance ratios
- Time-based measurements

**Output**: `MarketUnderstanding`

```python
understanding = self._geometry.analyze(candidate)
```

---

### C008: CLASSIFY (StateClassifier)

**File**: `st_lms/classify/classifier.py`

**Fungsi**: Mengklasifikasikan state market berdasarkan understanding

**Klasifikasi**:
- Trend direction (LONG/SHORT/SIDEWAY)
- Strength level
- Confidence score

**Output**: `StructuralState`

```python
structural = self._classifier.classify(understanding, candidate)
```

---

### C009: TRADING PLAN (PlanManager)

**File**: `st_lms/trading_plan/planner.py`

**Fungsi**: Membuat dan memvalidasi trading plan

**Builders**:
- `long_builder.py` - Build plan untuk LONG
- `short_builder.py` - Build plan untuk SHORT
- `sideway_builder.py` - Build plan untuk SIDEWAY

**Validators**:
- `plan_validator.py` - Validasi plan memenuhi konstitusi

**Models**:
- `adaptive_grid.py` - Adaptive grid untuk entry/exit

**Output**: `TradingPlan`

```python
plan = self._plan_manager.create_and_validate(structural)
```

---

### C010: RIVER REVIEW (RiverReview)

**File**: `st_lms/river/river_review.py`

**Fungsi**: Review plan menggunakan shared learning patterns

**Komponen River**:
- `river_learning.py` - Snapshot pembelajaran
- `river_entry.py` - Learning untuk entry
- `river_exit.py` - Learning untuk exit
- `river_repository.py` - Repository learning
- `shared_learning_repository.py` - Shared patterns across trades
- `opportunity_learning.py` - Learning dari opportunity yang terlewat

**Proses**:
1. Match pattern dengan shared learning
2. Generate recommendation (APPROVE/REJECT)
3. Record rejected plans untuk opportunity cost

**Output**: `RiverState` dengan recommendation

```python
river_state = self._review.review(plan, learning, self._shared_repo)
```

---

### C011: AUTHORIZE (AuthorizationGateway)

**File**: `st_lms/authorize/authorization_gateway.py`

**Fungsi**: Gateway final authorization sebelum eksekusi

**Input**:
- TradingPlan dari C009
- Recommendation dari C010

**Output**: `Authorization` (APPROVED/REJECTED)

```python
auth = self._plan_manager.authorize(plan, river_state.recommendation)
```

---

### C012: EXECUTE (OrderManager + Executor)

**Files**:
- `st_lms/execute/order_manager.py`
- `st_lms/execute/executor.py`
- `st_lms/execute/simulation_executor.py`
- `st_lms/execute/live_executor.py`
- `st_lms/execute/testnet_executor.py`

**Fungsi**: Eksekusi order dengan risk management

**Proses**:
1. Compute position size via RiskManager
2. Place MARKET order via OrderManager
3. Execute trade via Executor
4. Simulate price movement untuk fill

**Executors**:
- `SimulationExecutor` - Untuk backtest
- `LiveExecutor` - Untuk live trading
- `TestnetExecutor` - Untuk testnet

**Output**: Position ID

```python
pos_size = self._risk.compute_position(plan, all_outcomes, risk_method)
order = self._order_manager.place_market(plan, pos_size)
pos_id = self._executor.execute(plan, pos_size)
```

---

### RISK MANAGEMENT (RiskManager)

**File**: `st_lms/risk/risk_manager.py`

**Fungsi**: Menghitung position size berdasarkan risk method

**Methods**:
- `fixed_fraction` - Fixed % dari balance
- `kelly` - Kelly criterion optimization

**Input**:
- TradingPlan
- Historical outcomes dari SharedLearningRepository

**Output**: Position size (Decimal)

---

### POST-TRADE: LEARN (RiverLearning + improve)

**Files**:
- `st_lms/river/river_learning.py`
- `st_lms/improve.py`

**Fungsi**: Pembelajaran setelah trade closed

**Proses**:
1. Capture trade result
2. Call `improve()` untuk update learning
3. Store ke SharedLearningRepository

```python
if pos.state.value == "CLOSED":
    improve(self._river, pos, current_price, "SL/TP", self._shared_repo)
```

---

### POST-TRADE: DARWIN (DarwinEngine)

**File**: `st_lms/darwin/darwin_engine.py`

**Fungsi**: Optimasi parameter tanpa menyentuh core formulas

**Prinsip**: 
- Tidak mengubah ATR/ST/MACD formulas
- Hanya optimize parameters (multiplier, period, etc.)
- Berdasarkan learning snapshot dan structural state

**Output**: `DarwinRecommendation`

```python
darwin_rec = self._darwin.optimize(self._shared_repo, self._river.get_snapshot(), structural.state)
```

---

## Models (Data Structures)

Semua model ada di `st_lms/models/`:

| Model | File | Deskripsi |
|-------|------|-----------|
| Candle | `candle.py` | OHLCV data |
| MarketSnapshot | `market_snapshot.py` | Snapshot kondisi pasar |
| IndicatorSnapshot | `indicator_snapshot.py` | Snapshot semua indikator |
| StructureSnapshot | `structure_snapshot.py` | Snapshot struktur ST |
| SupertrendLine | `supertrend_line.py` | Garis Supertrend |
| SupertrendWave | `supertrend_wave.py` | Wave dari ST lines |
| MarketUnderstanding | `market_understanding.py` | Hasil analisis geometri |
| StructuralState | `structural_state.py` | State klasifikasi |
| TradingPlan | `trading_plan.py` | Plan untuk trading |
| Authorization | `authorization.py` | Status authorization |
| Position | `position.py` | Posisi trading aktif |
| Order | `order.py` | Order ke exchange |
| LearningSnapshot | `learning_snapshot.py` | Snapshot pembelajaran |
| DarwinRecommendation | `darwin_recommendation.py` | Rekomendasi optimasi |
| Provenance | `provenance.py` | Tracking lineage snapshots |

---

## Configuration

**Files**:
- `config/core_config.py` - Konfigurasi inti
- `config/exchange_config.py` - Konfigurasi exchange
- `config/supertrend_config.py` - Parameter Supertrend
- `config/trading_config.py` - Parameter trading

---

## Utilities & Common

**Common** (`st_lms/common/`):
- `enums.py` - Enum definitions (Timeframe, Direction, etc.)
- `types.py` - Type aliases
- `math_utils.py` - Fungsi matematika
- `price_utils.py` - Utility harga
- `datetime_utils.py` - Utility datetime
- `core_constants.py` - Konstanta sistem

**Utils** (`st_lms/utils/`):
- `logger.py` - Logging system
- `helpers.py` - Helper functions

**Exceptions** (`st_lms/exceptions/`):
- `trading_exception.py`
- `validation_exception.py`
- `structure_exception.py`

---

## Persistence Layer

**Files**:
- `persistence/base_repository.py` - Base repository interface
- `persistence/sqlite_repository.py` - SQLite implementation

---

## API & Dashboard

**API** (`st_lms/api/`):
- `superbot_api.py` - REST API endpoints

**Dashboard** (`st_lms/dashboard/`):
- `app.py` - Streamlit dashboard app
- `dashboard_server.py` - Dashboard server
- `superbot_dashboard.py` - Dashboard utama
- `superbot_simple_v1.py` - Simple dashboard v1

---

## Testing

**Directory**: `st_lms/tests/`

| Test | File | Coverage |
|------|------|----------|
| Classifier | `test_classifier.py` | C008 |
| Measure | `test_measure.py` | C002 |
| Models | `test_models.py` | All models |
| Trading Plan | `test_trading_plan.py` | C009 |
| Adaptive Grid | `test_adaptive_grid.py` | Grid system |
| Constitution | `test_constitution/` | Constitutional rules |
| Stress Test | `test_stress/` | Performance under load |
| Integration | `test_integration/` | End-to-end pipeline |

---

## Entry Points

**Main Scripts**:
- `main.py` - Main entry point
- `run_bot.py` - Run trading bot
- `pipeline.py` - Pipeline implementation
- `improve.py` - Improvement module

**Shell Scripts**:
- `run_all.sh` - Run complete pipeline
- `start_superbot.sh` - Start SuperBot
- `start_dashboard.sh` - Start dashboard

---

## Exchange Integration

**Files**:
- `exchange/exchange_service.py` - Base exchange service
- `exchange/binance/binance_service.py` - Binance service
- `exchange/binance/binance_client.py` - Binance API client

---

## Backtesting

**File**: `st_lms/backtest/engine.py`

**Fungsi**: Backtest engine untuk testing strategi historis

---

## Telemetry

**File**: `st_lms/core/telemetry.py`

**Fungsi**: Monitoring dan telemetry sistem

---

## Package Metadata

- `pyproject.toml` - Python project metadata
- `requirements.txt` - Dependencies
- `__init__.py` - Package initialization

---

## Flow Summary

```
OBSERVE → MEASURE → ENGINE → PRESERVE → REMEMBER → SELECT → 
UNDERSTAND → CLASSIFY → TRADING PLAN → RIVER REVIEW → AUTHORIZE → 
EXECUTE → RISK MANAGE → LEARN → DARWIN OPTIMIZE
```

Setiap stage menghasilkan snapshot yang disimpan dengan provenance tracking untuk audit trail lengkap dan pembelajaran berkelanjutan.
