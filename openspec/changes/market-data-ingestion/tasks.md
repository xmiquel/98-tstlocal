# Tasks: market-data-ingestion

## Phase 1: Dependencies & Config
- [x] `uv add duckdb~=1.0`
- [x] Update `.gitignore` — add `data/market.duckdb`
- [x] Add `MARKET_DB_PATH` to `app/settings.py`
- [x] Add `MARKET_DB_PATH` to `.env.example`

## Phase 2: Market module
- [x] Create `app/market.py` — `MarketDatabase` class with connect, close, ensure_table
- [x] Table `dt_ohlc_m1` with correct schema
- [x] DuckDB file path from settings

## Phase 3: Ingestion CLI
- [x] Create `app/ingest.py` — `__main__` entry point
- [x] Parse CLI args: CSV path, optional DB path override
- [x] Read CSV with DuckDB `read_csv_auto`
- [x] Parse datetime as `date||' '||time` (no TZ conversion)
- [x] Add `origen` (filename) and `fecha_carga` (start time)
- [x] INSERT into `dt_ohlc_m1`
- [x] Report: filename, row count, duration

## Phase 4: Tests
- [x] Test `MarketDatabase` creates table on connect
- [x] Test ingestion from a minimal CSV fixture
- [x] Test `origen` and `fecha_carga` metadata correctness
- [x] Test datetime parsing (no TZ conversion)
- [x] Test empty CSV handling
- [x] Test settings integration

## Phase 5: Real data load
- [x] Load NDX.csv → DuckDB
- [x] Verify row count matches CSV
- [x] Verify quality: ruff, format, mypy, pytest

**Total**: ~120 lines delta, single PR
