# Tasks: Timeframe Aggregation for OHLCV API and Chart

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~180 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Backend — Aggregation

- [x] 1.1 Add `INTERVAL_MAP` dict + `_query_ohlc_aggregated()` to `app/market.py`
- [x] 1.2 Refactor `query_ohlc()` to route 1m → raw, others → aggregated
- [x] 1.3 Add `spread` field to result dict in both raw and aggregated paths

## Phase 2: API — Validation

- [x] 2.1 Add timeframe validation in `app/main.py` (422 for invalid values)
- [x] 2.2 Route passes validated timeframe to `query_ohlc()`

## Phase 3: Frontend — Timeframe Selector

- [x] 3.1 Swap hidden `<input name="timeframe">` for visible `<select>` in `chart.html`

## Phase 4: Tests

- [x] 4.1 Add tests in `test_market.py`: each timeframe produces bars with correct field names
- [x] 4.2 Verify `spread` is present in aggregated results
- [x] 4.3 Run full suite: `uv run pytest` — 19 passed

## Phase 5: Verify

- [x] 5.1 `ruff check . && ruff format --check . && mypy .` — all clean
