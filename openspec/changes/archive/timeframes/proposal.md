# Proposal: Timeframe Aggregation for OHLCV API and Chart

## Intent

Add timeframe aggregation (5m, 15m, 30m, 1h, 4h, 1d) to the OHLCV API and chart page. The `timeframe` param currently exists but is ignored. DuckDB's `time_bucket()` enables efficient wall-clock-aligned aggregation at ~46ms for 3.4M rows.

## Scope

### In Scope
- Aggregation logic in `query_ohlc()` via `time_bucket(CAST(? AS INTERVAL), datetime)`
- `1m` kept as direct query (no aggregation overhead)
- `LIMIT` applied after aggregation (subquery pattern)
- `spread` field added to API response
- Visible `<select name="timeframe">` in chart page
- Updated tests for aggregation queries and `spread`

### Out of Scope
- Lazy loading on drag/pan
- Layout persistence
- Visual regression testing

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `market-chart`: remove "only 1m implemented" caveat; add timeframe selector requirement
- `trading-domain`: update OHLCV Query requirement with aggregation support and `spread` field

## Approach

Interval map dict: `{"1m": None, "5m": "5 minutes", "15m": "15 minutes", "30m": "30 minutes", "1h": "1 hour", "4h": "4 hours", "1d": "1 day"}`. For `1m`, run direct query. For all others, use `time_bucket(CAST(? AS INTERVAL), datetime)` with `first(open)`, `max(high)`, `min(low)`, `last(close)`, `sum(volume)`, `first(spread)`. Limit mode: `ORDER BY bucket DESC LIMIT ?` + reverse. Date range mode: filter `WHERE datetime >= ? AND datetime < ?` then group and order ascending. Frontend: swap hidden `<input>` for visible `<select>` — JS already handles `timeframe` param.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/market.py` | Modified | Add aggregation to `query_ohlc()`, activate `timeframe` param |
| `app/main.py` | Modified | Add `spread` to API response, pass timeframe to chart template |
| `templates/market/chart.html` | Modified | Replace hidden input with visible timeframe `<select>` |
| `openspec/specs/market-chart/spec.md` | Modified | Remove "only 1m" caveat, add timeframe selector |
| `openspec/specs/trading-domain/spec.md` | Modified | Update OHLCV Query with aggregation |
| `tests/test_market.py` | Modified | Add aggregation + spread tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `time_bucket` unavailable (< DuckDB 0.10) | Low | DuckDB 1.5.3 confirmed; epoch math fallback |
| `spread` breaks existing frontend consumers | Low | JS ignores unknown keys; backward compatible |

## Rollback Plan

Revert `timeframe` activation in `query_ohlc()` to ignore the param. Remove `spread` from response. Restore hidden `<input>` in template. Timeframe param returns to `# noqa: ARG002` status.

## Dependencies

None. DuckDB 1.5.3 confirmed with `time_bucket`.

## Success Criteria

- [ ] `GET /api/ohlc?symbol=NDX&timeframe=5m` returns aggregated 5m bars with `spread`
- [ ] `GET /api/ohlc?symbol=NDX&timeframe=1m` returns direct 1m bars (unchanged behavior)
- [ ] `spread` field present in every OHLCV response
- [ ] Chart page `<select>` lists all 7 timeframe options
- [ ] All tests pass (existing + new aggregation tests)
