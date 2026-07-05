# ST_LMS v1.1 — 13-Layer Trading Pipeline

> **Identity:** Supertrend Living Market Structure — Pipeline C001-C012 + Post-Trade
> **Version:** 1.1.0
> **Python:** 3.12+
> **Modules:** RiskManager | BacktestEngine | Metrics | OrderManager | WebSocketObserver | RiverReview | DarwinEngine

---

## 🔄 Main Trading Pipeline (Real-Time Loop)

```text
Binance Futures (Simulation / Testnet / Live)
  │
  ▼
C001 — OBSERVE ─────────────────────────── MarketSnapshot [snapshot_id]
  Mengamati pasar apa adanya (Candle, Volume, Open Interest).
  Tidak ada analisis di tahap ini.
  │
  ▼
C002 — MEASURE ────────────────────────── IndicatorSnapshot [snapshot_id]
  Mengubah observasi menjadi data terukur (ATR, Supertrend Point, MACD, OI State).
  Tidak membentuk struktur.
  │
  ▼
C003 — MULTI-TIMEFRAME STRUCTURE ENGINE ── StructureSnapshot [snapshot_id]
  Membangun Supertrend Point [point_id] → Line [line_id] → Wave [wave_id]
  pada seluruh timeframe (4H, 1H, 15M, 5M, 1M).
  Seluruh struktur berasal dari Supertrend Point, bukan harga langsung.
  │
  ▼
C004 — PRESERVE ──────────────────────── SnapshotRepository + LineStatusManager
  Menjaga kontinuitas seluruh Supertrend Line.
  Line tidak dihapus, hanya berubah status (ACTIVE → BROKEN → ARCHIVED).
  │
  ▼
C005 — REMEMBER ──────────────────────── HistoricalStructureRepository (Append-only)
  Menyimpan seluruh sejarah struktur ke Historical Structure Repository.
  Tidak ada penghapusan. Hanya tambah.
  │
  ▼
C006 — SELECT ────────────────────────── Candidate + AdaptiveStructureStack
  Adaptive Structure Stack memilih Living Market Structure
  (struktur yang masih relevan dengan harga saat ini).
  Memperhitungkan Structure Age (kematangan struktur).
  │
  ▼
C007 — UNDERSTAND ────────────────────── MarketUnderstanding [snapshot_id]
  Structural Geometry memahami bentuk geometri struktur:
  ASCENDING, DESCENDING, CORRIDOR, CONVERGING, DIVERGING,
  CHAOTIC, SINGLE_DIRECTION, NO_STRUCTURE.
  │
  ▼
C008 — CLASSIFY ──────────────────────── StructuralSnapshot [snapshot_id]
  Menghasilkan Structural State resmi market
  (UPTREND, DOWNTREND, SIDEWAY) + Structural State Confidence.
  Otoritas tunggal kondisi pasar.
  │
  ▼
C009 — ADAPTIVE TRADING PLAN ─────────── TradingPlan [plan_id]
  Menyusun rencana trading lengkap & adaptif.
  ├── LONG BUILDER   → Trend Following, Fib 0.382
  ├── SHORT BUILDER  → Trend Following, Fib 0.618
  └── SIDEWAY BUILDER
        ├── TradingPlan  [plan_id]   (ADAPTIVE_GRID_SIDEWAY)
        └── AdaptiveGrid [grid_id]   (HANYA di Sideway)
  │
  ▼
C010 — RIVER PLAN REVIEW ─────────────── RiverRecommendation + Confidence
  River membandingkan Trading Plan dengan pengalaman historis.
  Menghasilkan RiverRecommendation (ALLOW/CAUTION/REJECT/UNKNOWN)
  dan River Learning Confidence.
  River TIDAK membuat keputusan, hanya mereview.
  │
  ▼
C011 — AUTHORIZE ─────────────────────── Authorization [authorization_id]
  Memutuskan boleh / tidak boleh trading
  (APPROVED / REJECTED) + Authorization Reason (wajib audit).
  │
  ▼
C012 — EXECUTE ───────────────────────── Position [position_id]
  Melaksanakan izin (Simulation / Testnet / Live Execution).
  Hanya menjalankan perintah, tidak berpikir.
  │
  ▼
TRADE CLOSED / POSITION CLOSED
```

## 🧠 Post-Trade Loop (Continuous Improvement)

```text
Trade Closed
  │
  ├──▶ RIVER EXPERIENCE LEARNING
  │     Belajar dari hasil trade & Opportunity Cost
  │     (Termasuk trade yang sengaja ditolak → record_rejected_plan).
  │     LearningSnapshot [snapshot_id]
  │     TradeOutcome [trade_id]
  │
  ├──▶ RISK MANAGER UPDATE
  │     Update account balance setelah trade closed (PnL).
  │
  ├──▶ DARWIN IMPROVEMENT ENGINE
  │     Menganalisis Shared Learning Repository.
  │     Menghasilkan OptimizedParameters
  │     (atr_mult, tp_mult, sl_mult, conf_threshold, grid params).
  │     Tidak mengubah Formula Authority.
  │
  └──▶ SHARED LEARNING REPOSITORY
        Pusat pengetahuan bersama untuk Long, Short, dan Sideway.
        Menyimpan: TradeOutcome + RejectedPlan records.
```

## 🔒 5 Prinsip Mutlak (Core Rules)

1. **Structure First** — Seluruh keputusan berasal dari struktur pasar (Supertrend Line)
2. **Plan Before Trade** — Tidak ada eksekusi tanpa Adaptive Trading Plan
3. **Review Before Authorize** — River meninjau Trading Plan sebelum izin diberikan
4. **Learn After Result** — River dan Darwin hanya belajar setelah hasil trade diketahui
5. **Improve Without Touching Core** — Darwin tidak mengubah Formula Authority (ATR, ST, MACD, Fib, OI)

## 🔒 Locked Principles (11 Total)

| # | Rule | Penjelasan |
|---|------|------------|
| 1 | **Snapshot First** | Setiap layer output snapshot baru, tidak mengubah snapshot lama |
| 2 | **Data First** | Tidak ada keputusan tanpa data |
| 3 | **Structure First** | Trading Plan tidak pernah membaca Candle langsung — hanya dari StructuralSnapshot |
| 4 | **River Never Execute** | River hanya belajar dari histori, tidak pernah memutuskan entry/exit |
| 5 | **Darwin Never Trade** | Darwin hanya optimasi parameter sekunder, tidak mengubah core formula |
| 6 | **Adaptive Grid Rule** | AdaptiveGrid hanya ada di SidewayBuilder — Long/Short tidak tahu Grid |
| 7 | **Builder Isolation** | 3 builder independent — tidak saling import |
| 8 | **Identity Rule** | Setiap model punya ID unik: `snapshot_id`, `point_id`, `line_id`, `wave_id`, `plan_id`, `grid_id`, `trade_id`, `position_id`, `authorization_id` |
| 9 | **Relationship Rule** | Relasi pakai ID, bukan object reference |
| 10 | **Snapshot Rule** | Semua model `@dataclass(frozen=True, slots=True)` — immutable |
| 11 | **Lifecycle Rule** | Setiap model punya lifecycle via Enum |

## ID Mapping per Layer

| Layer | Output | ID Field |
|-------|--------|----------|
| C001 Observe | MarketSnapshot | `snapshot_id` |
| C002 Measure | IndicatorSnapshot | `snapshot_id` |
| C003 Engine | StructureSnapshot | `snapshot_id` |
| C003 sub | SupertrendPoint | `point_id` |
| C003 sub | SupertrendLine | `line_id` |
| C003 sub | SupertrendWave | `wave_id` |
| C007 Understand | MarketUnderstanding | `snapshot_id` |
| C008 Classify | StructuralSnapshot | `snapshot_id` |
| C009 Trading Plan | TradingPlan | `plan_id` |
| C009 Sideway only | AdaptiveGrid | `grid_id` |
| C010 River Review | RiverState | `snapshot_id` |
| C011 Authorize | Authorization | `authorization_id` |
| C012 Execute | Position | `position_id` |
| Post-Trade River | LearningSnapshot / TradeOutcome | `snapshot_id` / `trade_id` |
| Post-Trade Darwin | DarwinState | `snapshot_id` |

---

## Project Structure

```
st_lms/
├── main.py                          # Entry point
├── improve.py                       # Post-Trade improve → River + Opportunity Learning
├── pyproject.toml / .env.example    # Project config
│
├── common/
│   ├── enums.py                     # 20 enum (Timeframe, Direction, StructuralState,
│   │                                #   StructuralGeometry 8 values, LineStatus, WaveState,
│   │                                #   TradingPlanState 7, GridState 6, RiverState 6,
│   │                                #   RiverRecommendation 4, DarwinState 6,
│   │                                #   AuthorizationStatus, PositionSide, PositionState,
│   │                                #   MACDBucket, OpenInterestState, MarketSession,
│   │                                #   Environment)
│   ├── core_constants.py
│   ├── types.py / datetime_utils.py / math_utils.py / price_utils.py
│
├── config/
│   ├── core_config.py               # BOT_NAME, DEFAULT_TIMEFRAMES, PRIMARY_TIMEFRAME
│   ├── supertrend_config.py         # ATR_PERIOD, MULTIPLIER, GRID_ATR_MULTIPLIER
│   ├── trading_config.py            # RISK_PER_TRADE, AUTHORIZATION_MIN_CONFIDENCE
│   └── exchange_config.py           # EXCHANGE, ENVIRONMENT, API_KEY
│
├── models/                          # 18 frozen dataclass models
│   ├── candle.py                    # OHLCV
│   ├── atr.py / macd.py / open_interest.py
│   ├── supertrend_point.py          # [point_id]
│   ├── supertrend_line.py           # [line_id]
│   ├── supertrend_wave.py           # [wave_id]
│   ├── market_snapshot.py           # C001 output [snapshot_id]
│   ├── indicator_snapshot.py        # C002 output [snapshot_id]
│   ├── structure_snapshot.py        # C003 output [snapshot_id] + TrendInfo, CompressionZone, FibLevel
│   ├── market_understanding.py      # C007 output [snapshot_id]
│   ├── learning_snapshot.py         # River output [snapshot_id] + TradeOutcome [trade_id]
│   ├── provenance.py                # Data lineage
│   ├── structural_state.py          # C008 output [snapshot_id]
│   ├── trading_plan.py              # C009 [plan_id]
│   ├── authorization.py             # C011 [authorization_id]
│   ├── position.py                  # C012 [position_id]
│   ├── river_state.py               # C010 [snapshot_id]
│   └── darwin_state.py              # Post-Trade [snapshot_id]
│
├── exchange/
│   ├── exchange_service.py          # Abstract ExchangeService
│   └── binance/
│       ├── binance_client.py        # Low-level API wrapper
│       └── binance_service.py       # Concrete ExchangeService
│
├── observe/                         # C001
│   ├── observer.py / binance_observer.py / simulation_observer.py
│
├── measure/                         # C002
│   ├── atr_calculator.py / macd_calculator.py / supertrend_calculator.py
│   ├── open_interest_calculator.py / volatility_calculator.py
│   ├── oi_delta_calculator.py / price_momentum_calculator.py
│
├── multi_timeframe_structural_engine/  # C003
│   └── engine.py                    # Point→Line→Wave→Trend/Compression/Fib
│
├── preserve/                        # C004
│   ├── preserver.py                 # SnapshotRepository + LineStatusManager
│   └── line_status_manager.py       # ACTIVE→BROKEN→ARCHIVED transitions
│
├── remember/                        # C005
│   ├── memory.py                    # StructureMemory → HistoricalContext
│   └── historical_repository.py     # Append-only Historical Structure Repository
│
├── select/                          # C006
│   ├── selector.py                  # Candidate ranking/filter
│   └── adaptive_stack.py            # AdaptiveStructureStack + StructureAge
│
├── understand/                      # C007
│   └── geometry.py                  # 8 geometry types detection
│
├── classify/                        # C008
│   └── classifier.py                # UPTREND/DOWNTREND/SIDEWAY
│
├── trading_plan/                    # C009
│   ├── planner.py                   # Route structural state ke builder
│   ├── plan_manager.py              # Create → Review → Authorize flow
│   ├── models/adaptive_grid.py      # [grid_id] — only for SIDEWAY
│   ├── builders/long_builder.py     # Fib 0.382
│   ├── builders/short_builder.py    # Fib 0.618
│   ├── builders/sideway_builder.py  # Adaptive Grid
│   ├── validators/plan_validator.py # Direction-aware SL/TP
│   ├── repository/plan_repository.py
│
├── river/                           # C010 + Post-Trade
│   ├── river_learning.py            # Pattern accumulation
│   ├── river_entry.py               # Entry validation
│   ├── river_exit.py                # ATR trailing stop
│   ├── river_review.py              # Plan Review → RiverState
│   ├── river_repository.py          # River state storage
│   └── shared_learning_repository.py # Pusat pengetahuan (outcomes + rejected plans)
│
├── risk/                            # Position Sizing
│   └── risk_manager.py              # Kelly Criterion + Fixed Fraction
│
├── backtest/                        # Backtesting
│   └── engine.py                    # Historical candle replay → pipeline → metrics
│
├── observe/                         # C001
│   ├── observer.py                  # Base observer
│   ├── simulation_observer.py       # Simulated data
│   ├── binance_observer.py          # REST observer
│   └── websocket_observer.py        # Real-time streaming (sub-H1)
│
├── execute/                         # C012
│   ├── executor.py                  # Abstract base
│   ├── simulation_executor.py       # Simulated execution + position tracking
│   ├── testnet_executor.py          # Binance Testnet (stub)
│   ├── live_executor.py             # Live execution (stub)
│   └── order_manager.py             # MARKET/LIMIT/OCO + partial fill + cancel-replace
│
├── models/                          # 23 frozen dataclass models
│   ├── ...                          # (existing 18 models)
│   ├── metrics.py                   # TradingMetrics + calculate_metrics()  [NEW]
│   ├── order.py                     # Order + Fill lifecycle              [NEW]
│   └── backtest_result.py           # BacktestResult + BacktestTrade      [NEW]
│
├── darwin/                          # Post-Trade
│   └── darwin_engine.py             # ATR/TP/SL/Grid optimizer
├── authorize/                       # C011
│   └── authorization_gateway.py     # Plan + River Review → APPROVED/REJECTED
│
├── execute/                         # C012
│   ├── executor.py                  # Abstract base
│   ├── simulation_executor.py       # Simulated execution + position tracking
│   ├── testnet_executor.py          # Binance Testnet (stub)
│   └── live_executor.py             # Live execution (stub)
│
├── darwin/                          # Post-Trade
│   └── darwin_engine.py             # ATR/TP/SL/Grid optimizer
│
├── utils/
│   ├── logger.py
│   └── helpers.py                   # 7 ID generators
│
└── tests/                           # 36 test cases
    ├── test_enums.py
    ├── test_models.py
    ├── test_measure.py
    ├── test_classifier.py
    ├── test_trading_plan.py
    └── test_adaptive_grid.py
```

---

## Trader's Review

### Strengths

1. **Structure-first dogma** — Bot tidak bereaksi terhadap noise harga, hanya terhadap perubahan struktur.
2. **Plan-before-execute** — Setiap trade harus melewati pipeline 12 C + Post-Trade.
3. **Review Before Authorize** — River meninjau sebelum izin, bukan sesudah.
4. **Multi-timeframe seragam** — Semua timeframe pakai logika yang sama.
5. **Immutable models** — Semua model `frozen=True, slots=True`.

### Weaknesses

1. **River entry masih basic** — Butuh konfirmasi tambahan sebelum entry.
2. **Live/Testnet executor masih stub** — Hanya Simulation yang jalan penuh.
3. **Belum ada DAO/data persistence layer** — Semua in-memory.

---

## What Can Be Improved

| Prioritas | Module | Fungsi |
|-----------|--------|--------|
| Tinggi | `observe/binance_observer.py` | WebSocket real-time production |
| Tinggi | `execute/testnet_executor.py` | Binance Testnet integration |
| Tinggi | `execute/live_executor.py` | Live execution |
| Sedang | `preserve/preserver.py` | Persistence layer (SQLite/Postgres) |
| Rendah | All new modules | Unit tests for RiskManager, Backtest, Metrics, OrderManager, WebSocketObserver |
