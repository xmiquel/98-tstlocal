"""Contract tests for application settings.

Tests cover default values, environment variable overrides,
and type coercion from string to the expected Python types.
"""

from app.settings import Settings


def test_default_values() -> None:
    """Settings() with no env overrides returns sensible defaults."""
    settings = Settings()
    assert settings.APP_NAME == "98-tstlocal"
    assert settings.DEBUG is False
    assert settings.HOST == "0.0.0.0"  # noqa: S104 — matches dev-server default
    assert settings.PORT == 8000
    assert settings.DATABASE_URL == "sqlite:///./data/trading.db"


def test_env_override_partial() -> None:
    """Settings(HOST=...) overrides only the given field; others stay default."""
    settings = Settings(HOST="1.2.3.4")
    assert settings.HOST == "1.2.3.4"
    assert settings.APP_NAME == "98-tstlocal"
    assert settings.DEBUG is False
    assert settings.PORT == 8000


def test_env_override_all() -> None:
    """Settings(...) with all keyword arguments overrides every field."""
    settings = Settings(
        APP_NAME="custom-app",
        DEBUG=True,
        HOST="127.0.0.1",
        PORT=9000,
        DATABASE_URL="sqlite:///./custom.db",
    )
    assert settings.APP_NAME == "custom-app"
    assert settings.DEBUG is True
    assert settings.HOST == "127.0.0.1"
    assert settings.PORT == 9000
    assert settings.DATABASE_URL == "sqlite:///./custom.db"


def test_type_coercion_debug_string_true() -> None:
    """DEBUG='true' is coerced from string to bool True."""
    settings = Settings(DEBUG="true")  # type: ignore[arg-type]
    assert settings.DEBUG is True
    assert isinstance(settings.DEBUG, bool)


def test_type_coercion_debug_string_false() -> None:
    """DEBUG='false' is coerced from string to bool False."""
    settings = Settings(DEBUG="false")  # type: ignore[arg-type]
    assert settings.DEBUG is False
    assert isinstance(settings.DEBUG, bool)


def test_type_coercion_port_string() -> None:
    """PORT='9000' is coerced from string to int 9000."""
    settings = Settings(PORT="9000")  # type: ignore[arg-type]
    assert settings.PORT == 9000
    assert isinstance(settings.PORT, int)


def test_type_coercion_port_string_zero_padded() -> None:
    """PORT='08000' is coerced to int 8000 (octal interpretation avoided)."""
    settings = Settings(PORT="08000")  # type: ignore[arg-type]
    assert settings.PORT == 8000
    assert isinstance(settings.PORT, int)


def test_market_db_path_default() -> None:
    """MARKET_DB_PATH defaults to data/market.duckdb."""
    from app.settings import settings

    assert settings.MARKET_DB_PATH == "data/market.duckdb"
