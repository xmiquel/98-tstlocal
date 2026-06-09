# Design: market-data-ingestion

## Architecture decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | DuckDB file at `data/market.duckdb` | Embedded, columnar, no container needed; gitignored |
| 2 | `dt_ohlc_m1` table with TIMESTAMP + OHLCV + metadata | Matches user's expected schema; TIMESTAMP for range queries |
| 3 | `app/market.py` — `MarketDatabase` class | DuckDB connection management (connect, close, table creation) |
| 4 | `app/ingest.py` — `__main__` CLI | Standalone script: `uv run python -m app.ingest <csv_path>` |
| 5 | DuckDB native read_csv_auto | Fastest ingestion; parallel by default |
| 6 | `date||' '||time` direct concat | NO timezone conversion; store exactly what's in the CSV |
| 7 | `fecha_carga` = fixed TIMESTAMP per run | Same value for all rows in one load invocation |
| 8 | `MARKET_DB_PATH` setting | Configurable via `.env`; default `data/market.duckdb` |

## Table schema

```sql
CREATE TABLE IF NOT EXISTS dt_ohlc_m1 (
    datetime    TIMESTAMP,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    tickvol     BIGINT,
    volume      BIGINT,
    spread      INT,
    origen      VARCHAR,
    fecha_carga TIMESTAMP
);
```

## File changes

| File | Action |
|------|--------|
| `app/settings.py` | Add `MARKET_DB_PATH: str = "data/market.duckdb"` |
| `app/market.py` | New — DuckDB connection + table creation |
| `app/ingest.py` | New — CLI entry point for CSV loading |
| `pyproject.toml` | Add `duckdb~=1.0` |
| `.gitignore` | Add `data/market.duckdb` |
| `.env.example` | Add `MARKET_DB_PATH` |

## Ingestion Flow

```
CSV file → DuckDB read_csv_auto → parse datetime → add origen/fecha_carga → INSERT INTO dt_ohlc_m1
```

CLI:
```
uv run python -m app.ingest D:\repos\Quantdle_Data\ML_Data\CSV\NDX.csv
```

Output:
```
Loaded NDX.csv: 3,458,386 rows in 2.3s → dt_ohlc_m1
```
