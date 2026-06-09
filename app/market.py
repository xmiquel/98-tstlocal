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

    INTERVAL_MAP: dict[str, str | None] = {
        "1m": None,
        "5m": "5 minutes",
        "15m": "15 minutes",
        "30m": "30 minutes",
        "1h": "1 hour",
        "4h": "4 hours",
        "1d": "1 day",
    }

    def _query_ohlc_raw(
        self,
        symbol: str,
        limit: int = 200,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, object]]:
        """Query raw 1-minute OHLCV bars with spread."""
        if start_date is not None:
            end = end_date or datetime.date(9999, 12, 31)
            rows = self._conn.execute(
                """
                SELECT datetime, open, high, low, close, volume, spread
                FROM dt_ohlc_m1
                WHERE symbol = ? AND datetime >= ? AND datetime < ?
                ORDER BY datetime
                """,
                [symbol, start_date, end],
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT datetime, open, high, low, close, volume, spread
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
                "spread": int(row[6]),
            }
            for row in rows
        ]

    def _query_ohlc_aggregated(
        self,
        symbol: str,
        interval: str,
        limit: int = 200,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, object]]:
        """Query aggregated OHLCV bars using time_bucket with spread."""
        if start_date is not None:
            sql = """
                SELECT time_bucket(CAST(? AS INTERVAL), datetime) AS t,
                       first(open ORDER BY datetime) AS open,
                       max(high) AS high,
                       min(low) AS low,
                       last(close ORDER BY datetime) AS close,
                       sum(volume) AS volume,
                       first(spread ORDER BY datetime) AS spread
                FROM dt_ohlc_m1
                WHERE symbol = ? AND datetime >= ? AND datetime < ?
                GROUP BY t ORDER BY t
            """
            params: list[object] = [
                interval,
                symbol,
                start_date,
                end_date or datetime.date(9999, 12, 31),
            ]
        else:
            sql = """
                SELECT t, open, high, low, close, volume, spread FROM (
                    SELECT time_bucket(CAST(? AS INTERVAL), datetime) AS t,
                           first(open ORDER BY datetime) AS open,
                           max(high) AS high,
                           min(low) AS low,
                           last(close ORDER BY datetime) AS close,
                           sum(volume) AS volume,
                           first(spread ORDER BY datetime) AS spread
                    FROM dt_ohlc_m1
                    WHERE symbol = ?
                    GROUP BY t ORDER BY t DESC LIMIT ?
                ) sub ORDER BY t
            """
            params = [interval, symbol, limit]

        result = self._conn.execute(sql, params).fetchall()
        return [
            {
                "time": int(row[0].timestamp()),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": int(row[5]),
                "spread": int(row[6]),
            }
            for row in result
        ]

    def query_ohlc(
        self,
        symbol: str,
        timeframe: str = "1m",
        limit: int = 200,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict[str, object]]:
        """Query OHLCV bars from dt_ohlc_m1.

        Routes 1m to raw query, other timeframes to time_bucket aggregation.
        Two modes:
        - Date range mode (start_date provided): filters by datetime range.
        - Limit mode (default): returns the last N bars and reverses to ascending.
        """
        interval = self.INTERVAL_MAP.get(timeframe)
        if timeframe == "1m":
            return self._query_ohlc_raw(symbol, limit, start_date, end_date)
        if interval is not None:
            return self._query_ohlc_aggregated(symbol, interval, limit, start_date, end_date)
        msg = f"Unsupported timeframe: {timeframe}"
        raise ValueError(msg)

    def close(self) -> None:
        """Close the DuckDB connection."""
        self._conn.close()
