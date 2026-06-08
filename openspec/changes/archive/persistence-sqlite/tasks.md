# Tasks: Persistence — SQLite

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~120–180 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Foundation

- [x] 1.1 Add `sqlalchemy~=2.0` to `pyproject.toml` `[project] dependencies`
- [x] 1.2 Create `app/database.py` — `Base`, `StrategyModel`, engine factory, `os.makedirs` for data dir

## Phase 2: TDD (RED) — Adapt tests for DB

- [x] 2.1 Create `tests/conftest.py` with autouse `_reset_store` fixture (in-memory SQLite + `create_all`)
- [x] 2.2 Remove `_clear_store` fixture from `tests/test_strategies.py` (moved to conftest)
- [x] 2.3 Run `uv run pytest` — confirm failures against old dict-backed store (RED) — 1 failure confirmed

## Phase 3: TDD (GREEN) — Store rewrite

- [x] 3.1 Rewrite `app/store.py` internals: accept `db_url`, create `_session_factory`, session-per-operation CRUD, `_to_schema` helper
- [x] 3.2 Implement `clear()` as `DELETE FROM strategies` for backward compat
- [x] 3.3 Run `uv run pytest` — all 22+ tests pass (GREEN) — 22 passed, 97% coverage

## Phase 4: Wiring

- [x] 4.1 Add `DATABASE_URL: str = "sqlite:///./data/trading.db"` to `app/settings.py`
- [x] 4.2 Add FastAPI lifespan handler in `app/main.py` — `Base.metadata.create_all` + `os.makedirs("data", exist_ok=True)`
- [x] 4.3 Run `uv run pytest` — all route tests still pass — 22 passed

## Phase 5: Cleanup

- [x] 5.1 Add `*.db` and `data/` to `.gitignore`
- [x] 5.2 Add commented `# DATABASE_URL=sqlite:///./data/trading.db` to `.env.example`
- [x] 5.3 Run `uv run make ci` — ruff, mypy strict, pytest, coverage all pass
