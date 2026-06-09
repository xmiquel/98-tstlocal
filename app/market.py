"""Market data storage using DuckDB for OHLCV time-series data."""

import datetime
from contextlib import suppress

import duckdb

from app.settings import settings


class MarketDatabase:
    """Manages DuckDB connection and table lifecycle for market data."""

    def __init__(self, db_path: str | None = None) -> None:
        """Open (or create) a DuckDB database at the given path."""
        self._path = db_path or settings.MARKET_DB_PATH
        self._conn = duckdb.connect(str(self._path))
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create dt_ohlc_m1 if it does not exist; migrate schema if needed."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS dt_ohlc_m1 (
                datetime    TIMESTAMP,
                symbol      VARCHAR,
                open        DOUBLE,
                high        DOUBLE,
                low         DOUBLE,
                close       DOUBLE,
                tickvol     BIGINT,
                volume      BIGINT,
                spread      INT,
                origen      VARCHAR,
                fecha_carga TIMESTAMP
            )
        """)
        # Migrate existing tables that lack the symbol column (v1 schema)
        with suppress(Exception):
            self._conn.execute("ALTER TABLE dt_ohlc_m1 ADD COLUMN IF NOT EXISTS symbol VARCHAR")

    def ingest_csv(  # noqa: PLR0913
        self,
        csv_path: str,
        symbol: str,
        origen: str,
        fecha_carga: datetime.datetime,
    ) -> int:
        """Load a CSV file into dt_ohlc_m1. Returns row count."""
        self._conn.execute(
            """
            INSERT INTO dt_ohlc_m1
            SELECT
                date::DATE + time::TIME AS datetime,
                ? AS symbol,
                open::DOUBLE,
                high::DOUBLE,
                low::DOUBLE,
                close::DOUBLE,
                tickvol::BIGINT,
                volume::BIGINT,
                spread::INT,
                ? AS origen,
                ?::TIMESTAMP AS fecha_carga
            FROM read_csv_auto(?, header=true)
        """,
            [symbol, origen, fecha_carga.isoformat(), csv_path],
        )
        result = self._conn.execute("SELECT COUNT(*) FROM dt_ohlc_m1").fetchone()
        # COUNT(*) always produces exactly one row; fetchone will never be None
        return 0 if result is None else result[0]

    def truncate(self) -> None:
        """Delete all rows from dt_ohlc_m1."""
        self._conn.execute("DELETE FROM dt_ohlc_m1")

    def list_symbols(self) -> list[str]:
        """Return distinct symbols from dt_ohlc_m1, sorted alphabetically."""
        result = self._conn.execute(
            "SELECT DISTINCT symbol FROM dt_ohlc_m1 ORDER BY symbol"
        ).fetchall()
        return [row[0] for row in result]

    def query_ohlc(
        self,
        symbol: str,
        timeframe: str = "1m",  # noqa: ARG002 — accepted for future compat
        limit: int = 200,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, object]]:
        """Query OHLCV bars from dt_ohlc_m1.

        Two modes:
        - Date range mode (start_date provided): filters by datetime range.
        - Limit mode (default): returns the last N bars and reverses to ascending.
        """
        if start_date is not None:
            end = end_date or datetime.date(9999, 12, 31)
            rows = self._conn.execute(
                """
                SELECT datetime, open, high, low, close, volume
                FROM dt_ohlc_m1
                WHERE symbol = ? AND datetime >= ? AND datetime < ?
                ORDER BY datetime
                """,
                [symbol, start_date, end],
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT datetime, open, high, low, close, volume
                FROM dt_ohlc_m1
                WHERE symbol = ?
                ORDER BY datetime DESC
                LIMIT ?
                """,
                [symbol, limit],
            ).fetchall()
            rows.reverse()

        return [
            {
                "time": int(row[0].timestamp()),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": int(row[5]),
            }
            for row in rows
        ]

    def close(self) -> None:
        """Close the DuckDB connection."""
        self._conn.close()
