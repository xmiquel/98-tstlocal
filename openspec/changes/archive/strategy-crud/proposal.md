# Change: strategy-crud

## Why

First real domain feature after the skeleton. Users can POST, list, read by ID, and delete trading strategies via the API. Establishes Pydantic model patterns, CRUD endpoint patterns, in-memory store pattern, and test isolation — the template ALL future domain features will follow. This slice moves the project from "the toolchain works" to "the application does something useful."

## What Changes

- `app/schemas.py` (NEW): `StrategyCreate` (input) / `Strategy` (output) Pydantic models with UUID
- `app/store.py` (NEW): `StrategyStore` dict store with `list()`/`create()`/`get()`/`delete()`/`clear()`
- `app/main.py` (MODIFIED): 4 routes — `GET /strategies`, `POST /strategies` (201), `GET /strategies/{id}` (200/404), `DELETE /strategies/{id}` (204/404)
- `tests/test_strategies.py` (NEW): ~6 contract tests (empty list, create, list after create, get by id, get 404, delete, delete 404)
- Canonical spec: NEW `trading-domain` capability with `Strategy CRUD` ADDED Requirement

## Impact

**Affected**: `app/main.py` (+~15 lines) + 3 new files (`schemas.py`, `store.py`, `test_strategies.py`). Canonical spec gets new `trading-domain` capability.

**NOT affected**: No new deps, no `uv.lock`, no `pyproject.toml`, no `Makefile`, no CI, no `AGENTS.md`, no `test_health.py`. No frontend, DB, MT5, auth, settings, or uvicorn.

## Out of Scope (Non-Goals)

Frontend, persistence, MT5, auth, settings, uvicorn, httpx warning, business logic beyond CRUD, `make run` target.

## Capabilities

### New Capabilities
- `trading-domain`: domain models and CRUD endpoints for trading strategies. New capability at `openspec/specs/trading-domain/spec.md`. Reason: clean separation from `python-toolchain` (tooling concerns). The skeleton's "Application Runtime" proved the toolchain works; strategy-crud is the first real domain feature and deserves its own capability.

### Modified Capabilities
- None.

## Approach

One PR, three commits in strict TDD order: (1) `test(strategies): add RED test` → (2) `feat(strategies): implement CRUD` → (3) `chore(spec): openspec delta`. Test isolation via `store.clear()` autouse fixture. Zero new dependencies. ~135 lines.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Singleton store leaks state between tests | Low | `store.clear()` autouse fixture |
| UUID non-determinism in test assertions | Low | Assert `"id" in data`, not specific value |
| Future DB migration from in-memory store | Low | Thin class interface — trivially swappable |

## Rollback Plan

Single `git revert` of the squash commit on `main`. Removes `app/schemas.py`, `app/store.py`, `tests/test_strategies.py`. Reverts `app/main.py` to skeleton state. Reverts `trading-domain` delta from canonical specs. No data, no migrations, no backwards-compat concerns.

## Success Criteria

- [ ] `uv run pytest` exits 0; coverage on `app/` >= 80%
- [ ] `uv run ruff check .` and `uv run mypy .` exit 0
- [ ] `GET /strategies` returns `[]` when store is empty
- [ ] `POST /strategies` returns 201 with JSON body containing `id`
- [ ] `GET /strategies/{id}` returns 200 (existing) or 404 (missing)
- [ ] `DELETE /strategies/{id}` returns 204 (existing) or 404 (missing)
