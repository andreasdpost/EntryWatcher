import numpy as np
import pandas as pd

from entrywatcher.config import RiskSettings, RuleSettings
from entrywatcher.indicators import Indicators
from entrywatcher.rules import NotOverheated, RuleSet, StockTrend
from tests.helpers import ohlc, rising


def ind(frame, **rules):
    return Indicators(RuleSettings(**rules), RiskSettings()).compute(frame)


def test_steady_uptrend_passes_all_rules_when_market_is_up():
    frame = rising()
    i = ind(frame)
    allowed = RuleSet.from_settings(RuleSettings()).entry_allowed(i, pd.Series(True, index=i.index))
    assert allowed.iloc[-1] and not allowed.iloc[100]      # anfangs fehlt die 200er/12-Monats-Historie


def test_market_downtrend_blocks_everything():
    i = ind(rising())
    assert not RuleSet.from_settings(RuleSettings()).entry_allowed(i, pd.Series(False, index=i.index)).any()


def test_jump_of_20_percent_in_a_month_is_overheated():
    closes = list(100 * np.cumprod(np.full(380, 1.001))) + list(np.linspace(146, 176, 20))
    i = ind(ohlc(closes))
    rule = NotOverheated(0.15)
    assert not rule.series(i, None).iloc[-1] and rule.series(i, None).iloc[-30]


def test_falling_stock_fails_trend_rule():
    i = ind(ohlc(list(np.linspace(200, 100, 400))))
    assert not StockTrend().series(i, None).iloc[-1]


def test_confirmation_is_only_added_when_enabled():
    assert len(RuleSet.from_settings(RuleSettings(confirmation=True)).rules) == \
        len(RuleSet.from_settings(RuleSettings()).rules) + 1
