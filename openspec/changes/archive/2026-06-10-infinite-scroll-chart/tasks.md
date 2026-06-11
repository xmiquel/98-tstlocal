# Tasks: Infinite Scroll Chart Loading

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend before-cursor queries + API + frontend scroll | PR 1 | Single PR — well under 400 lines |

## Phase 1: Backend Before-Cursor Queries (TDD)

- [x] 1.1 Write unit test `test_query_ohlc_raw_before` in `tests/test_market.py` — asserts all returned times < before_ts
- [x] 1.2 Implement `_query_ohlc_raw_before()` in `app/market.py` — `WHERE datetime < to_timestamp(?::DOUBLE) ORDER BY datetime DESC LIMIT ?` + reverse
- [x] 1.3 Write unit test `test_query_ohlc_5m_before` in `tests/test_market.py` — aggregated before-cursor test
- [x] 1.4 Implement `_query_ohlc_aggregated_before()` in `app/market.py` — time_bucket with before cursor
- [x] 1.5 Write unit test `test_query_ohlc_1h_before` in `tests/test_market.py` — 1h aggregation with before
- [x] 1.6 Write unit test `test_query_ohlc_before_returns_fewer` in `tests/test_market.py` — fewer bars than limit
- [x] 1.7 Route `before` param in `query_ohlc()` — if `before` is set without `start_date`, dispatch to before methods

## Phase 2: API Before-Cursor Endpoint (TDD)

- [x] 2.1 Write integration test `test_api_ohlc_before_returns_older_data` in `tests/test_chart.py` — GET with before=timestamp, assert times < ts
- [x] 2.2 Add `before: int | None = Query(None)` to `get_ohlc` in `app/main.py`
- [x] 2.3 Wire before-cursor dispatch in handler: when `before` is set without `start`/`end`, call before methods

## Phase 3: Frontend Scroll Loading (TDD)

- [x] 3.1 Write E2E test `test_infinite_scroll_triggers_fetch` in `tests/test_chart_e2e.py` — evaluate JS near edge, assert allData grew
- [x] 3.2 Write E2E test `test_no_duplicate_bars_after_prepend` in `tests/test_chart_e2e.py` — no duplicate timestamps
- [x] 3.3 Refactor `chart.js`: replace `var rawData` with `let allData`, modify `loadData()` to prepend new bars on before-response
- [x] 3.4 Add scroll subscription: `chart.timeScale().subscribeVisibleLogicalRangeChange` + `barsInLogicalRange()` check for `barsBefore < 50`
- [x] 3.5 Add `loading` gate flag: set before fetch, clear after setData + restore position, re-check `barsBefore` on completion

## Phase 4: Verification

- [x] 4.1 Run quality gate — all tests pass, coverage >= 80%
