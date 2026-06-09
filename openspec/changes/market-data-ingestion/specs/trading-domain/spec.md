# Trading Domain — Market Data Ingestion

## Requirements

### Req-MD-1: Market Data Storage (ADDED)
The system MUST persist OHLCV market data in a DuckDB database for analytical queries and backtesting.

**Scenarios:**

1. **Load NDX.csv into dt_ohlc_m1**
   Given a CSV file at a known path with MT5-format OHLCV data
   When the ingestion script runs with that file path
   Then all rows are inserted into the `dt_ohlc_m1` table with correct types
   And `origen` is set to the CSV filename (e.g., `NDX.csv`)
   And `fecha_carga` is a constant TIMESTAMP across all inserted rows
   And no timezone conversion is applied to the datetime field

2. **Table creation on first run**
   Given no existing DuckDB database
   When the ingestion script runs
   Then the `dt_ohlc_m1` table is created automatically
   And the schema matches: datetime TIMESTAMP, open/high/low/close DOUBLE, tickvol/volume BIGINT, spread INT, origen VARCHAR, fecha_carga TIMESTAMP

3. **Idempotent re-ingestion**
   Given an existing DuckDB with previously loaded data for NDX.csv
   When the ingestion script runs again with the same file
   Then duplicated rows MAY exist (no upsert logic required for v1)

4. **Custom database path**
   Given a `MARKET_DB_PATH` setting
   When the ingestion script runs
   Then the DuckDB file is created at the configured path
   And the path defaults to `data/market.duckdb`

5. **Large file handling**
   Given a 197MB CSV file (NDX.csv, 3.45M rows)
   When the ingestion script runs
   Then it completes in under 30 seconds
   And reports row count and duration
