"""Verdrahtet den Backtest: Daten, Varianten, Steuer, Bericht. Keine eigene Handelslogik."""

from __future__ import annotations

from dataclasses import dataclass, replace

import pandas as pd

from .backtest import Trade, TradeSimulator, taxes_paid, time_invested
from .config import AppConfig
from .indicators import Indicators, market_uptrend
from .market_data import PriceSource
from .rules import RuleSet
from .tax import GermanTaxAccount


@dataclass(frozen=True)
class Variant:
    label: str
    atr_multiple: float
    confirmation: bool


VARIANTS = (Variant("Standard: Stop 2×ATR, ohne Bestätigung", 2.0, False),
            Variant("Stop 3×ATR, ohne Bestätigung", 3.0, False),
            Variant("Stop 2×ATR, mit Bestätigung", 2.0, True))


@dataclass(frozen=True)
class VariantResult:
    variant: Variant
    trades: list[Trade]
    per_ticker: pd.DataFrame
    gain_before_tax: float
    taxes: float
    capital: float
    years: float

    def cagr(self, after_tax: bool) -> float:
        gain = self.gain_before_tax - (self.taxes if after_tax else 0.0)
        return ((self.capital + gain) / self.capital) ** (1 / self.years) - 1


class BacktestApp:
    def __init__(self, config: AppConfig, prices: PriceSource) -> None:
        self._cfg = config
        self._prices = prices

    def run(self) -> tuple[list[VariantResult], pd.DataFrame, pd.Timestamp, pd.Timestamp]:
        cfg = self._cfg
        data = {t: self._prices.ohlc(t, cfg.backtest.start) for t in cfg.backtest.tickers}
        market = self._prices.ohlc(cfg.rules.market_ticker, "1990-01-01")["Close"]
        market_up = market_uptrend(market, cfg.rules.trend_sma_days)
        start = pd.Timestamp(cfg.backtest.start) + pd.DateOffset(years=1)
        end = max(f.index[-1] for f in data.values())
        years = (end - start).days / 365.25
        results = [self._variant(v, data, market_up, start, years) for v in VARIANTS]
        return results, self._buy_and_hold(data, market, start, end, years), start, end

    def _variant(self, v: Variant, data, market_up, start, years) -> VariantResult:
        cfg = self._cfg
        risk = replace(cfg.risk, atr_multiple=v.atr_multiple)
        rules = replace(cfg.rules, confirmation=v.confirmation)
        sim = TradeSimulator(RuleSet.from_settings(rules), risk, cfg.backtest)
        all_trades, rows = [], []
        for ticker, ohlc in data.items():
            ind = Indicators(rules, risk).compute(ohlc)
            trades = sim.run(ticker, ind, ohlc["Open"], market_up, start)
            all_trades += trades
            wins = [t.gain for t in trades if t.gain > 0]
            losses = [t.gain for t in trades if t.gain <= 0]
            rows.append({"ticker": ticker, "trades": len(trades),
                         "hit_rate": len(wins) / len(trades) if trades else 0.0,
                         "avg_win": sum(wins) / len(wins) if wins else 0.0,
                         "avg_loss": sum(losses) / len(losses) if losses else 0.0,
                         "worst": min((t.gain for t in trades), default=0.0),
                         "gain": sum(t.gain for t in trades),
                         "invested_time": time_invested(trades, ind.loc[start:].index)})
        taxes = taxes_paid(all_trades, lambda: GermanTaxAccount(cfg.tax))
        capital = cfg.risk.max_position_eur * len(data)
        return VariantResult(v, all_trades, pd.DataFrame(rows),
                             sum(t.gain for t in all_trades), taxes, capital, years)

    def _buy_and_hold(self, data, market, start, end, years) -> pd.DataFrame:
        """Je Aktie das Budget am ersten möglichen Tag kaufen, am Ende verkaufen und versteuern."""
        cfg = self._cfg
        rate = cfg.tax.effective_rate * (1 - cfg.tax.partial_exemption)
        rows = []
        for ticker, ohlc in data.items():
            close = ohlc["Close"].loc[start:]
            gain = cfg.risk.max_position_eur * (close.iloc[-1] / close.iloc[0] - 1)
            rows.append({"ticker": ticker, "gain": gain})
        frame = pd.DataFrame(rows)
        m = market.loc[start:end]
        msci = cfg.risk.max_position_eur * len(data) * (m.iloc[-1] / m.iloc[0] - 1)
        frame.attrs["msci_gain"] = msci
        frame.attrs["rate"] = rate
        return frame
