# Proposal: Auto-Load Symbol Chart

## Intent

Remove the Load button from `/market/chart`. All chart controls (symbol, timeframe, date range) auto-trigger `loadData()` on `change` event, eliminating a redundant click from the user workflow.

## Scope

### In Scope
- Add `change` event listeners on symbol `<select>`, timeframe `<select>`, and date `<input>` elements in `chart.js`
- Remove the `<button type="submit">Load</button>` from `chart.html`
- Remove the submit event handler from `chart.js`
- Remove isolated `#chart-controls button` CSS rule from `app.css`
- Update `test_date_form_updates_chart` in E2E tests to use `select_option()` instead of button click

### Out of Scope
- Debounce (not needed — `<select>` fires `change` once per user action; date inputs fire on picker close)
- HTMX rewrite (chart is JS-only with Lightweight Charts; no server-side rendering change)
- Server-side changes (API endpoint unchanged)
- Multi-timeframe aggregation (pre-existing, not part of this change)
- The `<form>` element itself (left in place; harmless without submit button)

## Capabilities

### New Capabilities
None — this modifies existing `market-chart` behavior only.

### Modified Capabilities
- `market-chart`: Chart controls auto-trigger data loading on any `change` event; Load button removed

## Approach

Pure JS `change` event listeners on all `#chart-controls` form controls. Each listener reads current form values and calls the existing `loadData()` function. Remove the submit handler and the Load button. The `loadData()` function already handles URL construction and fetch — no logic change needed.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `static/js/chart.js` | Modified | Add `change` listeners on controls; remove submit handler |
| `templates/market/chart.html` | Modified | Remove `<button type="submit">Load</button>` (line 32) |
| `static/css/app.css` | Modified | Remove `#chart-controls button` rule (lines 337–339) |
| `tests/test_chart_e2e.py` | Modified | Replace `button.click()` with `select_option()` in `test_date_form_updates_chart` (line 31) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| E2E test fails with button removed | Low | Update test to trigger via `select_option()` which fires a native `change` event |
| Date input `change` event varies by browser | Low | Standard `<input type="date">` fires `change` on user commit across all modern browsers |

## Rollback Plan

Revert `chart.js` to restore submit handler and remove change listeners. Re-add `<button>` to template. Revert CSS. Revert test. No data or API changes — purely client-side.

## Dependencies

None.

## Success Criteria

- [ ] Selecting a different symbol reloads the chart immediately
- [ ] Changing date range reloads the chart immediately
- [ ] Changing timeframe reloads the chart immediately
- [ ] Load button is no longer present in the template
- [ ] All existing E2E tests pass
- [ ] Coverage >= 80%
