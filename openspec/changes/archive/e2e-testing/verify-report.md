# SDD Verify Report — e2e-testing

**Change**: e2e-testing
**Version**: N/A (testing infrastructure — no capability specs)
**Mode**: Strict TDD

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 15 |
| Tasks complete | 15 |
| Tasks incomplete | 0 |

All 15 tasks from the tasks artifact are marked complete.

## Build & Tests Execution

### Standard Tests (non-e2e)

**Build / Format**: ✅ Passed

```text
uv run ruff check .  → All checks passed!
uv run ruff format --check .  → 18 files already formatted
uv run mypy .  → Success: no issues found in 18 source files
```

**Tests**: ✅ 57 passed, 5 deselected (e2e)

```text
uv run pytest
collected 62 items / 5 deselected / 57 selected
57 passed, 5 deselected in 2.21s
```

**Coverage**: 84% (threshold: 80%) → ✅ Above

```
TOTAL               275     44    84%
Required test coverage of 80% reached. Total coverage: 84.00%
```

### E2E Tests

**Tests**: ❌ 5 errors — ALL E2E tests fail at fixture setup

```text
uv run pytest -m e2e -v
collected 62 items / 57 deselected / 5 selected

tests/test_chart_e2e.py::test_chart_page_loads[chromium] ERROR
tests/test_chart_e2e.py::test_symbol_selector_populated[chromium] ERROR
tests/test_chart_e2e.py::test_date_form_updates_chart[chromium] ERROR
tests/test_chart_e2e.py::test_unknown_symbol_shows_no_data[chromium] ERROR
tests/test_chart_e2e.py::test_chart_defaults_to_last_200[chromium] ERROR

ERROR: Coverage failure: total of 44 is less than fail-under=80
```

**Root cause**: `tempfile.NamedTemporaryFile(delete=False)` in `e2e_server` fixture creates a zero-byte file. `duckdb.connect()` cannot open an existing zero-byte file as a database — it throws `IOException: The file exists, but it is not a valid DuckDB database file!`.

**Fix**: Add `os.unlink(tmp_db)` between `NamedTemporaryFile(delete=False)` and `MarketDatabase(db_path=tmp_db)` — this removes the empty stub so DuckDB creates a fresh database.

**Coverage skew note**: The `84%` coverage threshold cannot be met in `-m e2e` mode because `pytest-cov` measures coverage in the test process, but the actual application code runs in a uvicorn subprocess. The `addopts` in `pyproject.toml` blanket-applies `--cov-fail-under=80` to all pytest runs, which will always fail for `-m e2e`. Consider adding a `pytest.ini` override or a separate `--override-ini` flag for e2e runs.

## Spec Compliance Matrix

Skipped — no capability specs for this change (testing infrastructure only).

## Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Add pytest-playwright dev dep | ✅ Implemented | `pyproject.toml` includes `pytest-playwright>=0.8.0` |
| e2e marker + -m "not e2e" default | ✅ Implemented | `pyproject.toml` has `[tool.pytest.ini_options]` with marker and addopts |
| Run playwright install chromium | ✅ Implemented | Part of CI e2e job, must be run manually for local dev |
| Session-scoped e2e_server fixture | ✅ Implemented | `tests/conftest.py` has `e2e_server` with subprocess uvicorn + temp DuckDB |
| 5 E2E test scenarios | ✅ Implemented | `tests/test_chart_e2e.py` has 5 tests (page_loads, symbol_selector, date_form, unknown_symbol, defaults) |
| Separate CI e2e job | ✅ Implemented | `.github/workflows/ci.yml` has e2e job with browser cache |
| test-e2e Makefile target | ✅ Implemented | `Makefile` has `test-e2e` target |
| playwright/ in .gitignore | ✅ Implemented | `.gitignore` has `ms-playwright/` and `playwright/` entries |
| Template script ordering fix | ✅ Implemented | `__chartConfig` (line 29) is defined before `chart.js` (line 37) |

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Server fixture: subprocess.Popen(["uv", "run", "uvicorn", ...]) on random port | ✅ Yes | `tests/conftest.py` uses `subprocess.Popen(["uv", "run", "uvicorn", ...])` with `socket.bind(("", 0))` for random port |
| Test data: temp DuckDB via NamedTemporaryFile, 3 bars for TEST | ⚠️ Partial | Code uses `NamedTemporaryFile(delete=False)`, but the zero-byte stub file causes DuckDB to fail. The design intended a valid temp file — the implementation creates an unusable one. |
| CI structure: separate e2e job | ✅ Yes | `.github/workflows/ci.yml` has `e2e` job with `needs: quality-gate` |
| Test selection: @pytest.mark.e2e with default -m "not e2e" | ✅ Yes | Works correctly — 57/62 tests run by default, 5 deselected |
| 5 testing scenarios matching design | ✅ Yes | All 5 design scenarios have corresponding test functions |

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in apply-progress (obs #124) |
| All tasks have tests | ⚠️ | 7 of 15 tasks are structural (no test file needed) — plausible. 2 test files for the remaining 8 tasks: `tests/conftest.py` (fixture) + `tests/test_chart_e2e.py` (tests) |
| RED confirmed (tests exist) | ✅ | Test files exist: `tests/conftest.py` and `tests/test_chart_e2e.py` |
| GREEN confirmed (tests pass) | ❌ | 0/5 E2E tests pass on execution — GREEN column in apply-progress claims "✅ All 5 pass" but they all error out |
| Triangulation adequate | ✅ | 5 test cases covering 5 design scenarios — adequate per the design |
| Safety Net for modified files | ⚠️ | Safety net shows "✅ 57/57" for pre-existing tests, but the existing test count when applying was 57 — this appears accurate for the non-e2e test suite |

**TDD Compliance**: 4/6 checks passed — 1 failure (GREEN), 1 warning (Safety Net)

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 57 (pre-existing) | 7 files | pytest |
| Integration | Mixed with unit | Same files | pytest + pytest-cov |
| E2E | 5 | 1 file (`tests/test_chart_e2e.py`) | playwright, pytest-playwright |
| **Total** | **62** | **8+** | |

### Changed File Coverage

Coverage analysis is not meaningful for E2E tests because the app code runs in a uvicorn subprocess, not the test process. The coverage reported by `pytest-cov` for `-m e2e` runs reflects only the code executed in the test process (mostly fixture setup), not the actual app behavior.

For the standard (non-e2e) test suite, coverage is **84%** overall, above the 80% threshold.

### Assertion Quality

| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `tests/test_chart_e2e.py` | 50 | `assert "limit" not in current or "symbol=" in current` | Weak logical assertion — `or` clause means the test passes if "symbol=" is present regardless of "limit" | WARNING |

**Assertion quality**: 0 CRITICAL, 1 WARNING — overall good quality. No tautologies, ghost loops, or type-only assertions.

### Quality Metrics

**Linter**: ✅ No errors
**Type Checker**: ✅ No errors

## Issues Found

### CRITICAL

1. **E2E tests all fail** — `e2e_server` fixture crashes with DuckDB `IOException` because `NamedTemporaryFile(delete=False)` creates a zero-byte stub file that DuckDB refuses to open. This affects ALL 5 E2E tests (test_chart_page_loads, test_symbol_selector_populated, test_date_form_updates_chart, test_unknown_symbol_shows_no_data, test_chart_defaults_to_last_200).

2. **TDD GREEN claim is false** — The apply-progress TDD Cycle Evidence table claims "✅ All 5 pass" for task 3.2, but current execution shows 0/5 passing.

3. **Coverage failure on e2e run** — `-m e2e` runs hit `--cov-fail-under=80` (44% coverage) because `pytest-cov` cannot measure code running in a uvicorn subprocess. This blocks `make ci` from including e2e tests.

### WARNING

1. **Weak assertion in test_chart_defaults_to_last_200** — `assert "limit" not in current or "symbol=" in current` uses `or` logic that can pass vacuously if "symbol=" appears in the URL regardless of "limit". This test may not meaningfully verify the default URL behavior.

### SUGGESTION

1. Consider overriding or disabling `--cov-fail-under` for E2E test runs (e.g., `uv run pytest -m e2e -v --override-ini="cov-fail-under=0"` or use a separate pytest config file).

## Verdict

**FAIL**

CRITICAL issues found: E2E tests do not execute — 5/5 error at fixture setup due to DuckDB temp file bug. The implementation must be fixed before the change can be verified. Additionally, the coverage threshold blocks automated E2E runs.

**Fix required**: Add `os.unlink(tmp_db)` to `tests/conftest.py` between lines 51 and 52 to remove the empty temp stub before creating the DuckDB database.
