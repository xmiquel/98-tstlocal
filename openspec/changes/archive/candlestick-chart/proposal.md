# Proposal: Candlestick Chart

## Intent

Add TradingView-like candlestick charting for OHLCV market data stored in DuckDB. The app has no charting — only strategy CRUD. Users need visual price analysis to inform trading decisions.

## Scope

### In Scope
- `MarketDatabase.query_ohlc()` — query by symbol, limit, date range, timeframe
- `GET /api/ohlc` — JSON endpoint (Lightweight Charts format)
- `GET /market/chart` — HTML page with symbol selector, date inputs, chart canvas
- `static/js/chart.js` — plain JS fetcher + Lightweight Charts renderer
- `templates/market/chart.html` — chart page template
- Nav link in `base.html`
- Tests: unit (query_ohlc) + integration (both endpoints)

### Out of Scope
- Lazy loading on drag/pan — future
- Multi-timeframe (5m, 1h, 1d) — future (API param accepted, only `1m` supported)
- Aggregation/resampling logic — future
- Layout presets or workspace persistence — future

## Capabilities

### New Capabilities
- `market-chart`: Frontend for OHLCV candlestick charting — symbol selector, date range UI, Lightweight Charts rendering, `/api/ohlc` JSON endpoint

### Modified Capabilities
- `trading-domain`: Adds OHLCV query requirement — `MarketDatabase.query_ohlc(symbol, limit, start, end, timeframe)` with DuckDB read access pattern

## Approach

Lightweight Charts v4 from unpkg CDN (zero build toolchain). API returns `[{time: unix_seconds, open, high, low, close, volume}]`. Default: last 200 bars. Date range overrides limit. Symbol selector populated from `SELECT DISTINCT symbol FROM dt_ohlc_m1`. Timeframe param accepted for future compat, only `1m` implemented.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/market.py` | Modified | Add `query_ohlc()` method |
| `app/main.py` | Modified | Register `/api/ohlc` + `/market/chart` routes |
| `templates/base.html` | Modified | Add "Market" nav link |
| `templates/market/chart.html` | New | Chart page with symbol selector, date inputs, chart div |
| `static/js/chart.js` | New | Lightweight Charts init, API fetch, setData() |
| `static/css/app.css` | Modified | Chart container sizing |
| `tests/test_market.py` | Modified | Unit tests for query_ohlc |
| `tests/test_chart.py` | New | Integration tests for both chart endpoints |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Naive TIMESTAMP DST ambiguity | Medium | Accept for v1; consistent intraday offset makes charts correct |
| CDN availability | Low | Add local fallback file if needed |
| Empty chart on holidays | Low | Show "No data" state in chart area |

## Rollback Plan

Revert the implementation commit (touches `app/main.py`, `app/market.py`, `templates/`, `static/`). DuckDB data is read-only — no migration needed.

## Dependencies

- Lightweight Charts v4 (unpkg CDN script) — no npm/pip dependency

## Success Criteria

- [ ] `GET /api/ohlc?symbol=NDX&limit=200` returns 200 bars as valid JSON
- [ ] `GET /market/chart` renders an interactive candlestick chart with working symbol selector
- [ ] Tests pass with >= 80% coverage on new/modified code
