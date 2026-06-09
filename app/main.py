"""FastAPI application for the 98-tstlocal trading app.

Provides health-check and trading strategy CRUD endpoints backed by a
SQLite database via SQLAlchemy. Routes are registered on a module-level
FastAPI instance with a lifespan handler for database bootstrap.
"""

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


@app.get("/")
def index(request: Request) -> Response:
    """Render the application index page."""
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/strategies")
def list_strategies(
    request: Request,
    name: str | None = Query(None),
) -> Response:
    """Return all strategies as JSON, or render HTML for browser requests."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        strats = store.list()
        return templates.TemplateResponse(request, "strategies/list.html", {"strategies": strats})
    return JSONResponse(jsonable_encoder([s.model_dump() for s in store.list(name_filter=name)]))


@app.get("/strategies/new")
def create_strategy_form(request: Request) -> Response:
    """Render the strategy creation form."""
    return templates.TemplateResponse(
        request,
        "strategies/form.html",
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
    """Create a strategy from HTML form data, return updated list."""
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
    return templates.TemplateResponse(request, "strategies/list.html", {"strategies": store.list()})


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
        "strategies/form.html",
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
    return templates.TemplateResponse(request, "strategies/list.html", {"strategies": store.list()})


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
    return templates.TemplateResponse(request, "strategies/list.html", {"strategies": store.list()})
