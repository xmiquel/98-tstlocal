# Tasks: fastapi-skeleton

## Overview

Four work units, one branch, one PR, squash-merge to `main`. Strict TDD: deps, RED test, GREEN, spec arc. Delta: +24 code, +4 openspec, +~250 uv.lock.

## 1. chore(deps): add fastapi~=0.116 and httpx~=0.27

- **Type**: config
- **Conventional commit**: `chore(deps): add fastapi~=0.116 and httpx~=0.27`
- **Files touched**: `pyproject.toml`, `uv.lock`
- **Acceptance**:
  - `pyproject.toml` line 6: `dependencies = ["fastapi~=0.116", "httpx~=0.27"]`
  - `uv lock --check` exits 0; `uv.lock` in same work unit
- **TDD state**: N/A
- **Depends on**: none

## 2. test(health): add RED test for GET /health

- **Type**: test
- **Conventional commit**: `test(health): add RED test for GET /health`
- **Files touched**: `tests/test_health.py` (NEW)
- **Acceptance**:
  - Imports `from fastapi.testclient import TestClient` and `from app.main import app`
  - `uv run pytest` fails with `ModuleNotFoundError: No module named 'app.main'` (RED; no skip)
  - `git log --oneline` shows this commit precedes `feat(health):`
- **TDD state**: RED
- **Depends on**: 1

## 3. feat(health): add minimal FastAPI app with /health route

- **Type**: code
- **Conventional commit**: `feat(health): add minimal FastAPI app with /health route`
- **Files touched**: `app/main.py` (NEW)
- **Acceptance**:
  - Defines `app: FastAPI = FastAPI()` and `@app.get("/health")` returning `{"status": "ok"}`
  - `uv run pytest` exits 0; coverage on `app/` is 100%
  - `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .` exit 0
- **TDD state**: GREEN
- **Depends on**: 2

## 4. chore(spec): include openspec delta for fastapi-skeleton

- **Type**: docs
- **Conventional commit**: `chore(spec): include openspec delta for fastapi-skeleton`
- **Files touched**: `openspec/changes/fastapi-skeleton/{proposal.md, specs/python-toolchain/spec.md, design.md, tasks.md}` (4 on disk)
- **Acceptance**:
  - All 4 openspec files present in the change folder
  - `openspec/specs/python-toolchain/spec.md` (canonical) UNCHANGED
  - No `Co-Authored-By:`; conventional commit format
- **TDD state**: N/A
- **Depends on**: 1, 2, 3

## Work-Unit Sequencing

Branch `feat/fastapi-skeleton`, one PR, squash-merge to `main`. 1 → 2 → 3 → 4.

Tasks 1-3 form the strict-TDD chain: deps first, test before implementation, implementation flips GREEN. Task 4 bundles the spec arc on the same PR. Four commits on the branch ref — `git log --oneline` shows RED-before-GREEN before squash.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~30 code + ~250 lockfile + 4 openspec files |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR (4 commits, squash) |
| Delivery strategy | single-pr |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

## Pre-Apply Checks

Apply MUST run all from repo root, all exit 0, before push:

- [ ] `uv run pytest` — passes; coverage on `app/` >= 80%
- [ ] `uv run ruff check .` — lint clean (S101 ignored in `tests/**`)
- [ ] `uv run ruff format --check .` — format clean
- [ ] `uv run mypy .` — strict type check clean
- [ ] `uv lock --check` — lockfile matches (binding CI step)
- [ ] `make ci` — aggregates the 6 local commands

PowerShell `RemoteException` banners on `uv` are terminal artifacts; trust the exit code.
