"""SQLAlchemy-backed store for trading strategies.

Provides a StrategyStore class with list, create, get, delete, and clear
operations backed by a SQLite database via SQLAlchemy 2.0 ORM. A module-level
singleton ``store`` is available for convenient import by route handlers.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import sessionmaker

from app.database import StrategyModel
from app.schemas import Strategy, StrategyCreate, StrategyUpdate
from app.settings import settings


class StrategyStore:
    """SQLAlchemy-backed store for Strategy objects.

    Each CRUD method opens and closes its own database session. This keeps
    the store self-contained and avoids the need for route-level session
    injection (Depends(get_db)).
    """

    def __init__(self, db_url: str = "sqlite:///./data/trading.db") -> None:
        _ensure_db_dir(db_url)
        self._engine = create_engine(db_url, echo=False)
        self._session_factory = sessionmaker(self._engine)

    def list(self) -> list[Strategy]:
        """Return all strategies ordered by creation time."""
        with self._session_factory() as session:
            rows = (
                session.execute(select(StrategyModel).order_by(StrategyModel.created_at))
                .scalars()
                .all()
            )
            return [self._to_schema(r) for r in rows]

    def create(self, data: StrategyCreate) -> Strategy:
        """Create a new strategy from the input data and persist it.

        Returns the created Strategy with an assigned id and timestamp.
        """
        with self._session_factory() as session:
            model = StrategyModel(name=data.name, description=data.description)
            session.add(model)
            session.flush()
            session.commit()
            return self._to_schema(model)

    def get(self, strategy_id: str) -> Strategy | None:
        """Retrieve a strategy by id, or None if not found."""
        with self._session_factory() as session:
            model = session.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            ).scalar_one_or_none()
            if model is None:
                return None
            return self._to_schema(model)

    def update(self, strategy_id: str, data: StrategyUpdate) -> Strategy:
        """Update an existing strategy in-place.

        Raises KeyError if strategy_id does not exist.
        Returns the updated Strategy object.
        """
        with self._session_factory() as session:
            model = session.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            ).scalar_one_or_none()
            if model is None:
                msg = f"Strategy {strategy_id!r} not found"
                raise KeyError(msg)
            model.name = data.name
            model.description = data.description
            session.commit()
            return self._to_schema(model)

    def delete(self, strategy_id: str) -> bool:
        """Delete a strategy by id.

        Returns True if the strategy existed and was removed, False otherwise.
        """
        with self._session_factory() as session:
            model = session.execute(
                select(StrategyModel).where(StrategyModel.id == strategy_id)
            ).scalar_one_or_none()
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True

    def clear(self) -> None:
        """Remove all strategies from the store. Used for test isolation."""
        with self._session_factory() as session:
            session.execute(delete(StrategyModel))
            session.commit()

    @staticmethod
    def _to_schema(model: StrategyModel) -> Strategy:
        """Convert an ORM model instance to the Pydantic Strategy schema."""
        return Strategy(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )


def _ensure_db_dir(db_url: str) -> None:
    """Create the parent directory for a SQLite database file if needed.

    SQLAlchemy's create_engine creates the database file but NOT parent
    directories. This helper ensures they exist before engine creation.
    """
    if db_url.startswith("sqlite:///"):
        db_path = db_url[len("sqlite:///") :]
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)


store: StrategyStore = StrategyStore(db_url=settings.DATABASE_URL)
