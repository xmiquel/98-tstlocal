# Tasks: Auto-Load Symbol Chart

## Review Workload Forecast

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

Estimated changed lines: ~15–25. Tiny, focused client-side change. No chain needed — single PR.

## Phase 1: Update E2E Test (RED)

- [x] 1.1 `tests/test_chart_e2e.py` — In `test_date_form_updates_chart`, replace `button.click()` with `fill()` dates + `evaluate()` to dispatch `change` event on each date input; remove button locator

## Phase 2: Core Implementation (GREEN)

- [x] 2.1 `static/js/chart.js` — Replace `submit` handler on `#chart-controls` (lines 146–157) with individual `change` listeners on `[name=symbol]`, `[name=timeframe]`, `[name=start]`, `[name=end]`; each listener reads all form values and calls `loadData()`
- [x] 2.2 `templates/market/chart.html` — Remove `<button type="submit">Load</button>` (line 32)
- [x] 2.3 `static/css/app.css` — Remove `#chart-controls button` rule block (lines 337–339)

## Phase 3: Verification

- [x] 3.1 Run E2E tests: `uv run pytest tests/test_chart_e2e.py -v --e2e` — all pass
- [x] 3.2 Run `make ci` — full quality gate passes
