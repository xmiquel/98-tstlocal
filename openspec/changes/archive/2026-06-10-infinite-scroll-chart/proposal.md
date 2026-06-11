# Proposal: Infinite / Lazy Scroll Chart Loading

## Intent

When the user pans/drags the candlestick chart left (into the past) and reaches the last loaded candle, automatically fetch and prepend 1000 more historical bars. Seamless scrolling — no button, no reload.

## Scope

### In Scope
- Backend: `before` (UNIX timestamp) param on `GET /api/ohlc` — cursor-based pagination
- Backend: `_query_ohlc_raw_before()` + `_query_ohlc_aggregated_before()` methods querying `WHERE datetime < ?`
- Frontend: Accumulated `allData` array (replaces separate `rawData`)
- Frontend: Subscribe to `chart.timeScale().subscribeVisibleLogicalRangeChange`
- Frontend: Detect `barsBefore < 50`, fetch with `before=oldestTimestamp`, prepend, call `series.setData(allData)`, restore position via `setVisibleLogicalRange()`
- Frontend: `loading` gate flag to prevent concurrent fetches
- Tests: Unit + API + E2E for `before` parameter and scroll-triggered fetch

### Out of Scope
- Infinite scroll forward (future) — only historical left-pan
- Debounce/throttle beyond the loading gate flag
- Memory cap (200 + 1000 per fetch is reasonable)
- HTMX integration (chart is JS-only with Lightweight Charts)
- Removing the 5000 API cap

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `trading-domain`: OHLC query methods gain `before` cursor for paginated historical loads
- `market-chart`: Chart page gains lazy-load scroll behavior with data accumulation

## Approach

Subscribe to Lightweight Charts `subscribeVisibleLogicalRangeChange`. Call `series.barsInLogicalRange()` — when `barsBefore < 50`, fetch 1000 bars via `GET /api/ohlc?before=<ts>`. Prepend to `allData`, call `series.setData(allData)`, restore scroll position with `setVisibleLogicalRange()`. Loading gate prevents concurrent fetches.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/market.py` | Modified | Add `_query_ohlc*_before()` methods |
| `app/main.py` | Modified | Add `before: int \| None` to `/api/ohlc` |
| `static/js/chart.js` | Modified | Scroll detection, data accumulation, prepend |
| `tests/test_market.py` | Modified | Before-cursor query tests |
| `tests/test_chart_e2e.py` | Modified | Scroll-triggered fetch E2E |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Race condition | Medium | `loading` gate; re-check barsBefore after response |
| Visible range jump | Low | Capture range before, restore via `setVisibleLogicalRange` |
| Duplicate bars | Low | `WHERE datetime < ?` prevents overlap |
| Memory growth | Low | 1000 bars per fetch — reasonable for typical usage |

## Rollback Plan

Revert `app/market.py` query methods, `app/main.py` API changes, and `static/js/chart.js` changes. Tests revert with them.

## Dependencies

None.

## Success Criteria

- [ ] `GET /api/ohlc?before=<ts>&limit=1000` returns older bars only
- [ ] Panning left near edge triggers fetch automatically
- [ ] New bars prepended without visible jump
- [ ] No duplicate bars at boundary
- [ ] Loading gate prevents concurrent fetches
- [ ] All tests pass (coverage >= 80%)
