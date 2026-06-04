# Tasks: Bootstrap Python Toolchain

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~280-350 (pyproject ~50, .gitignore ~15, tests ~10, .gga diff ~3, openspec diff ~1, uv.lock ~200-270) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single commit, single PR |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: stacked-to-main
400-line budget risk: Low

> Lockfile dominates line count but is generated; splitting would scatter coupled files.

## Dependencies

- `uv` MUST be on PATH before Phase 3 (host prerequisite, not delivered here).
- Phase 2 depends on Phase 1. Phase 3 depends on Phases 1+2. Phase 4 depends on Phase 3.

## 1.0 Project Foundation

- [x] 1.1 Create `.python-version` at the repo root containing the single line `3.12`.

- [x] 1.2 Create `pyproject.toml` with all sections from the spec: `[project]` (name, version, requires-python=">=3.12,<3.13", empty dependencies); `[dependency-groups].dev` (pytest, pytest-cov, ruff, mypy); `[tool.uv]` (package=false); `[tool.pytest.ini_options]` (testpaths=tests, addopts with 80% coverage gate against `app`); `[tool.ruff]` (py312, line-length 100, rules E/F/I/B/UP/SIM/S, isort, format); `[tool.mypy]` (strict=true, python_version=3.12).

- [x] 1.3 Create `.gitignore` with the Python-standard ignore list from the spec (venv, caches, build, coverage, egg-info).

- [x] 1.4 Create empty `tests/__init__.py` and `tests/test_smoke.py` with a docstring noting FastAPI imports are deferred and `def test_math_still_works() -> None: assert 1 + 1 == 2`. NO fastapi/httpx/pydantic-settings imports.

- [x] 1.5 Create empty `app/__init__.py` package marker. The file MUST be empty (or a single comment line) — zero source lines. This package is the destination for the upcoming FastAPI application; the marker exists so that `pytest --cov=app` has an importable module to measure. Authorized during apply-phase recovery (spec MODIFIED: Test Runner and Coverage Gate; see apply-progress 2026-06-05).

## 2.0 Tool Config

- [x] 2.1 Modify `.gga` to switch GGA into Python mode. Leave PROVIDER, RULES_FILE, STRICT_MODE, TIMEOUT untouched. Required diff: `FILE_PATTERNS="*.py"`; `EXCLUDE_PATTERNS="*_test.py,test_*.py,conftest.py,.venv/*,__pycache__/*,.pytest_cache/*,.ruff_cache/*,.mypy_cache/*,htmlcov/*"`; append `MODE="balanced"`.

- [x] 2.2 Update `openspec/config.yaml` line 24: flip `apply.tdd: false` to `apply.tdd: true`. Leave all other lines untouched.

- [x] 2.3 Read both files back; confirm only the in-scope fields changed.

## 3.0 Install and Verify

- [x] 3.1 Run `uv sync` from the workspace root. If `uv` is not on PATH, STOP and tell the user to install it (https://docs.astral.sh/uv/). Do NOT fall back to pip. MUST exit 0 and create `uv.lock`.

- [x] 3.2 Re-run `uv run pytest` after creating `app/__init__.py`. The smoke test passes and the coverage gate is satisfied (pytest-cov reports 100% on the empty package; no application source code is in scope of this change).

- [x] 3.3 Run `uv run ruff check .` and `uv run ruff format --check .`. Both MUST exit 0.

- [x] 3.4 Run `uv run mypy .`. MUST exit 0 (strict baseline over empty `app/` is the deliberate no-source load test).

- [x] 3.5 Run `uv lock --check`. MUST exit 0. If it fails, regenerate via `uv lock` and re-run.

- [x] 3.6 Re-read `openspec/config.yaml` and confirm `apply.tdd: true` is on disk before staging.

## 4.0 Commit

- [x] 4.0 Branch `chore/bootstrap-toolchain` already created from the previous blocked run (no prior commits).

- [x] 4.1 Stage ONLY in-scope files. One work-unit commit: `chore(toolchain): bootstrap python 3.12 with uv, pytest, ruff, mypy strict`. No `Co-Authored-By` line. No micro-commits.

- [x] 4.2 Do NOT open a PR unless the user explicitly asks. Default: clean local commit on the feature branch.

## Verification (all from repo root, all must pass)

- [x] V.1 `uv sync` exits 0; `uv.lock` produced.
- [x] V.2 `uv run pytest` exits 0; smoke test passes; coverage gate does not fail.
- [x] V.3 `uv run ruff check .` exits 0.
- [x] V.4 `uv run ruff format --check .` exits 0.
- [x] V.5 `uv run mypy .` exits 0.
- [x] V.6 `uv lock --check` exits 0.
- [x] V.7 `git status` shows no venv/caches/coverage artefacts.
- [x] V.8 `grep tdd openspec/config.yaml` shows `apply.tdd: true`.
- [x] V.9 `grep FILE_PATTERNS .gga` shows `FILE_PATTERNS="*.py"`.
