# Delta for Market Chart

## MODIFIED Requirements

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
