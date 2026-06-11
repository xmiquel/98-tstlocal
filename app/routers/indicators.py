"""Indicator calculation and catalog API router.

Provides GET /api/indicators/catalog and POST /api/indicators/calculate
endpoints backed by the IndicatorEngine and MarketDatabase.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from app.indicators import CATALOG, IndicatorEngine
from app.market import MarketDatabase
from app.schemas import CatalogEntry, IndicatorRequest, IndicatorResult

router = APIRouter(prefix="/api/indicators", tags=["indicators"])

# Reusable engine instance (in-process cache shared across requests)
_engine = IndicatorEngine()


@router.get("/catalog", response_model=list[CatalogEntry])
def get_catalog() -> list[dict[str, Any]]:
    """Return the static indicator catalog with parameter definitions."""
    return CATALOG


@router.post("/calculate", response_model=IndicatorResult)
def calculate_indicator(request: IndicatorRequest) -> JSONResponse:
    """Calculate the requested indicator for the given symbol and parameters.

    Loads OHLCV data via MarketDatabase, runs the indicator through
    IndicatorEngine, and returns the computed values.
    """
    # Validate that the indicator exists in the catalog
    indicator_names = {entry["name"] for entry in CATALOG}
    if request.indicator not in indicator_names:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown indicator: {request.indicator}",
        )

    db = MarketDatabase()
    try:
        df = db.query_ohlc_as_df(
            symbol=request.symbol,
            timeframe=request.timeframe,
        )
    finally:
        db.close()

    if df.empty:
        return JSONResponse({"label": f"{request.indicator}(...)", "values": []})

    config = {"name": request.indicator, "params": dict(request.params)}
    results = _engine.calculate(
        df,
        config,
        symbol=request.symbol,
        timeframe=request.timeframe,
    )

    # Return the first result line (single-line indicators return one entry;
    # multi-line indicators return multiple — the frontend PR will extend this)
    return JSONResponse(results[0])
