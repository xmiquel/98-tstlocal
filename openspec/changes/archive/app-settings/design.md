# Design: App Settings

## Technical Approach

Add `pydantic-settings`-based env config and a `uvicorn` dev server. The `Settings` singleton loads from `.env` at import time and wires into `FastAPI()` construction. The `make run` target launches uvicorn with hot-reload. Tests validate defaults, env overrides, and type coercion — no import-order hacks needed.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Settings lifecycle | App-level singleton `settings = Settings()` | Lazy init, DI per-request | Matches existing module-level `app` pattern. Static config doesn't need per-request DI — over-engineering for four fields. |
| Settings fields | `APP_NAME: str`, `DEBUG: bool`, `HOST: str`, `PORT: int` | Single dict, YAML file, TOML | pydantic gives type safety + env fallback + `.env` file support in one class. 12-factor standard. |
| Wiring to FastAPI | `FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)` | Import settings in endpoint handlers | title/debug are app-level constructor args, not per-request. One-line diff. |
| uvicorn config | Makefile `HOST`/`PORT` vars, passed as CLI args | `uvicorn.run()` in `main.py`, uvicorn TOML config | Keeps `main.py` focused on domain wiring. CLI args are self-documenting in the Makefile target. |
| Testing approach | Fresh `Settings(**overrides)` per test | `monkeypatch` before import, `importlib.reload` | Creating instances directly is simpler and avoids import-ordering fragility. |

## Data Flow

```
.env ──→ pydantic-settings ──→ Settings(APP_NAME, DEBUG, HOST, PORT)
                                     │
                                     ├──→ FastAPI(title=..., debug=...)
                                     │
                                     └──→ make run (HOST/PORT → uvicorn CLI)
```

Resolution order: explicit env var > `.env` file > class default.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/settings.py` | Create | `Settings(BaseSettings)` — 4 typed fields, `env_file=".env"` |
| `.env.example` | Create | Documented template with defaults and descriptions. Git-tracked. |
| `.gitignore` | Modify | Add `.env` to prevent accidental commit |
| `pyproject.toml` | Modify | Add `uvicorn` + `pydantic-settings` to `[project] dependencies` |
| `Makefile` | Modify | Add `HOST`, `PORT` vars + `run` target |
| `app/main.py` | Modify | Import `settings`, pass to `FastAPI(title=..., debug=...)` |
| `tests/test_settings.py` | Create | Settings contract — defaults, env override, type coercion |
| `.env` | Create (gitignored) | Local overrides — NOT tracked. Copy from `.env.example`. |

## Interfaces / Contracts

```python
# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "98-tstlocal"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Default values | `Settings()` with no env — assert all 4 defaults |
| Unit | Env override | `Settings(HOST="1.2.3.4")` — assert field overridden, others unchanged |
| Unit | Type coercion | `Settings(DEBUG="true")` → `bool(True)`, `PORT="9000"` → `int(9000)` |
| Integration | App startup | Existing `TestClient` tests pass — no import-order regression |

## Migration / Rollout

No migration required. Developers copy `.env.example → .env` and customize. `.env` is gitignored — never committed.

## Open Questions

None.
