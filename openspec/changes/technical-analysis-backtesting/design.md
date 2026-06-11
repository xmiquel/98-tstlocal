# Design: Technical Analysis & Indicator Overlays

## Technical Approach

Server-side indicator engine (`pandas-ta-classic` + `cachetools.TTLCache` 300s) computing SMA, EMA, RSI, MACD, BBANDS from OHLCV at query time. New APIRouter at `app/routers/indicators.py` for `POST /api/indicators/calculate` and `GET /api/indicators/catalog`. Chart page gains HTMX indicator panel; `chart.js` exposes overlay hooks consumed by new `chart-indicators.js`. Active indicator configs survive reload via `localStorage`. No DuckDB persistence — on-demand computation only.

## Architecture Decisions

### Cache Strategy
| Option | Tradeoff | Decision |
|--------|----------|----------|
| **TTLCache 5min** | Simple, in-process, auto-expire | **Chosen** |
| Redis | Distributed — overkill for single-process | Rejected |
| No cache | Recomputes on every hover; wasteful | Rejected |

Keyed by `(symbol, timeframe, indicator, params_hash)`, maxsize 256.

### APIRouter Pattern
| Option | Tradeoff | Decision |
|--------|----------|----------|
| **New APIRouter** | First router in app — establishes pattern | **Chosen** |
| Flat functions | Consistent but mixes concerns | Rejected |

Package `app/routers/__init__.py` + `indicators.py`, registered via `app.include_router()`.

### JS Overlay Management
| Option | Tradeoff | Decision |
|--------|----------|----------|
| **`window.chartApi`** | Minimal refactor, keeps IIFE pattern | **Chosen** |
| ES modules / bundler | Requires build step; current code is vanilla IIFE | Rejected |

`chartApi` surface: `getChart()`, `getSeries()`, `onReload(cb)`, `getCurrentParams()`.

### localStorage Persistence
| Option | Tradeoff | Decision |
|--------|----------|----------|
| **Key `trading:indicators:active`** | Survives reload, zero server state | **Chosen** |
| Server-side DB | Needs user/auth; overkill | Rejected |
| Session only | Lost on reload, bad UX | Rejected |

Format: `[{indicator: "SMA", params: {period: 20}}, ...]`.

## Data Flow

```ascii
Panel "Add SMA" → GET /catalog → static catalog
  → config form partial (HTMX)
  → POST /calculate {symbol, indicator, params}
      ├─ MarketDatabase.query_ohlc_as_df() → pd.DataFrame
      └─ IndicatorEngine.calculate(df, config)
           ├─ TTLCache hit → return cached
           └─ miss → pandas-ta compute → cache
  → HTMX renders row in panel
  → chart-indicators.js: chart.addLineSeries()
  → localStorage.setItem("trading:indicators:active", ...)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Modify | Add `pandas-ta-classic`, `pandas`, `cachetools` |
| `app/indicators.py` | Create | `IndicatorEngine` with TTLCache |
| `app/routers/__init__.py` | Create | Package marker |
| `app/routers/indicators.py` | Create | Calculate + catalog endpoints |
| `app/schemas.py` | Modify | Indicator request/result/catalog schemas |
| `app/market.py` | Modify | Add `query_ohlc_as_df()` |
| `app/main.py` | Modify | Register indicators router |
| `static/js/chart.js` | Modify | Expose `window.chartApi`, reload triggers callbacks |
| `static/js/chart-indicators.js` | Create | Overlay lifecycle (addLineSeries, remove, palette) |
| `static/css/app.css` | Modify | Panel + legend styles |
| `templates/market/chart.html` | Modify | Panel + legend containers |
| `templates/indicators/panel.html` | Create | HTMX panel shell |
| `templates/indicators/config_form.html` | Create | Per-indicator config form |
| `templates/indicators/row.html` | Create | Active indicator row with remove |

## Interfaces / Contracts

```python
class IndicatorParam(BaseModel):
    name: str; type: str  # int|float|select
    default: float | int | str; description: str

class IndicatorCatalogEntry(BaseModel):
    name: str; params: list[IndicatorParam]

class IndicatorRequest(BaseModel):
    symbol: str; timeframe: str = "1m"
    indicator: str; params: dict[str, float|int|str] = {}

class IndicatorValue(BaseModel):
    time: int; value: float

class IndicatorResult(BaseModel):
    label: str; values: list[IndicatorValue]
```

```javascript
// window.chartApi consumed by chart-indicators.js:
//   getChart() → chart instance
//   getSeries() → candlestick series
//   onReload(fn) → post-data-reload callback
//   getCurrentParams() → {symbol, timeframe, start, end, limit}
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | IndicatorEngine all 5 indicators | Pass known df, assert label + values shape |
| Unit | TTLCache hit/miss | Inspect cache internals |
| Unit | query_ohlc_as_df() shape + params | Same fixture pattern as test_market.py |
| Int | POST /calculate end-to-end | TestClient + in-memory DuckDB |
| Int | GET /catalog 5 entries + schema | TestClient |
| E2E | Add indicator → overlay renders | Playwright (fixture exists) |
| E2E | localStorage persistence across reload | Playwright: set, reload, assert restored |
| Int | chart.js reload triggers callbacks | TestClient + HTML parse |

## Migration / Rollout

No migration required. Zero DB schema changes. `query_ohlc()` untouched — `query_ohlc_as_df()` is additive. Chart page gains panel without breaking existing behavior.

## Open Questions

- [ ] TA-Lib optional dep — install by default or skip? Proposal says pandas-ta-classic is primary path.
- [ ] Color palette: 5 predefined hex values or cycle through N? Spec says cycle through predefined palette.
- [ ] Should chart tooltip show indicator values on crosshair? Spec doesn't require it, but worth confirming.
