# Delta for Market Chart

## ADDED Requirements

### Requirement: Indicator Selection Panel

The system SHALL render an HTMX-powered indicator panel on the chart page for adding, removing, and configuring indicator overlays. The panel SHALL list active indicators with a remove button per entry and a "Add Indicator" dropdown populated from `GET /api/indicators/catalog`. Selecting an indicator SHALL open a configuration form (via HTMX partial) with fields for each parameter defined in the catalog. On form submission, the system SHALL call `POST /api/indicators/calculate` and return the result as a rendered overlay row. Each row SHALL display the indicator label and a remove button — no inline chart rendering in the panel.

#### Scenario: Add indicator via HTMX partial

- GIVEN the chart page is rendered with an indicator panel
- WHEN the user selects "SMA" from the Add Indicator dropdown
- THEN the panel SHALL load a configuration form for SMA parameters
- AND the form SHALL include a period field with default 20

#### Scenario: Indicator configuration submission triggers calculation

- GIVEN the SMA configuration form is displayed with period=20
- WHEN the user submits the form
- THEN a POST request to `/api/indicators/calculate` is sent with `{"symbol": "NDX", "indicator": "SMA", "params": {"period": 20}}`
- AND the panel SHALL update to show a row with label "SMA(20)" and a remove button

#### Scenario: Remove indicator removes row and overlay

- GIVEN the panel displays an active SMA(20) row
- WHEN the user clicks the remove button for SMA(20)
- THEN the row SHALL be removed from the panel
- AND the corresponding overlay SHALL be removed from the chart

### Requirement: Indicator Overlay Rendering

The system SHALL render active indicator values as Lightweight Charts line series overlays on the candlestick chart. Each indicator SHALL create a new `addLineSeries()` instance with a distinct color. Colors SHALL cycle through a predefined palette. Overlay series SHALL be registered with the chart via a management interface exposed by `chart-indicators.js`. On data reload (symbol change, date range change), the system SHALL preserve all active indicator configs and re-issue calculation requests after the OHLCV data loads.

#### Scenario: Indicator renders as colored line series

- GIVEN the chart displays candlesticks for "NDX" and SMA(20) is active
- WHEN `POST /api/indicators/calculate` returns values
- THEN a new `addLineSeries()` is created on the Lightweight Charts instance
- AND the series SHALL have a distinct color from other active indicators

#### Scenario: Symbol change re-fetches all active indicators

- GIVEN SMA(20) and RSI(14) are active with data for "NDX"
- WHEN the user selects "SPX" from the symbol selector
- THEN after OHLCV data loads for SPX, POST requests for both SMA(20) and RSI(14) are issued
- AND both overlays render on the SPX chart

### Requirement: Indicator Config Persistence

The system SHALL persist active indicator configurations to localStorage under key `trading:indicators:active`. On page load, the system SHALL read this key and restore the saved indicator configs, re-issuing calculation requests automatically. The serialized format SHALL be a JSON array of `{indicator, params}` objects. When the user adds, removes, or modifies a config, the system SHALL update localStorage immediately.

#### Scenario: Indicator configs survive page reload

- GIVEN SMA(20) is active and saved to localStorage
- WHEN the user refreshes the chart page
- THEN the indicator panel SHALL show SMA(20) as active
- AND the chart SHALL render the SMA overlay without manual reconfiguration

#### Scenario: Empty localStorage results in clean panel

- GIVEN localStorage has no `trading:indicators:active` key
- WHEN the chart page loads
- THEN the indicator panel SHALL be empty
- AND no indicator overlays are rendered

## MODIFIED Requirements

### Requirement: Chart Page

The system SHALL serve `GET /market/chart` as an HTML page. The page SHALL include a symbol `<select>` populated from `SELECT DISTINCT symbol FROM dt_ohlc_m1`, optional start and end date `<input>` fields, a chart `<div>` container, and an indicator panel `<div>` container with a legend area for active indicator labels. On page load, JavaScript SHALL fetch `GET /api/ohlc?symbol=<selected>&limit=200` and render the data as a candlestick chart using Lightweight Charts v4 loaded from unpkg CDN. After OHLCV data loads, the page SHALL restore active indicator configs from localStorage and issue calculation requests. `chart.js` SHALL expose overlay management hooks consumed by `chart-indicators.js`. When any chart control (symbol selector, timeframe selector, start date, or end date) changes, JavaScript SHALL automatically fetch and re-render the chart data AND re-fetch all active indicator overlays. A submit button or Load button SHALL NOT be required to trigger data loading. The chart tooltip SHALL reference CSS custom properties for its background, text, and border colors instead of hardcoded values.
(Previously: No indicator panel or legend area; no localStorage restore; chart.js had no overlay hooks; data reload did not preserve indicators)

#### Scenario: Page renders with chart canvas, selector, and indicator panel

- GIVEN dt_ohlc_m1 contains symbols "NDX" and "SPX"
- WHEN a client sends `GET /market/chart`
- THEN the response status is 200
- AND the body contains a `<select>` element, date input fields, a chart `<div>`, and an indicator panel `<div>`

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
- AND then restores active indicator configs from localStorage and issues calculation requests

#### Scenario: Chart controls auto-trigger data and indicator reload

- GIVEN the chart page is rendered with data for symbol "NDX" and SMA(20) active
- WHEN the user selects "SPX" from the symbol dropdown
- THEN the JavaScript SHALL fetch `GET /api/ohlc?symbol=SPX&limit=200`
- AND then re-fetch all active indicators for symbol "SPX"
- AND the chart SHALL re-render with SPX candlesticks and indicator overlays

#### Scenario: Date change auto-triggers chart and indicator reload

- GIVEN SMA(20) is active
- WHEN the user changes the start date input value
- THEN the JavaScript SHALL fetch `/api/ohlc` with the updated start parameter
- AND re-fetch all active indicators with the same date range
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

*(Unchanged from main spec — preserving existing behavior)*

The chart SHALL automatically load more historical data when the user pans or scrolls near the leftmost loaded candlestick bar. The system MUST use Lightweight Charts `chart.timeScale().subscribeVisibleLogicalRangeChange()` combined with `series.barsInLogicalRange()` to detect when the visible range approaches the earliest loaded data. When `barsBefore < 50`, the system SHALL fetch additional bars via `GET /api/ohlc?symbol=<current>&before=<oldest_timestamp>&limit=1000`. The fetched bars MUST be prepended to the accumulated data array and redrawn via `series.setData(allData)`. The visible range MUST be preserved by calling `setVisibleLogicalRange()` after the data update. A `loading` boolean gate SHALL prevent concurrent fetch requests.

#### Scenario: Panning near left edge triggers data fetch

- GIVEN the chart is rendered with 200 bars for symbol "NDX"
- WHEN the user pans left until `barsBefore < 50` in the visible logical range
- THEN a fetch to `GET /api/ohlc?symbol=NDX&before=<oldest_time>&limit=1000` is initiated
- AND the response data is prepended to the existing chart data

#### Scenario: Loading gate prevents concurrent requests

- GIVEN a lazy-load fetch is in progress (`loading = true`)
- WHEN the user continues panning left and triggers another scroll-edge detection
- THEN no additional fetch is initiated

#### Scenario: Prepend does not cause visible position jump

- GIVEN chart data is visible for symbol "NDX"
- WHEN a lazy-load response arrives with prepended bars
- THEN `setVisibleLogicalRange()` restores the logical range to match the pre-fetch viewport
- AND the visible chart area does not jump

#### Scenario: Older bars at boundary are not duplicated

- GIVEN the chart displays bars down to Unix timestamp T
- WHEN a lazy-load fetch returns bars with `time < T` via the `before=T` parameter
- THEN exactly zero bars with `time >= T` are added to the accumulated data
