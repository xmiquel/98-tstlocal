# Tasks: Frontend CRUD Forms

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~90 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Templates

- [x] 1.1 Create `templates/strategies/form.html` — shared create/edit form with conditional pre-fill, error display, action/method context
- [x] 1.2 Update `templates/strategies/list.html` — add `<th>Actions</th>` column, edit link (`href`), delete button (`hx-delete`, `hx-confirm`, `hx-target`, `hx-swap`)

## Phase 2: Routes

- [x] 2.1 Add `GET /strategies/new` to `app/main.py` — render empty form.html
- [x] 2.2 Add `POST /strategies/html` to `app/main.py` — validate with Pydantic, create strategy, return list.html (success) or form.html with errors (422)
- [x] 2.3 Add `GET /strategies/{id}/edit` to `app/main.py` — load strategy, render pre-filled form.html
- [x] 2.4 Add `PUT /strategies/{id}/html` to `app/main.py` — validate, update, return list.html (success) or form.html with errors (422)
- [x] 2.5 Add `DELETE /strategies/{id}/html` to `app/main.py` — delete strategy, return updated list.html

## Phase 3: Tests

- [x] 3.1 Test: `GET /strategies/new` returns 200 with `<form>` containing name and description inputs
- [x] 3.2 Test: `GET /strategies/1/edit` pre-fills name field with existing strategy data
- [x] 3.3 Test: `POST /strategies/html` with valid data creates strategy and includes it in response
- [x] 3.4 Test: `PUT /strategies/1/html` updates strategy name and reflects change in response
- [x] 3.5 Test: `DELETE /strategies/1/html` removes strategy from response list
- [x] 3.6 Test: `POST /strategies/html` with empty name returns 422 with validation error
- [x] 3.7 Test: Parse `list.html` — delete button has `hx-delete`, `hx-confirm`, `hx-target` attributes

## Phase 4: Verify

- [x] 4.1 Run `make ci` — all new tests + existing regression pass
