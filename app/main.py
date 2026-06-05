"""Minimal FastAPI application for the 98-tstlocal trading app skeleton.

The full app (strategies, backtest, MT5 connector) lands in subsequent
changes. This module exists today so the runtime-dep toolchain can be
exercised end-to-end on a real feature: a single GET /health route that
returns a fixed status payload, exercised by tests/test_health.py.
"""

from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    """Health-check endpoint; returns a fixed status payload."""
    return {"status": "ok"}
