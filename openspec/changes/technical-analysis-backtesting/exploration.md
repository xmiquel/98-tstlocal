## Exploration: Technical Indicators + Backtesting Preparation

### Current State

**1. Chart Data Pipeline**

OHLCV data flows through a clean three-layer chain:

```
DuckDB (dt_ohlc_m1)
  → MarketDatabase.query_ohlc() in app/market.py
    → GET /api/ohlc in app/main.py (FastAPI)
      → JSON response [{time, open, high, low, close, tickvol, spread}, ...]
        → chart.js fetch() → series.setData(allData)
          → Lightweight Charts v4 (CDN from unpkg)
```

Key details:
- `MarketDatabase._row_to_dict()` returns `time` (Unix seconds int), `open`, `high`, `low`, `close`, `tickvol`, `spread` — no raw `volume` or `origen`/`fecha_carga` metadata
- Three query modes: raw 1m, aggregated via `time_bucket()` (5m–1d), and before-cursor pagination for infinite scroll
- The chart loads URL parameters from `window.__chartConfig` (set in Jinja template)

**2. Existing API Structure**

- Routes are flat module-level functions on `app.main.app` — no `APIRouter` usage yet
- `MarketDatabase` in `app/market.py` manages DuckDB: connection, table creation (on connect), CSV ingestion, and OHLCV queries
- `app/settings.py` has `MARKET_DB_PATH = "data/market.duckdb"` — a 467MB file on disk
- Two data stores: DuckDB (`app/market.py`) for market data, SQLite (`app/store.py`) for strategies
- No indicator calculation, no pandas/numpy, no caching layer exists yet

**3. Chart JS Code (`static/js/chart.js`)**

- IIFE pattern with `"use strict"`
- Single `series` on the chart (candlestick) — no line or baseline series exist
- Custom tooltip via `subscribeCrosshairMove` — looks up `allData` array by time match, formats OHLCV+spread
- `allData` array is the single source of truth for the chart + tooltip
- `loadData()` has two modes:
  - **Initial/reload**: `series.setData(allData)` with `chart.timeScale().fitContent()`
  - **Prepend**: data concat + range restoration for infinite scroll
- Form controls trigger `change` event → `reloadFromForm()` reads DOM values → new fetch
- `reloadFromForm()` does NOT preserve indicator overlays — a full reload kills any added series
- The chart instance and `series` are local to the IIFE, not exposed globally

**4. Data Model (DuckDB)**

`dt_ohlc_m1` schema:
```sql
datetime    TIMESTAMP,
symbol      VARCHAR,
open        DOUBLE,
high        DOUBLE,
low         DOUBLE,
close       DOUBLE,
tickvol     BIGINT,
volume      BIGINT,
spread      INT,
origen      VARCHAR,
fecha_carga TIMESTAMP
```

The API response drops `volume`, `origen`, `fecha_carga` — only returns `time`, `open`, `high`, `low`, `close`, `tickvol`, `spread`.

**5. Template Structure**

- `base.html`: Nav with links (Home, Strategies, Market), HTMX v2 CDN, theme toggle JS, `{{ content }}` block
- `market/chart.html`: Extends `base.html`
  - `#chart-controls` form: symbol `<select>`, date inputs, timeframe `<select>`, hidden limit
  - `#chart` div (position: relative, 100% × 500px) with `#chart-tooltip` inside
  - Lightweight Charts v4.2.1 from unpkg
  - `window.__chartConfig` JSON inline
  - `chart.js` loaded last
- No indicators panel exists — the chart page has space for one (below the controls or beside the chart)

**6. Frontend Stack**

- **HTMX v2** is used in `base.html` via CDN (`https://unpkg.com/htmx.org@2`)
- Used for strategy CRUD views: table partial swaps, form submissions (`hx-*` attributes)
- **NOT used** for the chart page — chart.js is vanilla JS with `fetch()` + DOM event listeners
- HTMX **is viable** for indicator control panel: add/remove indicators via `hx-post`/`hx-delete`, swap a config form partial, etc.
- Chart overlay management (adding/removing Lightweight Charts series) **must be JS** — HTMX cannot manage chart series lifecycle

**7. Current Dependencies (`pyproject.toml`)**

```toml
dependencies = [
    "duckdb~=1.0",
    "fastapi~=0.116",
    "httpx2~=2.2",
    "jinja2>=3.1.6",
    "pydantic-settings>=2.7",
    "python-multipart~=0.0",
    "sqlalchemy~=2.0",
    "uvicorn>=0.34",
]
```

No pandas, numpy, TA-Lib, pandas-ta, vectorbt, or any data science dependency yet.

---

### Affected Areas

| File | Why Affected |
|------|-------------|
| `pyproject.toml` | Add `pandas-ta-classic`, `TA-Lib` (optional), `vectorbt`, `pandas`, `numpy` deps |
| `app/main.py` | Add new `/api/indicators` route(s) for calculating indicators |
| `app/market.py` | May need `query_ohlc_raw_as_df()` returning a pandas DataFrame for indicator input |
| `app/indicators.py` | **New** — Indicator engine with pandas-ta wrapper + LRU cache |
| `app/schemas.py` | Add Pydantic models for indicator config requests/responses |
| `static/js/chart.js` | Major refactor: manage multiple series (candlestick + N line series), indicator overlay lifecycle, preserve overlays across reloads |
| `static/css/app.css` | Add styles for indicator panel, indicator line legend/color picker |
| `templates/market/chart.html` | Add indicator control panel (HTMX or JS) + indicator legend area |
| `templates/indicators/` | **New** — HTMX partials for indicator add form, config form, indicator list |
| `openspec/specs/market-chart/spec.md` | Update spec to cover indicator overlay requirements |
| `tests/test_indicators.py` | **New** — tests for indicator engine |
| `tests/test_chart.py` | Update for new indicator API endpoint tests |

---

### Approaches

#### 1. **Server-side pandas-ta engine + HTMX control panel + JS overlay manager** (Recommended)

- **Backend**: `app/indicators.py` wraps `pandas-ta-classic` functions with an LRU cache (`functools.lru_cache` or `cachetools.TTLCache`). New `MarketDatabase.query_ohlc_as_df()` returns a pandas DataFrame. New `GET /api/indicators` and `POST /api/indicators/calculate` endpoints.
- **Frontend controls**: Indicator panel rendered via HTMX partials — add button opens a form (symbol, indicator name, params), submits via `hx-post`, response swaps the indicator list partial. Remove via `hx-delete`.
- **Frontend overlays**: chart.js extension (`chart-indicators.js`) manages a registry of `{id, indicator, params, series}`. When indicator data arrives from API, it creates/updates the corresponding `addLineSeries()`, `addBaselineSeries()`, or `addHistogramSeries()`. On chart reload (form change), it re-fetches indicators with the new symbol/timeframe.
- **Pros**: Clean separation of concerns; HTMX works naturally for CRUD-like panel interactions; server-side caching avoids re-calculating for every scroll event; pandas-ta has 200+ indicators without custom math
- **Cons**: Network round-trip for indicator calculation (vs client-side); need to manage series lifecycle carefully on reload; LRU cache invalidation needs thought
- **Effort**: **Medium** (new module + API + JS extension + templates)

#### 2. **Server-side engine + full JS panel + JS overlay manager**

- **Backend**: Same as approach 1
- **Frontend controls**: Pure vanilla JS panel — no HTMX. State managed in a JS object or module, DOM rendered by JS.
- **Frontend overlays**: Same as approach 1
- **Pros**: More control over state; panel state survives chart reload (pure JS); no HTMX dependency in chart area
- **Cons**: More JS code (form validation, DOM manipulation, state sync) when HTMX already handles this well; inconsistent with the rest of the app (HTMX is the established pattern)
- **Effort**: **Medium-High** (more JS work, less reuse of existing patterns)

#### 3. **Client-side TA-Lib via WASM + JS panel**

- **Frontend**: Compile TA-Lib to WASM and run indicator calculations in-browser
- **Backend**: Only serves OHLCV data, no indicator endpoints
- **Frontend panels/overlays**: Same as approach 2
- **Pros**: Zero server load for indicators; instant calculation (no network); works offline
- **Cons**: TA-Lib WASM build is complex (not officially maintained); limited to TA-Lib indicators (no pandas-ta extras); 467MB of OHLCV data needs to go to the browser; huge build complexity vs value
- **Effort**: **Very High** (WASM compilation, JS integration, no existing patterns in project)

---

### Recommendation

**Approach 1 — Server-side pandas-ta engine + HTMX control panel + JS overlay manager.**

Rationale:
1. **Consistent with project patterns**: HTMX already established for CRUD-like interactions. The indicator panel is fundamentally CRUD: list (GET), add (POST), configure, delete.
2. **Server-side calculation is the right default**: The DuckDB data lives server-side (467MB). Sending all OHLCV to the browser for each indicator calculation is wasteful. LRU cache keeps hot indicators fast.
3. **pandas-ta-classic over TA-Lib**: pandas-ta-classic wraps TA-Lib optionally (falls back to numba/vectorized numpy). Zero C compilation, pure Python. Install `ta-lib` binaries if available, but not required.
4. **vectorbt stays installed but unused**: Add it to `pyproject.toml` now (as a dependency), but the indicator engine for phase 1 uses pandas-ta. vectorbt is for the future backtesting phase.
5. **JS overlay management is unavoidable**: Lightweight Charts series must be created/managed via JS — HTMX cannot do this. The overlay manager should be a separate module (`chart-indicators.js`) that chart.js delegates to.

**Implementation outline**:

| Step | What | Where |
|------|------|-------|
| 1 | Add deps: `pandas`, `numpy`, `pandas-ta-classic`, `TA-Lib` (optional), `vectorbt` | `pyproject.toml` |
| 2 | Add `query_ohlc_as_df()` to MarketDatabase | `app/market.py` |
| 3 | Create `IndicatorEngine` with LRU cache + pandas-ta wrapper | `app/indicators.py` |
| 4 | Add Pydantic models: `IndicatorConfig`, `IndicatorResult` | `app/schemas.py` |
| 5 | Add API endpoints: `POST /api/indicators/calculate`, `GET /api/indicators` | `app/main.py` (or `app/routers/indicators.py`) |
| 6 | Create indicator panel HTML partials | `templates/indicators/` |
| 7 | Extend chart.html: add indicator panel container + legend area | `templates/market/chart.html` |
| 8 | Create `static/js/chart-indicators.js`: manages overlay series lifecycle | `static/js/` |
| 9 | Modify `chart.js` to delegate overlay management and preserve on reload | `static/js/chart.js` |
| 10 | Add CSS for indicator panel + legend | `static/css/app.css` |

---

### Risks

- **LRU cache staleness**: If new OHLCV data is ingested (market updates), cached indicator values become stale. Solution: time-based TTL on cache, or version-key by last data timestamp.
- **Series lifecycle on scroll/change**: When chart reloads (e.g., user changes timeframe), all indicator series must be removed and re-created. If the indicator manager doesn't clean up properly, memory leaks or phantom lines appear. Mitigation: clear registry before re-fetch.
- **pandas-ta-classic API stability**: The `pandas-ta-classic` fork has a known API. Verify `pandas_ta.indicators` module structure works with the calculation patterns planned.
- **vectorbt dependency weight**: vectorbt pulls in many numeric deps (numba, etc.). Adding it now may increase install time. Acceptable since it won't be imported until the backtesting phase.
- **HTMX + JS state conflict**: HTMX swaps can destroy JS-managed DOM state. The indicator list partial must be designed so HTMX swaps do NOT touch the chart container. Use scoped swap targets (`hx-target="#indicator-list"` not `#chart`).
- **TA-Lib optional dependency**: If TA-Lib binaries are not installed, pandas-ta-classic may fall back to slower numpy implementations for some indicators. Document this clearly.

---

### Ready for Proposal

**Yes.** The exploration is thorough enough to proceed to the proposal phase. The orchestrator should tell the user:

> The exploration reveals a clean codebase with well-established patterns (HTMX for CRUD, FastAPI flat routes, DuckDB market data, Lightweight Charts candles). The recommended approach is:
> 1. Server-side pandas-ta-classic engine with LRU cache
> 2. HTMX indicator control panel (consistent with existing patterns)
> 3. JS overlay manager for Lightweight Charts (unavoidable — HTMX can't manage chart series)
> 4. vectorbt added as a dependency but not used until the backtesting change
>
> The main architectural decision points for the proposal are:
> - Whether to use `APIRouter` for new indicator endpoints (recommended for organization)
> - Cache TTL strategy (time-based vs data-version-based)
> - Whether indicator configs persist to DuckDB or are in-memory only (user said "no persist" — confirm in proposal)

