"""CLI entry point for ingesting MT5-format CSV files into DuckDB.

Usage:
    uv run python -m app.ingest <path-to-csv>
"""

import datetime
import os
import sys
import time


def main() -> None:
    """Parse args, ingest CSV, report results."""
    if len(sys.argv) < 2:
        print("Usage: uv run python -m app.ingest <path-to-csv>", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    replace = "--replace" in args
    csv_path = os.path.abspath([a for a in args if not a.startswith("--")][0])
    if not os.path.isfile(csv_path):
        print(f"File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    origen = os.path.basename(csv_path)
    symbol = os.path.splitext(origen)[0]
    fecha_carga = datetime.datetime.now()

    from app.market import MarketDatabase

    db = MarketDatabase()
    if replace:
        db.truncate()
    start = time.perf_counter()

    try:
        row_count = db.ingest_csv(csv_path, symbol, origen, fecha_carga)
        elapsed = time.perf_counter() - start
        print(f"Loaded {origen}: {row_count:,} rows in {elapsed:.2f}s -> dt_ohlc_m1")
    finally:
        db.close()


if __name__ == "__main__":
    main()
