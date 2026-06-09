# Market Chart

## Purpose

OHLCV candlestick charting for market data stored in DuckDB. Delivers a pure-HTML chart page with symbol selector, date range inputs, and Lightweight Charts v4 rendering — all served server-side with zero build toolchain.

## Requirements

### Requirement: OHLCV Data API

The system SHALL expose `GET /api/ohlc` returning a JSON array of OHLCV bars. The endpoint SHALL accept `symbol` (required), `limit` (default 200, max 5000), `start` (optional Unix epoch seconds), `end` (optional Unix epoch seconds), and `timeframe` (reserved, default `"1m"`, only `1m` implemented). If `start` and `end` are provided, they filter by time range; if omitted, the last `limit` bars are returned. Limits above 5000 SHALL be silently capped to 5000.

#### Scenario: Basic query returns last 200 bars

- GIVEN dt_ohlc_m1 contains 500 bars for symbol "NDX"
- WHEN a client sends `GET /api/ohlc?symbol=NDX`
- THEN the response status is 200
- AND the JSON body is an array of at most 200 objects with keys `time`, `open`, `high`, `low`, `close`, `volume`

#### Scenario: limit parameter is capped at 5000

- GIVEN dt_ohlc_m1 contains 10000 bars for symbol "NDX"
- WHEN a client sends `GET /api/ohlc?symbol=NDX&limit=99999`
- THEN the response array contains at most 5000 bars
- AND no error is raised

#### Scenario: Date range overrides limit

- GIVEN dt_ohlc_m1 contains bars for symbol "NDX" on 2024-01-01 only
- WHEN a client sends `GET /api/ohlc?symbol=NDX&start=1704067200&end=1704153600`
- THEN all returned bars SHALL have time within that range

#### Scenario: Missing symbol returns 422

- GIVEN the application is running
- WHEN a client sends `GET /api/ohlc` without the symbol parameter
- THEN the response status is 422

#### Scenario: Unknown symbol returns empty array

- GIVEN dt_ohlc_m1 contains no data for symbol "NONEXISTENT"
- WHEN a client sends `GET /api/ohlc?symbol=NONEXISTENT`
- THEN the response status is 200
- AND the JSON body is `[]`

### Requirement: Chart Page

The system SHALL serve `GET /market/chart` as an HTML page. The page SHALL include a symbol `<select>` populated from `SELECT DISTINCT symbol FROM dt_ohlc_m1`, optional start and end date `<input>` fields, and a chart `<div>` container. On page load, JavaScript SHALL fetch `GET /api/ohlc?symbol=<selected>&limit=200` and render the data as a candlestick chart using Lightweight Charts v4 loaded from unpkg CDN.

#### Scenario: Page renders with chart canvas and selector

- GIVEN dt_ohlc_m1 contains symbols "NDX" and "SPX"
- WHEN a client sends `GET /market/chart`
- THEN the response status is 200
- AND `Content-Type` includes `text/html`
- AND the body contains a `<select>` element, date input fields, and a `<div>` for the chart

#### Scenario: Symbol selector lists distinct symbols

- GIVEN dt_ohlc_m1 contains symbols "NDX" and "SPX"
- WHEN a client sends `GET /market/chart`
- THEN the `<select>` element contains `<option>` elements for "NDX" and "SPX"
- AND no duplicate options are present

#### Scenario: Chart JS loads from the API on init

- GIVEN the application is running
- WHEN a client navigates to `/market/chart`
- THEN the page's JavaScript sends `GET /api/ohlc?symbol=<first-option>&limit=200` on page load
- AND calls `setData()` on the Lightweight Charts instance with the response

## Out of Scope (Non-Requirements)

- Lazy loading on drag/pan
- Multi-timeframe aggregation (5m, 1h, 1d)
- Layout persistence or workspace presets
