# Frontend

## Purpose

The frontend capability delivers a server-rendered HTML layer over the existing
FastAPI application. This first slice establishes Jinja2Templates, static file
serving, and the HTMX partial-refresh pattern — enabling non-developer users
to view strategies without Swagger UI or curl. All JSON API endpoints remain
untouched.

## Requirements

### Requirement: Strategy List Page

The system SHALL serve an HTML page at `GET /strategies` that displays all
strategies in a table via Jinja2Templates. The page SHALL load strategy data
via HTMX partial request on page load (`hx-get` + `hx-trigger="load"`). A base
layout template (`base.html`) SHALL provide the HTML5 shell, navigation, and
HTMX CDN script. All existing JSON API endpoints SHALL remain unchanged.

#### Scenario: GET /strategies returns HTML with strategy table

- GIVEN the store contains at least one strategy
- WHEN a client sends `GET /strategies`
- THEN the response status is 200
- AND `Content-Type` includes `text/html`
- AND the response body renders the strategy's name in a table row

#### Scenario: GET /strategies with empty store renders placeholder

- GIVEN the store contains no strategies
- WHEN a client sends `GET /strategies`
- THEN the response status is 200
- AND the response body contains a "no strategies" message

#### Scenario: GET /strategies renders each strategy name

- GIVEN the store contains strategies named "MACD crossover" and "RSI divergence"
- WHEN a client sends `GET /strategies`
- THEN the response body contains both "MACD crossover" and "RSI divergence"
- AND each name appears exactly once in the table

#### Scenario: GET / redirects to /strategies or renders index

- GIVEN the application is running
- WHEN a client sends `GET /`
- THEN the response is either a redirect (302/307) to `/strategies` or an
  index page containing a link to the strategy list

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

#### Scenario: DELETE /strategies/{id}/html via HTMX removes strategy

- GIVEN the store contains a strategy with id 1 and name "MACD crossover"
- WHEN a client sends `DELETE /strategies/1/html` with `HX-Request: true`
- THEN the response status is 200
- AND the response body no longer contains "MACD crossover"

#### Scenario: POST /strategies/html with empty name rejects submission

- GIVEN the store contains no strategies
- WHEN a client sends `POST /strategies/html` with `name=` and `description=A test`
- AND the request includes `HX-Request: true`
- THEN the response status is 422 or 400
- AND the response contains a validation error message for the name field

## Out of Scope (Non-Requirements)

Pagination, sorting, and search filtering via HTML are not included.
