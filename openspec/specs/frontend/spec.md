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

### Requirement: CSS Custom Properties Color Architecture

The system SHALL define all application color values as CSS custom properties on `:root` in `static/css/app.css`. Every CSS rule SHALL reference these variables via `var(--*)` rather than hardcoded hex codes. This enables systematic theming without modifying individual rules.

#### Scenario: All colors sourced from custom properties

- GIVEN `static/css/app.css` is loaded
- WHEN inspecting any element's computed color
- THEN the value originates from a `var(--*)` reference
- AND no hardcoded color appears outside the `:root` block

#### Scenario: Variable rename propagates everywhere

- GIVEN `--primary` is defined in `:root`
- WHEN `--primary` is changed to a different color
- THEN all elements referencing `var(--primary)` reflect the new color
- AND no element retains the old hardcoded value

### Requirement: Dark Mode Overrides

The system SHALL define dark-mode color overrides under `[data-theme="dark"]` in `static/css/app.css`. When the `<html>` element carries `data-theme="dark"`, all CSS custom properties SHALL re-evaluate to dark-appropriate values.

#### Scenario: Dark mode applied via attribute selector

- GIVEN the page is rendering
- WHEN `data-theme="dark"` is set on `<html>`
- THEN `--bg` evaluates to a dark color
- AND `--text` evaluates to a light color
- AND the page renders in dark mode without additional CSS

### Requirement: Basic UI Component Styling

The system SHALL define basic styles for `.btn`, `.toolbar`, `.error-summary`, `.form-group`, `.form-actions`, and `.cancel-link` in `static/css/app.css`. All color values in these rules SHALL reference CSS custom properties.

#### Scenario: Button styled with CSS variables

- GIVEN `static/css/app.css` is loaded
- WHEN an element has class `.btn`
- THEN it SHALL use `var(--btn-bg)` and `var(--btn-text)` for colors
- AND switching to dark mode updates button appearance automatically

#### Scenario: Error summary adapts to theme

- GIVEN an element with class `.error-summary`
- WHEN the page is in light mode
- THEN the error summary has sufficient contrast for readability
- WHEN the page toggles to dark mode
- THEN the error summary colors adapt without separate CSS rules

## Out of Scope (Non-Requirements)

Pagination, sorting, and search filtering via HTML are not included.
