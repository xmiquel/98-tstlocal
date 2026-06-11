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

    If `request.data` is provided, uses it directly (frontend's accumulated
    dataset from infinite scroll). Otherwise queries the DB (fallback for
    initial load or when called without full data).
    """
    # Validate that the indicator exists in the catalog
    indicator_names = {entry["name"] for entry in CATALOG}
    if request.indicator not in indicator_names:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown indicator: {request.indicator}",
        )

    import pandas as pd

    # Use provided data or query DB
    if request.data:
        df = pd.DataFrame(request.data)
        # Accept 'tickvol' as alias for 'volume' (API returns tickvol)
        if "tickvol" in df.columns and "volume" not in df.columns:
            df = df.rename(columns={"tickvol": "volume"})
        # Ensure required columns exist
        required = {"time", "open", "high", "low", "close", "volume"}
        if not required.issubset(df.columns):
            raise HTTPException(
                status_code=422,
                detail=f"Provided data missing required columns: {required - set(df.columns)}",
            )
        # Sort by time to be safe
        df = df.sort_values("time").reset_index(drop=True)
    else:
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
    # multi-line indicators return multiple)
    return JSONResponse(results[0])
