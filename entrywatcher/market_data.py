"""Kursdaten laden: je Ticker ein DataFrame mit Open, High, Low, Close (dividendenbereinigt).

Aufbau wie in leverageForTheLongRun/SectorEtfBot (Yahoo, CSV, Cache), aber mit
Hoch/Tief, weil Stop und ATR die Tagesspanne brauchen.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from .quiet import quiet_yfinance

COLUMNS = ["Open", "High", "Low", "Close"]


class PriceSource(ABC):
    @abstractmethod
    def ohlc(self, ticker: str, start: str = "2000-01-01") -> pd.DataFrame: ...


class YahooPriceSource(PriceSource):
    def ohlc(self, ticker: str, start: str = "2000-01-01") -> pd.DataFrame:
        import yfinance as yf  # erst hier: Tests brauchen kein Netz

        with quiet_yfinance():
            raw = yf.download(ticker, start=start, auto_adjust=True, progress=False)
        if raw is None or raw.empty:
            raise RuntimeError(f"Yahoo lieferte keine Daten für {ticker}")
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        frame = raw[COLUMNS].dropna().astype(float)
        frame.index = pd.to_datetime(frame.index).tz_localize(None).normalize()
        return frame


class CsvPriceSource(PriceSource):
    """Offline-Quelle: <verzeichnis>/<ticker>.csv mit Spalten date, Open, High, Low, Close."""

    def __init__(self, directory: Path | str) -> None:
        self._dir = Path(directory)

    @staticmethod
    def file_name(ticker: str) -> str:
        return ticker.replace("^", "").replace("=", "_").replace("/", "_") + ".csv"

    def ohlc(self, ticker: str, start: str = "2000-01-01") -> pd.DataFrame:
        frame = pd.read_csv(self._dir / self.file_name(ticker), parse_dates=["date"]).set_index("date")
        return frame.loc[frame.index >= pd.Timestamp(start), COLUMNS].astype(float)

    def save(self, ticker: str, frame: pd.DataFrame) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        frame[COLUMNS].rename_axis("date").to_csv(self._dir / self.file_name(ticker))


class CachedPriceSource(PriceSource):
    """Lädt einmal aus `source`, legt eine CSV ab; danach nur noch aus der Datei. Für den Backtest."""

    def __init__(self, source: PriceSource, cache: CsvPriceSource, refresh: bool = False) -> None:
        self._source, self._cache, self._refresh = source, cache, refresh

    def ohlc(self, ticker: str, start: str = "2000-01-01") -> pd.DataFrame:
        if not self._refresh:
            try:
                return self._cache.ohlc(ticker, start)
            except FileNotFoundError:
                pass
        frame = self._source.ohlc(ticker, "1990-01-01")
        self._cache.save(ticker, frame)
        return frame.loc[frame.index >= pd.Timestamp(start)]
