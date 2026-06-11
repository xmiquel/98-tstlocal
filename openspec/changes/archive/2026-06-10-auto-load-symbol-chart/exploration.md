## Exploration: auto-load-symbol-chart

### Current State

The chart page (`/market/chart`) works through a combination of server-rendered HTML and client-side JavaScript:

1. **Template** (`templates/market/chart.html`): Renders a `<form id="chart-controls">` with a symbol `<select>`, date `<input>` fields, a timeframe `<select>`, a hidden `limit` field, and a `<button type="submit">Load</button>`. On the server side, `GET /market/chart` accepts query parameters and passes them as `window.__chartConfig` via an inline `<script>` block.

2. **Chart JS** (`static/js/chart.js`): On page load, creates a `LightweightCharts` instance and calls `loadData()` using config from the server. The `loadData()` function builds a URL from parameters, fetches `GET /api/ohlc`, and calls `series.setData(data)`. A form submit listener (`#chart-controls` submit) calls `e.preventDefault()`, reads form values, and calls `loadData()` — bypassing the native form GET navigation entirely.

3. **API** (`GET /api/ohlc`): Accepts `symbol` (required), `timeframe`, `limit`, `start`, `end`. Returns a JSON array of bars with keys `time`, `open`, `high`, `low`, `close`, `tickvol`, `spread`.

4. **HTMX**: Loaded globally in `base.html` but **not used** on the chart page — the chart uses pure JS + `fetch()`.

5. **E2E tests** (`test_chart_e2e.py`): `test_date_form_updates_chart` clicks `button[type="submit"]` to trigger a chart update. If the button is removed, this test needs updating.

### Affected Areas

- `templates/market/chart.html` — The `<button type="submit">Load</button>` line (line 32) and the form's `method="get"` need updating/removal
- `static/js/chart.js` — Add `change` event listeners to the symbol `<select>` (and optionally timeframe/date inputs) to auto-trigger `loadData()`
- `tests/test_chart_e2e.py` — `test_date_form_updates_chart` clicks the submit button; needs a replacement trigger strategy (JS change event or keep button hidden)
- `openspec/specs/market-chart/spec.md` — Would need a new or modified requirement for auto-load behavior
- `static/css/app.css` — Minor: the `#chart-controls button` style block (lines 337-339) could be removed if the button goes away

### Approaches

1. **Pure JS `change` listeners on all controls** — Add `change` event listeners to the symbol `<select>`, timeframe `<select>`, and date `<input>` elements. Each listener reads all form values and calls `loadData()`. Remove the Load button from the template.
   - Pros: Minimal change (only JS + template); leverages existing `loadData()` function; all controls auto-trigger; HTMX not needed; button truly eliminated
   - Cons: E2E test needs updating; date change fires only on user commit (change event), not on every keystroke (which is actually correct UX)
   - Effort: Low

2. **JS `change` listener on symbol select only** — Add a `change` listener only to the symbol `<select>`. Keep the Load button for date/timeframe changes. Don't touch other controls.
   - Pros: Even smaller change; existing tests pass unchanged (still a submit button)
   - Cons: Load button stays; user still needs to click for date/timeframe changes; user asked for button removal
   - Effort: Low

3. **HTMX approach** — Add `hx-get="/api/ohlc"` with `hx-trigger="change"` to the symbol select, changing the chart to render server-side via HTMX swap.
   - Pros: Leverages HTMX already loaded in base.html
   - Cons: Fundamental architecture change (chart is JS-rendered, not HTML); Lightweight Charts is a JS library; would require rewriting the rendering pipeline; massive scope; not worth it
   - Effort: High

### Recommendation

**Approach 1 (Pure JS on all controls)** wins. The current architecture already uses `fetch()` + JS rendering. Adding `change` listeners to all form controls (symbol, timeframe, date inputs) is a natural extension of the existing pattern. The `loadData()` function already exists and works perfectly — we just need more triggers. The Load button becomes truly unnecessary and can be removed cleanly.

Implementation sketch:
- In `chart.js`, add individual `change` event listeners to the symbol select, timeframe select, and date inputs (or a single delegated listener on the form for all `change` events).
- Each listener reads all form field values and calls `loadData()` — exactly the same logic the submit handler uses.
- Remove the submit handler entirely since `change` on the inputs replaces it.
- Remove the `<button type="submit">Load</button>` from the template.
- Update the E2E test to trigger via Playwright's `select_option()` (which fires `change`) instead of clicking the button.

### Risks

- **Date input `change` vs `input`**: `<input type="date">` fires `change` when the user picks a date and closes the picker — correct behavior. `input` would fire on every keystroke in a manual date entry, which would cause excessive API calls. Using `change` is correct.
- **E2E test maintenance**: `test_date_form_updates_chart` must be updated. Low risk — trivial change.
- **Rapid symbol switching**: If the user rapidly changes symbols (e.g., keyboard arrow keys), multiple `change` events fire in sequence. The `loadData()` function does not debounce or cancel in-flight requests. This is a pre-existing concern (the submit handler has the same issue). Not new risk, but worth noting.
- **Existing spec alignment**: The current market-chart spec has a scenario "Chart JS loads from the API on init" which describes initial load. The auto-load behavior would need a new requirement. The out-of-scope section lists "Multi-timeframe aggregation" — which is now implemented (the code has a full `INTERVAL_MAP` and aggregation logic). The spec seems outdated in that regard.

### Ready for Proposal

Yes — the change is well-defined, low effort, low risk, and the approach is straightforward. Clear to proceed to sdd-propose.
