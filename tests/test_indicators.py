"""Tests for the IndicatorEngine (pandas-ta-classic wrapper with TTLCache)."""

from __future__ import annotations

import pandas as pd
import pytest

from app.indicators import CATALOG, IndicatorEngine


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """Create a 250-bar OHLCV DataFrame for testing indicators."""
    import numpy as np

    base_ts = 1704067200  # 2024-01-01 00:00:00 UTC
    n = 250
    return pd.DataFrame(
        {
            "time": [base_ts + i * 60 for i in range(n)],
            "open": 100.0 + np.random.default_rng(42).normal(0, 0.5, n).cumsum(),
            "high": 100.0 + np.random.default_rng(43).normal(0, 0.5, n).cumsum(),
            "low": 100.0 + np.random.default_rng(44).normal(0, 0.5, n).cumsum(),
            "close": 100.0 + np.random.default_rng(45).normal(0, 0.5, n).cumsum(),
            "volume": [1000 + i * 10 for i in range(n)],
        }
    )


def test_catalog_contains_5_entries() -> None:
    """CATALOG has exactly 5 indicator definitions."""
    assert len(CATALOG) == 5
    names = {e["name"] for e in CATALOG}
    assert names == {"SMA", "EMA", "RSI", "MACD", "BBANDS"}


class TestIndicatorEngine:
    """Tests for the IndicatorEngine class."""

    # ── Indicator correctness ─────────────────────────────────────────────

    def test_sma_calculates_label_and_values(self, ohlcv_df: pd.DataFrame) -> None:
        """SMA returns label 'SMA(20)' and correct number of values.

        Now returns ALL points (length == input length) with None for warmup NaN.
        """
        engine = IndicatorEngine()
        config = {"name": "SMA", "params": {"timeperiod": 20}}
        results = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(results) == 1
        assert results[0]["label"] == "SMA(20)"
        assert len(results[0]["values"]) == len(ohlcv_df)  # full alignment
        # First 19 should be None (warmup), rest should be float
        non_none = [v for v in results[0]["values"] if v["value"] is not None]
        assert len(non_none) == len(ohlcv_df) - 19
        for v in results[0]["values"]:
            assert "time" in v
            assert "value" in v
            assert isinstance(v["time"], int)

    def test_ema_calculates_label_and_values(self, ohlcv_df: pd.DataFrame) -> None:
        """EMA returns label 'EMA(20)' with values."""
        engine = IndicatorEngine()
        config = {"name": "EMA", "params": {"timeperiod": 20}}
        results = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(results) == 1
        assert results[0]["label"] == "EMA(20)"
        assert len(results[0]["values"]) > 0
        assert len(results[0]["values"]) <= len(ohlcv_df)

    def test_rsi_calculates_label_and_values(self, ohlcv_df: pd.DataFrame) -> None:
        """RSI returns label 'RSI(14)' with values."""
        engine = IndicatorEngine()
        config = {"name": "RSI", "params": {"timeperiod": 14}}
        results = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(results) == 1
        assert results[0]["label"] == "RSI(14)"
        assert len(results[0]["values"]) == len(ohlcv_df)  # full alignment
        # RSI values should be between 0 and 100 (skip None warmup)
        for v in results[0]["values"]:
            if v["value"] is not None:
                assert 0 <= v["value"] <= 100

    def test_macd_returns_multiple_lines(self, ohlcv_df: pd.DataFrame) -> None:
        """MACD returns three result lines: MACD, MACD_SIGNAL, MACD_HIST."""
        engine = IndicatorEngine()
        config = {"name": "MACD", "params": {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}}
        results = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(results) == 3
        labels = {r["label"] for r in results}
        assert "MACD" in labels
        assert "MACD_SIGNAL" in labels
        assert "MACD_HIST" in labels
        for r in results:
            assert len(r["values"]) > 0

    def test_bbands_returns_multiple_lines(self, ohlcv_df: pd.DataFrame) -> None:
        """BBANDS returns three result lines: BB_UPPER, BB_MIDDLE, BB_LOWER."""
        engine = IndicatorEngine()
        config = {"name": "BBANDS", "params": {"timeperiod": 20, "nbdevup": 2, "nbdevdn": 2}}
        results = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(results) == 3
        labels = {r["label"] for r in results}
        assert "BB_UPPER" in labels
        assert "BB_MIDDLE" in labels
        assert "BB_LOWER" in labels
        for r in results:
            assert len(r["values"]) > 0

    # ── Cache behavior ────────────────────────────────────────────────────

    def test_cache_hit_returns_same_as_first_call(self, ohlcv_df: pd.DataFrame) -> None:
        """Second call with same symbol/timeframe/params returns cached result."""
        engine = IndicatorEngine()
        config = {"name": "SMA", "params": {"timeperiod": 10}}

        first = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(engine._cache) > 0

        second = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert first[0]["label"] == second[0]["label"]
        assert len(first[0]["values"]) == len(second[0]["values"])
        for v1, v2 in zip(first[0]["values"], second[0]["values"], strict=True):
            assert v1 == v2

    def test_cache_miss_with_different_params(self, ohlcv_df: pd.DataFrame) -> None:
        """Different params produce different results (cache key differs)."""
        engine = IndicatorEngine()
        config_10 = {"name": "SMA", "params": {"timeperiod": 10}}
        config_50 = {"name": "SMA", "params": {"timeperiod": 50}}

        result_10 = engine.calculate(ohlcv_df, config_10, "TEST", "1m")
        result_50 = engine.calculate(ohlcv_df, config_50, "TEST", "1m")

        # Both return full alignment (same length), but non-None values differ
        assert len(result_10[0]["values"]) == len(result_50[0]["values"]) == len(ohlcv_df)
        # Compare first non-None value to ensure different results
        val_10 = next(v["value"] for v in result_10[0]["values"] if v["value"] is not None)
        val_50 = next(v["value"] for v in result_50[0]["values"] if v["value"] is not None)
        assert val_10 != val_50

    def test_cache_key_includes_symbol(self, ohlcv_df: pd.DataFrame) -> None:
        """Same indicator/params but different symbol => separate cache entries."""
        engine = IndicatorEngine()
        config = {"name": "SMA", "params": {"timeperiod": 20}}

        engine.calculate(ohlcv_df, config, "SYM_A", "1m")
        engine.calculate(ohlcv_df, config, "SYM_B", "1m")

        # Two symbols => two cache entries (same indicator/params but diff symbol)
        assert len(engine._cache) == 2

    def test_cache_key_includes_timeframe(self, ohlcv_df: pd.DataFrame) -> None:
        """Same symbol/indicator but different timeframe => separate cache entries."""
        engine = IndicatorEngine()
        config = {"name": "SMA", "params": {"timeperiod": 20}}

        engine.calculate(ohlcv_df, config, "TEST", "1m")
        engine.calculate(ohlcv_df, config, "TEST", "5m")

        # Two timeframes => two cache entries
        assert len(engine._cache) == 2

    # ── NaN handling ──────────────────────────────────────────────────────

    def test_nan_values_preserved_as_none_for_alignment(self, ohlcv_df: pd.DataFrame) -> None:
        """NaN values from warmup period are preserved as None for time alignment."""
        engine = IndicatorEngine()
        config = {"name": "SMA", "params": {"timeperiod": 200}}
        results = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(results) == 1
        assert len(results[0]["values"]) == len(ohlcv_df)  # full alignment
        # First 199 should be None (warmup), last 51 should have values
        none_count = sum(1 for v in results[0]["values"] if v["value"] is None)
        assert none_count == 199
        non_none_count = sum(1 for v in results[0]["values"] if v["value"] is not None)
        assert non_none_count == 51
        # Verify no actual NaN survived (None instead)
        for v in results[0]["values"]:
            if v["value"] is not None:
                assert not (isinstance(v["value"], float) and pd.isna(v["value"]))

    # ── Error handling ────────────────────────────────────────────────────

    def test_unknown_indicator_raises_value_error(self, ohlcv_df: pd.DataFrame) -> None:
        """Unknown indicator name raises ValueError."""
        engine = IndicatorEngine()
        config = {"name": "INVALID", "params": {}}
        with pytest.raises(ValueError, match="Unknown indicator"):
            engine.calculate(ohlcv_df, config, "TEST", "1m")

    # ── Cache lifecycle ───────────────────────────────────────────────────

    def test_cache_ttl_is_300_seconds(self) -> None:
        """TTLCache has a 300-second TTL."""
        engine = IndicatorEngine()
        assert engine._cache.ttl == 300

    def test_cache_maxsize_is_256(self) -> None:
        """TTLCache has maxsize 256 (matches design doc)."""
        engine = IndicatorEngine()
        assert engine._cache.maxsize == 256

    def test_ttl_expiry_causes_cache_miss(
        self, ohlcv_df: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When TTL expires, pandas-ta is called again proving cache eviction.

        Spec scenario: TTLCache recomputes after 5 minutes.
        GIVEN same symbol+indicator was computed 6 minutes ago
        WHEN calculate() is called
        THEN pandas-ta-classic SHALL be called (cache miss)
        """
        import pandas_ta_classic as ta  # type: ignore[import-untyped]
        from cachetools import TTLCache

        # TTLCache resolves the timer function at import time, so global
        # patching of time.time has no effect. We inject a custom timer.
        custom_time: list[float] = [1000000.0]

        def fake_timer() -> float:
            return custom_time[0]

        engine = IndicatorEngine()
        # Replace the default cache with one that uses our controlled timer
        engine._cache = TTLCache(maxsize=128, ttl=300, timer=fake_timer)

        config = {"name": "SMA", "params": {"timeperiod": 20}}

        # First calculation at T=1000000 — populates cache
        engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert len(engine._cache) == 1

        # Spy on ta.sma to track whether it's called
        original_sma = ta.sma
        call_counter: list[int] = [0]

        def counting_sma(*args: object, **kwargs: object) -> object:  # noqa: ANN401
            call_counter[0] += 1
            return original_sma(*args, **kwargs)

        monkeypatch.setattr(ta, "sma", counting_sma)

        # At T=1000000 (same time, within TTL) — should be cache hit
        result = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert call_counter[0] == 0, "ta.sma should NOT be called within TTL"
        assert result[0]["label"] == "SMA(20)"

        # Advance time past TTL (T=1000301) — cache miss
        custom_time[0] = 1000301.0
        result = engine.calculate(ohlcv_df, config, "TEST", "1m")
        assert call_counter[0] == 1, "ta.sma SHOULD be called after TTL expiry"
        assert result[0]["label"] == "SMA(20)"
