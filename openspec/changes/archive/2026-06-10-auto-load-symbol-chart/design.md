# Design: Auto-Load Symbol Chart

## Technical Approach

Replace the form submit interaction model with individual `change` event listeners on each chart control. When any control changes, read all form values and call the existing `loadData()`. Remove the submit button and its handler. No backend changes — the API endpoint and `loadData()/buildUrl()` remain untouched.

## Architecture Decisions

### Decision: `change` vs `input` event

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `change` | Fires once on user commit — picker close, option selected | ✅ **Chosen** |
| `input` | Fires on every keystroke and intermediate select navigation | Rejected — excessive fetches |

**Rationale**: `change` fires once per user action. On `<select>` when the user picks an option, on `<input type="date">` when the date picker closes. `input` would fire on every keyboard arrow press inside a select — wasteful and potentially race-prone.

### Decision: Individual listeners vs delegated listener

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Individual listener per control | Explicit, easy to read/debug, easy to exclude one control later | ✅ **Chosen** |
| Single delegated listener on `<form>` | Less code, event filtering required | Rejected — harder to modify per-control behavior |

**Rationale**: Both work. Individual listeners are more explicit — each reads the full form state and calls `loadData()`. No performance concern with 4 listeners. Easier to evolve (e.g., if one day a control should NOT trigger reload).

### Decision: No debounce

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Fire immediately | No delay, instant feedback | ✅ **Chosen** |
| Debounce 300ms | Unnecessary latency, no rapid-fire scenario exists | Rejected |

**Rationale**: `change` does not fire rapidly. `<select>` fires once per user choice (not on keyboard cycling). `<input type="date">` fires on picker close. No debounce needed.

## Data Flow

```
User changes control (select/date)
        │
        ▼
Control fires "change" event
        │
        ▼
Listener reads all form values: symbol, timeframe, start, end, limit
        │
        ▼
loadData(sym, tf, lim, st, en)
        │
        ▼
buildUrl() ──→ fetch /api/ohlc?... ──→ series.setData(data) ──→ chart.timeScale().fitContent()
```

Same flow regardless of which control triggered it — all listeners read the full form state identically.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `static/js/chart.js` | Modify | Replace submit handler with `change` listeners on `[name=symbol]`, `[name=timeframe]`, `[name=start]`, `[name=end]` |
| `templates/market/chart.html` | Modify | Remove `<button type="submit">Load</button>` (line 32) |
| `static/css/app.css` | Modify | Remove `#chart-controls button` block (lines 337–339) — rule only set `margin-bottom: 0` which is already covered by the flex layout |
| `tests/test_chart_e2e.py` | Modify | `test_date_form_updates_chart`: fill dates via `fill()`, dispatch `change` event on each input; remove button click |

## Interfaces / Contracts

No new interfaces. The existing function signatures remain unchanged:

```js
function loadData(sym, tf, lim, st, en)  // unchanged
function buildUrl(sym, tf, lim, st, en)   // unchanged
```

Form control `name` attributes (`symbol`, `timeframe`, `start`, `end`, `limit`) remain stable — all listeners read them dynamically.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | N/A | Pure event wiring — no new testable logic surface |
| Integration | API endpoint | Existing `test_ohlc*.py` — no changes needed (API untouched) |
| E2E | Chart reloads on date change | Update `test_date_form_updates_chart`: `fill()` dates, then `locator.evaluate(el => el.dispatchEvent(new Event('change', {bubbles: true})))` on each input |

The `test_chart_page_loads`, `test_symbol_selector_populated`, `test_unknown_symbol_shows_no_data`, `test_chart_defaults_to_last_200`, `test_tooltip_shows_tickvol_and_spread`, and theme tests are unaffected — they don't interact with the submit button.

## Migration / Rollout

No migration required. Deploy JS, template, and CSS changes atomically. Purely client-side — no data migration, no feature flags, no server changes.

## Open Questions

None — all design decisions resolved.
