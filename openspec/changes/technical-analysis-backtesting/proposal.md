# Proposal: Technical Analysis & Indicator Overlays

## Intent

Add server-side technical indicator calculation with interactive chart overlays for SMA, EMA, RSI, MACD, and Bollinger Bands. Indicators are computed from OHLCV at query time using pandas-ta-classic + TTLCache — no database persistence. Active indicator configs survive page reloads via localStorage.

## Scope

### In Scope
- Indicator engine (pandas-ta-classic + TTLCache, 5 min TTL)
- REST API: `POST /api/indicators/calculate`, `GET /api/indicators/catalog`
- New APIRouter at `app/routers/indicators.py`
- HTMX partials for add/remove/configure indicators
- JS overlay manager (`chart-indicators.js`) for Lightweight Charts line series
- localStorage persistence for active indicator configs
- Initial 5 indicators: SMA, EMA, RSI, MACD, Bollinger Bands

### Out of Scope
- Full indicator catalog (252+) with search/browse UI
- Multi-timeframe indicator calculation
- Indicator persistence to DuckDB/SQLite
- Backtesting with vectorbt (separate change)
- Alerting, signal notifications, drawing tools

## Capabilities

### New Capabilities
- `technical-indicators`: indicator engine, REST API for calculation/catalog, HTMX panel for add/remove/configure, JS overlay lifecycle management, localStorage persistence.

### Modified Capabilities
- `market-chart`: chart page gains indicator panel and legend area; `chart.js` refactored for overlay hooks; indicator overlays managed by `chart-indicators.js`.
- `trading-domain`: new `query_ohlc_as_df()` method on MarketDatabase returning a pandas DataFrame with OHLCV columns.

## Approach

1. Add deps (`pandas-ta-classic`, TA-Lib optional) to `pyproject.toml`
2. Add `query_ohlc_as_df()` to MarketDatabase in `app/market.py`
3. Create `IndicatorEngine` in `app/indicators.py` with TTLCache
4. Create `app/routers/indicators.py` with calculate + catalog endpoints
5. Register router in `app/main.py`
6. Build HTMX partials in `templates/indicators/`
7. Create `chart-indicators.js` for overlay series lifecycle
8. Refactor `chart.js` to expose overlay hooks
9. Add CSS for indicator panel and legend
10. Integrate indicator panel into `chart.html`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `pyproject.toml` | Modified | Add deps |
| `app/market.py` | Modified | Add `query_ohlc_as_df()` |
| `app/main.py` | Modified | Register indicators router |
| `app/indicators.py` | New | IndicatorEngine + TTLCache |
| `app/routers/indicators.py` | New | Indicator API endpoints |
| `app/schemas.py` | New | Pydantic models |
| `static/js/chart.js` | Modified | Overlay management hooks |
| `static/js/chart-indicators.js` | New | Overlay lifecycle |
| `static/css/app.css` | Modified | Panel/legend styles |
| `templates/market/chart.html` | Modified | Panel + legend containers |
| `templates/indicators/*.html` | New | HTMX partials |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| TTLCache serves stale data on real-time feed | Low | Current data is EOD/historical; real-time is future scope |
| Large OHLCV ranges slow calculation | Low | TTLCache + 5000-bar cap; lightweight initial set |
| TA-Lib unavailable on deploy | Low | pandas-ta-classic is primary path; TA-Lib is optional perf boost |

## Rollback Plan

1. Remove router registration from `app/main.py`
2. Revert `pyproject.toml` deps
3. Delete new files: `app/indicators.py`, `app/routers/indicators.py`, `app/schemas.py`, `static/js/chart-indicators.js`, `templates/indicators/`
4. Revert `chart.js`, `chart.html`, `app/market.py`, `app.css` changes

## Dependencies

- `pandas-ta-classic` >= 0.6.20
- `TA-Lib` >= 0.6.8 (optional, Windows prebuilt wheels)
- `vectorbt` >= 1.0.0 (installed, used in future backtesting change)
- `pandas` >= 2.x
- Existing `MarketDatabase.query_ohlc()` in `app/market.py`

## Success Criteria

- [ ] All 5 indicators render as correct overlays on the candlestick chart
- [ ] Add/remove/configure indicators via HTMX panel works end-to-end
- [ ] Active indicator configs survive page reload (localStorage)
- [ ] TTLCache returns cached results within 5 min TTL
- [ ] Empty symbol returns empty result (no server crash)
- [ ] All existing tests pass; new tests cover engine + API
