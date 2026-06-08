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
