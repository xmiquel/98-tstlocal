"""Integration tests for the indicator REST API endpoints.

Covers GET /api/indicators/catalog and POST /api/indicators/calculate.
"""

from __future__ import annotations

import datetime
import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.market import MarketDatabase

client = TestClient(app)


# ── GET /api/indicators/catalog ──────────────────────────────────────────────


def test_catalog_returns_200_with_5_entries() -> None:
    """GET /api/indicators/catalog returns 200 with 5 indicator entries."""
    response = client.get("/api/indicators/catalog")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    names = {entry["name"] for entry in data}
    assert names == {"SMA", "EMA", "RSI", "MACD", "BBANDS"}


def test_catalog_each_entry_has_name_and_params() -> None:
    """Each catalog entry has name and params with name/type/default/description."""
    response = client.get("/api/indicators/catalog")
    assert response.status_code == 200
    data = response.json()
    for entry in data:
        assert "name" in entry
        assert "params" in entry
        assert isinstance(entry["params"], list)
        for param in entry["params"]:
            assert "name" in param
            assert "type" in param
            assert "default" in param
            assert "description" in param


# ── POST /api/indicators/calculate ────────────────────────────────────────────


@pytest.fixture
def market_with_data(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Populate a temp DuckDB with test OHLCV data for indicator tests.

    Uses a temp file so data survives across MarketDatabase connections.
    DuckDB needs to create its own database file, so we unlink the temp file first.
    """
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as tmp:
        tmp_path = tmp.name
    os.unlink(tmp_path)  # DuckDB must create its own database file

    monkeypatch.setattr("app.market.settings.MARKET_DB_PATH", tmp_path)
    db = MarketDatabase(db_path=tmp_path)
    base_dt = datetime.datetime(2024, 1, 1, 0, 0, 0)
    for i in range(200):
        dt = base_dt + datetime.timedelta(minutes=i)
        db._conn.execute(
            "INSERT INTO dt_ohlc_m1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                dt,
                "TEST",
                100.0 + i * 0.1,
                101.0 + i * 0.1,
                99.0 + i * 0.1,
                100.5 + i * 0.1,
                100,
                1000 + i,
                1,
                "test",
                dt,
            ],
        )
    db.close()
    yield
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


def test_calculate_sma_returns_200_with_values(market_with_data: None) -> None:
    """POST /api/indicators/calculate with valid SMA returns 200 and values."""
    response = client.post(
        "/api/indicators/calculate",
        json={"symbol": "TEST", "indicator": "SMA", "params": {"timeperiod": 20}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "SMA(20)"
    assert len(data["values"]) > 0
    assert "time" in data["values"][0]
    assert "value" in data["values"][0]


def test_calculate_unknown_indicator_returns_422(market_with_data: None) -> None:
    """POST /api/indicators/calculate with unknown indicator returns 422."""
    response = client.post(
        "/api/indicators/calculate",
        json={"symbol": "TEST", "indicator": "INVALID"},
    )
    assert response.status_code == 422
    assert "INVALID" in response.text


def test_calculate_empty_symbol_returns_empty_values() -> None:
    """POST /api/indicators/calculate with symbol having no data returns empty values."""
    response = client.post(
        "/api/indicators/calculate",
        json={"symbol": "NONEXISTENT", "indicator": "SMA", "params": {"timeperiod": 20}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["values"] == []


def test_calculate_missing_symbol_returns_422() -> None:
    """POST /api/indicators/calculate without symbol returns 422."""
    response = client.post(
        "/api/indicators/calculate",
        json={"indicator": "SMA"},
    )
    assert response.status_code == 422


def test_calculate_missing_indicator_returns_422() -> None:
    """POST /api/indicators/calculate without indicator returns 422."""
    response = client.post(
        "/api/indicators/calculate",
        json={"symbol": "TEST"},
    )
    assert response.status_code == 422
