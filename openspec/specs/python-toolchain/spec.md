# Delta for python-toolchain

## Purpose

The `python-toolchain` capability installs a strict Python development environment for the upcoming FastAPI trading app. Pinning Python 3.12, committing `uv.lock`, and configuring pytest (80% coverage gate), ruff (with security rules), and mypy `--strict` from day one lets every later change inherit TDD, lint, and type safety as a foundation. The capability flips `openspec/config.yaml` `apply.tdd` to `true` and switches `.gga` to Python mode, unlocking RED→GREEN→REFACTOR. The CI quality contract established in `ci-quality-gate` enforces this contract on every pull request, so the rules captured here are no longer local-only. The dev-tooling cycle landed local pre-commit hooks (`ruff format`, `ruff check --fix`, `mypy`) for fast feedback, a `Makefile` wrapping the test runner and the full quality chain in the same order as the CI workflow, Dependabot auto-updates for GitHub Actions and `pyproject.toml` dev-deps, an `AGENTS.md` for future AI/agents, and tightened dev-dep pins from `>=` to `~=` so breaking bumps are blocked while patches flow through. This change ships zero application code.

## ADDED Requirements

### Requirement: Toolchain Pinning and Lockfile

Python 3.12.x SHALL be pinned via `.python-version` and `pyproject.toml` `requires-python = ">=3.12,<3.13"`. All runtime and dev dependencies SHALL be declared in `pyproject.toml`. Dev-dependencies (`pytest`, `pytest-cov`, `ruff`, `mypy`) SHALL be pinned with the compatible-release specifier `~=` to allow patch updates while blocking breaking bumps. `pre-commit` SHALL be declared as a dev-dependency. `uv.lock` SHALL be committed. `uv sync` SHALL be the canonical install command. The verification step SHALL run `uv lock --check`; if it fails the change MUST be marked failed and `uv.lock` regenerated. The CI workflow SHALL run `uv lock --check` on every pull request targeting `main`; the step SHALL exit non-zero on lockfile drift.
(Previously: dev-deps used `>=` specifiers; `pre-commit` was not a dev-dep; Dependabot did not track `pyproject.toml`.)

> Satisfies: dev-dep version tightening (`>=` → `~=`) for `pytest`, `pytest-cov`, `ruff`, `mypy`; `pre-commit` added to dev-deps; Dependabot tracking on `pyproject.toml` dev-deps.

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

#### Scenario: Dev-dependency pins use compatible-release specifier

- GIVEN `pyproject.toml` lists dev-deps (`pytest`, `pytest-cov`, `ruff`, `mypy`) and `pre-commit`
- WHEN `uv lock` is run
- THEN all 4 dev-deps use `~=` specifiers and `uv lock` resolves without constraint errors

#### Scenario: Dependabot tracks dev-dependency version bumps

- GIVEN `.github/dependabot.yml` declares the `uv` ecosystem (or `pip` fallback if `uv` is not yet supported) with the `pyproject.toml` path
- WHEN Dependabot runs
- THEN it proposes PRs for dev-deps whose latest release is within the `~=` range but not yet locked

### Requirement: Code Quality (Lint, Format, Type Check)

`ruff` SHALL be the linter and formatter with rule sets `E`, `F`, `I`, `B`, `UP`, `SIM`, `S`. `ruff check .` and `ruff format --check .` SHALL pass with zero findings. `mypy` SHALL run with `strict = true`; type hints SHALL be present on every public function and method added in any subsequent change. `mypy .` SHALL pass with zero errors. The project SHALL ship a `.pre-commit-config.yaml` declaring 3 hooks (`ruff format`, `ruff check --fix`, `mypy`) that run on `git commit` for fast local feedback; the hooks SHALL be local-only and SHALL NOT be invoked in CI (CI mirrors the same checks via `uv run`). The CI workflow SHALL run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy .` on every pull request targeting `main`; all three SHALL exit zero or the run SHALL be marked failed.
(Previously: pre-commit hooks were not installed; ruff and mypy checks ran only in CI and via direct local invocations.)

> Satisfies: local pre-commit hooks (`ruff format`, `ruff check --fix`, `mypy`) for fast feedback; CI continues to mirror the same checks via `uv run`.

#### Scenario: Clean lint, format, and type check

- GIVEN committed code conforms to rule sets and is fully hinted
- WHEN a developer runs `ruff check .`, `ruff format --check .`, and `mypy .`
- THEN all three exit with code 0

#### Scenario: Lint error fails CI on a PR

- GIVEN a PR introduces a lint finding (e.g. an unused import)
- WHEN the CI workflow runs `uv run ruff check .`
- THEN that step exits non-zero and the run is marked failed

#### Scenario: Pre-commit hook runs ruff format on commit

- GIVEN `.pre-commit-config.yaml` is installed via `uv run pre-commit install`
- WHEN a developer runs `git commit` on a file that has formatting drift
- THEN the commit is blocked and `ruff format` reformats the file

#### Scenario: Pre-commit hook runs ruff check on commit

- GIVEN a staged file with a lint error
- WHEN `git commit` is attempted
- THEN the commit is blocked with the ruff error message

#### Scenario: Pre-commit hook runs mypy on commit

- GIVEN a staged file with a type error
- WHEN `git commit` is attempted
- THEN the commit is blocked with the mypy error message

#### Scenario: Pre-commit bypass flag works for emergencies

- GIVEN a developer needs to bypass hooks temporarily
- WHEN they pass `--no-verify` to `git commit`
- THEN the commit succeeds (mitigation: CI still runs the same checks on the PR)

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

### Requirement: Dependabot

The project SHALL contain `.github/dependabot.yml` configuring Dependabot to keep the project's dependencies current and reduce manual maintenance. Dependabot SHALL track both the `github-actions` ecosystem (for action version bumps, including the forced Node 24 migration on 2026-06-16) and a Python ecosystem (`uv` primary, `pip` fallback if `uv` is not yet supported) for `pyproject.toml` dev-deps. Dependabot PRs SHALL be auto-merged using squash strategy when the `Quality Gate` CI check passes and the repo has auto-merge enabled.

> Satisfies: auto-update of GitHub Actions and `pyproject.toml` dev-deps; auto-merge on CI green reduces PR noise.

#### Scenario: Dependabot tracks GitHub Actions

- GIVEN `.github/dependabot.yml` declares the `github-actions` ecosystem with the project's workflow path (`.github/workflows/ci.yml`)
- WHEN Dependabot runs
- THEN it opens PRs for `actions/checkout` and `astral-sh/setup-uv` when new versions are released

#### Scenario: Dependabot tracks Python dependencies

- GIVEN `.github/dependabot.yml` declares the `uv` ecosystem (or `pip` fallback if `uv` is not yet supported) with the `pyproject.toml` path
- WHEN Dependabot runs
- THEN it opens PRs for dev-deps whose latest version is not yet locked

#### Scenario: Dependabot auto-merges when CI is green

- GIVEN the repo has auto-merge enabled (`gh repo view` reports `auto-merge: enabled`) and Dependabot PRs are labeled with `dependencies`
- WHEN the `Quality Gate` check passes on a Dependabot PR
- THEN the PR is auto-merged using squash strategy

### Requirement: Pre-commit Hooks

The project SHALL ship a `.pre-commit-config.yaml` declaring 3 local pre-commit hooks (`ruff format`, `ruff check --fix`, `mypy`) that run on `git commit` for fast local feedback. The hooks SHALL be local-only; the CI workflow SHALL NOT invoke `pre-commit run` and SHALL mirror the same checks via `uv run`. `pre-commit` SHALL be declared in dev-dependencies. `AGENTS.md` SHALL document the one-time install step (`uv run pre-commit install`).

> Satisfies: local quality gates (`ruff format`, `ruff check --fix`, `mypy`) on `git commit` for fast feedback; CI remains the source of truth.

#### Scenario: Pre-commit configuration declares 3 hooks

- GIVEN `.pre-commit-config.yaml` exists at the repo root
- WHEN a developer reads the file
- THEN it declares exactly 3 hooks: `ruff format`, `ruff check --fix`, and `mypy`

#### Scenario: Pre-commit install is documented in AGENTS.md

- GIVEN a developer reads `AGENTS.md`
- WHEN they look for setup instructions
- THEN they find a section explaining how to run `uv run pre-commit install` once after cloning

#### Scenario: Pre-commit hooks are local-only

- GIVEN the CI workflow file (`.github/workflows/ci.yml`)
- WHEN a developer inspects its steps
- THEN no step runs `pre-commit run` (CI mirrors the checks directly via `uv run`)

### Requirement: Makefile Targets

The project SHALL ship a `Makefile` at the repo root exposing 7 named targets that wrap the test runner and the full quality chain. All targets SHALL delegate to `uv run <tool>` rather than calling the tool directly. The `ci` target SHALL run the 6 local quality commands in the same order as the 6 quality steps in `.github/workflows/ci.yml`.

> Satisfies: 7 named Makefile targets (`test`, `lint`, `format`, `format-check`, `typecheck`, `lock-check`, `ci`) wrapping the same `uv run` invocations the CI workflow uses, in the same order.

#### Scenario: Makefile has 7 named targets

- GIVEN the `Makefile` exists at the repo root
- WHEN a developer runs `make help` or inspects the file
- THEN exactly 7 named targets are documented: `test`, `lint`, `format`, `format-check`, `typecheck`, `lock-check`, `ci`

#### Scenario: All Makefile targets delegate to `uv run`

- GIVEN any Makefile target
- WHEN a developer inspects its body
- THEN the body invokes `uv run <tool>` rather than calling the tool directly

#### Scenario: `make ci` matches the CI workflow order

- GIVEN a developer runs `make ci` on a clean tree
- WHEN the command completes
- THEN the 6 local quality commands ran sequentially in the same order as the 6 quality steps in `.github/workflows/ci.yml` and the exit code is 0

### Requirement: AGENTS.md

The project SHALL ship an `AGENTS.md` at the repo root providing project context for future AI/agents. The file SHALL have at least 4 required sections (Project overview, Pointers, Conventions, Known gotchas) and SHALL reference this spec from the top of the file.

> Satisfies: project documentation scaffold for AI/agents; 4 required sections (overview, pointers, conventions, gotchas) and a top-of-file OpenSpec reference.

#### Scenario: AGENTS.md exists at the repo root

- GIVEN a developer clones the repo
- WHEN they look for project documentation for AI agents
- THEN `AGENTS.md` exists at the repo root

#### Scenario: AGENTS.md has 4 required sections

- GIVEN `AGENTS.md` exists
- WHEN a developer reads it
- THEN it has at least these 4 sections: Project overview, Pointers (to `openspec/`, `README.md`, `Makefile`, `.pre-commit-config.yaml`), Conventions (Conventional Commits, no AI attribution, `uv run <tool>`), Known gotchas (PowerShell `RemoteException` on `uv`)

#### Scenario: AGENTS.md documents the `gh` CLI Windows path quirk

- GIVEN `AGENTS.md` exists
- WHEN a developer looks for `gh` CLI setup notes
- THEN they find a note about the winget install path quirk on Windows

#### Scenario: AGENTS.md has a top-of-file OpenSpec reference

- GIVEN `AGENTS.md` exists
- WHEN a developer reads the first 5 lines
- THEN there is a comment or note referencing `openspec/changes/dev-tooling/specs/python-toolchain/spec.md`

## MODIFIED Requirements

### Requirement: Test Runner and Coverage Gate

`pytest` SHALL be the runner with `--cov-fail-under=80` against `app/`. The `app/` package SHALL exist (empty `app/__init__.py` marker) so coverage is measurable from day one. A `Makefile` at the repo root SHALL expose `make test` as a thin wrapper around `uv run pytest` (passing the same flags the project uses) and SHALL expose `make ci` as a wrapper that runs the 6 local quality commands in the same order as the 6 quality steps in `.github/workflows/ci.yml` (the 2 CI-infra steps `actions/checkout` and `astral-sh/setup-uv` are skipped locally because they are CI infrastructure, not local commands). The CI workflow SHALL run `uv run pytest` on every pull request targeting `main`; the run SHALL exit non-zero if coverage falls below 80% or any test fails.
(Previously: `uv run pytest` was the only entry point to the test runner; no Makefile wrapper exposed the suite or the CI chain.)

> Satisfies: `make test` and `make ci` as thin `uv run` wrappers exposing the test runner and the full quality chain locally, in the same order as the CI workflow.

#### Scenario: Smoke test satisfies the coverage floor

- GIVEN `tests/test_smoke.py` and the empty `app/__init__.py` marker exist
- WHEN a developer runs `uv run pytest`
- THEN the smoke test passes and the 80% gate is satisfied (pytest-cov reports 100% on the empty package)

#### Scenario: Coverage below 80% fails CI on a PR

- GIVEN a PR that drops `app/` coverage to 70%
- WHEN the CI workflow runs `uv run pytest`
- THEN `--cov-fail-under=80` causes a non-zero exit and the run is marked failed

#### Scenario: Make target `make test` runs the test suite

- GIVEN a developer runs `make test`
- WHEN the command completes
- THEN `uv run pytest` was executed with the same flags the CI uses, and the exit code matches pytest's exit code

#### Scenario: Make target `make ci` runs the full quality chain

- GIVEN a developer runs `make ci`
- WHEN the command completes
- THEN the 6 local quality commands ran sequentially in the same order as the 6 quality steps in `.github/workflows/ci.yml` and the exit code is 0 on a clean tree

## Out of Scope (Non-Requirements)

Explicitly NOT part of this capability, deferred to later changes:
- FastAPI and the trading application code (next change)
- Runtime dependencies (deferred until app code lands)
- Docker images, deployment manifests, container registries
- Database, persistence layer, brokers, exchange connectors
- Frontend assets, static files, CDN, auth systems
