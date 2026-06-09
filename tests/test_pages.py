"""Integration tests for the frontend HTML page rendering.

These tests verify that the strategy list page serves HTML content,
renders strategy data from the store, handles the empty state, and
includes HTMX wiring attributes.

All tests use the existing ``_reset_store`` autouse fixture from
``conftest.py`` for full test isolation.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import StrategyCreate
from app.store import store

client = TestClient(app)

BROWSER_ACCEPT = "text/html,application/xhtml+xml"  # Mimics a browser Accept header

STRATEGY_CREATE_PAYLOAD = {"name": "MACD Cross", "description": "A test strategy"}
FORM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


# ── GET / strategies ──────────────────────────────────────────────────────


def test_strategies_page_returns_html() -> None:
    """GET /strategies with browser Accept header returns 200 and text/html."""
    response = client.get("/strategies", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_strategies_page_lists_strategies() -> None:
    """GET /strategies with populated store renders each strategy name."""
    store.create(StrategyCreate(name="MACD crossover"))
    store.create(StrategyCreate(name="RSI divergence"))
    response = client.get("/strategies", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    body = response.text
    assert "MACD crossover" in body
    assert "RSI divergence" in body


def test_strategies_page_empty() -> None:
    """GET /strategies with empty store shows a placeholder message."""
    response = client.get("/strategies", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    body = response.text
    assert "No strategies" in body or "no strategies" in body.lower()


def test_strategies_page_has_refresh_button() -> None:
    """The strategies table page has an HTMX refresh button."""
    store.create(StrategyCreate(name="Test strategy"))
    response = client.get("/strategies", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    body = response.text
    assert 'hx-get="/strategies"' in body
    assert 'hx-target="#strategy-table"' in body or 'hx-target="#strategies-table"' in body


# ── GET / ─────────────────────────────────────────────────────────────────


def test_index_renders_html() -> None:
    """GET / returns 200 and text/html with a link to the strategy list."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "/strategies" in body or "strategy" in body.lower()


# ── GET /strategies/new (create form) ─────────────────────────────────────


def test_create_form_renders() -> None:
    """GET /strategies/new returns 200 with <form> containing name/description inputs."""
    response = client.get("/strategies/new", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "<form" in body
    assert 'name="name"' in body or 'name="name "' in body
    assert "textarea" in body or 'name="description"' in body
    # Triangulate: form action points to create endpoint
    assert 'action="/strategies/html"' in body
    assert "Cancel" in body


def test_edit_form_prefilled() -> None:
    """GET /strategies/{id}/edit returns pre-filled form."""
    create_resp = client.post("/strategies", json={"name": "Mean Reversion"})
    strat_id = create_resp.json()["id"]
    response = client.get(f"/strategies/{strat_id}/edit", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "Mean Reversion" in body
    # Triangulate: form action URL contains the strategy ID
    assert strat_id in body


# ── POST /strategies/html (create via form) ────────────────────────────────


def test_create_via_form() -> None:
    """POST /strategies/html with valid form data creates strategy and includes it."""
    response = client.post(
        "/strategies/html",
        data={"name": "Test Strategy", "description": "A test"},
        headers=FORM_HEADERS,
    )
    assert response.status_code == 200
    body = response.text
    assert "Test Strategy" in body
    # Triangulate: description is also persisted in the response
    assert "A test" in body


def test_form_rejects_empty_name() -> None:
    """POST /strategies/html with empty name returns 422 with error message."""
    response = client.post(
        "/strategies/html",
        data={"name": "", "description": "A test"},
        headers=FORM_HEADERS,
    )
    assert response.status_code == 422
    body = response.text
    # Triangulate: form error message shows up (not raw JSON)
    assert "Name is required" in body
    # Triangulate: error is rendered as HTML, not JSON
    assert "text/html" in response.headers["content-type"]


# ── PUT /strategies/{id}/html (edit via form) ──────────────────────────────


def test_edit_via_form() -> None:
    """PUT /strategies/{id}/html updates strategy and reflects change."""
    create_resp = client.post("/strategies", json={"name": "Original Name"})
    strat_id = create_resp.json()["id"]
    response = client.put(
        f"/strategies/{strat_id}/html",
        data={"name": "Updated Name", "description": "Updated desc"},
        headers=FORM_HEADERS,
    )
    assert response.status_code == 200
    body = response.text
    assert "Updated Name" in body
    # Triangulate: original name is no longer present
    assert "Original Name" not in body
    # Triangulate: edit with name-only (no description) still works
    strat2_resp = client.post("/strategies", json={"name": "Second"})
    strat2_id = strat2_resp.json()["id"]
    r2 = client.put(
        f"/strategies/{strat2_id}/html",
        data={"name": "Updated Second"},
        headers=FORM_HEADERS,
    )
    assert r2.status_code == 200
    assert "Updated Second" in r2.text


# ── DELETE /strategies/{id}/html (delete via HTMX) ─────────────────────────


def test_delete_via_form() -> None:
    """DELETE /strategies/{id}/html removes strategy from response list."""
    create_resp = client.post("/strategies", json={"name": "To Delete"})
    strat_id = create_resp.json()["id"]
    # Triangulate: another strategy remains untouched
    client.post("/strategies", json={"name": "Keep Me"})
    response = client.delete(f"/strategies/{strat_id}/html")
    assert response.status_code == 200
    body = response.text
    assert "To Delete" not in body
    # Triangulate: other strategies remain in the response
    assert "Keep Me" in body


# ── Delete button and Edit link attributes in list view ────────────────────


def test_delete_button_attributes() -> None:
    """List view delete button has hx-delete, hx-confirm, hx-target attributes."""
    store.create(StrategyCreate(name="Test strategy"))
    response = client.get("/strategies", headers={"Accept": BROWSER_ACCEPT})
    assert response.status_code == 200
    body = response.text
    assert "hx-delete=" in body
    assert "hx-confirm=" in body
    assert 'hx-target="#strategies-table"' in body
    # Triangulate: Edit link exists with correct href
    assert "/strategies/" in body
    assert "/edit" in body
