"""Market data storage using DuckDB for OHLCV time-series data."""

import datetime

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
        """Create the dt_ohlc_m1 table if it does not exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS dt_ohlc_m1 (
                datetime    TIMESTAMP,
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

    def ingest_csv(self, csv_path: str, origen: str, fecha_carga: datetime.datetime) -> int:
        """Load a CSV file into dt_ohlc_m1. Returns row count."""
        self._conn.execute(
            """
            INSERT INTO dt_ohlc_m1
            SELECT
                date::DATE + time::TIME AS datetime,
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
            [origen, fecha_carga.isoformat(), csv_path],
        )
        result = self._conn.execute("SELECT COUNT(*) FROM dt_ohlc_m1").fetchone()
        # COUNT(*) always produces exactly one row; fetchone will never be None
        return 0 if result is None else result[0]

    def truncate(self) -> None:
        """Delete all rows from dt_ohlc_m1."""
        self._conn.execute("DELETE FROM dt_ohlc_m1")

    def close(self) -> None:
        """Close the DuckDB connection."""
        self._conn.close()
