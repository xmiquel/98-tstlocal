"""Smoke test for the Python toolchain bootstrap.

FastAPI / httpx / pydantic imports are intentionally deferred to the next
change. This module exists so `uv run pytest` has at least one passing
test and the 80% coverage gate has something to run against.
"""


def test_math_still_works() -> None:
    assert 1 + 1 == 2
