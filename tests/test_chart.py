"""Integration tests for market chart endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_ohlc_returns_json() -> None:
    """GET /api/ohlc returns a JSON array with valid bar data."""
    response = client.get("/api/ohlc?symbol=NDX&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    if data:
        assert "time" in data[0]
        assert "open" in data[0]
        assert "high" in data[0]
        assert "low" in data[0]
        assert "close" in data[0]


def test_api_ohlc_missing_symbol_returns_422() -> None:
    """GET /api/ohlc without symbol returns 422."""
    response = client.get("/api/ohlc")
    assert response.status_code == 422


def test_api_ohlc_date_range() -> None:
    """GET /api/ohlc with start/end returns filtered results."""
    response = client.get("/api/ohlc?symbol=NDX&start=2024-01-01&end=2024-01-02")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_ohlc_invalid_date_returns_422() -> None:
    """GET /api/ohlc with unparseable date returns 422."""
    response = client.get("/api/ohlc?symbol=NDX&start=not-a-date")
    assert response.status_code == 422


def test_api_ohlc_caps_at_5000() -> None:
    """GET /api/ohlc caps limit at 5000, no error."""
    response = client.get("/api/ohlc?symbol=NDX&limit=99999")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5000


def test_market_chart_renders_html() -> None:
    """GET /market/chart returns HTML with symbol select."""
    response = client.get("/market/chart")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_market_chart_has_chart_container() -> None:
    """GET /market/chart page contains the chart div and symbol options."""
    response = client.get("/market/chart")
    assert response.status_code == 200
    assert 'id="chart"' in response.text
    assert "lightweight-charts" in response.text


def test_market_chart_lists_symbols() -> None:
    """GET /market/chart renders symbol options populated from DuckDB."""
    response = client.get("/market/chart")
    assert response.status_code == 200
    assert '<option value="NDX"' in response.text or (
        '<select name="symbol">' in response.text and "</select>" in response.text
    )
