# Technical Indicators

## Purpose

Server-side technical indicator calculation using pandas-ta-classic with TTLCache. Indicators are computed from OHLCV at query time — never persisted to DuckDB. The engine exposes a REST API for calculation and catalog listing, plus HTMX partials and a JS overlay manager for Lightweight Charts integration.

## Requirements

### Requirement: Indicator Engine

The system SHALL implement an `IndicatorEngine` class wrapping pandas-ta-classic. The engine SHALL accept a pandas DataFrame with columns `time`, `open`, `high`, `low`, `close`, `volume` and an indicator config (name + parameters) and return a list of time-value pairs per indicator line plus a human-readable label. Results SHALL be cached via TTLCache with a 5-minute TTL, keyed by symbol + timeframe + indicator name + parameter hash. Cache misses SHALL compute and store; hits SHALL return without recomputation.

#### Scenario: SMA calculated from OHLCV DataFrame

- GIVEN a DataFrame with 200 bars for "NDX" and a valid config `{name: "SMA", params: {period: 20}}`
- WHEN `engine.calculate(df, config)` is called
- THEN the result contains `label: "SMA(20)"` and a list of `{time, value}` pairs matching the bar count minus the warmup period

#### Scenario: TTLCache returns cached result within TTL

- GIVEN the same symbol + indicator combo was computed 2 minutes ago
- WHEN `engine.calculate(df, config)` is called again
- THEN pandas-ta-classic SHALL NOT be called (cache hit)
- AND the returned values match the first computation exactly

#### Scenario: TTLCache recomputes after 5 minutes

- GIVEN the same symbol + indicator combo was computed 6 minutes ago
- WHEN `engine.calculate(df, config)` is called
- THEN pandas-ta-classic SHALL be called (cache miss)
- AND fresh values are returned

### Requirement: POST /api/indicators/calculate

The system SHALL expose `POST /api/indicators/calculate` accepting `symbol` (required), `timeframe` (default `"1m"`), `indicator` (required — name string), and `params` (optional — dict of indicator parameters). The endpoint SHALL load OHLCV data via `MarketDatabase.query_ohlc_as_df()`, run the indicator through `IndicatorEngine`, and return a JSON object with `label` (str) and `values` (list of `{time, value}` objects). Unknown indicator names SHALL return 422. Symbols with no data SHALL return an empty values array.

#### Scenario: Valid RSI request returns 200 with values

- GIVEN dt_ohlc_m1 contains 200 bars for "NDX"
- WHEN a client sends `POST /api/indicators/calculate` with `{"symbol": "NDX", "indicator": "RSI", "params": {"period": 14}}`
- THEN the response status is 200
- AND the body contains `"label": "RSI(14)"` and a non-empty `values` array

#### Scenario: Unknown indicator returns 422

- GIVEN the catalog does not contain "INVALID"
- WHEN a client sends `POST /api/indicators/calculate` with `{"symbol": "NDX", "indicator": "INVALID"}`
- THEN the response status is 422
- AND the error message identifies the unknown indicator

#### Scenario: Empty symbol returns empty values

- GIVEN dt_ohlc_m1 has no data for "NONEXISTENT"
- WHEN a client sends `POST /api/indicators/calculate` with `{"symbol": "NONEXISTENT", "indicator": "SMA", "params": {"period": 20}}`
- THEN the response status is 200
- AND `values` is an empty array

### Requirement: GET /api/indicators/catalog

The system SHALL expose `GET /api/indicators/catalog` returning a JSON array of available indicators. Each entry SHALL contain `name` (str) and `params` (list of `{name, type, default, description}`). The initial set SHALL be: SMA, EMA, RSI, MACD, Bollinger Bands. The endpoint SHALL NOT require authentication. The catalog SHALL be defined statically in code — not loaded from a database.

#### Scenario: Catalog returns initial 5 indicators

- GIVEN the application is running
- WHEN a client sends `GET /api/indicators/catalog`
- THEN the response status is 200
- AND the body is an array with exactly 5 entries including "SMA", "EMA", "RSI", "MACD", "BBANDS"

#### Scenario: Each entry defines its parameters

- GIVEN the catalog response
- WHEN inspecting any entry
- THEN each entry SHALL contain `name` and `params`
- AND each param SHALL define `name`, `type`, `default`, and `description`

## Out of Scope (Non-Requirements)

- Full indicator catalog (252+) with search/browse UI
- Multi-timeframe indicator calculation
- Indicator persistence to DuckDB or SQLite
- Real-time indicator updates (streaming)
- Alerting or signal notifications
