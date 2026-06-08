# Proposal: Strategy List Page (frontend-list-page)

## Intent

Deliver the first visible frontend slice — a read-only strategy list page. Moves the project from pure-API to a browsable application, enabling non-developer users to view strategies without Swagger UI or curl.

## Scope

### In Scope
- HTML route `GET /strategies` rendering a strategy table with HTMX `?_` refresh
- Base layout template with nav, content block, and HTMX CDN script
- Minimal CSS for the strategy table
- TestClient-based page rendering tests

### Out of Scope
- Create/Edit/Delete forms (deferred to subsequent slices)
- Strategy detail page, dashboard, or landing page
- HTMX form submission or swap mechanics
- Pagination, sorting, or search filtering via HTML

## Capabilities

### New Capabilities
- `frontend`: Server-rendered HTML layer. First requirement: Strategy List Page — a read-only table of all strategies.

### Modified Capabilities
- None

## Approach

Additive HTML routes in same FastAPI app. Register `Jinja2Templates` and mount `StaticFiles`. `GET /strategies` calls existing `store.list()`, passes `Strategy` objects to `strategies/list.html`. HTMX via CDN in base template enables `hx-get` with `hx-trigger="load"` for table partial — swap of the full table content on `?_` busts cache. All JSON API routes untouched.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/main.py` | Modified | ADD `Jinja2Templates` + `StaticFiles` imports and mounts. Add HTML route handlers. |
| `templates/base.html` | New | Base layout: HTML5, nav, content block, HTMX CDN script |
| `templates/strategies/list.html` | New | Strategy table — Jinja2 partial consumed by HTMX |
| `static/css/app.css` | New | Minimal table styling |
| `tests/test_pages.py` | New | TestClient assertions: status 200, expected text |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Template tests fragile to HTML structure | Med | Use text-content assertions, not DOM selectors |

## Rollback Plan

Revert `app/main.py` additions, delete `templates/` and `static/` directories. All JSON routes remain functional.

## Dependencies

None. Jinja2Templates bundled with Starlette. HTMX via CDN.

## Success Criteria

- [ ] TestClient confirms `GET /strategies` returns 200 with strategy rows
- [ ] HTMX `?_` refresh loads updated strategies without full page reload
- [ ] All existing JSON API tests still pass
