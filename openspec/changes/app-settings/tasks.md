# Tasks: App Settings

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~145 (30 code + 15 test + 100 lockfile) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Full app-settings change | PR 1 | Single PR; base = main; all tasks in one batch |

## Phase 1: Foundation

- [x] 1.1 Add `uvicorn` and `pydantic-settings` to `pyproject.toml` `[project] dependencies`
- [x] 1.2 Run `uv lock` to regenerate `uv.lock`
- [x] 1.3 Create `app/settings.py` — `Settings(BaseSettings)` with `APP_NAME`, `DEBUG`, `HOST`, `PORT`; `env_file=".env"`
- [x] 1.4 Create `.env.example` — documented template for every env var with defaults
- [x] 1.5 Add `.env` to `.gitignore`

## Phase 2: Integration

- [x] 2.1 Wire `settings` into `app/main.py` — import singleton, use `FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)`
- [x] 2.2 Add `HOST`/`PORT` vars + `run` target to `Makefile` — `uv run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload`
- [x] 2.3 Create `.env` (gitignored) with local dev overrides for testing

## Phase 3: Testing

- [x] 3.1 Create `tests/test_settings.py` — test default values for all 4 fields
- [x] 3.2 Test env override via `Settings(HOST="1.2.3.4")` — verify override, others unchanged
- [x] 3.3 Test type coercion: `DEBUG="true"` → `True`, `PORT="9000"` → `9000`
