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

The system SHALL serve `GET /market/chart` as an HTML page. The page SHALL include a symbol `<select>` populated from `SELECT DISTINCT symbol FROM dt_ohlc_m1`, optional start and end date `<input>` fields, and a chart `<div>` container. On page load, JavaScript SHALL fetch `GET /api/ohlc?symbol=<selected>&limit=200` and render the data as a candlestick chart using Lightweight Charts v4 loaded from unpkg CDN. When any chart control (symbol selector, timeframe selector, start date, or end date) changes, JavaScript SHALL automatically fetch and re-render the chart data. A submit button or Load button SHALL NOT be required to trigger data loading. The chart tooltip SHALL reference CSS custom properties for its background, text, and border colors instead of hardcoded values.
(Previously: Data loading triggered by form submit button; no auto-load on control change)

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

#### Scenario: Chart controls auto-trigger data loading

- GIVEN the chart page is rendered with data for symbol "NDX"
- WHEN the user selects "SPX" from the symbol dropdown
- THEN the JavaScript SHALL fetch `GET /api/ohlc?symbol=SPX&limit=200`
- AND the chart SHALL re-render with SPX data

#### Scenario: Date change auto-triggers chart reload

- GIVEN the chart page is rendered
- WHEN the user changes the start date input value
- THEN the JavaScript SHALL fetch `/api/ohlc` with the updated start parameter
- AND the chart SHALL re-render

#### Scenario: Load button is absent from the page

- GIVEN the application is running
- WHEN a client receives `GET /market/chart`
- THEN the response body SHALL NOT contain a `<button>` element with text "Load"

#### Scenario: Chart tooltip adapts to theme via CSS variables

- GIVEN the chart page is rendered
- WHEN the page is in light mode
- THEN the chart tooltip background and text use light-appropriate CSS variable values
- WHEN the theme switches to dark mode
- THEN the chart tooltip colors update to dark-appropriate values without JavaScript changes

### Requirement: Infinite Scroll Loading

The chart SHALL automatically load more historical data when the user pans or scrolls near the leftmost loaded candlestick bar. The system MUST use Lightweight Charts `chart.timeScale().subscribeVisibleLogicalRangeChange()` combined with `series.barsInLogicalRange()` to detect when the visible range approaches the earliest loaded data. When `barsBefore < 50` (fewer than 50 bars exist before the visible range), the system SHALL fetch additional bars via `GET /api/ohlc?symbol=<current>&before=<oldest_timestamp>&limit=1000`. The fetched bars MUST be prepended to the accumulated data array and redrawn via `series.setData(allData)`. The visible range MUST be preserved by calling `setVisibleLogicalRange()` after the data update to prevent visual position jumps. A `loading` boolean gate SHALL prevent concurrent fetch requests — if a fetch is in progress, subsequent scroll-triggered attempts SHALL be silently ignored.

#### Scenario: Panning near left edge triggers data fetch

- GIVEN the chart is rendered with 200 bars for symbol "NDX"
- WHEN the user pans left until `barsBefore < 50` in the visible logical range
- THEN a fetch to `GET /api/ohlc?symbol=NDX&before=<oldest_time>&limit=1000` is initiated
- AND the response data is prepended to the existing chart data

#### Scenario: Loading gate prevents concurrent requests

- GIVEN a lazy-load fetch is in progress (`loading = true`)
- WHEN the user continues panning left and triggers another scroll-edge detection
- THEN no additional fetch is initiated
- AND only the in-flight response is processed when it arrives

#### Scenario: Prepend does not cause visible position jump

- GIVEN chart data is visible for symbol "NDX"
- WHEN a lazy-load response arrives with prepended bars
- THEN `setVisibleLogicalRange()` restores the logical range to match the pre-fetch viewport
- AND the visible chart area does not jump to a different time position

#### Scenario: Older bars at boundary are not duplicated

- GIVEN the chart displays bars down to Unix timestamp T
- WHEN a lazy-load fetch returns bars with `time < T` via the `before=T` parameter
- THEN exactly zero bars with `time >= T` are added to the accumulated data
- AND the oldest bar timestamp before the fetch is unchanged

## Out of Scope (Non-Requirements)

- Multi-timeframe aggregation (5m, 1h, 1d)
- Layout persistence or workspace presets
