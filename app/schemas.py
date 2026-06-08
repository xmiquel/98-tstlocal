"""Pydantic models for trading strategy domain objects.

StrategyCreate is the input model (used by POST /strategies).
Strategy extends it with an id and created_at timestamp.
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


def _generate_id() -> str:
    """Generate a short unique hex identifier for a strategy."""
    return uuid.uuid4().hex


class StrategyCreate(BaseModel):
    """Input model for creating a new trading strategy."""

    name: str
    description: str | None = None


class Strategy(StrategyCreate):
    """Domain model representing a trading strategy with identity."""

    id: str = Field(default_factory=_generate_id)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
