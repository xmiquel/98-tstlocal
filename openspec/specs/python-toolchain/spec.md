# Delta for python-toolchain

## Purpose

The `python-toolchain` capability installs a strict Python development environment for the upcoming FastAPI trading app. Pinning Python 3.12, committing `uv.lock`, and configuring pytest (80% coverage gate), ruff (with security rules), and mypy `--strict` from day one lets every later change inherit TDD, lint, and type safety as a foundation. The capability flips `openspec/config.yaml` `apply.tdd` to `true` and switches `.gga` to Python mode, unlocking RED→GREEN→REFACTOR. This change ships zero application code.

## ADDED Requirements

### Requirement: Toolchain Pinning and Lockfile

Python 3.12.x SHALL be pinned via `.python-version` and `pyproject.toml` `requires-python = ">=3.12,<3.13"`. All runtime and dev dependencies SHALL be declared in `pyproject.toml`. `uv.lock` SHALL be committed. `uv sync` SHALL be the canonical install command. The verification step SHALL run `uv lock --check`; if it fails the change MUST be marked failed and `uv.lock` regenerated.

#### Scenario: A developer clones the repo

- GIVEN a fresh clone with `uv` on PATH
- WHEN the developer runs `uv sync`
- THEN Python 3.12.x is selected from `.python-version` and the env installs deterministically

#### Scenario: Lockfile drift fails verification

- GIVEN `pyproject.toml` declares a version not yet in `uv.lock`
- WHEN the verification step runs `uv lock --check`
- THEN the change SHALL be marked failed

### Requirement: Code Quality (Lint, Format, Type Check)

`ruff` SHALL be the linter and formatter with rule sets `E`, `F`, `I`, `B`, `UP`, `SIM`, `S`. `ruff check .` and `ruff format --check .` SHALL pass with zero findings. `mypy` SHALL run with `strict = true`; type hints SHALL be present on every public function and method added in any subsequent change. `mypy .` SHALL pass with zero errors.

#### Scenario: Clean lint, format, and type check

- GIVEN committed code conforms to rule sets and is fully hinted
- WHEN a developer runs `ruff check .`, `ruff format --check .`, and `mypy .`
- THEN all three exit with code 0

### Requirement: OpenSpec Strict TDD Mode

`openspec/config.yaml` SHALL set `rules.apply.tdd: true` once this change lands. All subsequent changes SHALL follow RED→GREEN→REFACTOR.

#### Scenario: A follow-up change triggers strict TDD

- GIVEN this change is merged and `apply.tdd: true` is in effect
- WHEN a developer opens a PR for a new change
- THEN `sdd-apply` requires a failing test before any implementation commit

### Requirement: GGA Python Mode

`.gga` SHALL use `FILE_PATTERNS="*.py"`, `MODE=balanced`, and `EXCLUDE_PATTERNS` covering `*_test.py`, `test_*.py`, `conftest.py`, `.venv/*`, `__pycache__/*`, `.pytest_cache/*`, `.ruff_cache/*`, `.mypy_cache/*`, `htmlcov/*`. First-run noise on Node-flavoured infra (`.atl/`, `.windsurf/`, `openspec/`) is expected and SHALL produce no spurious findings.

#### Scenario: GGA ignores test, cache, and venv paths

- GIVEN `.gga` is configured per this requirement
- WHEN GGA runs against the repository
- THEN only `*.py` files outside the exclude list are reviewed

### Requirement: Repository Hygiene

`.gitignore` SHALL exclude `.venv/`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `htmlcov/`, `.coverage`, `*.egg-info/`, `dist/`, `build/`, `.uv-cache/`.

#### Scenario: Venv and cache artefacts never enter git

- GIVEN the ignore list is in effect
- WHEN `git status` runs after `uv sync`, `uv run pytest`, `ruff`, `mypy`
- THEN no `.venv`, `__pycache__`, `.ruff_cache`, `.mypy_cache`, or `htmlcov` entries appear

## MODIFIED Requirements

### Requirement: Test Runner and Coverage Gate

`pytest` SHALL be the runner with `--cov-fail-under=80` against `app/`. The `app/` package SHALL exist (empty `app/__init__.py` marker) so coverage is measurable from day one.

#### Scenario: Smoke test satisfies the coverage floor

- GIVEN `tests/test_smoke.py` and the empty `app/__init__.py` marker exist
- WHEN a developer runs `uv run pytest`
- THEN the smoke test passes and the 80% gate is satisfied (pytest-cov reports 100% on the empty package)

> 2026-06-05 — MODIFIED: empty `app/__init__.py` added so the 80% gate is satisfiable on day one. pytest-cov requires an importable target; an empty package marker provides 100% coverage of zero statements.

## Out of Scope (Non-Requirements)

Explicitly NOT part of this capability, deferred to later changes:
- FastAPI and the trading application code (next change)
- Runtime dependencies (deferred until app code lands)
- CI workflows under `.github/workflows/`
- Docker images, deployment manifests, container registries
- Database, persistence layer, brokers, exchange connectors
- Frontend assets, static files, CDN, auth systems
