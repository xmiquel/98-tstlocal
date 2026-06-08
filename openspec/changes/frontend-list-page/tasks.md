# Tasks: Strategy List Page (frontend-list-page)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~90 (60 code + 30 tests + templates) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Templates

- [x] 1.1 Create `templates/base.html` — HTML5 shell with nav, `{% block content %}`, HTMX v2 CDN script, CSS link
- [x] 1.2 Create `templates/strategies/list.html` — strategy table via `{% for s in strategies %}`, wrapped in `<div id="strategy-table">`
- [x] 1.3 Create `static/css/app.css` — table borders, hover row highlight, responsive width

## Phase 2: Routes

- [x] 2.1 Add `Jinja2Templates` import + `StaticFiles` mount to `app/main.py`
- [x] 2.2 Add `GET /` — render index page with link to strategy list
- [x] 2.3 Add `GET /strategies` — content-negotiated HTML render (see design deviation note)

## Phase 3: Tests

- [x] 3.1 Create `tests/test_pages.py` — `TestClient`: `GET /` returns 200 + link text in HTML
- [x] 3.2 Test `GET /strategies` with populated store — assert each strategy name in HTML body
- [x] 3.3 Test `GET /strategies` with empty store — assert "no strategies" placeholder message
- [x] 3.4 Assert `hx-get="/strategies"` attribute present in rendered HTML

## Phase 4: Cleanup

- [x] 4.1 Run `make ci` to verify no regressions on JSON endpoints
- [x] 4.2 Verify `GET /health` and all existing `test_strategies.py` tests pass unchanged
