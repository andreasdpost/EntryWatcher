"""Kennzahlen je Handelstag aus Kursen. Nur Rechnung, keine Regeln."""

from __future__ import annotations

import pandas as pd

from .config import RiskSettings, RuleSettings


class Indicators:
    """Rechnet alle Spalten, die Regeln und Stop brauchen, für die ganze Historie.

    Jeder Wert an Tag t nutzt nur Kurse bis einschließlich t.
    """

    def __init__(self, rules: RuleSettings, risk: RiskSettings) -> None:
        self._rules = rules
        self._risk = risk

    def compute(self, ohlc: pd.DataFrame) -> pd.DataFrame:
        r, k = self._rules, self._risk
        close, high, low = ohlc["Close"], ohlc["High"], ohlc["Low"]
        prev_close = close.shift()
        true_range = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()],
                               axis=1).max(axis=1)
        out = pd.DataFrame(index=ohlc.index)
        out["close"] = close
        out["high"] = high
        out["low"] = low
        out["sma_trend"] = close.rolling(r.trend_sma_days, min_periods=r.trend_sma_days).mean()
        out["sma_fast"] = close.rolling(r.fast_sma_days, min_periods=r.fast_sma_days).mean()
        out["ema"] = close.ewm(span=r.ema_days, adjust=False).mean()
        out["atr"] = true_range.rolling(k.atr_days, min_periods=k.atr_days).mean()
        out["return_1m"] = close / close.shift(r.momentum_skip_days) - 1
        out["momentum_12_1"] = close.shift(r.momentum_skip_days) / close.shift(r.momentum_days) - 1
        out["swing_low"] = low.rolling(k.swing_low_days, min_periods=k.swing_low_days).min()
        out["pulled_back"] = (low <= out["ema"]).rolling(r.pullback_days, min_periods=1).max().astype(bool)
        out["prev_high"] = high.shift()
        return out


def market_uptrend(market_close: pd.Series, days: int) -> pd.Series:
    """True, solange der Markt über seinem Durchschnitt der letzten `days` Schlusskurse liegt."""
    return market_close > market_close.rolling(days, min_periods=days).mean()
