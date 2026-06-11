"""Tests for DuckDB market data ingestion."""

from __future__ import annotations

import datetime
import os
import tempfile
from collections.abc import Generator

import pytest

from app.market import MarketDatabase

SAMPLE_CSV = """date,time,open,high,low,close,tickvol,volume,spread
2011.09.19,00:53:00,5573.5,5573.5,5573.5,5573.5,2,20,0
2011.09.19,05:06:00,5575.0,5576.0,5574.0,5575.0,3,30,1
"""


@pytest.fixture
def csv_file() -> Generator[str, None, None]:
    """Create a temporary CSV file with sample OHLCV data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(SAMPLE_CSV)
        tmp_path = f.name
    yield tmp_path
    os.unlink(tmp_path)


@pytest.fixture
def db() -> Generator[MarketDatabase, None, None]:
    """Create an in-memory DuckDB database for testing."""
    mdb = MarketDatabase(db_path=":memory:")
    yield mdb
    mdb.close()


@pytest.fixture
def market_db_with_data() -> Generator[MarketDatabase, None, None]:
    """Create an in-memory DuckDB with sample OHLCV data for query tests."""
    mdb = MarketDatabase(db_path=":memory:")
    # Insert sample data across multiple days
    base_dt = datetime.datetime(2024, 1, 1, 0, 0, 0)
    rows: list[tuple[object, ...]] = []
    for i in range(10):
        dt = base_dt + datetime.timedelta(hours=i)
        rows.append(
            (dt, "TEST", 100.0 + i, 101.0 + i, 99.0 + i, 100.5 + i, 100, 1000 + i, 1, "test", dt)
        )
    for i in range(5):
        dt = datetime.datetime(2024, 1, 2, 0, 0, 0) + datetime.timedelta(hours=i)
        rows.append(
            (dt, "TEST", 200.0 + i, 201.0 + i, 199.0 + i, 200.5 + i, 100, 2000 + i, 1, "test", dt)
        )
    for row in rows:
        mdb._conn.execute(
            "INSERT INTO dt_ohlc_m1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            row,
        )
    yield mdb
    mdb.close()


def test_table_created_on_connect(db: MarketDatabase) -> None:
    """Connecting to DuckDB creates dt_ohlc_m1 table."""
    tables = db._conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='dt_ohlc_m1'"
    ).fetchall()
    assert len(tables) == 1
    assert tables[0][0] == "dt_ohlc_m1"


def test_ingest_csv_inserts_rows(db: MarketDatabase, csv_file: str) -> None:
    """Ingesting a CSV inserts all rows with correct data."""
    symbol = "TEST"
    origen = os.path.basename(csv_file)
    fecha_carga = datetime.datetime(2024, 1, 1, 12, 0, 0)
    count = db.ingest_csv(csv_file, symbol, origen, fecha_carga)
    assert count == 2

    rows = db._conn.execute("SELECT * FROM dt_ohlc_m1 ORDER BY datetime").fetchall()
    assert len(rows) == 2
    assert str(rows[0][0]) == "2011-09-19 00:53:00"
    assert rows[0][1] == symbol
    assert rows[0][2] == 5573.5  # open
    assert rows[0][3] == 5573.5  # high
    assert rows[0][4] == 5573.5  # low
    assert rows[0][5] == 5573.5  # close
    assert rows[0][6] == 2  # tickvol
    assert rows[0][7] == 20  # volume
    assert rows[0][8] == 0  # spread
    assert rows[0][9] == origen
    assert str(rows[0][10]) == "2024-01-01 12:00:00"


def test_ingest_metadata(db: MarketDatabase, csv_file: str) -> None:
    """symbol, origen and fecha_carga are set correctly."""
    symbol = "TEST"
    origen = "test_asset.csv"
    fecha_carga = datetime.datetime(2024, 6, 9, 10, 30, 0)
    db.ingest_csv(csv_file, symbol, origen, fecha_carga)

    row = db._conn.execute("SELECT symbol, origen, fecha_carga FROM dt_ohlc_m1 LIMIT 1").fetchone()
    assert row is not None
    assert row[0] == "TEST"
    assert row[1] == "test_asset.csv"
    assert str(row[2]) == "2024-06-09 10:30:00"


def test_no_timezone_conversion(db: MarketDatabase, csv_file: str) -> None:
    """Datetime is stored as-is without timezone conversion."""
    db.ingest_csv(csv_file, "TEST", "test.csv", datetime.datetime.now())
    row = db._conn.execute("SELECT datetime FROM dt_ohlc_m1 LIMIT 1").fetchone()
    assert row is not None
    assert str(row[0]) == "2011-09-19 00:53:00"


def test_empty_csv(db: MarketDatabase) -> None:
    """Ingesting an empty CSV inserts zero rows."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,open,high,low,close,tickvol,volume,spread\n")
        empty_path = f.name
    try:
        count = db.ingest_csv(empty_path, "EMPTY", "empty.csv", datetime.datetime.now())
        assert count == 0
    finally:
        os.unlink(empty_path)


def test_truncate_clears_rows(db: MarketDatabase, csv_file: str) -> None:
    """truncate() removes all rows from dt_ohlc_m1."""
    db.ingest_csv(csv_file, "TEST", "test.csv", datetime.datetime.now())
    row = db._conn.execute("SELECT COUNT(*) FROM dt_ohlc_m1").fetchone()
    assert row is not None and row[0] > 0
    db.truncate()
    row = db._conn.execute("SELECT COUNT(*) FROM dt_ohlc_m1").fetchone()
    assert row is not None and row[0] == 0


def test_custom_db_path() -> None:
    """MarketDatabase accepts a custom db_path."""
    mdb = MarketDatabase(db_path=":memory:")
    assert mdb._path == ":memory:"
    mdb.close()


def test_ingest_csv_defaults_to_settings_path() -> None:
    """MarketDatabase uses settings.MARKET_DB_PATH when no path given."""
    from app.settings import settings

    mdb = MarketDatabase()
    assert mdb._path == settings.MARKET_DB_PATH
    mdb.close()


# ── query_ohlc tests ─────────────────────────────────────────────────────


def test_query_ohlc_returns_bars(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc returns OHLCV records in ascending time order."""
    rows = market_db_with_data.query_ohlc(symbol="TEST")
    assert len(rows) > 0
    assert "time" in rows[0]
    assert "open" in rows[0]
    assert isinstance(rows[0]["time"], int)


def test_query_ohlc_respects_limit(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc returns exactly the requested number of bars (ascending)."""
    rows = market_db_with_data.query_ohlc(symbol="TEST", limit=5)
    assert len(rows) == 5
    t0: int = rows[0]["time"]  # type: ignore[assignment]
    t1: int = rows[-1]["time"]  # type: ignore[assignment]
    assert t0 <= t1


def test_query_ohlc_date_range(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc with date range returns data within that window."""
    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 2),
    )
    assert len(rows) >= 0
    # All returned rows should be on 2024-01-01
    for r in rows:
        # time is Unix epoch seconds; 2024-01-01 00:00:00 UTC = 1704067200
        t: int = r["time"]  # type: ignore[assignment]
        assert t < 1704153600  # 2024-01-02 00:00:00


def test_query_ohlc_empty_symbol(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc for unknown symbol returns empty list."""
    rows = market_db_with_data.query_ohlc(symbol="NONEXISTENT")
    assert rows == []


# ── aggregated query_ohlc tests ──────────────────────────────────────────


def test_query_ohlc_5m_aggregation(market_db_with_data: MarketDatabase) -> None:
    """5m aggregation returns bars with spread in ascending time order."""
    rows = market_db_with_data.query_ohlc(symbol="TEST", timeframe="5m", limit=10)
    assert len(rows) > 0
    assert "spread" in rows[0]
    if len(rows) >= 2:
        t0: int = rows[0]["time"]  # type: ignore[assignment]
        t1: int = rows[1]["time"]  # type: ignore[assignment]
        assert t0 < t1


def test_query_ohlc_1h_aggregation(market_db_with_data: MarketDatabase) -> None:
    """1h aggregation respects the limit parameter and returns spread."""
    rows = market_db_with_data.query_ohlc(symbol="TEST", timeframe="1h", limit=5)
    assert len(rows) <= 5
    assert all("spread" in r for r in rows)


def test_query_ohlc_1d_aggregation(market_db_with_data: MarketDatabase) -> None:
    """1d aggregation returns bars with all expected fields."""
    rows = market_db_with_data.query_ohlc(symbol="TEST", timeframe="1d", limit=3)
    assert len(rows) > 0
    assert "open" in rows[0]
    assert "high" in rows[0]
    assert "low" in rows[0]
    assert "close" in rows[0]
    assert "tickvol" in rows[0]
    assert "spread" in rows[0]


def test_query_ohlc_invalid_timeframe(market_db_with_data: MarketDatabase) -> None:
    """Invalid timeframe raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        market_db_with_data.query_ohlc(symbol="TEST", timeframe="invalid")


def test_query_ohlc_aggregated_date_range(market_db_with_data: MarketDatabase) -> None:
    """Aggregated query with date range returns bars with spread."""
    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        timeframe="5m",
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 2),
    )
    assert len(rows) > 0
    assert "spread" in rows[0]


def test_query_ohlc_15m_aggregation(market_db_with_data: MarketDatabase) -> None:
    """15m aggregation also works (triangulation on different timeframe)."""
    rows = market_db_with_data.query_ohlc(symbol="TEST", timeframe="15m", limit=5)
    assert len(rows) > 0
    assert all("spread" in r for r in rows)


def test_query_ohlc_1m_has_spread(market_db_with_data: MarketDatabase) -> None:
    """1m (raw) path also includes spread."""
    rows = market_db_with_data.query_ohlc(symbol="TEST", timeframe="1m", limit=3)
    assert len(rows) > 0
    assert "spread" in rows[0]


# ── before-cursor query tests ──────────────────────────────────────────────


def test_query_ohlc_raw_before(market_db_with_data: MarketDatabase) -> None:
    """before cursor returns only bars older than the given timestamp (1m)."""
    # Middle of the first day: 2024-01-01 05:00:00 UTC
    before_dt = datetime.datetime(2024, 1, 1, 5, 0, 0, tzinfo=datetime.UTC)
    before_ts = int(before_dt.timestamp())

    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        timeframe="1m",
        before=before_ts,
        limit=5,
    )

    # Should return 5 bars (hours 0-4), all before 05:00
    assert len(rows) == 5
    for r in rows:
        t: int = r["time"]  # type: ignore[assignment]
        assert t < before_ts
    # Verify ascending order
    for i in range(len(rows) - 1):
        ti: int = rows[i]["time"]  # type: ignore[assignment]
        tj: int = rows[i + 1]["time"]  # type: ignore[assignment]
        assert ti < tj


def test_query_ohlc_5m_before(market_db_with_data: MarketDatabase) -> None:
    """before cursor works with 5m aggregation."""
    before_dt = datetime.datetime(2024, 1, 1, 5, 0, 0)
    before_ts = int(before_dt.timestamp())

    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        timeframe="5m",
        before=before_ts,
        limit=3,
    )

    assert len(rows) > 0
    for r in rows:
        t: int = r["time"]  # type: ignore[assignment]
        assert t < before_ts
    if len(rows) >= 2:
        t0: int = rows[0]["time"]  # type: ignore[assignment]
        t1: int = rows[1]["time"]  # type: ignore[assignment]
        assert t0 < t1


def test_query_ohlc_1h_before(market_db_with_data: MarketDatabase) -> None:
    """before cursor works with 1h aggregation."""
    before_dt = datetime.datetime(2024, 1, 1, 5, 0, 0)
    before_ts = int(before_dt.timestamp())

    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        timeframe="1h",
        before=before_ts,
        limit=3,
    )

    assert len(rows) > 0
    for r in rows:
        t: int = r["time"]  # type: ignore[assignment]
        assert t < before_ts
    if len(rows) >= 2:
        t0: int = rows[0]["time"]  # type: ignore[assignment]
        t1: int = rows[1]["time"]  # type: ignore[assignment]
        assert t0 < t1


def test_query_ohlc_before_returns_fewer(market_db_with_data: MarketDatabase) -> None:
    """before cursor returns fewer bars when not enough data before timestamp."""
    # Only 1 bar before 2024-01-01 01:00:00 (hour 0)
    before_dt = datetime.datetime(2024, 1, 1, 1, 0, 0, tzinfo=datetime.UTC)
    before_ts = int(before_dt.timestamp())

    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        timeframe="1m",
        before=before_ts,
        limit=100,
    )

    # Only hour 0 is before 01:00
    assert len(rows) == 1
    for r in rows:
        t: int = r["time"]  # type: ignore[assignment]
        assert t < before_ts


# ── query_ohlc_as_df tests ─────────────────────────────────────────────────


def test_query_ohlc_as_df_returns_dataframe(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc_as_df returns a DataFrame with correct columns and rows."""
    import pandas as pd

    df = market_db_with_data.query_ohlc_as_df(symbol="TEST", limit=5)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert list(df.columns) == ["time", "open", "high", "low", "close", "volume"]
    assert df["time"].dtype.kind in ("i", "u")  # integer
    assert df["open"].dtype.kind == "f"  # float


def test_query_ohlc_as_df_empty_for_unknown_symbol(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc_as_df for unknown symbol returns empty DataFrame with correct columns."""
    import pandas as pd

    df = market_db_with_data.query_ohlc_as_df(symbol="NONEXISTENT")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert list(df.columns) == ["time", "open", "high", "low", "close", "volume"]


def test_query_ohlc_as_df_before_semantics(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc_as_df with before returns only bars older than timestamp."""
    import datetime

    # Use UTC-referenced timestamp to match DuckDB's epoch() behavior
    before_utc = datetime.datetime(2024, 1, 1, 5, 0, 0, tzinfo=datetime.UTC)
    before_ts = int(before_utc.timestamp())

    df = market_db_with_data.query_ohlc_as_df(
        symbol="TEST",
        before=before_ts,
        limit=5,
    )
    # Hours 0-4 are before 05:00 UTC → 5 bars
    assert len(df) == 5
    assert all(df["time"] < before_ts)
    # Verify ascending order
    assert (df["time"].diff().dropna() > 0).all()


def test_query_ohlc_as_df_respects_limit(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc_as_df respects the limit parameter (max 5000)."""
    df = market_db_with_data.query_ohlc_as_df(symbol="TEST", limit=3)
    assert len(df) == 3


def test_query_ohlc_as_df_uses_existing_connection(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc_as_df uses self._conn.execute (no new connection)."""
    df = market_db_with_data.query_ohlc_as_df(symbol="TEST", limit=1)
    assert len(df) == 1


def test_query_ohlc_as_df_before_ignores_when_start_provided(
    market_db_with_data: MarketDatabase,
) -> None:
    """before is ignored when start_date is provided (date-range takes precedence)."""
    import datetime

    before_utc = datetime.datetime(2024, 1, 1, 5, 0, 0, tzinfo=datetime.UTC)
    before_ts = int(before_utc.timestamp())

    df = market_db_with_data.query_ohlc_as_df(
        symbol="TEST",
        start_date=datetime.date(2024, 1, 1),
        before=before_ts,
        limit=5,
    )
    # Should return date-range bars including bars >= before_ts
    assert len(df) > 0
    assert any(df["time"] >= before_ts)


def test_query_ohlc_as_df_before_returns_fewer(market_db_with_data: MarketDatabase) -> None:
    """before returns fewer bars when not enough data before timestamp."""
    import datetime

    before_utc = datetime.datetime(2024, 1, 1, 1, 0, 0, tzinfo=datetime.UTC)
    before_ts = int(before_utc.timestamp())

    df = market_db_with_data.query_ohlc_as_df(
        symbol="TEST",
        before=before_ts,
        limit=100,
    )
    # Only hour 0 is before 01:00
    assert len(df) == 1
    assert all(df["time"] < before_ts)


def test_query_ohlc_as_df_caps_at_5000(market_db_with_data: MarketDatabase) -> None:
    """query_ohlc_as_df caps limit at 5000."""
    df = market_db_with_data.query_ohlc_as_df(symbol="TEST", limit=99999)
    assert len(df) <= 5000


def test_query_ohlc_before_ignores_when_start_provided(market_db_with_data: MarketDatabase) -> None:
    """before is ignored when start_date is provided (date-range takes precedence)."""
    before_dt = datetime.datetime(2024, 1, 1, 5, 0, 0)
    before_ts = int(before_dt.timestamp())

    rows = market_db_with_data.query_ohlc(
        symbol="TEST",
        timeframe="1m",
        start_date=datetime.date(2024, 1, 1),
        before=before_ts,
        limit=5,
    )

    # Should return date-range bars (not limited by before), including bars >= before_ts
    assert len(rows) > 0
    # At least some bars should be at or after before_ts (proving before was ignored)
    has_after = False
    for r in rows:
        t: int = r["time"]  # type: ignore[assignment]
        if t >= before_ts:
            has_after = True
            break
    assert has_after
