import pandas as pd
import pytest

from entrywatcher.backtest import Trade, TradeSimulator, taxes_paid
from entrywatcher.config import BacktestSettings, RiskSettings, RuleSettings, TaxRules
from entrywatcher.indicators import Indicators
from entrywatcher.rules import RuleSet
from entrywatcher.tax import GermanTaxAccount
from tests.helpers import ohlc, rising


def simulate(frame, **risk):
    r = RiskSettings(**risk)
    i = Indicators(RuleSettings(), r).compute(frame)
    sim = TradeSimulator(RuleSet.from_settings(RuleSettings()), r, BacktestSettings(fee_per_order=0, half_spread=0))
    return sim.run("T", i, frame["Open"], pd.Series(True, index=i.index))


def test_enters_day_after_signal_and_holds_open_position_to_end():
    trades = simulate(rising())
    assert len(trades) == 1 and trades[0].gain > 0


def test_gap_below_stop_sells_at_open_not_at_stop():
    base = rising(400)
    closes = list(base.Close) + [base.Close.iloc[-1] * 0.7]
    opens = list(base.Close) + [base.Close.iloc[-1] * 0.7]
    trades = simulate(ohlc(closes, opens=opens))
    assert trades[0].exit_price == pytest.approx(closes[-1])


def test_tax_nets_losses_against_gains_across_tickers():
    d = pd.Timestamp("2021-06-01")
    trades = [Trade("A", d, d, 1, 100, 300, 0), Trade("B", d, d + pd.Timedelta(days=1), 1, 100, 50, 0)]
    paid = taxes_paid(trades, lambda: GermanTaxAccount(TaxRules()))
    assert paid == pytest.approx(150 * TaxRules().effective_rate)
