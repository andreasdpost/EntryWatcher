"""Backtest der Regeln über die Aktien aus [backtest] tickers → reports/backtest.md."""

from __future__ import annotations

import argparse
from pathlib import Path

from entrywatcher.backtest_app import BacktestApp
from entrywatcher.config import ConfigLoader
from entrywatcher.market_data import CachedPriceSource, CsvPriceSource, YahooPriceSource
from entrywatcher.report import BacktestReport


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Kurse neu laden")
    parser.add_argument("--out", default="reports/backtest.md")
    args = parser.parse_args()
    config = ConfigLoader().load()
    prices = CachedPriceSource(YahooPriceSource(), CsvPriceSource("data/cache"), refresh=args.refresh)
    results, bh, start, end = BacktestApp(config, prices).run()
    text = BacktestReport().render(results, bh, start, end, config.risk.max_position_eur)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
