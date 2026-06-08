# Trading Domain

## Purpose

First domain capability for the trading application. Establishes Pydantic
model patterns, CRUD endpoint patterns, in-memory store pattern, and test
isolation — the template all future domain features follow. This moves the
project from "the toolchain works" to "the application does something useful."

## Requirements

### Requirement: Strategy CRUD

The system SHALL expose a complete CRUD interface for trading strategies
via the existing FastAPI application. Pydantic models (`StrategyCreate`,
`StrategyUpdate`, `Strategy`) SHALL be defined in `app/schemas.py`. An in-memory
`StrategyStore` SHALL be defined in `app/store.py` with `list()`,
`create()`, `get()`, `update(id, data)`, `delete(id)`, and `clear()` methods. Five endpoints
SHALL be registered on the existing `app.main.app` instance. The store
SHALL expose a `clear()` method callable from test fixtures for isolation.
All source code SHALL follow strict TDD: the test commit SHALL precede
the implementation commit. Zero new dependencies SHALL be introduced —
pydantic ships with FastAPI, UUID and datetime are stdlib.
(Previously: Four endpoints, no update method or StrategyUpdate model)

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

#### Scenario: PUT /strategies/{id} returns 200 with updated strategy

- GIVEN a strategy exists in the store
- WHEN a client sends `PUT /strategies/{id}` with a valid `StrategyUpdate` payload
- THEN the response status is 200 AND the JSON body reflects the updated fields

#### Scenario: PUT /strategies/{id} returns 404 for non-existent id

- GIVEN no strategy with the given ID exists
- WHEN a client sends `PUT /strategies/{non-existent-id}` with any valid payload
- THEN the response status is 404

### Requirement: Strategy CRUD — Name Filter

The `GET /strategies` endpoint SHOULD accept an optional `name` query parameter for case-insensitive substring matching. When `name` is provided, the system MUST return only strategies whose name contains the given value. When omitted, the system MUST return all strategies (backward compatible).

#### Scenario: GET /strategies?name=MACD returns matching strategies

- GIVEN the store contains strategies named "MACD crossover", "RSI divergence", and "Bollinger squeeze"
- WHEN a client sends `GET /strategies?name=MACD`
- THEN the response status is 200 and the JSON body contains exactly "MACD crossover"
- AND strategies without "MACD" in their name are excluded

#### Scenario: GET /strategies?name=NonExistent returns empty list

- GIVEN the store contains strategies with various names
- WHEN a client sends `GET /strategies?name=NonExistent`
- THEN the response status is 200 and the JSON body is `[]`

### Requirement: Data Persistence

The system SHALL persist strategies to a SQLite database file so that all data survives application restarts. Persistence SHALL be transparent to clients — the existing route interface and response contracts SHALL remain unchanged. The database file SHALL be created automatically on first startup if it does not exist. On startup, the system SHALL load all previously persisted strategies into the active store.

#### Scenario: Created strategies survive server restart

- GIVEN a running application instance
- WHEN a client creates a strategy via POST /strategies
- AND the application is stopped and restarted
- THEN a subsequent GET /strategies SHALL return the previously created strategy

#### Scenario: Existing strategies are loaded from database on startup

- GIVEN a SQLite database file containing previously persisted strategies
- WHEN the application starts
- THEN the store SHALL contain all strategies from the database
- AND a GET /strategies SHALL return them without any client action

#### Scenario: Database file is created automatically if missing

- GIVEN no existing SQLite database file at the configured DATABASE_URL path
- WHEN the application starts
- THEN a new database file SHALL be created at that path
- AND the strategies table SHALL exist in the newly created file

#### Scenario: Strategy CRUD operations persist to database

- GIVEN the application is running with a SQLite-backed store
- WHEN a client performs any CRUD operation (POST, GET, PUT, DELETE)
- THEN mutations SHALL be committed to the database before the response is returned
- AND reads SHALL reflect the current state of the database

## Out of Scope (Non-Requirements)

Frontend, MT5, auth, settings, uvicorn, httpx warning,
business logic beyond CRUD, `make run` target.
