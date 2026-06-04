# Proposal: Bootstrap Python Toolchain

## Intent

Land a strict Python toolchain FIRST so the upcoming FastAPI trading app inherits TDD, lint cleanliness, and type safety from day one. Adds testing/linting/typing infra and flips `openspec/config.yaml` `apply.tdd` to `true`. Ships zero application code.

## Scope

### In Scope
- `pyproject.toml` — uv-managed, Python 3.12, single source of truth
- `uv.lock` — committed for reproducibility
- `.python-version` — pin 3.12
- `ruff.toml` with rule sets `E, F, I, B, UP, SIM, S` (S = security is mandatory: money-adjacent app)
- `mypy.ini` with `strict = true` (no-source baseline tolerates empty source for now)
- pytest config (in `pyproject.toml`) with `--cov-fail-under=80`
- `tests/test_smoke.py` asserting `1 + 1 == 2` (`import fastapi` deferred to next change)
- `.gitignore` — Python standard ignores
- `.gga` — switch to Python: `FILE_PATTERNS="*.py"`, updated `EXCLUDE_PATTERNS`, `MODE=balanced`; keep other defaults
- `openspec/config.yaml` — flip `apply.tdd: false → true`

### Out of Scope
- FastAPI / app code, runtime dependencies (next change)
- CI, `.github/workflows/`, Docker, deployment
- Trading domain (strategies, backtest, persistence)

## Capabilities

### New Capabilities
- `python-toolchain`: Strict Python dev toolchain — uv-managed Python 3.12, pytest+coverage (80% gate), ruff (incl. S=security), mypy `--strict`, `.gga` Python-mode. Foundation subsequent changes MUST inherit.

### Modified Capabilities
- None

## Approach

`pyproject.toml` declares Python 3.12 + dev-deps `pytest`, `pytest-cov`, `ruff`, `mypy` (no runtime deps yet). `uv sync` resolves `uv.lock` (committed for reproducibility). `ruff.toml` enables `E, F, I, B, UP, SIM, S`; `mypy.ini` enables `strict = true` with a no-source baseline that still exercises the toolchain. Pytest runs `tests/` with the 80% coverage gate (floor, not target). `.gitignore` blocks Python venv/cache artifacts. `.gga` re-patterns to `*.py` + test/venv/cache excludes + `MODE=balanced`. `openspec/config.yaml` flips `apply.tdd` to `true` — the unlock for strict TDD in subsequent changes.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `pyproject.toml` | New | uv project + dev-deps |
| `uv.lock`, `.python-version` | New | Pin + lockfile (lockfile committed) |
| `ruff.toml` | New | Lint config (E,F,I,B,UP,SIM,S) |
| `mypy.ini` | New | Type-check config (strict) |
| `pyproject.toml [tool.pytest.ini_options]` | New | Runner + 80% coverage gate |
| `tests/test_smoke.py` | New | Smoke test (`1+1==2`) |
| `.gitignore` | New | Python ignores |
| `.gga` | Modified | Switch to Python patterns + `MODE=balanced` |
| `openspec/config.yaml` | Modified | `apply.tdd: true` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `.gga` Python switch surfaces infra files (`.atl/`, `.windsurf/`, `openspec/`) on first run | Med | Expected; EXCLUDE list covers it. Follow-up change if scope creeps. |
| `mypy --strict` requires type hints on every new function | Med | Discipline baked into specs. No silent `Any` escape hatch. |
| 80% coverage gate is a floor, not a target — easy to game | Med | Floor enforced in CI (next change). PR review guards against drops. |
| `uv.lock` must be committed for reproducibility | Low | Listed in success criteria; CI will verify. |
| FastAPI import deferred — smoke test only proves runner | Low | Intentional scope guard against creep. |

## Alternatives Considered
- **pip + venv** — rejected: no lockfile, slower than `uv`.
- **poetry** — rejected: heavier; `uv` is the modern default and integrates with `pyproject.toml`.
- **ruff without `S`** — rejected: trading app is money-adjacent; security rules are mandatory.
- **mypy gradual typing** — rejected: cheaper to start `strict` than retrofit later.
- **`.gga` `strict` mode** — rejected for now: `balanced` matches the early-stage toolchain bootstrap; revisit when app code lands.

## Dependencies
- `uv` installed and on PATH (prerequisite; not delivered by this change).

## Rollback Plan

Single `git revert` — pure toolchain, no app code, no data, no migrations. Restore `.gga` and `openspec/config.yaml` from `HEAD~1`; delete `pyproject.toml`, `uv.lock`, `.python-version`, `ruff.toml`, `mypy.ini`, `tests/`, `.gitignore`.

## Success Criteria

- [ ] `uv sync` succeeds; `uv.lock` is committed.
- [ ] `pytest` runs and `tests/test_smoke.py` passes.
- [ ] `pytest --cov --cov-fail-under=80` passes.
- [ ] `ruff check .` and `ruff format --check .` exit clean.
- [ ] `mypy .` exits clean (no-source baseline still loads the toolchain).
- [ ] `openspec/config.yaml` shows `apply.tdd: true`.
- [ ] `.gga` shows `FILE_PATTERNS="*.py"` and the updated `EXCLUDE_PATTERNS`.

## Test & Verification Plan

From repo root, in order:
1. `uv sync`
2. `pytest`
3. `pytest --cov --cov-fail-under=80`
4. `ruff check .`
5. `ruff format --check .`
6. `mypy .`
7. `cat openspec/config.yaml` — confirm `tdd: true`
8. `cat .gga` — confirm `FILE_PATTERNS="*.py"` and updated `EXCLUDE_PATTERNS`

All eight steps must pass before the change is marked verified.
