# Proposal: E2E Testing for JS Chart Runtime

## Intent

The current test stack (pytest + TestClient) cannot verify JavaScript execution — `fetch()`, Lightweight Charts `setData()`, canvas rendering. The candlestick-chart archive explicitly flagged this gap. Add Playwright-based E2E testing to close the gap without introducing a JS toolchain.

## Scope

### In Scope
- Add `pytest-playwright` dev dependency to `pyproject.toml`
- Create session-scoped `e2e_server` fixture: uvicorn subprocess + temp DuckDB
- Create `tests/test_chart_e2e.py` with 5 Playwright tests
- Add `@pytest.mark.e2e` — excluded from default `uv run pytest`
- Add separate `e2e` CI job with `playwright install chromium`
- Add `test-e2e` Makefile target

### Out of Scope
- Visual regression testing (screenshot diff)
- Non-chart E2E scenarios
- Multi-browser testing (Chromium only)

## Capabilities

### New Capabilities
None — testing infrastructure, not a product capability.

### Modified Capabilities
None — no spec-level behavior changes.

## Approach

1. `uv add --dev pytest-playwright` + configure e2e marker in pyproject.toml
2. Session-scoped fixture: `subprocess.Popen(["uvicorn", ...])` on random port, poll `/health`, terminate on teardown; temp DuckDB with 3 OHLCV bars for symbol TEST
3. 5 Playwright tests: page loads clean, candles render, symbol selector triggers re-render, date range form updates chart, empty data shows no candles
4. CI: separate `e2e` job with `playwright install chromium` + cache `~/.cache/ms-playwright`
5. Makefile: `test-e2e` target for local runs

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `pyproject.toml` | Modified | Add pytest-playwright dep + e2e marker config |
| `tests/conftest.py` | Modified | Add e2e_server session-scoped fixture |
| `tests/test_chart_e2e.py` | New | 5 Playwright E2E tests |
| `.github/workflows/ci.yml` | Modified | Add e2e job (separate from quality-gate) |
| `Makefile` | Modified | Add test-e2e target |
| `.gitignore` | Modified | Add `playwright/` browser cache dir |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| CI ~300MB browser download | Medium | Cache `~/.cache/ms-playwright` in GHA |
| Test flakiness (async timing) | Medium | `expect()` auto-wait, 10s timeout, optional retries |
| Port conflicts | Low | OS-assigned port via `bind(("127.0.0.1", 0))` |
| Orphaned temp DB on crash | Low | `atexit` cleanup + fixture `finally` block |

## Rollback

Revert the commit. All changes are dev-tooling only — no app code touched.

## Dependencies

None.

## Success Criteria

- [ ] `uv run pytest -m e2e` passes with all tests green
- [ ] CI `e2e` job passes on GitHub Actions
- [ ] `uv run pytest` (without `-m e2e`) skips E2E tests and still passes
