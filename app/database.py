"""SQLAlchemy ORM models for the 98-tstlocal trading application.

Provides the declarative Base and StrategyModel table definition.
Engine and session factory are owned by StrategyStore in app/store.py.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models in the application."""


class StrategyModel(Base):
    """ORM model for trading strategies backed by a SQLite database."""

    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
