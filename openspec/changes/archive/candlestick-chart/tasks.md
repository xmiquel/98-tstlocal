# Tasks: Candlestick Chart

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~260 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: DB Layer — query_ohlc()

- [x] 1.1 Write tests for `query_ohlc()` in `tests/test_market.py`: limit mode (last N bars), date range mode (`datetime.date`), unknown symbol returns `[]`, ascending order, uses `self._conn`
- [x] 1.2 Add `query_ohlc()` to `MarketDatabase` in `app/market.py` — two modes: limit subquery (`ORDER BY datetime DESC LIMIT ?`) and date-range WHERE (`datetime>=? AND datetime<?`)

## Phase 2: API Endpoint — GET /api/ohlc

- [x] 2.1 Write integration tests in `tests/test_chart.py` for `GET /api/ohlc`: basic query 200, 5000 cap, date range, 422 missing symbol, empty `[]` for unknown symbol
- [x] 2.2 Add `GET /api/ohlc` route in `app/main.py` with `min(limit, 5000)` cap, symbol validation, Unix epoch to `datetime.date` conversion

## Phase 3: Chart Page — GET /market/chart

- [x] 3.1 Write integration tests in `tests/test_chart.py` for `GET /market/chart`: 200 HTML, symbol `<select>` with options, chart `<div>`, date `<input>` fields
- [x] 3.2 Create `templates/market/chart.html` extending `base.html` — symbol select, start/end date inputs, chart div, Lightweight Charts CDN script
- [x] 3.3 Create `static/js/chart.js` — fetch `/api/ohlc`, `LightweightCharts.createChart()`, `candlestickSeries.setData()`
- [x] 3.4 Add `GET /market/chart` route in `app/main.py` with inline `SELECT DISTINCT symbol` for template context
- [x] 3.5 Add "Market" nav link to `templates/base.html` (`<a href="/market/chart">Market</a>`)
- [x] 3.6 Add chart container styles (`#chart`, form layout) to `static/css/app.css`

## Phase 4: Verify

- [x] 4.1 Run `uv run pytest -ra --strict-markers --strict-config --cov=app --cov-report=term-missing --cov-fail-under=80`
- [x] 4.2 Run `uv run ruff check . && uv run ruff format --check . && uv run mypy .`
