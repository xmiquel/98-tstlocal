# Delta for Market Chart

## ADDED Requirements

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
