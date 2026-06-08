# Design: Strategy Update Endpoint

## Technical Approach

Add a `PUT /strategies/{id}` endpoint that replaces a strategy's fields in-place. Follows the exact patterns established by the existing GET/POST/DELETE routes: a new `StrategyUpdate` Pydantic model (reusing `StrategyCreate` fields), a `store.update(id, data)` method raising `KeyError` on missing ID, and a route handler returning 200 with the updated strategy or 404.

## Architecture Decisions

| Decision | Options | Trade-off | Choice |
|----------|---------|-----------|--------|
| PUT vs PATCH | PUT (full replace), PATCH (partial) | PUT simpler, idiomatic; PATCH more flexible but adds merge logic | **PUT** — full replacement, matches existing CRUD patterns |
| StrategyUpdate model | New model vs reuse `StrategyCreate` directly | New model creates duplication; reuse creates semantic confusion | **New `StrategyUpdate`** — structurally identical to `StrategyCreate`, but signals intent and allows future divergence |
| Store.update() return semantics | Return updated `Strategy`, return `None`, raise exception | `None` forces caller to re-fetch; raising `KeyError` matches existing GET 404 pattern | **Raise `KeyError`** — consistent with store.get() → 404 handling in routes |
| Route structure | Mirror DELETE pattern vs separate validation | Mirror DELETE is less code; separate is more explicit | **Mirror DELETE** — existing pattern is proven and tested |

## Data Flow

```
Client ──PUT /strategies/{id} {name, description}──→ FastAPI route
                                                          │
                                                    validate id (str)
                                                          │
                                                    store.update(id, data)
                                                          │
                                              ┌───────────┴───────────┐
                                              │ KeyError?             │
                                              │   → HTTP 404          │
                                              │ Success?              │
                                              │   → HTTP 200 + body   │
                                              └───────────────────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/schemas.py` | Modify | Add `StrategyUpdate` model (alias to `StrategyCreate`) |
| `app/store.py` | Modify | Add `update(id, data)` method |
| `app/main.py` | Modify | Add `PUT /strategies/{id}` route |
| `tests/test_strategies.py` | Modify | Add 4 test cases: store.update success + KeyError, route 200 + 404 |
| `openspec/specs/trading-domain/spec.md` | Modify | Add PUT scenarios (delta spec already covers this) |

## Interfaces / Contracts

```python
# app/schemas.py — new input model for updates
class StrategyUpdate(BaseModel):
    name: str
    description: str | None = None


# app/store.py — new method on StrategyStore
def update(self, strategy_id: str, data: StrategyUpdate) -> Strategy:
    """Update an existing strategy in-place.

    Raises KeyError if strategy_id does not exist.
    Returns the updated Strategy object.
    """


# app/main.py — new route handler
@app.put("/strategies/{strategy_id}")
def update_strategy(strategy_id: str, payload: StrategyUpdate) -> dict[str, object]:
    ...
```

`StrategyUpdate` is structurally identical to `StrategyCreate` today. The separation exists to signal semantic intent: `StrategyCreate` for creation, `StrategyUpdate` for updates. This prevents confusion if they diverge later (e.g., update might allow partial fields in a future PATCH).

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `store.update()` returns updated strategy | Create strategy via store, update via store, assert fields changed, id and created_at preserved |
| Unit | `store.update()` raises `KeyError` on missing id | Call update with non-existent id, assert `KeyError` |
| Integration | `PUT /strategies/{id}` returns 200 | Create via POST, update via PUT with new name, assert 200 + new name returned |
| Integration | `PUT /strategies/{id}` returns 404 | Send PUT with non-existent id, assert 404 |

## Migration / Rollout

No migration required. Additive change — existing data and routes unaffected.

## Open Questions

None.
