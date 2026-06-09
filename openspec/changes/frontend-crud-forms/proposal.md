# Proposal: Frontend CRUD Forms

## Intent

The existing frontend slice renders a read-only strategy list. Users cannot create, edit, or delete strategies through the UI — they must use the JSON API. This change adds full CRUD forms so non-developer users can manage strategies entirely through the browser.

## Scope

### In Scope
- `templates/strategies/form.html` — shared create/edit template, pre-filled for edit
- `templates/strategies/detail.html` — single strategy view with edit/delete actions
- `GET /strategies/new` — render empty create form
- `GET /strategies/{id}/edit` — render pre-filled edit form
- `POST /strategies/html` — create from form data via HTMX, return list partial
- `PUT /strategies/{id}/html` — update from form data via HTMX, return list partial
- Delete button: `hx-delete` + `hx-confirm` + `hx-target="#strategies-table" hx-swap="outerHTML"`
- Update `list.html` with edit/delete buttons per row
- Tests: form renders, create, edit, delete via HTMX trigger attributes

### Out of Scope
- Inline editing (all edits go through the form page)
- Pagination, sorting, search
- Client-side validation beyond HTML5 required/pattern

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `frontend`: add Strategy CRUD Forms requirements (create, edit, delete via HTML routes with `/html` suffix)

## Approach

Add HTML-form routes to `app/main.py` using the `/html` suffix convention to remain additive to existing JSON endpoints. Shared `form.html` template renders for both create and edit, pre-filled when a strategy ID is present. Delete uses `hx-delete` at the existing JSON endpoint (`DELETE /strategies/{id}`) with HTMX swap back to the table. `list.html` gains action columns for edit and delete.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/main.py` | Modified | Add form routes (GET/POST/PUT with /html suffix) |
| `templates/strategies/list.html` | Modified | Add action columns for edit/delete per row |
| `templates/strategies/form.html` | New | Shared create/edit form template |
| `templates/strategies/detail.html` | New | Single strategy view with actions |
| `tests/test_pages.py` | Modified | Add tests for form routes and delete attributes |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Form route names collide with future JSON routes | Low | `/html` suffix convention keeps them separate |
| HTMX swap targets break on partial response | Low | Use stable `#strategies-table` target; test with TestClient |

## Rollback Plan

Revert the proposal file and all changed routes/templates from the branch. The JSON API is untouched — existing clients are unaffected. Delete new templates, revert `list.html`, revert `app/main.py` additions.

## Dependencies

None — all routes are additive to existing store/schema layer.

## Success Criteria

- [ ] Create form renders and submits via POST /strategies/html
- [ ] Edit form renders pre-filled with existing strategy data
- [ ] PUT /strategies/{id}/html updates strategy and returns updated list
- [ ] Delete button in list has hx-delete, hx-confirm, and swap attributes
- [ ] All existing JSON endpoints and page tests remain passing
