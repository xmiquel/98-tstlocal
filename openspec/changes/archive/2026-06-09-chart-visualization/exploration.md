## Exploration: Chart Visualization Improvements

### Current State

The codebase is significantly AHEAD of the stated assumptions. Both features are already largely implemented:

**Time scale formatting:** Already present in `static/js/chart.js` lines 22-25:
```js
timeScale: {
    timeVisible: true,
    secondsVisible: false,
},
```
Lightweight Charts handles the intraday/daily distinction automatically — `timeVisible` shows HH:MM for intraday timeframes, and the chart suppresses time for daily data. No additional work needed.

**Custom tooltip:** The full implementation exists:
- **HTML**: `<div id="chart-tooltip">` is inside the `position: relative` chart container in `templates/market/chart.html` (line 36)
- **JS**: Complete crosshair subscription in `chart.js` lines 31-91:
  - Hides/shows tooltip based on crosshair presence
  - Extracts OHLCV + spread from `param.seriesData.get(series)`
  - Renders formatted HTML with date, O, H, L, C, V, Spr values
  - Positions tooltip near crosshair with boundary clamping (flips to left side if near right edge)
  - Handles both object-based and timestamp-based time formats
- **CSS**: **MISSING** — `static/css/app.css` has zero tooltip styles

The only actual gap is CSS styling for the tooltip. Without it, the tooltip:
- Has no `position: absolute` — JS `left`/`top` values are ineffective
- Has no `display: none` initially — always visible
- Has no background, color, padding, border, shadow, or z-index
- Has no `pointer-events: none` — interferes with chart interaction
- Has no font size or text styling

### Affected Areas

| File | Status | Impact |
|------|--------|--------|
| `static/js/chart.js` | **Complete** | No changes needed |
| `templates/market/chart.html` | **Complete** | No changes needed |
| `static/css/app.css` | **Missing tooltip CSS** | ~30 lines needed |
| `openspec/config.yaml` | **Out of date** | Describes "no source code" — project has evolved |

### Approaches

1. **Add tooltip CSS only** (recommended)
   - Add ~30 lines of CSS to `static/css/app.css` for `#chart-tooltip` and `.tt-*` classes
   - Dark theme styling matched to current chart colors (#131722 bg, #d1d4dc text)
   - Pros: Minimum diff, zero risk, full feature completion
   - Cons: None
   - Effort: **Low** (~15 minutes)

2. **Rewrite tooltip as a Lightweight Charts plugin**
   - Create a plugin extending the chart's plugin API
   - Pros: More idiomatic for LC v4, reusable
   - Cons: Overkill for a single tooltip, larger diff, requires understanding plugin lifecycle
   - Effort: **Medium** (more complex than justified)

3. **HTML overlay with pointer-events (current approach already uses this)**
   - The current implementation already uses this pattern — `position: relative` container + `absolute` positioned div
   - No changes needed to approach; just needs CSS to activate it
   - Effort: Already implemented

### Recommendation

**Approach 1 — Add tooltip CSS only.** The JS and HTML are already complete and correct. The only real work is adding the CSS that makes the tooltip visible and styled. This is a trivial addition:

```css
/* ── Chart Tooltip ─────────────────────────────────────────── */
#chart-tooltip {
    display: none;
    position: absolute;
    z-index: 100;
    pointer-events: none;
    background: #1e222d;
    border: 1px solid #2a2e39;
    border-radius: 6px;
    padding: 8px 12px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    font-size: 12px;
    line-height: 1.5;
    color: #d1d4dc;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    min-width: 140px;
}
.tt-time {
    font-size: 11px;
    color: #787b86;
    margin-bottom: 4px;
    padding-bottom: 4px;
    border-bottom: 1px solid #2a2e39;
}
.tt-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
}
.tt-label {
    color: #787b86;
}
.tt-val-o { color: #089981; }
.tt-val-h { color: #d1d4dc; }
.tt-val-l { color: #d1d4dc; }
.tt-val-c { color: #089981; }
```

Also, `openspec/config.yaml` should be updated — it currently states "no source code, no test runner" which is stale (project has evolved significantly since init).

### Risks

- **None** for the tooltip CSS addition — purely additive, no behavior changes
- **Stale config**: `openspec/config.yaml` misrepresenting the project state could confuse future SDD phases or new contributors

### Ready for Proposal

**Yes.** The work is clearly scoped — the exploration reveals that what was thought to be missing is actually already implemented. The only deliverable is a ~30-line CSS addition.

The proposal should clarify:
1. Only CSS needs writing
2. The JS and HTML are already complete and working
3. The `openspec/config.yaml` also needs updating to reflect current project state
