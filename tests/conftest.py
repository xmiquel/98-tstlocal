"""Shared test fixtures for the 98-tstlocal trading application.

Provides an autouse fixture that replaces the store's engine with a fresh
in-memory SQLite database before each test for full test isolation.

Uses ``StaticPool`` to ensure the in-memory database is shared across
threads (FastAPI's TestClient runs route handlers in a thread pool).
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from collections.abc import Generator

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.store import store


@pytest.fixture(autouse=True)
def _reset_store() -> Generator[None, None, None]:
    """Replace store's engine with fresh in-memory SQLite before each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    store._session_factory = sessionmaker(bind=engine)
    yield


@pytest.fixture(scope="session")
def e2e_server() -> Generator[str, None, None]:
    """Start uvicorn subprocess with temp DuckDB for Playwright E2E tests."""
    import datetime
    import tempfile

    from app.market import MarketDatabase

    # Temp DuckDB with 3 TEST bars
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        tmp_db = f.name
    os.unlink(tmp_db)  # DuckDB needs to create its own database file
    db = MarketDatabase(db_path=tmp_db)
    base = datetime.datetime(2024, 1, 1, 9, 30, 0)
    for i in range(3):
        dt = base + datetime.timedelta(minutes=i)
        db._conn.execute(
            "INSERT INTO dt_ohlc_m1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [dt, "TEST", 100.0 + i, 101.0 + i, 99.0 + i, 100.5 + i, 100, 1000, 1, "test", dt],
        )
    db.close()

    # Random port
    with socket.socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    # Start uvicorn
    env = os.environ.copy()
    env["MARKET_DB_PATH"] = tmp_db
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        env=env,
    )

    url = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            r = requests.get(f"{url}/health", timeout=2)
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        proc.terminate()
        pytest.fail("Server did not start")

    yield url

    proc.terminate()
    proc.wait(timeout=5)
    os.unlink(tmp_db)
