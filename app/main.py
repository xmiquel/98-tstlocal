"""FastAPI application for the 98-tstlocal trading app.

Provides health-check and trading strategy CRUD endpoints backed by a
SQLite database via SQLAlchemy. Routes are registered on a module-level
FastAPI instance with a lifespan handler for database bootstrap.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.database import Base
from app.schemas import StrategyCreate, StrategyUpdate
from app.settings import settings
from app.store import store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Create database tables on startup if they do not exist."""
    Base.metadata.create_all(store._engine)
    yield


app: FastAPI = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health-check endpoint; returns a fixed status payload."""
    return {"status": "ok"}


@app.get("/strategies")
def list_strategies() -> list[dict[str, object]]:
    """Return all strategies as a list of dictionaries."""
    return [s.model_dump() for s in store.list()]


@app.post("/strategies", status_code=201)
def create_strategy(payload: StrategyCreate) -> dict[str, object]:
    """Create a new strategy from the given payload."""
    strategy = store.create(payload)
    return strategy.model_dump()


@app.get("/strategies/{strategy_id}")
def get_strategy(strategy_id: str) -> dict[str, object]:
    """Return a strategy by id, or 404 if not found."""
    strategy = store.get(strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy.model_dump()


@app.put("/strategies/{strategy_id}")
def update_strategy(strategy_id: str, payload: StrategyUpdate) -> dict[str, object]:
    """Update a strategy by id, or 404 if not found."""
    try:
        strategy = store.update(strategy_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Strategy not found") from None
    return strategy.model_dump()


@app.delete("/strategies/{strategy_id}", status_code=204)
def delete_strategy(strategy_id: str) -> None:
    """Delete a strategy by id, or 404 if not found."""
    deleted = store.delete(strategy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found")
