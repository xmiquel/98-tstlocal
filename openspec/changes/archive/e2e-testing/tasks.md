# Tasks: E2E Testing for JS Chart Runtime

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~160 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | E2E infra + tests | PR 1 | Single PR; all changes are dev-tooling only |

## Phase 1: Foundation

- [x] 1.1 Add `pytest-playwright` dev dependency to `pyproject.toml`
- [x] 1.2 Add `e2e` marker config + `-m "not e2e"` default to `pyproject.toml`
- [x] 1.3 Run `uv run playwright install chromium`

## Phase 2: Fixtures

- [x] 2.1 Add session-scoped `e2e_server` fixture in `tests/conftest.py` (subprocess uvicorn + temp DuckDB on random port)

## Phase 3: Tests

- [x] 3.1 Create `tests/test_chart_e2e.py` with 5 tests: page loads, candles render, symbol select, form submit, empty data
- [x] 3.2 Run and fix: `uv run pytest -m e2e -v`

## Phase 4: CI + Makefile

- [x] 4.1 Add separate `e2e` job to `.github/workflows/ci.yml` with browser cache
- [x] 4.2 Add `test-e2e` target to `Makefile`
- [x] 4.3 Add `playwright/` cache dir to `.gitignore`

## Phase 5: Verify

- [x] 5.1 Run `uv run pytest` — confirm e2e tests are skipped
- [x] 5.2 Run `uv run pytest -m e2e` — confirm only e2e tests run
- [x] 5.3 Run `ruff check . && ruff format --check . && mypy .`
