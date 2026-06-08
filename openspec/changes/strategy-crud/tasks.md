# Tasks: strategy-crud

## Overview

Three tasks in one PR on branch `feat/strategy-crud` (from `main`). Strict TDD: RED test commit precedes implementation. In-memory StrategyStore with Pydantic models. ~335 lines total (~135 code + test, ~200 spec/delta). Zero new dependencies — pydantic is transitive from FastAPI, uuid and datetime are stdlib.

## Numbered Task List

### 1. test(strategies): add RED tests for strategy CRUD

- **Type**: test
- **Conventional commit**: `test(strategies): add RED tests for strategy CRUD`
- **Files touched**: `tests/test_strategies.py` (NEW)
- **Acceptance criteria**:
  - ~8 scenario tests: empty list, create (201), list after create, get by id (200), get 404, delete (204), delete 404, store isolation via `store.clear()` autouse fixture
  - `uv run pytest` fails with `ImportError: cannot import name 'store' from 'app.store'` (RED; no skip, no mark)
  - `git log --oneline` shows this commit precedes `feat(strategies):`
- **TDD state**: RED
- **Depends on**: none

### 2. feat(strategies): implement in-memory strategy CRUD

- **Type**: code
- **Conventional commit**: `feat(strategies): implement in-memory strategy CRUD`
- **Files touched**: `app/schemas.py` (NEW), `app/store.py` (NEW), `app/main.py` (+4 routes + import)
- **Acceptance criteria**:
  - `app/schemas.py`: `StrategyCreate(BaseModel)` with `name: str` + optional `description: str`; `Strategy(StrategyCreate)` with UUID `id` and datetime `created_at`
  - `app/store.py`: `StrategyStore` with `_strategies: dict[str, Strategy]`, methods `list()` / `create(StrategyCreate) -> Strategy` / `get(id) -> Strategy | None` / `delete(id) -> bool` / `clear()`; module-level `store = StrategyStore()`
  - `app/main.py`: `GET /strategies` (200), `POST /strategies` (201), `GET /strategies/{id}` (200/404), `DELETE /strategies/{id}` (204/404)
  - `uv run pytest` exits 0; coverage on `app/` >= 80%
  - `uv run ruff check .`, `uv run mypy .` exit 0
- **TDD state**: GREEN
- **Depends on**: 1

### 3. chore(spec): include openspec delta for strategy-crud

- **Type**: docs
- **Conventional commit**: `chore(spec): include openspec delta for strategy-crud`
- **Files touched**: `openspec/changes/strategy-crud/{proposal.md, specs/trading-domain/spec.md, tasks.md}`
- **Acceptance criteria**:
  - All openspec artifacts present (proposal, spec, tasks)
  - `git log --oneline` shows `test(strategies):` before `feat(strategies):` before `chore(spec):`
  - No `Co-Authored-By:`; conventional commit format
- **TDD state**: N/A
- **Depends on**: 1, 2

## Work-Unit Sequencing

Branch `feat/strategy-crud` from `main`. Single PR, squash-merge to `main`. 1 → 2 → 3. RED commit before GREEN commit per strict TDD. Spec-delta commit closes the change on the same PR.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~335 total (~135 code+test, ~200 spec artifacts) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR (3 commits, squash) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

## Pre-Apply Checks

- [x] `uv run pytest` exits 0; coverage on `app/` >= 80%
- [x] `uv run ruff check .` exits 0
- [x] `uv run ruff format --check .` exits 0
- [x] `uv run mypy .` exits 0
- [x] `uv lock --check` exits 0
- [x] `git log --oneline` shows RED commit before GREEN commit
