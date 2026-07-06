# SuperBot - Complete Pipeline Tracking System

## Overview
SuperBot adalah sistem lengkap untuk tracking dan monitoring pipeline trading ST_LMS (C001-C012) dengan fitur:
- ✅ Full pipeline traceability (semua stage C001-C012 dapat dilacak)
- ✅ Supertrend points & lines tracking di semua timeframe
- ✅ River & Darwin learning visualization
- ✅ Binance Futures API integration dengan date range selection
- ✅ Real-time execution tracking
- ✅ Interactive dashboard dengan charts dan tables

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 SuperBot Dashboard                   │
│              (Streamlit UI - Port 8501)             │
└──────────────────┬──────────────────────────────────┘
                   │ REST API
                   ▼
┌─────────────────────────────────────────────────────┐
│                  SuperBot API                        │
│            (FastAPI Backend - Port 8000)            │
├─────────────────────────────────────────────────────┤
│  Endpoints:                                          │
│  • POST /api/v1/candles/fetch                       │
│  • POST /api/v1/pipeline/run                        │
│  • GET  /api/v1/pipeline/traces                     │
│  • GET  /api/v1/supertrend/lines                    │
│  • GET  /api/v1/supertrend/points/{line_id}         │
│  • GET  /api/v1/river/learning                      │
│  • GET  /api/v1/darwin/recommendations              │
│  • GET  /api/v1/executions                          │
│  • POST /api/v1/backtest/run                        │
│  • GET  /api/v1/dashboard/stats                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              SQLite Database (superbot.db)          │
│  Tables:                                             │
│  • pipeline_traces                                  │
│  • supertrend_lines                                 │
│  • supertrend_points                                │
│  • execution_tracks                                 │
└─────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
```bash
pip install fastapi uvicorn streamlit requests pandas plotly python-multipart
```

### Quick Start
```bash
# Cara 1: Menggunakan script startup
./st_lms/start_superbot.sh

# Cara 2: Manual
# Terminal 1 - Start API
python -m st_lms.api.superbot_api

# Terminal 2 - Start Dashboard
streamlit run st_lms/dashboard/superbot_dashboard.py --server.port 8501
```

## Features

### 1. Dashboard Overview
- Real-time metrics: Total Pipelines, Trades, Win Rate, PnL
- Pipeline success rate chart
- Supertrend statistics
- River learning summary

### 2. Pipeline Traces
- Track setiap eksekusi pipeline dari C001 sampai C012
- Stage completion heatmap
- Detailed trace information
- Filter by symbol dan timeframe

### 3. Supertrend Lines
- View semua Supertrend lines di semua timeframe
- Filter: symbol, timeframe, active only
- Statistics: UP/DOWN trends, active lines
- Click to view points

### 4. Supertrend Points
- View individual points untuk setiap line
- Interactive price chart dengan ATR overlay
- Color-coded by trend direction (UP=green, DOWN=red)
- Data table dengan semua point details

### 5. River Learning
- Comprehensive learning metrics
- Win/Loss statistics
- Profit factor, avg win/loss
- Best/worst trades
- Consecutive wins/losses

### 6. Darwin Recommendations
- View semua optimization recommendations
- State, confidence, adjustments
- Reasoning untuk setiap recommendation
- Historical recommendations table

### 7. Execution Tracks
- Complete trade traceability
- Open/Closed positions
- PnL tracking
- PnL distribution histogram
- Filter by symbol dan status

### 8. Run Backtest
- Execute backtest dengan date range selection
- Multiple timeframe support
- Equity curve visualization
- All trades table

### 9. Run Pipeline
- Live pipeline execution
- Real-time stage results
- Darwin recommendation display
- Automatic trace storage

## API Documentation

### Fetch Candles
```bash
POST /api/v1/candles/fetch
{
    "symbol": "BTCUSDT",
    "timeframe": "H4",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "limit": 1000
}
```

### Run Pipeline
```bash
POST /api/v1/pipeline/run?symbol=BTCUSDT&timeframe=H4&start_date=2024-01-01&end_date=2024-01-31
```

### Get Pipeline Traces
```bash
GET /api/v1/pipeline/traces?symbol=BTCUSDT&timeframe=H4&limit=100
```

### Get Supertrend Lines
```bash
GET /api/v1/supertrend/lines?symbol=BTCUSDT&timeframe=H4&active_only=true&limit=100
```

### Get Supertrend Points
```bash
GET /api/v1/supertrend/points/{line_id}
```

### Get River Learning
```bash
GET /api/v1/river/learning
```

### Get Darwin Recommendations
```bash
GET /api/v1/darwin/recommendations?limit=50
```

### Get Execution Tracks
```bash
GET /api/v1/executions?symbol=BTCUSDT&status=CLOSED&limit=100
```

### Run Backtest
```bash
POST /api/v1/backtest/run
{
    "symbol": "BTCUSDT",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "timeframes": ["H4", "D1"],
    "initial_balance": 10000.0,
    "risk_method": "fixed_fraction"
}
```

### Dashboard Stats
```bash
GET /api/v1/dashboard/stats
```

## Database Schema

### pipeline_traces
- trace_id (PK)
- timestamp
- symbol
- timeframe
- stages_json
- market_snapshot_id
- indicator_snapshot_id
- structure_snapshot_id
- understanding_id
- structural_snapshot_id
- trading_plan_id
- authorization_id
- position_id
- position_size
- darwin_recommendation_json

### supertrend_lines
- line_id (PK)
- symbol
- timeframe
- trend_direction
- start_timestamp
- end_timestamp
- start_price
- current_price
- points_count
- is_active
- strength
- created_at

### supertrend_points
- point_id (PK)
- line_id (FK)
- timestamp
- price
- trend_direction
- atr_value
- multiplier
- timeframe
- symbol
- created_at

### execution_tracks
- execution_id (PK)
- pipeline_trace_id (FK)
- plan_id
- symbol
- direction
- entry_price
- exit_price
- position_size
- pnl
- pnl_percent
- status
- entry_timestamp
- exit_timestamp
- exit_reason
- duration_seconds
- river_learning_json
- darwin_recommendation_json

## Usage Examples

### Example 1: Run Pipeline untuk BTCUSDT H4 (Last 7 Days)
1. Buka Dashboard: http://localhost:8501
2. Pilih menu "▶️ Run Pipeline"
3. Isi form:
   - Symbol: BTCUSDT
   - Timeframe: H4
   - Start Date: 7 days ago
   - End Date: Today
   - Initial Balance: 10000
   - Risk Method: fixed_fraction
4. Klik "▶️ Run Pipeline"
5. Lihat hasil eksekusi dengan stage-by-stage breakdown

### Example 2: Track Supertrend Lines
1. Buka Dashboard: http://localhost:8501
2. Pilih menu "📈 Supertrend Lines"
3. Filter by symbol (BTCUSDT) dan timeframe (H4)
4. Lihat list semua lines dengan statistics
5. Klik line tertentu untuk melihat points

### Example 3: View River Learning
1. Buka Dashboard: http://localhost:8501
2. Pilih menu "🧠 River Learning"
3. Lihat comprehensive metrics:
   - Total trades, wins, losses
   - Win rate, profit factor
   - Average win/loss
   - Best/worst trades

### Example 4: Run Backtest
1. Buka Dashboard: http://localhost:8501
2. Pilih menu "🧪 Run Backtest"
3. Isi form:
   - Symbol: BTCUSDT
   - Date Range: Last 30 days
   - Timeframes: H4, D1
   - Initial Balance: 10000
4. Klik "▶️ Run Backtest"
5. Lihat equity curve dan semua trades

## Integration with ST_LMS Pipeline

SuperBot terintegrasi penuh dengan pipeline ST_LMS:
- **C001 Observe**: Market snapshot tracking
- **C002 Measure**: Indicator snapshot tracking
- **C003 Engine**: Structure snapshot tracking
- **C004 Preserve**: Line evaluation tracking
- **C005 Remember**: Memory context tracking
- **C006 Select**: Candidate selection tracking
- **C007 Understand**: Geometry analysis tracking
- **C008 Classify**: Structural state tracking
- **C009 Trading Plan**: Plan creation tracking
- **C010 River Review**: Learning review tracking
- **C011 Authorize**: Authorization tracking
- **C012 Execute**: Position execution tracking

Setiap stage disimpan dalam database untuk complete traceability.

## Troubleshooting

### API tidak connect
```bash
# Cek apakah API server running
curl http://localhost:8000/

# Jika error, restart API
python -m st_lms.api.superbot_api
```

### Dashboard tidak muncul
```bash
# Cek apakah Streamlit running
# Restart dashboard
streamlit run st_lms/dashboard/superbot_dashboard.py --server.port 8501
```

### Database error
```bash
# Reset database (hapus file lama)
rm superbot.db

# Restart API (akan create database baru)
python -m st_lms.api.superbot_api
```

### No data shown
```bash
# Pastikan sudah run pipeline atau backtest terlebih dahulu
# Data akan tersimpan setelah ada eksekusi
```

## License
MIT License

## Support
Untuk pertanyaan atau issue, silakan buat issue di repository.
