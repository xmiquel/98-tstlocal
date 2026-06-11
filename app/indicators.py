"""Indicator engine wrapping pandas-ta-classic with TTLCache.

Computes SMA, EMA, RSI, MACD, and Bollinger Bands from OHLCV DataFrames.
Results are cached via a TTLCache with 300-second TTL, keyed by
(symbol, timeframe, indicator name, params hash).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pandas as pd
import pandas_ta_classic as ta  # type: ignore[import-untyped]
from cachetools import TTLCache

# Static catalog of supported indicators with their parameters.
CATALOG: list[dict[str, Any]] = [
    {
        "name": "SMA",
        "params": [
            {
                "name": "timeperiod",
                "type": "int",
                "default": 20,
                "description": "Number of periods",
            },
        ],
    },
    {
        "name": "EMA",
        "params": [
            {
                "name": "timeperiod",
                "type": "int",
                "default": 20,
                "description": "Number of periods",
            },
        ],
    },
    {
        "name": "RSI",
        "params": [
            {
                "name": "timeperiod",
                "type": "int",
                "default": 14,
                "description": "Number of periods",
            },
        ],
    },
    {
        "name": "MACD",
        "params": [
            {"name": "fastperiod", "type": "int", "default": 12, "description": "Fast EMA period"},
            {"name": "slowperiod", "type": "int", "default": 26, "description": "Slow EMA period"},
            {
                "name": "signalperiod",
                "type": "int",
                "default": 9,
                "description": "Signal line period",
            },
        ],
    },
    {
        "name": "BBANDS",
        "params": [
            {
                "name": "timeperiod",
                "type": "int",
                "default": 20,
                "description": "Moving average period",
            },
            {
                "name": "nbdevup",
                "type": "float",
                "default": 2,
                "description": "Std devs above (upper band)",
            },
            {
                "name": "nbdevdn",
                "type": "float",
                "default": 2,
                "description": "Std devs below (lower band)",
            },
        ],
    },
]

# Map catalog param names to pandas_ta keyword argument names.
_PARAM_MAP: dict[str, dict[str, str]] = {
    "SMA": {"timeperiod": "length"},
    "EMA": {"timeperiod": "length"},
    "RSI": {"timeperiod": "length"},
    "MACD": {"fastperiod": "fast", "slowperiod": "slow", "signalperiod": "signal"},
    "BBANDS": {"timeperiod": "length"},
}


def _make_cache_key(
    symbol: str,
    timeframe: str,
    indicator: str,
    params: dict[str, Any],
) -> str:
    """Generate a deterministic cache key from symbol, timeframe, indicator, params."""
    raw = json.dumps(
        {"symbol": symbol, "timeframe": timeframe, "indicator": indicator, "params": params},
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


class IndicatorEngine:
    """Computes technical indicators using pandas-ta-classic with TTLCache.

    Usage:
        engine = IndicatorEngine()
        results = engine.calculate(
            df, {"name": "SMA", "params": {"timeperiod": 20}},
            symbol="NDX", timeframe="1m",
        )
        # returns [{"label": "SMA(20)", "values": [{"time": ..., "value": ...}]}]
    """

    def __init__(self) -> None:
        """Initialize with a 300-second TTLCache (maxsize 256)."""
        self._cache: TTLCache[str, list[dict[str, Any]]] = TTLCache(maxsize=256, ttl=300)

    def calculate(
        self,
        df: pd.DataFrame,
        config: dict[str, Any],
        symbol: str = "",
        timeframe: str = "",
    ) -> list[dict[str, Any]]:
        """Compute the indicator for the given OHLCV DataFrame.

        Args:
            df: DataFrame with columns time, open, high, low, close, volume.
            config: Dict with 'name' (str) and 'params' (dict).
            symbol: Market symbol for cache key isolation.
            timeframe: Timeframe string for cache key isolation.

        Returns:
            List of result dicts, each with 'label' (str) and 'values'
            (list of {time, value}). Multi-line indicators (MACD, BBANDS)
            return multiple entries; single-line indicators return one.
        """
        name = config["name"]
        params = config.get("params", {})

        cache_key = _make_cache_key(symbol, timeframe, name, params)
        if cache_key in self._cache:
            return self._cache[cache_key]

        close = df["close"]

        if name == "SMA":
            length = int(params.get("timeperiod", 20))
            result_series = ta.sma(close, length=length)
            results = self._series_to_results(result_series, df["time"], f"SMA({length})")

        elif name == "EMA":
            length = int(params.get("timeperiod", 20))
            result_series = ta.ema(close, length=length)
            results = self._series_to_results(result_series, df["time"], f"EMA({length})")

        elif name == "RSI":
            length = int(params.get("timeperiod", 14))
            result_series = ta.rsi(close, length=length)
            results = self._series_to_results(result_series, df["time"], f"RSI({length})")

        elif name == "MACD":
            fast = int(params.get("fastperiod", 12))
            slow = int(params.get("slowperiod", 26))
            signal = int(params.get("signalperiod", 9))
            macd_df = ta.macd(close, fast=fast, slow=slow, signal=signal)
            results = self._macd_to_results(macd_df, df["time"], fast, slow, signal)

        elif name == "BBANDS":
            length = int(params.get("timeperiod", 20))
            nbdevup = float(params.get("nbdevup", 2))
            nbdevdn = float(params.get("nbdevdn", 2))
            bb_df = ta.bbands(close, length=length, std=nbdevup)
            results = self._bbands_to_results(bb_df, df["time"], length, nbdevup, nbdevdn)

        else:
            msg = f"Unknown indicator: {name}"
            raise ValueError(msg)

        self._cache[cache_key] = results
        return results

    def _series_to_results(
        self,
        series: pd.Series,
        times: pd.Series,
        label: str,
    ) -> list[dict[str, Any]]:
        """Convert a single pandas_ta Series to a result list with one entry.

        Keeps NaN entries as null so the output length matches the input candles.
        Lightweight Charts renders null as gaps, preserving time alignment.
        """
        values = [
            {"time": int(t), "value": float(v) if not pd.isna(v) else None}
            for t, v in zip(times, series, strict=False)
        ]
        return [{"label": label, "values": values}]

    def _macd_to_results(
        self,
        macd_df: pd.DataFrame,
        times: pd.Series,
        fast: int,  # noqa: ARG002
        slow: int,  # noqa: ARG002
        signal: int,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Convert MACD DataFrame to three result lines."""
        lines: list[dict[str, Any]] = []
        for col in macd_df.columns:
            col_str = str(col)
            if col_str.startswith("MACDh"):
                line_label = "MACD_HIST"
            elif col_str.startswith("MACDs"):
                line_label = "MACD_SIGNAL"
            else:
                line_label = "MACD"

            series = macd_df[col]
            values = [
                {"time": int(t), "value": float(v) if not pd.isna(v) else None}
                for t, v in zip(times, series, strict=False)
            ]
            lines.append({"label": line_label, "values": values})
        return lines

    def _bbands_to_results(
        self,
        bb_df: pd.DataFrame,
        times: pd.Series,
        length: int,  # noqa: ARG002
        nbdevup: float,  # noqa: ARG002
        nbdevdn: float,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Convert Bollinger Bands DataFrame to three result lines.

        Returns BB_UPPER, BB_MIDDLE, BB_LOWER (skips BBB and BBP).
        """
        col_map: dict[str, str] = {
            "BBU": "BB_UPPER",
            "BBM": "BB_MIDDLE",
            "BBL": "BB_LOWER",
        }
        lines: list[dict[str, Any]] = []
        for col in bb_df.columns:
            col_str = str(col)
            prefix = col_str.split("_")[0]
            line_label = col_map.get(prefix)
            if line_label is None:
                continue  # skip BBB, BBP

            series = bb_df[col]
            values = [
                {"time": int(t), "value": float(v) if not pd.isna(v) else None}
                for t, v in zip(times, series, strict=False)
            ]
            lines.append({"label": line_label, "values": values})
        return lines
