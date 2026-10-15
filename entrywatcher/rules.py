"""Die Einstiegsregeln (Säule 2 und 4). Jede Regel ist eine Klasse mit genau einer Prüfung.

Jede Regel liefert eine boolesche Reihe über die ganze Historie (für den
Backtest) und erklärt sich für einen einzelnen Tag (für die Meldung).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from .config import RuleSettings


@dataclass(frozen=True)
class RuleResult:
    name: str
    passed: bool
    detail: str


class Rule(ABC):
    name: str

    @abstractmethod
    def series(self, ind: pd.DataFrame, market_up: pd.Series) -> pd.Series:
        """True an Tagen, an denen die Regel erfüllt ist. Fehlende Daten → False."""

    @abstractmethod
    def detail(self, row: pd.Series) -> str: ...

    def check(self, ind: pd.DataFrame, market_up: pd.Series, day: pd.Timestamp) -> RuleResult:
        return RuleResult(self.name, bool(self.series(ind, market_up).loc[day]), self.detail(ind.loc[day]))


class MarketTrend(Rule):
    name = "Markt über 200-Tage-Linie"

    def series(self, ind, market_up):
        return market_up.reindex(ind.index).ffill().fillna(False).astype(bool)

    def detail(self, row):
        return ""


class StockTrend(Rule):
    name = "Aktie über 200-Tage-Linie, 50er über 200er"

    def series(self, ind, market_up):
        return (ind["close"] > ind["sma_trend"]) & (ind["sma_fast"] > ind["sma_trend"])

    def detail(self, row):
        return f"Kurs {row['close'] / row['sma_trend'] - 1:+.0%} zur 200er"


class LongMomentum(Rule):
    name = "Momentum 12 Monate (ohne letzten) positiv"

    def series(self, ind, market_up):
        return ind["momentum_12_1"] > 0

    def detail(self, row):
        return f"{row['momentum_12_1']:+.0%}"


class NotOverheated(Rule):
    """Gegen das Muster aus 2026: Käufe nach +10 bis +43 % in einem Monat (E-005)."""

    def __init__(self, max_return_1m: float) -> None:
        self._max = max_return_1m
        self.name = f"Nicht überhitzt: letzter Monat unter {max_return_1m:+.0%}"

    def series(self, ind, market_up):
        return ind["return_1m"] < self._max

    def detail(self, row):
        return f"{row['return_1m']:+.0%}"


class NotExtended(Rule):
    def __init__(self, max_above: float) -> None:
        self._max = max_above
        self.name = f"Nicht mehr als {max_above:.0%} über der 50-Tage-Linie"

    def series(self, ind, market_up):
        return ind["close"] / ind["sma_fast"] - 1 < self._max

    def detail(self, row):
        return f"{row['close'] / row['sma_fast'] - 1:+.0%}"


class PullbackConfirmation(Rule):
    """Säule 2: Rücksetzer an die EMA in den letzten Tagen, heute Schluss über EMA und Vortageshoch."""

    name = "Bestätigung: Rücksetzer an EMA20, Schluss darüber und über Vortageshoch"

    def series(self, ind, market_up):
        return ind["pulled_back"] & (ind["close"] > ind["ema"]) & (ind["close"] > ind["prev_high"])

    def detail(self, row):
        return ""


class RuleSet:
    """Alle aktiven Regeln. Kauf nur, wenn jede erfüllt ist."""

    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules

    @classmethod
    def from_settings(cls, s: RuleSettings) -> "RuleSet":
        rules: list[Rule] = [MarketTrend(), StockTrend(), LongMomentum(),
                             NotOverheated(s.max_return_1m), NotExtended(s.max_above_fast_sma)]
        if s.confirmation:
            rules.append(PullbackConfirmation())
        return cls(rules)

    def entry_allowed(self, ind: pd.DataFrame, market_up: pd.Series) -> pd.Series:
        allowed = pd.Series(True, index=ind.index)
        for rule in self.rules:
            allowed &= rule.series(ind, market_up).fillna(False)
        return allowed

    def check(self, ind: pd.DataFrame, market_up: pd.Series, day: pd.Timestamp) -> list[RuleResult]:
        return [rule.check(ind, market_up, day) for rule in self.rules]
