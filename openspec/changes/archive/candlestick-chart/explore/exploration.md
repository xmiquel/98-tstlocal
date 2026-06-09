## Exploration: Candlestick Chart

### Current State

The application serves trading strategy CRUD via FastAPI + Jinja2Templates + HTMX v2. Market data (OHLCV) lives in DuckDB (`data/market.duckdb`) under table `dt_ohlc_m1` — **3.4M+ rows per symbol** (NDX, SP500), naive `TIMESTAMP` datetimes ranging from 2011-09 to 2024-04. The `MarketDatabase` class in `app/market.py` currently has **no read/query methods** — only `ingest_csv`, `truncate`, and `close`. No charting capability exists anywhere. The nav in `base.html` has only two links: home (`/`) and strategies (`/strategies`). No JS files are shipped yet (only HTMX v2 from CDN in `base.html` and `app.css` in `/static/css/`).

### Affected Areas

- `app/market.py` — must add a `query_ohlc(symbol, date)` method for DuckDB reads
- `app/main.py` — must register new routes: `GET /market/chart` (HTML) and `GET /api/ohlc` (JSON)
- `templates/base.html` — must add a "Market" nav link
- `templates/market/chart.html` — NEW: chart page template with Lightweight Charts JS
- `static/js/chart.js` — NEW: Lightweight Charts initialization and data fetching
- `static/css/app.css` — minor additions for chart page layout (container sizing)
- `openspec/specs/trading-domain/spec.md` — update if we add OHLC query capability as a domain requirement
- `openspec/specs/frontend/spec.md` — new market-chart requirement to add
- `tests/test_market.py` — add tests for the new `query_ohlc` method
- `tests/test_pages.py` or new `tests/test_chart.py` — add integration tests for chart page routes

### Approaches

1. **Lightweight Charts (TradingView) + No-Build Approach** — Load Lightweight Charts v4 from CDN (`https://unpkg.com/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js`, ~40KB gzipped). JS file as a plain static file. API returns JSON in the format Lightweight Charts expects (`time` as Unix epoch seconds, `open`, `high`, `low`, `close`, `volume`).
   - **Pros**: Zero build toolchain; authentic TradingView visual; proven library (used by TradingView themselves); small CDN footprint; straightforward `createChart()` API
   - **Cons**: Not server-rendered (chart is 100% client JS); date picker must be plain HTML/JS; no React/Svelte integration (irrelevant here — we have no framework)
   - **Effort**: Low (1-2 days: API endpoint, template, JS file, nav update)

2. **ApexCharts or ECharts** — Alternative charting libraries with more built-in features (zoom, pan, tooltips out of the box). ApexCharts has built-in candlestick support but looks generic. ECharts is powerful but ~1MB gzipped.
   - **Pros**: More features out of the box; no need to configure crosshair/tooltip manually; ECharts has built-in data zoom
   - **Cons**: Heavier bundle; **looks NOTHING like TradingView** (the stated user desire); ECharts is overkill for one chart type; both add visual inconsistency with the TradingView-like goal
   - **Effort**: Low (same effort, different CDN)

3. **Server-Side SVG Chart** — Render candlesticks server-side as SVG/Canvas via a Python library (mplfinance, plotly).
   - **Pros**: Zero JS dependency on the client; works without JS
   - **Cons**: No interactivity (zoom, pan, crosshair) without re-rendering the whole page; banding/aliasing on SVG for thousands of candles; fundamentally not "TradingView-like"
   - **Effort**: Medium (server-side rendering, image streaming or embedded SVG, full-page reload for date changes)

### Recommendation

**Use Lightweight Charts by TradingView (Approach 1)**.

It matches the explicit "TradingView-like" requirement perfectly, requires zero build toolchain (just a `<script>` tag), and is designed specifically for financial time-series visualization. The library is ~40KB gzipped — smaller than most alternatives — and produces visuals that are indistinguishable from TradingView's actual product, which is exactly the user's goal.

The API design should be:

- `GET /market` — market data landing page (future: symbol selector, link to chart)
- `GET /market/chart?symbol=NDX&date=2023-12-15` — chart page with date picker and Lightweight Charts canvas
- `GET /api/ohlc?symbol=NDX&date=2023-12-15` — JSON endpoint returning `[{time: <unix_seconds>, open, high, low, close, volume}, ...]`

The date picker should be a plain `<input type="date">` + button. On click, re-fetch `/api/ohlc` and call `series.setData()`. No HTMX needed for chart data — the chart is fully JS-rendered.

MarketDatabase must gain a `query_ohlc` method using:
```sql
SELECT datetime, open, high, low, close, volume
FROM dt_ohlc_m1
WHERE symbol = ? AND datetime >= ? AND datetime < ?
ORDER BY datetime
```

The naive `TIMESTAMP` issue is manageable: DuckDB returns naive Python `datetime` objects. Convert to Unix epoch seconds via `int(dt.timestamp())`. The one caveat is DST — the naive timestamps behave as local time when calling `.timestamp()`. Since MT5 data is typically in broker local time (not UTC), and chart rendering is visual against the time axis, this is acceptable for the initial version. A note should be added to `AGENTS.md` for future TZ handling.

### Risks

- **Timezone Ambiguity**: `datetime` column is naive TIMESTAMP. `datetime.timestamp()` treats naive datetimes as local time. If the data is from MT5 which typically uses UTC+2/UTC+3 (broker server time), the time axis could shift when DST changes. Mitigation: Use `datetime.utcfromtimestamp()` equivalent or store TZ-aware datetimes. For now, the chart renders correctly within a single day filter because the offset is consistent intraday. A future change should add a `check_timezone()` utility and document the MT5 server-time assumption.
- **Date format for `input[type=date]`**: HTML date inputs expect `YYYY-MM-DD` format. Jinja2 defaults to ISO strings which match this. The query parameter on the API must parse `datetime.date.fromisoformat(date_str)`.
- **Single-day filter may show gaps**: If the market is closed for a holiday, the chart will show an empty day (no candles). The user should see a clear "No data" state rather than a blank chart.
- **Lightweight Charts CDN availability**: If unpkg.com is down, the chart won't load. Mitigation: Consider a `static/js/` local fallback or a `<script>` integrity check.
- **No query methods on MarketDatabase yet**: The class only ingests. Adding `query_ohlc` is straightforward but needs test coverage.
- **Large initial data for symbols with trades outside regular hours**: NDX has some data at 00:53 (from the sample). The chart will show pre-market candles. This is likely desired behavior.
- **Performance**: 1440 candles is well within Lightweight Charts' capability (it handles 10,000+ smoothly).

### Ready for Proposal

**Yes** — the exploration is conclusive. The path is clear:

1. Lightweight Charts from CDN (no build toolchain)
2. `GET /api/ohlc` JSON endpoint → DuckDB query → epoch-seconds conversion
3. `GET /market/chart` HTML page with date picker + static JS
4. Add nav link to `base.html`
5. Add `query_ohlc(symbol, date)` to `MarketDatabase`
6. Tests: unit test for `query_ohlc`, integration test for both endpoints

The orchestrator should proceed to `sdd-propose` to formalize scope, or to `sdd-spec` if the scope is already clear from this analysis.
