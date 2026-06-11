# Design: Infinite / Lazy Scroll Chart Loading

## Technical Approach

Cursor-based pagination on `GET /api/ohlc?before=<unix_ts>` returns bars strictly older than the given timestamp. Lightweight Charts `subscribeVisibleLogicalRangeChange` + `barsInLogicalRange()` detect when `barsBefore < 50`, triggering a fetch prepend. Accumulated `allData` array replaces the ephemeral `rawData` — every write goes through `series.setData(allData)`, restoring scroll position via `setVisibleLogicalRange()`.

## Architecture Decisions

### Decision: `before` cursor vs offset pagination

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `?before=<ts>` cursor | Stable under concurrent ingestion; no skipped/duplicate pages | **Chosen** |
| `?page=N&offset=M` | Shifts when new bars arrive; race-prone | Rejected |

**Rationale**: OHLC data is append-only forward in time. A `WHERE datetime < ?` cursor is naturally stable — inserting new recent bars never touches historical pages.

### Decision: `allData` accumulation vs fetch-and-replace

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Accumulate in `allData` | Single source of truth for tooltip + chart; prepend is O(n) but n stays under 10k | **Chosen** |
| Fetch-and-replace on every scroll | Resets scroll position; loses loaded history | Rejected |

**Rationale**: `allData` grows by ~1000 bars per fetch, trivially small for Lightweight Charts. A single mutation point (`series.setData(allData)`) guarantees tooltip and chart are always in sync.

### Decision: `loading` gate vs debounce

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Boolean `loading` gate | Simple; prevents concurrent fetches but may miss a second trigger | **Chosen** |
| `rxjs` / debounce | Heavy for one flag; over-engineering for a simple scroll check | Rejected |

**Rationale**: After fetch completes, a re-check (`barsBefore` re-read) covers the edge case where the user kept scrolling during the fetch.

## Data Flow

```
User pans chart left
       │
       ▼
subscribeVisibleLogicalRangeChange fires
       │
       ▼
series.barsInLogicalRange(range)
       │
       ├── barsBefore ≥ 50 → no-op
       │
       └── barsBefore < 50 AND !loading
               │
               ▼
           loading = true
           beforeTs = allData[0].time
               │
               ▼
           GET /api/ohlc?symbol=X&timeframe=1m&limit=1000&before=<beforeTs>
               │
               ▼
           newBars = response (already ascending)
           allData = [...newBars, ...allData]   // prepend
           series.setData(allData)
               │
               ▼
           snapshot = {from: newBars.length, to: newBars.length + prevVisible}
           chart.timeScale().setVisibleLogicalRange(snapshot)
               │
               ▼
           loading = false
           // re-check barsBefore (user may have kept scrolling)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/market.py` | Modify | Add `_query_ohlc_raw_before()` and `_query_ohlc_aggregated_before()` |
| `app/main.py` | Modify | Add `before: int \| None = Query(None)` to `GET /api/ohlc` |
| `static/js/chart.js` | Modify | Replace `rawData` → `allData`; add scroll subscription, prepend logic, loading gate |
| `tests/test_market.py` | Modify | Add tests for `_query_ohlc_raw_before` and `_query_ohlc_aggregated_before` |
| `tests/test_chart.py` | Modify | Add API integration test for `?before=` param |
| `tests/test_chart_e2e.py` | Modify | Add E2E test for scroll-triggered data fetch |

## Interfaces / Contracts

**`GET /api/ohlc` — new optional parameter:**

```python
@app.get("/api/ohlc")
def get_ohlc(
    symbol: str = Query(...),
    timeframe: str = Query("1m"),
    limit: int = Query(200, ge=1),
    start: str | None = Query(None),
    end: str | None = Query(None),
    before: int | None = Query(None, description="UNIX timestamp cursor"),
) -> JSONResponse
```

**Behavior matrix:**

| `start`/`end` | `before` | Behavior |
|---------------|----------|----------|
| Provided | Ignored | Date-range mode (unchanged) |
| Not provided | Not provided | Limit mode — last N bars (unchanged) |
| Not provided | Provided | Cursor mode — N bars strictly before `before` timestamp |

**`_query_ohlc_raw_before(symbol, limit, before_ts) -> list[dict]`**

```sql
SELECT datetime, open, high, low, close, tickvol, spread
FROM dt_ohlc_m1
WHERE symbol = ? AND datetime < ?
ORDER BY datetime DESC
LIMIT ?
```
→ reverse results to ascending.

**`_query_ohlc_aggregated_before(symbol, limit, before_ts, bucket) -> list[dict]`**

Same pattern with `time_bucket` aggregation and `WHERE datetime < ?`.

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | `_query_ohlc_raw_before` returns correct bars before timestamp | DuckDB in-memory with known data, assert all returned times < before_ts |
| Unit | `_query_ohlc_aggregated_before` aggregation with before cursor | Same pattern with time_bucket timeframes |
| Unit | `before` takes priority only when no start/end | Test all three endpoint paths route correctly |
| Integration | `GET /api/ohlc?before=<ts>` returns 200 with expected data | TestClient, verify all times < timestamp |
| Integration | `before` with large `limit` capped at 5000 | Same cap as existing endpoint |
| E2E | Scroll-triggered fetch | Evaluate JS to call `setVisibleLogicalRange` near chart edge, wait for network, assert `allData` grew |
| E2E | No duplicate bars | After scroll-triggered load, verify no duplicate timestamps in accumulated data |

## Migration / Rollout

No migration required. The `before` parameter is additive — existing clients that never send `before` get identical behavior. The frontend change is purely client-side progressive enhancement.

## Open Questions

- [ ] What default fetch size to use? Proposal says 1000 — confirm it's not too slow for aggregated timeframes (1h/1d) where the SQL does `time_bucket` + sort.
- [ ] Should the `before` param accept an ISO date string too, or only UNIX int? Keeping it int-only keeps type-safety simple, but the existing API uses ISO strings for `start`/`end`.
