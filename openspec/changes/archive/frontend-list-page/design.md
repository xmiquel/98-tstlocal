# Design: Strategy List Page

## Technical Approach

Additive HTML layer on top of the existing FastAPI application. Register `Jinja2Templates` and mount `StaticFiles` in `app/main.py`. `GET /` renders an index page with a link; `GET /strategies` renders the full strategy list with server-rendered table content. HTMX v2 via CDN enables incremental table refresh via `hx-get` + `hx-trigger="load"` with `?_` cache busting. All JSON API routes remain untouched — no imports, routes, or logic changed for them.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Template engine | `Jinja2Templates` (Starlette) | Mako, custom string templates | Ships with Starlette (FastAPI dep), zero added deps, well-typed |
| Base layout | `templates/base.html` | Per-page layouts only | DRY — HTMX script, nav, CSS link in one place |
| Table partial | `templates/strategies/list.html` | Inline in base.html | HTMX swaps only the table; clean separation from layout |
| HTMX endpoint | Same `GET /strategies` | Separate `/strategies/table` partial | Simpler — no extra route; HTMX `hx-select` extracts the table element from the full response |
| CSS delivery | `static/css/app.css` via `StaticFiles` | Inline `<style>`, Tailwind CDN | Minimal table styling; no build step; `StaticFiles` is already needed |
| HTMX source | CDN (`https://unpkg.com/htmx.org@2`) | npm, vendored copy | No `package.json` or build tooling; v2 has `hx-select` and `hx-trigger` natively |
| GET `/` treatment | Index page with link | 302 redirect | Redirect breaks browser back button; index is discoverable and testable |
| Route schema | `include_in_schema=False` | Default (included) | HTML routes are for browsers; OpenAPI stays clean for API consumers |

## Data Flow

```
Browser ──GET /─────────→ FastAPI ──→ Jinja2Templates(base.html) ──→ index HTML

Browser ──GET /strategies ──→ FastAPI ──→ store.list()
                                              │
                                         list[Strategy]
                                              │
                                         Jinja2Templates(list.html) ──→ full HTML
                                         (base.html extended)

  On page load, HTMX:
  hx-get="/strategies?_={timestamp}"
  hx-select="#strategy-table"
  hx-swap="outerHTML"
                                              │
Browser ──GET /strategies?_=xxx ──→ FastAPI (same route, hx-select extracts table)
                                              │
                                     Only table HTML swapped into DOM
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/main.py` | Modify | Add `Jinja2Templates` import, `StaticFiles` mount, `GET /` and `GET /strategies` HTML routes (both with `include_in_schema=False`) |
| `templates/base.html` | Create | HTML5 shell: `<head>` with HTMX CDN v2, CSS link, `<nav>` with app title + nav links, `{% block content %}{% endblock %}` |
| `templates/strategies/list.html` | Create | Strategy table via `{% for s in strategies %}` over Strategy objects; empty-state via `{% if not strategies %}`; table wrapped in `<div id="strategy-table">` for HTMX targeting |
| `static/css/app.css` | Create | Minimal table styling: borders, hover row highlight, responsive width |
| `tests/test_pages.py` | Create | TestClient-based page rendering tests (follows existing `conftest.py` pattern with module-level `client = TestClient(app)`) |

## Interfaces / Contracts

**Template context for `strategies/list.html`** (informal contract):

```python
context = {
    "strategies": list[Strategy],  # from store.list()
    "request": Request,            # Jinja2Templates requires Request in context
}
```

**New route signatures** (added to `app/main.py`):

```python
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {...})

@app.get("/strategies", include_in_schema=False)
def strategies_html(request: Request) -> HTMLResponse:
    strats = store.list()
    return templates.TemplateResponse(request, "strategies/list.html", {"strategies": strats})
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Integration | `GET /` returns 200 with `text/html` | `TestClient.get("/")` → assert 200 + `content-type` starts with `text/html` + link text present |
| Integration | `GET /strategies` with strategies | Create via POST, `GET /strategies` → assert each strategy `name` appears in HTML body |
| Integration | `GET /strategies` empty store | `TestClient.get("/strategies")` → assert "no strategies" or equivalent message in HTML |
| Integration | No regression on JSON routes | Existing `test_strategies.py` tests pass unchanged |
| Integration | HTMX `hx-get` attribute present | Assert `hx-get="/strategies"` appears in rendered HTML (verifies HTMX wiring) |

All tests use the existing `_reset_store` autouse fixture for full isolation. No browser or E2E tests in this slice.

## Migration / Rollout

No migration required. HTML routes are purely additive — all existing JSON endpoints remain functional. Rollback is a single `git revert` of the five affected files.

## Open Questions

None.
