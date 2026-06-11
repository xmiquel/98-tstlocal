# Tasks: Technical Analysis & Indicator Overlays

## Review Workload Forecast

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

~900-1000 estimated changed lines. Recommended split: 3 chained PRs.

### Suggested Work Units
| Unit | Goal | PR | Base |
|------|------|----|------|
| 1 | Backend: deps, engine, query_ohlc_as_df, API, schemas | PR 1 | main |
| 2 | Frontend: chart refactor, overlays, HTMX, data panel | PR 2 | main |
| 3 | E2E tests + CSS polish | PR 3 | main |

**Chain strategy resolved**: stacked-to-main (each PR merges independently to main).

## Phase 1: Dependencies & Foundation

- [x] 1.1 Add `pandas-ta-classic`, `cachetools` to `pyproject.toml` (TA-Lib optional — skipped to keep install simple)
- [x] 1.2 Test: `query_ohlc_as_df()` returns DataFrame with correct columns/params in `tests/test_market.py`
- [x] 1.3 Add `query_ohlc_as_df()` to `app/market.py` — reuses `self._conn.execute()`, returns pd.DataFrame
- [x] 1.4 Test: `IndicatorEngine.calculate()` all 5 indicators + cache hit/miss in `tests/test_indicators.py`
- [x] 1.5 Create `app/indicators.py` with `IndicatorEngine` + TTLCache (300s TTL)

## Phase 2: API Endpoints

- [x] 2.1 Test: `GET /api/indicators/catalog` returns 5 entries in `tests/test_indicators_api.py`
- [x] 2.2 Test: `POST /api/indicators/calculate` valid/422/empty in `tests/test_indicators_api.py`
- [x] 2.3 Add indicator schemas (`IndicatorParam`, `CatalogEntry`, `IndicatorRequest`, `IndicatorResult`) to `app/schemas.py`
- [x] 2.4 Create `app/routers/__init__.py` + `app/routers/indicators.py` with catalog + calculate
- [x] 2.5 Register router in `app/main.py` via `app.include_router()`

## Phase 3: Frontend

- [x] 3.1 Refactor `static/js/chart.js`: expose `window.chartApi` (getChart, getSeries, onReload, getCurrentParams)
- [x] 3.2 Create `static/js/chart-indicators.js`: overlay lifecycle, color palette (blue/orange/purple/red/green), `subscribeCrosshairMove` data panel
- [x] 3.3 Create HTMX partials: `templates/indicators/panel.html`, `config_form.html`, `row.html`
- [x] 3.4 Update `templates/market/chart.html`: add indicator panel div, data panel div, script includes
- [x] 3.5 Add localStorage `trading:indicators:active` save/restore in chart-indicators.js
- [x] 3.6 Add indicator panel + data panel + legend styles to `static/css/app.css`

## Phase 4: Testing & Verification

- [x] 4.1 E2E test: add SMA(20) → overlay renders (Playwright) in `tests/e2e/test_indicators.py`
- [x] 4.2 E2E test: localStorage config survives page reload in `tests/e2e/test_indicators.py`
- [ ] 4.3 Verify: `uv run pytest`, `uv run mypy --strict`, coverage >= 80%, all green

## Phase 5: Polish

- [x] 5.1 Verify chart tooltip uses CSS variables (data panel follows same pattern)
