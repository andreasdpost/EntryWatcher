"""Täglicher Lauf: Watchlist prüfen, Positionen verfolgen, Telegram bei Änderung."""

from __future__ import annotations

import argparse
import logging
import re

from entrywatcher.app import WatchApp
from entrywatcher.config import ConfigLoader
from entrywatcher.earnings import YahooEarningsCalendar
from entrywatcher.market_data import YahooPriceSource
from entrywatcher.positions import PositionBook, PositionTracker
from entrywatcher.state import StateStore
from entrywatcher.telegram import TelegramNotifier
from entrywatcher.watcher import EntryWatcher


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--always", action="store_true", help="alles senden, nicht nur Änderungen")
    parser.add_argument("--no-telegram", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    config = ConfigLoader().load()
    prices = YahooPriceSource()
    notifier = TelegramNotifier(None, None) if args.no_telegram else TelegramNotifier.from_env()
    app = WatchApp(config, EntryWatcher(config, prices, YahooEarningsCalendar()),
                   PositionTracker(config, prices), PositionBook("data/positions.json"),
                   StateStore("data/state.json"), notifier)
    print(re.sub(r"</?b>", "", app.run(always=args.always)))


if __name__ == "__main__":
    main()
