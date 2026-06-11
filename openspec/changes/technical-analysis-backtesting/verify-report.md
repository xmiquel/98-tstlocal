# Verification Report: technical-analysis-backtesting — PR#1 (Backend)

**Date**: 2026-06-11
**Change**: technical-analysis-backtesting
**Scope**: PR#1 — Backend (tasks 1.1–2.5)
**Mode**: hybrid (openspec + engram)
**Strict TDD**: ENABLED

---

## Completeness Table

| Artifact | Status | Notes |
|----------|--------|-------|
| Proposal | done | Read from `proposal.md` |
| Specs | done | 3 spec files (trading-domain, market-chart, technical-indicators) |
| Design | done | Read from `design.md` |
| Tasks | done | 10 of 54 tasks checked [x] (backend scope only) |
| Apply Progress | partial | PR#1 implemented first 10 of 10 backend tasks |
| Verify Report | done | This file |

## Task Progress

| Task | Status | Evidence |
|------|--------|----------|
| 1.1 Add `pandas-ta-classic`, `cachetools` to `pyproject.toml` | ✅ Done | Dependencies present in `pyproject.toml` |
| 1.2 Test: `query_ohlc_as_df()` returns DataFrame | ✅ Done | 7 tests in `tests/test_market.py` (lines 358–475) |
| 1.3 Add `query_ohlc_as_df()` to `app/market.py` | ✅ Done | Lines 404–441 — reuses `self._conn.execute()` |
| 1.4 Test: `IndicatorEngine.calculate()` all 5 indicators + cache | ✅ Done | 12 tests in `tests/test_indicators.py` |
| 1.5 Create `app/indicators.py` with `IndicatorEngine` + TTLCache | ✅ Done | 220 lines, TTLCache maxsize=128, ttl=300 |
| 2.1 Test: `GET /api/indicators/catalog` returns 5 entries | ✅ Done | 2 tests in `tests/test_indicators_api.py` |
| 2.2 Test: `POST /api/indicators/calculate` valid/422/empty | ✅ Done | 5 tests in `tests/test_indicators_api.py` |
| 2.3 Add indicator schemas to `app/schemas.py` | ✅ Done | `IndicatorParam`, `CatalogEntry`, `IndicatorRequest`, `IndicatorValue`, `IndicatorResult` |
| 2.4 Create `app/routers/indicators.py` with catalog + calculate | ✅ Done | 60 lines, both endpoints implemented |
| 2.5 Register router in `app/main.py` | ✅ Done | Line 42: `app.include_router(indicators_router)` |

**10/10 backend tasks complete**. Remaining 44 tasks (frontend, E2E, polish) are out of scope for PR#1.

---

## Command Evidence

### Test Suite (full, with coverage)

```
102 passed, 10 deselected in 8.98s
Coverage: 86.80% (above 80% gate)
```

| File | Coverage | Notes |
|------|----------|-------|
| `app/indicators.py` | 100% | Full coverage |
| `app/routers/indicators.py` | 100% | Full coverage |
| `app/schemas.py` | 100% | Full coverage |
| `app/market.py` | 82% | New `query_ohlc_as_df` methods covered |
| `app/main.py` | 90% | Router registration covered |

### Indicator Tests (verbose)

```
19 passed in 3.08s
test_indicators.py: 12/12 passed
test_indicators_api.py: 7/7 passed
```

### Lint Check

```
ruff check: 16 errors FOUND — FAILED
ruff format: 6 files would be reformatted — FAILED
mypy: 9 errors in 5 files — FAILED
```

---

## Spec Compliance Matrix

### Technical Indicators Spec

| Scenario | Status | Test Evidence |
|----------|--------|---------------|
| SMA calculated from OHLCV DataFrame | ✅ PASS | `test_sma_calculates_label_and_values` |
| TTLCache returns cached result within TTL | ✅ PASS | `test_cache_hit_returns_same_as_first_call` |
| TTLCache recomputes after 5 minutes | ❌ UNTESTED | No time-travel test for eviction; TTL value verified as 300s |
| Valid RSI request returns 200 with values | ✅ PASS | `test_calculate_sma_returns_200_with_values` (same logic) |
| Unknown indicator returns 422 | ✅ PASS | `test_calculate_unknown_indicator_returns_422` |
| Empty symbol returns empty values | ✅ PASS | `test_calculate_empty_symbol_returns_empty_values` |
| Catalog returns initial 5 indicators | ✅ PASS | `test_catalog_returns_200_with_5_entries` (SMA, EMA, RSI, MACD, BBANDS) |
| Each entry defines its parameters | ✅ PASS | `test_catalog_each_entry_has_name_and_params` |

### Trading Domain Spec

| Scenario | Status | Test Evidence |
|----------|--------|---------------|
| query_ohlc_as_df returns DataFrame | ✅ PASS | `test_query_ohlc_as_df_returns_dataframe` |
| Unknown symbol returns empty DataFrame | ✅ PASS | `test_query_ohlc_as_df_empty_for_unknown_symbol` |
| DataFrame reuses existing DuckDB connection | ✅ PASS | `test_query_ohlc_as_df_uses_existing_connection` |
| before parameter semantics match query_ohlc | ✅ PASS | `test_query_ohlc_as_df_before_semantics` |

### Spec Requirement: Cache Key

> "Results SHALL be cached via TTLCache with a 5-minute TTL, keyed by **symbol + timeframe + indicator name + parameter hash**."

**STATUS: ❌ FAIL** — Cache key implementation:
```python
def _make_cache_key(indicator: str, params: dict[str, Any]) -> str:
    raw = json.dumps({"indicator": indicator, "params": params}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()
```
The key only includes `indicator` and `params` (name + params hash). **Missing `symbol` and `timeframe`**. This means requesting the same indicator+params for different symbols returns the first symbol's data. This is a correctness bug.

---

## Correctness Table

| Check | Status | Details |
|-------|--------|---------|
| All tasks checked | ✅ PASS | 10/10 backend tasks marked [x] |
| Tests pass | ✅ PASS | 102 passed, all indicator tests pass |
| Coverage >= 80% | ✅ PASS | 86.80% |
| TTLCache maxsize=128, ttl=300 | ✅ PASS | Verified by tests |
| Cache key includes symbol+timeframe | ❌ FAIL | Spec violation — see above |
| Schema models exist | ✅ PASS | IndicatorParam, CatalogEntry, IndicatorRequest, IndicatorValue, IndicatorResult |
| Router registered | ✅ PASS | Line 42 in main.py |
| catalog returns 5 entries | ✅ PASS | SMA, EMA, RSI, MACD, BBANDS |
| Invalid indicator → 422 | ✅ PASS | Tested via API |
| Empty symbol → empty values | ✅ PASS | Tested via API |

---

## Design Coherence Table

| Design Decision | Implementation | Status | Notes |
|-----------------|----------------|--------|-------|
| TTLCache keyed by (symbol, timeframe, indicator, params_hash) | Keyed by (indicator, params) only | ❌ FAIL | Missing symbol+timeframe in key |
| maxsize=256 | maxsize=128 | ⚠️ WARNING | Design says 256, code uses 128 (test asserts 128) |
| TTLCache 5min TTL | TTL=300 | ✅ MATCH | Correct |
| New APIRouter pattern | `app/routers/indicators.py` + `include_router` | ✅ MATCH | Correct |
| `query_ohlc_as_df()` reuses connection | Uses `self._conn.execute()` | ✅ MATCH | Correct |
| `IndicatorParam`, `IndicatorCatalogEntry`, `IndicatorRequest`, `IndicatorResult` | `IndicatorParam`, `CatalogEntry`, `IndicatorRequest`, `IndicatorResult` | ✅ MATCH | Minor naming: `CatalogEntry` instead of `IndicatorCatalogEntry` — functionally identical |

---

## Issues

### CRITICAL

1. **Cache key omits symbol and timeframe** — `_make_cache_key()` only hashes `indicator` + `params`, not `symbol` or `timeframe`. Spec explicitly says "keyed by symbol + timeframe + indicator name + parameter hash". Cross-symbol requests with the same indicator/params would return the wrong cached values. **File**: `app/indicators.py` lines 65–68.

2. **ruff check: 16 errors** — All E501 (line too long) in `app/indicators.py` (8 errors), `tests/test_indicators.py` (1), `tests/test_indicators_api.py` (1), `tests/test_market.py` (1), plus B905, SIM115, UP17. **CI would fail**.

3. **ruff format: 6 files unformatted** — `app/indicators.py`, `app/market.py`, `app/routers/__init__.py`, `tests/test_chart.py`, `tests/test_indicators_api.py`, `tests/test_market.py`. **CI would fail**.

4. **mypy: 9 errors** — 6 stub errors (pandas, pandas_ta_classic, cachetools — acceptable/pre-existing pattern). 3 real errors:
   - `app/indicators.py:73` — Unused `type: ignore` comment
   - `app/indicators.py:110` — Returning Any from function declared `list[dict[str, Any]]` (from unstubbed cache)
   - `app/routers/indicators.py:23` — Missing type arguments for `dict` → should be `list[dict[str, Any]]`

5. **Strict TDD gap: TTLCache recompute after expiry** — Spec scenario requires a test proving recomputation after TTL expiry (6 minutes ago → cache miss). No test exists. Test `test_cache_ttl_is_300_seconds` only verifies the TTL value, not expiry behavior.

### WARNING

1. **Design says maxsize=256, implementation uses 128** — Minor, but a design deviation. Test explicitly asserts 128, so this appears intentional.
2. **No `IndicatorCatalogEntry` → `CatalogEntry`** — Design uses `IndicatorCatalogEntry`, implementation uses `CatalogEntry`. Minor naming deviation.

### SUGGESTION

1. Line length violations in CATALOG entries could be fixed with multi-line formatting.
2. `tests/test_indicators.py:115` — Add `strict=True` to `zip()` call.
3. `tests/test_indicators_api.py:62` — Use context manager for temp files.
4. `tests/test_market.py:385,416,434` — Use `datetime.UTC` alias.

---

## Final Verdict

**FAIL**

PR#1 (Backend) implementation is functionally complete: all 10 tasks are implemented, all 102 tests pass, coverage is 86.80%, and most spec scenarios have passing tests. However, three CRITICAL issues prevent a pass:

1. **Cache key spec violation** — missing `symbol`+`timeframe` in cache key (correctness bug)
2. **CI tooling failures** — ruff (16 errors), ruff format (6 files), mypy (9 errors) would all fail CI
3. **Strict TDD gap** — TTLCache recompute-after-expiry scenario has no covering test

The cache key issue is the most serious: it means requesting SMA(20) for symbol "NDX" followed by SMA(20) for "SPX" would return NDX's values for SPX. This must be resolved before the code is reliable.

**Remediation required**: Fix cache key to include symbol+timeframe, address CI tooling issues, and add TTLCache expiry test.
