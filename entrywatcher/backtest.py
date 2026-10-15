"""Backtest der Regeln über viele Aktien.

Je Aktie ein eigenes Konto mit Budget nach RiskSettings; Einstieg zum Schluss
des Tages nach dem Signal; Ausstieg wie eine echte Stop-Loss-Order: fällt das
Tagestief auf oder unter den Stop, wird zum Stop verkauft — oder zum
Eröffnungskurs, wenn dieser schon darunter lag (Kurslücke, E-010).
Steuer: alle Verkäufe aller Aktien laufen zeitlich geordnet durch EIN
Steuerkonto, wie im echten Depot.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import BacktestSettings, RiskSettings
from .risk import PositionSizer, StopCalculator
from .rules import RuleSet
from .tax import GermanTaxAccount


@dataclass(frozen=True)
class Trade:
    ticker: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    shares: int
    entry_price: float
    exit_price: float
    costs: float                 # Gebühren + Spanne, Kauf und Verkauf

    @property
    def gain(self) -> float:
        return self.shares * (self.exit_price - self.entry_price) - self.costs

    @property
    def invested(self) -> float:
        return self.shares * self.entry_price


class TradeSimulator:
    def __init__(self, rules: RuleSet, risk: RiskSettings, costs: BacktestSettings) -> None:
        self._rules = rules
        self._risk = risk
        self._costs = costs
        self._stops = StopCalculator(risk)
        self._sizer = PositionSizer(risk)

    def run(self, ticker: str, ind: pd.DataFrame, opens: pd.Series, market_up: pd.Series,
            start: pd.Timestamp | None = None, close_open_at_end: bool = True) -> list[Trade]:
        allowed = self._rules.entry_allowed(ind, market_up)
        rows = ind.assign(open=opens.reindex(ind.index), allowed=allowed)
        if start is not None:
            rows = rows.loc[rows.index >= start]
        trades: list[Trade] = []
        pos = None
        signal = False
        for day, r in rows.iterrows():
            if pos is not None:
                if r["low"] <= pos["stop"]:
                    exit_price = min(r["open"], pos["stop"]) if pd.notna(r["open"]) else pos["stop"]
                    trades.append(self._close(ticker, pos, day, exit_price))
                    pos = None
                else:
                    pos["high"] = max(pos["high"], r["close"])
                    pos["stop"] = self._stops.trailing(pos["stop0"], pos["high"], r["atr"])
            elif signal and pd.notna(r["atr"]) and pd.notna(r["swing_low"]):
                stop = self._stops.initial(r["close"], r["atr"], r["swing_low"])
                size = self._sizer.size(r["close"], stop)
                if size.shares > 0:
                    pos = dict(day=day, price=r["close"], shares=size.shares, stop0=stop.price,
                               stop=stop.price, high=r["close"])
            signal = bool(r["allowed"]) and pos is None
        if pos is not None and close_open_at_end:
            trades.append(self._close(ticker, pos, rows.index[-1], rows["close"].iloc[-1]))
        return trades

    def _close(self, ticker: str, pos: dict, day: pd.Timestamp, price: float) -> Trade:
        value_in, value_out = pos["shares"] * pos["price"], pos["shares"] * price
        costs = 2 * self._costs.fee_per_order + self._costs.half_spread * (value_in + value_out)
        return Trade(ticker, pos["day"], day, pos["shares"], pos["price"], price, costs)


def taxes_paid(trades: list[Trade], tax_factory) -> float:
    """Steuer aller Verkäufe, zeitlich geordnet durch ein Steuerkonto (Verlustverrechnung)."""
    account: GermanTaxAccount = tax_factory()
    for t in sorted(trades, key=lambda t: t.exit_date):
        account.realize(t.gain, t.exit_date.year)
    return account.total_paid


def time_invested(trades: list[Trade], index: pd.DatetimeIndex) -> float:
    invested = pd.Series(False, index=index)
    for t in trades:
        invested.loc[t.entry_date:t.exit_date] = True
    return float(invested.mean()) if len(index) else 0.0
