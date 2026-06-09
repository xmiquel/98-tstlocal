# Design: Candlestick Chart

## Technical Approach

Two-route architecture: a JSON API endpoint (`/api/ohlc`) and an HTML page (`/market/chart`) that uses Lightweight Charts v4 from unpkg CDN — zero build toolchain. The API delegates to a new `MarketDatabase.query_ohlc()` that queries DuckDB `dt_ohlc_m1`. Symbol list is populated inline at page render via a separate `SELECT DISTINCT` query. 5000-bar cap enforced in the API route, not the DB layer.

## Architecture Decisions

### Decision: Two separate routes (API + HTML) vs content negotiation

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Single route with `Accept` header dispatch | Fewer routes, but mixes API and HTML concerns; strategy code already does this for HTMX, but the chart page has distinct JS lifecycle | **Two routes** — `/api/ohlc` returns JSON, `/market/chart` returns HTML. Clear separation, simpler testing, and the JS can `fetch()` the API directly without header hacks |
| Content negotiation on `/market/chart` | One URL for both | Rejected — the JS needs a dedicated JSON endpoint for `fetch()`, and the HTML page needs separate template rendering |

### Decision: 5000 cap in API route, not DB layer

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Cap in query_ohlc() | DB method always safe, but couples DB layer to HTTP semantics | **Cap in route** — `query_ohlc()` accepts `limit` and returns what's asked; the route does `min(limit, 5000)` before passing it. Keeps the DB method general-purpose |
| Cap in DB layer | Defensive, but limits reuse | Rejected — the route is the policy enforcement point |

### Decision: Symbol list fetched inline at page render

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Dedicated `/api/symbols` endpoint | Clean separation, cacheable | **Inline render** — simpler, no extra endpoint. Render-time query is fast (DuckDB, distinct on indexed column). Can extract later if needed |
| Static list in config | No DB dependency | Rejected — stale on data changes |

### Decision: JSON `time` as Unix epoch seconds

This is the Lightweight Charts v4 contract (`time` as `UTCTimestamp` — integer seconds). No datetime string conversion. The API returns `time` as an integer, the JS passes it directly to `createChart().setData()`.

### Decision: Vanilla JS, no bundler

Lightweight Charts v4 is loaded from unpkg CDN via `<script src="...">`. `static/js/chart.js` is a plain `<script>` file that uses the global `LightweightCharts` object. No npm, no webpack, no build step.

## Data Flow

```
Browser
  │
  ├─ GET /market/chart ──────────────────────────────────────────┐
  │                                                              ▼
  │                                              Jinja2 → chart.html
  │                                              (symbols from DuckDB inline)
  │                                                              │
  │  ┌─ page load ───────────────────────────────────────────────┘
  │  │
  │  └─ fetch(/api/ohlc?symbol=NDX&limit=200)
  │          │
  │          ▼
  │    FastAPI route (GET /api/ohlc)
  │      │  min(limit, 5000) ← cap enforcement
  │      │  MarketDatabase.query_ohlc(symbol, limit)
  │      │      │
  │      │      ▼
  │      │    DuckDB: WHERE symbol=? ORDER BY datetime DESC LIMIT ?  (limit mode)
  │      │        └─ results reversed to ascending
  │      │    DuckDB: WHERE symbol=? AND datetime>=? AND datetime<?  (date range mode)
  │      │
  │      └─ JSON [{time, open, high, low, close, volume}]
  │
  └─ LightweightCharts.createChart().setData(response)
```

## query_ohlc() Interface

```python
def query_ohlc(
    self,
    symbol: str,
    timeframe: str = "1m",
    limit: int = 200,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
) -> list[dict]:
```

Two query modes:
- **Limit mode** (no start/end): `WHERE symbol=? ORDER BY datetime DESC LIMIT ?` → reverse to ascending
- **Date range mode**: `WHERE symbol=? AND datetime>=? AND datetime<? ORDER BY datetime`

Result: each dict has `time` (int, Unix epoch seconds), `open`, `high`, `low`, `close`, `volume` (float/int).

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/market.py` | Modify | Add `query_ohlc()` method to MarketDatabase |
| `app/main.py` | Modify | Register `GET /api/ohlc` + `GET /market/chart` routes |
| `templates/base.html` | Modify | Add "Market" nav link |
| `templates/market/chart.html` | Create | Chart page: symbol `<select>`, date inputs, chart `<div>` |
| `static/js/chart.js` | Create | Lightweight Charts init, fetch API, `setData()` |
| `static/css/app.css` | Modify | Chart container and form styles |
| `tests/test_market.py` | Modify | Add unit tests for `query_ohlc()` |
| `tests/test_chart.py` | Create | Integration tests for both chart endpoints |

## Interfaces / Contracts

### JSON Response (`GET /api/ohlc`)

```json
[
  {"time": 1704067200, "open": 5573.5, "high": 5576.0, "low": 5573.5, "close": 5575.0, "volume": 30}
]
```

- Always an array (empty `[]` for unknown symbol)
- `time` is integer Unix epoch seconds (Lightweight Charts `UTCTimestamp`)
- Ordered ascending by time

### Error Response

```json
{"detail": "symbol is required"}
```
- 422 for missing `symbol`
- No 404 for unknown symbol — returns empty array

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | `query_ohlc()` — limit mode, date range mode, empty symbol, max limit, ascending order | `MarketDatabase(db_path=":memory:")` fixture, insert known data, assert returned records |
| Integration | `GET /api/ohlc` — valid request, 5000 cap, 422 missing symbol, empty array for unknown, date range filter | `TestClient(app)` against FastAPI |
| Integration | `GET /market/chart` — 200 HTML, symbol options present, chart div exists | `TestClient(app)`, check body for key elements |

## Migration / Rollout

No migration required. DuckDB data is read-only. New routes are additive — no breaking changes to existing endpoints.

## Open Questions

- None

## Out of Scope (per proposal)

- Lazy loading on drag/pan
- Multi-timeframe aggregation (5m, 1h, 1d)
- localStorage state persistence
