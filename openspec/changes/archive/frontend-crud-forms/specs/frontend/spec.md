# Delta for Frontend

## ADDED Requirements

### Requirement: Strategy CRUD Forms

The system SHALL provide HTML form routes for creating, editing, and deleting strategies via HTMX. All form routes SHALL use the `/html` suffix to remain additive to existing JSON endpoints. The system SHALL validate form submissions and reject requests with empty required fields.

#### Scenario: GET /strategies/new renders create form

- GIVEN the application is running
- WHEN a client sends `GET /strategies/new` with `Accept: text/html`
- THEN the response status is 200
- AND `Content-Type` includes `text/html`
- AND the response body contains a `<form>` with name and description input fields

#### Scenario: POST /strategies/html creates strategy and returns list partial

- GIVEN the store contains strategies "MACD crossover" and "RSI divergence"
- WHEN a client sends `POST /strategies/html` with valid form data (`name=Test Strategy`, `description=A test`)
- AND the request includes `HX-Request: true`
- THEN the response status is 200
- AND the response body contains the new strategy "Test Strategy" alongside existing strategies in the list

#### Scenario: GET /strategies/{id}/edit renders pre-filled edit form

- GIVEN the store contains a strategy with id 1 and name "MACD crossover"
- WHEN a client sends `GET /strategies/1/edit` with `Accept: text/html`
- THEN the response status is 200
- AND the response body contains a `<form>` with the name field pre-filled to "MACD crossover"

#### Scenario: PUT /strategies/{id}/html updates strategy and returns updated list

- GIVEN the store contains a strategy with id 1 and name "MACD crossover"
- WHEN a client sends `PUT /strategies/1/html` with `name=Updated Strategy`
- AND the request includes `HX-Request: true`
- THEN the response status is 200
- AND the response body contains "Updated Strategy" in the strategy list

#### Scenario: DELETE /strategies/{id} via HTMX removes strategy

- GIVEN the store contains a strategy with id 1 and name "MACD crossover"
- WHEN a client sends `DELETE /strategies/1` with `HX-Request: true`
- THEN the response status is 204 or 200
- AND the response body no longer contains "MACD crossover"

#### Scenario: POST /strategies/html with empty name rejects submission

- GIVEN the store contains no strategies
- WHEN a client sends `POST /strategies/html` with `name=` and `description=A test`
- AND the request includes `HX-Request: true`
- THEN the response status is 422 or 400
- AND the response contains a validation error message for the name field
