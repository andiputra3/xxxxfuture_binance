# SuperBot & ST-LMS Function Reference

Dokumentasi lengkap seluruh fungsi, kelas, dan endpoint yang terdapat dalam sistem SuperBot dan pipeline ST-LMS.

---

## 📂 1. Core Pipeline (`st_lms/core/`)

### `pipeline.py` - Orchestrator Utama
Mengkoordinasikan 12 stage mutlak (C001-C012) dari observasi hingga eksekusi.

| Fungsi / Kelas | Deskripsi | Input | Output |
| :--- | :--- | :--- | :--- |
| `ST_LMS_Pipeline` | Kelas utama pengendali alur kerja pipeline. | Konfigurasi awal | Objek Pipeline |
| `.run(symbol, timeframe, ...)` | Menjalankan siklus penuh pipeline untuk simbol & timeframe tertentu. | Symbol, TF, Date Range | `PipelineResult` (Snapshot, Plan, Execution ID) |
| `_observe()` | **C001**: Mengambil data pasar (OHLCV) dan snapshot kondisi terkini. | Market Data | `MarketSnapshot` |
| `_measure()` | **C002**: Menghitung indikator teknikal (Supertrend, ATR, RSI, MACD). | OHLCV | `IndicatorSnapshot` |
| `_engine()` | **C003**: Mendeteksi struktur market (High/Low, Swing Points). | MarketSnapshot | `StructureSnapshot` |
| `_preserve()` | **C004**: Menyimpan state struktur ke memori jangka pendek. | StructureSnapshot | Boolean (Success) |
| `_remember()` | **C005**: Mengambil pola historis dari database (River). | Pattern Query | List[PastPatterns] |
| `_select()` | **C006**: Memilih konteks market yang relevan dari memori. | Patterns, Current State | `Context` |
| `_understand()` | **C007**: Menganalisis makna konteks (Trend, Reversal, Sideway). | Context | `Understanding` |
| `_classify()` | **C008**: Mengklasifikasikan setup ke dalam kategori trade spesifik. | Understanding | `StructuralSnapshot` |
| `_plan()` | **C009**: Membangun rencana trading (Entry, SL, TP, Size). | StructuralSnapshot | `TradingPlan` |
| `_review()` | **C010**: Review rencana oleh modul "River" (Risk Check). | TradingPlan | `ReviewResult` |
| `_authorize()` | **C011**: Otorisasi akhir sebelum eksekusi (Darwin Check). | ReviewResult | `Authorization` |
| `_execute()` | **C012**: Eksekusi order (Simulasi atau Real) dan pencatatan. | Authorization | `ExecutionResult` (Position ID) |

---

## 📂 2. Indicators & Math (`st_lms/indicators/`)

### `supertrend.py`
Inti dari strategi trend-following.

| Fungsi | Deskripsi | Input | Output |
| :--- | :--- | :--- | :--- |
| `calculate_supertrend(df, period, multiplier)` | Menghitung garis Supertrend, arah trend, dan nilai ATR. | DataFrame (OHLC), Period, Multiplier | DataFrame (ST_Line, ST_Direction, ATR) |
| `_calculate_atr(df, period)` | Helper: Menghitung Average True Range. | DataFrame, Period | Series (ATR Values) |

### `macd.py`
Momentum indicator.

| Fungsi | Deskripsi | Input | Output |
| :--- | :--- | :--- | :--- |
| `calculate_macd(df, fast, slow, signal)` | Menghitung garis MACD, Signal, dan Histogram. | DataFrame, Fast, Slow, Signal | DataFrame (MACD, Signal, Hist) |

### `rsi.py`
Relative Strength Index.

| Fungsi | Deskripsi | Input | Output |
| :--- | :--- | :--- | :--- |
| `calculate_rsi(df, period)` | Menghitung nilai RSI (0-100). | DataFrame, Period | Series (RSI Values) |

### `velocity.py`
Kecepatan perubahan harga.

| Fungsi | Deskripsi | Input | Output |
| :--- | :--- | :--- | :--- |
| `calculate_velocity(df, lookback)` | Mengukur laju perubahan harga per candle. | DataFrame, Lookback | Series (Velocity Values) |

### `math_utils.py` (BARU)
Utilitas matematika presisi tinggi (Integer Arithmetic).

| Fungsi | Deskripsi | Input | Output |
| :--- | :--- | :--- | :--- |
| `price_to_int(price)` | Mengubah harga desimal menjadi integer murni dengan menghapus titik desimal. | Float/Decimal (e.g., 79.23) | Tuple `(int_value, scale)` (e.g., 7923, 2) |
| `int_to_price(value, scale)` | Mengembalikan integer ke format harga desimal asli. | Int, Scale | Decimal (e.g., 79.23) |
| `safe_divide(a, b)` | Pembagian aman untuk integer (menghindari div by zero). | Int, Int | Float/Decimal |

---

## 📂 3. Builders & Strategy (`st_lms/builders/`)

Modul pembentuk rencana trading berdasarkan strategi yang dipilih.

### `long_builder.py`
| Fungsi | Deskripsi |
| :--- | :--- |
| `build_long_plan(snapshot)` | Membuat rencana BUY: Menentukan Entry, SL (di bawah support), TP (Resistence). |

### `short_builder.py`
| Fungsi | Deskripsi |
| :--- | :--- |
| `build_short_plan(snapshot)` | Membuat rencana SELL: Menentukan Entry, SL (di atas resistance), TP (Support). |

### `sideway_builder.py`
| Fungsi | Deskripsi |
| :--- | :--- |
| `build_sideway_plan(snapshot)` | Membuat rencana RANGE: Buy di Support bawah, Sell di Resistance atas. |

---

## 📂 4. API Backend (`st_lms/api/superbot_api.py`)

FastAPI server untuk handling request eksternal dan database.

### Endpoints

| Method | Endpoint | Deskripsi | Parameter Utama |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/candles/fetch` | Mengambil data historis dari Binance Futures. | `symbol`, `timeframe`, `start_date`, `end_date` |
| `POST` | `/api/v1/pipeline/run` | Menjalankan pipeline secara manual via API. | `symbol`, `timeframe`, `strategy`, `balance` |
| `GET` | `/api/v1/pipeline/traces` | Mengambil riwayat eksekusi pipeline (C001-C012). | `symbol`, `limit` |
| `GET` | `/api/v1/supertrend/lines` | Daftar semua garis Supertrend yang terdeteksi. | `symbol`, `timeframe`, `active_only` |
| `GET` | `/api/v1/supertrend/points/{line_id}` | Detail titik-titik pembentuk garis Supertrend. | `line_id` |
| `GET` | `/api/v1/river/learning` | Statistik pembelajaran AI (Win rate, patterns). | - |
| `GET` | `/api/v1/darwin/recommendations` | Saran optimasi dari modul Darwin. | - |
| `GET` | `/api/v1/executions` | Riwayat trade (Open/Closed) dengan PnL. | `status`, `symbol` |
| `POST` | `/api/v1/backtest/run` | Menjalankan backtest pada rentang waktu tertentu. | `symbol`, `start_date`, `end_date`, `strategy` |
| `GET` | `/api/v1/dashboard/stats` | Ringkasan statistik untuk dashboard utama. | - |

### Fungsi Internal API
| Fungsi | Deskripsi |
| :--- | :--- |
| `fetch_binance_candles(...)` | Koneksi ke Binance API untuk download data OHLCV. |
| `convert_utc_to_wib(timestamp)` | Helper konversi waktu UTC ke WIB (UTC+7). |
| `price_to_int(...)`, `int_to_price(...)` | Wrapper untuk fungsi matematika presisi tinggi. |

---

## 📂 5. Dashboard Frontend (`st_lms/dashboard/superbot_dashboard.py`)

Streamlit UI untuk visualisasi dan monitoring.

### Halaman (Pages)
1.  **Dashboard Overview**: Ringkasan performa, saldo, open positions.
2.  **Pipeline Traces**: Tabel status C001-C012 per eksekusi (Heatmap).
3.  **Supertrend Lines**: Visualisasi garis trend multi-timeframe.
4.  **Supertrend Points**: Detail koordinat titik pembentuk garis.
5.  **River Learning**: Grafik win-rate, distribution profit/loss.
6.  **Darwin Recommendations**: List saran optimasi parameter.
7.  **Execution Tracks**: Log detail entry/exit setiap trade.
8.  **Run Backtest**: Form untuk menjalankan simulasi masa lalu.
9.  **Run Pipeline**: Form untuk trigger pipeline live/manual.

### Fungsi Utama Dashboard
| Fungsi | Deskripsi |
| :--- | :--- |
| `render_sidebar()` | Input kontrol global (Symbol, Timeframe, Strategy, Date Range). |
| `display_pipeline_trace()` | Visualisasi status 12 stage dengan ikon ✅/❌. |
| `plot_supertrend_chart()` | Plotly chart harga + garis Supertrend + area warna trend. |
| `convert_timestamps_in_df()` | Mengubah kolom waktu di DataFrame dari UTC ke WIB sebelum display. |
| `format_currency()` | Format angka ke format USD mata uang. |

---

## 📂 6. Database & Models (`st_lms/models/` & `db/`)

Struktur data penyimpanan (SQLite).

### Tabel Database
| Tabel | Kolom Utama | Deskripsi |
| :--- | :--- | :--- |
| `pipeline_traces` | `id`, `symbol`, `timeframe`, `strategy`, `c001_observed`...`c012_executed`, `timestamp_wib` | Log hasil setiap stage pipeline. |
| `supertrend_lines` | `id`, `symbol`, `timeframe`, `direction`, `start_time`, `end_time`, `value` | Garis trend yang terbentuk. |
| `supertrend_points` | `id`, `line_id`, `price`, `time`, `sequence` | Titik koordinat pembentuk garis. |
| `executions` | `id`, `position_id`, `symbol`, `type`, `entry_price`, `exit_price`, `pnl`, `status` | Riwayat trade nyata/simulasi. |
| `river_learning` | `pattern_hash`, `win_count`, `loss_count`, `avg_pnl` | Memori pola market. |
| `darwin_recommendations` | `id`, `recommendation_type`, `details`, `confidence`, `created_at` | Saran optimasi sistem. |

---

## 🔄 Alur Data Lengkap (Data Flow)

1.  **User Input** (Dashboard/API): Pilih Symbol (BTCUSDT), Timeframe (H1), Strategi (LONG_ONLY), Tanggal (WIB).
2.  **API Fetch**: `fetch_binance_candles` mengambil data mentah → Disimpan sementara.
3.  **Preprocessing**: `price_to_int` mengubah harga ke integer untuk presisi.
4.  **Pipeline Run**:
    *   **C001-C005**: Observasi & Struktur (Integer Math).
    *   **C006-C008**: Analisis & Klasifikasi (Logic).
    *   **C009**: Builder (Long/Short/Sideway) membuat rencana.
    *   **C010-C011**: Review & Otorisasi.
    *   **C012**: Eksekusi → Simpan ke DB `executions`.
5.  **Postprocessing**: `int_to_price` mengembalikan hasil ke desimal untuk laporan.
6.  **Visualization**: Dashboard menampilkan data dengan waktu WIB dan format currency.

---

## 🛠️ Konstanta & Konfigurasi

*   **Timeframes**: `['1m', '5m', '15m', '1h', '4h', '1d']`
*   **Strategies**: `['LONG_ONLY', 'SHORT_ONLY', 'SIDEWAY_ONLY']`
*   **Timezone**: `UTC+7` (WIB) untuk display, `UTC` untuk storage internal.
*   **Precision**: Integer arithmetic dengan dynamic scale (max 8 desimal).
