## Exploration: E2E Testing for JS Chart

### Current State

The candlestick-chart SDD change is **archived and complete**. The JS chart (`static/js/chart.js`) uses Lightweight Charts v4 from CDN: on page load, it reads `window.__chartConfig`, calls `fetch("/api/ohlc?symbol=X&limit=N")`, and renders candles via `series.setData(data)`. Form submit re-fetches with new parameters.

**Current test coverage for chart behavior:**

| Layer | What it tests | Status |
|-------|--------------|--------|
| Unit (`test_market.py`) | `MarketDatabase.query_ohlc()` — limit mode, date range, unknown symbol | ✅ 10 tests |
| Integration (`test_chart.py`) | `GET /api/ohlc` response shape, status codes, caps | ✅ 6 tests |
| Integration (`test_chart.py`) | `GET /market/chart` HTML structure (has chart div, script tag, symbol select) | ✅ 2 tests |
| **E2E (JS runtime)** | **`fetch()` actually fires, `setData()` succeeds, canvas renders candles** | **❌ UNTESTED** |

The verify report for candlestick-chart explicitly flagged this gap:

> *Scenario "Chart JS loads from the API on init" untested — No test verifies that the page's JavaScript performs `fetch()` to `/api/ohlc` and calls `setData()`. This is JS runtime behavior that requires a browser context.*

### Affected Areas

- `pyproject.toml` — add `pytest-playwright` dev dependency
- `.github/workflows/ci.yml` — add `playwright install chromium` step, optionally separate e2e job
- `Makefile` — add `test-e2e` target
- `tests/conftest.py` — add Playwright fixtures (server lifecycle, test DB)
- `tests/test_chart_e2e.py` — NEW: Playwright E2E tests
- `static/js/chart.js` — may need minor changes for testability (e.g., expose chart instance on `window` for assertion)
- `.env.example` — document `MARKET_DB_PATH` override for E2E
- `.gitignore` — add `playwright/` browser cache if installed locally

### Approaches

1. **Playwright Python (`pytest-playwright`)** — **RECOMMENDED**
   - Install: `uv add --dev pytest-playwright` + `playwright install chromium`
   - Runs inside pytest: Playwright tests coexist with existing tests
   - `page` fixture from `pytest-playwright` gives a browser page
   - Start FastAPI via `subprocess.Popen` with `uvicorn` in session-scoped fixture
   - Use `@pytest.mark.e2e` to distinguish from unit/integration
   - Pros:
     - Stays in Python ecosystem — no new toolchain
     - Reuses existing pytest infrastructure (fixtures, markers, CI integration)
     - `pytest-playwright` plugin is mature (Microsoft-maintained)
     - Can test real JS execution in Chromium
     - Supports headless mode out of the box
     - Page object model or direct `page.locator()` assertions
   - Cons:
     - ~300MB browser binary download (`playwright install chromium` ~ 1-2 min)
     - Tests are slower (~2-5s per test instead of ms)
     - Flakiness possible with async timing (race conditions)
     - Cannot test visual rendering beyond element existence (no screenshot diff without extra setup)
   - Effort: **Medium** (fixture setup, test DB management, CI config)

2. **Playwright JS/Node** — separate Node.js test runner
   - Install: `npm init -y` + `npm install @playwright/test`
   - Separate `playwright.config.ts` and test files
   - Pros:
     - More idiomatic for JS testing
     - Better debugging tools (trace viewer, VS Code extension)
     - No pytest integration complexity
   - Cons:
     - **Introduces Node.js as a dev dependency** (currently zero JS tooling)
     - Separate CI setup, separate test runs
     - Duplicate CI dependencies (uv for Python, npm for Node)
     - No shared fixtures with pytest (server setup must be duplicated)
     - Project principle: "zero build toolchain" — this breaks it
   - Effort: **Medium-High** (new toolchain, CI duplication, dual lockfiles)

3. **Selenium (`selenium-wire`)** — heavier Playwright alternative
   - Install: `uv add --dev selenium`
   - Uses WebDriver (needs chromedriver on PATH)
   - Lower-level API than Playwright
   - Pros:
     - Well-known, extensive community
     - Works with any browser
   - Cons:
     - **Slower** than Playwright (WebDriver protocol vs CDP)
     - **Flakier** — more timing-related failures
     - Python bindings feel clunky compared to Playwright's async/sync API
     - No official pytest plugin (community `pytest-selenium` is less maintained)
     - Chromedriver adds another binary to manage
   - Effort: **Medium** (similar scope, worse DX)

4. **Cypress** — JavaScript-only E2E runner
   - Pros:
     - Great developer experience (time travel, auto-waiting)
     - Active community
   - Cons:
     - **Node-only** — cannot integrate with pytest
     - Adds ~200MB for Cypress binary
     - Separate CI pipeline entirely
     - Does NOT support Firefox/Chrome on Windows in all configurations
     - Cannot share FastAPI server fixtures
   - Effort: **High** (entirely separate toolchain, CI rethink)

5. **`httpx` + manual DOM parsing** — status quo
   - Pros:
     - Already works, no new dependencies
     - Fast (milliseconds per test)
   - Cons:
     - Does NOT test JavaScript execution
     - Cannot verify `fetch()`, `setData()`, canvas rendering
     - Leaves the spec scenario permanently untested
   - Effort: **None** (but doesn't solve the problem)

### Recommendation

**Use Playwright Python (`pytest-playwright`).** It's the only option that:
1. Stays in the Python ecosystem (project principle: zero JS toolchain)
2. Integrates directly with the existing pytest runner
3. Shares fixtures and server lifecycle with existing tests
4. Requires only `uv add --dev pytest-playwright`
5. Covers the untested spec scenario: JS chart fetch + setData

#### Implementation Design

**FastAPI server management:**

Use a session-scoped fixture in `tests/conftest.py` that:

1. Picks a random available port (or fixed port like 8765)
2. Sets `MARKET_DB_PATH` to a temporary DuckDB with seed data (2-3 bars for symbol "TEST")
3. Spawns `uvicorn app.main:app --host 127.0.0.1 --port {port}` via `subprocess.Popen`
4. Polls `http://127.0.0.1:{port}/health` until 200 (timeout 10s)
5. Yields the base URL to tests
6. Terminates the subprocess on teardown

```python
@pytest.fixture(scope="session")
def e2e_server():
    """Start FastAPI server with test DuckDB for E2E tests."""
    import subprocess, time, socket, os, tempfile, duckdb, urllib.request, urllib.error

    # Find free port
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    # Create temp DuckDB with seed data
    db_fd, db_path = tempfile.mkstemp(suffix=".duckdb")
    os.close(db_fd)
    conn = duckdb.connect(db_path)
    conn.execute("""CREATE TABLE dt_ohlc_m1 (
        datetime TIMESTAMP, symbol VARCHAR, open DOUBLE, high DOUBLE,
        low DOUBLE, close DOUBLE, tickvol BIGINT, volume BIGINT,
        spread INT, origen VARCHAR, fecha_carga TIMESTAMP
    )""")
    dt = datetime.datetime(2024, 1, 1, 9, 30, 0)
    conn.execute("INSERT INTO dt_ohlc_m1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (dt, "TEST", 100.0, 101.0, 99.0, 100.5, 100, 1000, 1, "e2e", dt))
    conn.close()

    env = os.environ.copy()
    env["MARKET_DB_PATH"] = db_path
    proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        env=env
    )

    # Wait for readiness
    url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            urllib.request.urlopen(f"{url}/health")
            break
        except urllib.error.URLError:
            time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError("FastAPI server did not start")

    yield url

    proc.terminate()
    proc.wait()
    os.unlink(db_path)
```

**Test data strategy:**

Create a small in-memory DuckDB with 2-3 bars for symbol "TEST" (mimicking the same pattern `test_market.py` uses). The server process gets `MARKET_DB_PATH` pointing to this temp file so `MarketDatabase.__init__() -> settings.MARKET_DB_PATH` picks it up automatically. No code changes needed.

**Test example:**

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_chart_js_fetches_and_renders(page: Page, e2e_server: str):
    """Chart JS fetches /api/ohlc and renders candlestick series."""
    page.goto(f"{e2e_server}/market/chart?symbol=TEST")
    
    # Wait for the chart canvas to render (Lightweight Charts creates a canvas)
    canvas = page.locator("#chart canvas").first
    expect(canvas).to_be_visible(timeout=10000)
    
    # Verify no console errors
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
    page.goto(f"{e2e_server}/market/chart?symbol=TEST")
    page.wait_for_timeout(2000)
    assert len(console_errors) == 0, f"Console errors: {console_errors}"
```

**CI changes:**

The existing CI job should NOT run E2E tests by default (avoids adding ~2min for every PR). Instead:

Option A: **Separate CI job** (preferred)
```yaml
  e2e:
    name: E2E Tests
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v7
      - run: uv sync
      - run: uv run playwright install chromium
      - run: uv run pytest -m e2e --cov=app --cov-report=term-missing
```

Option B: **Same job, conditional step** — run E2E only on push to main or tagged releases.

Option A is preferred because:
- CI stays fast for PRs (~2min saved per PR)
- E2E failures don't block the quality gate
- Separate concerns: lint+types+tests vs E2E

**pytest markers and configuration:**

```toml
[tool.pytest.ini_options]
markers = [
    "e2e: marks tests that require Playwright + running server (skipped by default)",
]
addopts = [
    "-m", "not e2e",
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]
```

This means `uv run pytest` runs everything EXCEPT E2E. `uv run pytest -m e2e` runs ONLY E2E. `uv run pytest -m "not unit"` runs integration + e2e.

**Makefile additions:**
```makefile
test-e2e:  ## Run E2E tests with Playwright
    uv run playwright install chromium
    uv run pytest -m e2e -v --tb=long

.PHONY: test test-e2e ci
```

#### What changes are needed

| File | Change | Impact |
|------|--------|--------|
| `pyproject.toml` | Add `pytest-playwright` to `[dependency-groups] dev` | Low |
| `pyproject.toml` | Add `e2e` marker, set `-m "not e2e"` in `addopts` | Low |
| `.github/workflows/ci.yml` | Add `e2e` job (chromium install + `-m e2e`) | Medium |
| `Makefile` | Add `test-e2e` target | Low |
| `tests/conftest.py` | Add `e2e_server` session-scoped fixture, `LiveServer` logic | Medium |
| `tests/test_chart_e2e.py` | NEW: Playwright E2E test module | Low-Medium |
| `.gitignore` | Add `playwright/` (browser cache directory) | Low |
| `openspec/config.yaml` | Update `context` to mention E2E capability | Low |

**Total delta:** ~120 lines added, 0 lines modified in app code.

#### What would NOT change

- No app code changes (`chart.js`, `main.py`, `market.py` stay as-is)
- No npm, node_modules, package.json
- Existing pytest behavior unchanged (E2E excluded by default)
- Coverage threshold unaffected (E2E tests use `--cov` but DuckDB data is ephemeral)

#### What can E2E tests actually verify?

| Behavior | Verifiable? | How |
|----------|-------------|-----|
| Page loads without JS errors | ✅ | Listen to `console` events, assert no errors |
| `fetch()` to `/api/ohlc` fires | ✅ | Mock/route intercept `page.route("**/api/ohlc**")` or check network tab |
| `setData()` completes | ⚠️ Partial | Canvas renders with candles after fetch (no JS error implies success) |
| Candles visible on chart | ✅ | Wait for `#chart canvas` + check `canvas.getAttribute("height") > 0` |
| Form submit re-fetches | ✅ | Intercept API route, change form value, submit, verify new request |
| CDN loads Lightweight Charts | ⚠️ Indirect | Script tag present, no 404s in network log |
| Visual regression (candles look right) | ❌ | Would need screenshot comparison (separate feature) |

### Risks

1. **CI Windows + Playwright compatibility**: Playwright on `windows-latest` runners is well supported, but browser downloads can timeout in constrained CI network environments. Mitigation: add a timeout and retry in CI setup.

2. **Test flakiness**: Network timing, async JS, canvas rendering race conditions can cause intermittent failures. Mitigation: use `expect().to_be_visible(timeout=10000)` (auto-waiting) rather than raw `page.wait_for_timeout()`. Add `@pytest.mark.flaky(reruns=2)` if needed.

3. **Port conflicts**: If a dev server is already running on the chosen port, the fixture fails. Mitigation: use OS-assigned port (port 0) via socket bind-and-release pattern.

4. **Temp DB cleanup**: If the test process crashes, the temp DuckDB file may be orphaned. Mitigation: register `atexit` cleanup in fixture or use `tempfile` with `delete=True` where possible.

5. **Browser cache in CI**: `playwright install chromium` downloads ~300MB every run. Mitigation: add GitHub Actions cache for `~/.cache/ms-playwright` or the Windows equivalent.

6. **Coverage reporting**: E2E tests run against a subprocess server, so `--cov` may not capture coverage from route handlers. Mitigation: for E2E, coverage can be skipped (`--no-cov`) or use `--cov-append` with a separate `.coverage.e2e` file.

### Ready for Proposal

**Yes** — this exploration is conclusive. The path is clear:

1. **Adopt `pytest-playwright`** (Python bindings, not Node.js)
2. **Separate CI job** for E2E (`e2e` job, not part of main `quality-gate`)
3. **Session-scoped server fixture** with temp DuckDB
4. **`@pytest.mark.e2e`** — excluded from default `uv run pytest`
5. **3-5 initial tests**: page loads cleanly, fetch fires, candles render, form submit re-fetches

The orchestrator should proceed to `sdd-propose` to formalize scope, then `sdd-spec` for the spec scenarios, `sdd-design` for fixture architecture, `sdd-tasks` for implementation breakdown, and `sdd-apply` for code changes.
