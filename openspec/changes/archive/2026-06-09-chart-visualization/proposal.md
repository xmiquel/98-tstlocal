# Proposal: Chart Visualization

## Intent

Add OHLCV + Spread tooltip on crosshair hover and time scale formatting to the candlestick chart. Per exploration, JS and HTML are already complete on disk — the only remaining work is ~30 lines of tooltip CSS in `static/css/app.css`.

## Scope

### In Scope
- Add tooltip CSS (~30 lines) to `static/css/app.css` — `#chart-tooltip` and `.tt-*` classes
- Update `openspec/config.yaml` to reflect current project state (stale "no source code" description)

### Out of Scope
- Visual regression testing — deferred
- Lightweight Charts version upgrade — out of scope
- Any JS or HTML template changes — already complete, zero changes needed

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `market-chart`: Add tooltip visibility, dark-theme positioning styling, and time scale formatting (`timeVisible: true` / `secondsVisible: false`)

## Approach

Add ~30 lines of CSS to `static/css/app.css` for `#chart-tooltip` and `.tt-*` classes. Dark theme matching the chart's existing palette (#131722 bg, #d1d4dc text, #2a2e39 borders). CSS handles: initial `display: none`, `position: absolute` for JS positioning, `pointer-events: none` for chart passthrough, background/color/padding/border/shadow for readability.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `static/css/app.css` | Modified | Add ~30 lines tooltip + time-scale CSS |
| `openspec/config.yaml` | Modified | Update stale project context |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| None — purely additive CSS | N/A | Zero behavior change, no runtime risk |

## Rollback Plan

Revert the single commit touching `static/css/app.css` and `openspec/config.yaml`. No database, schema, or behavioral changes — instant revert.

## Dependencies

None.

## Success Criteria

- [ ] Crosshair hover shows a styled tooltip with OHLCV + Spread values
- [ ] Tooltip hidden when no crosshair is active
- [ ] Tooltip positions correctly near crosshair with boundary clamping
- [ ] Tooltip has dark theme matching the chart (#131722 / #d1d4dc)
