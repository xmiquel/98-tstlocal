"""Shared test fixtures for the 98-tstlocal trading application.

Provides an autouse fixture that replaces the store's engine with a fresh
in-memory SQLite database before each test for full test isolation.

Uses ``StaticPool`` to ensure the in-memory database is shared across
threads (FastAPI's TestClient runs route handlers in a thread pool).
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
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
