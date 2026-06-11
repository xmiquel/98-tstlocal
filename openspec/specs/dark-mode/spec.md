# Dark Mode

## Purpose

Dark mode provides a CSS-based theming infrastructure that respects user OS preference, persists choice across sessions, and applies before initial paint to prevent flash. All visual colors reference CSS custom properties defined in `static/css/app.css`. No backend changes are required.

## Requirements

### Requirement: CSS Custom Properties for Light and Dark Themes

The system SHALL define color CSS custom properties on `:root` (light theme) and `[data-theme="dark"]` (dark theme) in `static/css/app.css`. All visual color values in the application SHALL reference these variables instead of hardcoded values.

#### Scenario: Light theme variables defined on :root

- GIVEN `static/css/app.css` is loaded
- WHEN the document has no `data-theme` attribute
- THEN `var(--bg)` evaluates to the light background color
- AND `var(--text)` evaluates to the light text color

#### Scenario: Dark theme variables defined on [data-theme="dark"]

- GIVEN `static/css/app.css` is loaded
- WHEN the `<html>` element has `data-theme="dark"`
- THEN `var(--bg)` evaluates to the dark background color
- AND `var(--text)` evaluates to the dark text color

### Requirement: Theme Detection and Persistence

The system SHALL detect the user's preferred theme on first visit using `prefers-color-scheme`, persist the choice to `localStorage`, and restore it on subsequent visits. An inline `<script>` in `templates/base.html` `<head>` SHALL run before first paint to prevent flash.

#### Scenario: First visit respects OS preference

- GIVEN the user has no localStorage theme entry
- WHEN the page loads
- THEN the inline script reads `window.matchMedia("(prefers-color-scheme: dark)")`
- AND sets `data-theme` to match OS preference before render

#### Scenario: Subsequent visit restores saved preference

- GIVEN the user previously selected dark mode
- WHEN the page loads
- THEN the inline script reads `localStorage.getItem("theme")`
- AND sets `data-theme` to `"dark"` without consulting `prefers-color-scheme`

### Requirement: Theme Toggle Button

The system SHALL render a text toggle button in the `<nav>` element on every page via `templates/base.html`. Clicking the button SHALL toggle `data-theme` on `<html>` and persist the new choice to `localStorage`.

#### Scenario: Toggle button renders in nav

- GIVEN a client navigates to any page
- WHEN the page renders
- THEN the `<nav>` element contains a button indicating the current theme
- AND the button is reachable and clickable

#### Scenario: Clicking toggle switches theme immediately

- GIVEN the page is in light mode
- WHEN the user clicks the toggle button
- THEN `data-theme` changes to `"dark"`
- AND CSS variables re-evaluate to dark values immediately

#### Scenario: Preference persisted to localStorage on toggle

- GIVEN the user clicks the toggle button
- WHEN the theme changes
- THEN `localStorage.setItem("theme", "dark")` is called
- AND the saved value persists after page reload

## Out of Scope (Non-Requirements)

- Server-side theme detection or persistence
- Multiple theme variants (e.g., high contrast, sepia)
- User settings page for theme configuration
- Animated transitions between themes
