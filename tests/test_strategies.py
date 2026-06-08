"""Contract tests for strategy CRUD endpoints.

These tests are written BEFORE the implementation (strict TDD).
Importing from app.store will fail until app/store.py exists.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_store() -> None:
    """Ensure each test starts with a clean store for isolation."""
    store.clear()


def test_list_strategies_returns_empty_list() -> None:
    """GET /strategies returns [] when the store is empty."""
    response = client.get("/strategies")
    assert response.status_code == 200
    assert response.json() == []


def test_create_strategy_returns_201_with_id() -> None:
    """POST /strategies returns 201 and a JSON body with id, name, created_at."""
    payload = {"name": "MACD Cross"}
    response = client.post("/strategies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "MACD Cross"
    assert "created_at" in data


def test_list_strategies_returns_created_strategy() -> None:
    """GET /strategies returns a non-empty list after a strategy is created."""
    client.post("/strategies", json={"name": "RSI Divergence"})
    response = client.get("/strategies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "RSI Divergence"


def test_create_strategy_with_description() -> None:
    """POST /strategies accepts an optional description field."""
    payload = {"name": "Bollinger Band Squeeze", "description": "Volatility-based strategy"}
    response = client.post("/strategies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bollinger Band Squeeze"
    assert data["description"] == "Volatility-based strategy"


def test_get_strategy_by_id_returns_200() -> None:
    """GET /strategies/{id} returns 200 with the matching strategy."""
    create_resp = client.post("/strategies", json={"name": "Mean Reversion"})
    strategy_id = create_resp.json()["id"]
    response = client.get(f"/strategies/{strategy_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == strategy_id
    assert data["name"] == "Mean Reversion"


def test_get_strategy_by_id_returns_404() -> None:
    """GET /strategies/{id} returns 404 for a non-existent id."""
    response = client.get("/strategies/non-existent-id")
    assert response.status_code == 404


def test_delete_strategy_returns_204() -> None:
    """DELETE /strategies/{id} returns 204 and removes the strategy."""
    create_resp = client.post("/strategies", json={"name": "Trend Following"})
    strategy_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/strategies/{strategy_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"/strategies/{strategy_id}")
    assert get_resp.status_code == 404


def test_delete_strategy_returns_404() -> None:
    """DELETE /strategies/{id} returns 404 for a non-existent id."""
    response = client.delete("/strategies/non-existent-id")
    assert response.status_code == 404
