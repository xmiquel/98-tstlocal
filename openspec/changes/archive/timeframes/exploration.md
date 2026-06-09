## Exploration: Multi-Timeframe Aggregation for OHLC Endpoint

### Current State

The system serves `GET /api/ohlc` which queries `dt_ohlc_m1` directly — no aggregation. The `timeframe` parameter is accepted but ignored (`# noqa: ARG002 — accepted for future compat`). Only `1m` works. The response returns `{time, open, high, low, close, volume}` per bar. The frontend has a hidden `<input name="timeframe">` and never exposes it to the user.

**Data source**: Single table `dt_ohlc_m1` with 1-minute OHLCV bars. The table has columns: `datetime, symbol, open, high, low, close, tickvol, volume, spread, origen, fecha_carga`.

**Existing draft query pattern** (limit mode):
```sql
SELECT datetime, open, high, low, close, volume
FROM dt_ohlc_m1 WHERE symbol = ?
ORDER BY datetime DESC LIMIT ?
```

### Affected Areas

- `app/market.py` — `query_ohlc()` needs the aggregation logic; `timeframe` parameter activated
- `app/main.py` — `GET /api/ohlc` route — may need `spread` in response; no structural changes
- `app/main.py` — `GET /market/chart` route — expose timeframe in form, pass to template
- `templates/market/chart.html` — replace hidden `timeframe` input with visible `<select>`
- `static/js/chart.js` — `buildUrl()` already includes `timeframe`; form submit handler already reads `[name=timeframe]` — JS is already ready, just needs the `<select>` in the DOM
- `tests/test_market.py` — add tests for aggregation queries (5m, 1h, 1d) and `spread` field
- `openspec/specs/market-chart/spec.md` — update to remove "only 1m implemented" caveat, add timeframe requirement
- `openspec/specs/trading-domain/spec.md` — update OHLCV Query requirement to include aggregation

### Key Finding: DuckDB `date_bin` Does NOT Exist

DuckDB **1.5.3** does not have `date_bin()`. The user's original assumption needs correction. Two alternatives work:

| Function | Syntax | Works with params? | Notes |
|----------|--------|-------------------|-------|
| `time_bucket(INTERVAL, ts)` | `time_bucket(INTERVAL '5 minutes', datetime)` | `CAST(? AS INTERVAL)` works | Native function, aligns to wall-clock boundaries — correct for trading timeframes |
| Epoch math | `TIMESTAMP '1970-01-01' + INTERVAL (epoch(ts) / N * N) SECOND` | Yes (N computed from param) | Slightly more portable, equivalent performance, more verbose |

**Recommendation**: Use `time_bucket()` — it's the canonical DuckDB function, cleaner SQL, and performance is identical to epoch math.

**Performance verified** (3.4M synthetic rows):
- 1d aggregation: **46ms**
- 1h aggregation: **50ms** (more buckets returned)
- Raw query (no aggregation, 200 rows): **~2ms**
- `time_bucket` vs epoch math: neck-and-neck (~4ms avg on 10K rows, 100 runs)

DuckDB handles this trivially. No indexing needed for aggregation queries on this scale.

### Approaches

1. **`time_bucket` with interval map** (RECOMMENDED)
   - Map timeframe strings to DuckDB interval strings via a dict
   - `1m` → direct query (no aggregation, no `time_bucket` call)
   - `5m` → `time_bucket(CAST(? AS INTERVAL), datetime)` with interval `'5 minutes'`
   - `15m` → `'15 minutes'`, `30m` → `'30 minutes'`, `1h` → `'1 hour'`, `4h` → `'4 hours'`, `1d` → `'1 day'`
   - Uses `first(open ORDER BY datetime)`, `max(high)`, `min(low)`, `last(close ORDER BY datetime)`, `sum(volume)`, `first(spread ORDER BY datetime)`
   - Add `spread` to response dict (new key, non-breaking)
   - Frontend: dropdown with timeframe options, JS already compatible

   - **Pros**: Clean SQL, uses native DuckDB function, wall-clock-aligned buckets, trivial performance
   - **Cons**: Depends on `time_bucket` (available since DuckDB 0.10+), interval string mapping needed
   - **Effort**: Low — ~3 files backend (market.py, tests, spec updates), ~2 files frontend (template, JS)
   - **Backward compatibility**: Fully compatible — existing API consumers see no breaking changes; new `spread` key is additive
   - **Performance**: ~46-50ms for 3.4M rows even at 1h/1d aggregation; sub-ms overhead vs raw query

2. **Epoch math approach**
   - Replace `time_bucket` with `TIMESTAMP '1970-01-01' + INTERVAL (CAST(epoch(datetime) / ? AS BIGINT) * ?) SECOND`
   - Same aggregation functions, same interval mapping
   - Compute bucket width in seconds from the timeframe string

   - **Pros**: Works on any DuckDB version (no `time_bucket` requirement), same performance
   - **Cons**: More verbose SQL, harder to read, epoch math is a hack
   - **Effort**: Low (same as approach 1, different SQL)
   - **Performance**: Identical to approach 1

### Recommendation

**Approach 1 — `time_bucket` with interval map.** Here's why:

1. **`time_bucket` is the canonical function** — it's what DuckDB developers would expect. Epoch math is clever but unnecessary complexity.
2. **Performance is identical** — the query planner optimizes both equally.
3. **The code is cleaner** — `WHERE symbol=? AND time_bucket(...)=?` reads naturally.
4. **Alignment is correct** — `time_bucket(INTERVAL '1 hour', ts)` aligns to wall-clock hours (00:00, 01:00, ...) which is what traders expect. Epoch math can produce different alignments for non-divisible intervals (e.g., 4h buckets), though in practice for these intervals both align identically.

**Key design decisions:**

**a) `time_bucket` WITHOUT explicit origin**: The default origin is `2000-01-01` which aligns to wall-clock boundaries. This gives us the expected candle boundaries: 5-minute candles at `00:00, 00:05, 00:10, ...`, 1-hour candles at `00:00, 01:00, ...`, 1-day candles at midnight. No origin parameter needed.

**b) `1m` stays as direct query**: No `time_bucket` call. No GROUP BY overhead. The user explicitly asked for this — it's the right call since it avoids unnecessary aggregation overhead for the native timeframe.

**c) Include `spread` in the response**: The data has it, the user's aggregation query includes it, and adding it is a non-breaking backward-compatible change. Lightweight Charts won't render it but API consumers benefit from having it available.

**d) `LIMIT` after aggregation**: The user explicitly specified this. The subquery approach is:
```sql
SELECT bucket, open, high, low, close, volume, spread
FROM (
    SELECT
        time_bucket(CAST(? AS INTERVAL), datetime) AS bucket,
        first(open ORDER BY datetime) AS open,
        max(high) AS high,
        min(low) AS low,
        last(close ORDER BY datetime) AS close,
        sum(volume) AS volume,
        first(spread ORDER BY datetime) AS spread
    FROM dt_ohlc_m1
    WHERE symbol = ?
    GROUP BY bucket
    ORDER BY bucket DESC
    LIMIT ?
) sub ORDER BY bucket
```
Wait — `LIMIT` after GROUP BY with `ORDER BY bucket DESC` then reverse... Actually, for the limit mode the current pattern is:
```sql
ORDER BY datetime DESC LIMIT ?
-- then rows.reverse() in Python
```
For aggregated queries, the same pattern applies on the grouped result.

**e) Date range mode**: When `start_date` is provided, the WHERE clause filters by datetime range, THEN aggregation is applied. This is naturally correct since the filter narrows the set before grouping.

### Interval String Mapping

| timeframe param | DuckDB interval | seconds | 
|----------------|-----------------|---------|
| `1m` | (no aggregation) | 60 |
| `5m` | `'5 minutes'` | 300 |
| `15m` | `'15 minutes'` | 900 |
| `30m` | `'30 minutes'` | 1800 |
| `1h` | `'1 hour'` | 3600 |
| `4h` | `'4 hours'` | 14400 |
| `1d` | `'1 day'` | 86400 |

### Sample SQL (5m aggregation, limit mode)

```sql
SELECT
    time_bucket(CAST(? AS INTERVAL), datetime) AS bucket,
    first(open ORDER BY datetime) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close ORDER BY datetime) AS close,
    sum(volume) AS volume,
    first(spread ORDER BY datetime) AS spread
FROM dt_ohlc_m1
WHERE symbol = ?
GROUP BY bucket
ORDER BY bucket DESC
LIMIT ?
```
Parameters: `['5 minutes', 'NDX', 200]` → reverse in Python → response.

### SQL for date range mode

```sql
SELECT
    time_bucket(CAST(? AS INTERVAL), datetime) AS bucket,
    first(open ORDER BY datetime) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close ORDER BY datetime) AS close,
    sum(volume) AS volume,
    first(spread ORDER BY datetime) AS spread
FROM dt_ohlc_m1
WHERE symbol = ? AND datetime >= ? AND datetime < ?
GROUP BY bucket
ORDER BY bucket
```

### Frontend Changes

The `<select>` for timeframe should go next to the date inputs:

```html
<label>Timeframe:
    <select name="timeframe">
        <option value="1m" {% if timeframe == '1m' %}selected{% endif %}>1 min</option>
        <option value="5m" {% if timeframe == '5m' %}selected{% endif %}>5 min</option>
        <option value="15m" {% if timeframe == '15m' %}selected{% endif %}>15 min</option>
        <option value="30m" {% if timeframe == '30m' %}selected{% endif %}>30 min</option>
        <option value="1h" {% if timeframe == '1h' %}selected{% endif %}>1 hour</option>
        <option value="4h" {% if timeframe == '4h' %}selected{% endif %}>4 hours</option>
        <option value="1d" {% if timeframe == '1d' %}selected{% endif %}>1 day</option>
    </select>
</label>
```

The JS is already compatible — `buildUrl()` includes `timeframe`, and the form submit handler reads `[name=timeframe].value`. Only the template needs the visible `<select>`.

### Risks

- **`time_bucket` availability**: Available since DuckDB 0.10.x. DuckDB 1.5.3 has it. If someone runs an older DuckDB (< 0.10), they'd need to fall back to epoch math. Mitigation: add a simple `has_time_bucket` detection or use epoch math directly.
- **Empty aggregation results**: If no data matches the `WHERE` clause, the aggregation returns empty (empty list, correct 200 response). No error case to worry about.
- **`spread` field is new in API response**: Existing frontend code ignores extra keys, so this is safe. But spec docs and tests need updating.
- **Frontend: bucket -> `time` conversion**: Aggregation returns `bucket` timestamps (the grouped time). These get converted via `int(row[0].timestamp())` same as now. The `time_bucket` result is a TIMESTAMP, same as the original `datetime` — no type mismatch.

### Ready for Proposal

Yes. The exploration is complete. `time_bucket` is confirmed working, interval mapping is clear, performance is verified, and the code changes are well-understood.

**What the orchestrator should tell the user**: 

1. **Correction needed**: DuckDB 1.5.3 uses `time_bucket(INTERVAL, timestamp)` not `date_bin()`. `date_bin` is a PostgreSQL/Spark function — not available in DuckDB.
2. **The approach is solid**: Performance is excellent (46ms for 1d on 3.4M rows), `first/last ORDER BY` aggregates work correctly, and `CAST(? AS INTERVAL)` handles parameterized intervals.
3. **`spread` will be added** to the API response since it's in the data and the aggregation already computes it — zero marginal cost.
4. **Frontend changes are minimal** because the JS already handles `timeframe` — just swap the hidden input for a visible `<select>`.
