"""FastAPI application for the 98-tstlocal trading app.

Provides health-check and trading strategy CRUD endpoints backed by a
SQLite database via SQLAlchemy. Routes are registered on a module-level
FastAPI instance with a lifespan handler for database bootstrap.
"""

import datetime
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.templating import Jinja2Templates

from app.database import Base
from app.market import MarketDatabase
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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/health")
def health() -> dict[str, str]:
    """Health-check endpoint; returns a fixed status payload."""
    return {"status": "ok"}


@app.get("/api/ohlc")
def get_ohlc(
    symbol: str = Query(...),
    timeframe: str = Query("1m"),
    limit: int = Query(200, ge=1),
    start: str | None = Query(None),
    end: str | None = Query(None),
) -> JSONResponse:
    """Return OHLCV bars as JSON array.

    The limit is capped at 5000. Start/end are ISO date strings.
    """
    actual_limit = min(limit, 5000)

    if timeframe not in MarketDatabase.INTERVAL_MAP:
        raise HTTPException(status_code=422, detail=f"Unsupported timeframe: {timeframe}")

    try:
        start_date = datetime.date.fromisoformat(start) if start else None
        end_date = datetime.date.fromisoformat(end) if end else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format") from None

    db = MarketDatabase()
    try:
        data = db.query_ohlc(
            symbol=symbol,
            timeframe=timeframe,
            limit=actual_limit,
            start_date=start_date,
            end_date=end_date,
        )
    finally:
        db.close()
    return JSONResponse(data)


@app.get("/market/chart")
def market_chart(
    request: Request,
    symbol: str | None = Query(None),
    timeframe: str = Query("1m"),
    limit: int = Query(200),
    start: str | None = Query(None),
    end: str | None = Query(None),
) -> Response:
    """Render the market chart page with symbol selector and date inputs."""
    db = MarketDatabase()
    try:
        symbols = db.list_symbols()
    finally:
        db.close()

    selected = symbol or (symbols[0] if symbols else None)
    return templates.TemplateResponse(
        request,
        "market/chart.html",
        {
            "symbols": symbols,
            "selected_symbol": selected,
            "timeframe": timeframe,
            "limit": limit,
            "start": start or "",
            "end": end or "",
        },
    )


@app.get("/")
def index(request: Request) -> Response:
    """Render the application index page."""
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/strategies")
def list_strategies(
    request: Request,
    name: str | None = Query(None),
) -> Response:
    """Return strategies as JSON, full page for browsers, or table partial for HTMX."""
    accept = request.headers.get("accept", "")
    is_htmx = request.headers.get("hx-request", "").lower() == "true"

    if is_htmx:
        # HTMX swap (refresh button, post-delete): return table partial only
        return templates.TemplateResponse(
            request, "strategies/table.html", {"strategies": store.list()}
        )
    if "text/html" in accept:
        # Full page load
        strats = store.list()
        return templates.TemplateResponse(request, "strategies/list.html", {"strategies": strats})
    return JSONResponse(jsonable_encoder([s.model_dump() for s in store.list(name_filter=name)]))


@app.get("/strategies/new")
def create_strategy_form(request: Request) -> Response:
    """Render the strategy creation form."""
    return templates.TemplateResponse(
        request,
        "strategies/form_page.html",
        {
            "action": "/strategies/html",
            "method": "post",
            "strategy": None,
            "errors": None,
        },
    )


@app.post("/strategies", status_code=201)
def create_strategy(payload: StrategyCreate) -> dict[str, object]:
    """Create a new strategy from the given payload."""
    strategy = store.create(payload)
    return strategy.model_dump()


@app.post("/strategies/html")
def create_strategy_html(
    request: Request,
    name: str | None = Form(None),
    description: str | None = Form(None),
) -> Response:
    """Create a strategy from HTML form data; redirect to list on success."""
    if not name:
        return templates.TemplateResponse(
            request,
            "strategies/form.html",
            {
                "action": "/strategies/html",
                "method": "post",
                "strategy": None,
                "errors": "Name is required",
            },
            status_code=422,
        )
    try:
        payload = StrategyCreate(name=name, description=description)
        store.create(payload)
    except ValidationError as e:
        return templates.TemplateResponse(
            request,
            "strategies/form.html",
            {
                "action": "/strategies/html",
                "method": "post",
                "strategy": None,
                "errors": str(e),
            },
            status_code=422,
        )
    return Response(headers={"HX-Redirect": "/strategies"})


@app.get("/strategies/{strategy_id}")
def get_strategy(strategy_id: str) -> dict[str, object]:
    """Return a strategy by id, or 404 if not found."""
    strategy = store.get(strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy.model_dump()


@app.get("/strategies/{strategy_id}/edit")
def edit_strategy_form(request: Request, strategy_id: str) -> Response:
    """Render the strategy edit form pre-filled with existing data."""
    strategy = store.get(strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return templates.TemplateResponse(
        request,
        "strategies/form_page.html",
        {
            "action": f"/strategies/{strategy_id}/html",
            "method": "put",
            "strategy": strategy,
            "errors": None,
        },
    )


@app.put("/strategies/{strategy_id}")
def update_strategy(strategy_id: str, payload: StrategyUpdate) -> dict[str, object]:
    """Update a strategy by id, or 404 if not found."""
    try:
        strategy = store.update(strategy_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Strategy not found") from None
    return strategy.model_dump()


@app.put("/strategies/{strategy_id}/html")
def update_strategy_html(
    request: Request,
    strategy_id: str,
    name: str | None = Form(None),
    description: str | None = Form(None),
) -> Response:
    """Update a strategy from HTML form data, return updated list."""
    if not name:
        return templates.TemplateResponse(
            request,
            "strategies/form.html",
            {
                "action": f"/strategies/{strategy_id}/html",
                "method": "put",
                "strategy": None,
                "errors": "Name is required",
            },
            status_code=422,
        )
    try:
        payload = StrategyUpdate(name=name, description=description)
        store.update(strategy_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Strategy not found") from None
    except ValidationError as e:
        return templates.TemplateResponse(
            request,
            "strategies/form.html",
            {
                "action": f"/strategies/{strategy_id}/html",
                "method": "put",
                "strategy": None,
                "errors": str(e),
            },
            status_code=422,
        )
    return Response(headers={"HX-Redirect": "/strategies"})


@app.delete("/strategies/{strategy_id}", status_code=204)
def delete_strategy(strategy_id: str) -> None:
    """Delete a strategy by id, or 404 if not found."""
    deleted = store.delete(strategy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found")


@app.delete("/strategies/{strategy_id}/html")
def delete_strategy_html(request: Request, strategy_id: str) -> Response:
    """Delete a strategy and return updated list (200, not 204, for HTMX swap)."""
    deleted = store.delete(strategy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return templates.TemplateResponse(
        request, "strategies/table.html", {"strategies": store.list()}
    )
