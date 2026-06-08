# Proposal: Persistence — SQLAlchemy + SQLite

## Intent

Replace in-memory dict-backed StrategyStore with SQLAlchemy+SQLite so strategies survive restarts. Preserve the exact same interface — routes and schemas unchanged.

## Scope

### In Scope
- SQLAlchemy 2.0 `StrategyModel` and `Base` in new `app/database.py`
- StrategyStore internals rewritten with SQLAlchemy session-per-operation
- `DATABASE_URL` setting in `app/settings.py` (default `sqlite:///./data/trading.db`)
- FastAPI lifespan handler for `create_all` on startup
- Test fixtures adapted for in-memory SQLite isolation
- `sqlalchemy~=2.0` added to `pyproject.toml`

### Out of Scope
- Async SQLAlchemy / aiosqlite (sync matches existing `def` routes)
- Alembic migrations (create_all sufficient for dev)
- Abstract store protocol / multi-backend support
- `updated_at` tracking or schema changes
- Session-per-request via `Depends(get_db)`

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `trading-domain`: Add persistence requirement — data MUST survive restarts via SQLite-backed storage

## Approach

Sync SQLAlchemy 2.0 (`DeclarativeBase`, `mapped_column`, `select()`). StrategyStore accepts `db_url`, creates `engine` + `sessionmaker`. Each method opens/closes a Session per call. Routes unchanged. FastAPI lifespan calls `create_all()`. Tests: in-memory SQLite + `create_all` per fixture.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/database.py` | New | SQLAlchemy Base + StrategyModel |
| `app/store.py` | Modified | Dict → SQLAlchemy; interface preserved |
| `app/main.py` | Modified | +lifespan for create_all |
| `app/settings.py` | Modified | +DATABASE_URL setting |
| `tests/conftest.py` | New | In-memory DB fixture |
| `tests/test_strategies.py` | Modified | Fixture: clear() → _reset_store() |
| `pyproject.toml` | Modified | +sqlalchemy~=2.0 |
| `openspec/specs/trading-domain/spec.md` | Modified | +persistence requirement |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQLAlchemy + mypy strict | Med | 2.0 style well-typed; Mapped[] + mapped_column |
| Coverage drops | Low | Fixture-driven; model class has no branching |
| SQLite parent dir missing | Low | Create `data/` in init or settings |

## Rollback Plan

`git revert` persistence commit → `uv remove sqlalchemy` → delete `app/database.py` → restore `app/store.py` from git → restore test fixture. No data migration risk.

## Dependencies

- `sqlalchemy~=2.0`

## Success Criteria

- [ ] All 22 tests pass with SQLite store (100% coverage)
- [ ] `make ci` passes (ruff, mypy strict, pytest, coverage)
- [ ] Strategies survive restart with file-based SQLite
- [ ] `POST → restart → GET` returns created strategy
