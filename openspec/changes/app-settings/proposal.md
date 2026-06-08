# Proposal: App Settings

## Intent

Enable local development with `make run` by adding **uvicorn** (dev server) and **pydantic-settings** (env-based config). Pure dev infrastructure — no domain features, no spec-level behavior changes.

## Scope

### In Scope
- `app/settings.py`: `BaseSettings` class with `APP_NAME`, `DEBUG`, `HOST`, `PORT`
- `.env.example`: documented env vars template (git-tracked)
- `pyproject.toml`: add `uvicorn` and `pydantic-settings` as runtime deps
- `Makefile`: add `run` target — `uv run uvicorn app.main:app --reload`
- `uv.lock`: regenerated via `uv lock`
- `tests/test_settings.py`: settings loading and env override contract

### Out of Scope
- Production config (Docker, systemd, reverse proxy)
- httpx pin changes or other dep bumps
- Domain features or endpoint changes
- `.env` committed to repo (gitignored — only `.env.example` tracked)

## Capabilities

> Pure dev infrastructure — no spec-level behavior changes.

### New Capabilities
None.

### Modified Capabilities
None.

## Approach

1. Add `uvicorn` and `pydantic-settings` to `pyproject.toml` `[project] dependencies`
2. Run `uv lock` to regenerate `uv.lock`
3. Create `app/settings.py` with a `Settings(BaseSettings)` class (model_config from `.env`)
4. Create `.env.example` documenting every var (HOST, PORT, APP_NAME, DEBUG)
5. Create `tests/test_settings.py` for default values and env-override behavior
6. Add `run` target to `Makefile`
7. Wire settings into `app/main.py` app instantiation (minimal — pass `title`)

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `pyproject.toml` | Modified | Add uvicorn + pydantic-settings deps |
| `uv.lock` | Modified | Regenerated lockfile |
| `Makefile` | Modified | Add `run` target |
| `app/settings.py` | New | Settings class (pydantic-settings) |
| `.env.example` | New | Documented env vars template |
| `tests/test_settings.py` | New | Settings contract tests |
| `app/main.py` | Modified | Wire settings into FastAPI init |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| pydantic-settings picks up unexpected env vars | Low | Explicit model config; test documents every known var |
| uvicorn version conflict with fastapi | Low | Pulled automatically; both from same ecosystem |
| uvicorn added as runtime dep (not dev) | Low | Deliberate — used for dev today, may run prod later |

## Rollback Plan

Revert `pyproject.toml` dep additions, delete `app/settings.py`, `.env.example`, `tests/test_settings.py`, remove `run` target from `Makefile`, and run `uv lock` to restore `uv.lock`.

## Dependencies

- `uvicorn` — ASGI server for local dev
- `pydantic-settings` — env-based config (ships pydantic dependency)

## Success Criteria

- [ ] `make run` starts the server on `http://0.0.0.0:8000` (defaults)
- [ ] `GET /health` returns 200 when served via uvicorn
- [ ] `pydantic-settings` reads `APP_NAME` from `.env` and falls back to default
- [ ] All existing tests pass with coverage >= 80%
- [ ] `uv run mypy .` passes with zero errors (new code is fully typed)
