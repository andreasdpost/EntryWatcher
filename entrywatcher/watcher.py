"""Prüft eine Aktie der Watchlist am letzten Handelstag: Regeln, Termin, Stop, Größe."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from .config import AppConfig, WatchItem
from .earnings import EarningsCalendar
from .indicators import Indicators, market_uptrend
from .market_data import PriceSource
from .risk import PositionSize, PositionSizer, StopCalculator, StopLevel
from .rules import RuleResult, RuleSet

BUY = "KAUFEN ERLAUBT"
WAIT = "WARTEN"


@dataclass(frozen=True)
class Assessment:
    item: WatchItem
    day: pd.Timestamp
    close: float
    atr: float
    checks: list[RuleResult]
    stop: StopLevel
    size: PositionSize

    @property
    def status(self) -> str:
        return BUY if all(c.passed for c in self.checks) and self.size.shares > 0 else WAIT


class EntryWatcher:
    def __init__(self, config: AppConfig, prices: PriceSource, earnings: EarningsCalendar,
                 today: date | None = None) -> None:
        self._cfg = config
        self._prices = prices
        self._earnings = earnings
        self._today = today or date.today()
        self._rules = RuleSet.from_settings(config.rules)
        self._market_up: pd.Series | None = None

    def _market(self) -> pd.Series:
        if self._market_up is None:
            close = self._prices.ohlc(self._cfg.rules.market_ticker, self._start())["Close"]
            self._market_up = market_uptrend(close, self._cfg.rules.trend_sma_days)
        return self._market_up

    def _start(self) -> str:
        return (pd.Timestamp(self._today) - pd.DateOffset(years=3)).strftime("%Y-%m-%d")

    def assess(self, item: WatchItem) -> Assessment:
        risk = item.risk(self._cfg.risk)
        ind = Indicators(self._cfg.rules, risk).compute(self._prices.ohlc(item.ticker, self._start()))
        day = ind.index[-1]
        row = ind.loc[day]
        checks = self._rules.check(ind, self._market(), day) + [self._earnings_check(item.ticker)]
        stop = StopCalculator(risk).initial(row["close"], row["atr"], row["swing_low"])
        size = PositionSizer(risk).size(row["close"], stop)
        checks.append(RuleResult(f"Stop-Abstand höchstens {risk.max_stop_distance:.0%}",
                                  stop.distance <= risk.max_stop_distance, f"{stop.distance:.1%}"))
        return Assessment(item, day, row["close"], row["atr"], checks, stop, size)

    def _earnings_check(self, ticker: str) -> RuleResult:
        block = self._cfg.rules.earnings_block_days
        name = f"Keine Quartalszahlen in den nächsten {block} Tagen"
        when = self._earnings.next_date(ticker)
        if when is None:
            return RuleResult(name, True, "Termin unbekannt")
        days = (when - self._today).days
        return RuleResult(name, days < 0 or days > block, f"in {days} Tagen ({when:%d.%m.})")
