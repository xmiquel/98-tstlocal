# Change Proposal: market-data-ingestion

## Intent
Load OHLCV market data from MT5-format CSV files into a DuckDB database for backtesting and analysis.

## Problem
The project needs market data (OHLCV) for trading strategy backtesting. Data exists as CSV files (~15GB total, 42 instruments) in MT5 export format. No ingestion or query path exists.

## Solution
Use DuckDB as the market data store — embedded, columnar, no server dependency, fast analytical queries.

### Key decisions
- **Store**: `data/market.duckdb` (gitignored, outside repo)
- **Table**: `dt_ohlc_m1` with OHLCV fields + metadata (origen, fecha_carga)
- **Ingestion**: Python CLI via `uv run python -m app.ingest NDX.csv`
- **Parse**: Direct concatenation of `date||' '||time` — NO timezone conversion
- **Load**: DuckDB native CSV reader (fastest path)
- **Config**: `MARKET_DB_PATH` in `app/settings.py`

### Scope
- **In**: DuckDB dep, market module, ingestion CLI, NDX.csv load
- **Out**: Query API, backtesting engine, web UI for market data, incremental loads

### CSVs available (42 total)
NDX.csv (197MB), SP500.csv, EURUSD.csv (471MB), XAUUSD.csv, and 38 more — all same MT5 format: date,time,open,high,low,close,tickvol,volume,spread
