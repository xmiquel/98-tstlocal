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

## Out of Scope (Non-Requirements)

HTMX form submission, swap mechanics, and CRUD operations (create/edit/delete)
are deferred to subsequent frontend slices. Pagination, sorting, and search
filtering via HTML are not included. HTMX `hx-delete` is architecturally noted
but not testable in this slice — no test requirement exists for it.
