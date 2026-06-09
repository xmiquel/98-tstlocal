# Delta for Trading Domain

## ADDED Requirements

### Requirement: OHLCV Query

The system SHALL implement `MarketDatabase.query_ohlc()` to query candlestick data from the DuckDB `dt_ohlc_m1` table. The method SHALL accept parameters: `symbol` (str, required), `limit` (int, default 200), `start` (Optional[int], Unix epoch seconds), `end` (Optional[int], Unix epoch seconds), and `timeframe` (str, default `"1m"`, reserved for future). Queries SHALL be read-only — no INSERT/UPDATE/DELETE on market data. The returned list SHALL be ordered by time ascending, with a hard cap of 5000 bars. The DuckDB connection SHALL reuse the existing `MarketDatabase.conn` instance (read pattern: `conn.execute(sql, params).fetchall()`).

#### Scenario: query_ohlc returns last N bars for a symbol

- GIVEN dt_ohlc_m1 contains 500 bars for symbol "NDX"
- WHEN `query_ohlc(symbol="NDX", limit=200)` is called
- THEN the result is a list of 200 OHLCV records ordered by time ascending
- AND each record contains `time`, `open`, `high`, `low`, `close`, `volume`

#### Scenario: query_ohlc with date range filters correctly

- GIVEN dt_ohlc_m1 contains bars for "NDX" on 2024-01-01 and 2024-01-02
- WHEN `query_ohlc(symbol="NDX", start=1704067200, end=1704153600)` is called
- THEN only bars with time between those Unix seconds are returned

#### Scenario: query_ohlc caps at 5000 bars

- GIVEN dt_ohlc_m1 contains 10000 bars for symbol "NDX"
- WHEN `query_ohlc(symbol="NDX", limit=99999)` is called
- THEN the returned list has at most 5000 records

#### Scenario: query_ohlc with unknown symbol returns empty list

- GIVEN dt_ohlc_m1 contains no data for symbol "NONEXISTENT"
- WHEN `query_ohlc(symbol="NONEXISTENT")` is called
- THEN the result is an empty list

#### Scenario: Query reuses MarketDatabase DuckDB connection

- GIVEN `MarketDatabase` is initialized
- WHEN `query_ohlc()` executes
- THEN it SHALL use `self.conn.execute()` on the existing DuckDB connection
- AND it SHALL NOT open a new connection
