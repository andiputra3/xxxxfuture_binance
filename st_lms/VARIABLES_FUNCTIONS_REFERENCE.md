# ST-LMS Variables & Functions Reference

Dokumentasi lengkap semua variabel, fungsi, dan class di proyek ST-LMS

**Total Files:** 130

**Total Modules:** 32

---

## Table of Contents

- [api](#api)
- [authorize](#authorize)
- [backtest](#backtest)
- [classify](#classify)
- [common](#common)
- [config](#config)
- [core](#core)
- [darwin](#darwin)
- [dashboard](#dashboard)
- [exceptions](#exceptions)
- [exchange](#exchange)
- [exchange/binance](#exchange-binance)
- [execute](#execute)
- [measure](#measure)
- [models](#models)
- [multi_timeframe_structural_engine](#multi-timeframe-structural-engine)
- [multi_timeframe_structural_engine/supertrend_line](#multi-timeframe-structural-engine-supertrend-line)
- [observe](#observe)
- [persistence](#persistence)
- [preserve](#preserve)
- [remember](#remember)
- [risk](#risk)
- [river](#river)
- [root](#root)
- [select](#select)
- [trading_plan](#trading-plan)
- [trading_plan/builders](#trading-plan-builders)
- [trading_plan/models](#trading-plan-models)
- [trading_plan/repository](#trading-plan-repository)
- [trading_plan/validators](#trading-plan-validators)
- [understand](#understand)
- [utils](#utils)

---

## Module: api

### File: `__init__.py`

### File: `superbot_api.py`

#### Classes

**CandleRequest** (line 41)

**Attributes:**
- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `limit`

**PipelineTraceResponse** (line 49)

**Attributes:**
- `pipeline_id`
- `timestamp`
- `symbol`
- `timeframe`
- `strategy`
- `stages`
- `market_snapshot_id`
- `indicator_snapshot_id`
- `structure_snapshot_id`
- `understanding_id`
- `structural_snapshot_id`
- `trading_plan_id`
- `authorization_id`
- `position_id`
- `position_size`
- `darwin_recommendation`

**SupertrendPointResponse** (line 68)

**Attributes:**
- `point_id`
- `timestamp`
- `price`
- `trend_direction`
- `atr_value`
- `multiplier`
- `line_id`
- `timeframe`
- `symbol`

**SupertrendLineResponse** (line 80)

**Attributes:**
- `line_id`
- `timeframe`
- `symbol`
- `trend_direction`
- `start_timestamp`
- `end_timestamp`
- `start_price`
- `current_price`
- `points_count`
- `is_active`
- `strength`

**RiverLearningResponse** (line 94)

**Attributes:**
- `snapshot_id`
- `total_trades`
- `wins`
- `losses`
- `win_rate`
- `total_pnl`
- `profit_factor`
- `avg_win`
- `avg_loss`
- `best_trade`
- `worst_trade`
- `consecutive_wins`
- `consecutive_losses`
- `patterns_learned`

**DarwinRecommendationResponse** (line 111)

**Attributes:**
- `recommendation_id`
- `timestamp`
- `state`
- `adjustments`
- `confidence`
- `reasoning`

**ExecutionTrackResponse** (line 120)

**Attributes:**
- `execution_id`
- `pipeline_trace_id`
- `plan_id`
- `symbol`
- `direction`
- `entry_price`
- `exit_price`
- `position_size`
- `pnl`
- `pnl_percent`
- `status`
- `entry_timestamp`
- `exit_timestamp`
- `exit_reason`
- `duration_seconds`

**PipelineRunRequest** (line 138)

> Request model for running pipeline with strategy selection.

**Attributes:**
- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `strategy`
- `initial_balance`
- `risk_method`
- `leverage`

**BacktestRequest** (line 150)

**Attributes:**
- `symbol`
- `start_date`
- `end_date`
- `strategy`
- `timeframes`
- `initial_balance`
- `risk_method`

**BacktestResultResponse** (line 160)

**Attributes:**
- `backtest_id`
- `symbol`
- `start_date`
- `end_date`
- `total_trades`
- `wins`
- `losses`
- `win_rate`
- `total_pnl`
- `final_balance`
- `max_drawdown`
- `sharpe_ratio`
- `trades`
- `equity_curve`

#### Functions

**get_db_connection**() - line 203

> Get SQLite connection.

**init_superbot_db**() - line 210

> Initialize SuperBot database tables.

**candle_to_dict**(candle) - line 308

> Convert Candle to dictionary.

**fetch_binance_candles**(symbol, timeframe, start_date, end_date, limit) - line 322

> Fetch candles from Binance Futures API.

**extract_supertrend_data**(struct_snap) - line 378

> Extract supertrend lines and points from structure snapshot.

#### Variables

- `_db_path` = `superbot.db` (line 196)
- `candles` = `[]` (line 343)
- `lines_data` = `[]` (line 380)
- `query` = `SELECT * FROM pipeline_traces WHERE 1=1` (line 654)
- `params` = `[]` (line 655)
- `traces` = `[]` (line 672)
- `query` = `SELECT * FROM supertrend_lines WHERE 1=1` (line 711)
- `params` = `[]` (line 712)
- `lines` = `[]` (line 732)
- `points` = `[]` (line 766)
- `patterns` = `[]` (line 821)
- `recs` = `[]` (line 858)
- `query` = `SELECT * FROM execution_tracks WHERE 1=1` (line 886)
- `params` = `[]` (line 887)
- `executions` = `[]` (line 904)
- `valid_strategies` = `['LONG_ONLY', 'SHORT_ONLY', 'SIDEWAY_ONLY']` (line 497)
- `darwin_rec_dict` = `None` (line 562)
- `all_candles` = `{}` (line 944)
- `trades` = `[]` (line 961)


---

## Module: authorize

### File: `__init__.py`

### File: `authorization_gateway.py`

#### Classes

**AuthorizationGateway** (line 16)

> C011 — SINGLE authorization authority.

5-layer evaluation:
1. Plan state must be READY
2. Confidence >= AUTHORIZATION_MIN_CONFIDENCE
3. Risk <= 5%
4. River Recommendation != REJECT
5. Liquidation Har...

**Methods:**
- `authorize()`

#### Functions

**authorize**(self, plan, river_recommendation, enable_time_filter, enable_liquidation_check) - line 27

> Run all authorization layers and return result.

Args:
    plan: TradingPlan must be in READY state
    river_recommendation: Wajib — Prinsip Mutlak #3 (Review Before Authorize)
    enable_time_filter: Enable Time-Based Filter (default False for simulation/backtest)
    enable_liquidation_check: Ena...


---

## Module: backtest

### File: `__init__.py`

### File: `engine.py`

#### Classes

**BacktestEngine** (line 17)

> Backtest Engine — replay historical candles through the pipeline.

Cara kerja:
1. Iterasi candle per-step
2. Setiap step: jalankan pipeline dengan data sampai candle tersebut
3. Track semua trade, equ...

**Methods:**
- `__init__()`
- `run()`

#### Functions

**run**(self, symbol, candles, step) - line 34

> Run backtest dengan historical candle replay.

Args:
    symbol: Trading pair
    candles: Dict timeframe -> list of candles (sorted)
    step: Process every N candles (1 = every candle)

Returns:
    BacktestResult dengan metrics lengkap

#### Variables

- `rejected_count` = `0` (line 49)


---

## Module: classify

### File: `__init__.py`

### File: `classifier.py`

#### Classes

**StateClassifier** (line 13)

> C008 — SINGLE authority for Structural State.

Classify layer — menentukan Structural State dari MarketUnderstanding.
Menghasilkan confidence sendiri berdasarkan geometry + support/resistance range.

**Methods:**
- `classify()`
- `_determine_state()`
- `_calculate_confidence()`

#### Functions

**resolve_multi_tf_conflict**(tf_states) - line 74

> Multi-TF Conflict Resolution Protocol.

Rules:
- All TF aligned → use that state
- Higher TF aligned, Lower TF conflict → use higher TF
- Higher TF conflict, Lower TF aligned → REJECT (return SIDEWAY)
- All TF conflict → SIDEWAY

**classify**(self, understanding, candidate) - line 20

> Produces StructuralSnapshot dari MarketUnderstanding + Candidate.


---

## Module: common

### File: `__init__.py`

### File: `core_constants.py`

#### Variables

- `SUPERTREND_ATR_PERIOD` = `10` (line 5)
- `MIN_SUPERTREND_LINE_CANDLES` = `5` (line 7)
- `BINANCE_FUTURES` = `BINANCE_FUTURES` (line 9)

### File: `datetime_utils.py`

#### Functions

**ms_to_datetime**(ms) - line 6

> Convert epoch milliseconds to UTC datetime.

**datetime_to_ms**(dt) - line 11

> Convert UTC datetime to epoch milliseconds.

### File: `enums.py`

#### Classes

**Timeframe** (line 6)

> Supported Binance Futures timeframes.

**Direction** (line 16)

> Market direction.

**StructuralState** (line 24)

> Official market classification.

**StructuralGeometry** (line 32)

> Structural geometry shapes from Understand layer.

**PositionSide** (line 45)

> Trading position side.

**PositionState** (line 52)

> Position lifecycle.

**MACDBucket** (line 62)

> MACD classification.

**OpenInterestState** (line 71)

> Open Interest classification.

**LineStatus** (line 80)

> Supertrend Line lifecycle status.

**WaveState** (line 88)

> Supertrend Wave lifecycle.

**TradingPlanState** (line 97)

> Trading Plan lifecycle.

**GridState** (line 109)

> Adaptive Grid lifecycle.

**RiverState** (line 120)

> River learning lifecycle.

**RiverRecommendation** (line 131)

> River review output.

**DarwinState** (line 140)

> Darwin improvement lifecycle.

**AuthorizationStatus** (line 151)

> Authorization result.

**MarketSession** (line 158)

> Market trading session.

**Environment** (line 167)

> Runtime environment.

#### Variables

- `M1` = `1m` (line 9)
- `M5` = `5m` (line 10)
- `M15` = `15m` (line 11)
- `H1` = `1h` (line 12)
- `H4` = `4h` (line 13)
- `LONG` = `LONG` (line 19)
- `SHORT` = `SHORT` (line 20)
- `NEUTRAL` = `NEUTRAL` (line 21)
- `UPTREND` = `UPTREND` (line 27)
- `DOWNTREND` = `DOWNTREND` (line 28)
- `SIDEWAY` = `SIDEWAY` (line 29)
- `ASCENDING` = `ASCENDING` (line 35)
- `DESCENDING` = `DESCENDING` (line 36)
- `CORRIDOR` = `CORRIDOR` (line 37)
- `CONVERGING` = `CONVERGING` (line 38)
- `DIVERGING` = `DIVERGING` (line 39)
- `CHAOTIC` = `CHAOTIC` (line 40)
- `SINGLE_DIRECTION` = `SINGLE_DIRECTION` (line 41)
- `NO_STRUCTURE` = `NO_STRUCTURE` (line 42)
- `LONG` = `LONG` (line 48)
- `SHORT` = `SHORT` (line 49)
- `WAITING` = `WAITING` (line 55)
- `OPEN` = `OPEN` (line 56)
- `PARTIAL` = `PARTIAL` (line 57)
- `CLOSING` = `CLOSING` (line 58)
- `CLOSED` = `CLOSED` (line 59)
- `BULLISH` = `BULLISH` (line 65)
- `BEARISH` = `BEARISH` (line 66)
- `WEAKENING` = `WEAKENING` (line 67)
- `NEUTRAL` = `NEUTRAL` (line 68)
- `INCREASING` = `INCREASING` (line 74)
- `DECREASING` = `DECREASING` (line 75)
- `FLAT` = `FLAT` (line 76)
- `ABSENT` = `ABSENT` (line 77)
- `ACTIVE` = `ACTIVE` (line 83)
- `BROKEN` = `BROKEN` (line 84)
- `ARCHIVED` = `ARCHIVED` (line 85)
- `BUILDING` = `BUILDING` (line 91)
- `ACTIVE` = `ACTIVE` (line 92)
- `COMPLETED` = `COMPLETED` (line 93)
- `ARCHIVED` = `ARCHIVED` (line 94)
- `CREATED` = `CREATED` (line 100)
- `WAITING` = `WAITING` (line 101)
- `READY` = `READY` (line 102)
- `AUTHORIZED` = `AUTHORIZED` (line 103)
- `EXECUTING` = `EXECUTING` (line 104)
- `FINISHED` = `FINISHED` (line 105)
- `ARCHIVED` = `ARCHIVED` (line 106)
- `WAITING` = `WAITING` (line 112)
- `ACTIVE` = `ACTIVE` (line 113)
- `SHIFTING` = `SHIFTING` (line 114)
- `STOP_NEW_ORDER` = `STOP_NEW_ORDER` (line 115)
- `EXITING` = `EXITING` (line 116)
- `FINISHED` = `FINISHED` (line 117)
- `EMPTY` = `EMPTY` (line 123)
- `COLLECTING` = `COLLECTING` (line 124)
- `LEARNING` = `LEARNING` (line 125)
- `STABLE` = `STABLE` (line 126)
- `ADAPTIVE` = `ADAPTIVE` (line 127)
- `EXPERT` = `EXPERT` (line 128)
- `ALLOW` = `ALLOW` (line 134)
- `CAUTION` = `CAUTION` (line 135)
- `REJECT` = `REJECT` (line 136)
- `UNKNOWN` = `UNKNOWN` (line 137)
- `EMPTY` = `EMPTY` (line 143)
- `OBSERVING` = `OBSERVING` (line 144)
- `ANALYZING` = `ANALYZING` (line 145)
- `IMPROVING` = `IMPROVING` (line 146)
- `VALIDATING` = `VALIDATING` (line 147)
- `STABLE` = `STABLE` (line 148)
- `APPROVED` = `APPROVED` (line 154)
- `REJECTED` = `REJECTED` (line 155)
- `ASIA` = `ASIA` (line 161)
- `LONDON` = `LONDON` (line 162)
- `NEW_YORK` = `NEW_YORK` (line 163)
- `OVERLAP` = `OVERLAP` (line 164)
- `SIMULATION` = `SIMULATION` (line 170)
- `TESTNET` = `TESTNET` (line 171)
- `LIVE` = `LIVE` (line 172)

### File: `math_utils.py`

#### Functions

**round_price**(value, tick_size) - line 6

> Round price to nearest tick size.

**percentage_change**(old, new) - line 11

> Calculate percentage change between two values.

### File: `price_utils.py`

#### Functions

**validate_positive_price**(price, name) - line 6

> Validate that a price value is positive.

### File: `types.py`


---

## Module: config

### File: `__init__.py`

### File: `core_config.py`

#### Variables

- `BOT_NAME` = `ST_LMS` (line 5)
- `CORE_VERSION` = `1.0.0` (line 6)

### File: `exchange_config.py`

### File: `supertrend_config.py`

#### Variables

- `MIN_LINE_CANDLES` = `5` (line 9)

### File: `trading_config.py`

#### Variables

- `MAX_OPEN_POSITIONS` = `1` (line 9)
- `DEFAULT_SYMBOL` = `BTCUSDT` (line 10)
- `MAX_LEVERAGE` = `3` (line 12)


---

## Module: core

### File: `telemetry.py`

#### Classes

**PipelineStage** (line 14)

**TelemetryEvent** (line 30)

**Attributes:**
- `timestamp`
- `stage`
- `action`
- `details`
- `status`
- `duration_ms`

**Methods:**
- `to_dict()`

**TelemetrySystem** (line 48)

**Methods:**
- `__init__()`
- `start_cycle()`
- `log()`
- `get_recent_events()`
- `get_current_cycle_log()`
- `get_river_learning_summary()`
- `get_darwin_status()`

#### Functions

**to_dict**(self) - line 38

**start_cycle**(self) - line 55

**log**(self, stage, action, details, status, duration_ms) - line 60

**get_recent_events**(self, limit) - line 76

**get_current_cycle_log**(self) - line 80

**get_river_learning_summary**(self) - line 84

**get_darwin_status**(self) - line 100

#### Variables

- `OBSERVE` = `C001 - Observe` (line 15)
- `MEASURE` = `C002 - Measure` (line 16)
- `STRUCTURE` = `C003 - Multi-TF Structure` (line 17)
- `PRESERVE` = `C004 - Preserve` (line 18)
- `REMEMBER` = `C005 - Remember` (line 19)
- `SELECT` = `C006 - Select` (line 20)
- `UNDERSTAND` = `C007 - Understand` (line 21)
- `CLASSIFY` = `C008 - Classify` (line 22)
- `PLAN` = `C009 - Trading Plan` (line 23)
- `RIVER_REVIEW` = `C010 - River Review` (line 24)
- `AUTHORIZE` = `C011 - Authorize` (line 25)
- `EXECUTE` = `C012 - Execute` (line 26)
- `POST_TRADE` = `Post-Trade Learning` (line 27)


---

## Module: darwin

### File: `__init__.py`

### File: `darwin_engine.py`

#### Classes

**StrategyRotationSignal** (line 15)

> Darwin recommendation to rotate strategy allocation.

**Attributes:**
- `from_strategy`
- `to_strategy`
- `reason`
- `confidence`

**OptimizedParameters** (line 24)

> Darwin internal — parameter optimal hasil optimasi.

Trend parameters (LONG/SHORT):
- atr_multiplier: SuperTrend multiplier
- tp_multiplier: Take profit distance (dalam ATR)
- sl_multiplier: Stop loss...

**Attributes:**
- `atr_multiplier`
- `tp_multiplier`
- `sl_multiplier`
- `confidence_threshold`
- `grid_atr_multiplier`
- `grid_levels`

**DarwinEngine** (line 47)

> Darwin layer — optimasi parameter strategi dari Shared Learning Repository.

Darwin hanya mengoptimalkan parameter.
Darwin tidak pernah trade.
Darwin tidak mengubah core formula (ATR period, Fibonacci...

**Methods:**
- `__init__()`
- `get_parameters()`
- `optimize()`
- `_optimize_grid()`
- `_optimize_trend()`
- `detect_strategy_rotation()`

#### Functions

**get_parameters**(self) - line 63

**optimize**(self, shared_repo, learning, state) - line 66

> Optimasi parameter dari Shared Learning Repository + River learning.

Args:
    shared_repo: SharedLearningRepository — Constitution: Darwin analyzes Shared Learning Repository
    learning: LearningSnapshot dari River
    state: StructuralState saat ini

Returns:
    DarwinRecommendation dengan par...

**detect_strategy_rotation**(self, worker_win_rates) - line 184

> Detect if a worker's win rate dropped >25% over 200 trades → recommend rotation.

#### Variables

- `grid_patterns` = `['GRID_TOO_TIGHT', 'GRID_TOO_WIDE', 'FALSE_BREAKOU` (line 120)
- `affected` = `['ADAPTIVE_GRID_SIDEWAY']` (line 123)
- `affected` = `['TREND_FOLLOWING_LONG', 'TREND_FOLLOWING_SHORT']` (line 157)


---

## Module: dashboard

### File: `app.py`

#### Functions

**generate_base_candles**(n) - line 42

#### Variables

- `candles` = `[]` (line 43)

### File: `dashboard_server.py`

#### Classes

**BotState** (line 39)

> Menyimpan state bot secara global untuk diakses server

**Methods:**
- `__init__()`

**STLMSHandler** (line 66)

**Methods:**
- `__init__()`
- `do_GET()`
- `do_POST()`
- `send_json_response()`
- `do_OPTIONS()`

#### Functions

**update_bot_state_from_telemetry**() - line 144

**simulate_bot_activity**() - line 181

**do_GET**(self) - line 70

**do_POST**(self) - line 110

**send_json_response**(self, data) - line 128

**do_OPTIONS**(self) - line 137

#### Variables

- `SYSTEM_AVAILABLE` = `True` (line 21)
- `SYSTEM_AVAILABLE` = `False` (line 23)
- `stages` = `['C001 - Observe', 'C002 - Measure', 'C003 - Multi` (line 203)

### File: `superbot_dashboard.py`

#### Functions

**convert_utc_to_wib**(utc_timestamp) - line 33

> Convert UTC timestamp to WIB (UTC+7).

**convert_timestamps_in_df**(df, timestamp_columns) - line 50

> Convert timestamp columns in DataFrame to WIB.

**fetch_dashboard_stats**() - line 150

> Fetch dashboard statistics.

**fetch_pipeline_traces**(symbol, timeframe, limit) - line 161

> Fetch pipeline traces.

**fetch_supertrend_lines**(symbol, timeframe, active_only, limit) - line 178

> Fetch supertrend lines.

**fetch_supertrend_points**(line_id) - line 195

> Fetch supertrend points for a line.

**fetch_river_learning**() - line 206

> Fetch river learning state.

**fetch_darwin_recommendations**(limit) - line 217

> Fetch darwin recommendations.

**fetch_execution_tracks**(symbol, status, limit) - line 228

> Fetch execution tracks.

#### Variables

- `API_BASE_URL` = `http://localhost:8000` (line 28)
- `WIB_OFFSET_HOURS` = `7` (line 31)
- `api_status` = `✅ Connected` (line 98)
- `api_status` = `❌ Disconnected` (line 100)
- `display_cols` = `['pipeline_id', 'timestamp', 'symbol', 'timeframe'` (line 378)
- `stage_cols` = `['C001_Observe', 'C002_Measure', 'C003_Engine', 'C` (line 360)
- `stage_data` = `[]` (line 364)
- `display_cols` = `['line_id', 'symbol', 'timeframe', 'trend_directio` (line 469)
- `default_line` = `None` (line 500)
- `display_cols` = `['recommendation_id', 'timestamp', 'state', 'confi` (line 664)
- `display_cols` = `['execution_id', 'symbol', 'direction', 'entry_pri` (line 707)

### File: `superbot_simple_v1.py`

#### Functions

**convert_utc_to_wib**(utc_timestamp) - line 32

> Convert UTC timestamp to WIB (UTC+7).

**convert_timestamps_in_df**(df, timestamp_columns) - line 55

> Convert timestamp columns in DataFrame to WIB.

**get_db_connection**() - line 66

> Get SQLite database connection.

**fetch_table_data**(query, params) - line 75

> Fetch data from database and return as DataFrame.

**format_pipeline_stages**(row) - line 93

> Format pipeline stages as ✅/❌ indicators.

**format_pnl**(pnl) - line 660

**format_confidence**(score) - line 865

#### Variables

- `DB_PATH` = `st_lms/superbot.db` (line 18)
- `WIB_OFFSET_HOURS` = `7` (line 19)
- `timeframes` = `['M1', 'M5', 'M15', 'H1', 'H4', 'D1', 'ALL']` (line 133)
- `strategies` = `['ALL', 'LONG_ONLY', 'SHORT_ONLY', 'SIDEWAY_ONLY']` (line 144)
- `stages` = `[]` (line 95)
- `stage_mapping` = `[('C001', 'Observe'), ('C002', 'Measure'), ('C003'` (line 96)
- `query` = `
    SELECT 
        id, symbol, timeframe, strate` (line 177)
- `query` = `
    SELECT 
        id, symbol, timeframe,
      ` (line 327)
- `query` = `
    SELECT 
        sp.id, sp.line_id, sp.symbol,` (line 440)
- `query` = `
    SELECT 
        id, symbol, timeframe,
      ` (line 522)
- `query` = `
    SELECT 
        id, symbol, timeframe, strate` (line 623)
- `query` = `
    SELECT 
        id, symbol, timeframe,
      ` (line 743)
- `query` = `
    SELECT 
        id, symbol, timeframe,
      ` (line 838)
- `stats_query` = `
    SELECT 
        COUNT(DISTINCT symbol) as tot` (line 936)
- `display_cols` = `['id', 'created_at', 'timeframe', 'strategy', 'Sta` (line 247)
- `display_cols` = `['id', 'created_at', 'timeframe', 'Trend', 'start_` (line 374)
- `display_cols` = `['id', 'line_id', 'timeframe', 'timestamp', 'price` (line 482)
- `display_cols` = `['id', 'created_at', 'timeframe', 'Wave Type', 'wa` (line 570)
- `display_cols` = `['id', 'entry_time', 'timeframe', 'strategy', 'ent` (line 687)
- `display_cols` = `['id', 'created_at', 'timeframe', 'total_trades', ` (line 779)
- `display_cols` = `['id', 'created_at', 'timeframe', 'recommendation_` (line 888)
- `tf_query` = `
        SELECT timeframe, COUNT(*) as count
     ` (line 972)
- `strat_query` = `
        SELECT strategy, COUNT(*) as count
      ` (line 987)
- `points_query` = `
                SELECT id, timestamp, price, tren` (line 416)


---

## Module: exceptions

### File: `__init__.py`

### File: `structure_exception.py`

#### Classes

**StructureException** (line 4)

> Base exception for structure layer errors.

**LineBuildError** (line 8)

> Raised when Supertrend Line construction fails.

**WaveBuildError** (line 12)

> Raised when Wave construction fails.

**FusionError** (line 16)

> Raised when structure fusion across timeframes fails.

### File: `trading_exception.py`

#### Classes

**TradingException** (line 4)

> Base exception for trading layer errors.

**AuthorizationError** (line 8)

> Raised when authorization fails.

**ExecutionError** (line 12)

> Raised when order execution fails.

**RiskLimitExceeded** (line 16)

> Raised when risk limit is exceeded.

### File: `validation_exception.py`

#### Classes

**ValidationException** (line 4)

> Base exception for validation errors.

**ModelValidationError** (line 8)

> Raised when model validation fails.

**ConfigValidationError** (line 12)

> Raised when configuration validation fails.

**PlanValidationError** (line 16)

> Raised when Trading Plan validation fails.


---

## Module: exchange

### File: `__init__.py`

### File: `exchange_service.py`

#### Classes

**ExchangeService** (line 13)

> Abstract interface for exchange operations.

**Methods:**
- `get_candles()`
- `get_open_interest()`
- `get_positions()`
- `place_order()`
- `close_position()`
- `cancel_order()`
- `get_account()`

#### Functions

**get_candles**(self, symbol, timeframe, limit) - line 17

**get_open_interest**(self, symbol) - line 21

**get_positions**(self, symbol) - line 25

**place_order**(self, symbol, side, quantity) - line 29

**close_position**(self, symbol) - line 33

**cancel_order**(self, order_id) - line 37

**get_account**(self) - line 41


---

## Module: exchange/binance

### File: `__init__.py`

### File: `binance_client.py`

#### Classes

**BinanceClient** (line 14)

> Low-level Binance Futures client wrapper.

**Methods:**
- `__init__()`
- `get_klines()`
- `get_open_interest()`
- `place_order()`
- `cancel_order()`
- `get_account_info()`

#### Functions

**get_klines**(self, symbol, interval, limit) - line 25

**get_open_interest**(self, symbol) - line 30

**place_order**(self, symbol, side, quantity) - line 35

**cancel_order**(self, symbol, order_id) - line 45

**get_account_info**(self) - line 50

#### Variables

- `Client` = `None` (line 8)

### File: `binance_service.py`

#### Classes

**BinanceService** (line 23)

> Concrete Binance Futures exchange service.

**Methods:**
- `__init__()`
- `get_candles()`
- `get_open_interest()`
- `get_positions()`
- `place_order()`
- `close_position()`
- `cancel_order()`
- `get_account()`

#### Functions

**get_candles**(self, symbol, timeframe, limit) - line 29

**get_open_interest**(self, symbol) - line 46

**get_positions**(self, symbol) - line 57

**place_order**(self, symbol, side, quantity) - line 60

**close_position**(self, symbol) - line 64

**cancel_order**(self, order_id) - line 67

**get_account**(self) - line 71


---

## Module: execute

### File: `__init__.py`

### File: `executor.py`

#### Classes

**Executor** (line 8)

> Abstract trade executor.

**Methods:**
- `execute()`

#### Functions

**execute**(self, plan) - line 12

### File: `live_executor.py`

#### Classes

**LiveExecutor** (line 14)

> C012 — Live production trading execution.

Melaksanakan trading plan di Binance Futures LIVE.
Menggunakan BinanceClient dengan API_KEY / API_SECRET production.
Mencatat posisi untuk tracking dan monit...

**Methods:**
- `__init__()`
- `execute()`
- `get_position()`
- `close_position()`
- `simulate_price()`
- `get_all_positions()`
- `emergency_close_all()`

#### Functions

**execute**(self, plan, quantity) - line 29

> Execute trading plan di Binance LIVE.

Args:
    plan: TradingPlan yang sudah di-authorize
    quantity: Optional quantity override (default dari plan.risk_percent)
    
Returns:
    position_id
    
Raises:
    RuntimeError: Jika environment bukan LIVE atau eksekusi gagal

**get_position**(self, position_id) - line 92

> Get position by ID.

**close_position**(self, position_id, reason) - line 96

> Close position di Binance LIVE.

Args:
    position_id: ID posisi yang akan ditutup
    reason: Alasan penutupan (SL/TP/manual)
    
Returns:
    True jika berhasil, False jika gagal

**simulate_price**(self, position_id, current_price) - line 140

> Simulasi pengecekan SL/TP untuk monitoring.

Tidak menutup posisi secara otomatis di LIVE,
hanya mengembalikan status apakah SL/TP tersentuh.
Penutupan harus dilakukan manual via close_position().

**get_all_positions**(self) - line 177

> Get semua posisi aktif.

**emergency_close_all**(self) - line 181

> Emergency close semua posisi aktif.

Gunakan hanya dalam kondisi darurat (system failure, margin call, dll).

Returns:
    Dict mapping position_id -> success status

#### Variables

- `sl_hit` = `False` (line 155)
- `tp_hit` = `False` (line 156)
- `exit_reason` = `` (line 157)
- `sl_hit` = `True` (line 161)
- `exit_reason` = `SL` (line 162)
- `sl_hit` = `True` (line 168)
- `exit_reason` = `SL` (line 169)
- `tp_hit` = `True` (line 164)
- `exit_reason` = `TP` (line 165)
- `tp_hit` = `True` (line 171)
- `exit_reason` = `TP` (line 172)

### File: `order_manager.py`

#### Classes

**OrderManager** (line 13)

> C012 — Order management with partial fills, OCO, cancel-replace.

Menangani lifecycle order:
- PENDING → FILLED (full fill)
- PENDING → PARTIAL (partial fill, tetap open)
- PENDING → CANCELLED
- OCO: ...

**Methods:**
- `__init__()`
- `place_market()`
- `place_limit()`
- `place_oco()`
- `fill_partial()`
- `cancel_replace()`
- `cancel()`
- `get_order()`
- `get_orders_by_plan()`

#### Functions

**place_market**(self, plan, quantity, max_slippage_pct) - line 26

> Place MARKET order — langsung terisi penuh.

Args:
    plan: TradingPlan
    quantity: Order quantity
    max_slippage_pct: Maximum allowed slippage (default 0.1%). If exceeded, order is REJECTED.

Returns:
    Order with state FILLED or REJECTED

**place_limit**(self, plan, quantity, limit_price) - line 87

> Place LIMIT order — menunggu sampai harga tersentuh.

**place_oco**(self, plan, quantity, entry_price, stop_price, limit_price) - line 108

> Place OCO (One Cancels Other) orders.

Args:
    plan: Trading plan
    quantity: Order quantity
    entry_price: Harga entry
    stop_price: Harga stop (untuk stop-loss order)
    limit_price: Harga limit (untuk take-profit order)

Returns:
    Tuple (stop_order, limit_order)

**fill_partial**(self, order_id, fill_price, fill_qty) - line 160

> Isi sebagian order (partial fill).

**cancel_replace**(self, order_id, new_price) - line 202

> Cancel existing order dan replace dengan harga baru (cancel-replace).

Old order → CANCELLED
New order → PENDING dengan harga baru

**cancel**(self, order_id) - line 252

> Cancel a pending/partial order.

**get_order**(self, order_id) - line 274

**get_orders_by_plan**(self, plan_id) - line 277

### File: `simulation_executor.py`

#### Classes

**SimulationExecutor** (line 12)

> C012 — Simulated trade execution with SL/TP simulation.

Melaksanakan izin di mode simulasi.
Mencatat posisi untuk tracking.
simulate_price() untuk menguji apakah SL/TP tersentuh.

**Methods:**
- `__init__()`
- `execute()`
- `simulate_price()`
- `close_position()`
- `get_position()`
- `compute_liquidation_price()`

#### Functions

**execute**(self, plan, quantity) - line 24

**simulate_price**(self, position_id, current_price) - line 46

> Simulasi pergerakan harga — cek apakah SL/TP tersentuh.

**close_position**(self, position_id, exit_reason) - line 90

**get_position**(self, position_id) - line 103

**compute_liquidation_price**(self, position, leverage) - line 106

> Compute liquidation price (approx 90% of margin).

#### Variables

- `sl_hit` = `False` (line 56)
- `tp_hit` = `False` (line 57)
- `exit_reason` = `` (line 58)
- `sl_hit` = `True` (line 62)
- `exit_reason` = `SL` (line 63)
- `sl_hit` = `True` (line 69)
- `exit_reason` = `SL` (line 70)
- `tp_hit` = `True` (line 65)
- `exit_reason` = `TP` (line 66)
- `tp_hit` = `True` (line 72)
- `exit_reason` = `TP` (line 73)

### File: `testnet_executor.py`

#### Classes

**TestnetExecutor** (line 14)

> C012 — Binance Testnet execution.

Melaksanakan trading plan di Binance Testnet.
Menggunakan BinanceClient dengan TESTNET_API_KEY / TESTNET_API_SECRET.
Mencatat posisi untuk tracking.

**Methods:**
- `__init__()`
- `execute()`
- `get_position()`
- `close_position()`
- `simulate_price()`

#### Functions

**execute**(self, plan, quantity) - line 27

> Execute trading plan di Binance Testnet.

Args:
    plan: TradingPlan yang sudah di-authorize
    quantity: Optional quantity override (default dari plan.risk_percent)
    
Returns:
    position_id
    
Raises:
    RuntimeError: Jika environment bukan TESTNET atau eksekusi gagal

**get_position**(self, position_id) - line 87

> Get position by ID.

**close_position**(self, position_id, reason) - line 91

> Close position di Binance Testnet.

Args:
    position_id: ID posisi yang akan ditutup
    reason: Alasan penutupan (SL/TP/manual)
    
Returns:
    True jika berhasil, False jika gagal

**simulate_price**(self, position_id, current_price) - line 135

> Simulasi pengecekan SL/TP untuk monitoring.

Tidak menutup posisi secara otomatis di Testnet,
hanya mengembalikan status apakah SL/TP tersentuh.

#### Variables

- `sl_hit` = `False` (line 149)
- `tp_hit` = `False` (line 150)
- `exit_reason` = `` (line 151)
- `sl_hit` = `True` (line 155)
- `exit_reason` = `SL` (line 156)
- `sl_hit` = `True` (line 162)
- `exit_reason` = `SL` (line 163)
- `tp_hit` = `True` (line 158)
- `exit_reason` = `TP` (line 159)
- `tp_hit` = `True` (line 165)
- `exit_reason` = `TP` (line 166)


---

## Module: measure

### File: `__init__.py`

### File: `atr_calculator.py`

#### Functions

**calculate_atr**(candles, period) - line 10

> Wilder-smoothed ATR from candle high/low/close.

### File: `macd_calculator.py`

#### Functions

**calculate_macd**(candles, fast, slow, signal) - line 11

> MACD from close prices with bucket classification.

### File: `oi_delta_calculator.py`

#### Functions

**calculate_oi_delta**(values) - line 8

> Perubahan OI dalam 24h dalam persen.

### File: `open_interest_calculator.py`

#### Functions

**classify_open_interest**(values) - line 10

> Classify the latest OI state based on trend.

### File: `orchestrator.py`

#### Classes

**MeasureOrchestrator** (line 21)

> C002 — Measure layer orchestrator.

Mengubah observasi menjadi data terukur (ATR, MACD, Volatility, dll).
Tidak membentuk struktur — hanya mengukur.

**Methods:**
- `measure()`

#### Functions

**measure**(self, market, candles) - line 28

> Run all calculators and package results into IndicatorSnapshot.

### File: `price_momentum_calculator.py`

#### Functions

**calculate_price_momentum**(candles, period) - line 8

> Perubahan harga dalam periode tertentu dalam persen.

### File: `supertrend_calculator.py`

#### Functions

**calculate_supertrend_points**(symbol, timeframe, candles, period, multiplier) - line 14

> Calculate Supertrend Points from candle data.

### File: `volatility_calculator.py`

#### Functions

**calculate_volatility**(candles, period) - line 10

> Standar deviasi dari close price return sebagai ukuran volatilitas.


---

## Module: models

### File: `__init__.py`

### File: `atr.py`

#### Classes

**ATR** (line 8)

> Immutable ATR model.

**Attributes:**
- `timestamp`
- `period`
- `value`

**Methods:**
- `__post_init__()`

#### Functions

### File: `authorization.py`

#### Classes

**Authorization** (line 10)

> Authorization result with confidence and reason.

**Attributes:**
- `authorization_id`
- `status`
- `confidence`
- `reason`
- `timestamp`

**Methods:**
- `__post_init__()`

#### Functions

### File: `backtest_result.py`

#### Classes

**BacktestTrade** (line 13)

> Single trade dalam backtest.

**Attributes:**
- `timestamp`
- `plan_id`
- `symbol`
- `direction`
- `entry_price`
- `exit_price`
- `quantity`
- `pnl`
- `pnl_percent`
- `exit_reason`
- `authorization`

**BacktestResult** (line 29)

> Hasil backtest lengkap.

**Attributes:**
- `symbol`
- `total_candles`
- `total_trades`
- `initial_balance`
- `final_balance`
- `metrics`
- `trades`
- `equity_curve`
- `rejected_count`
- `errors`

### File: `candle.py`

#### Classes

**Candle** (line 10)

> Immutable market candle.

**Attributes:**
- `symbol`
- `timeframe`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

**Methods:**
- `__post_init__()`

#### Functions

### File: `darwin_recommendation.py`

#### Classes

**DarwinRecommendation** (line 8)

> Darwin output — rekomendasi optimasi dengan confidence dan reason.

Sesuai Constitution: "Menghasilkan Darwin Recommendation."

**Attributes:**
- `recommendation_id`
- `parameter_changes`
- `confidence`
- `reason`
- `affected_strategies`

**Methods:**
- `__post_init__()`

#### Functions

### File: `darwin_state.py`

#### Classes

**DarwinState** (line 10)

> Darwin improvement state.

**Attributes:**
- `snapshot_id`
- `state`
- `improvement_confidence`
- `recommendations_count`

**Methods:**
- `__post_init__()`

#### Functions

### File: `indicator_snapshot.py`

#### Classes

**IndicatorSnapshot** (line 10)

> Measure layer output — seluruh indikator pada satu timestamp.

**Attributes:**
- `snapshot_id`
- `timestamp`
- `atr`
- `macd`
- `volatility`
- `oi_delta`
- `price_momentum`

**Methods:**
- `__post_init__()`

#### Functions

### File: `learning_snapshot.py`

#### Classes

**TradeOutcome** (line 9)

> Record of a single completed trade.

**Attributes:**
- `trade_id`
- `plan_id`
- `direction`
- `entry_price`
- `exit_price`
- `pnl_percent`
- `duration_hours`
- `exit_reason`

**LearningSnapshot** (line 23)

> River layer output — hasil belajar dari histori trade.

**Attributes:**
- `snapshot_id`
- `timestamp`
- `total_trades`
- `win_rate`
- `avg_rr`
- `profit_factor`
- `max_drawdown`
- `patterns`
- `failure_patterns`
- `recent_outcomes`

**Methods:**
- `__post_init__()`

#### Functions

### File: `macd.py`

#### Classes

**MACD** (line 10)

> Immutable MACD model.

**Attributes:**
- `timestamp`
- `macd`
- `signal`
- `histogram`
- `bucket`

**Methods:**
- `__post_init__()`

#### Functions

### File: `market_snapshot.py`

#### Classes

**MarketSnapshot** (line 12)

> Observe layer output — seluruh snapshot market pada satu timestamp.

**Attributes:**
- `snapshot_id`
- `symbol`
- `timestamp`
- `candle`
- `open_interest`
- `volume`
- `exchange_data`

**Methods:**
- `__post_init__()`

#### Functions

### File: `market_understanding.py`

#### Classes

**MarketUnderstanding** (line 10)

> Understand layer output — pemahaman struktur yang sudah dianalisis.

**Attributes:**
- `snapshot_id`
- `timestamp`
- `trend_strength`
- `compression_level`
- `wave_quality`
- `structural_confidence`
- `geometry`

**Methods:**
- `__post_init__()`

#### Functions

### File: `metrics.py`

#### Classes

**TradingMetrics** (line 11)

> Comprehensive trading metrics from a set of trade outcomes.

win_rate:         0.0 - 1.0
sharpe_ratio:     annualized, based on daily returns
max_drawdown:     0.0 - 1.0
profit_factor:    gross profit...

**Attributes:**
- `win_rate`
- `sharpe_ratio`
- `max_drawdown`
- `profit_factor`
- `avg_rr`
- `total_trades`
- `avg_win`
- `avg_loss`
- `expectancy`
- `equity_curve`

**Methods:**
- `__post_init__()`

#### Functions

**calculate_metrics**(outcomes) - line 44

> Calculate comprehensive metrics from a list of trade outcomes.

#### Variables

- `sharpe_ratio` = `0.0` (line 94)

### File: `open_interest.py`

#### Classes

**OpenInterest** (line 10)

> Immutable Open Interest model.

**Attributes:**
- `symbol`
- `timestamp`
- `value`
- `state`

**Methods:**
- `__post_init__()`

#### Functions

### File: `order.py`

#### Classes

**Fill** (line 11)

> Partial fill of an order.

**Attributes:**
- `fill_id`
- `price`
- `quantity`
- `timestamp`
- `fee`

**Order** (line 21)

> An order placed on an exchange (real or simulated).

order_type: MARKET / LIMIT / STOP / OCO
state:      PENDING / FILLED / PARTIAL / CANCELLED / REJECTED

**Attributes:**
- `order_id`
- `plan_id`
- `symbol`
- `direction`
- `order_type`
- `price`
- `quantity`
- `filled_quantity`
- `state`
- `timestamp`
- `fills`
- `oco_order_id`

**Methods:**
- `__post_init__()`

#### Functions

### File: `position.py`

#### Classes

**Position** (line 10)

> Trading position with lifecycle state.

**Attributes:**
- `position_id`
- `symbol`
- `side`
- `entry_price`
- `quantity`
- `state`
- `timestamp`

**Methods:**
- `__post_init__()`

#### Functions

### File: `provenance.py`

#### Classes

**Provenance** (line 8)

> Data lineage — melacak asal-usul snapshot.

**Attributes:**
- `source_layer`
- `source_timestamp`
- `parent_snapshots`
- `pipeline_version`

**Methods:**
- `__post_init__()`

#### Functions

### File: `river_state.py`

#### Classes

**RiverState** (line 10)

> River learning state with recommendation.

**Attributes:**
- `snapshot_id`
- `state`
- `recommendation`
- `learning_confidence`
- `total_trades`

**Methods:**
- `__post_init__()`

#### Functions

### File: `structural_state.py`

#### Classes

**StructuralSnapshot** (line 10)

> Official market structural snapshot with state, confidence and geometry.

**Attributes:**
- `snapshot_id`
- `state`
- `confidence`
- `geometry`
- `nearest_support`
- `nearest_resistance`

**Methods:**
- `__post_init__()`

#### Functions

### File: `structure_snapshot.py`

#### Classes

**TrendInfo** (line 13)

> Trend line identified from Supertrend Lines.

**Attributes:**
- `direction`
- `strength`
- `start_timestamp`
- `end_timestamp`
- `slope`

**CompressionZone** (line 23)

> Sideways / low volatility zone.

**Attributes:**
- `start_timestamp`
- `end_timestamp`
- `upper_price`
- `lower_price`
- `atr_percent`

**FibLevel** (line 33)

> Fibonacci retracement level.

**Attributes:**
- `level`
- `price`

**StructureSnapshot** (line 40)

> Multi-Timeframe Structure Engine output — seluruh struktur market.

**Attributes:**
- `snapshot_id`
- `symbol`
- `timestamp`
- `points`
- `lines`
- `waves`
- `trends`
- `compressions`
- `fib_levels`
- `nearest_support`
- `nearest_resistance`

**Methods:**
- `__post_init__()`

#### Functions

### File: `supertrend_line.py`

#### Classes

**SupertrendLine** (line 10)

> Immutable Supertrend Line.

**Attributes:**
- `line_id`
- `symbol`
- `timeframe`
- `direction`
- `price`
- `start_timestamp`
- `end_timestamp`
- `candle_count`
- `touch_count`
- `status`

**Methods:**
- `__post_init__()`

#### Functions

### File: `supertrend_point.py`

#### Classes

**SupertrendPoint** (line 10)

> Immutable Supertrend Point.

**Attributes:**
- `point_id`
- `symbol`
- `timeframe`
- `timestamp`
- `price`
- `atr`
- `direction`
- `candle_index`

**Methods:**
- `__post_init__()`

#### Functions

### File: `supertrend_wave.py`

#### Classes

**SupertrendWave** (line 10)

> Immutable Supertrend Wave.

**Attributes:**
- `wave_id`
- `symbol`
- `timeframe`
- `direction`
- `start_line_id`
- `end_line_id`
- `amplitude`
- `duration`
- `status`

**Methods:**
- `__post_init__()`

#### Functions

### File: `trading_plan.py`

#### Classes

**PartialExit** (line 11)

> Partial exit level for scaled exit strategy.

**Attributes:**
- `price`
- `percent`

**TradingPlan** (line 18)

> Adaptive Trading Plan - core object of the system.

**Attributes:**
- `plan_id`
- `strategy`
- `direction`
- `entry_zone_low`
- `entry_zone_high`
- `stop_loss`
- `take_profit`
- `risk_percent`
- `confidence`
- `state`
- `reason`
- `revision`
- `partial_exits`
- `funding_cost_estimate`
- `liquidation_price`

**Methods:**
- `__post_init__()`

#### Functions


---

## Module: multi_timeframe_structural_engine

### File: `__init__.py`

### File: `engine.py`

#### Classes

**MultiTimeframeStructuralEngine** (line 18)

> Orchestrates structure building across all timeframes.

Output: StructureSnapshot (Trend + Compression + Fibonacci + Points/Lines/Waves)

**Methods:**
- `__init__()`
- `process()`
- `_build_points()`
- `_build_lines()`
- `_build_waves()`
- `_detect_trends()`
- `_detect_compressions()`
- `_calculate_fib_levels()`
- `_find_support_resistance()`

#### Functions

**process**(self, symbol, candles) - line 30

> Process all timeframes and return StructureSnapshot.

#### Variables

- `segment_start` = `0` (line 83)
- `start_idx` = `0` (line 165)
- `strength` = `5` (line 166)
- `strength` = `5` (line 184)


---

## Module: multi_timeframe_structural_engine/supertrend_line

### File: `__init__.py`


---

## Module: observe

### File: `__init__.py`

### File: `binance_observer.py`

#### Classes

**BinanceObserver** (line 15)

> C001 — Real data collection from Binance Futures (REST + WebSocket ready).

**Methods:**
- `__init__()`
- `get_candles()`
- `get_open_interest()`
- `observe()`

#### Functions

**get_candles**(self, symbol, timeframes, limit) - line 21

**get_open_interest**(self, symbol) - line 28

**observe**(self, symbol, timeframes, candle_limit) - line 34

> Override observe untuk mengambil data real dari Binance.

### File: `live_pipeline.py`

#### Classes

**LivePipeline** (line 16)

> Pipeline yang menggunakan data real dari Binance (REST).

**Methods:**
- `__init__()`
- `run()`

#### Functions

**run**(self, symbol, timeframes, candle_limit, risk_method) - line 24

> Jalankan satu siklus pipeline dengan data live.

### File: `observer.py`

#### Classes

**Observer** (line 14)

> C001 — Abstract data collection orchestrator.

Mengamati pasar apa adanya (Candle, Volume, Open Interest).
Tidak ada analisis di tahap ini.

**Methods:**
- `get_candles()`
- `get_open_interest()`
- `observe()`

#### Functions

**get_candles**(self, symbol, timeframes, limit) - line 22

**get_open_interest**(self, symbol) - line 26

**observe**(self, symbol, timeframes, candle_limit) - line 29

> C001 — Observe: kumpulkan data market dan bungkus dalam MarketSnapshot.

Returns MarketSnapshot dengan candle terakhir, OI, dan volume.

### File: `simulation_observer.py`

#### Classes

**SimulationObserver** (line 12)

> Data collection from simulation data source.

Mengembalikan data default untuk simulasi.

**Methods:**
- `get_candles()`
- `get_open_interest()`

#### Functions

**get_candles**(self, symbol, timeframes, limit) - line 18

**get_open_interest**(self, symbol) - line 21

### File: `websocket_observer.py`

#### Classes

**WebSocketObserver** (line 14)

> C001 — WebSocket observer untuk sub-H1 timeframes real-time.

Mengamati pasar via WebSocket (simulated).
Sub-H1 timeframes: 1m, 5m, 15m — untuk deteksi struktur lebih granular.

**Methods:**
- `__init__()`
- `start()`
- `stop()`
- `feed_candle()`
- `get_candles()`
- `get_open_interest()`
- `observe()`

#### Functions

**start**(self) - line 25

> Start WebSocket connection (simulated).

**stop**(self) - line 29

> Stop WebSocket connection.

**feed_candle**(self, candle) - line 33

> Feed a new candle (simulated WebSocket message).

**get_candles**(self, symbol, timeframes, limit) - line 40

> Get candles from buffer (sub-H1 real-time).

**get_open_interest**(self, symbol) - line 49

> WebSocket OI — default flat untuk simulasi.

**observe**(self, symbol, timeframes, candle_limit) - line 54

> Observe: ambil candle terbaru dari buffer WebSocket.


---

## Module: persistence

### File: `__init__.py`

#### Variables

- `__all__` = `['BaseRepository', 'SqlitePlanRepository', 'Sqlite` (line 21)

### File: `base_repository.py`

#### Classes

**BaseRepository** (line 13)

> Abstract base repository interface.

**Methods:**
- `save()`
- `get()`
- `list_all()`
- `delete()`
- `count()`
- `update()`
- `find_by()`

#### Functions

**save**(self, entity) - line 17

> Save an entity.

**get**(self, entity_id) - line 22

> Get an entity by ID.

**list_all**(self) - line 27

> List all entities.

**delete**(self, entity_id) - line 32

> Delete an entity by ID.

**count**(self) - line 37

> Count total entities.

**update**(self, entity_id, data) - line 41

> Update an entity by ID.

**find_by**(self) - line 45

> Find entities by criteria.

### File: `sqlite_repository.py`

#### Classes

**SqliteConnectionManager** (line 20)

> Manage SQLite connections with proper lifecycle.

**Methods:**
- `__init__()`
- `get_connection()`
- `close()`

**SqlitePlanRepository** (line 153)

> SQLite repository for Trading Plans.

**Methods:**
- `__init__()`
- `_get_conn()`
- `save()`
- `get()`
- `_row_to_plan()`
- `list_all()`
- `delete()`
- `count()`
- `find_by_status()`
- `find_by_symbol()`

**SqliteOutcomeRepository** (line 281)

> SQLite repository for Trade Outcomes.

**Methods:**
- `__init__()`
- `_get_conn()`
- `save()`
- `get()`
- `_row_to_outcome()`
- `list_all()`
- `delete()`
- `count()`
- `find_by_plan_id()`
- `get_win_rate()`

**SqliteStructureRepository** (line 399)

> SQLite repository for Historical Structures.

**Methods:**
- `__init__()`
- `_get_conn()`
- `save()`
- `get()`
- `_row_to_snapshot()`
- `list_all()`
- `delete()`
- `count()`
- `find_by_symbol()`

**SqliteLearningRepository** (line 498)

> SQLite repository for Learning Data.

**Methods:**
- `__init__()`
- `_get_conn()`
- `store()`
- `get()`
- `delete()`
- `count()`
- `find_by_category()`

**SqliteBacktestRepository** (line 566)

> SQLite repository for Backtest Results.

**Methods:**
- `__init__()`
- `_get_conn()`
- `save()`
- `get()`
- `list_all()`
- `delete()`
- `count()`
- `find_best_strategy()`

#### Functions

**get_db_manager**(db_path) - line 45

**init_database**(db_path) - line 52

> Initialize database schema.

**get_connection**(self) - line 27

**close**(self) - line 35

**save**(self, plan) - line 163

**get**(self, plan_id) - line 194

**list_all**(self) - line 231

**delete**(self, plan_id) - line 243

**count**(self) - line 250

**find_by_status**(self, status) - line 256

**find_by_symbol**(self, symbol) - line 268

**save**(self, outcome) - line 291

**get**(self, trade_id) - line 319

**list_all**(self) - line 351

**delete**(self, trade_id) - line 363

**count**(self) - line 370

**find_by_plan_id**(self, plan_id) - line 376

**get_win_rate**(self) - line 388

> Calculate overall win rate.

**save**(self, snapshot) - line 409

**get**(self, snapshot_id) - line 432

**list_all**(self) - line 460

**delete**(self, snapshot_id) - line 472

**count**(self) - line 479

**find_by_symbol**(self, symbol) - line 485

**store**(self, category, key, value, confidence) - line 508

**get**(self, category, key) - line 527

**delete**(self, category, key) - line 539

**count**(self) - line 546

**find_by_category**(self, category) - line 552

**save**(self, backtest_result) - line 576

**get**(self, backtest_id) - line 605

**list_all**(self) - line 614

**delete**(self, backtest_id) - line 621

**count**(self) - line 628

**find_best_strategy**(self) - line 634

> Find the best performing strategy by total PnL.

#### Variables

- `plans` = `[]` (line 236)
- `plans` = `[]` (line 261)
- `plans` = `[]` (line 273)
- `outcomes` = `[]` (line 356)
- `outcomes` = `[]` (line 381)
- `snapshots` = `[]` (line 465)
- `snapshots` = `[]` (line 490)
- `result` = `{}` (line 557)


---

## Module: preserve

### File: `__init__.py`

### File: `line_status_manager.py`

#### Classes

**LineStatusManager** (line 10)

> C004 — Menjaga kontinuitas Supertrend Line.

Line tidak pernah dihapus, hanya berubah status:
ACTIVE  → masih relevan dengan harga saat ini
BROKEN  → harga sudah menembus line
ARCHIVED → sudah lama br...

**Methods:**
- `evaluate()`
- `_determine_status()`
- `_is_broken()`

#### Functions

**evaluate**(self, current_price, lines) - line 19

> Evaluasi semua line terhadap harga terkini, kembalikan line dgn status terbaru.

### File: `preserver.py`

#### Classes

**SnapshotRepository** (line 14)

> C004 — Preserve layer.

Menyimpan seluruh snapshot dengan provenance.
Menjaga kontinuitas Supertrend Line via LineStatusManager.

**Methods:**
- `__init__()`
- `store_market()`
- `store_indicators()`
- `store_structure()`
- `evaluate_lines()`
- `get_market()`
- `get_indicators()`
- `get_structure()`
- `get_provenance()`
- `get_latest_structure()`
- `list_all_structures()`

#### Functions

**store_market**(self, snapshot, parent_snapshots) - line 28

**store_indicators**(self, snapshot, parent_snapshots) - line 38

**store_structure**(self, snapshot, current_price, parent_snapshots) - line 48

> Store structure + evaluasi LineStatus terhadap harga terkini.

Args:
    snapshot: StructureSnapshot dari Engine
    current_price: Harga market aktual. Jika None, pakai nearest_support.

**evaluate_lines**(self, snapshot, current_price) - line 87

> Evaluasi ulang semua lines terhadap harga terbaru (untuk C004).

**get_market**(self, snap_id) - line 107

**get_indicators**(self, snap_id) - line 110

**get_structure**(self, snap_id) - line 113

**get_provenance**(self, snap_id) - line 116

**get_latest_structure**(self) - line 119

**list_all_structures**(self) - line 124


---

## Module: remember

### File: `__init__.py`

### File: `historical_repository.py`

#### Classes

**HistoricalStructureRepository** (line 8)

> C005 — Historical Structure Repository (Append-only).

Menyimpan seluruh struktur yang pernah terbentuk.
Tidak ada penghapusan. Hanya tambah.

**Methods:**
- `__init__()`
- `store()`
- `get()`
- `list_all()`
- `count()`

#### Functions

**store**(self, snapshot) - line 18

**get**(self, snapshot_id) - line 21

**list_all**(self) - line 24

**count**(self) - line 27

### File: `memory.py`

#### Classes

**HistoricalContext** (line 13)

> Remember layer output — konteks historis yang relevan.

**Attributes:**
- `similar_structures`
- `similar_waves`
- `similar_compressions`
- `similar_trends`
- `total_snapshots`

**StructureMemory** (line 22)

> C005 — Remember layer (Append-only).

Menyimpan seluruh histori struktur ke HistoricalStructureRepository.
Tidak ada penghapusan — append-only sesuai Constitution.

**Methods:**
- `__init__()`
- `store()`
- `find_similar()`
- `get_repository()`

#### Functions

**store**(self, snapshot) - line 32

**find_similar**(self, snapshot) - line 35

> Cari snapshot dengan struktur serupa dari repository append-only.

**get_repository**(self) - line 66


---

## Module: risk

### File: `__init__.py`

### File: `risk_manager.py`

#### Classes

**RiskManager** (line 11)

> Risk Manager — position sizing dengan Kelly / Fixed Fraction.

Menghitung ukuran posisi berdasarkan:
- Kelly Criterion (optimal f)
- Fixed Fraction (fixed % per trade)
- Account balance constraints

**Attributes:**
- `_consecutive_losses`

**Methods:**
- `__init__()`
- `balance()`
- `set_balance()`
- `kelly_percent()`
- `fixed_fraction_size()`
- `kelly_size()`
- `compute_position()`
- `compute_actual_quantity()`
- `record_loss()`
- `record_win()`
- `get_risk_multiplier()`
- `should_pause()`

#### Functions

**balance**(self) - line 24

**set_balance**(self, balance) - line 27

**kelly_percent**(self, outcomes) - line 30

> Kelly Criterion: f* = (p * b - q) / b

p = win_rate, q = 1-p, b = avg_win/avg_loss (odds)
Returns fraction of bankroll to risk (0.0 - 1.0).

**fixed_fraction_size**(self, risk_percent) - line 50

> Fixed Fraction sizing: position_size = balance * risk_percent / 100

**kelly_size**(self, outcomes, plan) - line 54

> Kelly-based position size: balance * kelly_fraction

**compute_position**(self, plan, outcomes, method) - line 61

> Compute position size untuk TradingPlan.

Args:
    plan: TradingPlan dengan risk_percent
    outcomes: Trade history untuk Kelly (optional)
    method: "fixed_fraction" atau "kelly"

Returns:
    Position size in quote currency

**compute_actual_quantity**(self, plan, balance, leverage) - line 77

> Compute actual contract quantity using formula: Quantity = (Balance × Risk%) / |Entry - SL|

Args:
    plan: TradingPlan with entry_zone_low and stop_loss
    balance: Current account balance
    leverage: Account leverage (default 1x)

Returns:
    Actual contract quantity (lot size) to trade

**record_loss**(self) - line 100

> Record a consecutive loss for drawdown control.

**record_win**(self) - line 104

> Reset consecutive loss counter on a win.

**get_risk_multiplier**(self) - line 108

> Return risk size multiplier based on consecutive losses.

Loss #1-2 → 100% (normal)
Loss #3 → 50%
Loss #4 → 25%
Loss #5+ → 0% (PAUSE)

**should_pause**(self) - line 124

> Return True if trading should pause (5+ consecutive losses).


---

## Module: river

### File: `__init__.py`

### File: `opportunity_learning.py`

#### Classes

**RejectedOpportunity** (line 11)

> Record of a rejected trading plan that became an opportunity (or correct rejection).

**Attributes:**
- `plan_id`
- `timestamp`
- `direction`
- `reason`
- `entry_price`
- `actual_direction`
- `price_movement`
- `was_missed_opportunity`
- `confidence_at_rejection`

**OpportunityLearning** (line 26)

> Opportunity Cost Tracking — belajar dari trade yang DITOLAK.

Mencatat semua trading plan yang ditolak oleh Authorize, lalu menganalisis:
- Apakah penolakan itu benar? (harga bergerak berlawanan → cor...

**Attributes:**
- `_rejected_plans`
- `_missed_count`
- `_correct_rejection_count`

**Methods:**
- `record_rejection()`
- `update_outcome()`
- `get_missed_opportunity_rate()`
- `get_analysis()`
- `get_patterns_to_relax()`
- `count()`

#### Functions

**record_rejection**(self, plan_id, timestamp, direction, reason, entry_price, confidence) - line 40

> Catat rencana trading yang ditolak.

**update_outcome**(self, plan_id, current_price, market_direction) - line 60

> Update hasil dari penolakan — apakah ini missed opportunity atau correct rejection?

Args:
    plan_id: ID dari rencana yang ditolak
    current_price: Harga pasar saat ini (setelah penolakan)
    market_direction: Arah pergerakan pasar setelah penolakan ("LONG" atau "SHORT")

**get_missed_opportunity_rate**(self, reason) - line 97

> Hitung persentase missed opportunity secara global atau per reason.

Returns:
    Float 0.0-1.0 menunjukkan seberapa sering kita melewatkan peluang

**get_analysis**(self) - line 116

> Dapatkan analisis lengkap opportunity cost.

Returns:
    {
        "total_rejected": int,
        "missed_opportunities": int,
        "correct_rejections": int,
        "missed_rate": float,
        "by_reason": {reason: {"missed": int, "correct": int, "rate": float}},
    }

**get_patterns_to_relax**(self, threshold) - line 158

> Identifikasi rejection reasons yang terlalu ketat (missed rate > threshold).

Args:
    threshold: Jika missed rate > threshold, reason ini perlu direlaksasi
    
Returns:
    List of reasons yang perlu direlaksasi

**count**(self) - line 176

> Total rejected plans yang tercatat.

#### Variables

- `patterns` = `[]` (line 168)

### File: `river_entry.py`

#### Classes

**RiverEntry** (line 11)

> River entry — validasi entry dengan konfirmasi tambahan.

**Methods:**
- `validate_entry()`

#### Functions

**validate_entry**(self, plan, current_price, oi, learning) - line 14

> Validasi entry: price in zone + konfirmasi dari River learning.

### File: `river_exit.py`

#### Classes

**RiverExit** (line 8)

> River exit — trailing stop + take profit bertahap.

**Methods:**
- `should_exit()`

#### Functions

**should_exit**(self, position, current_price, atr) - line 11

> Cek exit signal: trailing stop berdasarkan ATR.

### File: `river_learning.py`

#### Classes

**RiverLearning** (line 10)

> River learning — statistical pattern accumulation.

**Methods:**
- `__init__()`
- `record_outcome()`
- `get_snapshot()`

#### Functions

**record_outcome**(self, outcome) - line 16

**get_snapshot**(self) - line 19

### File: `river_repository.py`

#### Classes

**RiverRepository** (line 8)

> Repository untuk LearningSnapshot.

**Methods:**
- `__init__()`
- `save()`
- `get()`

#### Functions

**save**(self, symbol, snapshot) - line 14

**get**(self, symbol) - line 17

### File: `river_review.py`

#### Classes

**RiverReview** (line 14)

> C010 — River Plan Review dengan Shared Learning pattern matching.

Membandingkan Trading Plan dengan pengalaman historis.
Menghasilkan RiverRecommendation + RiverLearningConfidence.

Jika shared_repo ...

**Methods:**
- `review()`
- `_build_state()`
- `_review_global()`
- `_review_with_patterns()`

#### Functions

**review**(self, plan, learning, shared_repo) - line 26

> Review Trading Plan berdasarkan historical learning + pattern matching.

Args:
    plan: TradingPlan yang akan direview
    learning: LearningSnapshot dari River
    shared_repo: Optional — untuk per-pattern matching dari Shared Learning Repository

Returns:
    RiverState dengan recommendation + co...

### File: `shared_learning_repository.py`

#### Classes

**SharedLearningRepository** (line 9)

> Shared Learning Repository — pusat pengetahuan bersama.

Menyimpan semua TradeOutcome (termasuk rejected trades untuk Opportunity Learning).
Bisa diakses oleh Long, Short, dan Sideway Worker.
Append-o...

**Methods:**
- `__init__()`
- `record_outcome()`
- `record_rejected_plan()`
- `get_all_outcomes()`
- `get_rejected_plans()`
- `get_outcomes_by_direction()`
- `count()`
- `analyze_rejections()`

#### Functions

**record_outcome**(self, outcome) - line 21

**record_rejected_plan**(self, plan_id, reason, confidence, direction) - line 24

**get_all_outcomes**(self) - line 32

**get_rejected_plans**(self) - line 35

**get_outcomes_by_direction**(self, direction) - line 38

**count**(self) - line 41

**analyze_rejections**(self, current_price, actual_direction) - line 44

> Analyze opportunity cost from rejected plans.

Returns:
    {
        "total_rejected": int,
        "missed_opportunities": int,  # price moved in rejected direction
        "correct_rejections": int,    # price moved against rejected direction
    }

#### Variables

- `missed` = `0` (line 57)
- `correct` = `0` (line 58)


---

## Module: root

### File: `__init__.py`

#### Variables

- `__all__` = `['Pipeline', 'PipelineResult', 'RiskManager', 'Bac` (line 24)

### File: `improve.py`

#### Functions

**improve**(river_learning, position, exit_price, exit_reason, shared_repository) - line 13

> Post-Trade — Improve → River feedback loop.

Setelah trade closed, feedback dikirim ke River dan SharedLearningRepository.
Hanya mencatat outcome — tidak merekam rejection (itu untuk OpportunityLearning terpisah).

#### Variables

- `duration` = `0` (line 26)

### File: `main.py`

#### Functions

**main**() - line 21

> ST_LMS v1.1 — Final Pipeline (C001-C012 + Post-Trade).

### File: `main_server.py`

#### Classes

**BotState** (line 47)

**Methods:**
- `__init__()`

**ControlCommand** (line 64)

**Attributes:**
- `action`
- `mode`

**TradeHistoryItem** (line 68)

**Attributes:**
- `timestamp`
- `symbol`
- `side`
- `entry_price`
- `exit_price`
- `pnl`
- `status`

#### Functions

**root**() - line 80

**get_status**() - line 84

> Get real-time bot status for dashboard

**get_pipeline_logs**(limit) - line 99

> Get recent pipeline execution logs

**get_trade_history**() - line 104

> Get full trade history

**get_river_learning**() - line 109

> Get River learning stats and opportunity cost

**get_darwin_stats**() - line 122

> Get Darwin improvement stats

#### Variables

- `base_price` = `50000.0` (line 163)

### File: `pipeline.py`

#### Classes

**PipelineResult** (line 40)

> Hasil dari satu siklus pipeline penuh.

**Attributes:**
- `market_snapshot`
- `indicator_snapshot`
- `structure_snapshot`
- `understanding`
- `structural_snapshot`
- `trading_plan`
- `authorization`
- `position_id`
- `river_learning`
- `darwin_recommendation`
- `position_size`
- `parent_snapshot_ids`

**Pipeline** (line 56)

> Pipeline ST_LMS — C001 sampai C012 + Post-Trade.

Sesuai Constitution Final v1.0.
5 Prinsip Mutlak enforced:
1. Structure First: semua dari Supertrend Line
2. Plan Before Trade: TradingPlan wajib sebe...

**Methods:**
- `__init__()`
- `get_position()`
- `get_balance()`
- `set_balance()`
- `run()`

#### Functions

**get_position**(self, position_id) - line 99

> Public accessor for BacktestEngine.

**get_balance**(self) - line 103

> Public accessor for BacktestEngine.

**set_balance**(self, balance) - line 107

> Public accessor for BacktestEngine.

**run**(self, symbol, timeframes, candles, risk_method) - line 111

> Jalankan pipeline penuh dari C001 ke Post-Trade.

Args:
    symbol: Pasangan trading (e.g. BTCUSDT)
    timeframes: Daftar timeframe
    candles: Data candle per timeframe
    risk_method: "fixed_fraction" atau "kelly"

Returns:
    PipelineResult dengan semua output stage

### File: `run_bot.py`

#### Functions

**generate_demo_candles**(count) - line 19

> Generate demo candles (uptrend).

**run_single_cycle**() - line 39

**run_backtest**() - line 56

#### Variables

- `candles` = `[]` (line 21)


---

## Module: select

### File: `__init__.py`

### File: `adaptive_stack.py`

#### Classes

**StructureAge** (line 12)

> Umur struktur — berapa candle sejak terbentuk.

**Attributes:**
- `snapshot_id`
- `timestamp`
- `age_in_candles`
- `is_mature`

**RankedStructure** (line 21)

> Struktur yang sudah di-rank untuk Adaptive Structure Stack.

**Attributes:**
- `snapshot`
- `age`
- `price_distance`
- `relevance_score`

**AdaptiveStructureStack** (line 29)

> C006 — Adaptive Structure Stack.

Memilih Living Market Structure:
- Struktur terdekat dengan harga saat ini
- Struktur dengan age yang成熟 (mature)
- Struktur yang masih relevan (tidak terlalu tua)

**Methods:**
- `__init__()`
- `build()`
- `get_living_structures()`
- `_calculate_age()`
- `_price_distance()`
- `_calculate_relevance()`

#### Functions

**build**(self, snapshots, current_price) - line 41

> Bangun stack dari seluruh snapshot, urut berdasarkan relevansi.

**get_living_structures**(self, ranked) - line 57

> Filter hanya struktur yang masih 'hidup' (relevance > threshold).

### File: `selector.py`

#### Classes

**Candidate** (line 15)

> C006 — Select layer output: kandidat struktur terbaik untuk dianalisis.

**Attributes:**
- `snapshot`
- `context`
- `rank_score`
- `reason`
- `structure_age`

**Selector** (line 24)

> C006 — Select layer.

Menggunakan AdaptiveStructureStack untuk memilih Living Market Structure.
Memperhitungkan Structure Age (kematangan struktur).

**Methods:**
- `__init__()`
- `get_active_timeframes()`
- `get_primary_timeframe()`
- `get_confirmation_timeframes()`
- `select_candidate()`

#### Functions

**get_active_timeframes**(self) - line 35

**get_primary_timeframe**(self) - line 38

**get_confirmation_timeframes**(self) - line 41

**select_candidate**(self, snapshot, context) - line 44

> Rank dan filter kandidat — menggunakan AdaptiveStructureStack.


---

## Module: trading_plan

### File: `__init__.py`

### File: `plan_manager.py`

#### Classes

**PlanManager** (line 20)

> C009/C010/C011 — Orchestrates the full plan lifecycle.

Flow: PlanManager → RiverReview → AuthorizationGateway (single authority)

**Methods:**
- `__init__()`
- `create_and_validate()`
- `get_grid()`
- `review_plan()`
- `authorize()`

#### Functions

**create_and_validate**(self, snapshot) - line 34

> Create, validate and store a Trading Plan.

Transitions CREATED → READY after successful validation.

**get_grid**(self, plan_id) - line 69

> Ambil AdaptiveGrid untuk plan tertentu (hanya SIDEWAY).

**review_plan**(self, plan, learning) - line 73

> C010 — River Plan Review: review plan sebelum authorize.

**authorize**(self, plan, river_recommendation, enable_time_filter, enable_liquidation_check) - line 77

> C011 — Authorize: delegasi ke AuthorizationGateway (single authority).

Args:
    plan: TradingPlan must be in READY state
    river_recommendation: Wajib — hasil dari River Plan Review (Prinsip Mutlak #3)
    enable_time_filter: Enable Time-Based Filter (default False)
    enable_liquidation_check:...

### File: `planner.py`

#### Classes

**Planner** (line 14)

> Creates Trading Plans based on Structural State.

LONG → LongBuilder (Trend Following, Fib 0.382)
SHORT → ShortBuilder (Trend Following, Fib 0.618)
SIDEWAY → SidewayBuilder (Adaptive Grid)

**Methods:**
- `__init__()`
- `create_plan()`
- `create_plan_with_grid()`

#### Functions

**create_plan**(self, snapshot) - line 27

> Create a Trading Plan based on the current structural state.

**create_plan_with_grid**(self, snapshot) - line 39

> Create Trading Plan + AdaptiveGrid (khusus SIDEWAY).


---

## Module: trading_plan/builders

### File: `__init__.py`

### File: `long_builder.py`

#### Classes

**LongBuilder** (line 11)

> Builds LONG Trading Plans from Structural State with Partial Exit Strategy.

**Methods:**
- `build()`

#### Functions

**build**(self, snapshot, leverage) - line 14

> Create a LONG plan using Fibonacci 0.382 entry zone with scaled exit strategy.

Partial Exit Strategy:
- TP1 (50%): Fib 0.618 level
- TP2 (25%): Nearest resistance
- Runner (25%): Trailing stop based on Supertrend Line

### File: `short_builder.py`

#### Classes

**ShortBuilder** (line 11)

> Builds SHORT Trading Plans from Structural State with Partial Exit Strategy.

**Methods:**
- `build()`

#### Functions

**build**(self, snapshot, leverage) - line 14

> Create a SHORT plan using Fibonacci 0.618 entry zone with scaled exit strategy.

Partial Exit Strategy:
- TP1 (50%): Fib 0.382 level (from bottom)
- TP2 (25%): Nearest support
- Runner (25%): Trailing stop based on Supertrend Line

### File: `sideway_builder.py`

#### Classes

**SidewayBuilder** (line 13)

> Builds SIDEWAY Adaptive Grid strategy with Partial Exit and Funding Awareness.

Menghasilkan dua output:
1. TradingPlan — generik, berisi entry zone dan risk dengan partial exits
2. AdaptiveGrid — spe...

**Methods:**
- `build()`

#### Functions

**build**(self, snapshot, leverage) - line 23

> Create TradingPlan + AdaptiveGrid dari StructuralSnapshot SIDEWAY.

Features added:
- Liquidation price monitoring
- Funding cost estimate for grid holding period
- Partial exits for grid levels

#### Variables

- `partial_exits` = `[]` (line 50)


---

## Module: trading_plan/models

### File: `__init__.py`

### File: `adaptive_grid.py`

#### Classes

**AdaptiveGrid** (line 10)

> Sideway-specific grid strategy — hanya dibuat oleh SidewayBuilder saat StructuralState == SIDEWAY.

Field ini TIDAK boleh ada di TradingPlan karena Grid hanya milik Sideway.
LongBuilder dan ShortBuild...

**Attributes:**
- `grid_id`
- `plan_id`
- `entry_zone_low`
- `entry_zone_high`
- `grid_spacing`
- `grid_levels`
- `scale_in_size`
- `grid_take_profit`
- `risk_limit`
- `state`

**Methods:**
- `__post_init__()`

#### Functions


---

## Module: trading_plan/repository

### File: `__init__.py`

### File: `plan_repository.py`

#### Classes

**PlanRepository** (line 8)

> In-memory repository for Trading Plans.

**Methods:**
- `__init__()`
- `save()`
- `get()`
- `list_all()`

#### Functions

**save**(self, plan) - line 14

**get**(self, plan_id) - line 17

**list_all**(self) - line 20


---

## Module: trading_plan/validators

### File: `__init__.py`

### File: `plan_validator.py`

#### Classes

**PlanValidator** (line 9)

> Validates Trading Plan integrity and risk compliance.

**Methods:**
- `validate()`

#### Functions

**validate**(self, plan) - line 12

> Check if a Trading Plan passes all validation rules.


---

## Module: understand

### File: `__init__.py`

### File: `geometry.py`

#### Classes

**GeometryAnalyzer** (line 12)

> C007 — Understand layer.

Menganalisis bentuk geometri struktur:
ASCENDING, DESCENDING, CORRIDOR, CONVERGING, DIVERGING,
CHAOTIC, SINGLE_DIRECTION, NO_STRUCTURE

**Methods:**
- `analyze()`
- `_calculate_trend_strength()`
- `_calculate_compression_level()`
- `_calculate_wave_quality()`
- `_detect_geometry()`

#### Functions

**analyze**(self, candidate) - line 20

> Produces MarketUnderstanding dari kandidat struktur terpilih.

#### Variables

- `lines_list` = `[]` (line 65)


---

## Module: utils

### File: `__init__.py`

### File: `helpers.py`

#### Functions

**generate_plan_id**() - line 7

> Generate a unique Trading Plan ID.

**generate_line_id**(symbol, price) - line 15

> Generate a Supertrend Line ID.

**generate_point_id**() - line 20

> Generate a Supertrend Point ID.

**generate_snapshot_id**(prefix) - line 25

> Generate a unique Snapshot ID.

**generate_grid_id**() - line 30

> Generate a unique Adaptive Grid ID.

**generate_trade_id**() - line 35

> Generate a unique Trade ID.

**generate_authorization_id**() - line 40

> Generate a unique Authorization ID.

### File: `logger.py`

#### Functions

**get_logger**() - line 8

> Get the ST_LMS logger instance.

**setup_logging**(level) - line 13

> Configure ST_LMS logging.


---


## Summary Statistics

- **Total Classes:** 136
- **Total Public Functions:** 250
- **Total Module Variables:** 220
