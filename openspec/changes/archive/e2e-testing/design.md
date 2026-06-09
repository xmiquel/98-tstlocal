# Design: E2E Testing for JS Chart Runtime

## Technical Approach

Add Playwright Python (`pytest-playwright`) E2E tests for the Lightweight Charts JS runtime. A session-scoped fixture starts uvicorn as a subprocess with a temp DuckDB (3 bars for symbol TEST). Tests use Playwright's `page` fixture to verify JS `fetch()` + `setData()` work end-to-end. All E2E gated behind `@pytest.mark.e2e` — excluded from default runs to keep CI fast.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Server fixture | `subprocess.Popen(["uv", "run", "uvicorn", ...])` on random port | Thread with `uvicorn.run()`, subprocess without `uv run` | Process isolation — clean memory space, no GIL contention. `uv run` matches project convention. Random port via `bind(("", 0))` avoids conflicts. |
| Test data | Temp DuckDB via `tempfile.mktemp()`, 3 bars for "TEST" | Real `data/market.duckdb` (3.4M rows), in-memory DuckDB | Real DB is slow and non-deterministic. In-memory DuckDB doesn't match production path (`settings.MARKET_DB_PATH` is a file path). Temp file uses exact same code path. |
| CI structure | Separate `e2e` job (not part of `quality-gate`) | Same job with conditional steps, scheduled job | Chromium download adds ~2min. Separate job means normal pushes stay fast. Only E2E job waits for browser. |
| Test selection | `@pytest.mark.e2e`, default `addopts = "-m 'not e2e'"` | No marker, always run | Devs should never wait for Playwright. Explicit opt-in via `-m e2e`. `--strict-markers` prevents typos. |

## Data Flow

```
  pytest session
    │
    ├── e2e_server fixture (session scope)
    │     ├── Create temp DuckDB → insert 3 bars for "TEST"
    │     ├── Find free port via socket.bind(("", 0))
    │     ├── subprocess.Popen(["uv", "run", "uvicorn", ...]) with MARKDOWN_DB_PATH env
    │     ├── Poll /health → wait for 200
    │     ├── yield base_url → tests consume it
    │     └── teardown: proc.terminate(), os.unlink(db_path)
    │
    ├── test 1: page loads → page.goto(f"{url}/market/chart")
    │     └── JS: fetch("/api/ohlc?symbol=TEST") → setData() → canvas renders
    │
    ├── test 2: symbol selector → expect options[0].value == "TEST"
    │
    └── test N: ...
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Modify | Add `pytest-playwright` dev dep, `e2e` marker, `addopts` with `-m "not e2e"` |
| `tests/conftest.py` | Modify | Add session-scoped `e2e_server` fixture (subprocess + temp DuckDB) |
| `tests/test_chart_e2e.py` | Create | 5 Playwright E2E tests (page loads, candles render, symbol select, form submit, empty data) |
| `.github/workflows/ci.yml` | Modify | Add separate `e2e` job with `playwright install chromium` + browser cache |
| `Makefile` | Modify | Add `test-e2e` target |
| `.gitignore` | Modify | Add `playwright/` (local browser cache) |

## Interfaces / Contracts

No new interfaces. The `e2e_server` fixture yields a `str` (base URL). Tests consume Playwright's built-in `page: Page` fixture.

Key contract — the fixture setup sequence:
1. Temp DuckDB created → `MarketDatabase(db_path=...)` → table auto-created by `_ensure_table()`
2. 3 rows inserted via `db._conn.execute(...)`
3. `MARKET_DB_PATH` set in subprocess env so `settings.MARKET_DB_PATH` resolves to the temp file
4. Server is ready when `GET /health` returns 200

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| E2E | Chart page loads without JS errors | `expect(page).to_have_title(...)`, listen for `console` errors |
| E2E | Candles render after fetch | `expect(canvas).to_be_visible()`, verify `canvas height > 0` |
| E2E | Symbol selector renders TEST option | `expect(option).to_have_count(1)` — only "TEST" in temp DB |
| E2E | Form submit triggers re-render | Route-intercept `page.route("**/api/ohlc**")`, verify request count |
| E2E | Unknown symbol shows no candles | Navigate to nonexistent symbol, verify canvas exists but empty |

## Migration / Rollout

No migration required. E2E tests are additive — no existing behavior changes. Existing tests keep running with `-m "not e2e"`.

## Open Questions

None — design decisions resolved against the codebase and project conventions.
