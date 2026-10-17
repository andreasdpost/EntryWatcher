from datetime import date

import numpy as np

from entrywatcher.app import WatchApp
from entrywatcher.positions import Position, PositionTracker, SELL
from entrywatcher.state import StateStore
from entrywatcher.watcher import BUY, WAIT, EntryWatcher
from tests.helpers import FakeEarnings, FakePrices, config, ohlc, rising


def prices(stock):
    return FakePrices({"TEST": stock, "^990100-USD-STRD": rising(len(stock))})


def today(frame):
    return frame.index[-1].date()


def test_uptrend_gives_buy_with_stop_and_size():
    stock = rising()
    a = EntryWatcher(config(), prices(stock), FakeEarnings(), today(stock)).assess(config().watchlist[0])
    assert a.status == BUY and a.size.shares > 0 and a.size.risk <= 100.0
    assert a.stop.price < a.close


def test_earnings_within_block_days_means_wait():
    stock = rising()
    soon = date.fromordinal(today(stock).toordinal() + 3)
    a = EntryWatcher(config(), prices(stock), FakeEarnings(soon), today(stock)).assess(config().watchlist[0])
    assert a.status == WAIT


def test_position_is_sold_when_close_falls_below_trailing_stop():
    closes = list(rising(300).Close) + list(np.linspace(134, 100, 20))
    stock = ohlc(closes)
    pos = Position("TEST", str(stock.index[250].date()), float(stock.Close.iloc[250]), 5, 1.0)
    report = PositionTracker(config(), prices(stock)).report(pos)
    assert report.status == SELL and report.stop > pos.initial_stop


class Recorder:
    def __init__(self):
        self.sent = []

    def send(self, text):
        self.sent.append(text)
        return True


class NoPositions:
    def load(self):
        return []


def test_app_sends_only_on_status_change(tmp_path):
    stock = rising()
    cfg = config()
    watcher = EntryWatcher(cfg, prices(stock), FakeEarnings(), today(stock))
    notifier = Recorder()
    app = WatchApp(cfg, watcher, PositionTracker(cfg, prices(stock)), NoPositions(),
                   StateStore(tmp_path / "s.json"), notifier)
    app.run()
    app.run()
    assert len(notifier.sent) == 1 and "KAUFEN ERLAUBT" in notifier.sent[0]
    app.run(always=True)
    assert len(notifier.sent) == 2


def test_check_neither_sends_nor_saves_state(tmp_path):
    from entrywatcher.config import WatchItem
    stock = rising()
    cfg = config()
    notifier = Recorder()
    state = StateStore(tmp_path / "s.json")
    app = WatchApp(cfg, EntryWatcher(cfg, prices(stock), FakeEarnings(), today(stock)),
                   PositionTracker(cfg, prices(stock)), NoPositions(), state, notifier)
    text = app.check([WatchItem("TEST", max_position_eur=500)])
    assert "KAUFEN ERLAUBT" in text and notifier.sent == [] and state.load() == {}
