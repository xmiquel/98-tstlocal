# Delta for Trading Domain

## ADDED Requirements

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
