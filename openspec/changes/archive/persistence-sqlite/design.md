# Design: Persistence — SQLAlchemy + SQLite

## Technical Approach

Replace the dict-backed StrategyStore internals with sync SQLAlchemy 2.0 backed by SQLite, preserving the exact StrategyStore interface so routes and schemas remain unchanged. New `app/database.py` provides the ORM model and engine factory. Session-per-operation keeps the store self-contained. FastAPI lifespan bootstraps `create_all` on startup. Tests use in-memory SQLite via a swapped session factory.

## Architecture Decisions

| Dimension | Selected | Rationale |
|-----------|----------|-----------|
| Async vs Sync | **Sync** | Routes are `def`. Async would require converting all routes + `aiosqlite` — scope creep. |
| SQLAlchemy style | **2.0 style** | `DeclarativeBase`, `mapped_column`, `select()`. 1.x is legacy — not acceptable for new code. |
| Store pattern | **Replace internals** | Preserves `StrategyStore` interface — routes import `from app.store import store` unchanged. |
| Session lifecycle | **Session-per-operation** | Every endpoint calls one store method. `Depends(get_db)` adds zero value + forces route changes. |
| Test DB | **In-memory SQLite + create_all** | Fastest isolation, no file cleanup, trivially clean per test. |
| Migration | **create_all on startup** | No users yet. Alembic can be added when schema evolves. |

## Data Flow

```
HTTP Request → Route (def, unchanged) → Store method (unchanged interface)
    ├─ open Session()
    ├─ execute(select/insert/update/delete)
    ├─ commit()
    └─ close Session()
→ Pydantic model_dump() → HTTP Response

Startup: FastAPI lifespan → Base.metadata.create_all(engine) → yield
Test:    fixture → create_engine("sqlite:///:memory:") → create_all → swap session_factory
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/database.py` | Create | `Base`, `StrategyModel`, engine factory |
| `app/store.py` | Modify | Rewrite internals: `dict` → SQLAlchemy; API preserved |
| `app/main.py` | Modify | Add lifespan handler for `create_all` |
| `app/settings.py` | Modify | Add `DATABASE_URL: str = "sqlite:///./data/trading.db"` |
| `tests/conftest.py` | Create | Autouse `_reset_store` fixture with in-memory SQLite |
| `tests/test_strategies.py` | Modify | Rename `_clear_store` → `_reset_store`; update body |
| `pyproject.toml` | Modify | Add `sqlalchemy~=2.0` to `[project] dependencies` |
| `.env.example` | Modify | Add commented `DATABASE_URL` |
| `.gitignore` | Modify | Add `*.db`, `data/` |

## Interfaces / Contracts

### `app/database.py` (new)

```python
from datetime import UTC, datetime
from sqlalchemy import String, Text, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class StrategyModel(Base):
    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
```

### `app/store.py` (modified internals)

```
StrategyStore(db_url)          → creates engine + sessionmaker
.list()                        → session.execute(select(...)).scalars() → [Strategy]
.create(data: StrategyCreate)  → session.add(StrategyModel(...)) → commit → Strategy
.get(id)                       → session.get(StrategyModel, id) → Strategy | None
.update(id, data)              → session.get → update attrs → commit → Strategy
.delete(id)                    → session.get → session.delete → commit → bool
_clear() / _reset             → DROP/recreate tables (test only)
```

Each method follows this pattern:

```python
def create(self, data: StrategyCreate) -> Strategy:
    with self._session_factory() as session:
        model = StrategyModel(id=_generate_id(), name=data.name, description=data.description)
        session.add(model)
        session.commit()
        session.refresh(model)
        return self._to_schema(model)
```

### `app/main.py` lifespan

```python
from contextlib import asynccontextmanager
from app.database import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(store._engine)
    yield
```

### `app/settings.py` addition

```python
class Settings(BaseSettings):
    ...
    DATABASE_URL: str = "sqlite:///./data/trading.db"
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | StrategyModel mapping | Instantiate model, check column types |
| Unit | Store CRUD | 13 existing tests — fixture adapted, test logic unchanged |
| Integration | HTTP endpoints | 10 TestClient tests — no changes needed |
| E2E | Restart persistence | Manual: `POST → restart uvicorn → GET` returns strategy |

Test isolation — `conftest.py` autouse fixture:

```python
@pytest.fixture(autouse=True)
def _reset_store():
    """Replace store engine with fresh in-memory SQLite before each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    store._session_factory = sessionmaker(engine)
```

## Migration / Rollout

`Base.metadata.create_all(engine)` in lifespan handler. First startup creates `data/trading.db` + `strategies` table automatically. Subsequent starts are no-ops (`IF NOT EXISTS` semantics). No data to migrate — no persisted data exists yet. If parent `data/` directory is missing, `os.makedirs("data", exist_ok=True)` may be needed before `create_all`.

## Open Questions

- [ ] Does `data/` directory need explicit `os.makedirs` before `create_all`? SQLAlchemy creates the DB file but NOT parent directories.
- [ ] Should `clear()` be removed (tests now swap engines instead) or kept as `DELETE FROM strategies` for backward compat?
