"""Synthetische Kurse für Tests."""

import numpy as np
import pandas as pd

from entrywatcher.config import AppConfig, BacktestSettings, RiskSettings, RuleSettings, TaxRules, WatchItem


def ohlc(closes, start="2020-01-01", spread=0.01, opens=None):
    idx = pd.bdate_range(start, periods=len(closes))
    c = np.asarray(closes, dtype=float)
    o = np.asarray(opens, dtype=float) if opens is not None else c
    return pd.DataFrame({"Open": o, "High": np.maximum(c, o) * (1 + spread),
                         "Low": np.minimum(c, o) * (1 - spread), "Close": c}, index=idx)


def rising(n=400, start=100.0, step=0.001):
    return ohlc(start * np.cumprod(np.full(n, 1 + step)))


def config(**rules) -> AppConfig:
    return AppConfig(RiskSettings(), RuleSettings(**rules), TaxRules(), BacktestSettings(),
                     (WatchItem("TEST", "Test AG"),))


class FakePrices:
    def __init__(self, frames: dict):
        self.frames = frames

    def ohlc(self, ticker, start="2000-01-01"):
        f = self.frames[ticker]
        return f[f.index >= pd.Timestamp(start)]


class FakeEarnings:
    def __init__(self, when=None):
        self.when = when

    def next_date(self, ticker):
        return self.when
