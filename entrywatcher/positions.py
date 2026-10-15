"""Gekaufte Positionen: nachgezogener Stop je Position und ob er gerissen ist.

Die Datei data/positions.json pflegst du selbst nach dem Kauf (E-009):
  [{"ticker": "ENR.DE", "name": "Siemens Energy", "entry_date": "2026-11-03",
    "entry_price": 131.20, "shares": 7, "initial_stop": 119.50}]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import AppConfig
from .indicators import Indicators
from .market_data import PriceSource
from .risk import StopCalculator

HOLD = "HALTEN"
SELL = "VERKAUFEN"


@dataclass(frozen=True)
class Position:
    ticker: str
    entry_date: str
    entry_price: float
    shares: int
    initial_stop: float
    name: str = ""


@dataclass(frozen=True)
class PositionReport:
    position: Position
    day: pd.Timestamp
    close: float
    stop: float
    highest_close: float

    @property
    def status(self) -> str:
        return SELL if self.close < self.stop else HOLD

    @property
    def gain(self) -> float:
        return self.position.shares * (self.close - self.position.entry_price)

    @property
    def locked_in(self) -> float:
        """Ergebnis, falls genau zum Stop verkauft würde."""
        return self.position.shares * (self.stop - self.position.entry_price)


class PositionBook:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)

    def load(self) -> list[Position]:
        if not self._path.exists():
            return []
        return [Position(**p) for p in json.loads(self._path.read_text(encoding="utf-8"))]


class PositionTracker:
    """Stop = max(Anfangsstop, höchster Schluss seit Kauf − atr_multiple × ATR), auf Schlusskursen."""

    def __init__(self, config: AppConfig, prices: PriceSource) -> None:
        self._cfg = config
        self._prices = prices

    def report(self, position: Position) -> PositionReport:
        start = (pd.Timestamp(position.entry_date) - pd.DateOffset(months=3)).strftime("%Y-%m-%d")
        ind = Indicators(self._cfg.rules, self._cfg.risk).compute(self._prices.ohlc(position.ticker, start))
        since = ind.loc[ind.index >= pd.Timestamp(position.entry_date)]
        if since.empty:
            raise ValueError(f"{position.ticker}: keine Kurse seit {position.entry_date}")
        highest = max(since["close"].max(), position.entry_price)
        last = since.iloc[-1]
        stop = StopCalculator(self._cfg.risk).trailing(position.initial_stop, highest, last["atr"])
        return PositionReport(position, since.index[-1], last["close"], stop, highest)
