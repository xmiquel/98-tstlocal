# Delta for python-toolchain

## Purpose

Land the first real application code in `98-tstlocal`: a minimal
FastAPI surface in `app/main.py` plus a TestClient contract test in
`tests/test_health.py`. The slice turns the 80% coverage gate from
vacuous (100% of 0 statements) into a real signal. The 8-step CI
quality gate, ruff, mypy, the lockfile, pre-commit, and Dependabot
all keep working unchanged. The slice deliberately does NOT add
`uvicorn`, lifespan, middleware, CORS, persistence, auth, settings,
or endpoints beyond `/health`.

## ADDED Requirements

### Requirement: Application Runtime

The project SHALL ship a minimal FastAPI surface that proves the
runtime-dep toolchain works end-to-end. The application SHALL be a
module-level `FastAPI` instance (not a factory) exposed from
`app.main` under the name `app`, annotated `app: FastAPI = FastAPI()`
so the declaration passes `mypy --strict` -- the simplest pattern
for a single-process skeleton. The instance SHALL expose exactly one
endpoint: `GET /health`, returning HTTP 200 with a JSON body equal
to `{"status": "ok"}`. The endpoint SHALL NOT require authentication,
a database connection, or any startup state. The project SHALL ship
`tests/test_health.py` that drives the endpoint with
`from fastapi.testclient import TestClient` and asserts on the
response status code and the JSON body. The runtime dependencies
`fastapi` and `httpx` SHALL be declared in `pyproject.toml` under
`[project] dependencies` using `~=`, with `~=0.116` and `~=0.27` as
the locked minor lines. `uvicorn` SHALL NOT be a runtime dependency
in this slice. The apply phase SHALL follow strict TDD: the test
commit lands before the implementation commit that makes it pass.

> Satisfies: first real app code; minimal FastAPI surface; TestClient
> contract test; `~=` runtime pins; explicit `uvicorn` deferral;
> RED-before-GREEN.

#### Scenario: FastAPI instance is importable from `app.main`

- GIVEN `pyproject.toml` declares `fastapi~=0.116` and `httpx~=0.27` in `[project] dependencies`
- WHEN a developer runs `python -c "import app.main; from fastapi import FastAPI; assert isinstance(app.main.app, FastAPI)"`
- THEN the import succeeds and the symbol is a `FastAPI` instance

#### Scenario: `GET /health` returns 200 with the documented body

- GIVEN a `FastAPI` instance with a `GET /health` route returning `{"status": "ok"}`
- WHEN a `TestClient` issues a `GET /health` request
- THEN the response status code is 200 AND the JSON body equals `{"status": "ok"}`

#### Scenario: `/health` has no auth, database, or persistence dependencies

- GIVEN the application exposes `GET /health` and registers no auth middleware, database connection, or persistence layer
- WHEN a `TestClient` issues an unauthenticated `GET /health` request
- THEN the response status code is 200 (auth, DB, and persistence are explicitly deferred)

#### Scenario: TestClient test file exercises the `/health` contract

- GIVEN `tests/test_health.py` exists and imports `from fastapi.testclient import TestClient`
- WHEN a developer runs `uv run pytest tests/test_health.py`
- THEN the suite passes with at least one assertion on the `/health` status code and JSON body

#### Scenario: Runtime dependencies are declared with `~=` pins

- GIVEN the slice's `pyproject.toml`
- WHEN a developer inspects `[project] dependencies`
- THEN the list contains exactly `fastapi~=0.116` and `httpx~=0.27` AND `uv lock` resolves without constraint errors

#### Scenario: `uvicorn` is not a runtime dependency yet

- GIVEN the slice's `pyproject.toml`
- WHEN a developer inspects `[project] dependencies`
- THEN `uvicorn` is NOT in the list (deferred to a future slice that adds a run target or a runnable endpoint)

#### Scenario: Strict TDD -- test commit precedes implementation commit

- GIVEN the apply phase produces a work-unit sequence for this slice
- WHEN `git log --oneline` is run on the feature branch
- THEN a `test(health):` commit appears before the corresponding `feat(health):` commit

## Out of Scope (Non-Requirements)

Deferred to later changes: `uvicorn` runtime dep and any `make run` target; application lifespan and startup/shutdown events; middleware (CORS, GZip, trusted hosts); persistence (database, ORM, file storage); auth (API keys, OAuth2, JWT); settings / env loading; additional endpoints beyond `GET /health`; frontend, templates, static files, `fastapi[standard]` extras; the `httpx 0.27` `DeprecationWarning` cosmetic; MT5 / Windows-specific runtime deps.
