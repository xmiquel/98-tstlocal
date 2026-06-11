## Exploration: infinite-scroll-chart

### Current State

**Chart Technology**: Lightweight Charts v4.2.1 loaded via CDN. The chart renders candlestick data fetched from a FastAPI endpoint.

**Loading Logic** (`static/js/chart.js`):
- `loadData()` fetches OHLC data via `GET /api/ohlc`, calls `series.setData(data)` which **replaces all existing data**.
- After loading, `chart.timeScale().fitContent()` zooms to show all data.
- A separate `rawData` array is kept for tooltip crosshair lookups.
- **No incremental loading or scroll detection exists today.**

**API Endpoint** (`GET /api/ohlc` at `app/main.py:50`):
- Parameters: `symbol` (required), `timeframe` ("1m" default), `limit` (200 default, **capped at 5000**), `start` (ISO date), `end` (ISO date).
- **No cursor-based pagination parameter** (no `before` timestamp).
- When no dates provided: queries last N bars, ordered newest-first, then reversed client-side.

**Market Database** (`app/market.py`):
- Two query modes: date range (`datetime >= ? AND datetime < ?`) and limit mode (`ORDER BY datetime DESC LIMIT ?`).
- **No "load N bars before timestamp X" pattern exists.** Both raw and aggregated queries lack this.

**Template** (`templates/market/chart.html`):
- Passes `window.__chartConfig` with `{symbol, timeframe, limit, start, end}`.
- Limit is hardcoded to 200 in the form (`<input type="hidden" name="limit" value="200">`).

### Affected Areas

- `static/js/chart.js` — Add `subscribeVisibleLogicalRangeChange` listener, data accumulation, and scroll-aware loading.
- `app/main.py` — Add `before` query parameter to `GET /api/ohlc`.
- `app/market.py` — Add "load N bars before timestamp" query method for raw and aggregated OHLC.
- `templates/market/chart.html` — May need minor config changes (remove hardcoded limit?).
- `openspec/specs/{domain}/spec.md` — Update main spec with new infinite-scroll requirements.

### Approaches

1. **Logical range + `barsInLogicalRange` (recommended)** — Leverage the official Lightweight Charts API pattern for lazy loading.
   - Subscribe to `chart.timeScale().subscribeVisibleLogicalRangeChange(handler)`.
   - Inside handler, call `series.barsInLogicalRange(visibleRange)` — if `barsBefore < threshold` (e.g. 50), trigger fetch.
   - Fetch older data via new `before` API parameter, prepend to client-side array, call `series.setData(allData)`.
   - After prepend, restore scroll position with `chart.timeScale().setVisibleLogicalRange()` to avoid visual jump.
   - Pros: Official pattern documented in Lightweight Charts API; precise detection; no polling or guesswork.
   - Cons: Requires `setData` (full replace) since Lightweight Charts v4 has no `prepend` API — must concatenate client-side and reset visible range.
   - Effort: Medium

2. **Polling `getVisibleLogicalRange()` via scroll event** — Use wheel/scroll event listeners to detect when user reaches left edge, then fetch more.
   - Pros: More control over timing.
   - Cons: Reinventing what `subscribeVisibleLogicalRangeChange` already does; scroll events are noisy, need debouncing; no access to `barsInLogicalRange` metadata.
   - Effort: Medium-High

3. **Load all data upfront** — Increase limit to 5000 (max), load everything in one request.
   - Pros: Simplest code; no scroll detection needed.
   - Cons: Slow initial load; wastes bandwidth; defeats the purpose of lazy loading; 5000 may not be enough for some timeframes.
   - Effort: Low

### Recommendation

**Approach 1: Logical range + `barsInLogicalRange`.**

This is the exact pattern the Lightweight Charts API docs demonstrate for this use case:

```javascript
function onVisibleLogicalRangeChanged(newVisibleLogicalRange) {
    const barsInfo = series.barsInLogicalRange(newVisibleLogicalRange);
    if (barsInfo !== null && barsInfo.barsBefore < 50) {
        // fetch and prepend more data
    }
}
chart.timeScale().subscribeVisibleLogicalRangeChange(onVisibleLogicalRangeChanged);
```

**Backend changes needed:**
- Add `before: int | None = Query(None)` to `GET /api/ohlc` — UNIX timestamp cursor.
- If `before` is set, ignore `start`/`end` and query: `WHERE datetime < ? ORDER BY datetime DESC LIMIT ?`.
- Add `_query_ohlc_raw_before()` and `_query_ohlc_aggregated_before()` methods to `MarketDatabase`.

**Client-side changes needed:**
- Initialize empty `allData` array.
- On initial load and subsequent fetches, store data in `allData`.
- Subscribe to `visibleLogicalRangeChange`; when `barsBefore < threshold` (e.g. 50), compute `oldestTime` from `allData[0]`, fetch `before=oldestTime`, prepend to `allData`, call `series.setData(allData)`.
- After prepend, restore visible position using `setVisibleLogicalRange()` with adjusted logical range.
- Add loading indicator to prevent duplicate fetches while a request is in flight.
- Implement `series.setData()` with the accumulated array to avoid empty chart area during load.

### Risks

- **Race condition**: Multiple rapid scrolls could trigger concurrent fetches. Solution: use a `loading` flag to gate fetches.
- **Visible range flicker**: If `setData()` with prepended data shifts the view, `setVisibleLogicalRange()` must be called immediately after to restore position. This should be tested thoroughly.
- **Memory**: Accumulating all loaded data client-side could grow large with high-resolution timeframes (e.g. 1m). The 5000 cap per fetch + threshold-based limiting prevents runaway growth.
- **Tooltip data**: `rawData` must be kept in sync with `allData` (or replaced entirely by `series.data()` for lookups).

### Ready for Proposal
Yes
