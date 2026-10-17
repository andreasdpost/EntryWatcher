"""Täglicher Lauf: Watchlist prüfen, Positionen verfolgen, Telegram bei Änderung.

Einzelprüfung ohne Eintrag in der Watchlist (kein Telegram, kein Status):
  python run_watch.py --check NVD.DE
  python run_watch.py --check BAYN.DE DTE.DE --budget 1500 --max-loss 150
"""

from __future__ import annotations

import argparse
import logging
import re

from entrywatcher.app import WatchApp
from entrywatcher.config import ConfigLoader, WatchItem
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
    parser.add_argument("--check", nargs="+", metavar="TICKER",
                        help="einzelne Aktien prüfen (Yahoo-Symbol, z. B. NVD.DE), ohne Watchlist/Telegram")
    parser.add_argument("--budget", type=float, help="nur mit --check: max. Einsatz in € statt [risk]")
    parser.add_argument("--max-loss", type=float, help="nur mit --check: max. Verlust in € statt [risk]")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    config = ConfigLoader().load()
    prices = YahooPriceSource()
    notifier = TelegramNotifier(None, None) if args.no_telegram or args.check else TelegramNotifier.from_env()
    app = WatchApp(config, EntryWatcher(config, prices, YahooEarningsCalendar()),
                   PositionTracker(config, prices), PositionBook("data/positions.json"),
                   StateStore("data/state.json"), notifier)
    if args.check:
        items = [WatchItem(t.upper(), max_position_eur=args.budget, max_loss_eur=args.max_loss) for t in args.check]
        print(re.sub(r"</?b>", "", app.check(items)))
    else:
        print(re.sub(r"</?b>", "", app.run(always=args.always)))


if __name__ == "__main__":
    main()
