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


def test_table_created_on_connect(db: MarketDatabase) -> None:
    """Connecting to DuckDB creates dt_ohlc_m1 table."""
    tables = db._conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='dt_ohlc_m1'"
    ).fetchall()
    assert len(tables) == 1
    assert tables[0][0] == "dt_ohlc_m1"


def test_ingest_csv_inserts_rows(db: MarketDatabase, csv_file: str) -> None:
    """Ingesting a CSV inserts all rows with correct data."""
    origen = os.path.basename(csv_file)
    fecha_carga = datetime.datetime(2024, 1, 1, 12, 0, 0)
    count = db.ingest_csv(csv_file, origen, fecha_carga)
    assert count == 2

    rows = db._conn.execute("SELECT * FROM dt_ohlc_m1 ORDER BY datetime").fetchall()
    assert len(rows) == 2
    # Row 1
    assert str(rows[0][0]) == "2011-09-19 00:53:00"
    assert rows[0][1] == 5573.5  # open
    assert rows[0][2] == 5573.5  # high
    assert rows[0][3] == 5573.5  # low
    assert rows[0][4] == 5573.5  # close
    assert rows[0][5] == 2  # tickvol
    assert rows[0][6] == 20  # volume
    assert rows[0][7] == 0  # spread
    assert rows[0][8] == origen
    assert str(rows[0][9]) == "2024-01-01 12:00:00"


def test_ingest_metadata(db: MarketDatabase, csv_file: str) -> None:
    """origen and fecha_carga are set correctly."""
    origen = "test_asset.csv"
    fecha_carga = datetime.datetime(2024, 6, 9, 10, 30, 0)
    db.ingest_csv(csv_file, origen, fecha_carga)

    row = db._conn.execute("SELECT origen, fecha_carga FROM dt_ohlc_m1 LIMIT 1").fetchone()
    assert row is not None
    assert row[0] == "test_asset.csv"
    assert str(row[1]) == "2024-06-09 10:30:00"


def test_no_timezone_conversion(db: MarketDatabase, csv_file: str) -> None:
    """Datetime is stored as-is without timezone conversion."""
    db.ingest_csv(csv_file, "test.csv", datetime.datetime.now())
    row = db._conn.execute("SELECT datetime FROM dt_ohlc_m1 LIMIT 1").fetchone()
    assert row is not None
    assert str(row[0]) == "2011-09-19 00:53:00"


def test_empty_csv(db: MarketDatabase) -> None:
    """Ingesting an empty CSV inserts zero rows."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,open,high,low,close,tickvol,volume,spread\n")
        empty_path = f.name
    try:
        count = db.ingest_csv(empty_path, "empty.csv", datetime.datetime.now())
        assert count == 0
    finally:
        os.unlink(empty_path)


def test_truncate_clears_rows(db: MarketDatabase, csv_file: str) -> None:
    """truncate() removes all rows from dt_ohlc_m1."""
    db.ingest_csv(csv_file, "test.csv", datetime.datetime.now())
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
