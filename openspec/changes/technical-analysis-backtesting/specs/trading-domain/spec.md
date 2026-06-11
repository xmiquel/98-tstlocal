# Delta for Trading Domain

## ADDED Requirements

### Requirement: OHLCV Query as DataFrame

The system SHALL implement `MarketDatabase.query_ohlc_as_df()` returning a pandas DataFrame with columns `time`, `open`, `high`, `low`, `close`, `volume` ordered by time ascending. The method SHALL accept the same parameters as `query_ohlc()`: `symbol` (required), `limit` (default 200, max 5000), `start` (optional Unix epoch), `end` (optional Unix epoch), `before` (optional Unix epoch), and `timeframe` (default `"1m"`, reserved). All parameter semantics SHALL match `query_ohlc()` — including the 5000-bar cap, before vs. start/end precedence, and strict less-than for before. The column order SHALL be deterministic. The returned DataFrame SHALL reuse the same `MarketDatabase.conn.execute()` connection — no new connections opened.

#### Scenario: query_ohlc_as_df returns DataFrame for a symbol

- GIVEN dt_ohlc_m1 contains 500 bars for symbol "NDX"
- WHEN `query_ohlc_as_df(symbol="NDX", limit=200)` is called
- THEN the result is a pandas DataFrame with exactly 200 rows
- AND columns are `time`, `open`, `high`, `low`, `close`, `volume` in that order

#### Scenario: Unknown symbol returns empty DataFrame

- GIVEN dt_ohlc_m1 contains no data for symbol "NONEXISTENT"
- WHEN `query_ohlc_as_df(symbol="NONEXISTENT")` is called
- THEN the result is a pandas DataFrame with zero rows
- AND the columns match the expected schema

#### Scenario: DataFrame reuses existing DuckDB connection

- GIVEN `MarketDatabase` is initialized
- WHEN `query_ohlc_as_df()` executes
- THEN it SHALL use `self.conn.execute()` on the existing DuckDB connection
- AND it SHALL NOT open a new connection

#### Scenario: before parameter semantics match query_ohlc

- GIVEN dt_ohlc_m1 contains bars for "NDX" at timestamps 1704067200, 1704068100, and 1704069000
- WHEN `query_ohlc_as_df(symbol="NDX", before=1704068100, limit=5)` is called
- THEN only bars with `time < 1704068100` are returned
- AND the results are ordered by time ascending

## Out of Scope (Non-Requirements)

- Removing or modifying the existing `query_ohlc()` method — it SHALL remain unchanged
- Adding any database write or upsert method for OHLCV data
