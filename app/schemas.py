"""Pydantic models for trading strategy domain objects.

StrategyCreate is the input model (used by POST /strategies).
Strategy extends it with id and created_at — both set by the
database layer, never by callers.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    """Input model for creating a new trading strategy."""

    name: str = Field(min_length=1)
    description: str | None = None


class StrategyUpdate(BaseModel):
    """Input model for updating an existing trading strategy.

    Structurally identical to StrategyCreate today, but separated to
    signal semantic intent and allow future divergence (e.g. PATCH).
    """

    name: str = Field(min_length=1)
    description: str | None = None


class Strategy(StrategyCreate):
    """Domain model representing a trading strategy with identity.

    id and created_at are ALWAYS set by the store layer —
    this model requires them explicitly so there is no silent fallback.
    """

    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── Indicator API Models ──────────────────────────────────────────────────


class IndicatorParam(BaseModel):
    """Parameter definition for an indicator in the catalog."""

    name: str
    type: str
    default: float | int | str
    description: str


class CatalogEntry(BaseModel):
    """An entry in the indicator catalog."""

    name: str
    params: list[IndicatorParam]


class IndicatorRequest(BaseModel):
    """Request model for POST /api/indicators/calculate.

    If `data` is provided, it is used directly instead of querying the DB.
    This allows the frontend to send its full accumulated dataset (including
    prepended historical candles from infinite scroll) for accurate recalculation.
    """

    symbol: str
    timeframe: str = "1m"
    indicator: str
    params: dict[str, float | int | str] = {}
    data: list[dict[str, float | int]] | None = None


class IndicatorValue(BaseModel):
    """A single time-value pair for indicator output.

    Value can be null for initial periods where the indicator hasn't
    accumulated enough data (e.g., first 19 candles for SMA(20)).
    """

    time: int
    value: float | None = None


class IndicatorResult(BaseModel):
    """Response model for a single calculated indicator line."""

    label: str
    values: list[IndicatorValue]
