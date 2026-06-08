# Exploration: persistence-sqlite

## Current State

The project has a working **in-memory** strategy CRUD (`openspec/changes/archive/strategy-crud/` + `openspec/changes/archive/strategy-update/`). 22 tests, 100% coverage, all green.

- `app/store.py` — `StrategyStore` class backed by `dict[str, Strategy]`. Exposes `list()`, `create()`, `get()`, `update()`, `delete()`, `clear()`.
- `app/schemas.py` — `Strategy`, `StrategyCreate`, `StrategyUpdate` Pydantic models.
- `app/main.py` — 5 synchronous routes (`def`, not `async def`): `GET /health`, `GET/POST /strategies`, `GET/PUT/DELETE /strategies/{id}`.
- `tests/test_strategies.py` — 13 tests using `TestClient` + 3 direct store unit tests. Autouse fixture calls `store.clear()` for isolation.
- Zero SQLAlchemy or database dependencies installed. `uv.lock` has no persistence packages.

The canonical spec (`openspec/specs/trading-domain/spec.md`) currently lists persistence as out-of-scope — **the spec must be updated** to add a persistence requirement once this change merges.

---

## Affected Areas

| File | Why Affected |
|------|-------------|
| `app/store.py` | Implementation swapped from `dict` to SQLAlchemy. **Interface preserved.** |
| `app/database.py` | **NEW** — engine, session factory, Base, table model. |
| `app/main.py` | Add FastAPI lifespan handler for `create_all` on startup. |
| `app/schemas.py` | Strategy gains an `id` field with DB-aware default (no model change needed — current `uuid.uuid4().hex` is fine). |
| `app/settings.py` | Add `DATABASE_URL` setting (default `sqlite:///./data/trading.db`). |
| `tests/test_strategies.py` | Autouse fixture changes from `store.clear()` to DB reset. Direct store tests need session injection. |
| `tests/conftest.py` | **NEW** (optional) — DB fixtures for test isolation. |
| `pyproject.toml` | Add `sqlalchemy~=2.0` to `[project] dependencies`. |
| `uv.lock` | Regenerated after dep addition. |
| `.gitignore` | Add `*.db` / `data/` entries (optional, for SQLite files). |
| `.env` / `.env.example` | Add `DATABASE_URL` (optional). |
| `openspec/specs/trading-domain/spec.md` | Remove "persistence" from out-of-scope; add persistence requirement. |

---

## Decision Dimensions

### 1. Sync vs Async SQLAlchemy

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Sync** (recommended) | Matches existing `def` routes. Simpler typing (mypy strict). No `aiosqlie` dep. SQLite stdlib driver built-in. Session management is straightforward. | Slightly less throughput under high concurrency (irrelevant for dev tool). | Low |
| **Async** | Matches FastAPI's async capability. More idiomatic for production FastAPI. | Requires ALL routes to change from `def` to `async def`. `aiosqlite` dep needed. More complex mypy typing (`AsyncSession`, `async with`). Shifts scope from "add persistence" to "refactor entire route layer". | Medium+ |

**Verdict: SYNC.** The current routes are synchronous. Converting them to async is scope creep — the goal is persistence, not asyncifying the route layer. SQLite with sync SQLAlchemy is more than adequate for a local dev tool. If async is needed later, it's a separate change.

---

### 2. SQLAlchemy 2.0 Style (Required — no debate)

- Use `Base = DeclarativeBase` (not `declarative_base()`)
- Use `mapped_column()` (not `Column()`)
- Use `select()` / `execute()` (not `Query` / `session.query()`)
- All typing with `Mapped[]` annotations

No alternatives considered — 1.x style is legacy and not acceptable for a new project.

---

### 3. Repository Pattern (Replace Internals) vs Active Record

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Replace store.py internals** (recommended) | Preserves StrategyStore interface. Routes unchanged. Tests need minimal adaptation. Single source of truth for strategy operations. | Store becomes coupled to SQLAlchemy (not abstract). | Low |
| **Abstract Store protocol + SQL implementation** | Clean architecture purity. Swapable implementations. | Overengineering for a single store with no multi-backend requirement. Adds interface boilerplate. | Medium |
| **Active Record (SQLAlchemy model exposed to routes)** | Simpler — routes call model methods directly. | Breaks existing pattern. Contaminates route layer with DB concerns. Harder to test. | Low (but wrong) |

**Verdict: REPLACE INTERNALS.** The `StrategyStore` class already has the right interface. The SQL implementation replaces the `dict` inside, keeping `list()`, `create()`, `get()`, `update()`, `delete()`. Routes import `from app.store import store` — that import stays. Zero route changes needed.

The store accepts a `sessionmaker` at construction (or creates one from a connection string). Each method opens a short-lived `Session` via context manager, executes the operation, commits, and closes.

```python
# Pseudocode of the new internals
class StrategyStore:
    def __init__(self, db_url: str = "sqlite:///./data/trading.db") -> None:
        self._engine = create_engine(db_url, echo=False)
        self._session_factory = sessionmaker(self._engine)

    def list(self) -> list[Strategy]:
        with self._session_factory() as session:
            rows = session.execute(select(StrategyModel).order_by(StrategyModel.created_at)).scalars()
            return [self._to_schema(r) for r in rows]
    # ... create, get, update, delete follow the same pattern
```

---

### 4. Session Management

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Session-per-operation** (recommended) | Store is self-contained. No route changes. No `Depends(get_db)` dependency. Simple test isolation (swap session factory). | No cross-operation transactions (not needed for single-op endpoints). Sessions opened/closed per call. | Low |
| **Session-per-request via `Depends(get_db)`** | Standard FastAPI pattern. Transaction spans full request. | Requires changing ALL route signatures to accept `db: Session = Depends(get_db)`. More plumbing. Routes know about DB. | Medium |

**Verdict: SESSION-PER-OPERATION.** Each store method creates its own `Session()` via the factory. Since every endpoint calls exactly ONE store method per request, there is zero benefit to session-per-request, and significant cost in route changes. The store manages its own lifecycle.

---

### 5. Test Database Strategy

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **In-memory SQLite + create_all per fixture** (recommended) | Fastest. No file I/O. Perfect isolation. Trivially clean. | Cannot test migration behavior. Slightly different SQLite behavior vs file-based (not relevant for CRUD). | Low |
| **Transaction rollback** | Auto-rollback without recreating tables. Very fast. | Requires connection binding to session. More complex fixture. | Medium |
| **File-based test DB** | Closest to production. Can inspect test DB. | Slower. File cleanup needed. Potential for stale state between runs. | Low |

**Verdict: IN-MEMORY SQLITE with `create_all` per test session.** Simple pattern:

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def _reset_store():
    """Replace the store's engine with a fresh in-memory DB before each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    store._session_factory = sessionmaker(engine)
    yield
```

This gives each test a clean DB at maximum speed. No file cleanup. No transaction complexity.

**Important**: Direct store tests (e.g., `test_store_update_returns_updated_strategy`) will work because each test gets a fresh engine bound to the store. HTTP tests via `TestClient` work because they hit the same module-level `store` object.

---

### 6. Table Design

```sql
CREATE TABLE strategies (
    id          VARCHAR(32)  PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT         DEFAULT NULL,
    created_at  DATETIME     NOT NULL DEFAULT (datetime('now'))
);
```

SQLAlchemy model:

```python
class StrategyModel(Base):
    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
```

- `id` = `uuid.uuid4().hex` (32-char hex), generated in the model's `default` (same as current schema)
- `description` = nullable text, matching `StrategyCreate.description: str | None = None`
- `created_at` = set at insert time via Python default (same as current model)
- No `updated_at` — the current model doesn't track it. Adding it would be scope creep.

No indexes beyond PK (single-table CRUD at low volume doesn't need them).

---

### 7. Dependencies

| Package | Version | Why |
|---------|---------|-----|
| `sqlalchemy` | `~=2.0` | ORM and core. Sync SQLite uses stdlib `sqlite3` — no extra driver. |

**No `aiosqlite` needed** (sync decision).
**No `greenlet` needed** (sync decision — `greenlet` is an async SQLAlchemy transitive).
**No Alembic** (migration strategy covered below).

---

### 8. Migration Strategy

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **`Base.metadata.create_all()` on startup** (recommended) | Zero config. Auto-creates DB file + tables on first `make run`. Works for dev. | No migration path for schema changes. Destructive if table schema changes (drop + recreate). | Low |
| **Alembic** | Proper migration history. Safe for production. | Overkill for local dev. Adds complexity. Another config file. | Medium |
| **Manual SQL scripts** | Explicit control. | Not automated. Easy to forget. | Medium |

**Verdict: `create_all` on startup via FastAPI lifespan.** FastAPI 0.116+ supports the `lifespan` context manager pattern:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title=..., lifespan=lifespan)
```

This auto-creates `data/trading.db` and the `strategies` table when `uvicorn` starts. No manual setup. Alembic can be added later when the app has users with existing data.

---

### 9. Impact on Existing Tests

**Current behavior**: 22 tests, all passing, 100% coverage. Autouse fixture calls `store.clear()`.

**Required changes**:

| Test File | Change | Complexity |
|-----------|--------|------------|
| `tests/test_strategies.py` — HTTP tests (10 tests via TestClient) | **No change to test logic.** Autouse fixture changes from `store.clear()` to `_reset_store()` (replaces engine + creates tables). | Low |
| `tests/test_strategies.py` — Direct store tests (3 tests) | Need the same `_reset_store` fixture. `store.create()` and `store.update()` now hit SQLite — should work identically since the interface is the same. | Low |
| `tests/conftest.py` (NEW) | Shared DB fixture for all test files. | Low |

**Key insight**: Since the `StrategyStore` interface doesn't change, the HTTP tests need ZERO modification. The only change is the fixture body. The direct store tests also work unchanged because `store.create()` and `store.update()` return the same types.

**Coverage**: Must remain at 100%. The new `app/database.py` file will have test-covered code (table creation via fixture, engine creation via store init). The SQLAlchemy model class itself is trivial — coverage exception may be acceptable if mypy proves it's structurally sound.

---

### 10. Rollback Feasibility

**Rollback is trivial:**

1. `git revert` the persistence commit(s) — the in-memory store is still in git history.
2. `uv remove sqlalchemy` — remove the dependency.
3. Delete `app/database.py` — the new file.
4. Restore `app/store.py` from before the change — the interface is the same, routes don't change.
5. Restore `tests/test_strategies.py` — the old `store.clear()` fixture.
6. Delete `data/` directory if created.

**Risk of irreversible change**: None. The transition from in-memory to SQL is purely internal to the store. No data migration needed (there's no persisted data to lose). Routes and schemas don't change. No public API contract breaks.

---

## Recommendation

### Per-Dimension Verdicts

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| 1. Async vs Sync | **Sync** | Matches routes, fewer deps, simpler mypy |
| 2. SQLAlchemy style | **2.0 style** | No legacy API |
| 3. Repository vs Active Record | **Replace store.py internals** | Preserves interface, routes unchanged |
| 4. Session management | **Session-per-operation** | Self-contained store, no route changes |
| 5. Test database | **In-memory SQLite + create_all** | Fastest, perfect isolation |
| 6. Table design | `strategies(id, name, description, created_at)` | Matches current schema |
| 7. Dependencies | `sqlalchemy~=2.0` only | No aiosqlite, no greenlet, no alembic |
| 8. Migration | **create_all on startup** (FastAPI lifespan) | Zero setup for dev |
| 9. Test impact | **Minimal** — fixture swap only | HTTP tests unchanged |
| 10. Rollback | **Trivial** — git revert + remove 1 dep | Interface preserved |

### Deliverable Structure

```
openspec/changes/persistence-sqlite/
├── exploration.md        # ← this file
├── proposal.md           # sdd-propose
├── specs/
│   └── trading-domain/
│       └── spec.md       # sdd-spec (delta — adds persistence requirement)
├── design.md             # sdd-design
└── tasks.md              # sdd-tasks
```

### New/Modified Files Summary

| Action | File | Est. LOC |
|--------|------|----------|
| **NEW** | `app/database.py` | ~30 |
| **MODIFY** | `app/store.py` | ~60 (rewrite internals, keep interface) |
| **MODIFY** | `app/main.py` | +5 (lifespan + create_all import) |
| **MODIFY** | `app/settings.py` | +2 (DATABASE_URL) |
| **MODIFY** | `tests/test_strategies.py` | ~5 (fixture change) |
| **NEW** | `tests/conftest.py` | ~15 |
| **MODIFY** | `pyproject.toml` | +1 (sqlalchemy~=2.0) |
| **MODIFY** | `.env.example` | +1 (optional DATABASE_URL) |
| **AUTO** | `uv.lock` | regen |

**Total delta**: ~120 lines code + test, ~1 dep, ~1 file. Well under the 400-line review budget.

### Commit Plan (Strict TDD)

| # | Conventional commit | Files |
|---|-------------------|-------|
| 1 | `test(strategies): adapt tests for SQLite persistence` | `tests/conftest.py`, `tests/test_strategies.py` |
| 2 | `feat(strategies): replace in-memory store with SQLAlchemy+SQLite` | `app/database.py`, `app/store.py`, `app/main.py`, `app/settings.py`, `pyproject.toml` |
| 3 | `chore(spec): add persistence requirement to trading-domain spec` | SDD artifacts + `openspec/specs/trading-domain/spec.md` |

---

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **SQLAlchemy + mypy strict complexity** | Medium | SQLAlchemy 2.0 with `mapped_column` + `Mapped[]` is well-typed. Use `from __future__ import annotations` + `TYPE_CHECKING` guards if needed. May need `# type: ignore[attr-defined]` on session factory. |
| **Coverage drops below 80%** | Low | `database.py` has ~15 new lines; fixture-driven coverage ensures they're hit. Direct model class is a few lines with no branching. |
| **SQLite file path doesn't exist on first run** | Low | `create_all` creates the file automatically. Set `DATABASE_URL` parent dir as `.env`-configurable. Ensure `data/` dir exists or use engine `create_engine` with `sqlite:///./data/trading.db` — SQLAlchemy creates file but NOT parent dir. Must handle `data/` directory creation (e.g., in settings or store init). |
| **Test isolation failure (state leaking between tests)** | Low | Each test gets a fresh in-memory DB via the `_reset_store` fixture. No shared state possible. |
| **Existing tests fail after store swap** | Low | HTTP tests are interface-driven — same inputs, same outputs. Direct store tests may need the DB-active fixture. If `_reset_store` is autouse, they just work. |
| **Spec outdated — persistence in "out of scope"** | Medium | This is by design. The spec MUST be updated by `sdd-archive` to move persistence into scope. The archive phase handles this. |

---

## Ready for Proposal

**Yes.** The exploration is complete. All 10 decision dimensions have analyzed tradeoffs and produced clear recommendations. The recommended approach is **sync SQLAlchemy 2.0**, **replace store.py internals**, **session-per-operation**, **in-memory SQLite tests**, and **create_all on startup**.

The next phase is `sdd-propose` — create `openspec/changes/persistence-sqlite/proposal.md` with the formal change intent, scope definition, and full approach.

### What sdd-propose needs to know

- **Change name**: `persistence-sqlite`
- **Goal**: Replace `dict`-backed `StrategyStore` with SQLAlchemy+SQLite-backed store. Keep the exact same interface and routes.
- **Required**: The canonical spec `openspec/specs/trading-domain/spec.md` must be updated to add a persistence requirement (handled by `sdd-archive` after implementation).
- **Constraints**: Must preserve 100% coverage, mypy strict must pass, all 22 existing tests must continue passing with minimal fixture changes.
- **Delivery strategy**: Single PR (~120 lines + lockfile). Well under 400-line budget.
