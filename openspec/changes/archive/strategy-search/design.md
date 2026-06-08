# Design: Strategy Search

## Architecture Decisions

| Decision | Choice | Alternative | Rationale |
|---|---|---|---|
| Query parameter | `name` (Optional[str]) | `q`, `search`, JSON body | REST convention; FastAPI-native; zero new deps |
| Filter implementation | SQLAlchemy `.ilike()` on `StrategyModel.name` | Python `in` post-fetch, raw SQL `LIKE` | Case-insensitive by default; ORM-parameterized — injection-safe; no new deps |
| No filter behavior | Return all (existing path through `list()`) | Return empty, error if missing | Backward compatible — existing clients unaffected |
| Store interface | `list(name_filter: str \| None = None) -> list[Strategy]` | New `search()` method, overloaded `list()` | Minimal diff; single method; `None` preserves current behavior |
| Testing | 2 new TestClient tests + existing pass unchanged | Separate test module, fixture refactor | Delta spec defines two Gherkin scenarios; existing tests validate regression |

## Data Flow

```
Client GET /strategies?name=MACD
  → app.main:list_strategies(name="MACD")
    → app.store:StrategyStore.list(name_filter="MACD")
      → SQLAlchemy: SELECT ... WHERE name ILIKE '%MACD%' ORDER BY created_at
        → SQLite
```

## File Changes

| File | Action | Description |
|---|---|---|
| `app/store.py` | Modify | Add `name_filter` param to `list()`, append `.ilike()` when set |
| `app/main.py` | Modify | Add `name` query param to `list_strategies()`, pass to `store.list()` |
| `openspec/specs/trading-domain/spec.md` | Modify | Add Name Filter requirement + 2 scenarios |
| `tests/test_strategies.py` | Modify | Add 2 filter tests |

## Interfaces

```python
# Store signature change (backward compatible):
def list(self, name_filter: str | None = None) -> list[Strategy]: ...

# Route signature change (backward compatible):
@app.get("/strategies")
def list_strategies(name: str | None = None) -> list[dict[str, object]]: ...
```

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Route | Filter match — returns subset | TestClient `GET /strategies?name=MACD` |
| Route | No match — returns `[]` | TestClient `GET /strategies?name=NonExistent` |
| Regression | No param — returns all | Existing tests pass unchanged |

No migration required. Additive change, fully backward compatible.
