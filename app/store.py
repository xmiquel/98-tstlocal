"""In-memory store for trading strategies.

Provides a StrategyStore class with list, create, get, delete, and clear
operations backed by an in-memory dict. A module-level singleton `store`
is available for convenient import by route handlers and tests.
"""

from app.schemas import Strategy, StrategyCreate


class StrategyStore:
    """In-memory dict-backed store for Strategy objects."""

    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}

    def list(self) -> list[Strategy]:
        """Return all strategies currently in the store."""
        return list(self._strategies.values())

    def create(self, data: StrategyCreate) -> Strategy:
        """Create a new strategy from the input data and store it.

        Returns the created Strategy with an assigned id and timestamp.
        """
        strategy = Strategy(**data.model_dump())
        self._strategies[strategy.id] = strategy
        return strategy

    def get(self, strategy_id: str) -> Strategy | None:
        """Retrieve a strategy by id, or None if not found."""
        return self._strategies.get(strategy_id)

    def delete(self, strategy_id: str) -> bool:
        """Delete a strategy by id.

        Returns True if the strategy existed and was removed, False otherwise.
        """
        if strategy_id in self._strategies:
            del self._strategies[strategy_id]
            return True
        return False

    def clear(self) -> None:
        """Remove all strategies from the store. Used for test isolation."""
        self._strategies.clear()


store: StrategyStore = StrategyStore()
