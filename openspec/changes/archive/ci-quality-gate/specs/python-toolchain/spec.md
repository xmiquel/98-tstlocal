# Delta for python-toolchain

## Purpose

Promote the python-toolchain quality contract from *documentation* to *enforcement* on every pull request. The 80% coverage gate, ruff lint/format, mypy strict, and `uv lock --check` are no longer local-only — they run on a GitHub Actions workflow that must pass before merge. This change ships one new file (`.github/workflows/ci.yml`) and adds CI-enforcement clauses to three existing requirements. No source files are modified.

## ADDED Requirements

### Requirement: Continuous Integration Workflow

The project SHALL contain `.github/workflows/ci.yml`, a GitHub Actions workflow enforcing the python-toolchain contract.

| Field | Value |
|-------|-------|
| Triggers | `push` to `main`, `pull_request` to `main`, `workflow_dispatch` |
| Runner | `windows-latest` |
| Permissions | `contents: read` |
| Concurrency | `group: ${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true` |

Steps (sequential, each exits non-zero on failure): `actions/checkout@v4`, `astral-sh/setup-uv@v3` (with built-in cache), `uv sync`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`, `uv run pytest`, `uv lock --check`.

#### Scenario: All three triggers run the eight-step quality gate
- GIVEN a push to `main`, a PR targeting `main`, or a manual `workflow_dispatch`
- WHEN the workflow runs on `windows-latest`
- THEN all eight steps execute in order; a non-zero exit on any step marks the run failed

#### Scenario: Failing test fails the pytest step
- GIVEN a PR containing a deliberate test failure (e.g. `assert False` in a smoke test)
- WHEN the workflow reaches `uv run pytest`
- THEN that step exits non-zero, the run is marked failed, and the PR cannot be merged while the check is failing

#### Scenario: Lint error fails the ruff check step
- GIVEN a PR introduces an unused import
- WHEN the workflow reaches `uv run ruff check .`
- THEN that step exits non-zero and the run is marked failed

#### Scenario: Lockfile drift fails the uv lock check step
- GIVEN `uv.lock` on the PR is out of sync with `pyproject.toml`
- WHEN the workflow reaches `uv lock --check`
- THEN that step exits non-zero and the run is marked failed

#### Scenario: Push to a non-main branch does not trigger the workflow
- GIVEN a developer pushes a commit to a feature branch (no PR)
- WHEN the workflow trigger evaluates the event
- THEN the `push` filter does NOT match (only `main` is configured) and the workflow does not run

### Requirement: Out of Scope — Branch Protection Rules

Branch protection configuration on GitHub (e.g. "require status checks to pass before merging") is a repository-settings change, NOT a code change. Configuring it is a documented follow-up outside the python-toolchain capability.

#### Scenario: Failing PR may still merge before branch protection is configured
- GIVEN the CI workflow reports a failed check on a PR and branch protection is not yet set
- WHEN a maintainer with admin rights attempts to merge
- THEN the merge MAY succeed; the contract relies on the workflow existing, not on GitHub settings

## MODIFIED Requirements

### Requirement: Toolchain Pinning and Lockfile

Python 3.12.x SHALL be pinned via `.python-version` and `pyproject.toml` `requires-python = ">=3.12,<3.13"`. All runtime and dev dependencies SHALL be declared in `pyproject.toml`. `uv.lock` SHALL be committed. `uv sync` SHALL be the canonical install command. The verification step SHALL run `uv lock --check`; if it fails the change MUST be marked failed and `uv.lock` regenerated. The CI workflow SHALL run `uv lock --check` on every pull request targeting `main`; the step SHALL exit non-zero on lockfile drift.
(Previously: lockfile check was a local verification only.)

#### Scenario: A developer clones the repo
- GIVEN a fresh clone with `uv` on PATH
- WHEN the developer runs `uv sync`
- THEN Python 3.12.x is selected from `.python-version` and the env installs deterministically

#### Scenario: Lockfile drift fails verification locally
- GIVEN `pyproject.toml` declares a version not yet in `uv.lock`
- WHEN the verification step runs `uv lock --check`
- THEN the change SHALL be marked failed

#### Scenario: Lockfile drift fails CI on a PR
- GIVEN a PR with `uv.lock` out of sync with `pyproject.toml`
- WHEN the CI workflow runs `uv lock --check`
- THEN the step exits non-zero and the run is marked failed

### Requirement: Code Quality (Lint, Format, Type Check)

`ruff` SHALL be the linter and formatter with rule sets `E`, `F`, `I`, `B`, `UP`, `SIM`, `S`. `ruff check .` and `ruff format --check .` SHALL pass with zero findings. `mypy` SHALL run with `strict = true`; type hints SHALL be present on every public function and method added in any subsequent change. `mypy .` SHALL pass with zero errors. The CI workflow SHALL run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy .` on every pull request targeting `main`; all three SHALL exit zero or the run SHALL be marked failed.
(Previously: lint, format, and type checks were a local contract only.)

#### Scenario: Clean lint, format, and type check
- GIVEN committed code conforms to rule sets and is fully hinted
- WHEN a developer runs `ruff check .`, `ruff format --check .`, and `mypy .`
- THEN all three exit with code 0

#### Scenario: Lint error fails CI on a PR
- GIVEN a PR introduces a lint finding (e.g. an unused import)
- WHEN the CI workflow runs `uv run ruff check .`
- THEN that step exits non-zero and the run is marked failed

### Requirement: Test Runner and Coverage Gate

`pytest` SHALL be the runner with `--cov-fail-under=80` against `app/`. The `app/` package SHALL exist (empty `app/__init__.py` marker) so coverage is measurable from day one. The CI workflow SHALL run `uv run pytest` on every pull request targeting `main`; the run SHALL exit non-zero if coverage falls below 80% or any test fails.
(Previously: the coverage gate was a local contract only.)

#### Scenario: Smoke test satisfies the coverage floor
- GIVEN `tests/test_smoke.py` and the empty `app/__init__.py` marker exist
- WHEN a developer runs `uv run pytest`
- THEN the smoke test passes and the 80% gate is satisfied

#### Scenario: Coverage below 80% fails CI on a PR
- GIVEN a PR that drops `app/` coverage to 70%
- WHEN the CI workflow runs `uv run pytest`
- THEN `--cov-fail-under=80` causes a non-zero exit and the run is marked failed

## REMOVED Requirements

None.

## Out of Scope (Non-Requirements)

Explicitly NOT part of this change: GitHub branch protection rules; Dependabot; pre-commit hooks; version pinning beyond `pyproject.toml`; Makefile / taskfile; AGENTS.md note on PowerShell `RemoteException`; MT5-specific CI; release / deployment workflows, container images, deploy manifests; cross-platform runners (Linux, macOS); multi-version Python matrix.
