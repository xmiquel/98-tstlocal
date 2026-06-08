# Delta for trading-domain

## Purpose

First domain capability for the trading application. Establishes Pydantic
model patterns, CRUD endpoint patterns, in-memory store pattern, and test
isolation — the template all future domain features follow. This moves the
project from "the toolchain works" to "the application does something useful."

## ADDED Requirements

### Requirement: Strategy CRUD

The system SHALL expose a complete CRUD interface for trading strategies
via the existing FastAPI application. Pydantic models (`StrategyCreate`,
`Strategy`) SHALL be defined in `app/schemas.py`. An in-memory
`StrategyStore` SHALL be defined in `app/store.py` with `list()`,
`create()`, `get()`, `delete(id)`, and `clear()` methods. Four endpoints
SHALL be registered on the existing `app.main.app` instance. The store
SHALL expose a `clear()` method callable from test fixtures for isolation.
All source code SHALL follow strict TDD: the test commit SHALL precede
the implementation commit. Zero new dependencies SHALL be introduced —
pydantic ships with FastAPI, UUID and datetime are stdlib.

#### Scenario: GET /strategies returns empty list on empty store

- GIVEN the store contains no strategies
- WHEN a client sends `GET /strategies`
- THEN the response status is 200 and the JSON body is `[]`

#### Scenario: POST /strategies returns 201 with created strategy

- GIVEN a valid `StrategyCreate` JSON payload
- WHEN a client sends `POST /strategies`
- THEN the response status is 201 and the JSON body contains `"id"`, `"name"`, and `"created_at"`

#### Scenario: GET /strategies returns all created strategies

- GIVEN the store contains strategies created via POST
- WHEN a client sends `GET /strategies`
- THEN the response status is 200 and the JSON body is a non-empty list containing all strategies

#### Scenario: GET /strategies/{id} returns 200 for existing strategy

- GIVEN a strategy exists in the store
- WHEN a client sends `GET /strategies/{id}` with that strategy's ID
- THEN the response status is 200 and the JSON body matches the strategy

#### Scenario: GET /strategies/{id} returns 404 for non-existent id

- GIVEN no strategy with the given ID exists
- WHEN a client sends `GET /strategies/{non-existent-id}`
- THEN the response status is 404

#### Scenario: DELETE /strategies/{id} returns 204 and removes strategy

- GIVEN a strategy exists in the store
- WHEN a client sends `DELETE /strategies/{id}` with that strategy's ID
- THEN the response status is 204 AND the strategy is no longer returned by subsequent GET requests

#### Scenario: DELETE /strategies/{id} returns 404 for non-existent id

- GIVEN no strategy with the given ID exists
- WHEN a client sends `DELETE /strategies/{non-existent-id}`
- THEN the response status is 404

#### Scenario: store.clear() isolates tests

- GIVEN a test that creates strategies via POST
- WHEN a subsequent test runs
- THEN each test MUST have a clean store via an autouse fixture calling `store.clear()` before the test body runs

#### Scenario: Strict TDD — test commit precedes implementation commit

- GIVEN the apply phase produces commits for this requirement
- WHEN `git log --oneline` is inspected on the feature branch
- THEN a `test(strategies):` commit appears before the corresponding `feat(strategies):` commit

## Out of Scope (Non-Requirements)

Frontend, persistence, MT5, auth, settings, uvicorn, httpx warning,
business logic beyond CRUD, `make run` target.
