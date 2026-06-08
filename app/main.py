"""FastAPI application for the 98-tstlocal trading app.

Provides health-check and trading strategy CRUD endpoints backed by an
in-memory store. Routes are registered on a module-level FastAPI instance.
"""

from fastapi import FastAPI, HTTPException

from app.schemas import StrategyCreate, StrategyUpdate
from app.settings import settings
from app.store import store

app: FastAPI = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


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
